"""Agent 1: 文档解析专家 — 从简历+JD中提取结构化信息"""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from ..config import settings
from ..tools.resume_reader import read_resume_file
from .prompts import DOCUMENT_PARSER_PROMPT

_llm = init_chat_model(
    # model="deepseek-v4-flash",
    # api_key=settings.deepseek_api_key,
    model=settings.qwen_model_name,
    api_key=settings.siliconflow_api_key,
    base_url=settings.siliconflow_base_url,
    model_provider="openai",
    temperature=0.1,
)

parser_agent = create_agent(
    model=_llm,
    tools=[read_resume_file],
    system_prompt=DOCUMENT_PARSER_PROMPT,
)


async def parse_documents(resume_input: str, jd_text: str) -> str:
    """
    解析简历和JD文档

    Args:
        resume_input: 简历文件路径（PDF/DOCX/TXT）或纯文本内容
        jd_text: JD全文

    Returns:
        JSON 字符串（ParseResult格式）
    """
    query = f"""简历：
{resume_input}

JD：
{jd_text}"""
    result = await parser_agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    messages = result.get("messages", [])
    return messages[-1].content if messages else ""
