import requests

url = "https://api.siliconflow.cn/v1/uploads/audio/voice"

files = { "1.wav": ("1.wav", open("1.wav", "rb")) }
payload = {
    "model": "IndexTeam/IndexTTS-2",
    "customName": "your-voice-name",
    "text": "在一无所知中, 梦里的一天结束了，一个新的轮回便会开始",
    "audio": "data:audio/mpeg;base64,aGVsbG93b3JsZA=="
}
headers = {"Authorization": "Bearer " + os.getenv("INDEXTTS_KEY")}

response = requests.post(url, data=payload, files=files, headers=headers)

print(response.text)