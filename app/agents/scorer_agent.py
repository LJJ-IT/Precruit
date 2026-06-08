"""Agent 4: 综合评分与优化专家 — 加权评分 + 简历优化建议 + 发面试邀请"""

import json

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from ..config import settings
from ..tools.mcp_tools import get_email_tools
from .prompts import SCORER_PROMPT

_llm = init_chat_model(
    # model="deepseek-v4-flash",
    # api_key=settings.deepseek_api_key,
    model=settings.deepseek_model_name,
    api_key=settings.siliconflow_api_key,
    base_url=settings.siliconflow_base_url,
    model_provider="openai",
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


async def _get_email_agent():
    """延迟加载邮件 Agent，仅当评分达标时才启动 MCP 服务器"""
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
            print(f"[Agent4] 邮件 Agent 就绪 ({len(email_tools)} 工具)", flush=True)
        else:
            _email_agent = _default_agent
            print("[Agent4] 无邮件工具，仅评分", flush=True)
    return _email_agent


async def evaluate_final(
    parsed_resume: dict,
    parsed_jd: dict,
    skill_result: dict,
    culture_result: dict,
) -> str:
    """
    综合评分、简历优化建议、可选发送面试邀请

    邮件 MCP 延迟加载：只有 candidate_email 非空时才加载邮件工具。
    由 Agent 自行判断评分是否达标并调用 send_email。

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
    name = parsed_resume.get("name", "未知")

    print(f"[Agent4] 开始综合评分 | 候选人: {name} | 阈值: {settings.score_threshold}", flush=True)

    # 有邮箱才加载邮件 Agent，否则用默认 Agent
    if email:
        agent = await _get_email_agent()
    else:
        agent = _default_agent
        print("[Agent4] 无邮箱信息，跳过邮件工具加载", flush=True)

    query = f"""候选人：{json.dumps(parsed_resume, ensure_ascii=False)}
岗位：{json.dumps(parsed_jd, ensure_ascii=False)}
技能匹配：{json.dumps(skill_result, ensure_ascii=False)}
文化匹配：{json.dumps(culture_result, ensure_ascii=False)}

评分阈值: {settings.score_threshold} 分。
如果最终评分 ≥ {settings.score_threshold} 且邮箱非空，调用 send_email 发面试邀请:
  to: ["{email}"], subject: "面试邀请 - {company} - {position}"
  text: 正式邮件正文，包含候选人姓名{name}、岗位{position}、公司{company}、评分{'{final_score}'}分"""

    result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    messages = result.get("messages", [])
    content = messages[-1].content if messages else ""

    print(f"[Agent4] 评分完成，共 {len(messages)} 条消息", flush=True)
    return content
