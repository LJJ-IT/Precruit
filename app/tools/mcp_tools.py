"""
MCP 工具集：GitHub + 邮件

统一从此文件加载，供各 Agent 按需使用。
"""

import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from ..config import settings

# ═══════════════════════════════════════════════════════════════════
# GitHub MCP
# ═══════════════════════════════════════════════════════════════════

_github_tools = None
_github_client = None


async def get_github_tools():
    global _github_tools, _github_client
    if _github_tools is not None:
        print("[MCP] GitHub 使用缓存", flush=True)
        return _github_tools

    if not settings.github_token:
        print("[MCP] ⚠️ 未配置 GITHUB_TOKEN，跳过", flush=True)
        return []

    print("[MCP] 启动 GitHub Server...", flush=True)
    _github_client = MultiServerMCPClient({
        "github": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": settings.github_token},
        }
    })

    try:
        _github_tools = await asyncio.wait_for(_github_client.get_tools(), timeout=120)
    except asyncio.TimeoutError:
        print("[MCP] ❌ GitHub Server 超时", flush=True)
        return []

    print(f"[MCP] ✅ GitHub {len(_github_tools)} 个工具", flush=True)
    return _github_tools


# ═══════════════════════════════════════════════════════════════════
# 邮件 MCP（QQ邮箱 / 163 / Gmail 等，自动识别）
# ═══════════════════════════════════════════════════════════════════

_email_tools = None
_email_client = None


async def get_email_tools():
    global _email_tools, _email_client
    if _email_tools is not None:
        return _email_tools

    if not settings.email_user or not settings.email_password:
        print("[MCP] ⚠️ 未配置 EMAIL_USER / EMAIL_PASSWORD，跳过邮件工具", flush=True)
        return []

    print("[MCP] 启动 Email Server...", flush=True)
    _email_client = MultiServerMCPClient({
        "universal-email": {
            "transport": "stdio",
            "command": "npx",
            "args": ["mcp-email"],
            "env": {
                "EMAIL_USER": settings.email_user,
                "EMAIL_PASSWORD": settings.email_password,
                "EMAIL_TYPE": settings.email_type,
            },
        }
    })

    try:
        _email_tools = await asyncio.wait_for(_email_client.get_tools(), timeout=60)
    except asyncio.TimeoutError:
        print("[MCP] ❌ Email Server 超时", flush=True)
        return []

    print(f"[MCP] Email {len(_email_tools)} tools: {[t.name for t in _email_tools]}", flush=True)
    return _email_tools
