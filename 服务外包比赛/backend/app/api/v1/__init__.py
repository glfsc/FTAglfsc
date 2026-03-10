"""
API 路由汇总
"""
from fastapi import APIRouter
from app.api.v1.routes import fault_tree

router = APIRouter()

# 故障树路由：router 自带 prefix="/fault-tree"，不再加前缀
router.include_router(fault_tree.router)
