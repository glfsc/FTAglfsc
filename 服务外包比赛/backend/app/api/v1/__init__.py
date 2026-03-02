"""
API路由汇总
"""
from fastapi import APIRouter
from app.api.v1 import data, knowledge, fault_tree

router = APIRouter()

router.include_router(data.router, prefix="/data", tags=["数据导入"])
router.include_router(knowledge.router, prefix="/knowledge", tags=["知识提取"])
router.include_router(fault_tree.router, prefix="/fault/tree", tags=["故障树生成"])
