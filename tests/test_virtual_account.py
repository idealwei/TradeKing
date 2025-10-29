"""Tests for virtual account functionality."""

import json
import tempfile
from pathlib import Path

import pytest

from trade_agent.virtual_account import Order, Position, VirtualAccount


class TestPosition:
    """Test Position class."""

    def test_create_position(self):
        """Test creating a position."""
        pos = Position(symbol="AAPL.US", quantity=100, cost_basis=150.0)
        assert pos.symbol == "AAPL.US"
        assert pos.quantity == 100
        assert pos.cost_basis == 150.0
        assert pos.total_cost() == 15000.0

    def test_position_serialization(self):
        """Test position to/from dict."""
        pos = Position(symbol="TSLA.US", quantity=50, cost_basis=200.0)
        data = pos.to_dict()
        assert data == {
            "symbol": "TSLA.US",
            "quantity": 50,
            "cost_basis": 200.0,
        }

        pos2 = Position.from_dict(data)
        assert pos2.symbol == pos.symbol
        assert pos2.quantity == pos.quantity
        assert pos2.cost_basis == pos.cost_basis


class TestOrder:
    """Test Order class."""

    def test_create_order(self):
        """Test creating an order."""
        order = Order(
            timestamp="2025-10-29T10:00:00",
            order_type="BUY",
            symbol="AAPL.US",
            quantity=100,
            price=150.0,
            total_amount=15000.0,
        )
        assert order.order_type == "BUY"
        assert order.symbol == "AAPL.US"
        assert order.status == "FILLED"

    def test_order_serialization(self):
        """Test order to/from dict."""
        order = Order(
            timestamp="2025-10-29T10:00:00",
            order_type="SELL",
            symbol="TSLA.US",
            quantity=50,
            price=200.0,
            total_amount=10000.0,
        )
        data = order.to_dict()
        order2 = Order.from_dict(data)
        assert order2.order_type == order.order_type
        assert order2.symbol == order.symbol
        assert order2.quantity == order.quantity


class TestVirtualAccount:
    """Test VirtualAccount class."""

    def test_create_account(self):
        """Test creating a new account."""
        account = VirtualAccount(initial_cash=100000.0)
        assert account.cash_balance == 100000.0
        assert account.initial_cash == 100000.0
        assert len(account.positions) == 0
        assert len(account.order_history) == 0

    def test_buy_stock(self):
        """Test buying stock."""
        account = VirtualAccount(initial_cash=100000.0)

        success, message = account.buy("AAPL.US", 100, 150.0)
        assert success is True
        assert "Bought" in message
        assert account.cash_balance == 85000.0  # 100000 - 15000
        assert "AAPL.US" in account.positions
        assert account.positions["AAPL.US"].quantity == 100
        assert len(account.order_history) == 1

    def test_buy_insufficient_funds(self):
        """Test buying with insufficient funds."""
        account = VirtualAccount(initial_cash=1000.0)

        success, message = account.buy("AAPL.US", 100, 150.0)
        assert success is False
        assert "Insufficient funds" in message
        assert account.cash_balance == 1000.0
        assert len(account.positions) == 0

    def test_buy_multiple_times_same_stock(self):
        """Test buying same stock multiple times."""
        account = VirtualAccount(initial_cash=100000.0)

        # First buy
        account.buy("AAPL.US", 100, 150.0)
        # Second buy at different price
        account.buy("AAPL.US", 50, 160.0)

        # Check average cost basis
        pos = account.positions["AAPL.US"]
        assert pos.quantity == 150
        # Average: (100*150 + 50*160) / 150 = 153.33...
        expected_cost = (100 * 150.0 + 50 * 160.0) / 150
        assert abs(pos.cost_basis - expected_cost) < 0.01

    def test_sell_stock(self):
        """Test selling stock."""
        account = VirtualAccount(initial_cash=100000.0)

        # Buy first
        account.buy("AAPL.US", 100, 150.0)
        # Sell some
        success, message = account.sell("AAPL.US", 50, 160.0)

        assert success is True
        assert "Sold" in message
        assert account.cash_balance == 85000.0 + 8000.0  # sold 50 at 160
        assert account.positions["AAPL.US"].quantity == 50

    def test_sell_entire_position(self):
        """Test selling entire position."""
        account = VirtualAccount(initial_cash=100000.0)

        account.buy("AAPL.US", 100, 150.0)
        success, message = account.sell("AAPL.US", 100, 160.0)

        assert success is True
        assert "AAPL.US" not in account.positions  # Position removed

    def test_sell_no_position(self):
        """Test selling stock we don't own."""
        account = VirtualAccount(initial_cash=100000.0)

        success, message = account.sell("AAPL.US", 100, 150.0)
        assert success is False
        assert "No position" in message

    def test_sell_insufficient_shares(self):
        """Test selling more shares than we own."""
        account = VirtualAccount(initial_cash=100000.0)

        account.buy("AAPL.US", 100, 150.0)
        success, message = account.sell("AAPL.US", 150, 160.0)

        assert success is False
        assert "Insufficient shares" in message
        assert account.positions["AAPL.US"].quantity == 100  # Unchanged

    def test_get_account_info(self):
        """Test getting account info."""
        account = VirtualAccount(initial_cash=100000.0)
        account.buy("AAPL.US", 100, 150.0)

        info = account.get_account_info()
        assert info["cash_balance"] == 85000.0
        assert info["initial_cash"] == 100000.0
        assert info["currency"] == "USD"

    def test_get_positions(self):
        """Test getting positions."""
        account = VirtualAccount(initial_cash=100000.0)
        account.buy("AAPL.US", 100, 150.0)
        account.buy("TSLA.US", 50, 200.0)

        positions = account.get_positions()
        assert len(positions) == 2

        symbols = [p["symbol"] for p in positions]
        assert "AAPL.US" in symbols
        assert "TSLA.US" in symbols

    def test_get_order_history(self):
        """Test getting order history."""
        account = VirtualAccount(initial_cash=100000.0)
        account.buy("AAPL.US", 100, 150.0)
        account.sell("AAPL.US", 50, 160.0)

        history = account.get_order_history()
        assert len(history) == 2
        # Most recent first
        assert history[0]["order_type"] == "SELL"
        assert history[1]["order_type"] == "BUY"

    def test_calculate_assets(self):
        """Test calculating total assets."""
        account = VirtualAccount(initial_cash=100000.0)
        account.buy("AAPL.US", 100, 150.0)  # Cost: 15000
        account.buy("TSLA.US", 50, 200.0)   # Cost: 10000
        # Cash left: 75000

        market_prices = {
            "AAPL.US": 160.0,  # Profit: 1000
            "TSLA.US": 180.0,  # Loss: -1000
        }

        assets = account.calculate_assets(market_prices)
        assert assets["cash"] == 75000.0
        assert assets["positions_value"] == 160.0 * 100 + 180.0 * 50  # 25000
        assert assets["total_assets"] == 100000.0  # 75000 + 25000
        assert assets["total_pnl"] == 0.0  # Break even
        assert len(assets["positions"]) == 2

    def test_save_and_load(self):
        """Test saving and loading account."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "account.json"

            # Create and populate account
            account1 = VirtualAccount(initial_cash=100000.0)
            account1.buy("AAPL.US", 100, 150.0)
            account1.sell("AAPL.US", 50, 160.0)

            # Save
            account1.save(file_path)
            assert file_path.exists()

            # Load
            account2 = VirtualAccount.load(file_path)
            assert account2.initial_cash == 100000.0
            assert account2.cash_balance == account1.cash_balance
            assert len(account2.positions) == 1
            assert account2.positions["AAPL.US"].quantity == 50
            assert len(account2.order_history) == 2

    def test_load_nonexistent_file(self):
        """Test loading from non-existent file creates new account."""
        account = VirtualAccount.load("/tmp/does_not_exist_12345.json")
        assert account.initial_cash == 100000.0
        assert account.cash_balance == 100000.0
        assert len(account.positions) == 0
