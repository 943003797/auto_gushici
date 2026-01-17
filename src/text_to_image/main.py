import requests, os

from dotenv import load_dotenv

load_dotenv()

url = "https://open.bigmodel.cn/api/paas/v4/images/generations"

prompt = """
中国水墨画，写意风格。画面上方大面积留白象征欲明的天空，零星淡墨点缀残星。画面下方泼墨成山峦或简陋居室，笔触苍劲。室内一点暖色微光（孤灯）与室外清冷的墨色形成对比。宣纸质感，墨气淋漓，空灵禅意。
"""

payload = {
    "model": "CogView-3-Flash",
    "prompt": prompt,
    "size": "1024x1024",
    "watermark_enabled": False
}
headers = {
    "Authorization": "Bearer " + (os.getenv("BIGMODEL_KEY") or ""),
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

import json

response_data = response.json()
if 'data' in response_data and len(response_data['data']) > 0:
    image_url = response_data['data'][0]['url']
    print(image_url)
    # 下载图片
    image_response = requests.get(image_url)
    with open("output.png", "wb") as f:
        f.write(image_response.content)
else:
    print("未找到图片URL")
    print(response.text)