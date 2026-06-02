"""Agent 2: 技能与经历匹配专家 — 比对简历与JD，评估硬实力"""

import json

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from ..config import settings
from .prompts import SKILL_MATCHER_PROMPT

_llm = init_chat_model(
    model="deepseek-v4-flash",
    api_key=settings.deepseek_api_key,
    temperature=0.1,
)


def _build_agent(with_github: bool = False):
    """根据是否需要 GitHub 构建不同的 Agent"""
    tools = []
    if with_github:
        # GitHub MCP 将在编排器中统一管理，这里先预留接口
        pass
    return create_agent(model=_llm, tools=tools, system_prompt=SKILL_MATCHER_PROMPT)


async def evaluate_skills(parsed_resume: dict, parsed_jd: dict) -> str:
    """
    评估技能与经历匹配度

    Args:
        parsed_resume: Agent 1 输出的简历结构化数据
        parsed_jd: Agent 1 输出的JD结构化数据

    Returns:
        JSON 字符串（SkillMatchResult格式）
    """
    # 动态注入 GitHub MCP（仅当简历里有 github_username）
    github_username = parsed_resume.get("github_username", "")
    agent = _build_agent(with_github=bool(github_username))

    query = f"""候选人：{json.dumps(parsed_resume, ensure_ascii=False)}
岗位：{json.dumps(parsed_jd, ensure_ascii=False)}"""
    if github_username:
        query += f"\n（请调用 GitHub 工具查看 {github_username} 的开源项目）"

    result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    messages = result.get("messages", [])
    return messages[-1].content if messages else ""
