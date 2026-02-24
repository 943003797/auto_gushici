import random, os, dashscope, threading

from dashscope.audio.tts_v2 import SpeechSynthesizer, AudioFormat, ResultCallback

from dotenv import load_dotenv
load_dotenv()

class Callback(ResultCallback):
    def __init__(self, out_path: str):
        self.out_path = out_path
        self.file = None
        self.event = threading.Event()
        self.error = None
        
    def on_open(self):
        self.file = open(self.out_path, "wb")
        
    def on_complete(self):
        self.event.set()
        
    def on_error(self, message: str):
        print(f"语音合成出现异常：{message}")
        self.error = message
        self.event.set()
        
    def on_close(self):
        if self.file:
            self.file.close()
        
    def on_event(self, message):
        pass
        
    def on_data(self, data: bytes) -> None:
        if self.file:
            self.file.write(data)

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
            "刘涛慢速": "cosyvoice-v3-plus-bailian-bf14c1052cd3406c8d20234aa84bbc87",
            "周涛": "cosyvoice-v3-plus-bailian-03da774b17f2437c987ee2bd264ff157",
            "周涛flash": "cosyvoice-v3-flash-bailian-d8bf795f33844584bb099c0db119c669"
        }
        # self.voice_id = voice_id_map.get(voice_id, '周涛')
        self.voice_id = "cosyvoice-v3-plus-bailian-03da774b17f2437c987ee2bd264ff157"
        self.speech_rate = 1.10
        
    def textToAudio(self, text: str = "", out_path: str = "") -> bool:
        dashscope.api_key = os.getenv("ALI_KEY")
        dashscope.base_websocket_api_url = 'wss://dashscope.aliyuncs.com/api-ws/v1/inference'
        
        callback = Callback(out_path)
        
        synthesizer = SpeechSynthesizer(
            model = "cosyvoice-v3-plus",
            voice = self.voice_id,
            speech_rate = self.speech_rate,
            format = AudioFormat.WAV_44100HZ_MONO_16BIT,
            additional_params={"bit_rate": 128}, 
            seed = random.randint(0, 65535),
            language_hints = ["zh"],
            callback=callback,
        )
        
        synthesizer.call('<speak><break time="100ms"/>' + text + '。</speak>')
        
        callback.event.wait(timeout=30)
        
        if callback.error:
            return False
            
        return True
