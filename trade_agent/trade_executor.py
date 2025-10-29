"""Trade execution helper for processing AI decisions."""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional

from .virtual_account import VirtualAccount


class TradeExecutor:
    """Executes trades based on AI model decisions."""

    def __init__(self, virtual_account: VirtualAccount):
        self.account = virtual_account

    def parse_and_execute(self, decision_text: str, market_prices: Dict[str, float]) -> List[Dict]:
        """
        Parse trading decisions from AI output and execute them.

        Args:
            decision_text: The AI model's decision output
            market_prices: Current market prices for symbols

        Returns:
            List of execution results
        """
        results = []

        # Try to find JSON-formatted decisions
        json_trades = self._extract_json_trades(decision_text)
        if json_trades:
            for trade in json_trades:
                result = self._execute_trade(trade, market_prices)
                results.append(result)
            return results

        # Fallback: try to parse natural language decisions
        nl_trades = self._parse_natural_language(decision_text)
        for trade in nl_trades:
            result = self._execute_trade(trade, market_prices)
            results.append(result)

        return results

    def _extract_json_trades(self, text: str) -> List[Dict]:
        """Extract JSON-formatted trade instructions."""
        trades = []

        # Look for JSON arrays or objects
        json_pattern = r'\{[^{}]*"action"[^{}]*\}|\[[^\[\]]*"action"[^\[\]]*\]'
        matches = re.findall(json_pattern, text, re.IGNORECASE | re.DOTALL)

        for match in matches:
            try:
                data = json.loads(match)
                if isinstance(data, dict):
                    trades.append(data)
                elif isinstance(data, list):
                    trades.extend(data)
            except json.JSONDecodeError:
                continue

        return trades

    def _parse_natural_language(self, text: str) -> List[Dict]:
        """Parse natural language trading decisions."""
        trades = []

        # Pattern: BUY/SELL <quantity> <symbol> [at <price>]
        patterns = [
            r'(BUY|SELL)\s+(\d+)\s+(?:shares?\s+of\s+)?([A-Z]+\.?[A-Z]*)\s+(?:at\s+\$?(\d+\.?\d*))?',
            r'(BUY|SELL)\s+([A-Z]+\.?[A-Z]*)\s+(\d+)\s+(?:shares?\s+)?(?:at\s+\$?(\d+\.?\d*))?',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 4 and match[0] and match[1] and match[2]:
                    # First pattern: BUY 100 AAPL at 150.00
                    action, quantity, symbol, price = match
                    trades.append({
                        "action": action.upper(),
                        "symbol": symbol.upper(),
                        "quantity": int(quantity),
                        "price": float(price) if price else None,
                    })

        return trades

    def _execute_trade(self, trade: Dict, market_prices: Dict[str, float]) -> Dict:
        """
        Execute a single trade.

        Args:
            trade: Trade specification dict with keys: action, symbol, quantity, price (optional)
            market_prices: Current market prices

        Returns:
            Execution result dict
        """
        action = trade.get("action", "").upper()
        symbol = trade.get("symbol", "").upper()
        quantity = trade.get("quantity", 0)
        price = trade.get("price")

        # Validate inputs
        if action not in ["BUY", "SELL"]:
            return {
                "success": False,
                "message": f"Invalid action: {action}",
                "trade": trade,
            }

        if not symbol:
            return {
                "success": False,
                "message": "Symbol is required",
                "trade": trade,
            }

        if not isinstance(quantity, (int, float)) or quantity <= 0:
            return {
                "success": False,
                "message": f"Invalid quantity: {quantity}",
                "trade": trade,
            }

        # Use market price if not specified
        if price is None:
            price = market_prices.get(symbol)
            if price is None:
                return {
                    "success": False,
                    "message": f"No price available for {symbol}",
                    "trade": trade,
                }

        # Execute the trade
        if action == "BUY":
            success, message = self.account.buy(symbol, int(quantity), float(price))
        else:  # SELL
            success, message = self.account.sell(symbol, int(quantity), float(price))

        return {
            "success": success,
            "message": message,
            "trade": {
                "action": action,
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
            },
        }

    def execute_trades_from_json(self, trades_json: str | List[Dict], market_prices: Dict[str, float]) -> List[Dict]:
        """
        Execute trades from JSON string or list of trade dicts.

        Args:
            trades_json: JSON string or list of trade dictionaries
            market_prices: Current market prices

        Returns:
            List of execution results
        """
        if isinstance(trades_json, str):
            try:
                trades = json.loads(trades_json)
            except json.JSONDecodeError as e:
                return [{
                    "success": False,
                    "message": f"Invalid JSON: {e}",
                    "trade": None,
                }]
        else:
            trades = trades_json

        if not isinstance(trades, list):
            trades = [trades]

        results = []
        for trade in trades:
            result = self._execute_trade(trade, market_prices)
            results.append(result)

        return results
