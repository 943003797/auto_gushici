import os, json
import pyJianYingDraft as draft
from pyJianYingDraft import TextIntro, TextOutro, Text_loop_anim, Mask_type, VideoSceneEffectType, animation, IntroType, OutroType, Transition_type, trange, GroupAnimationType, TransitionType
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
        self.sfx_dir = "./material/sfx/"
        self.bgp_dir = os.getenv("DRAFT_DIR") + self.title + "/Resources/image/"
        self.output_dir = os.getenv("DRAFT_DIR") + self.title
        self.bgm = bgm
        self.bgv = bgv
        self.audioNowTime = 0
        self.textNowTime = 0

        self.script = draft.ScriptFile(1920, 1080)
        self.script.add_track(draft.TrackType.text, 'SY')
        self.script.add_track(draft.TrackType.text, 'TITLE')
        self.script.add_track(draft.TrackType.audio, 'BGM')
        self.script.add_track(draft.TrackType.audio, 'WENAN_AUDIO')
        self.script.add_track(draft.TrackType.audio, 'TTS')
        self.script.add_track(draft.TrackType.audio, 'SOUND')
        self.script.add_track(draft.TrackType.sticker, 'STK')
        self.script.add_track(draft.TrackType.video, 'BGV', mute= True, relative_index=0)
        self.script.add_track(draft.TrackType.video, 'BDTOP', mute= True, relative_index=1)
        self.script.add_track(draft.TrackType.video, 'BDBOT', mute= True, relative_index=1)
        self.script.add_track(draft.TrackType.text, 'WENAN')
        self.script.add_track(draft.TrackType.text, 'DANMU')
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
        # Title
        TextSegment = draft.TextSegment(self.title, trange(0, self.audioNowTime),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    border=draft.TextBorder(alpha=0.2,color=(0, 0, 0)),
                                    clip_settings=draft.ClipSettings(transform_x=0.765,transform_y=0.90, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
        TextSegment.add_animation(TextIntro.冰雪飘动, 1500000)
        TextSegment.add_animation(TextOutro.渐隐, 500000)
        self.script.add_segment(TextSegment, 'TITLE')

        # 水印
        TextSegment = draft.TextSegment("和光同尘、", trange(0, self.audioNowTime),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    border=draft.TextBorder(alpha=0.2,color=(0, 0, 0)),
                                    clip_settings=draft.ClipSettings(transform_x=-0.765,transform_y=0.90, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
        TextSegment.add_animation(TextIntro.冰雪飘动, 1500000)
        TextSegment.add_animation(TextOutro.渐隐, 500000)
        self.script.add_segment(TextSegment, 'SY')

        #边框
        video_material = draft.VideoMaterial("./material/border/border.png")
        video_duration = video_material.duration
        self.script.add_material(video_material)
        video_segment = draft.VideoSegment(material = video_material,
                                                        target_timerange  = trange(0, self.audioNowTime),
                                                        volume=0
                                                        )
        video_segment.add_animation(IntroType.渐显, 300000)
        video_segment.add_animation(OutroType.渐隐, 300000)
        self.script.add_segment(video_segment, 'BDTOP')

    def addItem(self) -> str:
        for key,item in enumerate(self.list):
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
                if(key%2 != 1):
                  video_segment.add_transition(TransitionType.叠化, duration = 100000)
                # video_segment.add_animation(IntroType.渐显, 100000)
                # video_segment.add_animation(OutroType.渐隐, 100000)
                # 交替使用BGV1和BGV2轨道
                track_name = 'BGV'
                self.script.add_segment(video_segment, track_name)

                # 字幕
                TextSegment = draft.TextSegment(f"{item['text']}", trange(int(itemPeiyinNow), int(audio_length)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                        font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                        style=draft.TextStyle(color=(1, 1, 1), size=10),                # 设置字体颜色为黄色
                                        border=draft.TextBorder(color=(0, 0, 0)),
                                        clip_settings=draft.ClipSettings(transform_y=-0.92, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
                TextSegment.add_animation(TextIntro.渐显, 500000)
                TextSegment.add_animation(TextOutro.渐隐, 500000)
                self.script.add_segment(TextSegment, 'WENAN')

                # 弹幕
                if item['danmu']:
                  match item['danmu_style']:
                    case 'middle':
                      TextSegment = draft.TextSegment(f"{item['danmu']}", trange(int(itemPeiyinNow), int(audio_length)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新） 
                                      font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                      style=draft.TextStyle(color=(1, 0.752, 0.239), size=16),                # 设置字体颜色为黄色
                                      # border=draft.TextBorder(color=(0, 0, 0)),
                                      clip_settings=draft.ClipSettings(transform_y=0, transform_x=0, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
                      TextSegment.add_animation(TextIntro.辉光, 1000000)
                      TextSegment.add_animation(TextOutro.渐隐, 1000000)
                      self.addSound(sfx="字幕显示短促.mp3")
                    case 'top':
                      TextSegment = draft.TextSegment(f"{item['danmu']}", trange(int(itemPeiyinNow), int(audio_length)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新） 
                                      font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                      style=draft.TextStyle(color=(1, 1, 1), size=14),                # 设置字体颜色为黄色
                                      # border=draft.TextBorder(color=(0, 0, 0)),
                                      clip_settings=draft.ClipSettings(transform_y=-0.92, transform_x=0, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
                      TextSegment.add_animation(TextIntro.辉光, 1000000)
                      TextSegment.add_animation(TextOutro.渐隐, 1000000)
                    case 'bottom':
                      item['danmu'] = f"""{item['danmu']}"""
                      # 统计item['danmu']中的换行符数量
                      newline_count = item['danmu'].count('\n')
                      print(f"当前弹幕换行符数量: {newline_count}")
                      TextSegment = draft.TextSegment(item['danmu'], trange(int(itemPeiyinNow), int(audio_length)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新） 
                                      font=draft.FontType.三极行楷简体_粗,
                                      border=draft.TextBorder(color=(0.172, 0.184, 0.231)),
                                      style=draft.TextStyle(
                                        color=(1, 0.752, 0.239),
                                        size=14,
                                        align=3,
                                        line_spacing = 10,
                                        letter_spacing = 4),                # 设置字体颜色为黄色
                                      # border=draft.TextBorder(color=(0, 0, 0)),
                                      clip_settings=draft.ClipSettings(transform_y=-0.65, transform_x=0, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
                      TextSegment.add_animation(TextIntro.星光闪闪, 1000000)
                      TextSegment.add_animation(TextOutro.渐隐, 1000000)
                      self.addSound(sfx="字幕显示短促.mp3")
                    case 'left':
                      item['danmu'] = f"""{item['danmu']}"""
                      # 统计item['danmu']中的换行符数量
                      newline_count = item['danmu'].count('\n')
                      print(f"当前弹幕换行符数量: {newline_count}")
                      TextSegment = draft.TextSegment(item['danmu'], trange(int(itemPeiyinNow), int(audio_length)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新） 
                                      font=draft.FontType.三极行楷简体_粗,
                                      border=draft.TextBorder(color=(0.172, 0.184, 0.231)),
                                      style=draft.TextStyle(
                                        color=(1, 0.752, 0.239),
                                        size=14,
                                        align=3,
                                        vertical=True,
                                        line_spacing = 10,
                                        letter_spacing = 4),                # 设置字体颜色为黄色
                                      # border=draft.TextBorder(color=(0, 0, 0)),
                                      clip_settings=draft.ClipSettings(transform_y=0, transform_x=-0.70, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
                      TextSegment.add_animation(TextIntro.打字机_II, 3000000)
                      TextSegment.add_animation(TextOutro.渐隐, 1000000)
                      self.addSound(sfx="字幕显示短促.mp3")
                    case 'right':
                      item['danmu'] = f"""{item['danmu']}"""
                      # 统计item['danmu']中的换行符数量
                      newline_count = item['danmu'].count('\n')
                      print(f"当前弹幕换行符数量: {newline_count}")
                      TextSegment = draft.TextSegment(f"{item['danmu']}", trange(int(itemPeiyinNow), int(audio_length)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新） 
                                      font=draft.FontType.三极行楷简体_粗,
                                      border=draft.TextBorder(color=(0.172, 0.184, 0.231)),
                                      style=draft.TextStyle(
                                        color=(1, 0.752, 0.239),
                                        size=14,
                                        align=3,
                                        vertical=True,
                                        line_spacing = 10,
                                        letter_spacing = 4),                # 设置字体颜色为黄色
                                      # border=draft.TextBorder(color=(0, 0, 0)),
                                      clip_settings=draft.ClipSettings(transform_y=0, transform_x=0.90 - 0.06 * newline_count, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
                      TextSegment.add_animation(TextIntro.打字机_II, 3000000)
                      TextSegment.add_animation(TextOutro.渐隐, 1000000)
                      self.addSound(sfx="字幕显示短促.mp3")
                  
                  self.script.add_segment(TextSegment, 'DANMU')


                # 重置剪辑进度
                itemPeiyinNow += audio_length
                audio_duration+=audio_length
                print(audio_duration/500000)
                self.audioNowTime += audio_duration
        return 'Success'
    def addSound(self, sfx: str = "字幕显示短促.mp3"):
        if os.path.exists(os.path.join(self.sfx_dir, sfx)):
          AudioMaterial = draft.AudioMaterial(os.path.join(self.sfx_dir, sfx))
          sfx_audio_length = AudioMaterial.duration
          self.script.add_material(AudioMaterial)
          AudioSegment = draft.AudioSegment(AudioMaterial,
                          trange(int(self.audioNowTime), int(sfx_audio_length)),
                          volume=0.4)
          self.script.add_segment(AudioSegment, 'SOUND')

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