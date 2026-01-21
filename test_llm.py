import unittest
from src.ai_models.big_model.llm import LLM

if __name__ == '__main__':
    llm = LLM()
    wenan = """
    它被公认为宋词里的“万古愁心之祖”。
    全篇没有一个“泪”字，
    却让无数人在读完后感到窒息般的压抑。
    开篇连用14个叠字，
    寻寻觅觅，冷冷清清，凄凄惨惨戚戚。
    看似只是文字的堆叠，
    实则是一个女人在精神崩溃边缘的低声呢喃
    它就是李清照的绝笔之一——《声声慢》。
    如果说苏轼的悼亡是十年后的深沉回望，
    那李清照的这首词，就是正在淌血的新鲜伤口。
    我们常以为，孤独是此时此刻没人陪伴。
    但李清照告诉我们，真正的孤独，
    是满屋子都是往事的影子，
    却再也抓不住那个能回应你的人。
    是曾经拥有过全世界的绚烂，
    最后只剩下一地鸡毛的凄凉。
    这种落差，比从未拥有过更让人绝望。
    """
    text = "寻寻觅觅，冷冷清清，凄凄惨惨戚戚。"
    # video_description = llm.get_video_description(wenan, text)

    video_content = ["开心的小孩在唱歌", "屋内一人在落寞的来回走动"]
    video_description = llm.match_video(wenan="它被公认为宋词里的万古愁心之祖", video_content=video_content)
    print(video_description)