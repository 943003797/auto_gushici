import os, json
import pyJianYingDraft as draft
from pyJianYingDraft import TextIntro, TextOutro, Text_loop_anim, Mask_type, VideoSceneEffectType, animation, IntroType, OutroType, Transition_type, trange, GroupAnimationType
from pyJianYingDraft.script_file import json
from dotenv import load_dotenv

load_dotenv()

class autoCut():
    def __init__(self, title: str = "", list: str = "[]", bgm: str = "爱的供养间奏.mp3", bgv: str = "温柔细粉.mp4"):
        self.title = title
        self.list = json.loads(list)
        self.tts_dir = os.getenv("DRAFT_DIR") + self.title + "/Resources/audioAlg/"
        self.bgm_dir = "./material/bgm/"
        self.bgv_dir = "./material/bgv/"
        self.bgp_dir = os.getenv("DRAFT_DIR") + self.title + "/Resources/image/"
        self.output_dir = os.getenv("DRAFT_DIR") + self.title
        self.bgm = bgm
        self.bgv = bgv
        self.audioNowTime = 0
        self.textNowTime = 0

        self.script = draft.ScriptFile(1920, 1080)
        self.script.add_track(draft.TrackType.text, 'SY')
        self.script.add_track(draft.TrackType.audio, 'BGM')
        self.script.add_track(draft.TrackType.audio, 'WENAN_AUDIO')
        self.script.add_track(draft.TrackType.audio, 'TTS')
        self.script.add_track(draft.TrackType.sticker, 'STK')
        self.script.add_track(draft.TrackType.video, 'BGV', mute= True, relative_index=0)
        self.script.add_track(draft.TrackType.video, 'BGVC', mute= True, relative_index=0)
        self.script.add_track(draft.TrackType.video, 'BDTOP', mute= True, relative_index=1)
        self.script.add_track(draft.TrackType.video, 'BDBOT', mute= True, relative_index=1)
        self.script.add_track(draft.TrackType.text, 'WENAN_TEXT_1')
        self.script.add_track(draft.TrackType.text, 'WENAN_TEXT_2')
        self.script.add_track(draft.TrackType.text, 'T0')
        self.script.add_track(draft.TrackType.text, 'T1')
        self.script.add_track(draft.TrackType.text, 'T2')
        self.script.add_track(draft.TrackType.text, 'T3')
        self.script.add_track(draft.TrackType.text, 'T4')
        self.script.add_track(draft.TrackType.text, 'T5')
        self.script.add_track(draft.TrackType.text, 'T6')
        self.script.add_track(draft.TrackType.text, 'ZZ')
        self.script.add_track(draft.TrackType.text, 'SX')

    def s(self, microseconds: int):
        return microseconds * 1000000

    def addBgm(self):
        audio_bgm = draft.AudioMaterial(os.path.join(self.bgm_dir, self.bgm))
        audio_bgm_lenth = audio_bgm.duration
        self.script.add_material(audio_bgm)
        print(self.audioNowTime)
        audio_bgm_segment = draft.AudioSegment(audio_bgm, trange(0, self.audioNowTime),volume=0.4)
        audio_bgm_segment.add_fade("0.2s", "1s")
        self.script.add_segment(audio_bgm_segment, 'BGM')
        # 水印
        TextSegment = draft.TextSegment("和光同尘、", trange(0, self.audioNowTime),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    border=draft.TextBorder(alpha=0.2,color=(0, 0, 0)),
                                    clip_settings=draft.ClipSettings(transform_x=-0.765,transform_y=0.90, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
        TextSegment.add_animation(TextIntro.冰雪飘动, 1500000)
        TextSegment.add_animation(TextOutro.渐隐, 500000)
        self.script.add_segment(TextSegment, 'SY')

        #边框TOP
        video_material = draft.VideoMaterial("./material/border/border.png")
        video_duration = video_material.duration
        self.script.add_material(video_material)
        video_segment = draft.VideoSegment(material = video_material,
                                                        target_timerange  = trange(0, self.audioNowTime),
                                                        volume=0,
                                                        clip_settings=draft.ClipSettings(transform_y=0.917))
        video_segment.add_animation(IntroType.渐显, 300000)
        video_segment.add_animation(OutroType.渐隐, 300000)
        self.script.add_segment(video_segment, 'BDTOP')

        #边框BOT
        video_material = draft.VideoMaterial("./material/border/border.png")
        video_duration = video_material.duration
        self.script.add_material(video_material)
        video_segment = draft.VideoSegment(material = video_material,
                                                        target_timerange  = trange(0, self.audioNowTime),
                                                        volume=0,
                                                        clip_settings=draft.ClipSettings(transform_y=-0.917, flip_vertical = True))
        video_segment.add_animation(IntroType.渐显, 300000)
        video_segment.add_animation(OutroType.渐隐, 300000)
        self.script.add_segment(video_segment, 'BDBOT')

    def addItem(self) -> str:
        for item in self.list:
            itemPeiyinNow = self.audioNowTime
            audio_duration = 0
            if os.path.exists(f"{item['audio_patch']}"):
                # 音频
                AudioMaterial = draft.AudioMaterial(os.path.join(f"{item['audio_patch']}"))
                audio_length = AudioMaterial.duration
                print(audio_length)
                self.script.add_material(AudioMaterial)
                AudioSegment = draft.AudioSegment(AudioMaterial,
                                trange(int(itemPeiyinNow), int(audio_length)),
                                volume=1)
                self.script.add_segment(AudioSegment, 'TTS')
                #背景
                video_material = draft.VideoMaterial(item['video_path'])
                video_duration = video_material.duration
                self.script.add_material(video_material)
                video_segment = draft.VideoSegment(material = video_material,
                                                                target_timerange  = trange(int(itemPeiyinNow), int(audio_length)),
                                                                volume=0)
                video_segment.add_animation(IntroType.渐显, 300000)
                video_segment.add_animation(OutroType.渐隐, 300000)
                self.script.add_segment(video_segment, 'BGV')

                # 字幕
                TextSegment = draft.TextSegment(f"{item['text']}", trange(int(itemPeiyinNow), int(audio_length)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                        font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                        style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                        border=draft.TextBorder(color=(0, 0, 0)),
                                        clip_settings=draft.ClipSettings(transform_y=-0.92, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
                TextSegment.add_animation(TextIntro.渐显, 500000)
                TextSegment.add_animation(TextOutro.渐隐, 500000)
                self.script.add_segment(TextSegment, 'ZZ')

                itemPeiyinNow += audio_length
                audio_duration+=audio_length
                print(audio_duration/500000)
                self.audioNowTime += audio_duration
        return 'Success'
    def general_draft(self):
        try:
            self.addItem()
            self.addBgm()
            # testObj.addVideo('bgv.mp4')
            self.script.dump(self.output_dir + '/draft_content.json')
            # # 导出
            # ctrl = draft.JianyingController()
            # 导出
        except Exception as e:
            print(f"生成草稿时发生错误: {str(e)}")
            raise
        return True

if __name__ == '__main__':
    title = "李清照词赏析"
    list = """[
  {
    "id": 1,
    "text": "它被公认为宋词里的“万古愁心之祖”。",
    "audio_length": 4,
    "video_path": "D:/Material/video/1/412.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/1.mp3"
  },
  {
    "id": 2,
    "text": "全篇没有一个“泪”字，却让无数人在读完后感到窒息般的压抑。",
    "audio_length": 7,
    "video_path": "D:/Material/video/1/367.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/2.mp3"
  },
  {
    "id": 3,
    "text": "开篇连用14个叠字，寻寻觅觅，冷冷清清，凄凄惨惨戚戚。",
    "audio_length": 7,
    "video_path": "D:/Material/video/1/367.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/3.mp3"
  },
  {
    "id": 4,
    "text": "看似只是文字的堆叠，实则是一个女人在精神崩溃边缘的低声呢喃。",
    "audio_length": 7,
    "video_path": "D:/Material/video/1/183.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/4.mp3"
  },
  {
    "id": 5,
    "text": "它就是李清照的绝笔之一——《声声慢》。",
    "audio_length": 4,
    "video_path": "D:/Material/video/1/412.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/5.mp3"
  },
  {
    "id": 6,
    "text": "如果说苏轼的悼亡是十年后的深沉回望，那李清照的这首词，就是正在淌血的新鲜伤口。",
    "audio_length": 10,
    "video_path": "D:/Material/video/1/631.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/6.mp3"
  },
  {
    "id": 7,
    "text": "我们常以为，孤独是此时此刻没人陪伴。",
    "audio_length": 5,
    "video_path": "D:/Material/video/1/261.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/7.mp3"
  },
  {
    "id": 8,
    "text": "但李清照告诉我们，真正的孤独，是满屋子都是往事的影子，却再也抓不住那个能回应你的人。",
    "audio_length": 10,
    "video_path": "D:/Material/video/1/40.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/8.mp3"
  },
  {
    "id": 9,
    "text": "是曾经拥有过全世界的绚烂，最后只剩下一地鸡毛的凄凉。",
    "audio_length": 7,
    "video_path": "D:/Material/video/1/396.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/9.mp3"
  },
  {
    "id": 10,
    "text": "这种落差，比从未拥有过更让人绝望。",
    "audio_length": 5,
    "video_path": "D:/Material/video/1/303.mp4",
    "audio_patch": "draft/JianyingPro Drafts/李清照词赏析/Resources/audioAlg/10.mp3"
  }
]"""
    poetry_draft = autoCut(title=title, list=list, bgm="落.mp3", bgv="温柔细闪.mp4")
    poetry_draft.general_draft()