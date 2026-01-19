import base64,os,json
from typing import Tuple
from zai import ZhipuAiClient
from dotenv import load_dotenv
import cv2
import re

load_dotenv()

client = ZhipuAiClient(api_key=os.getenv("BIG_MODEL"))  # 填写您自己的APIKey

class video:
    def __init__(self):
        self.model="glm-4.6v-flash"
        self.thinking={
            "type": "enabled"
        }

    def get_video_duration(self, video_path: str):
        """获取视频时长，单位为秒（整数）"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"无法打开视频文件: {video_path}")
                return None
            
            # 获取帧率
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0:
                print("无法获取视频帧率")
                cap.release()
                return None
            
            # 获取总帧数
            total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            
            # 计算时长（秒）
            duration = int(total_frames / fps)
            cap.release()
            return duration
        except Exception as e:
            print(f"获取视频时长失败: {e}")
            return None
    
    def get_video_resolution(self, video_path: str) -> Tuple[int, int]:
        """获取视频分辨率，返回(宽度, 高度)"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print(f"无法打开视频文件: {video_path}")
                return None, None
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            cap.release()
            return width, height
        except Exception as e:
            print(f"获取视频分辨率失败: {e}")
            return None, None

    def get_video_tag(self, video_path: str):
        with open(video_path, "rb") as img_file:
            img_base = base64.b64encode(img_file.read()).decode("utf-8")

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "video_url",
                            "video_url": {
                                "url": img_base
                            }
                        },
                        {
                            "type": "text",
                            "text": """
                            从这个视频中，截取3到9秒能表达视频核心意境的片段,输出用于分割的开始时间和结束时间（单位：秒）
                            按这个JSON格式输出：
                            {
                                "start": "",
                                "end": ""
                            }
                            """
                        }
                    ]
                }
            ],
            thinking=self.thinking
        )   
        raw = response.choices[0].message.content if response.choices else False
        if not raw:
            return False
        # 使用正则提取最外层{}中的JSON字符串
        match = re.search(r'\{.*\}', raw, flags=re.S)
        if match:
            try:
                json_str = match.group(0)
                parsed = json.loads(json_str)
                # 校验start和end字段值是否为数字
                if not (parsed.get('start').isdigit() and parsed.get('end').isdigit()):
                    return self.get_video_tag(video_path)
                # 校验start到end的时间是否超过9秒
                if int(parsed['end']) - int(parsed['start']) > 9:
                    return self.get_video_tag(video_path)
                # 校验必须字段及类型
                required_keys = {'start', 'end'}
                if not isinstance(parsed, dict) or not required_keys.issubset(parsed):
                    # 结构不符，重新调用本函数
                    return self.get_video_tag(video_path)
                # 校验字段值均为字符串
                for key in required_keys:
                    if not isinstance(parsed.get(key), str):
                        return self.get_video_tag(video_path)
                return parsed
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                return False
        return False

    def get_video_info_tag(self, video_path: str):
        with open(video_path, "rb") as img_file:
            img_base = base64.b64encode(img_file.read()).decode("utf-8")

        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "video_url",
                            "video_url": {
                                "url": img_base
                            }
                        },
                        {
                            "type": "text",
                            "text": """
                            给出视频的情绪标签（emotion）、场景标签（scene）、人物关系（person_relation）、互动标签（interaction）、抽象概念标签（abstract_concept）。
                            参考标签（必须从参考标签中分别选择出唯一一个权重最高的标签）：
                            情绪标签（emotion）： 平静|忧郁|豪迈|欢快|严肃|孤独|惆怅|温馨|沉重|激动|惊讶|思念
                            场景标签（scene）： 苍山|江海|大漠|云海|雨天|雪天|枯树|宫廷|院子|古道|古寺|书房|灯火|树林|市井|码头|田园
                            人物关系（person_relation）： 独处|好友|师徒|君臣|眷侣|路人
                            互动标签（interaction）： 书写|绘画|研墨|诵读|翻阅|对弈|抚琴|点香|对酌|独饮|行礼|相迎|赠别|挥手|远眺|观望|信步|游历|垂钓|采摘|耕作
                            抽象概念标签（abstract_concept）（提取时注意，视频注意视频是无声的）： 情感共鸣|时间流逝|留白艺术
                            tags： 合并情绪标签（emotion）、场景标签（scene）、人物关系（person_relation）、互动标签（interaction）、抽象概念标签（abstract_concept），用|分隔
                            按JSON格式输出(只输出JSON)：
                            {
                                "emotion": "标签",
                                "scene": "标签",
                                "person_relation": "关系",
                                "interaction": "标签",
                                "abstract_concept": "标签",
                                "tags": "标签",
                                "content": "以情绪标签、场景标签、人物关系、互动标签、抽象概念标签做参考,简短描述视频的主要内容"
                            }
                            """
                        }
                    ]
                }
            ],
            thinking=self.thinking
        )   
        raw = response.choices[0].message.content if response.choices else False
        print(raw)
        if not raw:
            return False
        # 使用正则提取最外层{}中的JSON字符串
        match = re.search(r'\{.*\}', raw, flags=re.S)
        if match:
            try:
                json_str = match.group(0)
                parsed = json.loads(json_str)
                # 校验必须字段及类型
                required_keys = {'emotion', 'scene', 'person_relation', 'interaction', 'abstract_concept', 'tags', 'content'}
                if not isinstance(parsed, dict) or not required_keys.issubset(parsed):
                    # 结构不符，重新调用本函数
                    return self.get_video_tag(video_path)
                # 校验字段值均为字符串
                for key in required_keys:
                    if not isinstance(parsed.get(key), str):
                        return self.get_video_tag(video_path)
                return parsed
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                return False
        return False
if __name__ == "__main__":
    v = video()
    # 测试获取视频时长
    # duration = video.get_video_duration("D:/Material/video_tmp/161.mp4")
    # print(f"视频时长: {duration} 秒")
    
    # 测试获取视频标签
    tag = v.get_video_tag("D:/Material/video_tmp/3.mp4")
    print(f"视频标签: {tag}")
