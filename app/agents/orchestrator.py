"""编排器 — 串联多Agent协作流程"""

import asyncio
import json
import re

from .document_parser_agent import parse_documents
from .skill_matcher_agent import evaluate_skills
from .culture_fit_agent import evaluate_culture_fit
from .scorer_agent import evaluate_final
from ..config import settings


def _parse_json(text: str) -> dict:
    """从Agent响应中提取JSON"""
    text = text.strip()
    m = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if m: return json.loads(m.group(1))
    m = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if m: return json.loads(m.group(1))
    return json.loads(text)


async def run_analysis(resume_input: str, jd_text: str) -> dict:
    """
    执行完整分析流程

    流程: Agent 1 → Agent 2 + Agent 3 并行 → Agent 4 → 条件发邮件

    Args:
        resume_input: 简历文件路径或纯文本
        jd_text: JD全文

    Returns:
        FinalReport dict
    """
    # ── Agent 1: 文档解析 ──
    print("[Orchestrator] Step 1: 文档解析...")
    raw_parsed = await parse_documents(resume_input, jd_text)
    parsed = _parse_json(raw_parsed)
    parsed_resume = parsed.get("resume", {})
    parsed_jd = parsed.get("jd", {})

    # ── Agent 2 + Agent 3: 并行分析 ──
    print("[Orchestrator] Step 2: 并行分析（技能匹配 + 文化匹配）...")
    skill_result, culture_result = await asyncio.gather(
        evaluate_skills(parsed_resume, parsed_jd),
        evaluate_culture_fit(parsed_resume, parsed_jd),
        return_exceptions=True,
    )

    # 处理可能的异常，提取 JSON 文本
    if isinstance(skill_result, Exception):
        skill_data = {"hard_skill_score": 0, "error": str(skill_result)}
    else:
        skill_data = _parse_json(skill_result)

    if isinstance(culture_result, Exception):
        culture_data = {"score": 0, "error": str(culture_result)}
    else:
        # culture_result 可能是 agent result dict（含 messages）或纯字符串
        if isinstance(culture_result, dict) and "messages" in culture_result:
            culture_data = _parse_json(culture_result["messages"][-1].content)
        else:
            culture_data = _parse_json(culture_result)

    # ── Agent 4: 综合评分 ──
    print("[Orchestrator] Step 3: 综合评分...")
    raw_final = await evaluate_final(parsed_resume, parsed_jd, skill_data, culture_data)
    final_report = _parse_json(raw_final)

    # ── 条件发送邮件 ──
    final_score = final_report.get("final_score", 0)
    email = parsed_resume.get("email", "")
    final_report["email_sent"] = False

    if final_score >= settings.score_threshold and email:
        print(f"[Orchestrator] 评分 {final_score} ≥ {settings.score_threshold}，触发邮件发送...")
        # TODO: 调用邮件MCP发送面试邀请
        # email_sent = await send_interview_email(email, final_report)
        # final_report["email_sent"] = email_sent
    else:
        print(f"[Orchestrator] 评分 {final_score} < {settings.score_threshold}，不发送邮件")

    print(f"[Orchestrator] 完成！最终得分: {final_score}")
    return final_report
