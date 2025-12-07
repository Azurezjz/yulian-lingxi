# 语联灵犀 - 基于大模型 Agent 与工具链框架的异构工具联动系统

## 📋 项目简介

**语联灵犀**是一款可视化 AI 助手系统，通过自然语言输入，自主选择工具执行任务，并输出结构化结果。项目采用 **"前端交互层→核心调度层→工具执行层"** 三层架构，支持 5 类工具调用和多工具协同执行。

### 核心特点

- 🎨 **强展示性**：Web 可视化界面，支持现场操作演示
- 🔧 **完整架构**：覆盖全流程，技术点丰富且不冗余
- 🎯 **可控难度**：基于开源工具与提示词工程，适合团队协作
- 💡 **实用性强**：能处理多类典型场景需求，成果可直接演示

---

## 🚀 快速开始

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

详细说明请参考：[前端运行指南](frontend/README.md)

### 后端启动

```bash
cd backend
# 创建虚拟环境（推荐）
conda create -n lingxi_backend python=3.9 -y
conda activate lingxi_backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制 .env.example 为 .env 并填入实际值）
cp .env.example .env

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 API 文档：http://localhost:8000/docs

详细说明请参考：[后端开发指南](backend/README.md)

---

## 📁 项目结构

```
yulian-lingxi/
├── frontend/              # 前端代码（React + TypeScript）
│   ├── src/
│   │   ├── api/          # API 接口定义
│   │   ├── components/   # React 组件
│   │   └── layouts/      # 布局组件
│   └── package.json
│
├── backend/              # 后端代码（FastAPI + Python）
│   ├── app/
│   │   ├── core/        # 核心调度层
│   │   ├── tools/       # 工具执行层
│   │   └── api/         # API 路由
│   └── requirements.txt
│
├── docs/                 # 项目文档
│   ├── API_SPEC.md       # API 接口规范
│   ├── TOOL_GUIDE.md     # 工具开发指南
│   └── ...
│
├── PROJECT_PLAN.md       # 项目总体规划
├── DEVELOPMENT_PROGRESS.md  # 开发进度跟踪
└── README.md            # 本文档
```

---

## 📚 核心文档

### 项目规划
- [项目总体规划](PROJECT_PLAN.md) - 项目概述、功能设计、技术方案
- [开发进度跟踪](DEVELOPMENT_PROGRESS.md) - 任务清单、进度跟踪

### 开发指南
- [API 接口规范](docs/API_SPEC.md) - 前后端接口定义
- [工具开发指南](docs/TOOL_GUIDE.md) - 工具封装规范
- [前端运行指南](frontend/README.md) - 前端开发说明
- [后端开发指南](backend/README.md) - 后端开发说明

### 协作文档
- [团队分工与协作指南](README.md) - 团队角色分工、协作流程

---

## 🎯 核心功能

### 1. 智能意图识别与工具调度
- 通过提示词引导，模型自主分析中文需求
- 自动选择适配工具，提取所需参数
- 支持多轮交互补全参数

### 2. 多工具协同执行
支持 5 类工具调用：
- **生活服务工具**：天气查询（近 7 天预报）
- **信息检索工具**：新闻检索（关键词/领域筛选）
- **数据处理工具**：股票数据查询、数值计算、图表生成
- **文档生成工具**：报告/邮件/总结生成
- **多工具联动**：跨工具串联执行

### 3. 可视化交互与结果输出
- Web 界面：需求输入、对话历史、工具日志、结果展示
- 图表展示：折线图、柱状图
- 文档下载：支持 Markdown/Word 格式

---

## 👥 团队分工

| 角色 | 职责 |
|------|------|
| **前端开发负责人** | 搭建 Web 可视化界面，实现交互功能 |
| **核心调度负责人** | 开发意图识别、工具调度逻辑 |
| **工具开发人员** | 封装各类工具接口 |
| **前后端协同人员** | 连接前后端，替换 Mock 为真实 API |
| **测试负责人** | 全链路测试、边界测试、验收 |
| **文档与项目管理** | 维护文档、跟踪进度、协调沟通 |

详细分工请参考：[团队分工与协作指南](README.md)

---

## 🛠️ 技术栈

### 前端
- **框架**：React 19 + TypeScript
- **构建工具**：Vite
- **UI 框架**：Tailwind CSS
- **图表库**：Recharts
- **图标库**：Lucide React

### 后端
- **框架**：FastAPI
- **语言**：Python 3.9+
- **工具链框架**：LangChain / LangGraph（可选）
- **HTTP 客户端**：httpx

---

## 📅 开发计划

### 第 1 周 ✅
- 环境搭建
- 前端基础界面
- 项目结构确定

### 第 2 周 🔄
- 工具封装（5 类工具）
- 调度层基础开发
- 意图识别实现

### 第 3 周 ⏳
- 前后端对接
- 多工具联动实现
- 功能完善

### 第 4 周 ⏳
- 测试优化
- UI 美化
- 文档完善

详细进度请参考：[开发进度跟踪](DEVELOPMENT_PROGRESS.md)

---

## 🔗 相关资源

### 开源工具链框架
- [LangChain](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [AutoGen](https://microsoft.github.io/autogen/)

### 开源大模型
- [Qwen](https://github.com/QwenLM/Qwen)
- [ChatGLM](https://github.com/THUDM/ChatGLM3)

### API 资源
- [OpenWeatherMap](https://openweathermap.org/api)
- [NewsAPI](https://newsapi.org/)
- [Alpha Vantage](https://www.alphavantage.co/)

---

## 📝 许可证

本项目为课程设计项目，仅供学习交流使用。

---

## 👤 贡献者

项目团队（6 人）

---

**最后更新**：2024年
