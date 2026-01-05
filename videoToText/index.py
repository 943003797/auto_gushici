from zai import ZhipuAiClient
import base64

client = ZhipuAiClient(api_key="f35ff2adf86a469ebe366f3f23f05e0f.ZAVA6V7XT6y1l2LL")  # 填写您自己的APIKey

img_path = "snippet/hudie.mp4"
with open(img_path, "rb") as img_file:
    img_base = base64.b64encode(img_file.read()).decode("utf-8")

response = client.chat.completions.create(
    model="glm-4.6v-flash",
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
                    "text": "总结其中权重最高的三个要素标签.和一句话总结视频内容.?"
                }
            ]
        }
    ],
    thinking={
        "type": "enabled"
    }
)
print(response.choices[0].message.content)