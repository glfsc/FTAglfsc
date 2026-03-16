"""
数据模型测试模块
用于测试 Schema 和数据验证功能
"""

import os
import sys
import pytest
from pydantic import ValidationError

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.models.schemas import (
    KnowledgeExtractRequest,
    KnowledgeExtractResponse,
    UploadKnowledgeRequest,
    UploadKnowledgeResponse,
    GenerateTreeResponse,
    ChatMessage,
    FaultTreeContext,
    ChatRequest,
)


class TestSchemas:
    """Schema 测试类"""
    
    def test_knowledge_extract_request(self):
        """测试知识抽取请求模型"""
        request = KnowledgeExtractRequest(
            file_id="test_file_123",
            top_event="系统故障"
        )
        
        assert request.file_id == "test_file_123"
        assert request.top_event == "系统故障"
        print("\n知识抽取请求模型测试通过")
    
    def test_upload_knowledge_request(self):
        """测试上传知识请求模型"""
        from app.models.schemas import Triplet
        
        triplet = Triplet(
            subject_name="电源故障",
            subject_type="BasicEvent",
            relation="resultsIn",
            object_name="系统故障",
            object_type="TopEvent",
            confidence=0.95,
            source="测试文档"
        )
        
        request = UploadKnowledgeRequest(triplets=[triplet])
        
        assert len(request.triplets) == 1
        assert request.triplets[0].subject_name == "电源故障"
        print("\n上传知识请求模型测试通过")
    
    def test_chat_message(self):
        """测试聊天消息模型"""
        message = ChatMessage(
            role="user",
            content="你好，请帮我分析故障树"
        )
        
        assert message.role == "user"
        assert message.content == "你好，请帮我分析故障树"
        print("\n聊天消息模型测试通过")
    
    def test_fault_tree_context(self):
        """测试故障树上下文模型"""
        context = FaultTreeContext(
            nodes=[
                {"id": "1", "type": "1", "label": "系统故障"},
                {"id": "2", "type": "3", "label": "电源故障"}
            ],
            edges=[
                {"source": "2", "target": "1"}
            ]
        )
        
        assert len(context.nodes) == 2
        assert len(context.edges) == 1
        print("\n故障树上下文模型测试通过")
    
    def test_chat_request(self):
        """测试聊天请求模型"""
        request = ChatRequest(
            messages=[
                ChatMessage(role="user", content="你好")
            ],
            context=FaultTreeContext(nodes=[], edges=[])
        )
        
        assert len(request.messages) == 1
        assert request.context is not None
        print("\n聊天请求模型测试通过")
    
    def test_validation_error(self):
        """测试数据验证错误"""
        try:
            # 缺少必填字段
            ChatMessage(role="invalid_role")  # type: ignore
            assert False, "应该抛出 ValidationError"
        except ValidationError as e:
            print(f"\n数据验证错误测试通过：{e.error_count()} 个错误")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
