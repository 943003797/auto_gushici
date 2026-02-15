import json
import os
import re


class KeywordExtractorV2:
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = input_file
        self.output_file = output_file or input_file.replace('.json', '_keywords_prompt.txt')
        self.data = None
        self.sentences = None

    def load_data(self):
        with open(self.input_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        self.sentences = self.data['transcripts'][0]['sentences']

    def generate_prompt(self) -> str:
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

        return prompt

    def save_prompt(self, prompt: str):
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"提示词已保存到: {self.output_file}")

    def run(self):
        print(f"加载数据: {self.input_file}")
        self.load_data()

        print("正在生成提示词...")
        prompt = self.generate_prompt()
        
        print("\n" + "="*60)
        print("生成的提示词：")
        print("="*60)
        print(prompt)
        print("="*60 + "\n")

        self.save_prompt(prompt)
        
        print("提示：")
        print("1. 复制上方提示词")
        print("2. 手动调用你选择的模型（如 ChatGPT、Claude 等）")
        print("3. 将模型返回的 JSON 结果保存到文件")
        print(f"4. 使用原版 extract_keywords.py 的 match_keywords_with_timestamps 方法匹配时间戳")
        
        return prompt


if __name__ == '__main__':
    extractor = KeywordExtractorV2(
        input_file='draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/asr.json',
        output_file='keywords_prompt.txt'
    )
    extractor.run()
