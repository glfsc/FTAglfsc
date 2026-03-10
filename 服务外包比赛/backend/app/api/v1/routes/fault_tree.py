# app/api/v1/routes/fault_tree.py

"""
故障树 API 路由：
- 上传知识三元组入库
- 生成可视化故障树 JSON

服务通过依赖注入从 app.state 获取，与 main 中 lifespan 初始化的 Neo4j 连接共用。
"""

from fastapi import APIRouter, HTTPException, Request, Depends, Query

from app.services.fault_tree_service import FaultTreeService
from app.models.schemas import (
    UploadKnowledgeRequest,
    UploadKnowledgeResponse,
    GenerateTreeResponse,
)


def get_fault_tree_service(request: Request) -> FaultTreeService:
    """从 app.state 获取故障树服务（由 main lifespan 注入）。"""
    if not hasattr(request.app.state, "fault_tree_service"):
        raise HTTPException(
            status_code=503,
            detail="故障树服务未初始化，请检查 Neo4j 连接与应用启动状态",
        )
    return request.app.state.fault_tree_service


router = APIRouter(prefix="/fault-tree", tags=["故障树生成"])


@router.post("/upload_knowledge", response_model=UploadKnowledgeResponse)
async def upload_knowledge(
    request: UploadKnowledgeRequest,
    service: FaultTreeService = Depends(get_fault_tree_service),
):
    """
    按交付模块规范：接收结构化三元组写入知识图谱。
    响应格式：{status, message}
    """
    try:
        inserted, skipped, duplicates = service.kg_builder.insert_triplets_batch(
            [t.model_dump() for t in request.triplets]
        )
        return {
            "status": "success",
            "message": f"处理完成！有效入库 {inserted} 条，拦截脏数据 {skipped} 条，内存去重 {duplicates} 条。",
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"图谱写入失败或数据库不可用: {str(e)}")


@router.get("/generate_tree", response_model=GenerateTreeResponse)
async def generate_tree(
    top_event: str = Query(..., description="顶事件名称"),
    service: FaultTreeService = Depends(get_fault_tree_service),
):
    """
    按交付模块规范：根据顶事件生成可渲染的故障树 JSON。
    响应格式：{status, data}
    """
    try:
        ft_json = service.tree_generator.build_tree_json(top_event_name=top_event)
        # 知识写入后/生成后建议清缓存，确保后续获取最新数据
        service.tree_generator.clear_cache(top_event)
        return {"status": "success", "data": ft_json}
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"算法执行失败: {str(e)}")