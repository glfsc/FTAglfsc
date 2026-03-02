"""
系统配置文件
"""
from pydantic_settings import BaseSettings

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
    NEO4J_PASSWORD: str = "password"
    
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
    
    class Config:
        env_file = ".env"

settings = Settings()
