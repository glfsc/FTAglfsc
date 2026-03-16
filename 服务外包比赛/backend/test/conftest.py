"""
测试工具函数
提供通用的测试辅助功能
"""

import os
import sys
from typing import Any, Dict, List


def add_project_to_path():
    """将项目根目录添加到 Python 路径"""
    # 获取 test 目录的父目录（即 backend 目录）
    test_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(test_dir)
    
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    return backend_dir


def load_env_variables(env_file: str = ".env"):
    """加载环境变量"""
    from dotenv import load_dotenv
    
    backend_dir = add_project_to_path()
    env_path = os.path.join(backend_dir, env_file)
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✓ 已加载环境变量：{env_path}")
    else:
        print(f"⚠ 环境变量文件不存在：{env_path}")


def create_mock_triplet(
    subject_name: str = "测试故障",
    subject_type: str = "BasicEvent",
    relation: str = "resultsIn",
    object_name: str = "系统故障",
    object_type: str = "TopEvent",
    confidence: float = 0.95,
    source: str = "测试文档"
) -> Dict[str, Any]:
    """创建模拟三元组数据"""
    return {
        "subject_name": subject_name,
        "subject_type": subject_type,
        "relation": relation,
        "object_name": object_name,
        "object_type": object_type,
        "confidence": confidence,
        "source": source
    }


def create_mock_fault_tree_context(
    node_count: int = 3,
    include_edges: bool = True
) -> Dict[str, List[Dict]]:
    """创建模拟故障树上下文"""
    nodes = [
        {"id": "1", "type": "1", "label": "系统故障"},
        {"id": "2", "type": "2", "label": "中间故障"},
        {"id": "3", "type": "3", "label": "基本故障"}
    ][:node_count]
    
    edges = []
    if include_edges and node_count >= 2:
        for i in range(node_count - 1):
            edges.append({
                "source": str(i + 2),
                "target": str(i + 1)
            })
    
    return {
        "nodes": nodes,
        "edges": edges
    }


def print_test_header(test_name: str, description: str = ""):
    """打印测试标题"""
    print("\n" + "=" * 60)
    print(f"测试：{test_name}")
    if description:
        print(f"说明：{description}")
    print("=" * 60)


def print_test_result(success: bool, message: str = ""):
    """打印测试结果"""
    if success:
        print(f"✓ 测试通过：{message}")
    else:
        print(f"✗ 测试失败：{message}")


class MockResponse:
    """模拟 HTTP 响应"""
    
    def __init__(self, status_code: int, data: Any = None):
        self.status_code = status_code
        self.data = data
    
    def json(self):
        return self.data
    
    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            raise Exception(f"HTTP Error: {self.status_code}")
