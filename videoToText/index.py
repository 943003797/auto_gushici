import base64,os
from zai import ZhipuAiClient
from dotenv import load_dotenv

load_dotenv()

client = ZhipuAiClient(api_key=os.getenv("BIG_MODEL"))  # 填写您自己的APIKey

class video:
    def __init__(self):
        self.model="glm-4.6v-flash"
        self.thinking={
            "type": "enabled"
        }

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
        return response.choices[0].message.content

if __name__ == "__main__":
    video = video()
    print(video.get_video_tag("D:/Material/split/358.mp4"))
