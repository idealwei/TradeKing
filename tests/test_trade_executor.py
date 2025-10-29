"""Tests for trade executor functionality."""

import json

import pytest

from trade_agent.trade_executor import TradeExecutor
from trade_agent.virtual_account import VirtualAccount


class TestTradeExecutor:
    """Test TradeExecutor class."""

    def test_execute_buy_trade(self):
        """Test executing a buy trade."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        market_prices = {"AAPL.US": 150.0}
        trade = {
            "action": "BUY",
            "symbol": "AAPL.US",
            "quantity": 100,
            "price": 150.0,
        }

        result = executor._execute_trade(trade, market_prices)
        assert result["success"] is True
        assert "Bought" in result["message"]
        assert account.cash_balance == 85000.0

    def test_execute_sell_trade(self):
        """Test executing a sell trade."""
        account = VirtualAccount(initial_cash=100000.0)
        account.buy("AAPL.US", 100, 150.0)

        executor = TradeExecutor(account)
        market_prices = {"AAPL.US": 160.0}
        trade = {
            "action": "SELL",
            "symbol": "AAPL.US",
            "quantity": 50,
            "price": 160.0,
        }

        result = executor._execute_trade(trade, market_prices)
        assert result["success"] is True
        assert "Sold" in result["message"]

    def test_execute_trade_with_market_price(self):
        """Test executing trade using market price."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        market_prices = {"AAPL.US": 150.0}
        trade = {
            "action": "BUY",
            "symbol": "AAPL.US",
            "quantity": 100,
            # No price specified, should use market price
        }

        result = executor._execute_trade(trade, market_prices)
        assert result["success"] is True
        assert result["trade"]["price"] == 150.0

    def test_execute_invalid_action(self):
        """Test executing trade with invalid action."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        trade = {
            "action": "HOLD",
            "symbol": "AAPL.US",
            "quantity": 100,
        }

        result = executor._execute_trade(trade, {})
        assert result["success"] is False
        assert "Invalid action" in result["message"]

    def test_execute_missing_symbol(self):
        """Test executing trade without symbol."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        trade = {
            "action": "BUY",
            "quantity": 100,
        }

        result = executor._execute_trade(trade, {})
        assert result["success"] is False
        assert "Symbol is required" in result["message"]

    def test_execute_no_market_price(self):
        """Test executing trade when market price unavailable."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        trade = {
            "action": "BUY",
            "symbol": "UNKNOWN.US",
            "quantity": 100,
        }

        result = executor._execute_trade(trade, {})
        assert result["success"] is False
        assert "No price available" in result["message"]

    def test_parse_json_trades(self):
        """Test parsing JSON formatted trades."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        decision = '''
        Based on analysis, I recommend:
        {"action": "BUY", "symbol": "AAPL.US", "quantity": 100, "price": 150.0}
        '''

        trades = executor._extract_json_trades(decision)
        assert len(trades) == 1
        assert trades[0]["action"] == "BUY"
        assert trades[0]["symbol"] == "AAPL.US"

    def test_parse_json_array_trades(self):
        """Test parsing JSON array of trades."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        decision = '''
        [
            {"action": "BUY", "symbol": "AAPL.US", "quantity": 100},
            {"action": "BUY", "symbol": "TSLA.US", "quantity": 50}
        ]
        '''

        trades = executor._extract_json_trades(decision)
        assert len(trades) == 2

    def test_parse_natural_language_buy(self):
        """Test parsing natural language buy decision."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        decision = "I recommend to BUY 100 shares of AAPL at $150.00"

        trades = executor._parse_natural_language(decision)
        assert len(trades) >= 1
        trade = trades[0]
        assert trade["action"] == "BUY"
        assert trade["symbol"] == "AAPL"
        assert trade["quantity"] == 100

    def test_parse_natural_language_sell(self):
        """Test parsing natural language sell decision."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        decision = "SELL 50 TSLA at 200.00"

        trades = executor._parse_natural_language(decision)
        assert len(trades) >= 1
        trade = trades[0]
        assert trade["action"] == "SELL"
        assert trade["quantity"] == 50

    def test_parse_and_execute(self):
        """Test full parse and execute flow."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        market_prices = {"AAPL.US": 150.0}
        decision = '{"action": "BUY", "symbol": "AAPL.US", "quantity": 100}'

        results = executor.parse_and_execute(decision, market_prices)
        assert len(results) == 1
        assert results[0]["success"] is True
        assert account.cash_balance == 85000.0

    def test_execute_trades_from_json_string(self):
        """Test executing trades from JSON string."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        market_prices = {"AAPL.US": 150.0}
        trades_json = json.dumps([
            {"action": "BUY", "symbol": "AAPL.US", "quantity": 100, "price": 150.0}
        ])

        results = executor.execute_trades_from_json(trades_json, market_prices)
        assert len(results) == 1
        assert results[0]["success"] is True

    def test_execute_trades_from_list(self):
        """Test executing trades from list."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        market_prices = {"AAPL.US": 150.0, "TSLA.US": 200.0}
        trades = [
            {"action": "BUY", "symbol": "AAPL.US", "quantity": 100},
            {"action": "BUY", "symbol": "TSLA.US", "quantity": 50},
        ]

        results = executor.execute_trades_from_json(trades, market_prices)
        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[1]["success"] is True
        assert len(account.positions) == 2

    def test_execute_multiple_trades_some_fail(self):
        """Test executing multiple trades where some fail."""
        account = VirtualAccount(initial_cash=100000.0)
        executor = TradeExecutor(account)

        market_prices = {"AAPL.US": 150.0}
        trades = [
            {"action": "BUY", "symbol": "AAPL.US", "quantity": 100},
            {"action": "SELL", "symbol": "TSLA.US", "quantity": 50},  # Will fail - no position
        ]

        results = executor.execute_trades_from_json(trades, market_prices)
        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[1]["success"] is False
