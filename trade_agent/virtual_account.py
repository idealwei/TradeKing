"""Virtual trading account for simulation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Position:
    """A stock position in the virtual account."""

    symbol: str
    quantity: int  # Number of shares
    cost_basis: float  # Average cost per share

    def total_cost(self) -> float:
        """Calculate total cost of this position."""
        return self.quantity * self.cost_basis

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "cost_basis": self.cost_basis,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Position:
        """Create from dictionary."""
        return cls(
            symbol=data["symbol"],
            quantity=data["quantity"],
            cost_basis=data["cost_basis"],
        )


@dataclass
class Order:
    """A trading order record."""

    timestamp: str
    order_type: str  # "BUY" or "SELL"
    symbol: str
    quantity: int
    price: float
    total_amount: float
    status: str = "FILLED"  # For simulation, all orders are immediately filled

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp,
            "order_type": self.order_type,
            "symbol": self.symbol,
            "quantity": self.quantity,
            "price": self.price,
            "total_amount": self.total_amount,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Order:
        """Create from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            order_type=data["order_type"],
            symbol=data["symbol"],
            quantity=data["quantity"],
            price=data["price"],
            total_amount=data["total_amount"],
            status=data.get("status", "FILLED"),
        )


@dataclass
class VirtualAccount:
    """Virtual trading account for simulation."""

    initial_cash: float = 100000.0  # Starting cash in USD
    cash_balance: float = field(default=0.0)  # Current cash balance
    positions: Dict[str, Position] = field(default_factory=dict)  # symbol -> Position
    order_history: List[Order] = field(default_factory=list)  # All historical orders

    def __post_init__(self):
        """Initialize cash balance if not set."""
        if self.cash_balance == 0.0:
            self.cash_balance = self.initial_cash

    def buy(self, symbol: str, quantity: int, price: float) -> tuple[bool, str]:
        """
        Execute a buy order.

        Args:
            symbol: Stock symbol (e.g., "AAPL.US")
            quantity: Number of shares to buy
            price: Price per share

        Returns:
            (success, message) tuple
        """
        total_cost = quantity * price

        # Check if we have enough cash
        if total_cost > self.cash_balance:
            return False, f"Insufficient funds. Need ${total_cost:.2f}, have ${self.cash_balance:.2f}"

        # Update cash balance
        self.cash_balance -= total_cost

        # Update or create position
        if symbol in self.positions:
            existing = self.positions[symbol]
            # Calculate new average cost
            total_quantity = existing.quantity + quantity
            total_value = existing.total_cost() + total_cost
            new_cost_basis = total_value / total_quantity

            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=total_quantity,
                cost_basis=new_cost_basis,
            )
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                cost_basis=price,
            )

        # Record order
        order = Order(
            timestamp=datetime.now().isoformat(),
            order_type="BUY",
            symbol=symbol,
            quantity=quantity,
            price=price,
            total_amount=total_cost,
        )
        self.order_history.append(order)

        return True, f"Bought {quantity} shares of {symbol} at ${price:.2f}"

    def sell(self, symbol: str, quantity: int, price: float) -> tuple[bool, str]:
        """
        Execute a sell order.

        Args:
            symbol: Stock symbol
            quantity: Number of shares to sell
            price: Price per share

        Returns:
            (success, message) tuple
        """
        # Check if we have the position
        if symbol not in self.positions:
            return False, f"No position in {symbol}"

        position = self.positions[symbol]

        # Check if we have enough shares
        if quantity > position.quantity:
            return False, f"Insufficient shares. Have {position.quantity}, trying to sell {quantity}"

        # Calculate proceeds
        proceeds = quantity * price

        # Update cash balance
        self.cash_balance += proceeds

        # Update position
        if quantity == position.quantity:
            # Sold entire position
            del self.positions[symbol]
        else:
            # Partial sale
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=position.quantity - quantity,
                cost_basis=position.cost_basis,  # Keep same cost basis
            )

        # Record order
        order = Order(
            timestamp=datetime.now().isoformat(),
            order_type="SELL",
            symbol=symbol,
            quantity=quantity,
            price=price,
            total_amount=proceeds,
        )
        self.order_history.append(order)

        return True, f"Sold {quantity} shares of {symbol} at ${price:.2f}"

    def get_account_info(self) -> dict:
        """Get account overview information."""
        return {
            "cash_balance": self.cash_balance,
            "initial_cash": self.initial_cash,
            "currency": "USD",
        }

    def get_positions(self) -> List[dict]:
        """Get all current positions."""
        return [
            {
                "symbol": pos.symbol,
                "quantity": pos.quantity,
                "cost_basis": pos.cost_basis,
                "total_cost": pos.total_cost(),
            }
            for pos in self.positions.values()
        ]

    def get_order_history(self, limit: Optional[int] = None) -> List[dict]:
        """
        Get order history.

        Args:
            limit: Maximum number of orders to return (most recent first)
        """
        orders = self.order_history[::-1]  # Most recent first
        if limit:
            orders = orders[:limit]
        return [order.to_dict() for order in orders]

    def calculate_assets(self, market_prices: Dict[str, float]) -> dict:
        """
        Calculate total assets based on current market prices.

        Args:
            market_prices: Dict mapping symbol to current price

        Returns:
            Dictionary with asset breakdown
        """
        position_value = 0.0
        position_details = []

        for symbol, position in self.positions.items():
            current_price = market_prices.get(symbol, position.cost_basis)
            market_value = position.quantity * current_price
            unrealized_pnl = market_value - position.total_cost()

            position_value += market_value
            position_details.append({
                "symbol": symbol,
                "quantity": position.quantity,
                "cost_basis": position.cost_basis,
                "current_price": current_price,
                "market_value": market_value,
                "unrealized_pnl": unrealized_pnl,
            })

        total_assets = self.cash_balance + position_value

        return {
            "cash": self.cash_balance,
            "positions_value": position_value,
            "total_assets": total_assets,
            "initial_cash": self.initial_cash,
            "total_pnl": total_assets - self.initial_cash,
            "positions": position_details,
        }

    def save(self, file_path: str | Path) -> None:
        """Save account state to JSON file."""
        data = {
            "initial_cash": self.initial_cash,
            "cash_balance": self.cash_balance,
            "positions": {
                symbol: pos.to_dict()
                for symbol, pos in self.positions.items()
            },
            "order_history": [order.to_dict() for order in self.order_history],
        }

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, file_path: str | Path) -> VirtualAccount:
        """Load account state from JSON file."""
        path = Path(file_path)

        if not path.exists():
            # Return new account with defaults
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        positions = {
            symbol: Position.from_dict(pos_data)
            for symbol, pos_data in data.get("positions", {}).items()
        }

        order_history = [
            Order.from_dict(order_data)
            for order_data in data.get("order_history", [])
        ]

        return cls(
            initial_cash=data.get("initial_cash", 100000.0),
            cash_balance=data.get("cash_balance", 100000.0),
            positions=positions,
            order_history=order_history,
        )
