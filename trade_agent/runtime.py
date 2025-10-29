"""Runtime helpers for the trading agent."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from .agent import TradingAgent
from .config import AgentSettings
from .tools.longbridge import LongbridgeClient, TradingDataFetcher
from .virtual_account import VirtualAccount


def create_agent(
    *,
    settings: Optional[AgentSettings] = None,
    account_file: Optional[str | Path] = None,
) -> TradingAgent:
    """
    Create a trading agent using environment configuration.

    Args:
        settings: Agent settings (uses environment if not provided)
        account_file: Path to virtual account data file (default: storage/virtual_account.json)

    Returns:
        Configured TradingAgent instance
    """
    agent_settings = settings or AgentSettings.from_env()
    data_fetcher = None

    # Load or create virtual account
    if account_file is None:
        account_file = Path("storage/virtual_account.json")
    virtual_account = VirtualAccount.load(account_file)

    if agent_settings.longbridge_access_token:
        client = LongbridgeClient(
            agent_settings.longbridge_access_token,
            base_url=agent_settings.longbridge_base_url,
            timeout=agent_settings.longbridge_timeout,
        )
        data_fetcher = TradingDataFetcher(client, virtual_account)

    return TradingAgent(
        settings=agent_settings,
        data_fetcher=data_fetcher,
        virtual_account=virtual_account,
        account_file=account_file,
    )


def run_once(symbols: Optional[Iterable[str]] = None):
    """Convenience method to run the trading agent."""
    agent = create_agent()
    initial_state = {"symbols": list(symbols)} if symbols else None
    result = agent.run(initial_state=initial_state)
    return result["decision"]


if __name__ == "__main__":
    print(run_once())
