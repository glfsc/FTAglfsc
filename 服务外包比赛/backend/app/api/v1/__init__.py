"""
API路由汇总
"""
from fastapi import APIRouter
from app.api.v1 import data, knowledge
from app.api.v1.routes import fault_tree
router = APIRouter()

router.include_router(data.router, prefix="/data", tags=["数据导入"])
router.include_router(knowledge.router, prefix="/knowledge", tags=["知识提取"])
# 故障树路由：router 自带 prefix="/fault-tree"，不再加前缀
router.include_router(fault_tree.router)
