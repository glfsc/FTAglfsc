"""
系统配置文件
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
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
    
    # Neo4j 配置
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "glf5549810348"
    
    # Neo4j 连接池参数
    NEO4J_MAX_CONNECTION_POOL_SIZE: int = Field(default=200)
    NEO4J_CONNECTION_ACQUISITION_TIMEOUT: int = Field(default=30)
    NEO4J_MAX_TRANSACTION_RETRY_TIME: int = Field(default=15)
    NEO4J_CONNECTION_TIMEOUT: int = Field(default=10)

    # 其他配置
    ALLOWED_ORIGINS: List[str] = Field(default=["*"])
    
    # DashScope API Key（用于知识抽取）
    DASHSCOPE_API_KEY: Optional[str] = Field(default=None)
    
    # Hugging Face Endpoint（可选）
    HF_ENDPOINT: Optional[str] = Field(default=None)

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # 忽略未定义的额外环境变量


settings = Settings()
