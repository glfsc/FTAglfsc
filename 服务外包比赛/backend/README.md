# 故障树智能生成系统 - 后端

## 📖 项目简介
基于 FastAPI + Neo4j + Transformers 的工业设备故障树智能生成系统，支持知识提取、图谱构建和故障树自动生成。

## 🛠️ 技术栈
- **Web 框架**: FastAPI（高性能异步 API）
- **数据库**: PostgreSQL（结构化数据）+ Neo4j（知识图谱）
- **AI 模型**: Transformers + PyTorch（知识提取与推理）
- **图计算**: NetworkX（故障树结构生成）
- **文档处理**: python-docx, pdfplumber（多格式文件解析）

---

## 🚀 快速启动

### 方式一：完整功能启动（推荐）

#### 1. 环境要求
- Python 3.8+
- Neo4j 数据库（本地或远程）
- PostgreSQL 数据库（可选，用于持久化存储）

#### 2. 安装依赖
```bash
# 安装完整生产环境依赖
pip install -r requirements.txt
```

#### 3. 配置环境变量
```bash
# 复制环境配置模板
cp .env.example .env

# 编辑 .env 文件，填入以下配置：
# - Neo4j 数据库连接信息
# - PostgreSQL 数据库连接信息（可选）
# - JWT 密钥
# - AI 模型路径
```

**.env 文件关键配置说明**：
```ini
# Neo4j 配置（必填）
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# PostgreSQL 配置（可选）
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=fault_tree_db

# JWT 密钥（生产环境请修改）
SECRET_KEY=your-secret-key-change-in-production

# AI 模型配置
MODEL_NAME=THUDM/chatglm3-6b
MODEL_CACHE_DIR=models
```

#### 4. 启动服务
```bash
# 方式 1：使用 uvicorn 直接启动（推荐）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 方式 2：运行 main.py
python main.py
```

#### 5. 访问服务
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/health
- **根路径**: http://localhost:8000

---

### 方式二：最小化启动（仅测试 API）

如果只需要测试 API 接口而不使用数据库和 AI 功能：

#### 1. 创建最小环境配置
```bash
# 创建 .env 文件
echo "ENVIRONMENT=testing" > .env
echo "NEO4J_URI=bolt://localhost:7687" >> .env
echo "NEO4J_USER=neo4j" >> .env
echo "NEO4J_PASSWORD=test" >> .env
```

#### 2. 安装最小依赖
```bash
pip install fastapi uvicorn pydantic python-dotenv
```

#### 3. 启动服务
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**注意**: 此模式下部分功能（如知识提取、图谱构建）将不可用。

---

## 🧪 运行测试

### 1. 安装测试依赖
```bash
pip install -r requirements-test.txt
```

### 2. 配置测试环境
```bash
# 确保 .env 文件已配置
# 测试将使用测试数据库或 Mock 数据
```

### 3. 执行测试
```bash
# 运行所有测试
pytest

# 运行特定测试目录
pytest test/api_tests/
pytest test/service_tests/

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

---

## 📁 项目结构
```
backend/
├── app/
│   ├── api/v1/          # API 路由（端点定义）
│   ├── core/            # 核心配置（设置、安全）
│   ├── models/          # 数据模型（SQLAlchemy, Neo4j）
│   ├── services/        # 业务逻辑（知识提取、图谱构建等）
│   └── utils/           # 工具函数
├── test/                # 测试用例
│   ├── api_tests/       # API 接口测试
│   ├── service_tests/   # 服务层测试
│   └── ...
├── uploads/             # 上传文件临时目录
├── exports/             # 导出文件目录
├── .env                 # 环境变量配置（需自行创建）
├── .env.example         # 环境变量模板
├── main.py              # 入口文件
├── requirements.txt     # 生产环境依赖
└── requirements-test.txt # 测试环境依赖
```

---

## 🔌 API 接口概览

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/data/import` | POST | 导入故障树数据文件 |
| `/api/v1/knowledge/extract` | POST | 从文档中提取知识三元组 |
| `/api/v1/fault-tree/generate` | POST | 基于知识图谱生成故障树 |
| `/api/v1/fault-tree/optimize` | POST | 优化现有故障树结构 |
| `/api/health` | GET | 系统健康检查 |
| `/docs` | GET | Swagger API 文档 |

详细文档请访问：http://localhost:8000/docs

---

## ⚙️ 高级配置

### 跨域配置（CORS）
默认允许以下前端端口（开发环境）：
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:8080`

生产环境请在 `.env` 中配置：
```ini
ALLOWED_ORIGINS=http://your-domain.com
```

### 日志配置
日志级别默认为 `INFO`，可在 `.env` 中调整：
```ini
LOG_LEVEL=DEBUG
```

---

## ❓ 常见问题

### Q1: 启动时提示 "Neo4j 数据库连接失败"
**A**: 检查以下项：
1. Neo4j 服务是否已启动
2. `.env` 文件中的 `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` 是否正确
3. 防火墙是否阻止了 7687 端口

### Q2: 导入 PDF/Word 文件失败
**A**: 
1. 确认已安装 `requirements.txt` 中的所有依赖
2. 检查文件路径是否正确
3. PDF 文件需要安装 `pdfplumber` 和 `pytesseract`（OCR 识别）

### Q3: 知识提取速度很慢
**A**: 
1. 首次运行会下载 AI 模型（约数 GB），请耐心等待
2. 后续运行会自动使用缓存的模型
3. 可在 `.env` 中配置 `MODEL_CACHE_DIR` 指定缓存目录

---

## 📝 开发指南

### 添加新的 API 端点
1. 在 `app/api/v1/` 下创建路由文件
2. 在 `main.py` 中注册路由
3. 编写对应的服务层逻辑（`app/services/`）
4. 添加单元测试（`test/`）

### 调试模式
```bash
# 启用热重载
uvicorn main:app --reload --log-level debug
```

---

## 📄 许可证
本项目采用 MIT 许可证
