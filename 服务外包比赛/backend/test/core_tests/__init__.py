"""
核心功能测试模块
用于测试核心配置和功能
"""

import os
import sys
import pytest

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.config import Settings


class TestConfig:
    """配置测试类"""
    
    def test_settings_initialization(self):
        """测试 Settings 初始化"""
        settings = Settings()
        
        assert settings.NEO4J_URI is not None
        print(f"\nNeo4j URI: {settings.NEO4J_URI}")
        print(f"Model Name: {settings.MODEL_NAME}")
        print("\nSettings 初始化测试通过")
    
    def test_env_variables(self):
        """测试环境变量加载"""
        api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if api_key:
            print(f"\nAPI Key 已配置：{api_key[:10]}...")
        else:
            print("\n警告：API Key 未配置")
        
        print("\n环境变量测试完成")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
