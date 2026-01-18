from src.autocut.cut_v5 import autoCut

title = "李清照词赏析"
list = """[
  {
    "id": 1,
    "text": "它被公认为宋词里的“万古愁心之祖”。",
    "audio_length": 6,
    "video_path": "D:/Material/video/1/328.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/1.mp3",
    "title": "李清照词赏析-1",
    "danmu": ["李清照-《声声慢》"],
    "danmu_style": "middle"
  },
  {
    "id": 2,
    "text": "全篇没有一个“泪”字，",
    "audio_length": 4,
    "video_path": "D:/Material/video/1/789.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/2.mp3",
    "title": "李清照词赏析-1",
    "danmu": "字字泣血\\n笔笔含泪\\n笔笔含泪\\n笔笔含泪",
    "danmu_style": "left"
  },
  {
    "id": 3,
    "text": "却让无数人在读完后感到窒息般的压抑。",
    "audio_length": 5,
    "video_path": "D:/Material/video/1/799.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/3.mp3",
    "title": "",
    "danmu": "1307年，安史之乱爆发",
    "danmu_style": "bottom"
  },
  {
    "id": 4,
    "text": "开篇连用14个叠字，",
    "audio_length": 3,
    "video_path": "D:/Material/video/1/338.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/4.mp3",
    "title": "",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 5,
    "text": "寻寻觅觅，冷冷清清，凄凄惨惨戚戚。",
    "audio_length": 6,
    "video_path": "D:/Material/video/1/960.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/5.mp3",
    "title": "",
    "danmu": "寻寻觅觅\\n冷冷清清\\n凄凄惨惨戚戚",
    "danmu_style": "right"
  },
  {
    "id": 6,
    "text": "看似只是文字的堆叠，",
    "audio_length": 3,
    "video_path": "D:/Material/video/1/345.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/6.mp3",
    "title": "",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 7,
    "text": "实则是一个女人在精神崩溃边缘的低声呢喃",
    "audio_length": 7,
    "video_path": "D:/Material/video/1/764.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/7.mp3",
    "title": "",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 8,
    "text": "它就是李清照的绝笔之一——《声声慢》。",
    "audio_length": 6,
    "video_path": "D:/Material/video/1/328.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/8.mp3",
    "title": "",
    "danmu": ["李清照-《声声慢》"],
    "danmu_style": "middle"
  },
  {
    "id": 9,
    "text": "如果说苏轼的悼亡是十年后的深沉回望，",
    "audio_length": 6,
    "video_path": "D:/Material/video/1/663.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/9.mp3",
    "title": "",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 10,
    "text": "那李清照的这首词，就是正在淌血的新鲜伤口。",
    "audio_length": 7,
    "video_path": "D:/Material/video/1/16.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/10.mp3",
    "title": "",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 11,
    "text": "我们常以为，孤独是此时此刻没人陪伴。",
    "audio_length": 6,
    "video_path": "D:/Material/video/1/752.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/11.mp3",
    "title": "",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 12,
    "text": "但李清照告诉我们，真正的孤独，",
    "audio_length": 5,
    "video_path": "D:/Material/video/1/66.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/12.mp3",
    "title": "",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 13,
    "text": "是满屋子都是往事的影子，",
    "audio_length": 4,
    "video_path": "D:/Material/video/1/728.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/13.mp3",
    "title": "",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 14,
    "text": "却再也抓不住那个能回应你的人。",
    "audio_length": 4,
    "video_path": "D:/Material/video/1/680.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/14.mp3",
    "title": "",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 15,
    "text": "是曾经拥有过全世界的绚烂，",
    "audio_length": 4,
    "video_path": "D:/Material/video/1/502.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/15.mp3",
    "title": "",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 16,
    "text": "最后只剩下一地鸡毛的凄凉。",
    "audio_length": 5,
    "video_path": "D:/Material/video/1/642.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/16.mp3",
    "title": "",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 17,
    "text": "这种落差，比从未拥有过更让人绝望。",
    "audio_length": 6,
    "video_path": "D:/Material/video/1/663.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/17.mp3",
    "title": "",
    "danmu": "",
    "danmu_style": ""
  }
]"""
poetry_draft = autoCut(title=title, list=list, bgm="落.mp3", bgv="温柔细闪.mp4")
poetry_draft.general_draft()