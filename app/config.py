"""
Precruit 配置管理

集中管理所有环境变量，提供类型安全的配置访问。
所有真实值从 .env 文件加载。
"""

import os
from dotenv import load_dotenv


load_dotenv()

# ── 环境变量后面加空字符串是为了None ──

class Settings:
    """全局配置单例"""

    # ── deepseek官方API ──
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")

    # ── SiliconFlow硅基流动 ──
    siliconflow_api_key: str = os.getenv("SILICONFLOW_API_KEY", "")
    siliconflow_base_url: str = os.getenv("SILICONFLOW_BASE_URL", "")
    deepseek_model_name: str = os.getenv("DEEPSEEK_MODEL_NAME", "")
    qwen_model_name: str = os.getenv("QWEN_MODEL_NAME", "")
    kimi_model_name: str = os.getenv("KIMI_MODEL_NAME", "")

    # ── MCP ──
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    github_token: str = os.getenv("GITHUB_TOKEN", "")
    gmail_credentials_path: str = os.getenv("GMAIL_CREDENTIALS_PATH", "")

    # ── 评分阈值 ──
    score_threshold: float = float(os.getenv("SCORE_THRESHOLD", "95"))

    # ── LangSmith（可选）──
    langsmith_api_key: str = os.getenv("LANGSMITH_API_KEY", "")
    langsmith_tracing: str = os.getenv("LANGSMITH_TRACING", "")
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "")


# 全局单例
settings = Settings()
