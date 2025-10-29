"""Runtime helpers for the trading agent."""

from __future__ import annotations

from typing import Iterable, Optional

from .agent import TradingAgent
from .config import AgentSettings
from .tools.longbridge import LongbridgeClient, TradingDataFetcher


def create_agent(
    *,
    settings: Optional[AgentSettings] = None,
) -> TradingAgent:
    """Create a trading agent using environment configuration."""
    agent_settings = settings or AgentSettings.from_env()
    data_fetcher = None

    if agent_settings.longbridge_access_token:
        client = LongbridgeClient(
            agent_settings.longbridge_access_token,
            base_url=agent_settings.longbridge_base_url,
            timeout=agent_settings.longbridge_timeout,
        )
        data_fetcher = TradingDataFetcher(client)

    return TradingAgent(settings=agent_settings, data_fetcher=data_fetcher)


def run_once(symbols: Optional[Iterable[str]] = None):
    """Convenience method to run the trading agent."""
    agent = create_agent()
    initial_state = {"symbols": list(symbols)} if symbols else None
    result = agent.run(initial_state=initial_state)
    return result["decision"]


if __name__ == "__main__":
    print(run_once())
