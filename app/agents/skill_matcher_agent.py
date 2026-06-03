"""Agent 2: 技能与经历匹配专家 — 比对简历与JD，评估硬实力"""

import json

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from ..config import settings
from ..tools.mcp_tools import get_github_tools
from .prompts import SKILL_MATCHER_PROMPT

_llm = init_chat_model(
    model="deepseek-v4-flash",
    api_key=settings.deepseek_api_key,
    temperature=0.1,
)

# 默认 Agent（无 GitHub 工具，大多数情况用这个）
_default_agent = create_agent(
    model=_llm,
    tools=[],
    system_prompt=SKILL_MATCHER_PROMPT,
)

# 缓存 GitHub Agent（首次需要时才创建）
_github_agent = None


async def _get_github_agent():
    """懒加载带 GitHub 工具的 Agent"""
    global _github_agent
    if _github_agent is None:
        print("[Agent2] 加载 GitHub MCP 工具...", flush=True)
        github_tools = await get_github_tools()
        print(f"[Agent2] 创建 GitHub Agent（{len(github_tools)} 个工具）...", flush=True)
        _github_agent = create_agent(
            model=_llm,
            tools=github_tools,
            system_prompt=SKILL_MATCHER_PROMPT,
        )
        print("[Agent2] GitHub Agent 创建完成", flush=True)
    return _github_agent


async def evaluate_skills(parsed_resume: dict, parsed_jd: dict) -> str:
    github_username = parsed_resume.get("github_username", "")

    print(f"[Agent2] GitHub 用户名: {github_username or '无'}", flush=True)

    if github_username:
        print("[Agent2] 获取 GitHub Agent...", flush=True)
        agent = await _get_github_agent()
        print("[Agent2] GitHub Agent 就绪", flush=True)
        query = f"""候选人：{json.dumps(parsed_resume, ensure_ascii=False)}
岗位：{json.dumps(parsed_jd, ensure_ascii=False)}

（请先调用 GitHub 工具查看 {github_username} 的开源项目，再综合评分）"""
    else:
        agent = _default_agent
        query = f"""候选人：{json.dumps(parsed_resume, ensure_ascii=False)}
岗位：{json.dumps(parsed_jd, ensure_ascii=False)}"""

    print("[Agent2] 开始调用 Agent...", flush=True)
    result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
    print(f"[Agent2] Agent 返回，共 {len(result.get('messages', []))} 条消息", flush=True)
    messages = result.get("messages", [])
    return messages[-1].content if messages else ""
