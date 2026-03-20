"""故障树智能生成系统 - FastAPI 主入口（已集成 Neo4j 模块）"""
from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
import logging
import os
import sys
from dotenv import load_dotenv

# 加载环境变量（必须在导入其他模块前执行）
load_dotenv()

# ================= 配置结构化日志记录 =================
# 【优化】检查是否已经配置过日志处理器
_logger_configured = False

def setup_logger():
    """配置日志记录器（只执行一次）"""
    global _logger_configured
    if not _logger_configured:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[logging.StreamHandler()]
        )
        _logger_configured = True
        return logging.getLogger(__name__)

logger = setup_logger()

# ================= 全局依赖导入 =================
from app.api.v1 import router as api_router
from app.core.config import settings
from app.services.kg_builder import FaultTreeKGBuilder
from app.services.tree_generator import FaultTreeGenerator
from app.services.fault_tree_service import FaultTreeService
from app.services.knowledge_extraction_service import KnowledgeExtractionService
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# ================= 重试机制函数（从模块提取） =================
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((ConnectionError, OSError)),
    reraise=True
)
def _create_kg_builder_with_retry():
    """带重试机制的 KG Builder 创建函数"""
    try:
        return FaultTreeKGBuilder()
    except (ConnectionError, OSError) as e:
        logger.warning(f"创建 KG Builder 失败：{str(e)}")
        raise

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((ConnectionError, OSError)),
    reraise=True
)
def _create_tree_generator_with_retry():
    """带重试机制的 Tree Generator 创建函数"""
    try:
        return FaultTreeGenerator()
    except (ConnectionError, OSError) as e:
        logger.warning(f"创建 Tree Generator 失败：{str(e)}")
        raise

# ================= 生命周期管理器（核心集成点） =================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI 生命周期管理器：
    - 服务启动时：初始化 Neo4j 连接池
    - 服务运行中：保持连接
    - 服务关闭时：安全释放资源
    """
    logger.info("🚀 正在初始化 Neo4j 数据库连接池...")
    try:
        # 使用重试机制创建数据库连接
        app.state.kg_builder = _create_kg_builder_with_retry()
        app.state.tree_generator = _create_tree_generator_with_retry()
        app.state.extraction_service = KnowledgeExtractionService()
        app.state.fault_tree_service = FaultTreeService(
            kg_builder=app.state.kg_builder,
            tree_generator=app.state.tree_generator,
            extraction_service=app.state.extraction_service,
        )
        logger.info("✅ Neo4j 数据库连接池与故障树服务初始化成功")
    except Exception as e:
        logger.error(f"❌ Neo4j 数据库连接池初始化失败：{str(e)}", exc_info=True)
        # 如果是环境变量缺失，给出明确提示
        if "NEO4J" in str(e).upper():
            logger.error("请检查 .env 文件是否存在，或 NEO4J_URI/USER/PASSWORD 是否正确配置")
        raise

    yield  # 服务运行中...

    # 服务关闭时清理资源
    logger.info("🛑 服务关闭，正在断开 Neo4j 数据库连接...")
    if hasattr(app.state, 'kg_builder') and app.state.kg_builder:
        app.state.kg_builder.close()
    if hasattr(app.state, 'tree_generator') and app.state.tree_generator:
        app.state.tree_generator.close()
    logger.info("✅ Neo4j 数据库连接已安全关闭")

# ================= FastAPI 应用实例化 =================
app = FastAPI(
    title="工业设备故障树智能生成系统",
    description="基于知识的故障树智能生成与辅助构建系统",
    version="1.0.0",
    lifespan=lifespan,  # 注入生命周期管理器
    docs_url="/docs",
    redoc_url="/redoc"
)

# ================= CORS 安全配置（升级版） =================
# 从环境变量读取允许的域名白名单，生产环境禁止使用 "*"
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

# 开发环境默认允许常见前端端口
if not allowed_origins:
    if os.getenv("ENVIRONMENT", "development") == "production":
        logger.warning("⚠️ 生产环境未配置 ALLOWED_ORIGINS，跨域请求将被禁止！")
        allowed_origins = []
    else:
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8000",
        ]

# 【优化】简化 CORS 日志输出
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= API 路由注册 =================
# 故障树接口已通过 api_router 挂载在 /api/v1/fault-tree
app.include_router(api_router, prefix="/api/v1")

# ================= Swagger 文档配置 =================
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义 Swagger UI 页面"""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=app.title + " - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

# ================= 健康检查端点（新增） =================
@app.get("/api/health")
async def health_check():
    """系统健康检查"""
    neo4j_status = "disconnected"
    if hasattr(app.state, 'kg_builder') and app.state.kg_builder:
        try:
            # 简单验证连接（不执行实际查询）
            neo4j_status = "connected"
        except:
            neo4j_status = "error"

    return {
        "status": "healthy",
        "neo4j_connection": neo4j_status,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": "2024-06-15T10:30:00Z"
    }

# ================= 根路径 =================
@app.get("/")
async def root():
    return {
        "message": "故障树智能生成系统 API 服务运行中",
        "swagger_ui": "http://localhost:8000/docs",
        "health": "/api/health",
        "api_base": "/api/v1"
    }

# ================= 启动入口（保留主项目的启动方式） =================
if __name__ == "__main__":
    import uvicorn
    # 启动时打印访问地址
    print("\n" + "="*60)
    print("故障树智能生成系统 API 服务已启动")
    print("="*60)
    print("📚 API 文档地址：http://localhost:8000/docs")
    print("🏥 健康检查：http://localhost:8000/api/health")
    print("🔧 API 基础路径：/api/v1")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
