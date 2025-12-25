import requests, base64

payload = {
    "model": "IndexTeam/IndexTTS-2",
    "input": "大鹏一日同风起",
    "max_tokens": 2048,
    "references": [{"audio": "data:audio/wav;base64," + base64.b64encode(open("2.mp3", "rb").read()).decode()}],
    "response_format": "mp3",
    "sample_rate": 32000,
    "stream": True,
    "speed": 1,
    "gain": 0
}
headers = {"Authorization": "Bearer sk-kvexcgafqqjhfuhnwayfrtmcyuolmoaazrqelenmhkgaaazg","Content-Type": "application/json"}

response = requests.post("https://api.siliconflow.cn/v1/audio/speech", json=payload, headers=headers)
with open("1.mp3", "wb") as f:
    f.write(response.content)

print(response.text)