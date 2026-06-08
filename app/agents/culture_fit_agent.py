"""Agent 3: 文化与业务匹配专家 — 搜索公司文化与业务方向，评估契合度"""

import json

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from ..config import settings
from ..tools.web_search import web_search
from .prompts import CULTURE_FIT_PROMPT

_llm = init_chat_model(
    # model="deepseek-v4-flash",
    # api_key=settings.deepseek_api_key,
    model=settings.deepseek_model_name,
    api_key=settings.siliconflow_api_key,
    base_url=settings.siliconflow_base_url,
    model_provider="openai",
    temperature=0.1,
)

culture_fit_agent = create_agent(
    model=_llm,
    tools=[web_search],
    system_prompt=CULTURE_FIT_PROMPT,
)


async def evaluate_culture_fit(parsed_resume: dict, parsed_jd: dict) -> dict:
    """
    评估文化匹配度

    Args:
        parsed_resume: 解析后的简历信息
        parsed_jd: 解析后的岗位信息

    Returns:
        agent result dict（含 messages）
    """
    company = parsed_jd.get("company_name", "未知公司")
    print(f"[Agent3] 目标公司: {company}", flush=True)
    print("[Agent3] 开始搜索公司文化与业务信息...", flush=True)

    query = f"""候选人：{json.dumps(parsed_resume, ensure_ascii=False)}
岗位：{json.dumps(parsed_jd, ensure_ascii=False)}"""

    result = await culture_fit_agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    messages = result.get("messages", [])
    print(f"[Agent3] 搜索完成，共 {len(messages)} 条消息", flush=True)
    return result
