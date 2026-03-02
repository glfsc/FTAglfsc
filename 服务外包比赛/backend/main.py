"""
故障树智能生成系统 - FastAPI主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1 import router as api_router
from app.core.config import settings

app = FastAPI(
    title="工业设备故障树智能生成系统",
    description="基于知识的故障树智能生成与辅助构建系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix="/api/v1")

# 托管前端静态文件
# app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.get("/")
async def root():
    return {"message": "故障树智能生成系统API服务运行中", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
