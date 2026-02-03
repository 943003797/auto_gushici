import base64,os,json,time
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
                            分析视频中的标签（必须从参考标签中分别选择出唯一一个权重最高的标签）：
                            人物正脸（positive_face）： 有|无
                            人物性别（person_gender）： 男|女|无
                            画面明亮度（brightness）： 明亮|中等|较暗
                            画面主体颜色（main_color）： 红色|淡红色|黄色|淡黄色|橙色|淡橙色|绿色|淡绿色|蓝色|淡蓝色|紫色|淡紫色|棕色|淡棕色|灰色|淡灰色|白色|淡白色|黑色|淡黑色|等
                            视频内容（content）： 描述视频的主要内容（只输出视频的主要内容，不输出其他内容）
                            按JSON格式输出(只输出JSON)：
                            {
                                "positive_face": "有|无",
                                "person_gender": "男|女|无",
                                "brightness": "明亮|中等|较暗",
                                "main_color": "红色|淡红色|黄色|淡黄色|橙色|淡橙色|绿色|淡绿色|蓝色|淡蓝色|紫色|淡紫色|棕色|淡棕色|灰色|淡灰色|白色|淡白色|黑色|淡黑色|等",
                                "emotion": "正面|中性|负面",
                                "content": "描述视频的主要内容（只输出视频的主要内容，不输出其他内容）"
                            }
                            """
                        }
                    ]
                }
            ],
            thinking=self.thinking
        )   
        raw = response.choices[0].message.content if response.choices else False
        print(f"raw: {raw}")
        if not raw:
            raw = {}
        # 使用正则提取最外层{}中的JSON字符串
        match = re.search(r'\{.*\}', raw, flags=re.S)
        if match:
            try:
                json_str = match.group(0)
                parsed = json.loads(json_str)
                # 校验必须字段及类型
                required_keys = {'positive_face', 'person_gender', 'brightness', 'main_color', 'emotion', 'content'}
                if not isinstance(parsed, dict) or not required_keys.issubset(parsed):
                    # 结构不符，重新调用本函数
                    time.sleep(2)
                    print(f"结构不符 sleep: 2")
                    return self.get_video_info_tag(video_path)
                # 校验字段值均为字符串
                for key in required_keys:
                    if not isinstance(parsed.get(key), str):
                        time.sleep(2)
                        print(f"字段值类型不符 sleep: 2")
                        return self.get_video_info_tag(video_path)
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
    tag = v.get_video_info_tag("D:/Material/video_tmp/56.mp4")
    print(f"{tag}")
    tag = v.get_video_info_tag("D:/Material/video_tmp/56.mp4")
    print(f"{tag}")
    tag = v.get_video_info_tag("D:/Material/video_tmp/56.mp4")
    print(f"{tag}")
