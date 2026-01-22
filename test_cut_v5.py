from src.autocut.cut_v5 import autoCut

title = "唐多令芦叶满汀州"
list = """[
  {
    "id": 1,
    "text": "如果要在宋词里找一首最让中年人破防的作品",
    "audio_length": 5,
    "video_path": "D:/Material/video/1/777.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/1.mp3",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 2,
    "text": "苏轼的纵使相逢应不识固然摧肝裂肺",
    "audio_length": 5,
    "video_path": "D:/Material/video/2/41.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/2.mp3",
    "danmu": "纵使相逢\\n应不识",
    "danmu_style": "bottom"
  },
  {
    "id": 3,
    "text": "但那终究是一场关乎生死的梦境",
    "audio_length": 3,
    "video_path": "D:/Material/video/2/4.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/3.mp3",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 4,
    "text": "而在我心中，真正能把岁月的无情、梦想的幻灭",
    "audio_length": 5,
    "video_path": "D:/Material/video/2/32.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/4.mp3",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 5,
    "text": "以及将那种人还在，心已老的悲凉写到骨子里的，只有刘过",
    "audio_length": 7,
    "video_path": "D:/Material/video/1/1827.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/5.mp3",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 6,
    "text": "这首词就是被无数当代年轻人奉为朋友圈文案天花板的",
    "audio_length": 6,
    "video_path": "D:/Material/video/1/328.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/6.mp3",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 7,
    "text": "《唐多令·芦叶满汀州》",
    "audio_length": 3,
    "video_path": "D:/Material/video/1/1588.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/7.mp3",
    "danmu": "《唐多令·芦叶满汀州》",
    "danmu_style": "middle"
  },
  {
    "id": 8,
    "text": "这首词最出名的那句欲买桂花同载酒，终不似，少年游",
    "audio_length": 6,
    "video_path": "D:/Material/video/1/1473.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/8.mp3",
    "danmu": "欲买桂花同载酒终不似少年游",
    "danmu_style": "right"
  },
  {
    "id": 9,
    "text": "短短十三个字，却像是一把钝刀",
    "audio_length": 4,
    "video_path": "D:/Material/video/2/3.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/9.mp3",
    "danmu": "",
    "danmu_style": ""
  },
  {
    "id": 10,
    "text": "慢慢地割开了每一个在生活里摸爬滚打的人",
    "audio_length": 5,
    "video_path": "D:/Material/video/1/1228.mp4",
    "audio_patch": "draft/JianyingPro Drafts/唐多令芦叶满汀州/Resources/audioAlg/10.mp3",
    "danmu": "",
    "danmu_style": ""
  }
]"""
poetry_draft = autoCut(title=title, list=list, bgm="落.mp3")
poetry_draft.general_draft()