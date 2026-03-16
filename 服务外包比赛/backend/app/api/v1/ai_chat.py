# app/api/v1/ai_chat.py

"""
AI 聊天 API：
- 基于 Qwen-max 的故障树智能分析助手
- 支持多轮对话
- 可分析故障树结构并提供优化建议
"""

import os
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import dashscope
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI 对话"])

# 初始化 DashScope API Key
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
if not dashscope.api_key:
    logger.warning("DASHSCOPE_API_KEY 环境变量未设置，AI 聊天功能将不可用")


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="角色 (user/assistant/system)")
    content: str = Field(..., description="消息内容")


class FaultTreeContext(BaseModel):
    """故障树上下文"""
    nodes: Optional[List[Dict[str, Any]]] = Field(default=None, description="节点列表")
    edges: Optional[List[Dict[str, Any]]] = Field(default=None, description="边列表")


class ChatRequest(BaseModel):
    """聊天请求"""
    messages: List[ChatMessage] = Field(..., description="历史消息")
    context: Optional[FaultTreeContext] = Field(default=None, description="故障树上下文")
    system_prompt: Optional[str] = Field(
        default=None, 
        description="系统提示词（可选，不提供则使用默认）"
    )


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str = Field(..., description="AI 回复内容")
    conversation_id: Optional[str] = Field(default=None, description="会话 ID")


# 默认系统提示词
DEFAULT_SYSTEM_PROMPT = """
你是一位专业的故障树分析（FTA）专家助手。你的任务是：

1. **故障树分析**：帮助用户分析故障树结构的合理性
2. **逻辑验证**：检查与门 (AND) 和或门 (OR) 的使用是否恰当
3. **优化建议**：提供简化故障树、改进逻辑的建议
4. **知识解答**：回答关于故障树分析方法的问题

### 核心能力：
- 识别故障传递路径（BasicEvent → IntermediateEvent → TopEvent）
- 检测可能的逻辑错误（如应该用与门却用了或门）
- 发现缺失的中间节点或冗余节点
- 评估置信度分数的合理性

### 回复规范：
- 使用专业但易懂的语言
- 对于复杂问题，分点阐述
- 如有必要，可提供 JSON 格式的修正建议（用 ```json 代码块包裹）
- 保持客观严谨，不确定的内容要明确说明

### 故障树类型说明：
- type="1": 顶事件 (TopEvent) - 红色节点
- type="2": 中间事件 (IntermediateEvent) - 蓝色节点  
- type="3": 基本事件 (BasicEvent) - 绿色节点

### 逻辑门说明：
- gate="1" 或 "AND": 与门 - 所有输入同时发生才会触发输出
- gate="2" 或 "OR": 或门 - 任一输入发生即可触发输出
"""


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_qwen_api(messages: list, model: str = "qwen-max") -> str:
    """
    调用通义千问 API
    
    Args:
        messages: 消息列表
        model: 模型名称
        
    Returns:
        AI 回复内容
    """
    try:
        response = dashscope.Generation.call(
            model=model,
            messages=messages,
            result_format='message',
            response_format={"type": "text"}
        )
        
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            raise Exception(f"API 调用失败：{response.code} - {response.message}")
    
    except Exception as e:
        logger.error(f"Qwen API 调用失败：{str(e)}")
        raise


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    与 AI 助手进行智能对话
    
    该接口支持：
    - 多轮对话（通过 messages 参数传递历史记录）
    - 故障树上下文注入（自动分析当前故障树结构）
    - 自定义系统提示词
    
    Args:
        request: 聊天请求
        
    Returns:
        AI 回复内容
    """
    try:
        # 构建系统提示词
        system_content = request.system_prompt or DEFAULT_SYSTEM_PROMPT
        
        # 如果有故障树上下文，注入到系统提示中
        if request.context and (request.context.nodes or request.context.edges):
            context_info = "\n\n### 当前分析的故障树结构：\n"
            
            if request.context.nodes:
                context_info += f"\n- 节点总数：{len(request.context.nodes)}\n"
                node_types = {}
                for node in request.context.nodes:
                    node_type = node.get('type', 'unknown')
                    node_types[node_type] = node_types.get(node_type, 0) + 1
                
                for type_code, count in node_types.items():
                    type_name = {"1": "顶事件", "2": "中间事件", "3": "基本事件"}.get(type_code, f"类型{type_code}")
                    context_info += f"  - {type_name}: {count}个\n"
            
            if request.context.edges:
                context_info += f"\n- 连接关系数：{len(request.context.edges)}\n"
            
            # 将上下文信息添加到系统提示词
            system_content += context_info
        
        # 构建完整的消息列表
        messages = [
            {"role": "system", "content": system_content}
        ]
        
        # 添加历史消息
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # 调用 Qwen API
        ai_response = call_qwen_api(messages)
        
        return {
            "response": ai_response,
            "conversation_id": None  # 可以在未来实现会话管理
        }
        
    except Exception as e:
        logger.error(f"AI 对话失败：{str(e)}")
        # 即使出错也返回友好提示，而不是直接抛异常给前端
        return {
            "response": f"非常抱歉，AI 助手暂时无法响应。错误信息：{str(e)}",
            "conversation_id": None
        }