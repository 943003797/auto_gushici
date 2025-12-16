import os, random, asyncio, json, dashscope

from dashscope.audio.tts_v2 import VoiceEnrollmentService, SpeechSynthesizer

from dotenv import load_dotenv

# Init env
load_dotenv()

def generate_audio_cosyvoiceV3(text: str = "", out_path: str = "") -> bool:
    dashscope.api_key = os.getenv("ALI_KEY")
    synthesizer = SpeechSynthesizer(
        model = "cosyvoice-v3-plus",
        voice = "cosyvoice-v3-plus-bailian-186316e2ef3e4cb09665af98872db566",
        speech_rate = 1.1,
        additional_params={"bit_rate": 64},
        seed = random.randint(0, 65535),
        language_hints = "zh"
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

# Test
if __name__ == "__main__":
    texts = '<speak><prosody rate="slow" pitch="medium">采菊东篱下，<break time="600ms"/>悠然见南山。</prosody></speak>'
    asyncio.run(generate_audio_cosyvoiceV3(text=texts, out_path="test.mp3"))