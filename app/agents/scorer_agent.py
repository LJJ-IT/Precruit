"""Agent 4: 综合评分与优化专家 — 加权评分 + 简历优化建议 + 面试问题"""

import json

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from ..config import settings
from .prompts import SCORER_PROMPT

_llm = init_chat_model(
    model="deepseek-v4-flash",
    api_key=settings.deepseek_api_key,
    temperature=0.3,
)

scorer_agent = create_agent(
    model=_llm,
    tools=[],
    system_prompt=SCORER_PROMPT,
)


async def evaluate_final(
    parsed_resume: dict,
    parsed_jd: dict,
    skill_result: dict,
    culture_result: dict,
) -> str:
    """
    综合评分与优化建议

    Args:
        parsed_resume: Agent 1 输出的简历数据
        parsed_jd: Agent 1 输出的JD数据
        skill_result: Agent 2 输出的技能匹配结果
        culture_result: Agent 3 输出的文化匹配结果

    Returns:
        JSON 字符串（FinalReport格式）
    """
    query = f"""候选人：{json.dumps(parsed_resume, ensure_ascii=False)}
岗位：{json.dumps(parsed_jd, ensure_ascii=False)}
技能匹配：{json.dumps(skill_result, ensure_ascii=False)}
文化匹配：{json.dumps(culture_result, ensure_ascii=False)}"""
    result = await scorer_agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    messages = result.get("messages", [])
    return messages[-1].content if messages else ""
