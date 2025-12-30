import os
import pyJianYingDraft as draft
from pyJianYingDraft import Intro_type, Transition_type, trange
from pyJianYingDraft import TextIntro, TextOutro, Text_loop_anim, Mask_type
from pyJianYingDraft import animation
from pyJianYingDraft.script_file import json
from dotenv import load_dotenv

load_dotenv()

class autoCut():

    def __init__(self, bgm: str = "", bgv: str = "", title: str = "", list: list = []):
        self.nowS = 0
        self.bgm = bgm
        self.bgv = bgv
        self.title = title
        self.list = list
        self.DUMP_PATH = os.getenv("DUMP_PATH")
        self.output_dir = os.getenv("DRAFT_DIR") + self.title
        self.tts_dir = os.getenv("DRAFT_DIR") + self.title + "/Resources/audioAlg/"
        self.bgm_dir = "material/bgm/"
        self.sfx_dir = "material/sfx/"
        self.bgv_dir = "material/bgv/"
        self.script = draft.ScriptFile(1920, 1080)
        self.script.add_track(draft.TrackType.audio, 'TTS')
        self.script.add_track(draft.TrackType.audio, 'BGM')
        self.script.add_track(draft.TrackType.audio, 'SFX')
        self.script.add_track(draft.TrackType.video, 'BGV', mute= True, relative_index=8)
        self.script.add_track(draft.TrackType.video, 'BGVC', mute= True, relative_index=0)
        self.script.add_track(draft.TrackType.video, 'BGP0', mute= True, relative_index=1)
        self.script.add_track(draft.TrackType.video, 'BGP1', mute= True, relative_index=2)
        self.script.add_track(draft.TrackType.video, 'BGP2', mute= True, relative_index=3)
        self.script.add_track(draft.TrackType.video, 'BGP3', mute= True, relative_index=4)
        self.script.add_track(draft.TrackType.video, 'BGP4', mute= True, relative_index=5)
        self.script.add_track(draft.TrackType.video, 'BGP5', mute= True, relative_index=6)
        self.script.add_track(draft.TrackType.video, 'BGP6', mute= True, relative_index=7)
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
        audio_bgm_segment = draft.AudioSegment(audio_bgm, trange(0, self.nowS),volume=0.4)
        audio_bgm_segment.add_fade("0.2s", "1s")
        self.script.add_segment(audio_bgm_segment, 'BGM')
        # 水印
        TextSegment = draft.TextSegment("和光同尘、", trange(0, self.nowS),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    border=draft.TextBorder(alpha=0.2,color=(0, 0, 0)),
                                    clip_settings=draft.ClipSettings(transform_x=-0.85,transform_y=0.90, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
        TextSegment.add_animation(TextIntro.冰雪飘动, 1500000)
        TextSegment.add_animation(TextOutro.渐隐, 500000)
        # self.script.add_segment(TextSegment, 'SY')
        #诗词背景
        video_material = draft.VideoMaterial(os.path.join(self.bgv_dir, self.bgv))
        video_duration = video_material.duration
        self.script.add_material(video_material)
        video_segment = draft.VideoSegment(material = video_material,
                                                        target_timerange  = trange(0, int(self.nowS) + 500000),
                                                        volume=0)
        self.script.add_segment(video_segment, 'BGVC')
    
    def addSubTitle(self, title: str):
        TextSegment = draft.TextSegment(title, trange(0, self.nowS),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    border=draft.TextBorder(alpha=0.2,color=(0, 0, 0)),
                                    clip_settings=draft.ClipSettings(transform_x=-0.85,transform_y=0.90, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
        TextSegment.add_animation(TextIntro.冰雪飘动, 1500000)
        TextSegment.add_animation(TextOutro.渐隐, 500000)
        self.script.add_segment(TextSegment, 'SY')

    def addTitle(self):
        # AudioMaterial = draft.AudioMaterial(os.path.join(self.tts_dir, 'title.mp3'))
        # audio_duration = AudioMaterial.duration
        # self.script.add_material(AudioMaterial)
        # AudioSegment = draft.AudioSegment(AudioMaterial,
        #                             trange(self.nowS, audio_duration),
        #                             volume=1)
        # self.script.add_segment(AudioSegment, 'TTS')
        # self.nowS += audio_duration + 500000
        title = self.title
        segments = [segment for segment in title.split('，') if segment]
        total_length = len(title)
        list = [[segment, round(len(segment) / total_length, 3)] for segment in segments]
        titleSplitCount = len(list)
        #一级标题展示
        for key, (segment, ratio) in enumerate(list):
                    # if key == 0:
                    #     start = 0
                    #     duration = AudioMaterial.duration
                    #     animation_duration = ratio * AudioMaterial.duration / 2
                    #     fixed_y = 0.2
                    # else:
                    #     start = AudioMaterial.duration * list[key-1][1]
                    #     duration = AudioMaterial.duration * ratio
                    #     animation_duration = ratio * AudioMaterial.duration / 4
                    #     fixed_y = -0.2
                    TextColor = (1, 0.27450980392156865, 0.12549019607843137) if key%2 == 1 else (1, 1, 1)
                    duration = titleSplitCount * 500000 - key * 500000 + 1000000
                    TextSegment = draft.TextSegment(list[key][0], trange(0 + key * 500000, duration),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                  font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                  style=draft.TextStyle(color= TextColor),                # 设置字体颜色为黄色
                                  clip_settings=draft.ClipSettings(transform_y=0.4 - key * 0.3))          # 模拟字幕的位置
                    TextSegment.add_animation(TextIntro.星光闪闪, 500000)
                    TextSegment.add_animation(TextOutro.渐隐, 300000)
                    self.script.add_segment(TextSegment, 'T' + str(key))
        self.nowS = titleSplitCount * 500000 + 1000000
        #二级标题
        TextSegment = draft.TextSegment("绝美 · 诗词", trange(self.nowS, 1500000),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                        font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                        style=draft.TextStyle(color= (1, 0.27450980392156865, 0.12549019607843137), size=15),                # 设置字体颜色为黄色
                        clip_settings=draft.ClipSettings(transform_y=0))          # 模拟字幕的位置
        TextSegment.add_animation(TextIntro.电光, 800000)
        TextSegment.add_animation(TextOutro.渐隐, 300000)
        self.script.add_segment(TextSegment, 'T' + str(key))
        #音效
        AudioMaterial = draft.AudioMaterial(os.path.join(self.sfx_dir, '电流.mp3'))
        self.script.add_material(AudioMaterial)
        AudioSegment = draft.AudioSegment(AudioMaterial,
                                    trange(self.nowS, 1000000),
                                    volume=0.10)
        self.script.add_segment(AudioSegment, 'SFX')

        self.nowS = self.nowS + 1500000
    
        video_material = draft.VideoMaterial(os.path.join(self.bgv_dir, "金粉向右飘.mp4"))
        video_duration = video_material.duration
        self.script.add_material(video_material)
        video_segment = draft.VideoSegment(video_material,
                                    trange(0, self.nowS),
                                    volume=0)
        self.script.add_segment(video_segment, 'BGV')
        
    
    def addItem(self) -> str:
        json_data = self.list
        for key, item in json_data.items() if isinstance(json_data, dict) else enumerate(json_data):
            # 音频素材
            itemPeiyinNow = self.nowS
            audio_duration = 0
            for i in range(10):
                if os.path.exists(os.path.join(self.tts_dir, f"{item['id']}_{i}.mp3")):
                    AudioMaterial = draft.AudioMaterial(os.path.join(self.tts_dir, f"{item['id']}_{i}.mp3"))
                    audio_length = AudioMaterial.duration
                    
                    self.script.add_material(AudioMaterial)
                    AudioSegment = draft.AudioSegment(AudioMaterial,
                                    trange(int(itemPeiyinNow), int(audio_length)),
                                    volume=1.5)
                    self.script.add_segment(AudioSegment, 'TTS')
                    itemPeiyinNow += audio_length
                    audio_duration+=audio_length
            
            # 背景素材,分段定制
            
            # video_material = draft.VideoMaterial(os.path.join(self.bgv_dir, "bgloop.mp4"))
            # video_duration = video_material.duration
            # self.script.add_material(video_material)
            # video_segment = draft.VideoSegment(material = video_material,
            #                                             target_timerange  = trange(int(self.nowS), int(audio_duration) + 500000),
            #                                             source_timerange = trange(f"{random.randint(110,240)}s", int(audio_duration)),
            #                                             volume=0)
            # self.script.add_segment(video_segment, 'BGV')

            # 蒙版贴纸
            StickerSegment = draft.StickerSegment(
                resource_id = "7226264888031694091",
                target_timerange = trange(int(self.nowS), int(audio_duration) + 250000),
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
            TextSegment = draft.TextSegment(f"——{item['zuozhe']}《{item['shiming']}》", trange(self.nowS, int(audio_duration)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    border=draft.TextBorder(color=(0, 0, 0)),
                                    clip_settings=draft.ClipSettings(transform_y=-0.7, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
            TextSegment.add_animation(TextIntro.随机上升, 1300000)
            TextSegment.add_animation(TextOutro.渐隐, 250000)
            self.script.add_segment(TextSegment, 'ZZ')
            # 赏析
            TextSegment = draft.TextSegment(f"{item['yiwen']}", trange(self.nowS, int(audio_duration)),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=(1, 1, 1)),                # 设置字体颜色为黄色
                                    border=draft.TextBorder(color=(0, 0, 0)),
                                    clip_settings=draft.ClipSettings(transform_y=-0.85, scale_x=0.45, scale_y=0.45))          # 模拟字幕的位置
            TextSegment.add_animation(TextIntro.随机上升, 1500000)
            TextSegment.add_animation(TextOutro.渐隐, 250000)
            self.script.add_segment(TextSegment, 'SX')
            indent = 250000
            for key, item in enumerate(list):
                        if key == 0:
                            start = self.nowS
                            duration = audio_duration
                            animation_duration = audio_duration / 4
                            print(splitNum)
                            fixed_x = split[splitNum]['fixed'][key][0]
                            fixed_y = split[splitNum]['fixed'][key][1]
                        else:
                            start = self.nowS + indent
                            duration = self.nowS + audio_duration - start
                            animation_duration = audio_duration / 4
                            fixed_x = split[splitNum]['fixed'][key][0]
                            fixed_y = split[splitNum]['fixed'][key][1]
                        TextColor = (1, 0.27450980392156865, 0.12549019607843137) if key%2 == 1 else (1, 1, 1)
                        TextSegment = draft.TextSegment(list[key][0], trange(start, duration),  # 文本将持续整个视频（注意script.duration在上方片段添加到轨道后才会自动更新）
                                    font=draft.FontType.三极行楷简体_粗,                                  # 设置字体为文轩体
                                    style=draft.TextStyle(color=TextColor),                # 设置字体颜色为黄色
                                    clip_settings=draft.ClipSettings(transform_x=fixed_x, transform_y=fixed_y))          # 模拟字幕的位置
                        TextSegment.add_animation(TextIntro.冰雪飘动, animation_duration)
                        TextSegment.add_animation(TextOutro.渐隐, animation_duration/3)
                        self.script.add_segment(TextSegment, 'T' + str(key))
                        indent += 250000
            print(audio_duration/250000)
            self.nowS += audio_duration + 250000
        return 'Success'
    
    def addVideo(self, filename: str):
        video_material = draft.VideoMaterial(os.path.join(self.bgv_dir, filename))
        video_duration = video_material.duration
        self.script.add_material(video_material)
        video_segment = draft.VideoSegment(video_material,
                                    trange(0, self.nowS),
                                    volume=0)
        self.script.add_segment(video_segment, 'BGV')

    def dumpDraft(self):
        self.script.dump(self.output_dir + '/draft_content.json')
    
    def general_draft(self, title: str = ""):
        try:
            self.addTitle()
            self.addItem()
            self.addBgm()
            # testObj.addVideo('bgv.mp4')
            self.dumpDraft()
            # # 导出
            # ctrl = draft.JianyingController()
            # ctrl.export_draft("千古词帝李煜的巅峰之作", "C:/Users/Kinso/Desktop/tmp", resolution=ExportResolution.RES_1080P, framerate=ExportFramerate.FR_24)
            # 导出
        except Exception as e:
            print(f"生成草稿时发生错误: {str(e)}")
            raise
        return True

if __name__ == "__main__":
    list = [
{
    "id": "1",
    "shangju": "雄关漫道真如铁",
    "xiaju": "而今迈步从头越",
    "shiming": "忆秦娥·娄山关",
    "zuozhe": "毛泽东",
    "yiwen": "雄伟的关隘纵然坚如钢铁，如今我们昂首阔步，重新跨越。"
},
{
"id": "2",
"shangju": "大鹏一日同风起",
"xiaju": "扶摇直上九万里",
"shiming": "上李邕",
"zuozhe": "李白",
"yiwen": "大鹏乘风而起，直冲九万里高空。"
},{
    "id": "3",
    "shangju": "即今江海一归客",
    "xiaju": "他日云霄万里人",
    "shiming": "送裴处士应制举诗",
    "zuozhe": "刘禹锡",
    "yiwen": "如今只是江湖归隐之人，来日定是翱翔云霄的万里英才。"
},
{
"id": "4",
"shangju": "追风赶月莫停留",
"xiaju": "平芜尽处是春山",
"shiming": "励志句",
"zuozhe": "佚名",
"yiwen": "一路疾行莫停歇，平坦荒野尽头便是春意盎然的青山。"
},
{
"id": "5",
"shangju": "苦尽甘来终有时",
"xiaju": "一路向阳待花期",
"shiming": "励志句",
"zuozhe": "佚名",
"yiwen": "苦难终会过去，甘甜必将到来；只要心向阳光，静待花开时节。"
},
{
"id": "6",
"shangju": "关关难过关关过",
"xiaju": "前路漫漫亦灿灿",
"shiming": "励志句",
"zuozhe": "佚名",
"yiwen": "每一关都难，但都能闯过；前路虽远，却光明灿烂。"
},
{
    "id": "7",
    "shangju": "万里腾飞仍有路",
    "xiaju": "莫愁四海正风尘",
    "shiming": "舟中忆邵景说寄张子退",
    "zuozhe": "夏完淳",
    "yiwen": "纵有万里征程，前路依然可通；不必忧愁天下纷扰，风尘终将落定。"
}
]
    # poetry_draft = autoCut(title="千古词帝李煜的巅峰之作", list=list, bgm='BGM_爱的供养_间奏.mp3', bgv='水墨山河.mp4')
    poetry_draft = autoCut(title="古人笔下，那些，砥砺前行的，励志诗句", list=list, bgm='wake.mp3', bgv='金粉向右飘.mp4')
    poetry_draft.general_draft()
