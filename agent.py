import os, asyncio, json
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from pydantic import BaseModel, Field
from dotenv import load_dotenv

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
        shiju: str = Field(description="诗句")
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
        基于用户提供的主题，找至少2首最符合主题的诗词，摘选每首精华部分（一般为上下整句）。
        严格按照以下JSON格式返回结果，不要包含任何额外信息：
        {
            [
                {
                    "id": "1",
                    "shiju": "问君能有几多愁，恰似一江春水向东流。",
                    "shiming": "虞美人",
                    "zuozhe": "李煜",
                    "yiwen": "请问你有多少愁苦？正像那滔滔江水向东流去一样。"
                },
                {
                    "id": "2",
                    "shiju": "国破山河在，城春草木深。",
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

# Test
if __name__ == "__main__":
    asyncio.run(general_poetry("千古词帝李煜的巅峰之作"))