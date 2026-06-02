"""GitHub MCP 工具 — 按需加载，供 Agent 2 条件注入"""

import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from ..config import settings

_github_tools = None
_mcp_client = None


async def get_github_tools():
    """懒加载 GitHub MCP 工具（首次调用时启动 MCP Server 子进程）"""
    global _github_tools, _mcp_client
    if _github_tools is not None:
        print("[GitHub MCP] 使用缓存工具", flush=True)
        return _github_tools

    if not settings.github_token:
        print("[GitHub MCP] ⚠️ 未配置 GITHUB_TOKEN，跳过", flush=True)
        return []

    print("[GitHub MCP] 启动 Server...", flush=True)
    _mcp_client = MultiServerMCPClient({
        "github": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": settings.github_token},
        }
    })

    print("[GitHub MCP] 加载工具列表(timeout=120s)...", flush=True)
    try:
        _github_tools = await asyncio.wait_for(_mcp_client.get_tools(), timeout=120)
    except asyncio.TimeoutError:
        print("[GitHub MCP] ❌ 超时！", flush=True)
        raise

    print(f"[GitHub MCP] ✅ {len(_github_tools)} 个工具: {[t.name for t in _github_tools]}", flush=True)
    return _github_tools
