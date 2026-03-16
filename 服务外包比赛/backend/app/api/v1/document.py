# app/api/v1/document.py

"""
文档上传与解析 API：
- 上传文件到服务器
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
import os
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/document", tags=["文档管理"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(..., description="上传的文件（支持 PDF、TXT、DOCX、MD 等格式）"),
):
    """
    上传文档到服务器
    
    Args:
        file: 上传的文件
        
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
            "message": "文档上传成功"
        }
        
    except Exception as e:
        logger.error(f"文档上传失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"文档上传失败：{str(e)}")
