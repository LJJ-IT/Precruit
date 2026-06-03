"""分析路由 — POST /api/analysis/submit"""

import json
import logging
import re
import traceback

from fastapi import APIRouter, HTTPException

from ...agents.orchestrator import run_analysis
from ...models.schemas import AnalysisRequest, AnalysisResponse, FinalReport

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analysis"])


def _dict_to_final_report(data: dict) -> FinalReport:
    """将编排器返回的 dict 转为 FinalReport 模型"""
    try:
        return FinalReport(**data)
    except Exception as e:
        logger.warning(f"FinalReport 构造失败（将用默认值填充）: {e}")
        return FinalReport(
            final_score=data.get("final_score", 0),
            passed=data.get("passed", False),
            email_sent=data.get("email_sent", False),
            overall_summary=data.get("overall_summary", ""),
        )


@router.post("/analysis/submit", response_model=AnalysisResponse)
async def submit_analysis(request: AnalysisRequest):
    """
    提交简历+JD进行匹配分析

    - **resume_text**: 简历文本内容（或文件路径）
    - **jd_text**: JD全文（至少200字符）
    """
    try:
        logger.info(f"收到分析请求，JD长度: {len(request.jd_text)} 字符")
        report_dict = await run_analysis(request.resume_text, request.jd_text)
        report = _dict_to_final_report(report_dict)
        logger.info(f"分析完成，得分: {report.final_score}")
        return AnalysisResponse(success=True, data=report)

    except json.JSONDecodeError as e:
        logger.error(f"JSON解析失败: {e}")
        raise HTTPException(status_code=422, detail=f"Agent输出解析失败: {e}")

    except Exception as e:
        logger.error(f"分析异常:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"分析失败: {e}")
