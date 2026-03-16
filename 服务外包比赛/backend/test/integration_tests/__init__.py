"""
集成测试模块
用于测试多个模块的协同工作
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from main import app


class TestIntegration:
    """集成测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.client = TestClient(app)
    
    def test_complete_workflow(self):
        """测试完整工作流程"""
        print("\n=== 完整工作流程测试 ===")
        
        # 1. 上传知识三元组
        print("\n1. 上传知识三元组...")
        upload_data = {
            "triplets": [
                {
                    "subject_name": "电池老化",
                    "subject_type": "BasicEvent",
                    "relation": "resultsIn",
                    "object_name": "电源故障",
                    "object_type": "IntermediateEvent",
                    "confidence": 0.95,
                    "source": "测试文档"
                },
                {
                    "subject_name": "电源故障",
                    "subject_type": "IntermediateEvent",
                    "relation": "resultsIn",
                    "object_name": "系统故障",
                    "object_type": "TopEvent",
                    "confidence": 0.98,
                    "source": "测试文档"
                }
            ]
        }
        
        upload_response = self.client.post("/api/v1/fault-tree/upload_knowledge", json=upload_data)
        print(f"   上传状态码：{upload_response.status_code}")
        if upload_response.status_code == 200:
            print(f"   响应：{upload_response.json()}")
        
        # 2. 生成故障树
        print("\n2. 生成故障树...")
        generate_response = self.client.get(
            "/api/v1/fault-tree/generate_tree",
            params={"top_event": "系统故障", "export": False}
        )
        print(f"   生成状态码：{generate_response.status_code}")
        if generate_response.status_code == 200:
            data = generate_response.json()
            print(f"   节点数：{len(data.get('data', {}).get('nodeList', []))}")
            print(f"   边数：{len(data.get('data', {}).get('linkList', []))}")
        
        # 3. AI 分析
        print("\n3. AI 分析...")
        chat_response = self.client.post(
            "/api/v1/ai/chat",
            json={
                "messages": [
                    {"role": "user", "content": "请分析这个故障树的逻辑结构"}
                ],
                "context": {
                    "nodes": [
                        {"id": "1", "type": "1", "label": "系统故障"},
                        {"id": "2", "type": "2", "label": "电源故障"},
                        {"id": "3", "type": "3", "label": "电池老化"}
                    ],
                    "edges": [
                        {"source": "3", "target": "2"},
                        {"source": "2", "target": "1"}
                    ]
                }
            }
        )
        print(f"   AI 响应状态码：{chat_response.status_code}")
        if chat_response.status_code == 200:
            data = chat_response.json()
            print(f"   AI 回复：{data['response'][:100]}...")
        
        print("\n=== 工作流程测试完成 ===")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
