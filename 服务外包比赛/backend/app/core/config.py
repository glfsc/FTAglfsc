"""
系统配置文件
"""
from pydantic_settings import BaseSettings
from typing import List, Optional  # 保留原有导入
from pydantic_settings import BaseSettings  # 关键：添加 Field 导入
from pydantic import Field
class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "故障树智能生成系统"
    VERSION: str = "1.0.0"
    
    # 数据库配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "fault_tree_db"
    
    # Neo4j配置
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "glf5549810348"
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: set = {".docx", ".xlsx", ".csv", ".txt"}
    
    # AI模型配置
    MODEL_NAME: str = "THUDM/chatglm3-6b"  # 可替换为Llama 3
    MODEL_CACHE_DIR: str = "models"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24小时

    # ===== 新增：Neo4j 连接池工业级参数 =====
    NEO4J_MAX_CONNECTION_POOL_SIZE: int = Field(
        default=200,
        description="最大连接池大小（应对高并发）"
    )
    NEO4J_CONNECTION_ACQUISITION_TIMEOUT: int = Field(
        default=30,
        description="获取连接最大等待时间(秒)"
    )
    NEO4J_MAX_TRANSACTION_RETRY_TIME: int = Field(
        default=15,
        description="事务重试最大时间窗口(秒)"
    )
    NEO4J_CONNECTION_TIMEOUT: int = Field(
        default=10,
        description="单个连接超时时间(秒)"
    )
    NEO4J_URI: str = Field(default="bolt://localhost:7687")
    NEO4J_USER: str = Field(default="neo4j")
    NEO4J_PASSWORD: str = Field(default="your_password")
    NEO4J_MAX_CONNECTION_POOL_SIZE: int = Field(default=200)  # 报错行对应的配置

    # 其他配置项（如PostgreSQL、CORS等）
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    ALLOWED_ORIGINS: List[str] = Field(default=["*"])

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
