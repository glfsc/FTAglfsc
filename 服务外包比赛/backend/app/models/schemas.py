"""
数据模型定义（Pydantic）
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 文件上传相关
class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_size: int
    status: str
    message: str

# 知识提取相关
class FaultEvent(BaseModel):
    """故障事件"""
    event_id: str
    event_name: str
    event_type: str  # top/middle/bottom
    description: Optional[str] = None
    probability: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None  # 溯源信息

class LogicGate(BaseModel):
    """逻辑门"""
    gate_id: str
    gate_type: str  # AND/OR/NOT
    input_events: List[str]
    output_event: str

class KnowledgeExtractRequest(BaseModel):
    """知识提取请求"""
    file_id: str = Field(description="文件ID或文件ID列表")
    top_event: str = Field(description="用户指定的顶事件")
    requirements: Optional[str] = Field(default=None, description="生成要求（提示词）")
    max_depth: int = Field(default=5, description="最大深度")

class KnowledgeExtractResponse(BaseModel):
    """知识提取响应（完整版，含事件与逻辑门）"""
    task_id: str
    events: List[FaultEvent]
    gates: List[LogicGate]
    status: str
    progress: float
    traceability: Optional[List[Dict]] = None  # 溯源依据
    accuracy_metrics: Optional[Dict] = None  # 准确率指标


class KnowledgeIngestResponse(BaseModel):
    """知识入库响应（从文档提取并写入知识图谱后的简要结果）"""
    task_id: str
    inserted: int
    skipped: int
    duplicates: int
    status: str

# 故障树相关
class FaultTreeTriplet(BaseModel):
    """知识三元组（交付模块上传格式）"""
    subject_name: str
    subject_type: str
    relation: str
    object_name: str
    object_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: Optional[str] = None


class UploadKnowledgeRequest(BaseModel):
    """POST /upload_knowledge 请求体"""
    triplets: List[FaultTreeTriplet]


class UploadKnowledgeResponse(BaseModel):
    """POST /upload_knowledge 响应体（交付模块格式）"""
    status: str
    message: str


class GenerateTreeResponse(BaseModel):
    """GET /generate_tree 响应体（交付模块格式）"""
    status: str
    data: Dict[str, Any]


class FaultTreeNode(BaseModel):
    """故障树节点"""
    node_id: str
    node_type: str  # event/gate
    label: str
    level: float  # 支持小数以便插入逻辑门
    x: Optional[float] = None
    y: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class FaultTreeEdge(BaseModel):
    """故障树边"""
    source: str
    target: str
    edge_type: str

class FaultTreeData(BaseModel):
    """故障树完整数据（节点/边格式）"""
    tree_id: str
    nodes: List[FaultTreeNode]
    edges: List[FaultTreeEdge]
    metadata: Dict


class FaultTreeGenerateResponse(BaseModel):
    """故障树生成接口响应（含前端可直接使用的 nodeList/linkList）"""
    tree_id: str
    tree_data: Dict[str, Any] = Field(description="含 nodeList、linkList 等，供前端渲染")
    metadata: Dict[str, Any]

class FaultTreeGenerateRequest(BaseModel):
    """故障树生成请求"""
    knowledge_id: Optional[str] = Field(default=None, description="知识来源ID，可选")
    top_event: str = Field(description="顶事件名称")
    max_depth: int = Field(default=5, ge=1, le=10, description="最大深度")
    requirements: Optional[str] = Field(default=None, description="生成要求")

class FaultTreeOptimizeRequest(BaseModel):
    """故障树优化请求（专家修正）"""
    tree_id: str
    modified_nodes: List[FaultTreeNode]
    modified_edges: List[FaultTreeEdge]
    optimization_notes: Optional[str] = None  # 专家修正说明

class ValidationResult(BaseModel):
    """逻辑校验结果"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[Dict]  # AI优化建议
