"""Configuration objects for the trading agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


class ModelChoice(str, Enum):
    """Supported foundation models."""

    GPT5 = "gpt5"
    DEEPSEEK = "deepseek"


@dataclass
class ModelConfig:
    """Configuration for a model provider reachable via the OpenAI-compatible API."""

    model_name: str
    api_key_env: str
    base_url_env: Optional[str] = None
    fallback_base_url: Optional[str] = None
    organization_env: Optional[str] = None

    def resolve_api_key(self) -> str:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"Environment variable {self.api_key_env} is required for model {self.model_name}."
            )
        return api_key

    def resolve_base_url(self) -> Optional[str]:
        if self.base_url_env:
            value = os.getenv(self.base_url_env)
            if value:
                return value
        return self.fallback_base_url

    def resolve_organization(self) -> Optional[str]:
        if not self.organization_env:
            return None
        return os.getenv(self.organization_env) or None


DEFAULT_MODEL_CONFIG: Dict[ModelChoice, ModelConfig] = {
    ModelChoice.GPT5: ModelConfig(
        model_name="gpt-5.0",
        api_key_env="OPENAI_API_KEY",
        base_url_env="OPENAI_BASE_URL",
        fallback_base_url="https://api.openai.com/v1",
        organization_env="OPENAI_ORG_ID",
    ),
    ModelChoice.DEEPSEEK: ModelConfig(
        model_name="deepseek-chat",
        api_key_env="DEEPSEEK_API_KEY",
        base_url_env="DEEPSEEK_BASE_URL",
        fallback_base_url="https://api.deepseek.com/v1",
    ),
}


@dataclass
class AgentSettings:
    """Runtime settings for the trading agent."""

    model_choice: ModelChoice = ModelChoice.GPT5
    temperature: float = 0.5
    max_output_tokens: int = 1024
    model_overrides: Dict[ModelChoice, ModelConfig] = field(
        default_factory=lambda: DEFAULT_MODEL_CONFIG.copy()
    )
    longbridge_access_token: Optional[str] = None
    longbridge_base_url: str = "https://openapi.longbridgeapp.com"
    longbridge_timeout: float = 10.0

    @classmethod
    def from_env(cls) -> "AgentSettings":
        """Create settings using environment variables."""
        model_choice = os.getenv("TRADE_AGENT_MODEL", ModelChoice.GPT5.value)
        try:
            parsed_model = ModelChoice(model_choice.lower())
        except ValueError as exc:
            raise ValueError(f"Unsupported TRADE_AGENT_MODEL: {model_choice}") from exc

        temperature = float(os.getenv("TRADE_AGENT_TEMPERATURE", "0.4"))
        max_output_tokens = int(os.getenv("TRADE_AGENT_MAX_OUTPUT_TOKENS", "1024"))

        settings = cls(
            model_choice=parsed_model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        access_token = os.getenv("LONGBRIDGE_ACCESS_TOKEN")
        if access_token:
            settings.longbridge_access_token = access_token
        base_url = os.getenv("LONGBRIDGE_BASE_URL")
        if base_url:
            settings.longbridge_base_url = base_url
        timeout = os.getenv("LONGBRIDGE_TIMEOUT")
        if timeout:
            settings.longbridge_timeout = float(timeout)
        return settings
