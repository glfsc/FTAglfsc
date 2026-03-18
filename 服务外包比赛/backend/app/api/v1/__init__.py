"""
API 路由汇总
"""
from fastapi import APIRouter
from app.api.v1 import fault_tree
from app.api.v1 import ai_chat
from app.api.v1 import document
from app.api.v1 import knowledge

router = APIRouter()

# 故障树路由：router 自带 prefix="/fault-tree"，不再加前缀
router.include_router(fault_tree.router)

# AI 对话路由：prefix="/ai"
router.include_router(ai_chat.router)

# 文档上传路由：prefix="/document"
router.include_router(document.router)

# 知识提取路由：prefix="/knowledge"
router.include_router(knowledge.router)
