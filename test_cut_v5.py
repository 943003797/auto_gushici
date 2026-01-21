from src.autocut.cut_v5 import autoCut

title = "李清照词赏析"
list = """[
  {
    "id": 1,
    "text": "是曾经拥有过全世界的绚烂",
    "audio_length": 4,
    "video_path": "D:/Material/video/1/484.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/1.mp3",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 2,
    "text": "最后只剩下一地鸡毛的凄凉。",
    "audio_length": 4,
    "video_path": "D:/Material/video/1/584.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/2.mp3",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 3,
    "text": "这种落差，比从未拥有过更让人绝望。",
    "audio_length": 4,
    "video_path": "D:/Material/video/1/458.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/3.mp3",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 4,
    "text": "是曾经拥有过全世界的绚烂",
    "audio_length": 4,
    "video_path": "D:/Material/video/1/1227.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/4.mp3",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 5,
    "text": "最后只剩下一地鸡毛的凄凉。",
    "audio_length": 3,
    "video_path": "D:/Material/video/1/1800.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/5.mp3",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 6,
    "text": "这种落差，比从未拥有过更让人绝望。",
    "audio_length": 4,
    "video_path": "D:/Material/video/1/777.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/6.mp3",
    "danmu": "",
    "danmu_style": ""
  }
]"""
poetry_draft = autoCut(title=title, list=list, bgm="落.mp3", bgv="温柔细闪.mp4")
poetry_draft.general_draft()