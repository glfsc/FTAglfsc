# app/api/v1/routes/ai_chat.py

"""
AI 对话 API 路由：
- 提供基于 Qwen-max 的智能对话服务
- 支持故障树分析
"""

import logging
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import re
import os
from dashscope import Generation
from dashscope.api_entities.dashscope_response import Role

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI 对话"])


class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context: Optional[Dict[str, Any]] = None  # 故障树上下文


class ChatResponse(BaseModel):
    response: str
    success: bool = True


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    与 AI 分析师对话，支持故障树分析、问题诊断和自动生成
    
    Args:
        request: 对话请求，包含消息历史和故障树上下文
        
    Returns:
        AI 回复的消息
    """
    try:
        # 获取 DashScope API Key
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="DashScope API Key 未配置")
        
        # 构建系统提示词
        system_instruction = """
你是一个专业的故障树分析 AI 助手。你的任务是帮助用户分析故障树结构、解释事件概率、识别关键路径等。

当前故障树上下文：
""" + json.dumps(request.context, ensure_ascii=False, indent=2) + """

重要功能：
- 如果用户要求修改、更新或生成故障树（例如："添加基本事件 X"、"改变顶事件为 Y"、"创建爆胎的故障树"），你必须返回一个 JSON 对象表示新的故障树结构。
- JSON 结构必须符合以下格式：
  {
    "nodeList": [
      { "id": "node-1", "name": "Top Event", "type": "1", "gate": "2", "event": { "id": "T01", "probability": "0.01" } },
      ...
    ],
    "linkList": [
      { "sourceId": "node-2", "targetId": "node-1" }, // Child -> Parent
      ...
    ]
  }
- 将 JSON 块用 ```json ... ``` 包裹，然后在后面提供简短的文字说明。

回答要求：
- 简洁、专业、有帮助
- 使用 Markdown 格式（加粗关键术语、列表等）
- 优先使用中文回答
"""

        # 构建消息历史
        messages = []
        
        # 添加系统指令
        messages.append({
            "role": Role.SYSTEM,
            "content": system_instruction
        })
        
        # 添加历史消息
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # 调用 Qwen-max API
        response = Generation.call(
            model='qwen-max',
            messages=messages,
            result_format='message',  # set the result to be "message" format
            api_key=api_key
        )
        
        if response.status_code == 200:
            ai_response = response.output.choices[0].message.content
            
            return ChatResponse(
                response=ai_response,
                success=True
            )
        else:
            logger.error(f"Qwen API 调用失败：{response.code} - {response.message}")
            raise HTTPException(
                status_code=500, 
                detail=f"AI 服务调用失败：{response.message}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI 对话异常：{str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"AI 服务异常：{str(e)}")
