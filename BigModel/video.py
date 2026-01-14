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
                            从这个视频中，截取2到7秒最有意义的视频片段,输出用于分割的开始时间和结束时间（单位：秒）
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

if __name__ == "__main__":
    v = video()
    # 测试获取视频时长
    # duration = video.get_video_duration("D:/Material/video_tmp/161.mp4")
    # print(f"视频时长: {duration} 秒")
    
    # 测试获取视频标签
    tag = v.get_video_tag("D:/Material/video_tmp/3.mp4")
    print(f"视频标签: {tag}")
