import os
import pyJianYingDraft as draft
from pyJianYingDraft import Intro_type, Transition_type, trange
from pyJianYingDraft import TextIntro, TextOutro, Text_loop_anim, Mask_type
from pyJianYingDraft import animation
from pyJianYingDraft.script_file import json
from pyJianYingDraft.jianying_controller import ExportResolution, ExportFramerate


class autoCut():

    def __init__(self, draft_path: str = "", bgm: str = "", bgv: str = ""):
        self.nowS = 0
        self.bgm = bgm
        self.bgv = bgv
        self.DUMP_PATH = draft_path
        self.output_dir = draft_path + "/Resources/"
        self.bgm_dir = draft_path + "/Resources/bgm/"
        self.bgv_dir = draft_path + "/Resources/bgv/"
        self.script = draft.ScriptFile(1920, 1080)
        self.script.add_track(draft.TrackType.audio, 'TTS')
        self.script.add_track(draft.TrackType.audio, 'BGM')
        self.script.add_track(draft.TrackType.video, 'BGV', mute= True, relative_index=1)
        self.script.add_track(draft.TrackType.video, 'BGVC', mute= True, relative_index=0)
        self.script.add_track(draft.TrackType.sticker, 'STK')
        self.script.add_track(draft.TrackType.text, 'T0')
        self.script.add_track(draft.TrackType.text, 'T1')
        self.script.add_track(draft.TrackType.text, 'T2')
        self.script.add_track(draft.TrackType.text, 'T3')
        self.script.add_track(draft.TrackType.text, 'T4')
        self.script.add_track(draft.TrackType.text, 'T5')
        self.script.add_track(draft.TrackType.text, 'T6')
        self.script.add_track(draft.TrackType.text, 'ZZ')
        self.script.add_track(draft.TrackType.text, 'SX')
        self.script.add_track(draft.TrackType.text, 'SY')

    def addBgm(self):
        audio_bgm = draft.AudioMaterial(os.path.join(self.bgm_dir, self.bgm))
        audio_bgm_lenth = audio_bgm.duration
        self.script.add_material(audio_bgm)
        audio_bgm_segment = draft.AudioSegment(audio_bgm, trange(0, self.nowS),volume=0.2)
        audio_bgm_segment.add_fade("1s", "1s")
        self.script.add_segment(audio_bgm_segment, 'BGM')
        # 水印
        TextSegment = draft.TextSegment("时间在走、", trange(0, self.nowS),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    border=draft.TextBorder(alpha=0.2,color=(0, 0, 0)),
                                    clip_settings=draft.ClipSettings(transform_x=-0.85,transform_y=0.90, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
        TextSegment.add_animation(TextIntro.冰雪飘动, 1500000)
        TextSegment.add_animation(TextOutro.渐隐, 500000)
        self.script.add_segment(TextSegment, 'SY')
                # 诗词背景
        video_material = draft.VideoMaterial(os.path.join(self.bgv_dir, self.bgv))
        video_duration = video_material.duration
        self.script.add_material(video_material)
        video_segment = draft.VideoSegment(material = video_material,
                                                        target_timerange  = trange(0, int(self.nowS) + 500000),
                                                        volume=0)
        self.script.add_segment(video_segment, 'BGVC')
        
    def addTitle(self):
        AudioMaterial = draft.AudioMaterial(os.path.join(self.output_dir, 'audioAlg/t0.mp3'))
        audio_duration = AudioMaterial.duration
        self.script.add_material(AudioMaterial)
        AudioSegment = draft.AudioSegment(AudioMaterial,
                                    trange(self.nowS, audio_duration),
                                    volume=1)
        self.script.add_segment(AudioSegment, 'TTS')
        self.nowS += audio_duration + 500000
        titleJson = os.path.join(self.output_dir, 'json/title.json')
        with open(titleJson, 'r', encoding='utf-8') as f:
            data = json.load(f)
            title = data.get('title')
        segments = [segment for segment in title.split('，') if segment]
        total_length = len(title)
        list = [[segment, round(len(segment) / total_length, 3)] for segment in segments]
        for key, (segment, ratio) in enumerate(list):
                    if key == 0:
                        start = 0
                        duration = AudioMaterial.duration
                        animation_duration = ratio * AudioMaterial.duration / 2
                        fixed_y = 0.2
                    else:
                        start = AudioMaterial.duration * list[key-1][1]
                        duration = AudioMaterial.duration * ratio
                        animation_duration = ratio * AudioMaterial.duration / 4
                        fixed_y = -0.2
                    TextSegment = draft.TextSegment(list[key][0], trange(start, duration),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                  font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                  style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                  clip_settings=draft.ClipSettings(transform_y=fixed_y))          # 模拟字幕的位置
                    TextSegment.add_animation(TextIntro.金粉飘落, animation_duration)
                    TextSegment.add_animation(TextOutro.渐隐, animation_duration/2)
                    self.script.add_segment(TextSegment, 'T' + str(key))
        video_material = draft.VideoMaterial(os.path.join(self.bgv_dir, "金粉向右飘.mp4"))
        video_duration = video_material.duration
        self.script.add_material(video_material)
        video_segment = draft.VideoSegment(video_material,
                                    trange(0, self.nowS),
                                    volume=0)
        self.script.add_segment(video_segment, 'BGV')
        
    
    def addItem(self) -> str:
        with open(os.path.join(self.output_dir, "json/item.json"), 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            json_data = json_data['lists']
        for key, item in json_data.items() if isinstance(json_data, dict) else enumerate(json_data):
            # 音频素材
            itemPeiyinNow = self.nowS
            audio_duration = 0
            for i in range(10):
                if os.path.exists(os.path.join(self.output_dir, f"audioAlg/{item['peiyin']}{i}.mp3")):
                    AudioMaterial = draft.AudioMaterial(os.path.join(self.output_dir, f"audioAlg/{item['peiyin']}{i}.mp3"))
                    audio_length = AudioMaterial.duration
                    
                    self.script.add_material(AudioMaterial)
                    AudioSegment = draft.AudioSegment(AudioMaterial,
                                    trange(int(itemPeiyinNow), int(audio_length)),
                                    volume=1)
                    self.script.add_segment(AudioSegment, 'TTS')
                    itemPeiyinNow += audio_length
                    audio_duration+=audio_length
            
            # 背景素材,分段定制
            
            # video_material = draft.VideoMaterial(os.path.join(self.output_dir, "bgloop.mp4"))
            # video_duration = video_material.duration
            # self.script.add_material(video_material)
            # video_segment = draft.VideoSegment(material = video_material,
            #                                             target_timerange  = trange(int(self.nowS), int(audio_duration) + 500000),
            #                                             source_timerange = trange(f"{random.randint(110,240)}s", int(audio_duration)),
            #                                             volume=0)
            # self.script.add_segment(video_segment, 'BGV')

            StickerSegment = draft.StickerSegment(
                resource_id = "7226264888031694091",
                target_timerange = trange(int(self.nowS), int(audio_duration) + 500000),
                clip_settings = draft.ClipSettings(
                    scale_x = 2,
                    scale_y = 0.25
                )
            )
            self.script.add_segment(StickerSegment, 'STK')
            # 字幕素材
            title = item['shiJuSplit']
            # title = '123|456'
            total_length = sum(len(segment) for segment in title)
            list = [[segment, round(len(segment) / total_length, 3)] for segment in title]
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
            TextSegment = draft.TextSegment(f"——{item['zuoZhe']}《{item['shiMing']}》", trange(self.nowS, int(audio_duration)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    border=draft.TextBorder(color=(0, 0, 0)),
                                    clip_settings=draft.ClipSettings(transform_y=-0.7, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
            TextSegment.add_animation(TextIntro.渐显, 500000)
            TextSegment.add_animation(TextOutro.渐隐, 500000)
            self.script.add_segment(TextSegment, 'ZZ')
            # 赏析
            TextSegment = draft.TextSegment(f"{item['shangXi']}", trange(self.nowS, int(audio_duration)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
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
                            start = self.nowS
                            duration = audio_duration
                            animation_duration = audio_duration / 4
                            fixed_x = split[splitNum]['fixed'][key][0]
                            fixed_y = split[splitNum]['fixed'][key][1]
                        else:
                            start = self.nowS + indent
                            duration = self.nowS + audio_duration - start
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
            self.nowS += audio_duration + 500000
        return 'Success'
    
    def addVideo(self, filename: str):
        video_material = draft.VideoMaterial(os.path.join(self.output_dir, filename))
        video_duration = video_material.duration
        self.script.add_material(video_material)
        video_segment = draft.VideoSegment(video_material,
                                    trange(0, self.nowS),
                                    volume=0)
        self.script.add_segment(video_segment, 'BGV')

    def dumpDraft(self):
        self.script.dump(self.DUMP_PATH + '/draft_content.json')
    
    def general_draft(self):
        try:
            self.addTitle()
            self.addItem()
            self.addBgm()
            # testObj.addVideo('bgv.mp4')
            self.dumpDraft()
            # 导出
            ctrl = draft.JianyingController()
            ctrl.export_draft("千古词帝李煜的巅峰之作", "C:/Users/Kinso/Desktop/tmp", resolution=ExportResolution.RES_1080P, framerate=ExportFramerate.FR_24)
            # 导出
        except Exception as e:
            print(f"生成草稿时发生错误: {str(e)}")
            raise
        return 'Success'
