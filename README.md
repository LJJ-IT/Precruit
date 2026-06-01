# Precruit — 简历与招聘JD智能匹配平台

基于 LangChain + LangGraph + MCP 的多智能体协作分析系统。

## 技术栈

- **LLM**: DeepSeek / OpenAI（可切换）
- **Agent框架**: LangChain + LangGraph
- **MCP集成**: langchain-mcp-adapters
- **后端**: FastAPI + Uvicorn
- **包管理**: uv

## 项目结构

```
matchai/
├── app/
│   ├── agents/          # Agent定义（4个分析Agent + 编排器）
│   ├── services/        # 服务层（LLM、MCP、简历解析）
│   ├── models/          # Pydantic数据模型
│   └── api/
│       ├── main.py      # FastAPI应用入口
│       └── routes/      # API路由
├── db/                  # 数据库文件（SQLite）
├── docs/                # 文档
├── pyproject.toml       # uv项目配置
└── langgraph.json       # LangGraph配置
```

## 快速开始

```bash
# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入API Key

# 启动开发服务器
uv run uvicorn app.api.main:app --reload --port 8000
```

