"""
API 路由汇总
v1 版本 - 按功能模块划分：
- /document - 文档上传与解析
- /knowledge - 知识抽取
- /fault-tree - 故障树生成与管理
- /ai - AI 对话与分析
"""
from fastapi import APIRouter
from app.api.v1 import document
from app.api.v1 import knowledge
from app.api.v1 import fault_tree
from app.api.v1 import validate
from app.api.v1 import ai_chat

router = APIRouter()

# 文档管理路由
router.include_router(document.router)

# 知识抽取路由
router.include_router(knowledge.router)

# 故障树路由
router.include_router(fault_tree.router)

# 故障树校验路由
router.include_router(validate.router)

# AI 对话路由
router.include_router(ai_chat.router)
