import json
import os
import re
import dashscope
from dashscope import Generation
from dotenv import load_dotenv

load_dotenv()


class KeywordExtractor:
    def __init__(self, input_file: str, output_file: str = None, extend_ms: int = 500):
        self.input_file = input_file
        self.output_file = output_file or input_file.replace('.json', '_keywords.json')
        self.extend_ms = extend_ms
        self.data = None
        self.full_text = None
        self.sentences = None
        self.all_words = []

    def load_data(self):
        with open(self.input_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.full_text = self.data['transcripts'][0]['text']
        self.sentences = self.data['transcripts'][0]['sentences']

        for sentence in self.sentences:
            for word in sentence.get('words', []):
                self.all_words.append(word)

    def extract_keywords_via_llm(self) -> list:
        dashscope.api_key = os.getenv("ALI_KEY")
        if not dashscope.api_key:
            raise Exception("请在 .env 文件中设置 ALI_KEY")

        sentences_text = ""
        for i, sentence in enumerate(self.sentences):
            sentences_text += f"第{i+1}句: {sentence['text']}\n"

        prompt = f"""请为每句话提取需要强调显示的内容，这些内容用于在视频画面上显示以引导观众注意力。

要求：
1. 每句话提取1个关键词或短句，数量与句子数量一致
2. 强调词/短句控制在 2-6 个字为宜，最多不超过8个字
3. 短句示例：如"元和十年"、"永州城外"等来自原文的精炼短句
4. 每个内容需要标注重要等级和类型：
   - level: 重要等级
     - 0级: 诗句或古文原文（如"千山鸟飞绝，万径人踪灭"，这是最高优先级，不限制长度）
     - 1级: 关键地点、诗句名字、关键事件、时间地点短语（如"元和十年"、"永州"）
     - 2级: 情感关键词
     - 3级: 其它值得强调的内容
   - type: 内容类型
     - 0: 诗名（如"江雪"）
     - 1: 诗句（如"千山鸟飞绝"、"孤舟蓑笠翁"）
     - 2: 其它关键词
5. 返回格式为 JSON 数组，每个元素包含 keyword、level 和 type 字段
6. keyword 必须是文案中存在的原句或词语，不要编造
7. 如果是诗句，请用换行符分割每句（如"千山鸟飞绝\\n万径人踪灭"）
8. 只返回 JSON 数组，不要其他内容

句子内容：
{sentences_text}

请提取需要强调的内容（返回JSON数组）："""

        response = Generation.call(
            model=Generation.Models.qwen_plus,
            prompt=prompt,
            result_format='message'
        )

        if response.status_code == 200:
            keywords_str = response.output.choices[0].message.content
            import re
            json_match = re.search(r'\[[\s\S]*\]', keywords_str)
            if json_match:
                keywords_list = json.loads(json_match.group())
                return keywords_list
            keywords_str = keywords_str.replace('、', ',').replace('，', ',')
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
            return [{'keyword': k, 'level': 3} for k in keywords]
        else:
            raise Exception(f"API 调用失败: {response.code} - {response.message}")

    def match_keywords_with_timestamps(self, keywords: list) -> list:
        results = []

        for kw_item in keywords:
            if isinstance(kw_item, dict):
                keyword = kw_item.get('keyword', '')
                level = kw_item.get('level', 3)
                kw_type = kw_item.get('type', 2)
            else:
                keyword = kw_item
                level = 3
                kw_type = 2

            if level == 0:
                matched_words = self._find_poetry_matching_words(keyword)
            else:
                matched_words = self._find_matching_words(keyword)

            if matched_words:
                begin_time = matched_words[0]['begin_time']
                end_time = matched_words[-1]['end_time']
                end_time = end_time + self.extend_ms

                results.append({
                    'keyword': keyword,
                    'level': level,
                    'type': kw_type,
                    'begin_time': begin_time,
                    'end_time': end_time
                })

        return results

    def _find_poetry_matching_words(self, keyword: str) -> list:
        lines = keyword.split('\n')
        all_matches = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            matched = self._find_matching_words(line)
            if matched:
                all_matches.extend(matched)

        return all_matches

    def _find_matching_words(self, keyword: str) -> list:
        all_text = ''.join([w['text'] for w in self.all_words])

        if keyword in all_text:
            start_idx = all_text.index(keyword)
            char_count = 0
            for i, word_info in enumerate(self.all_words):
                char_count += len(word_info['text'])
                if char_count > start_idx:
                    matched = [word_info]
                    target_len = len(keyword)
                    current_len = len(word_info['text'])
                    j = i + 1
                    while current_len < target_len and j < len(self.all_words):
                        matched.append(self.all_words[j])
                        current_len += len(self.all_words[j]['text'])
                        j += 1
                    return matched

        best_match = None
        best_len = 0

        for word_info in self.all_words:
            word_text = word_info['text']
            if keyword == word_text:
                if len(word_text) > best_len:
                    best_len = len(word_text)
                    best_match = word_info

        if best_match:
            return [best_match]

        for word_info in self.all_words:
            word_text = word_info['text']
            if keyword in word_text and len(keyword) >= 2:
                if len(word_text) > best_len:
                    best_len = len(word_text)
                    best_match = word_info

        if best_match:
            return [best_match]

        keyword_chars = set(keyword)
        for word_info in self.all_words:
            word_text = word_info['text']
            if len(word_text) >= 2:
                word_chars = set(word_text)
                overlap = len(keyword_chars & word_chars)
                if overlap >= len(keyword_chars) * 0.6:
                    if len(word_text) > best_len:
                        best_len = len(word_text)
                        best_match = word_info

        return [best_match] if best_match else []

    def save_results(self, results: list):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {self.output_file}")

    def run(self):
        print(f"加载数据: {self.input_file}")
        self.load_data()

        print("正在调用通义千问提取关键词...")
        keywords = self.extract_keywords_via_llm()
        print(f"提取到的关键词: {keywords}")

        print("正在匹配时间戳...")
        results = self.match_keywords_with_timestamps(keywords)
        results.sort(key=lambda x: x['begin_time'])
        print(f"成功匹配 {len(results)} 个关键词")

        for r in results:
            print(f"  - {r['keyword']}: {r['begin_time']}ms ~ {r['end_time']}ms")

        self.save_results(results)
        return results


if __name__ == '__main__':
    extractor = KeywordExtractor(
        input_file='1.json',
        output_file='keywords_output.json',
        extend_ms=500
    )
    extractor.run()
