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
    """知识提取响应"""
    task_id: str
    events: List[FaultEvent]
    gates: List[LogicGate]
    status: str
    progress: float
    traceability: Optional[List[Dict]] = None  # 溯源依据
    accuracy_metrics: Optional[Dict] = None  # 准确率指标

# 故障树相关
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
    """故障树完整数据"""
    tree_id: str
    nodes: List[FaultTreeNode]
    edges: List[FaultTreeEdge]
    metadata: Dict

class FaultTreeGenerateRequest(BaseModel):
    """故障树生成请求"""
    knowledge_id: str = Field(description="知识来源ID")
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
