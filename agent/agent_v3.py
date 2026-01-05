import os, asyncio, json, dashscope, random, base64, requests, time
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from pydantic import BaseModel, Field
from dashscope.audio.tts_v2 import VoiceEnrollmentService, SpeechSynthesizer
from dashscope.audio.tts_v2.speech_synthesizer import json
from dotenv import load_dotenv
from tts.cosyvoice.tts import TTS

# Init env
load_dotenv()

#Init LLM
gpt_5_mini = OpenAIChatCompletionClient(
    model="gpt-4.1-mini-2025-04-14",
    api_key=os.getenv("OPENAI_API_KEY") or "",
    base_url=os.getenv("OPENAI_BASE_URL") or "",
    )

# Define the output model
class poetryList(BaseModel):
    class PoetryItem(BaseModel):
        id: str = Field(description="自增id")
        shangju: str = Field(description="包含SSML标签的上句")
        xiaju: str = Field(description="包含SSML标签的下句")
        shiming: str = Field(description="诗名")
        zuozhe: str = Field(description="作者")
        yiwen: str = Field(description="译文")
    poetryList: list[PoetryItem] = Field(description="诗词列表")

# Define the agent
async def general_poetry(title: str = "") -> list:
    agent = AssistantAgent(
        name="single_turn_agent",
        model_client=gpt_5_mini,
        system_message="""
        基于用户提供的主题，找到6首最符合主题的诗词，摘选每首精华部分（一般为上下整句）。
        严格按照以下JSON格式返回结果，不要包含任何额外信息，yiwen不要太长，保持30字左右：
        {
            [
                {
                    "id": "1",
                    "shangju": "问君能有几多愁",
                    "xiaju": "恰似一江春水向东流",
                    "shiming": "虞美人",
                    "zuozhe": "李煜",
                    "yiwen": "请问你有多少愁苦？正像那滔滔江水向东流去一样。"
                },
                {
                    "id": "2",
                    "shangju": "国破山河在",
                    "xiaju": "城春草木深",
                    "shiming": "春望",
                    "zuozhe": "杜甫",
                    "yiwen": "国家沦陷只有山河依旧，春日的城区却荒芜残破。"
                }
            ]
        }  
        """,
        output_content_type=poetryList,
        output_content_type_format="json_object",
        memory=None
    )
    # Run agent once chat
    result = await agent.run(task=title)
    
    # 获取最后一条消息的内容
    if not result.messages:
        raise ValueError("Agent returned no messages")
    last_message = result.messages[-1]
    content = getattr(last_message, 'content', None)
    if content is None:
        raise ValueError("Last message has no content")
    
    # Python origin object to JSON
    json_content = json.dumps(content.model_dump(), ensure_ascii=False, indent=2)

    print(json_content)
    return json.loads(json_content)["poetryList"]

# Generate audio from text
def generate_audio_cosyvoiceV1(text: str = "", out_path: str = "") -> bool:
        dashscope.api_key = os.getenv("ALI_KEY")
        target_model = "cosyvoice-v1"
        voice_id = "cosyvoice-prefix-4eec46a3b5d8499a8c29c46766452a63"
        synthesizer = SpeechSynthesizer(model=target_model, voice=voice_id)
        audio_result = synthesizer.call(str(text))
        try:
            with open(out_path, "wb") as f:
                if audio_result is not None:
                    f.write(audio_result)
                else:
                    raise Exception("Geneal audio faild")
            return True
        except Exception as e:
            return False
# Generate audio from poetry
def generate_audio_cosyvoiceV3(text: str = "", out_path: str = "") -> bool:
    dashscope.api_key = os.getenv("ALI_KEY")
    synthesizer = SpeechSynthesizer(
        model = "cosyvoice-v3-plus",
        voice = "cosyvoice-v3-plus-bailian-d52a1ddb0cbe4c79bf917fed46bda195",
        speech_rate = 0.95,
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

def generate_audio_indextts2(text: str = "", out_path: str = "", reference_audio: str = "material/reference_audio/风吟.wav") -> bool:
    # 使用用户选择的参考音频文件，如果没有指定则使用默认文件
    if not os.path.exists(reference_audio):
        reference_audio = "material/reference_audio/风吟.wav"  # 回退到默认文件
    
    payload = {
        "model": "IndexTeam/IndexTTS-2",
        "input": text,
        "max_tokens": 2048,
        "references": [{"audio": "data:audio/wav;base64," + base64.b64encode(open(reference_audio, "rb").read()).decode()}],
        "response_format": "mp3",
        "sample_rate": 32000,
        "stream": True,
        "speed": 1,
        "gain": 0
    }
    headers = {"Authorization": f"Bearer {os.getenv('INDEXTTS_KEY')}","Content-Type": "application/json"}
    response = requests.post("https://api.siliconflow.cn/v1/audio/speech", json=payload, headers=headers)
    try:
        with open(out_path, "wb") as f: 
            f.write(response.content)
        return True
    except Exception as e:
        return False
async def generate_text(text: str = "", name: str = "", out_dir: str = "", reference_audio: str = "material/reference_audio/风吟.wav") -> bool:
    if not out_dir:
        out_dir = os.getenv("DRAFT_DIR") or ""
    generate_audio_indextts2(text=text + '。', out_path=f"{out_dir}/{name}", reference_audio=reference_audio)
    return True
async def generate_tts(title: str, wenan: str, poetry: str, out_dir: str = "", reference_audio: str = "material/reference_audio/风吟.wav") -> bool:
    if not out_dir:
        out_dir = os.getenv("DRAFT_DIR") or ""
    # generate_audio_cosyvoiceV3(text=title, out_path=f"{out_dir}/title.mp3")
    wenanList = wenan.split('，')
    for key, str in enumerate(wenanList):
        time.sleep(1)
        generate_audio_indextts2(text=str + '。', out_path=f"{out_dir}/wenan_{key}.mp3", reference_audio=reference_audio)
    if not poetry:
        return True
    print(poetry)
    for item in json.loads(poetry):
        shangju = item["shangju"]
        xiaju = item["xiaju"]
        generate_audio_indextts2(text=shangju + '。', out_path=f"{out_dir}/{item['id']}_1.mp3", reference_audio=reference_audio)
        time.sleep(1)
        generate_audio_indextts2(text=xiaju + '。', out_path=f"{out_dir}/{item['id']}_2.mp3", reference_audio=reference_audio)
        time.sleep(1)
    return True

# Test
if __name__ == "__main__":
    asyncio.run(general_poetry("千古词帝李煜的巅峰之作"))