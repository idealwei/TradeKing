"""LangGraph-based trading agent."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional, TypedDict

from langgraph.graph import END, StateGraph

from prompts.trade_prompts import TRADE_PROMPT

from .config import AgentSettings, ModelChoice
from .models import ModelDispatcher
from .tools.longbridge import TradingDataFetcher
from .virtual_account import VirtualAccount


class TradingState(TypedDict, total=False):
    account_data: str
    positions_data: str
    market_data: str
    assets_data: str
    orders_data: str
    symbols: Iterable[str]
    prompt: str
    decision: str


def render_prompt(template: str, variables: Dict[str, str]) -> str:
    result = template
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, value)
    return result


@dataclass
class TradingAgent:
    """Trading agent orchestrated with LangGraph."""

    settings: AgentSettings
    data_fetcher: Optional[TradingDataFetcher] = None
    virtual_account: Optional[VirtualAccount] = None
    account_file: Optional[str | Path] = None

    def __post_init__(self) -> None:
        self._dispatcher = ModelDispatcher(self.settings)
        self._graph = build_trading_graph(self)

    def _load_context(self, state: TradingState) -> TradingState:
        missing_keys = [
            key
            for key in ("account_data", "positions_data", "market_data", "assets_data", "orders_data")
            if key not in state
        ]
        if missing_keys:
            if not self.data_fetcher:
                # Provide empty default data when no data_fetcher is configured
                default_data = {
                    "account_data": {},
                    "positions_data": {},
                    "market_data": {},
                    "assets_data": {},
                    "orders_data": {},
                }
                for key in missing_keys:
                    if key in default_data:
                        state[key] = default_data[key]
            else:
                refreshed = self.data_fetcher.gather_context(symbols=state.get("symbols"))
                state.update(refreshed)
        return state

    def _compose_prompt(self, state: TradingState) -> TradingState:
        prompt_vars = {
            "model_name": self.settings.model_choice.value.upper(),
            "account_data": state["account_data"],
            "positions_data": state["positions_data"],
            "market_data": state["market_data"],
            "assets_data": state["assets_data"],
            "orders_data": state["orders_data"],
        }
        state["prompt"] = render_prompt(TRADE_PROMPT, prompt_vars)
        return state

    def _invoke_model(self, state: TradingState) -> TradingState:
        prompt = state["prompt"]
        choice = self.settings.model_choice
        user_tag = "trade-agent"
        result = self._dispatcher.generate_text(
            prompt,
            model_choice=choice,
            temperature=self.settings.temperature,
            max_output_tokens=self.settings.max_output_tokens,
            user=user_tag,
        )
        state["decision"] = result
        return state

    def run(self, initial_state: Optional[TradingState] = None) -> TradingState:
        """Execute the agent graph and return the final state."""
        state: TradingState = dict(initial_state or {})
        result = self._graph.invoke(state)

        # Save virtual account state after execution
        if self.virtual_account and self.account_file:
            self.virtual_account.save(self.account_file)

        return result


def build_trading_graph(agent: TradingAgent):
    graph = StateGraph(TradingState)
    graph.add_node("load_context", agent._load_context)
    graph.add_node("compose_prompt", agent._compose_prompt)
    graph.add_node("invoke_model", agent._invoke_model)

    graph.set_entry_point("load_context")
    graph.add_edge("load_context", "compose_prompt")
    graph.add_edge("compose_prompt", "invoke_model")
    graph.add_edge("invoke_model", END)

    return graph.compile()
