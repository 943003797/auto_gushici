from src.autocut.cut_v5 import autoCut

title = "唐多令芦叶满汀州"
list = """[
  {
    "id": 1,
    "text": "如果要在宋词里找一首最让中年人破防的作品",
    "audio_length": 5,
    "video_path": "D:/Material/video_back/1/777.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/1.mp3",
    "danmu": "旧江山浑是新愁欲买桂花同载酒",
    "danmu_style": "bottom"
  },
  {
    "id": 2,
    "text": "苏轼的纵使相逢应不识固然摧肝裂肺",
    "audio_length": 5,
    "video_path": "D:/Material/video_back/2/41.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/2.mp3",
    "danmu": "纵使相逢\\n应不识",
    "danmu_style": "bottom"
  },
  {
    "id": 3,
    "text": "但那终究是一场关乎生死的梦境",
    "audio_length": 3,
    "video_path": "D:/Material/video_back/2/4.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/3.mp3",
    "danmu": "",
    "danmu_style": ""
  }
]"""
poetry_draft = autoCut(title=title, list=list, bgm="落.mp3")
poetry_draft.general_draft()