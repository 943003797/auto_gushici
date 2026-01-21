import random, os, dashscope

from dashscope.audio.tts_v2 import SpeechSynthesizer

from dotenv import load_dotenv
load_dotenv()

class TTS:
    def __init__(self, voice_id: str = "风吟", speech_rate: float = 1.0)->bool:
        """
        初始化 TTS 实例

        参数:
            voice_id (str): 音色名称，默认 "风吟"；
                           支持传入映射表中的中文键，也可直接传 DashScope 的 voice_id。
            out_path (str): 默认输出目录，可在调用 textToAudio 时单独指定。
        """
        voice_id_map = {
            "风吟": "cosyvoice-v3-plus-bailian-e33a49563ae84b25880a6e0caee9de9b",
            "刘涛": "cosyvoice-v3-plus-bailian-e67cf27a251148e3ac712a2a442d704a",
        }
        self.voice_id = voice_id_map.get(voice_id, voice_id)
        self.speech_rate = speech_rate
        
    def textToAudio(self, text: str = "", out_path: str = "") -> bool:
        dashscope.api_key = os.getenv("ALI_KEY")
        synthesizer = SpeechSynthesizer(
            model = "cosyvoice-v3-plus",
            voice = self.voice_id,
            speech_rate = self.speech_rate,
            additional_params={"bit_rate": 64}, 
            seed = random.randint(0, 65535),
            language_hints = ["zh"]
        )
        audio_result = synthesizer.call(text)
        try:
            with open(out_path, "wb") as f:
                if audio_result is not None:
                    f.write(audio_result)
                else:
                    raise Exception("General audio failed")
            return True
        except Exception as e:
            return False