"""编排器 — 串联多Agent协作流程"""

import asyncio
import json
import re
from typing import Callable, Optional

from .document_parser_agent import parse_documents
from .skill_matcher_agent import evaluate_skills
from .culture_fit_agent import evaluate_culture_fit
from .scorer_agent import evaluate_final


def _parse_json(text: str) -> dict:
    """从Agent响应中提取JSON"""
    text = text.strip()
    m = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if m: return json.loads(m.group(1))
    m = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if m: return json.loads(m.group(1))
    return json.loads(text)


async def run_analysis(
    resume_input: str,
    jd_text: str,
    on_progress: Optional[Callable] = None,
) -> dict:
    """
    执行完整分析流程

    流程: Agent 1 → Agent 2 + Agent 3 并行 → Agent 4（评分 + 条件发邮件）

    Args:
        resume_input: 简历文件路径或纯文本
        jd_text: JD全文
        on_progress: 进度回调 async fn(step_name, agent_label)，用于SSE推送

    Returns:
        FinalReport dict
    """

    async def _progress(step: str, agent: str):
        """发送进度事件"""
        print(f"[Orchestrator] {step} — {agent}", flush=True)
        if on_progress:
            await on_progress(step, agent)

    # ── Agent 1: 文档解析 ──
    await _progress("解析文档", "文档解析智能体")
    raw_parsed = await parse_documents(resume_input, jd_text)
    parsed = _parse_json(raw_parsed)
    parsed_resume = parsed.get("resume", {})
    parsed_jd = parsed.get("jd", {})

    # ── Agent 2 + Agent 3: 并行分析 ──
    await _progress("并行分析", "技能匹配智能体 + 文化匹配智能体")
    print("[Orchestrator] Step 2: 并行分析（技能匹配 + 文化匹配）...", flush=True)
    skill_result, culture_result = await asyncio.gather(
        evaluate_skills(parsed_resume, parsed_jd),
        evaluate_culture_fit(parsed_resume, parsed_jd),
        return_exceptions=True,
    )

    # 处理可能的异常
    if isinstance(skill_result, Exception):
        skill_data = {"hard_skill_score": 0, "error": str(skill_result)}
    else:
        skill_data = _parse_json(skill_result)

    if isinstance(culture_result, Exception):
        culture_data = {"score": 0, "error": str(culture_result)}
    else:
        if isinstance(culture_result, dict) and "messages" in culture_result:
            culture_data = _parse_json(culture_result["messages"][-1].content)
        else:
            culture_data = _parse_json(culture_result)

    # ── Agent 4: 综合评分（内含条件发邮件）──
    await _progress("综合评分", "综合评分智能体")
    raw_final = await evaluate_final(parsed_resume, parsed_jd, skill_data, culture_data)
    final_report = _parse_json(raw_final)

    final_score = final_report.get("final_score", 0)
    email_sent = final_report.get("email_sent", False)
    if email_sent:
        print(f"[Orchestrator] 完成！得分: {final_score}，已发送面试邀请", flush=True)
    else:
        print(f"[Orchestrator] 完成！得分: {final_score}", flush=True)

    return final_report
