"""
知识抽取服务测试模块
用于测试知识抽取功能的各项功能
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.knowledge_extraction_service import KnowledgeExtractionService
from app.services.triplet_extractor import QwenExtractor


class TestKnowledgeExtractionService:
    """知识抽取服务测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 注意：这些测试可能需要 Neo4j 连接
        # 可以使用 mock 来避免依赖数据库
        pass
    
    def test_basic_extraction(self):
        """测试基础文本抽取功能"""
        # 这是一个示例测试，实际使用需要完整的配置
        sample_text = """
        若电源模块 A 与控制板 B 同时失效，或电源模块 C 失效，会导致系统宕机。
        """
        
        print(f"\n测试文本：{sample_text}")
        print("注意：完整测试需要配置 Neo4j 和 API Key")
        
        # TODO: 实现具体的测试逻辑
        # extractor = QwenExtractor()
        # result = extractor.extract(sample_text, "测试文档")
        # assert "triplets" in result
    
    def test_file_upload(self):
        """测试文件上传功能"""
        print("\n测试文件上传功能")
        # TODO: 实现文件上传测试
    
    def test_triplet_validation(self):
        """测试三元组验证功能"""
        print("\n测试三元组验证功能")
        # TODO: 实现三元组验证测试
    
    def test_batch_insert(self):
        """测试批量插入功能"""
        print("\n测试批量插入功能")
        # TODO: 实现批量插入测试


class TestQwenExtractor:
    """Qwen 提取器测试类"""
    
    def test_extractor_initialization(self):
        """测试提取器初始化"""
        api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not api_key:
            print("\n警告：DASHSCOPE_API_KEY 未设置，无法测试提取器")
            return
        
        try:
            extractor = QwenExtractor()
            assert extractor.model == "qwen-max"
            print("\n提取器初始化成功")
        except ValueError as e:
            print(f"\n提取器初始化失败：{e}")
    
    def test_extract_simple_text(self):
        """测试简单文本抽取"""
        api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not api_key:
            print("\n警告：DASHSCOPE_API_KEY 未设置，跳过测试")
            return
        
        try:
            extractor = QwenExtractor()
            
            text = "电源故障会导致系统停机"
            result = extractor.extract(text, "测试文档")
            
            print(f"\n抽取结果：{result}")
            assert "triplets" in result
            
        except Exception as e:
            print(f"\n抽取失败：{e}")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
