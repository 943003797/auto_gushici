import os
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools
from autogen_ext.tools.mcp import SseMcpToolAdapter, SseServerParams
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

gpt_5_mini = OpenAIChatCompletionClient(
    model="gpt-4.1-mini-2025-04-14",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
    )

class PoetryItem(BaseModel):
    id: str = Field(description="自增id")
    shiju: str = Field(description="诗句")
    shiming: str = Field(description="诗名")
    zuozhe: str = Field(description="作者")
    yiwen: str = Field(description="译文")

class Summary(BaseModel):
    poems: list[PoetryItem] = Field(description="诗词列表")

async def general_base_data(title: str = "") -> str:
    """单次对话模式，直接使用AssistantAgent进行一次性的问答，不使用团队聊天模式"""
    agent = AssistantAgent(
        name="single_turn_agent",
        model_client=gpt_5_mini,
        system_message="""
        基于用户提供的主题，找至少10首最符合主题的诗词，摘选每首精华部分（一般为上下整句）。
        严格按照以下JSON格式返回结果，不要包含任何额外信息：
        {
            "poems": [
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
        注意：poems是一个数组，包含多个诗词对象，每个对象都有id、shiju、shiming、zuozhe和yiwen字段。
        """,
        output_content_type=Summary,
        output_content_type_format="json_object",
        memory=None
    )
    # 直接运行agent进行单次对话
    result = await agent.run(task=title)
    # 将结果转换为JSON字符串格式输出
    import json
    content = result.messages[-1].content
    if isinstance(content, str):
        print(content)
    else:
        # 如果是对象，转换为JSON字符串
        return json.dumps(content.model_dump(), ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(general_base_data("千古词帝李煜的巅峰之作"))