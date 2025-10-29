# TradeKing API 测试套件

完整的 API 端点测试套件，用于验证 TradeKing 交易系统的所有外部访问接口。

## 📁 目录结构

```
tests/
├── api/                    # API 端点测试
│   ├── test_health.py      # 健康检查接口测试
│   ├── test_decisions.py   # 交易决策接口测试
│   ├── test_models.py      # 模型性能接口测试
│   └── test_portfolio.py   # 投资组合接口测试
├── integration/            # 集成测试
│   └── test_full_workflow.py  # 完整工作流测试
├── fixtures/               # 测试数据和固件
│   └── sample_data.py      # 示例测试数据
├── conftest.py            # Pytest 配置和共享固件
└── test_utils.py          # 测试工具函数
```

## 🚀 快速开始

### 安装依赖

```bash
pip install pytest pytest-cov httpx
```

### 运行所有测试

```bash
# 运行所有测试
pytest tests/

# 运行并显示详细输出
pytest tests/ -v

# 运行并显示测试覆盖率
pytest tests/ --cov=backend --cov-report=html
```

### 运行特定测试

```bash
# 只运行 API 测试
pytest tests/api/

# 只运行健康检查测试
pytest tests/api/test_health.py

# 运行集成测试
pytest tests/integration/

# 运行特定测试类
pytest tests/api/test_decisions.py::TestDecisionsEndpoint

# 运行特定测试方法
pytest tests/api/test_health.py::TestHealthEndpoint::test_health_check_success
```

## 📊 测试覆盖的 API 端点

### 1. 健康检查 (Health Check)

| 端点 | 方法 | 描述 | 测试文件 |
|------|------|------|----------|
| `/api/health` | GET | 系统健康状态检查 | `test_health.py` |

**测试用例：**
- ✅ 健康检查成功返回
- ✅ 数据库连接状态验证
- ✅ 调度器状态验证
- ✅ 版本号验证

### 2. 交易决策 (Trading Decisions)

| 端点 | 方法 | 描述 | 测试文件 |
|------|------|------|----------|
| `/api/decisions/execute` | POST | 执行交易决策 | `test_decisions.py` |
| `/api/decisions/latest` | GET | 获取最新决策列表 | `test_decisions.py` |
| `/api/decisions/{id}` | GET | 获取决策详情 | `test_decisions.py` |
| `/api/decisions/` | GET | 按条件过滤决策 | `test_decisions.py` |

**测试用例：**
- ✅ 成功执行交易决策
- ✅ 不指定股票代码执行决策
- ✅ 无效模型选择错误处理
- ✅ 获取最新决策列表
- ✅ 自定义限制数量
- ✅ 获取决策详情（包含完整上下文）
- ✅ 决策不存在错误处理
- ✅ 按模型过滤决策
- ✅ 无效过滤条件错误处理

### 3. 模型性能 (Model Performance)

| 端点 | 方法 | 描述 | 测试文件 |
|------|------|------|----------|
| `/api/models/performance` | GET | 获取所有模型性能 | `test_models.py` |
| `/api/models/performance/{model}` | GET | 获取特定模型性能 | `test_models.py` |

**测试用例：**
- ✅ 获取所有模型性能指标
- ✅ 获取特定模型性能
- ✅ 无效模型错误处理
- ✅ 无数据模型处理
- ✅ 性能指标计算准确性验证

### 4. 投资组合 (Portfolio)

| 端点 | 方法 | 描述 | 测试文件 |
|------|------|------|----------|
| `/api/portfolio/latest` | GET | 获取最新投资组合快照 | `test_portfolio.py` |
| `/api/portfolio/equity-curve` | GET | 获取权益曲线数据 | `test_portfolio.py` |

**测试用例：**
- ✅ 获取最新投资组合快照
- ✅ 按模型过滤快照
- ✅ 无快照数据错误处理
- ✅ 无效模型错误处理
- ✅ 获取权益曲线数据
- ✅ 自定义数据点数量
- ✅ 缺少必需参数错误处理

## 🔧 测试配置

### 环境变量

测试使用内存数据库和模拟环境变量：

```python
# 自动配置的环境变量（在 conftest.py 中）
OPENAI_API_KEY=test-api-key
TRADE_AGENT_MODEL=gpt5
SCHEDULER_ENABLED=false
DATABASE_URL=sqlite:///:memory:
```

### 测试固件 (Fixtures)

#### `test_db`
提供每个测试的独立数据库会话。

```python
def test_example(test_db):
    # 使用 test_db 进行数据库操作
    ...
```

#### `client`
提供配置好的 FastAPI 测试客户端。

```python
def test_api_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
```

#### `mock_env`
提供模拟的环境变量配置。

```python
def test_with_env(client, mock_env):
    # 环境变量已配置
    ...
```

## 📝 编写新测试

### 测试模板

```python
import pytest
from fastapi.testclient import TestClient

class TestNewEndpoint:
    """测试新端点的测试类"""

    def test_endpoint_success(self, client: TestClient):
        """测试成功场景"""
        response = client.get("/api/new-endpoint")

        assert response.status_code == 200
        data = response.json()
        assert "expected_field" in data

    def test_endpoint_error(self, client: TestClient):
        """测试错误处理"""
        response = client.get("/api/new-endpoint?invalid=param")

        assert response.status_code == 400
        assert "error" in response.json()["detail"].lower()
```

### Mock Agent 示例

```python
from unittest.mock import Mock, patch

@patch("backend.routers.decisions.create_agent")
def test_with_mock_agent(mock_create_agent, client, mock_env):
    """使用模拟 Agent 的测试"""
    # 设置 mock
    mock_agent = Mock()
    mock_agent.run.return_value = {
        "decision": "Test decision",
        "account_data": "{}",
        # ... 其他字段
    }
    mock_create_agent.return_value = mock_agent

    # 执行测试
    response = client.post("/api/decisions/execute", json={})
    assert response.status_code == 200
```

## 🎯 测试最佳实践

1. **每个测试独立**：不依赖其他测试的状态
2. **清晰命名**：测试名称应描述测试内容
3. **使用 Mock**：对外部服务和 Agent 使用 Mock
4. **验证结构**：检查响应数据结构和类型
5. **测试边界**：包含正常和异常情况
6. **使用固件**：复用常见的测试设置

## 📈 持续集成

将测试集成到 CI/CD 流程：

```yaml
# .github/workflows/tests.yml 示例
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
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov=backend --cov-report=xml
```

## 🐛 调试测试

```bash
# 显示打印输出
pytest tests/ -s

# 在第一个失败处停止
pytest tests/ -x

# 显示最慢的 10 个测试
pytest tests/ --durations=10

# 运行特定标记的测试
pytest tests/ -m "slow"
```

## 📚 相关文档

- [Pytest 文档](https://docs.pytest.org/)
- [FastAPI 测试](https://fastapi.tiangolo.com/tutorial/testing/)
- [TradeKing API 文档](../README.md)

## 💡 常见问题

### Q: 如何测试需要认证的端点？
A: 在 `conftest.py` 中添加认证 fixture，或在测试中添加认证头。

### Q: 如何测试异步端点？
A: 使用 `pytest-asyncio` 插件和 `@pytest.mark.asyncio` 装饰器。

### Q: 数据库测试数据如何清理？
A: `test_db` fixture 会在每个测试后自动回滚，无需手动清理。

## 🤝 贡献

添加新的 API 端点时，请：
1. 在相应的测试文件中添加测试
2. 更新此 README 文档
3. 确保所有测试通过
4. 保持测试覆盖率 > 80%
