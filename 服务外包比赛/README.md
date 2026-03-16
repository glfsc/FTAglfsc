# 故障树智能生成系统 - 联合开发文档

## 📋 项目概述

本项目是一个基于 **FastAPI + Vue 3** 的故障树智能生成系统，利用大语言模型（Qwen-max）从技术文档中自动提取故障知识，生成可视化的故障树结构。

### 核心功能
- 📄 **文档导入**：支持 PDF、TXT、DOCX、MD 等格式
- 🤖 **知识抽取**：使用 Qwen-max 大模型提取故障三元组
- 🌳 **故障树生成**：基于知识图谱自动生成故障树结构
- 🎨 **可视化编辑**：支持拖拽式编辑和逻辑验证
- 💬 **AI 助手**：智能分析故障树结构并提供优化建议

---

## 🏗️ 项目结构

```
CSSO/
├── 服务外包比赛/                    # 项目主目录
│   │
│   ├── backend/                     # 后端服务
│   │   ├── app/                     # 应用主代码
│   │   │   ├── api/v1/              # API路由层
│   │   │   │   ├── __init__.py      # 路由汇总（注册所有 v1 路由）
│   │   │   │   ├── ai_chat.py       # AI 聊天接口（POST /api/v1/ai/chat）
│   │   │   │   ├── document.py      # 文档上传接口（POST /api/v1/document/upload）
│   │   │   │   ├── fault_tree.py    # 故障树操作接口（上传、生成、导出）
│   │   │   │   ├── knowledge.py     # 知识抽取接口（POST /api/v1/knowledge/extract）
│   │   │   │   └── validate.py      # 逻辑验证接口（校验故障树合理性）
│   │   │   │
│   │   │   ├── core/                # 核心配置层
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py        # 配置管理（Settings 模型，环境变量读取）
│   │   │   │   └── database.py      # 数据库连接（Neo4j、PostgreSQL）
│   │   │   │
│   │   │   ├── models/              # 数据模型层
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas.py       # Pydantic Schema（请求/响应模型定义）
│   │   │   │   └── triplets.py      # 三元组模型（故障知识三元组结构）
│   │   │   │
│   │   │   ├── services/            # 业务逻辑层
│   │   │   │   ├── __init__.py
│   │   │   │   ├── fault_tree_service.py      # 故障树服务（知识抽取 + 树生成统一入口）
│   │   │   │   ├── kg_builder.py              # 知识图谱构建（三元组写入 Neo4j）
│   │   │   │   ├── knowledge_extraction_service.py  # 知识抽取服务（调用 Qwen API）
│   │   │   │   ├── multimodal_encoder.py      # 多模态编码器（处理图文混合内容）
│   │   │   │   ├── tree_generator.py          # 故障树生成器（图算法、布局计算）
│   │   │   │   └── triplet_extractor.py       # Qwen 提取器（封装 API 调用）
│   │   │   │
│   │   │   └── utils/               # 工具函数层
│   │   │       ├── __init__.py
│   │   │       └── logger.py        # 日志配置（结构化日志输出）
│   │   │
│   │   ├── test/                    # 测试模块（按功能分类）
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py          # pytest 配置和共享工具函数
│   │   │   ├── README.md            # 测试使用说明
│   │   │   ├── api_tests/           # API接口测试
│   │   │   │   ├── test_ai_chat.py  # AI 聊天测试（7 个用例）
│   │   │   │   └── test_fault_tree.py  # 故障树 API 测试（4 个用例）
│   │   │   ├── service_tests/       # 服务层测试
│   │   │   │   └── test_knowledge_extraction.py  # 知识抽取测试
│   │   │   ├── model_tests/         # 数据模型测试
│   │   │   │   └── test_schemas.py  # Schema 验证测试（6 个用例）
│   │   │   ├── core_tests/          # 核心功能测试
│   │   │   └── integration_tests/   # 集成测试（完整工作流程）
│   │   │
│   │   ├── data/                    # 数据目录
│   │   │   ├── fault_trees/         # 生成的故障树 JSON 文件
│   │   │   └── triplets/            # 提取的三元组 JSON 文件
│   │   │
│   │   ├── uploads/                 # 上传文件临时存储
│   │   ├── exports/                 # 导出文件存储
│   │   │
│   │   ├── main.py                  # 应用入口（FastAPI 实例、lifespan 配置）
│   │   ├── .env                     # 环境变量配置（数据库、API Key）
│   │   ├── .env.example             # 环境变量模板
│   │   ├── requirements.txt         # Python 依赖清单
│   │   ├── requirements-test.txt    # 测试依赖清单
│   │   ├── pyproject.toml           # pytest 配置文件
│   │   ├── 运行测试.bat             # 测试启动脚本（交互式菜单）
│   │   └── 测试框架使用指南.md       # 测试框架详细说明
│   │
│   ├── frontend/                    # 前端应用
│   │   ├── src/                     # 源代码
│   │   │   ├── api/                 # API 调用封装
│   │   │   │   └── index.js         # 统一 API接口（axios 实例、接口函数）
│   │   │   │
│   │   │   ├── components/          # 可复用组件
│   │   │   │   ├── AIChat.vue       # AI 聊天组件（对话界面、故障树上下文注入）
│   │   │   │   ├── FaultTreeNode.vue  # 故障树节点组件（事件节点渲染）
│   │   │   │   ├── GateNode.vue     # 逻辑门组件（AND/OR 门图形）
│   │   │   │   ├── Sidebar.vue      # 侧边栏组件（节点属性编辑）
│   │   │   │   └── GateEdge.vue     # 连线组件（逻辑关系可视化）
│   │   │   │
│   │   │   ├── pages/               # 页面组件
│   │   │   │   ├── StudioPage.vue   # 工作台页面（主编辑界面）
│   │   │   │   ├── GeneratePage.vue # 生成页面（上传文档、触发抽取）
│   │   │   │   ├── ExportPage.vue   # 导出页面（下载 JSON/PNG/Word）
│   │   │   │   ├── VerifyPage.vue   # 验证页面（逻辑检验、AI 优化）
│   │   │   │   └── FaultTreeVisualization.vue  # 可视化页面（完整故障树展示）
│   │   │   │
│   │   │   ├── router/              # 路由配置
│   │   │   │   └── index.js         # Vue Router 配置（页面路由定义）
│   │   │   │
│   │   │   ├── stores/              # 状态管理
│   │   │   │   └── faultTree.js     # Pinia Store（故障树全局状态）
│   │   │   │
│   │   │   ├── App.vue              # 根组件
│   │   │   └── main.js              # 入口文件（Vue 实例化、插件注册）
│   │   │
│   │   ├── public/                  # 静态资源
│   │   ├── package.json             # Node.js 依赖配置
│   │   ├── vite.config.js           # Vite 构建配置
│   │   └── README.md                # 前端说明文档
│   │
│   ├── API文档.md                   # API接口详细文档
│   ├── 快速启动.bat                  # 一键启动脚本（前后端同时启动）
│   ├── 安装依赖.bat                  # 依赖安装脚本（前后端分别安装）
│   ├── deploy.bat                   # 部署脚本
│   └── deploy-frontend.bat          # 前端部署脚本
│
└── .conda/                          # Python 虚拟环境（不纳入版本控制）
```

---

## 🔧 技术栈

### 后端技术
| 技术 | 版本 | 用途 |
|------|------|------|
| **Python** | 3.8+ | 主要编程语言 |
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
- Python 3.8+
- Node.js 16+
- Neo4j 4.x+（或 5.x）

### 1️⃣ 克隆项目
```bash
git clone <repository-url>
cd CSSO/服务外包比赛
```

### 2️⃣ 安装后端依赖
```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-test.txt  # 测试依赖（可选）
```

### 3️⃣ 配置环境变量
编辑 `backend/.env` 文件：
```ini
# Neo4j 配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# AI 模型配置
DASHSCOPE_API_KEY=sk-your-api-key

# 其他配置
MODEL_NAME=qwen-max
```

### 4️⃣ 安装前端依赖
```bash
cd ../frontend
npm install
```

### 5️⃣ 启动服务

**方式一：使用快速启动脚本（推荐）**
```bash
# 在项目根目录
.\快速启动.bat
```

**方式二：手动启动**
```bash
# 终端 1 - 启动后端
cd backend
python main.py

# 终端 2 - 启动前端
cd frontend
npm run dev
```

### 6️⃣ 访问应用
- 前端：http://localhost:5173
- 后端 API文档：http://localhost:8000/docs

---

## 📡 API接口说明

### 基础信息
- **基础 URL**: `http://localhost:8000/api/v1`
- **数据格式**: JSON
- **字符编码**: UTF-8

### 核心接口

#### 1. 文档上传
```http
POST /api/v1/document/upload
Content-Type: multipart/form-data

参数：file (文件对象)

响应：
{
  "file_id": "uuid",
  "filename": "设备手册.pdf",
  "file_size": 1024000,
  "status": "success"
}
```

#### 2. 知识抽取
```http
POST /api/v1/knowledge/extract
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
  "status": "completed",
  "progress": 1.0
}
```

#### 3. 上传知识三元组
```http
POST /api/v1/fault-tree/upload_knowledge

{
  "triplets": [
    {
      "subject_name": "电源故障",
      "subject_type": "BasicEvent",
      "relation": "resultsIn",
      "object_name": "系统故障",
      "object_type": "TopEvent",
      "confidence": 0.95
    }
  ]
}
```

#### 4. 生成故障树
```http
GET /api/v1/fault-tree/generate_tree?top_event=系统故障&export=false

响应：
{
  "status": "success",
  "data": {
    "nodeList": [...],
    "linkList": [...]
  }
}
```

#### 5. AI 聊天
```http
POST /api/v1/ai/chat

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

#### 6. 导出故障树
```http
GET /api/v1/fault-tree/download/{filename}
```

完整 API文档请访问：http://localhost:8000/docs

---

## 🧪 测试说明

### 运行测试

**方式一：使用批处理脚本**
```bash
cd backend
.\运行测试.bat
```

**方式二：pytest 命令**
```bash
# 运行所有测试
pytest

# 运行特定模块
pytest test/api_tests/
pytest test/service_tests/

# 运行单个测试
pytest test/api_tests/test_ai_chat.py::TestAIChatAPI::test_basic_chat -v
```

### 测试覆盖率
```bash
pytest --cov=app --cov-report=html
start htmlcov\index.html
```

### 测试文件说明
- `test/api_tests/`: API接口测试（使用 FastAPI TestClient）
- `test/service_tests/`: 服务层测试（Mock 外部依赖）
- `test/model_tests/`: 数据模型测试（Schema 验证）
- `test/integration_tests/`: 集成测试（完整流程）

详细测试文档见：`backend/测试框架使用指南.md`

---

## 👥 联合开发指南

### 分支管理
```bash
# 主分支
main          # 生产环境代码
develop       # 开发分支
feature/*     # 功能分支
bugfix/*      # 修复分支
```

### 开发流程
1. **创建功能分支**
   ```bash
   git checkout develop
   git checkout -b feature/your-feature
   ```

2. **本地开发**
   ```bash
   # 修改代码后运行测试
   cd backend
   .\运行测试.bat  # 选择对应模块测试
   
   # 确保测试通过
   ```

3. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加 XXX 功能"
   ```

4. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature
   # 在 GitHub/GitLab 创建 Pull Request
   ```

### 代码规范

#### Python
- 遵循 PEP 8 规范
- 使用 type hints
- 函数需要 docstring
- 测试覆盖率 > 80%

```python
def extract_knowledge(text: str, source: str) -> Dict[str, Any]:
    """
    从文本中提取故障知识
    
    Args:
        text: 输入文本
        source: 来源标记
        
    Returns:
        包含三元组的字典
    """
    pass
```

#### Vue
- 使用 Composition API
- 组件名 PascalCase
- Props 类型检查

```vue
<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  nodeData: NodeData;
  editable?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  editable: true
});
</script>
```

### 沟通协作
- **每日站会**: 同步进度和问题
- **代码审查**: PR 需要至少一人 review
- **文档更新**: 功能完成后更新相关文档

---

## 📝 常见问题

### Q1: Neo4j 连接失败？
A: 检查 `.env` 中的配置，确保 Neo4j 服务已启动：
```bash
neo4j start  # Linux/macOS
neo4j console  # Windows
```

### Q2: API Key 无效？
A: 确认 `DASHSCOPE_API_KEY` 配置正确，查看[ DashScope 官网](https://dashscope.aliyuncs.com/)

### Q3: 前端跨域问题？
A: 后端已配置 CORS，如仍有问题检查 `main.py` 中的中间件配置。

### Q4: 测试导入错误？
A: 确保在项目根目录运行 pytest，或调用 `add_project_to_path()`。

---

## 📚 相关文档

- `backend/README.md`: 后端详细说明
- `frontend/README.md`: 前端详细说明
- `backend/测试框架使用指南.md`: 测试使用指南
- `API文档.md`: API接口完整文档
- `服务外包比赛/技术实现方案.md`: 技术架构文档

---

## 🎯 下一步计划

### 待开发功能
- [ ] 用户认证和权限管理
- [ ] 故障树版本控制
- [ ] 多人协作编辑
- [ ] 更多导出格式（SVG、Excel）
- [ ] 性能优化（缓存、异步任务）

### 技术债务
- [ ] 增加单元测试覆盖率到 90%
- [ ] 添加 API 限流中间件
- [ ] 优化数据库查询性能
- [ ] 完善错误处理和日志记录

---

## 📞 联系方式

如有问题，请通过以下方式联系：
- 项目 Issues: https://github.com/your-repo/issues
- 团队邮箱：team@example.com

---

**最后更新**: 2026-03-15  
**维护者**: 故障树开发团队
