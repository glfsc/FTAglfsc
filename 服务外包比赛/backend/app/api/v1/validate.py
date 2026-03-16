# app/api/v1/validate.py

"""
故障树实时校验 API：
- 逻辑结构校验
- AI 优化建议生成
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fault-tree", tags=["故障树校验"])


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


class ValidationResult(BaseModel):
    """逻辑校验结果"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[Dict]  # AI 优化建议


class ValidateRequest(BaseModel):
    """校验请求"""
    nodes: List[FaultTreeNode]
    edges: List[FaultTreeEdge]
    top_event: Optional[str] = None


@router.post("/validate", response_model=ValidationResult)
async def validate_fault_tree(request: ValidateRequest):
    """
    实时校验故障树的逻辑结构
    
    Args:
        request: 校验请求（包含节点和边）
        
    Returns:
        校验结果（包含错误、警告和建议）
    """
    try:
        errors = []
        warnings = []
        suggestions = []
        
        # 1. 基础校验
        # 检查是否有顶事件
        if not request.nodes:
            errors.append("故障树不能为空")
            return ValidationResult(valid=False, errors=errors, warnings=warnings, suggestions=suggestions)
        
        # 检查节点 ID 唯一性
        node_ids = [node.node_id for node in request.nodes]
        if len(node_ids) != len(set(node_ids)):
            errors.append("存在重复的节点 ID")
        
        # 检查边的连接是否有效
        for edge in request.edges:
            if edge.source not in node_ids:
                errors.append(f"边的源节点 {edge.source} 不存在")
            if edge.target not in node_ids:
                errors.append(f"边的目标节点 {edge.target} 不存在")
        
        # 检查是否有孤立节点（除了顶事件）
        connected_nodes = set()
        for edge in request.edges:
            connected_nodes.add(edge.source)
            connected_nodes.add(edge.target)
        
        for node in request.nodes:
            if node.node_id not in connected_nodes and node.level == 0:
                # 顶事件可以没有父节点
                continue
            elif node.node_id not in connected_nodes:
                warnings.append(f"节点 {node.label} ({node.node_id}) 是孤立节点")
        
        # 2. 逻辑门校验
        gate_nodes = [node for node in request.nodes if node.metadata and node.metadata.get('gate')]
        for gate in gate_nodes:
            gate_type = gate.metadata.get('gate')
            inputs = [edge.source for edge in request.edges if edge.target == gate.node_id]
            
            if gate_type == 'AND' and len(inputs) < 2:
                warnings.append(f"与门 {gate.label} 只有一个输入，建议检查逻辑是否正确")
            elif gate_type == 'OR' and len(inputs) < 2:
                warnings.append(f"或门 {gate.label} 只有一个输入，建议检查逻辑是否正确")
        
        # 3. 使用 AI 生成优化建议
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if api_key and not errors:
            try:
                tree_data = {
                    "nodes": [node.model_dump() for node in request.nodes],
                    "edges": [edge.model_dump() for edge in request.edges],
                    "top_event": request.top_event
                }
                
                system_instruction = """
你是一个专业的故障树分析专家。你的任务是校验用户提供的故障树结构并给出优化建议。

请检查以下方面：
1. 逻辑门使用是否合理（与门/或门）
2. 是否存在冗余事件
3. 事件分类是否准确（顶事件/中间事件/基本事件）
4. 概率分配是否合理
5. 整体结构是否完整

返回格式：
- 如果有严重错误，在 errors 中列出
- 如果有潜在问题，在 warnings 中列出
- 给出 3-5 条具体的优化建议
"""
                
                messages = [
                    {"role": Role.SYSTEM, "content": system_instruction},
                    {"role": Role.USER, "content": f"请校验以下故障树结构：{json.dumps(tree_data, ensure_ascii=False)}"}
                ]
                
                response = Generation.call(
                    model='qwen-max',
                    messages=messages,
                    result_format='message',
                    api_key=api_key
                )
                
                if response.status_code == 200:
                    ai_feedback = response.output.choices[0].message.content
                    # 解析 AI 返回的建议（简化处理）
                    suggestions.append({
                        "type": "ai_optimization",
                        "content": ai_feedback
                    })
            except Exception as e:
                logger.warning(f"AI 校验失败，使用基础校验：{str(e)}")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            valid=is_valid,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions
        )
        
    except Exception as e:
        logger.error(f"故障树校验异常：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"校验服务异常：{str(e)}")
