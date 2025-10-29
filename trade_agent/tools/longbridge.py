"""Longbridge API helper utilities."""

from __future__ import annotations

import json
from typing import Dict, Iterable, Optional, Sequence

import requests

from ..virtual_account import VirtualAccount


class LongbridgeClient:
    """Thin wrapper around the Longbridge OpenAPI."""

    def __init__(
        self,
        access_token: str,
        *,
        base_url: str = "https://openapi.longbridgeapp.com",
        timeout: float = 10.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not access_token:
            raise ValueError("Longbridge access token is required")
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = session or requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }
        )

    def _request(self, method: str, path: str, *, params: Optional[dict] = None, payload: Optional[dict] = None):
        url = f"{self._base_url}/{path.lstrip('/')}"
        response = self._session.request(
            method=method.upper(),
            url=url,
            params=params,
            json=payload,
            timeout=self._timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("data", data)

    def get_account_overview(self):
        return self._request("GET", "/v1/asset/account")

    def get_positions(self):
        return self._request("GET", "/v1/asset/position/list")

    def get_order_history(self):
        return self._request("GET", "/v1/trade/order/history")

    def get_assets(self):
        return self._request("GET", "/v1/asset/account/currency")

    def get_market_snapshot(self, symbols: Sequence[str]):
        symbols_param = ",".join(symbols)
        return self._request(
            "GET",
            "/v1/market/snapshot",
            params={"symbols": symbols_param},
        )


def format_data_for_prompt(data) -> str:
    """Return a compact JSON string suitable for prompt injection."""
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


class TradingDataFetcher:
    """Aggregator that prepares the prompt context using Longbridge market data and virtual account data."""

    DEFAULT_SYMBOLS = ("NVDA.US", "TSLA.US", "GOOGL.US", "MSFT.US", "COIN.US", "BABA.US", "SPY.US", "GLD.US", "IBIT.US", "UVIX.US")

    def __init__(self, client: LongbridgeClient, virtual_account: VirtualAccount):
        self._client = client
        self._account = virtual_account

    def gather_context(
        self,
        *,
        symbols: Optional[Iterable[str]] = None,
    ) -> dict:
        watch_list = list(symbols or self.DEFAULT_SYMBOLS)

        # Only get market data from Longbridge API
        market_data = self._client.get_market_snapshot(watch_list)

        # Extract current prices from market data for asset calculation
        market_prices = self._extract_prices(market_data)

        # Get all other data from virtual account
        account_data = self._account.get_account_info()
        positions_data = self._account.get_positions()
        orders_data = self._account.get_order_history(limit=50)  # Last 50 orders
        assets_data = self._account.calculate_assets(market_prices)

        return {
            "account_data": format_data_for_prompt(account_data),
            "positions_data": format_data_for_prompt(positions_data),
            "orders_data": format_data_for_prompt(orders_data),
            "assets_data": format_data_for_prompt(assets_data),
            "market_data": format_data_for_prompt(market_data),
            "symbols": watch_list,
        }

    def _extract_prices(self, market_data) -> Dict[str, float]:
        """Extract current prices from market snapshot data."""
        prices = {}

        # Handle different possible market data structures
        if isinstance(market_data, dict):
            # If market_data has a 'data' key with list of snapshots
            snapshots = market_data.get("snapshots", market_data.get("data", []))
        elif isinstance(market_data, list):
            snapshots = market_data
        else:
            return prices

        for snapshot in snapshots:
            if isinstance(snapshot, dict):
                symbol = snapshot.get("symbol")
                # Try different price fields that might exist
                price = (
                    snapshot.get("last_done") or
                    snapshot.get("price") or
                    snapshot.get("close") or
                    snapshot.get("prev_close")
                )
                if symbol and price is not None:
                    prices[symbol] = float(price)

        return prices
