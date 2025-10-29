# Virtual Account System

## 概述

TradeKing 使用虚拟账户系统来模拟交易。系统的核心设计如下：

- **市场数据**：从长桥 API 获取实时股价
- **账户数据**：本地维护虚拟账户（余额、持仓、订单历史）
- **交易模拟**：在虚拟账户中模拟买入/卖出操作
- **数据持久化**：账户状态保存到 JSON 文件

## 架构

```
┌─────────────────┐
│   TradingAgent  │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
┌────────▼────────┐  ┌─────▼──────────────┐
│ TradingData     │  │ VirtualAccount     │
│ Fetcher         │  │                    │
│                 │  │ - Cash Balance     │
│ - Market Data ──┼──│ - Positions        │
│   (Longbridge)  │  │ - Order History    │
└─────────────────┘  │ - Buy/Sell Methods │
                     └────────────────────┘
                              │
                              │ Save/Load
                              ▼
                     ┌────────────────────┐
                     │ virtual_account.   │
                     │ json               │
                     └────────────────────┘
```

## 核心组件

### 1. VirtualAccount (虚拟账户)

管理模拟交易账户的状态。

**主要属性：**
- `initial_cash`: 初始资金（默认 $100,000）
- `cash_balance`: 当前现金余额
- `positions`: 持仓字典 {symbol: Position}
- `order_history`: 订单历史列表

**主要方法：**

```python
from trade_agent import VirtualAccount

# 创建新账户
account = VirtualAccount(initial_cash=100000.0)

# 买入股票
success, message = account.buy("AAPL.US", quantity=100, price=150.0)
# 返回: (True, "Bought 100 shares of AAPL.US at $150.00")

# 卖出股票
success, message = account.sell("AAPL.US", quantity=50, price=160.0)
# 返回: (True, "Sold 50 shares of AAPL.US at $160.00")

# 查询账户信息
account_info = account.get_account_info()
# {"cash_balance": 85000.0, "initial_cash": 100000.0, "currency": "USD"}

# 查询持仓
positions = account.get_positions()
# [{"symbol": "AAPL.US", "quantity": 50, "cost_basis": 150.0, "total_cost": 7500.0}]

# 查询订单历史
orders = account.get_order_history(limit=10)

# 计算总资产（需要当前市场价格）
market_prices = {"AAPL.US": 160.0}
assets = account.calculate_assets(market_prices)
# {
#   "cash": 85000.0,
#   "positions_value": 8000.0,
#   "total_assets": 93000.0,
#   "total_pnl": -7000.0,
#   "positions": [...]
# }

# 保存账户状态
account.save("storage/virtual_account.json")

# 加载账户状态
account = VirtualAccount.load("storage/virtual_account.json")
```

### 2. TradingDataFetcher (数据获取器)

现在只从长桥 API 获取市场数据，其他数据从虚拟账户获取。

**修改前（错误）：**
```python
# ❌ 尝试从长桥获取所有数据（会报错）
account_data = client.get_account_overview()
positions_data = client.get_positions()
orders_data = client.get_order_history()
```

**修改后（正确）：**
```python
# ✅ 只从长桥获取市场数据
market_data = client.get_market_snapshot(symbols)

# ✅ 从虚拟账户获取其他数据
account_data = virtual_account.get_account_info()
positions_data = virtual_account.get_positions()
orders_data = virtual_account.get_order_history()
assets_data = virtual_account.calculate_assets(market_prices)
```

### 3. TradeExecutor (交易执行器)

解析 AI 决策并执行虚拟交易。

**支持的格式：**

1. **JSON 格式：**
```json
{"action": "BUY", "symbol": "AAPL.US", "quantity": 100, "price": 150.0}
```

2. **JSON 数组：**
```json
[
  {"action": "BUY", "symbol": "AAPL.US", "quantity": 100},
  {"action": "SELL", "symbol": "TSLA.US", "quantity": 50}
]
```

3. **自然语言：**
```
BUY 100 shares of AAPL at $150.00
SELL 50 TSLA at 200.00
```

**使用示例：**

```python
from trade_agent import TradeExecutor, VirtualAccount

account = VirtualAccount(initial_cash=100000.0)
executor = TradeExecutor(account)

market_prices = {"AAPL.US": 150.0, "TSLA.US": 200.0}

# AI 决策文本
decision = '''
Based on my analysis, I recommend:
{"action": "BUY", "symbol": "AAPL.US", "quantity": 100}
'''

# 解析并执行
results = executor.parse_and_execute(decision, market_prices)

for result in results:
    if result["success"]:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ {result['message']}")
```

## 使用流程

### 完整示例

```python
from trade_agent import create_agent

# 1. 创建 Agent（会自动加载或创建虚拟账户）
agent = create_agent()

# 2. 运行 Agent（获取市场数据 + 虚拟账户数据 + AI 决策）
result = agent.run(initial_state={"symbols": ["AAPL.US", "TSLA.US"]})

# 3. 查看 AI 决策
print(result["decision"])

# 4. （可选）手动执行交易
from trade_agent import TradeExecutor

executor = TradeExecutor(agent.virtual_account)
market_prices = {"AAPL.US": 150.0}
executor.parse_and_execute(result["decision"], market_prices)

# 5. 账户状态会自动保存到 storage/virtual_account.json
```

### 数据持久化

虚拟账户数据保存格式（JSON）：

```json
{
  "initial_cash": 100000.0,
  "cash_balance": 85000.0,
  "positions": {
    "AAPL.US": {
      "symbol": "AAPL.US",
      "quantity": 100,
      "cost_basis": 150.0
    }
  },
  "order_history": [
    {
      "timestamp": "2025-10-29T10:00:00",
      "order_type": "BUY",
      "symbol": "AAPL.US",
      "quantity": 100,
      "price": 150.0,
      "total_amount": 15000.0,
      "status": "FILLED"
    }
  ]
}
```

## 配置

虚拟账户文件默认保存在 `storage/virtual_account.json`。

可以自定义路径：

```python
from trade_agent import create_agent

agent = create_agent(account_file="my_custom_account.json")
```

## 重置账户

如果想重置虚拟账户，删除账户文件即可：

```bash
rm storage/virtual_account.json
```

下次运行时会创建新的账户（初始资金 $100,000）。

## 注意事项

1. **长桥 API 用途**：仅用于获取实时市场数据（股价）
2. **虚拟账户**：所有账户、持仓、订单数据都在本地维护
3. **数据同步**：每次 Agent 运行后自动保存账户状态
4. **价格更新**：使用最新市场价格计算资产价值
5. **成本基础**：多次买入同一股票会计算平均成本

## 测试

运行测试验证功能：

```bash
# 测试虚拟账户
python -m pytest tests/test_virtual_account.py -v

# 测试交易执行器
python -m pytest tests/test_trade_executor.py -v
```

## 常见问题

**Q: 为什么要使用虚拟账户而不是直接从长桥获取？**

A: 长桥 API 主要提供市场数据服务。在模拟交易场景下，账户、持仓等信息需要本地维护。这样可以：
- 避免调用不存在的 API 端点
- 完全控制交易模拟逻辑
- 支持离线测试和开发
- 降低 API 调用成本

**Q: 如何查看当前账户状态？**

A: 直接查看 `storage/virtual_account.json` 文件，或者：

```python
from trade_agent import VirtualAccount

account = VirtualAccount.load("storage/virtual_account.json")
print(f"Cash: ${account.cash_balance:.2f}")
print(f"Positions: {len(account.positions)}")
print(f"Orders: {len(account.order_history)}")
```

**Q: 多次买入同一股票如何计算成本？**

A: 使用加权平均成本基础。例如：
- 第一次买入 100 股 @ $150 = $15,000
- 第二次买入 50 股 @ $160 = $8,000
- 平均成本 = $23,000 / 150 = $153.33/股

**Q: 如何初始化特定金额的账户？**

A: 修改代码或直接编辑 JSON 文件：

```python
account = VirtualAccount(initial_cash=1000000.0)  # $1M
account.save("storage/virtual_account.json")
```
