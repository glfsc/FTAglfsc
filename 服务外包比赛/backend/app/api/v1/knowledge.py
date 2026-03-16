# app/api/v1/knowledge.py

"""
知识抽取 API：
- 从文档中提取故障知识三元组
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.schemas import (
    KnowledgeExtractRequest,
    KnowledgeExtractResponse,
)
from app.services.fault_tree_service import FaultTreeService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/knowledge", tags=["知识抽取"])


def get_fault_tree_service(request: Request) -> FaultTreeService:
    """从 app.state 获取故障树服务（由 main lifespan 注入）。"""
    if not hasattr(request.app.state, "fault_tree_service"):
        raise HTTPException(
            status_code=503,
            detail="故障树服务未初始化，请检查 Neo4j 连接与应用启动状态",
        )
    return request.app.state.fault_tree_service


@router.post("/extract", response_model=KnowledgeExtractResponse)
async def extract_knowledge(
    request: KnowledgeExtractRequest,
    service: FaultTreeService = Depends(get_fault_tree_service),
):
    """
    从上传的文档中提取故障知识三元组
    
    Args:
        request: 提取请求（包含 file_id, top_event）
        
    Returns:
        提取的三元组、事件和逻辑门
    """
    try:
        result = service.extract_knowledge(request)
        
        return {
            "task_id": result["task_id"],
            "triplets": result["triplets"],
            "events": result["events"],
            "gates": result["gates"],
            "status": result["status"],
            "progress": result["progress"],
            "traceability": result.get("traceability"),
            "accuracy_metrics": result.get("accuracy_metrics"),
            "output_file": result.get("output_file")  # 用于测试的输出文件路径
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"知识提取失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"知识提取失败：{str(e)}")
