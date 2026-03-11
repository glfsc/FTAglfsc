# app/api/v1/routes/fault_tree.py

"""
故障树 API 路由：
- 上传知识三元组入库
- 上传文件
- 提取知识
- 生成可视化故障树 JSON
- 导出故障树到文件

服务通过依赖注入从 app.state 获取，与 main 中 lifespan 初始化的 Neo4j 连接共用。
"""

from fastapi import APIRouter, HTTPException, Request, Depends, Query, UploadFile, File
from fastapi.responses import FileResponse
import json
import os
import uuid
import logging
from datetime import datetime

from app.services.fault_tree_service import FaultTreeService
from app.models.schemas import (
    UploadKnowledgeRequest,
    UploadKnowledgeResponse,
    GenerateTreeResponse,
    KnowledgeExtractRequest,
    KnowledgeExtractResponse,
    FileUploadResponse,
)

logger = logging.getLogger(__name__)


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
        raise HTTPException(status_code=503, detail=f"图谱写入失败或数据库不可用：{str(e)}")


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(..., description="上传的文件"),
):
    """
    上传文件到服务器
    
    Args:
        file: 上传的文件（支持 PDF、TXT、DOCX、MD 等格式）
        
    Returns:
        文件 ID 和基本信息
    """
    try:
        # 创建 uploads 目录
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".txt"
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 获取文件大小
        file_size = len(content)
        
        return {
            "file_id": unique_filename,
            "filename": file.filename or unique_filename,
            "file_size": file_size,
            "status": "success",
            "message": "文件上传成功"
        }
        
    except Exception as e:
        logger.error(f"文件上传失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"文件上传失败：{str(e)}")


@router.post("/extract", response_model=KnowledgeExtractResponse)
async def extract_knowledge(
    request: KnowledgeExtractRequest,
    service: FaultTreeService = Depends(get_fault_tree_service),
):
    """
    从上传的文件中提取故障知识三元组
    
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


@router.get("/generate_tree", response_model=GenerateTreeResponse)
async def generate_tree(
    top_event: str = Query(..., description="顶事件名称"),
    service: FaultTreeService = Depends(get_fault_tree_service),
    export: bool = Query(False, description="是否导出为文件")
):
    """
    按交付模块规范：根据顶事件生成可渲染的故障树 JSON。
    响应格式：{status, data}
    
    Args:
        top_event: 顶事件名称
        export: 是否同时导出为 JSON 文件
    """
    try:
        ft_json = service.tree_generator.build_tree_json(top_event_name=top_event)
        # 知识写入后/生成后建议清缓存，确保后续获取最新数据
        service.tree_generator.clear_cache(top_event)
        
        # 如果需要导出文件
        if export:
            # 只使用顶事件命名（去掉日期时间戳）
            safe_top_event = "".join([c for c in top_event if c.isalnum() or c in '-_']).strip()
            filename = f"fault_tree_{safe_top_event}.json"
            output_path = os.path.join("data/fault_trees", filename)
            
            # 确保导出目录存在
            os.makedirs("data/fault_trees", exist_ok=True)
            
            # 保存到文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(ft_json, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "data": ft_json,
                "export_path": output_path,
                "download_url": f"/api/v1/fault-tree/download/{filename}"
            }
        
        return {"status": "success", "data": ft_json}
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"算法执行失败：{str(e)}")

# 新增：下载故障树文件接口
@router.get("/download/{filename}")
async def download_fault_tree(filename: str):
    """
    下载生成的故障树 JSON 文件
    """
    file_path = os.path.join("data/fault_trees", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

# 新增：下载三元组文件接口
@router.get("/download-triplets/{filename}")
async def download_triplets(filename: str):
    """
    下载知识三元组 JSON 文件
    """
    file_path = os.path.join("data/triplets", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

# 新增：直接生成并下载故障树（一键操作）
@router.post("/generate_and_download")
async def generate_and_download(
    top_event: str = Query(..., description="顶事件名称"),
    service: FaultTreeService = Depends(get_fault_tree_service)
):
    """
    生成故障树并直接返回可下载的 JSON 文件
    """
    try:
        ft_json = service.tree_generator.build_tree_json(top_event_name=top_event)
        service.tree_generator.clear_cache(top_event)
        
        # 生成临时文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fault_tree_{top_event.replace(' ', '_')}_{timestamp}.json"
        output_path = os.path.join("exports", filename)
        
        # 确保导出目录存在
        os.makedirs("exports", exist_ok=True)
        
        # 保存到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ft_json, f, ensure_ascii=False, indent=2)
        
        return FileResponse(
            path=output_path,
            filename=filename,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"算法执行失败：{str(e)}")
