"""编排器 — 串联多Agent协作流程（LangGraph StateGraph 引擎）"""

import json
import re
from typing import TypedDict, Optional, Callable

from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from langchain_core.runnables import RunnableConfig

from .document_parser_agent import parse_documents
from .skill_matcher_agent import evaluate_skills
from .culture_fit_agent import evaluate_culture_fit
from .scorer_agent import evaluate_final


def _parse_json(text: str) -> dict:
    """从Agent响应中提取JSON"""
    text = text.strip()
    m = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    m = re.search(r"```\s*(.*?)\s*```", text, re.DOTALL)
    if m:
        return json.loads(m.group(1))
    return json.loads(text)


# ═══════════════════════════════════════════════════════════════════
# State — LangGraph 共享状态
# ═══════════════════════════════════════════════════════════════════

class AnalysisState(TypedDict):
    """分析流程状态

    LangGraph StateGraph 的所有节点共享此状态。
    每个节点返回部分字段，LangGraph 自动合并到全局状态中。
    """
    # ── 输入 ──
    resume_input: str
    jd_text: str

    # ── Agent 1 输出 ──
    parsed_resume: dict
    parsed_jd: dict

    # ── Agent 2 输出 ──
    skill_result: dict

    # ── Agent 3 输出 ──
    culture_result: dict

    # ── Agent 4 输出 ──
    final_report: dict

    # ── 错误 ──
    error: str


# ═══════════════════════════════════════════════════════════════════
# 节点函数
# ═══════════════════════════════════════════════════════════════════

async def _node_parse_documents(state: AnalysisState, config: RunnableConfig) -> dict:
    """Agent 1: 文档解析专家 — 提取简历+JD结构化信息"""
    cb = config.get("configurable", {}).get("on_progress")
    if cb:
        await cb("解析文档", "文档解析智能体")

    print("[LangGraph] Step 1: 文档解析", flush=True)
    raw = await parse_documents(state["resume_input"], state["jd_text"])
    parsed = _parse_json(raw)

    return {
        "parsed_resume": parsed.get("resume", {}),
        "parsed_jd": parsed.get("jd", {}),
    }


def _fan_out_parallel(state: AnalysisState) -> list[Send]:
    """条件边：解析完成后 → 并行分发到 Agent 2 + Agent 3

    LangGraph 的 Send API 实现 fan-out 并行：
    - 返回多个 Send 对象 → 各目标节点并发执行
    - 所有目标节点都完成后 → 自动汇聚到下游节点

    这替代了原来的 asyncio.gather(evaluate_skills, evaluate_culture_fit)。
    """
    return [
        Send("evaluate_skills", state),
        Send("evaluate_culture", state),
    ]


async def _node_evaluate_skills(state: AnalysisState, config: RunnableConfig) -> dict:
    """Agent 2: 技能与经历匹配专家 — 逐项比对技能栈，量化硬实力"""
    cb = config.get("configurable", {}).get("on_progress")
    if cb:
        await cb("并行分析", "技能匹配智能体 + 文化匹配智能体")

    print("[LangGraph] Step 2a: 技能匹配", flush=True)

    try:
        raw = await evaluate_skills(state["parsed_resume"], state["parsed_jd"])
        skill_data = _parse_json(raw)
    except Exception as e:
        print(f"[LangGraph] Agent 2 异常: {e}", flush=True)
        skill_data = {"hard_skill_score": 0, "error": str(e)}

    return {"skill_result": skill_data}


async def _node_evaluate_culture(state: AnalysisState, config: RunnableConfig) -> dict:
    """Agent 3: 文化与业务匹配专家 — 搜索公司信息，评估文化契合度"""
    cb = config.get("configurable", {}).get("on_progress")
    if cb:
        await cb("并行分析", "技能匹配智能体 + 文化匹配智能体")

    print("[LangGraph] Step 2b: 文化匹配", flush=True)

    try:
        result = await evaluate_culture_fit(state["parsed_resume"], state["parsed_jd"])
        if isinstance(result, dict) and "messages" in result:
            culture_data = _parse_json(result["messages"][-1].content)
        else:
            culture_data = _parse_json(result)
    except Exception as e:
        print(f"[LangGraph] Agent 3 异常: {e}", flush=True)
        culture_data = {"score": 0, "error": str(e)}

    return {"culture_result": culture_data}


async def _node_evaluate_final(state: AnalysisState, config: RunnableConfig) -> dict:
    """Agent 4: 综合评分与优化专家 — 加权计算最终分数 + 条件发送面试邀请"""
    cb = config.get("configurable", {}).get("on_progress")
    if cb:
        await cb("综合评分", "综合评分智能体")

    print("[LangGraph] Step 3: 综合评分", flush=True)

    raw = await evaluate_final(
        state["parsed_resume"],
        state["parsed_jd"],
        state.get("skill_result", {}),
        state.get("culture_result", {}),
    )
    final_report = _parse_json(raw)

    final_score = final_report.get("final_score", 0)
    email_sent = final_report.get("email_sent", False)
    if email_sent:
        print(f"[Orchestrator] 完成！得分: {final_score}，已发送面试邀请", flush=True)
    else:
        print(f"[Orchestrator] 完成！得分: {final_score}", flush=True)

    return {"final_report": final_report}


# ═══════════════════════════════════════════════════════════════════
# 构建 Graph
# ═══════════════════════════════════════════════════════════════════

_builder = StateGraph(AnalysisState)

# 注册节点
_builder.add_node("parse_documents", _node_parse_documents)
_builder.add_node("evaluate_skills", _node_evaluate_skills)
_builder.add_node("evaluate_culture", _node_evaluate_culture)
_builder.add_node("evaluate_final", _node_evaluate_final)

# 编排边
#   START → parse_documents → [evaluate_skills ‖ evaluate_culture] → evaluate_final → END
_builder.add_edge(START, "parse_documents")
_builder.add_conditional_edges(
    "parse_documents",
    _fan_out_parallel,
    ["evaluate_skills", "evaluate_culture"],
)
_builder.add_edge("evaluate_skills", "evaluate_final")
_builder.add_edge("evaluate_culture", "evaluate_final")
_builder.add_edge("evaluate_final", END)

_analysis_graph = _builder.compile()


# ═══════════════════════════════════════════════════════════════════
# Public API（与旧版签名完全兼容）
# ═══════════════════════════════════════════════════════════════════

async def run_analysis(
    resume_input: str,
    jd_text: str,
    on_progress: Optional[Callable] = None,
) -> dict:
    """
    执行完整分析流程（LangGraph StateGraph 引擎）

    流程: Agent 1 → [Agent 2 ‖ Agent 3] → Agent 4（条件发邮件）

    Args:
        resume_input: 简历文件路径或纯文本
        jd_text: JD全文
        on_progress: 进度回调 async fn(step_name, agent_label)，用于SSE推送

    Returns:
        FinalReport dict
    """
    initial_state: AnalysisState = {
        "resume_input": resume_input,
        "jd_text": jd_text,
        "parsed_resume": {},
        "parsed_jd": {},
        "skill_result": {},
        "culture_result": {},
        "final_report": {},
        "error": "",
    }

    # 将进度回调注入 configurable，节点通过 RunnableConfig 获取
    final_state = await _analysis_graph.ainvoke(
        initial_state,
        config={"configurable": {"on_progress": on_progress}},
    )

    return final_state.get("final_report", {})
