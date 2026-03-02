# 故障树智能生成系统 - 后端

## 技术栈
- FastAPI：高性能异步Web框架
- PostgreSQL：结构化数据存储
- Neo4j：知识图谱存储
- Transformers：大模型推理
- NetworkX：图结构计算

## 快速启动

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，填入数据库配置
```

### 3. 启动服务
```bash
python main.py
```

访问 http://localhost:8000/docs 查看API文档

## 项目结构
```
backend/
├── app/
│   ├── api/v1/          # API路由
│   ├── core/            # 核心配置
│   ├── models/          # 数据模型
│   ├── services/        # 业务逻辑
│   └── utils/           # 工具函数
├── main.py              # 入口文件
└── requirements.txt     # 依赖清单
```

## API接口
- POST /api/v1/data/import - 文件导入
- POST /api/v1/knowledge/extract - 知识提取
- POST /api/v1/fault/tree/generate - 故障树生成
- POST /api/v1/fault/tree/optimize - 故障树优化
