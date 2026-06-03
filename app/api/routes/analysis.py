"""分析路由 — POST /api/analysis/submit + SSE 流式进度"""

import asyncio
import json
import logging
import traceback

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

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
    提交简历+JD进行匹配分析（等待完成后返回）

    - **resume_text**: 简历文本内容（或文件路径）
    - **jd_text**: JD全文
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


@router.post("/analysis/stream")
async def stream_analysis(request: AnalysisRequest):
    """
    提交简历+JD进行匹配分析（SSE实时推送进度）

    事件格式:
      data: {"type":"progress","step":"解析文档","agent":"文档解析智能体"}
      data: {"type":"progress","step":"并行分析","agent":"技能匹配智能体 + 文化匹配智能体"}
      data: {"type":"progress","step":"综合评分","agent":"综合评分智能体"}
      data: {"type":"progress","step":"发送面试邀请","agent":"邮件服务"}
      data: {"type":"result","data":{...}}
      data: {"type":"error","message":"..."}
    """

    async def event_generator():
        progress_queue: asyncio.Queue = asyncio.Queue()

        async def on_progress(step: str, agent: str):
            await progress_queue.put({
                "type": "progress",
                "step": step,
                "agent": agent,
            })

        async def run():
            try:
                result = await run_analysis(
                    request.resume_text,
                    request.jd_text,
                    on_progress=on_progress,
                )
                await progress_queue.put({
                    "type": "result",
                    "data": result,
                })
            except Exception as e:
                logger.error(f"分析异常: {traceback.format_exc()}")
                await progress_queue.put({
                    "type": "error",
                    "message": str(e),
                })

        task = asyncio.create_task(run())

        while not task.done():
            try:
                event = await asyncio.wait_for(progress_queue.get(), timeout=0.5)
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            except asyncio.TimeoutError:
                # 心跳，保持连接
                yield ": heartbeat\n\n"

        # 消费剩余事件
        while not progress_queue.empty():
            event = await progress_queue.get()
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
