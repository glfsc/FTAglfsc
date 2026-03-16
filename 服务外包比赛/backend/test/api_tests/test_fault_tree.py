"""
故障树 API 测试模块
用于测试故障树生成、导出等功能
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from main import app


class TestFaultTreeAPI:
    """故障树 API 测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.client = TestClient(app)
        
    def test_upload_knowledge(self):
        """测试上传知识三元组"""
        request_data = {
            "triplets": [
                {
                    "subject_name": "电源故障",
                    "subject_type": "BasicEvent",
                    "relation": "resultsIn",
                    "object_name": "系统故障",
                    "object_type": "TopEvent",
                    "confidence": 0.95,
                    "source": "测试文档"
                }
            ]
        }
        
        response = self.client.post("/api/v1/fault-tree/upload_knowledge", json=request_data)
        
        print(f"\n上传知识三元组状态码：{response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应：{data}")
    
    def test_generate_tree(self):
        """测试生成故障树"""
        params = {
            "top_event": "系统故障",
            "export": False
        }
        
        response = self.client.get("/api/v1/fault-tree/generate_tree", params=params)
        
        print(f"\n生成故障树状态码：{response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"节点数：{len(data.get('data', {}).get('nodeList', []))}")
            print(f"边数：{len(data.get('data', {}).get('linkList', []))}")
        elif response.status_code == 404:
            print("顶事件不存在，这是正常的（如果数据库中没有数据）")
    
    def test_download_fault_tree(self):
        """测试下载故障树文件"""
        # 这个测试需要先有生成的文件
        filename = "fault_tree_测试.json"
        
        response = self.client.get(f"/api/v1/fault-tree/download/{filename}")
        
        print(f"\n下载故障树文件状态码：{response.status_code}")
        if response.status_code == 404:
            print("文件不存在（正常，需要先生成）")
    
    def test_generate_and_download(self):
        """测试生成并下载故障树"""
        params = {
            "top_event": "系统故障"
        }
        
        response = self.client.get("/api/v1/fault-tree/generate_and_download", params=params)
        
        print(f"\n生成并下载故障树状态码：{response.status_code}")
        if response.status_code == 200:
            print("文件生成成功")
        elif response.status_code == 404:
            print("顶事件不存在")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
