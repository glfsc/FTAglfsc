"""
AI 聊天 API 测试模块
用于测试 AI 对话功能的各项功能
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from main import app
from app.api.v1.ai_chat import ChatMessage, FaultTreeContext, ChatRequest


class TestAIChatAPI:
    """AI 聊天 API 测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.client = TestClient(app)
        
    def test_basic_chat(self):
        """测试基础聊天功能"""
        request_data = {
            "messages": [
                {
                    "role": "user",
                    "content": "你好，请介绍一下故障树分析方法"
                }
            ]
        }
        
        response = self.client.post("/api/v1/ai/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        print(f"\nAI 回复：{data['response']}")
    
    def test_chat_with_fault_tree_context(self):
        """测试带故障树上下文的聊天"""
        request_data = {
            "messages": [
                {
                    "role": "user",
                    "content": "请分析这个故障树的逻辑结构是否合理"
                }
            ],
            "context": {
                "nodes": [
                    {"id": "1", "type": "1", "label": "系统故障"},
                    {"id": "2", "type": "2", "label": "电源故障"},
                    {"id": "3", "type": "3", "label": "电池老化"},
                    {"id": "4", "type": "3", "label": "电路短路"}
                ],
                "edges": [
                    {"source": "3", "target": "2"},
                    {"source": "4", "target": "2"},
                    {"source": "2", "target": "1"}
                ]
            }
        }
        
        response = self.client.post("/api/v1/ai/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        print(f"\nAI 分析结果：{data['response']}")
    
    def test_multi_turn_conversation(self):
        """测试多轮对话"""
        messages = [
            {"role": "user", "content": "什么是与门 (AND Gate)？"},
            {"role": "assistant", "content": "与门是故障树中的逻辑门，表示所有输入事件同时发生时，输出事件才会发生。"},
            {"role": "user", "content": "那或门呢？"}
        ]
        
        request_data = {
            "messages": messages
        }
        
        response = self.client.post("/api/v1/ai/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        print(f"\n多轮对话回复：{data['response']}")
    
    def test_optimization_suggestion(self):
        """测试优化建议功能"""
        request_data = {
            "messages": [
                {
                    "role": "user",
                    "content": "我的故障树中有 5 个基本事件都直接连接到顶事件，这样设计合理吗？有什么优化建议？"
                }
            ],
            "context": {
                "nodes": [
                    {"id": "1", "type": "1", "label": "系统故障"},
                    {"id": "2", "type": "3", "label": "硬件故障"},
                    {"id": "3", "type": "3", "label": "软件故障"},
                    {"id": "4", "type": "3", "label": "人为错误"},
                    {"id": "5", "type": "3", "label": "环境因素"},
                    {"id": "6", "type": "3", "label": "网络攻击"}
                ],
                "edges": [
                    {"source": "2", "target": "1"},
                    {"source": "3", "target": "1"},
                    {"source": "4", "target": "1"},
                    {"source": "5", "target": "1"},
                    {"source": "6", "target": "1"}
                ]
            }
        }
        
        response = self.client.post("/api/v1/ai/chat", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        print(f"\n优化建议：{data['response']}")
    
    def test_invalid_request(self):
        """测试无效请求处理"""
        # 空消息列表
        request_data = {
            "messages": []
        }
        
        response = self.client.post("/api/v1/ai/chat", json=request_data)
        
        # 应该返回错误或默认回复，而不是崩溃
        assert response.status_code in [200, 400, 422]
        print(f"\n无效请求处理：{response.status_code}")
    
    def test_api_key_missing(self):
        """测试 API Key 缺失时的处理"""
        # 临时删除环境变量
        original_key = os.getenv("DASHSCOPE_API_KEY")
        if "DASHSCOPE_API_KEY" in os.environ:
            del os.environ["DASHSCOPE_API_KEY"]
        
        try:
            request_data = {
                "messages": [
                    {"role": "user", "content": "测试"}
                ]
            }
            
            response = self.client.post("/api/v1/ai/chat", json=request_data)
            
            # 应该有友好的错误提示
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            print(f"\nAPI Key 缺失时的回复：{data['response']}")
            
        finally:
            # 恢复环境变量
            if original_key:
                os.environ["DASHSCOPE_API_KEY"] = original_key


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
