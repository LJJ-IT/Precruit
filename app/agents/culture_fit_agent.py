"""Agent 3: 文化匹配专家 — 搜索公司文化，评估候选人与公司文化契合度"""

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from ..config import settings
from .prompts import CULTURE_FIT_PROMPT

_llm = init_chat_model(
    model="deepseek-v4-flash",
    api_key=settings.deepseek_api_key,
    temperature=0.1,
)

_web_search = TavilySearch(
    max_results=5,
    topic="general",
)

culture_fit_agent = create_agent(
    model=_llm,
    tools=[_web_search],
    system_prompt=CULTURE_FIT_PROMPT,
)


async def evaluate_culture_fit(parsed_resume: dict, parsed_jd: dict) -> str:
    """
    评估候选人与公司文化匹配度

    Args:
        parsed_resume: Agent 1 输出的简历结构化数据
        parsed_jd: Agent 1 输出的JD结构化数据

    Returns:
        JSON 字符串（CultureFitResult格式）
    """
    import json

    company = parsed_jd.get("company_name", "")
    position = parsed_jd.get("position", "")
    culture_kw = ", ".join(parsed_jd.get("culture_keywords", []))
    self_intro = parsed_resume.get("self_intro", "")
    skills = ", ".join(parsed_resume.get("skills", []))
    experience = "; ".join(parsed_resume.get("experience", []))

    query = f"""请评估候选人与公司文化的匹配度。

公司: {company}
职位: {position}
JD文化关键词: {culture_kw}

候选人技能: {skills}
候选人经历: {experience}
候选人自我评价: {self_intro}

请先用搜索工具搜索"{company} 企业文化 工作氛围"了解公司情况，再结合候选人的工作风格进行评估。
"""
    result = await culture_fit_agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    messages = result.get("messages", [])
    return messages[-1].content if messages else ""
