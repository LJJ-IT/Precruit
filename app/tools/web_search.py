"""Tavily Web 搜索工具 — 供 Agent 搜索公司文化与业务信息"""

from langchain_tavily import TavilySearch

web_search = TavilySearch(
    max_results=5,
    topic="general",
)
