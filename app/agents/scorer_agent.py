"""Agent 4: 综合评分与优化专家 — 加权评分 + 简历优化建议 + 发面试邀请"""

import json

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from ..config import settings
from ..tools.mcp_tools import get_email_tools
from .prompts import SCORER_PROMPT

_llm = init_chat_model(
    model="deepseek-v4-flash",
    api_key=settings.deepseek_api_key,
    temperature=0.3,
)

# 默认 Agent（无邮件工具）
_default_agent = create_agent(
    model=_llm,
    tools=[],
    system_prompt=SCORER_PROMPT,
)

# 缓存带邮件工具的 Agent
_email_agent = None


async def _build_scorer_agent():
    global _email_agent
    if _email_agent is None:
        print("[Agent4] 加载邮件工具...", flush=True)
        email_tools = await get_email_tools()
        if email_tools:
            _email_agent = create_agent(
                model=_llm,
                tools=email_tools,
                system_prompt=SCORER_PROMPT,
            )
            print(f"[Agent4] ✅ 邮件 Agent 就绪", flush=True)
        else:
            _email_agent = _default_agent
            print("[Agent4] ⚠️ 无邮件工具，仅评分", flush=True)
    return _email_agent


async def evaluate_final(
    parsed_resume: dict,
    parsed_jd: dict,
    skill_result: dict,
    culture_result: dict,
) -> str:
    """
    综合评分、简历优化建议、可选发送面试邀请

    Args:
        parsed_resume: Agent 1 输出的简历结构化数据
        parsed_jd: Agent 1 输出的JD结构化数据
        skill_result: Agent 2 输出的技能匹配结果
        culture_result: Agent 3 输出的文化匹配结果

    Returns:
        JSON 字符串（FinalReport格式）
    """
    email = parsed_resume.get("email", "")
    company = parsed_jd.get("company_name", "")
    position = parsed_jd.get("position", "")

    query = f"""候选人：{json.dumps(parsed_resume, ensure_ascii=False)}
岗位：{json.dumps(parsed_jd, ensure_ascii=False)}
技能匹配：{json.dumps(skill_result, ensure_ascii=False)}
文化匹配：{json.dumps(culture_result, ensure_ascii=False)}

评分阈值: {settings.score_threshold} 分。
如果最终评分 ≥ {settings.score_threshold} 且邮箱非空，调用 send_email 发面试邀请:
  to: [{email}], subject: "面试邀请 - {company} - {position}"
"""
    agent = await _build_scorer_agent()
    result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    messages = result.get("messages", [])
    return messages[-1].content if messages else ""
