import os, random
import pyJianYingDraft as draft
from pyJianYingDraft import TextIntro, TextOutro, Text_loop_anim, Mask_type, VideoSceneEffectType, animation, IntroType, OutroType, Transition_type, trange, GroupAnimationType
from pyJianYingDraft.script_file import json
from dotenv import load_dotenv

load_dotenv()

class autoCut():
    def __init__(self, title: str = "", wenan: str = "", list: list = [], bgm: str = "", bgv: str = ""):
        self.title = title
        self.list = list
        self.tts_dir = os.getenv("DRAFT_DIR") + self.title + "/Resources/audioAlg/"
        self.bgm_dir = "./material/bgm/"
        self.bgv_dir = "./material/bgv/"
        self.bgp_dir = os.getenv("DRAFT_DIR") + self.title + "/Resources/image/"
        self.output_dir = os.getenv("DRAFT_DIR") + self.title
        self.bgm = bgm
        self.bgv = bgv
        self.wenan = wenan.split("，")
        self.audioNowTime = 0
        self.textNowTime = 0

        self.script = draft.ScriptFile(1920, 1080)
        self.script.add_track(draft.TrackType.text, 'SY')
        self.script.add_track(draft.TrackType.audio, 'BGM')
        self.script.add_track(draft.TrackType.audio, 'WENAN_AUDIO')
        self.script.add_track(draft.TrackType.audio, 'TTS')
        self.script.add_track(draft.TrackType.sticker, 'STK')
        self.script.add_track(draft.TrackType.video, 'BGV', mute= True, relative_index=8)
        self.script.add_track(draft.TrackType.video, 'BGVC', mute= True, relative_index=0)
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

    def cut_wenan(self) -> list:
        audioTimeCount = 0
        for k, str in enumerate(self.wenan):
            print(k, str)
            AudioMaterial = draft.AudioMaterial(os.path.join(self.tts_dir, f'wenan_{k}.mp3'))
            audio_time = AudioMaterial.duration
            self.script.add_material(AudioMaterial)
            AudioSegment = draft.AudioSegment(AudioMaterial,
                                        trange(self.audioNowTime, audio_time),
                                        volume=1)
            self.script.add_segment(AudioSegment, 'WENAN_AUDIO')
            self.audioNowTime += audio_time
            audioTimeCount += audio_time

            if (k+1) % 2 == 0:
                print(self.audioNowTime)
                TextSegment = draft.TextSegment(self.wenan[k - 1], trange(self.textNowTime, audioTimeCount),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                        font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                        style=draft.TextStyle(color=(1, 1, 1), size=22),                # 设置字体颜色为黄色
                                        border=draft.TextBorder(alpha=0.2,color=(0, 0, 0)),
                                        clip_settings=draft.ClipSettings(transform_x=-0.35,transform_y=0.25, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
                TextSegment.add_animation(TextIntro.激光雕刻, self.s(1.5))
                TextSegment.add_animation(TextOutro.渐隐, self.s(0.5))
                self.script.add_segment(TextSegment, 'WENAN_TEXT_1')

                TextSegment = draft.TextSegment(self.wenan[k], trange(self.audioNowTime - audio_time*1.4, audio_time*1.4),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                        font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                        style=draft.TextStyle(color=(1, 0.27450980392156865, 0.12549019607843137), size=22),                # 设置字体颜色为黄色
                                        border=draft.TextBorder(alpha=0.2,color=(0, 0, 0)),
                                        clip_settings=draft.ClipSettings(transform_x=0.15,transform_y=-0.25, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
                TextSegment.add_animation(TextIntro.激光雕刻, self.s(1.5))
                TextSegment.add_animation(TextOutro.渐隐, self.s(0.5))
                self.script.add_segment(TextSegment, 'WENAN_TEXT_2')
                self.audioNowTime += self.s(0.03)
                self.textNowTime = self.audioNowTime
                audioTimeCount = 0
        #诗词背景
        video_material = draft.VideoMaterial(os.path.join(self.bgv_dir, self.bgv))
        video_duration = video_material.duration
        self.script.add_material(video_material)
        video_segment = draft.VideoSegment(material = video_material,
                                                        target_timerange  = trange(0, int(self.textNowTime)),
                                                        volume=0)
        video_segment.add_animation(GroupAnimationType.旋出渐隐)
        self.script.add_segment(video_segment, 'BGVC')
    def addBgm(self):
        audio_bgm = draft.AudioMaterial(os.path.join(self.bgm_dir, self.bgm))
        audio_bgm_lenth = audio_bgm.duration
        self.script.add_material(audio_bgm)
        audio_bgm_segment = draft.AudioSegment(audio_bgm, trange(0, self.audioNowTime),volume=0.4)
        audio_bgm_segment.add_fade("0.2s", "1s")
        self.script.add_segment(audio_bgm_segment, 'BGM')
        # 水印
        TextSegment = draft.TextSegment("和光同尘、", trange(0, self.audioNowTime),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    border=draft.TextBorder(alpha=0.2,color=(0, 0, 0)),
                                    clip_settings=draft.ClipSettings(transform_x=-0.85,transform_y=0.90, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
        TextSegment.add_animation(TextIntro.冰雪飘动, 1500000)
        TextSegment.add_animation(TextOutro.渐隐, 500000)
        self.script.add_segment(TextSegment, 'SY')

    def addItem(self) -> str:
        json_data = self.list
        for key, item in json_data.items() if isinstance(json_data, dict) else enumerate(json_data):
            # 音频素材
            itemPeiyinNow = self.audioNowTime
            audio_duration = 0
            for i in range(10):
                if os.path.exists(os.path.join(self.tts_dir, f"{item['id']}_{i}.mp3")):
                    AudioMaterial = draft.AudioMaterial(os.path.join(self.tts_dir, f"{item['id']}_{i}.mp3"))
                    audio_length = AudioMaterial.duration
                    
                    self.script.add_material(AudioMaterial)
                    AudioSegment = draft.AudioSegment(AudioMaterial,
                                    trange(int(itemPeiyinNow), int(audio_length)),
                                    volume=1)
                    self.script.add_segment(AudioSegment, 'TTS')
                    itemPeiyinNow += audio_length
                    audio_duration+=audio_length
            
            # 背景素材,分段定制
            
            video_material = draft.VideoMaterial(os.path.join(self.bgp_dir, f"{item['id']}.png"))
            video_duration = video_material.duration
            self.script.add_material(video_material)
            video_segment = draft.VideoSegment(material = video_material,
                                                        target_timerange  = trange(int(self.audioNowTime), int(audio_duration) + 500000),
                                                        source_timerange = trange(f"{random.randint(110,240)}s", int(audio_duration)),
                                                        volume=0)
            video_segment.add_animation(IntroType.水墨, (int(audio_duration) + 500000)/20*6)
            if key == len(json_data) - 1:
                video_segment.add_animation(OutroType.渐隐, (int(audio_duration) + 500000)/20*6)
            else:
                video_segment.add_animation(OutroType.水墨, (int(audio_duration) + 500000)/20)
            self.script.add_segment(video_segment, 'BGV')

            StickerSegment = draft.StickerSegment(
                resource_id = "7226264888031694091",
                target_timerange = trange(int(self.audioNowTime), int(audio_duration) + 500000),
                clip_settings = draft.ClipSettings(
                    scale_x = 2,
                    scale_y = 0.25
                )
            )
            self.script.add_segment(StickerSegment, 'STK')
            # 字幕素材
            # title = item['shiju']
            title = '123|456'
            total_length = len(item['shangju']) + len(item['xiaju'])
            segments = []
            segments.append(item['shangju'])
            segments.append(item['xiaju'])
            print(segments)
            total_length = sum(len(segment) for segment in segments)
            list = [[segment, round(len(segment) / total_length, 3)] for segment in segments]
            splitNum = len(list) - 1
            split = [
                {
                    "fixed": [
                        [-0.5,0.5]
                    ]
                },
                {
                    "fixed": [
                        [-0.3,0.15],
                        [0.3,-0.15]
                    ]
                },
                {
                    "fixed": [
                        [0,0.2],
                        [0,0],
                        [0,-0.2]
                    ]
                },
                {
                    "fixed": [
                        [-0.4,0.15],
                        [0.4,0.15],
                        [-0.4,-0.15],
                        [0.4,-0.15]
                    ]
                }
            ]
            # 作者信息
            TextSegment = draft.TextSegment(f"{item['zuozhe']}《{item['shiming']}》", trange(self.audioNowTime, int(audio_duration)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    border=draft.TextBorder(color=(0, 0, 0)),
                                    clip_settings=draft.ClipSettings(transform_y=-0.7, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
            TextSegment.add_animation(TextIntro.渐显, 500000)
            TextSegment.add_animation(TextOutro.渐隐, 500000)
            self.script.add_segment(TextSegment, 'ZZ')
            # 赏析
            TextSegment = draft.TextSegment(f"{item['yiwen']}", trange(self.audioNowTime, int(audio_duration)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    border=draft.TextBorder(color=(0, 0, 0)),
                                    clip_settings=draft.ClipSettings(transform_y=-0.85, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
            TextSegment.add_animation(TextIntro.渐显, 500000)
            TextSegment.add_animation(TextOutro.渐隐, 500000)
            self.script.add_segment(TextSegment, 'SX')
            indent = 500000
            for key, item in enumerate(list):
                        if key == 0:
                            start = self.audioNowTime
                            duration = audio_duration
                            animation_duration = audio_duration / 4
                            print(splitNum)
                            fixed_x = split[splitNum]['fixed'][key][0]
                            fixed_y = split[splitNum]['fixed'][key][1]
                        else:
                            start = self.audioNowTime + indent
                            duration = self.audioNowTime + audio_duration - start
                            animation_duration = audio_duration / 4
                            fixed_x = split[splitNum]['fixed'][key][0]
                            fixed_y = split[splitNum]['fixed'][key][1]
                        TextSegment = draft.TextSegment(list[key][0], trange(start, duration),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    clip_settings=draft.ClipSettings(transform_x=fixed_x, transform_y=fixed_y))          # 模拟字幕的位置
                        TextSegment.add_animation(TextIntro.冰雪飘动, animation_duration)
                        TextSegment.add_animation(TextOutro.渐隐, animation_duration/3)
                        self.script.add_segment(TextSegment, 'T' + str(key))
                        indent += 500000
            print(audio_duration/500000)
            self.audioNowTime += audio_duration + 500000
        return 'Success'
    def general_draft(self):
        try:
            self.cut_wenan()
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

# wenan = "其实我更喜欢，好多年前的自己，他比我有胆量，比我遗憾少，比我懂得少，比我相信的更多，在失去的所有人中，我最怀念的是我自己"
# list = [
#        {
#         "id": "1",
#         "shangju": "花自飘零水自流",
#         "xiaju": "一种相思两处闲愁",
#         "shiming": "一剪梅·红藕香残玉簟秋",
#         "zuozhe": "李清照",
#         "yiwen": "花儿自顾飘零，水自顾流淌；同样的相思，分隔两地各自忧愁。"
#     },{
#         "id": "2",
#         "shangju": "物是人非事事休",
#         "xiaju": "欲语泪先流",
#         "shiming": "武陵春·春晚",
#         "zuozhe": "李清照",
#         "yiwen": "景物依旧，人事已非，万事皆休，话未出口泪已先流。"
#     }
# ]
# wenan = "其实我更喜欢，好多年前的自己"
# poetry_draft = autoCut(title="年少时的自己", wenan=wenan, list=list, bgm="我记得伴奏.mp3", bgv="温柔细闪.mp4")
# poetry_draft.general_draft()