import base64,os
from zai import ZhipuAiClient
from dotenv import load_dotenv
import cv2

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
                            "text": "简短一句话描述内容"
                        }
                    ]
                }
            ],
            thinking=self.thinking
        )
        return response.choices[0].message.content if response.choices else False

if __name__ == "__main__":
    video = video()
    # 测试获取视频时长
    duration = video.get_video_duration("D:/Material/split/358.mp4")
    print(f"视频时长: {duration} 秒")
    
    # 测试获取视频标签
    # tag = video.get_video_tag("D:/Material/split/358.mp4")
    # print(f"视频标签: {tag}")
