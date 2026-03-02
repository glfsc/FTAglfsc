"""
数据导入模块API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.file_parser import FileParser
from app.models.schemas import FileUploadResponse
from app.core.config import settings
import uuid
import os

router = APIRouter()

@router.post("/import", response_model=FileUploadResponse)
async def import_file(file: UploadFile = File(...)):
    """
    导入工业设备文档
    支持格式：DOCX, XLSX, CSV, TXT
    """
    # 文件大小校验
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"文件大小超过限制（{settings.MAX_FILE_SIZE / 1024 / 1024}MB）")
    
    # 文件格式校验
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式，仅支持：{settings.ALLOWED_EXTENSIONS}")
    
    # 保存文件
    file_id = str(uuid.uuid4())
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{file_ext}")
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 解析文件
    try:
        parser = FileParser()
        parsed_data = parser.parse(file_path, file_ext)
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_size=len(file_content),
            status="success",
            message=f"文件解析成功，提取{len(parsed_data)}条文本记录"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件解析失败：{str(e)}")

@router.get("/files")
async def list_files():
    """获取已上传文件列表"""
    # TODO: 从数据库查询文件列表
    return {"files": []}
