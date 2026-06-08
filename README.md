# Precruit — 简历与招聘 JD 智能匹配平台

基于 LangChain + LangGraph + MCP 的多智能体协作分析系统，用于自动化简历评估与 JD 匹配。

## 技术栈

- **LLM**: DeepSeek V4 / Qwen / Kimi（通过硅基流动平台统一接入）
- **Agent 框架**: LangChain + LangGraph（多智能体编排）
- **MCP 集成**: langchain-mcp-adapters（Web 搜索、GitHub、邮件）
- **后端**: FastAPI + Uvicorn
- **前端**: Vue 3 + Vite + Element Plus
- **包管理**: uv（Python）/ npm（Node.js）

## 项目结构

```
Precruit/
├── app/
│   ├── agents/          # 4 个分析 Agent + 编排器
│   │   ├── document_parser_agent.py   # 文档解析 Agent
│   │   ├── skill_matcher_agent.py     # 技能匹配 Agent
│   │   ├── culture_fit_agent.py       # 文化契合 Agent
│   │   ├── scorer_agent.py            # 综合评分 Agent
│   │   └── orchestrator.py            # LangGraph 编排器
│   ├── api/             # FastAPI 应用
│   │   ├── main.py      # 应用入口
│   │   └── routes/analysis.py         # 分析路由
│   ├── tools/           # MCP 工具（Web 搜索、简历解析）
│   ├── models/          # Pydantic 数据模型
│   └── config.py        # 配置管理
├── frontend/            # Vue 3 前端
│   ├── src/
│   │   ├── components/  # 输入面板 / 结果面板
│   │   └── api/         # 前端 API 调用
│   └── vite.config.js
├── main.py              # 后端启动入口（uvicorn）
├── requirements.txt     # Python 依赖
├── pyproject.toml       # uv 项目配置
├── .env.example         # 环境变量模板
└── s.yaml               # 阿里云 FC 部署配置
```

## 快速开始

### 后端

```bash
# 安装依赖
uv sync

# 或用 pip
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 启动开发服务器
uv run uvicorn app.api.main:app --reload --port 8000

# 生产环境
python main.py
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（端口 3000，代理到后端 8000）
npm run dev

# 构建生产版本
npm run build

# 预览构建产物
npm run preview
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 健康检查 |
| `POST` | `/api/analysis/submit` | 提交简历+JD，等待分析结果 |
| `POST` | `/api/analysis/stream` | 流式分析，SSE 推送进度和结果 |

请求体示例：

```json
{
  "resume_text": "张三的简历内容...",
  "jd_text": "职位描述..."
}
```

## 多智能体架构

```
    ┌──────────────────┐
    │ 文档解析 Agent   │ → 提取简历关键信息
    └────────┬─────────┘
             │
    ┌────────┴─────────┐
    │ 技能匹配 Agent   │ ←┐
    └────────┬─────────┘  │
             │            │
    ┌────────┴─────────┐  │ → 并行分析
    │ 文化契合 Agent   │ ←┘
    └────────┬─────────┘
             │
    ┌────────┴─────────┐
    │ 综合评分 Agent   │ → 打分 + 综合结论
    └────────┬─────────┘
             │
    ┌────────┴─────────┐
    │  邮件通知（可选）│ → 高分候选人自动发邮件
    └──────────────────┘
```

## 部署：阿里云函数计算（FC）

### 后端部署

1. 创建 Web 函数，运行环境选 "自定义运行时 (Debian10) + Python 3.10"
2. 关联 GitHub 仓库（分支：master）
3. 配置：

| 项 | 值 |
|----|-----|
| 代码包路径 | `.` |
| 构建环境 | Python 3.10 |
| 构建命令 | `mkdir -p python && pip install -r requirements.txt -t ./python` |
| 启动命令 | `python main.py` |
| 监听端口 | `9000` |
| 执行时长 | `120` 秒 |
| 环境变量 | `PYTHONPATH=/code:/code/python` |

4. 添加 API Key 相关环境变量（`DEEPSEEK_API_KEY`, `SILICONFLOW_API_KEY` 等）
5. 点击"部署"

### 前端部署

1. 在前端 `frontend/.env.production` 中配置后端 API 地址：

```
VITE_API_BASE_URL=https://你的后端FC域名
```

2. 打包：`npm run build`
3. 将 `dist/` 目录部署到 OSS 静态托管 / CDN / FC Web 函数

## 配置说明

所有敏感信息通过 `.env` 环境变量管理，具体字段见 [`.env.example`](./.env.example)：

- `DEEPSEEK_API_KEY` — DeepSeek 平台 API Key
- `SILICONFLOW_API_KEY` — 硅基流动平台 API Key
- `TAVILY_API_KEY` — Web 搜索 API Key
- `GITHUB_TOKEN` — GitHub Personal Access Token（MCP 工具）
- `EMAIL_USER` / `EMAIL_PASSWORD` — 邮件通知账号
- `SCORE_THRESHOLD` — 自动发邮件的评分阈值

## 本地开发常见问题

**Q: 启动后端报 `ModuleNotFoundError`？**
A: 确保用 `uv sync` 或 `pip install -r requirements.txt` 安装了全部依赖。

**Q: 前端请求 404？**
A: 检查前端 `api/analysis.js` 中的 `API_BASE_URL` 是否指向后端正确地址。

**Q: FC 部署后 `No module named 'xxx'`？**
A: 确保构建命令中的 `pip install ... -t ./python` 已将依赖安装到项目目录，并配置 `PYTHONPATH` 环境变量。

## License

MIT
