# 测试模块使用说明

## 目录结构

```
backend/test/
├── __init__.py              # 测试包初始化
├── conftest.py              # pytest 配置和共享工具函数
├── api_tests/               # API接口测试
│   ├── __init__.py
│   ├── test_ai_chat.py      # AI 聊天 API 测试
│   └── test_fault_tree.py   # 故障树 API 测试
├── service_tests/           # 服务层测试
│   ├── __init__.py
│   └── test_knowledge_extraction.py  # 知识抽取服务测试
├── model_tests/             # 数据模型测试
│   ├── __init__.py
│   └── test_schemas.py      # Schema 验证测试
├── core_tests/              # 核心功能测试
│   └── __init__.py
└── integration_tests/       # 集成测试
    └── __init__.py
```

## 快速开始

### 1. 安装测试依赖

```bash
cd backend
pip install -r requirements-test.txt
```

### 2. 运行测试

#### 运行所有测试
```bash
pytest
```

#### 运行特定模块测试
```bash
# API 测试
pytest test/api_tests/

# 服务层测试
pytest test/service_tests/

# 模型测试
pytest test/model_tests/
```

#### 运行单个测试文件
```bash
pytest test/api_tests/test_ai_chat.py -v
```

#### 运行单个测试方法
```bash
pytest test/api_tests/test_ai_chat.py::TestAIChatAPI::test_basic_chat -v
```

### 3. 使用覆盖率报告

```bash
# 生成 HTML 覆盖率报告
pytest --cov=app --cov-report=html

# 在浏览器中查看报告
open htmlcov/index.html  # macOS/Linux
start htmlcov\index.html  # Windows
```

### 4. 使用标记筛选测试

```bash
# 只运行 API 测试
pytest -m api

# 只运行集成测试
pytest -m integration

# 排除慢速测试
pytest -m "not slow"
```

## 编写测试的最佳实践

### 1. 测试命名规范
- 测试文件：`test_<module>.py`
- 测试类：`Test<Module>`
- 测试方法：`test_<feature>_<scenario>`

### 2. 使用夹具 (Fixtures)
```python
@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"
```

### 3. 参数化测试
```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected
```

### 4. Mock 外部依赖
```python
from unittest.mock import patch

@patch('module.external_api_call')
def test_with_mock(mock_api):
    mock_api.return_value = {"result": "success"}
    # 测试逻辑
```

## 常用测试场景示例

### API 测试示例
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_api_endpoint():
    response = client.post("/api/v1/endpoint", json={"data": "test"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

### 服务层测试示例
```python
from app.services.my_service import MyService

def test_service_method():
    service = MyService()
    result = service.process_data("input")
    assert result == "expected_output"
```

### 模型验证测试
```python
from pydantic import ValidationError
from app.models.schemas import MyModel

def test_model_validation():
    model = MyModel(field="value")
    assert model.field == "value"

def test_invalid_model():
    with pytest.raises(ValidationError):
        MyModel()  # 缺少必填字段
```

## 调试技巧

### 1. 打印输出
```bash
# 显示 print 输出
pytest -s

# 详细输出
pytest -vv
```

### 2. 失败后进入调试器
```bash
pytest --pdb
```

### 3. 逐步调试
```bash
pytest --pdb -s test/api_tests/test_ai_chat.py::TestAIChatAPI::test_basic_chat
```

## 持续集成

### GitHub Actions 示例
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
```

## 注意事项

1. **环境变量**: 确保 `.env` 文件配置正确
2. **数据库连接**: 部分测试需要 Neo4j 数据库运行
3. **API Key**: AI 相关测试需要配置 DASHSCOPE_API_KEY
4. **测试隔离**: 每个测试应该独立，不依赖其他测试的状态
5. **清理资源**: 使用 `teardown` 或 `yield fixture` 清理测试资源

## 常见问题

### Q: 测试失败提示 ImportError？
A: 确保已运行 `add_project_to_path()` 或在项目根目录运行 pytest

### Q: 如何跳过某些测试？
A: 使用 `@pytest.mark.skip` 装饰器

### Q: 如何测试异步代码？
A: 使用 `pytest-asyncio` 和 `@pytest.mark.asyncio` 装饰器

## 扩展测试

添加新的测试模块时，请遵循以下结构：

1. 在对应目录下创建 `test_<module>.py` 文件
2. 导入必要的依赖和工具函数
3. 创建测试类和方法
4. 使用断言验证结果
5. 运行测试并查看报告

祝测试愉快！🧪
