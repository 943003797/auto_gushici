import os, requests, time, json

from dotenv import load_dotenv
load_dotenv()

class TTS:
    def __init__(self, voice_id: str = "风吟磁性")->bool:
        """
        初始化 TTS 实例

        参数:
            voice_id (str): 音色名称，默认 "风吟"；
                           支持传入映射表中的中文键，也可直接传 DashScope 的 voice_id。
            out_path (str): 默认输出目录，可在调用 textToAudio 时单独指定。
        """
        voice_id_map = {
            "少女朗诵": "ttv-voice-2026012923280026-QF1iIMuq",
        }
        self.voice_id = voice_id_map.get(voice_id, voice_id)
        
    def textToAudio(self, text: str = "", out_path: str = "") -> bool:
        payload = {
            "model": "speech-2.6-turbo",
            "text": text,
            "voice_setting": {
                "voice_id": self.voice_id,
                "speed": 1,
                "vol": 1,
                "pitch": 0
            },
            "audio_setting": {
                "audio_sample_rate": 16000,
                "bitrate": 128000,
                "format": "mp3",
                "channel": 2
            },
            # "pronunciation_dict": { "tone": ["危险/dangerous"] },
            # "language_boost": "auto",
            "voice_modify": {
                "pitch": 0,
                "intensity": 0,
                "timbre": -2,
                # "sound_effects": "spacious_echo"
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('MINIMAX_KEY')}"
        }
        url = "https://api.minimaxi.com/v1/t2a_async_v2"
        audio_result = requests.post(url, json=payload, headers=headers)
        audio_result = json.loads(audio_result.text)
        task_id = audio_result["task_id"]
        file_id = audio_result["file_id"]
        # 轮询任务状态，每秒调用一次 get_general_status
        while True:
            status = self.get_general_status(task_id=task_id)
            print(f"当前任务状态: {status}")
            if status is True:          # 任务成功
                break
            time.sleep(1)                 # 等待 1 秒后继续查询

        url = f"https://api.minimaxi.com/v1/files/retrieve?file_id={file_id}"
        headers = {"Authorization": f"Bearer {os.getenv('MINIMAX_KEY')}"}
        # 任务成功后，获取音频文件数据
        response = requests.get(url, headers=headers)
        response = json.loads(response.text)
        # print(response["file"])
        # print(response["file"]["download_url"])
        fileUrl = response["file"]["download_url"]
        audioData = requests.get(fileUrl).content
        try:
            with open(out_path, "wb") as f:
                if audioData is not None:
                    f.write(audioData)
                else:
                    raise Exception("General audio failed")
            return True
        except Exception as e:
            return False

    def get_general_status(self, task_id: int = 0) -> dict:
        url = f"https://api.minimaxi.com/v1/query/t2a_async_query_v2?task_id={task_id}"
        headers = {"Authorization": f"Bearer {os.getenv('MINIMAX_KEY')}"}
        response = requests.get(url, headers=headers)
        response = response.json()
        if response["status"] == "Success":
            return True
        else:
            return False

if __name__ == "__main__":
    tts = TTS()
    tts.textToAudio(text="测试音频", out_path="test.mp3")