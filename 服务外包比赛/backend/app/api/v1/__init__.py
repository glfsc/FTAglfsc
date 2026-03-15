"""
API 路由汇总
"""
from fastapi import APIRouter
from app.api.v1.routes import fault_tree
from app.api.v1.routes import ai_chat

router = APIRouter()

# 故障树路由：router 自带 prefix="/fault-tree"，不再加前缀
router.include_router(fault_tree.router)

# AI 对话路由：prefix="/ai"
router.include_router(ai_chat.router)
