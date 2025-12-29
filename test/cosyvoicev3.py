import os, asyncio, json, dashscope, random
from dashscope.audio.tts_v2 import VoiceEnrollmentService, SpeechSynthesizer
from dashscope.audio.tts_v2.speech_synthesizer import json
from dotenv import load_dotenv

# Init env
load_dotenv()

def generate_audio_cosyvoiceV3(text: str = "", out_path: str = "") -> bool:
    dashscope.api_key = os.getenv("ALI_KEY")
    synthesizer = SpeechSynthesizer(
        model = "cosyvoice-v3-plus",
        voice = "cosyvoice-v3-plus-bailian-d52a1ddb0cbe4c79bf917fed46bda195",
        speech_rate = 0.95,
        additional_params={"bit_rate": 64},
        seed = random.randint(0, 65535)
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
txt = '<speak rate="2">我的语速比正常人快。</speak>'
# 对 txt 中的双引号进行转义，防止被误解析
txt_escaped = txt.replace('"', '\\"')
print(txt_escaped)


generate_audio_cosyvoiceV3(text=txt_escaped, out_path="test.mp3")
