from typing import Any


from agentscope.message._message_base import Msg


from agentscope.agent import ReActAgent, AgentBase
from agentscope.formatter import DashScopeChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg
from agentscope.model import OpenAIChatModel
import asyncio
import os
from dotenv import load_dotenv
from agentscope.message import TextBlock, ToolUseBlock
from agentscope.tool import ToolResponse, Toolkit, execute_python_code

# 加载 .env 文件中的环境变量
load_dotenv()

async def creating_react_agent() -> None:
    """创建一个 ReAct 智能体并运行一个简单任务。"""
    # 准备工具
    toolkit = Toolkit()
    toolkit.register_tool_function(execute_python_code)

    agent = ReActAgent(
        name="Jarvis",
        sys_prompt="你是一个名为 Jarvis 的助手",
        model=OpenAIChatModel(
            model_name="gpt-5-mini",
            api_key=os.environ["OPENAI_API_KEY"],
            stream=True,
            client_args={"base_url": "https://api3.wlai.vip/v1"}
        ),
        formatter=DashScopeChatFormatter(),
        toolkit=toolkit,
        memory=InMemoryMemory(),
    )

    msg = Msg(
        name="user",
        content="提供不超过90个字符的节选",
        role="user",
    )

    await agent(msg)


asyncio.run(creating_react_agent())