# 故障树智能生成系统 - 联合开发文档

## 📋 项目概述

本项目是一个基于 **FastAPI + Vue 3** 的故障树智能生成系统，利用大语言模型（Qwen-max）从技术文档中自动提取故障知识，生成可视化的故障树结构。



```
服务外包比赛/
├── backend/                         # 后端服务
│   ├── app/                         # 应用主代码
│   │   ├── api/v1/                  # API 路由层
│   │   │   ├── __init__.py
│   │   │   ├── ai_chat.py           # AI 聊天接口
│   │   │   ├── document.py          # 文档上传接口
│   │   │   ├── fault_tree.py        # 故障树操作接口
│   │   │   ├── knowledge.py         # 知识抽取接口
│   │   │   └── validate.py          # 逻辑验证接口
│   │   │
│   │   ├── core/                    # 核心配置层
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # 配置管理
│   │   │   └── database.py          # 数据库连接
│   │   │
│   │   ├── models/                  # 数据模型层
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py           # Pydantic Schema
│   │   │   └── triplets.py          # 三元组模型
│   │   │
│   │   ├── services/                # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── fault_tree_service.py        # 故障树服务
│   │   │   ├── kg_builder.py                # 知识图谱构建
│   │   │   ├── knowledge_extraction_service.py  # 知识抽取
│   │   │   ├── multimodal_encoder.py        # 多模态编码器
│   │   │   ├── tree_generator.py            # 故障树生成器
│   │   │   └── triplet_extractor.py         # 三元组提取器
│   │   │
│   │   └── utils/                   # 工具函数层
│   │       ├── __init__.py
│   │       └── logger.py            # 日志配置
│   │
│   ├── test/                        # 测试模块
│   │   ├── __init__.py
│   │   ├── conftest.py              # pytest 配置
│   │   ├── README.md                # 测试说明
│   │   ├── api_tests/               # API 接口测试
│   │   ├── service_tests/           # 服务层测试
│   │   ├── model_tests/             # 数据模型测试
│   │   ├── core_tests/              # 核心功能测试
│   │   └── integration_tests/       # 集成测试
│   │
│   ├── data/                        # 数据目录
│   │   ├── output/                  # 输出数据
│   │   └── triplets/                # 三元组数据
│   │
│   ├── main.py                      # 应用入口
│   ├── .env.example                 # 环境变量模板
│   ├── requirements.txt             # 生产依赖
│   ├── requirements-test.txt        # 测试依赖
│   ├── pyproject.toml               # pytest 配置
│   ├── 运行测试.bat                 # 测试启动脚本
│   ├── 测试框架使用指南.md          # 测试文档
│   └── README.md                    # 后端说明
│
├── frontend/                        # 前端应用
│   ├── src/                         # 源代码
│   │   ├── api/                     # API 调用封装
│   │   ├── components/              # 可复用组件
│   │   ├── pages/                   # 页面组件
│   │   ├── router/                  # 路由配置
│   │   ├── stores/                  # 状态管理
│   │   ├── styles/                  # 样式文件
│   │   ├── utils/                   # 工具函数
│   │   ├── App.vue                  # 根组件
│   │   └── main.js                  # 入口文件
│   │
│   ├── public/                      # 静态资源
│   ├── index.html                   # HTML 入口
│   ├── package.json                 # Node.js 依赖
│   ├── vite.config.js               # Vite 配置
│   ├── README.md                    # 前端说明
│   └── 启动服务器.bat               # 启动脚本
│
├── API文档.md                       # API 接口文档
├── 快速启动.bat                     # 一键启动脚本
├── 安装依赖.bat                     # 依赖安装脚本
├── deploy.bat                       # 部署脚本
└── deploy-frontend.bat              # 前端部署脚本
```

---

## 🔧 技术栈

### 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.10 | 主要编程语言 |
| **FastAPI** | 0.109.0 | 高性能 Web 框架 |
| **Pydantic** | 2.5.3 | 数据验证和序列化 |
| **Neo4j** | 5.16.0 | 知识图谱数据库 |
| **PostgreSQL** | - | 关系型数据库（可选） |
| **Transformers** | 4.37.0 | 大模型推理 |
| **NetworkX** | 3.2.1 | 图结构计算 |
| **DashScope** | - | 通义千问 API SDK |
| **Tenacity** | - | 重试机制库 |

### 前端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| **Vue 3** | 3.4.15 | 渐进式框架 |
| **Vite** | 5.0.11 | 构建工具 |
| **Pinia** | 2.1.7 | 状态管理 |
| **Vue Router** | 4.2.5 | 路由管理 |
| **Element Plus** | 2.5.4 | UI 组件库 |
| **@vue-flow/core** | 1.48.2 | 流程图/故障树可视化 |
| **Axios** | 1.6.5 | HTTP 客户端 |
| **Dagre** | 0.8.5 | 自动布局算法 |
| **jsPDF** | 4.2.0 | PDF 导出 |
| **Tailwind CSS** | - | 原子化 CSS |

---

## 🚀 快速开始

### 环境要求
- **Python** 3.10+
- **Node.js** 16+
- **Neo4j** 4.x 或 5.x（可选，用于知识图谱存储）

### 方式一：一键启动（推荐）

在项目根目录运行：

```bash
.\快速启动.bat
```

此脚本会自动：
1. 检查依赖并安装
2. 启动后端服务（端口 8000）
3. 启动前端服务（端口 3000）

### 方式二：手动启动

#### 1. 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 2. 配置环境变量
复制 `.env.example` 为 `.env`，编辑配置：
```bash
cp .env.example .env
```

编辑 `backend/.env`：
```ini
# Neo4j 配置（可选）
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# AI 模型配置
DASHSCOPE_API_KEY=sk-your-api-key
MODEL_NAME=qwen-max
```

#### 3. 启动后端
```bash
python main.py
```

后端将运行在 http://localhost:8000

#### 4. 安装前端依赖（新终端）
```bash
cd frontend
npm install
```

#### 5. 启动前端
```bash
npm run dev
```

前端将运行在 http://localhost:3000

### 访问应用

| 服务 | 地址 |
|------|------|
| 前端应用 | http://localhost:3000 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |
| 健康检查 | http://localhost:8000/api/health |

---

## 📡 API 接口说明

### 基础信息
- **基础 URL**: `http://localhost:8000/api/v1`
- **数据格式**: JSON
- **API 文档**: http://localhost:8000/docs（Swagger UI）

### 核心接口

#### 文档上传
```http
POST /document/upload
Content-Type: multipart/form-data

参数：file (PDF/Word/TXT 文件)

响应：
{
  "file_id": "uuid",
  "filename": "设备手册.pdf",
  "file_size": 1024000,
  "status": "success"
}
```

#### 知识抽取
```http
POST /knowledge/extract
Content-Type: application/json

{
  "file_id": "uuid",
  "top_event": "系统故障"
}

响应：
{
  "task_id": "extract_123",
  "triplets": [...],
  "events": [...],
  "gates": [...],
  "status": "completed"
}
```

#### 生成故障树
```http
GET /fault-tree/generate_tree?top_event=系统故障

响应：
{
  "status": "success",
  "data": {
    "nodeList": [...],
    "linkList": [...]
  }
}
```

#### AI 聊天
```http
POST /ai/chat

{
  "messages": [
    {"role": "user", "content": "请分析这个故障树"}
  ],
  "context": {
    "nodes": [...],
    "edges": [...]
  }
}
```

#### 导出故障树
```http
GET /fault-tree/download/{filename}
```

完整 API 文档请访问：http://localhost:8000/docs

---

## 🧪 测试说明

### 快速运行测试

```bash
cd backend

# 方式一：使用批处理脚本
.\运行测试.bat

# 方式二：使用 pytest
pytest
```

### 测试命令

```bash
# 运行所有测试
pytest

# 运行特定模块
pytest test/api_tests/
pytest test/service_tests/
pytest test/model_tests/

# 运行单个测试文件
pytest test/api_tests/test_ai_chat.py -v

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 测试结构

| 目录 | 说明 |
|------|------|
| `test/api_tests/` | API 接口测试 |
| `test/service_tests/` | 服务层测试 |
| `test/model_tests/` | 数据模型测试 |
| `test/core_tests/` | 核心功能测试 |
| `test/integration_tests/` | 集成测试 |

详细测试文档见：`backend/测试框架使用指南.md`

---

## 👥 联合开发指南

### 分支管理
```bash
main          # 生产环境代码
develop       # 开发分支
feature/*     # 功能分支
bugfix/*      # 修复分支
```

### 开发流程

1. **创建功能分支**
```bash
git checkout -b feature/your-feature-name
```

2. **提交代码**
```bash
git add .
git commit -m "feat: 描述你的功能"
```

3. **推送并创建 PR**
```bash
git push origin feature/your-feature-name
```

### 代码规范

- **后端**：遵循 PEP 8，使用类型注解
- **前端**：使用 ESLint + Prettier，遵循 Vue 3 风格指南
- **提交信息**：使用 Conventional Commits 格式

### 常用命令

```bash
# 后端开发
cd backend
python main.py              # 启动服务
pytest                      # 运行测试
pytest --cov=app           # 生成覆盖率

# 前端开发
cd frontend
npm run dev                 # 启动开发服务器
npm run build               # 构建生产版本
npm run lint                # 代码检查
```

