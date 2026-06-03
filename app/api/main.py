"""FastAPI 入口 — Precruit 简历-JD匹配平台API"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.analysis import router as analysis_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动/关闭"""
    logger.info("🚀 Precruit API 启动...")
    yield
    logger.info("🛑 Precruit API 关闭...")


app = FastAPI(
    title="Precruit API",
    version="0.1.0",
    description="简历与招聘JD智能匹配平台 — 多智能体协作分析",
    lifespan=lifespan,
)

# CORS（开发阶段允许所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(analysis_router, prefix="/api")


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok", "service": "precruit-api"}
