"""Model routing utilities."""

from __future__ import annotations

import logging
from typing import Dict, Optional

from openai import OpenAI

from .config import AgentSettings, ModelChoice, ModelConfig

logger = logging.getLogger(__name__)


class ModelDispatcher:
    """Builds OpenAI-compatible clients for the configured foundation models."""

    def __init__(self, settings: AgentSettings):
        self._settings = settings
        self._clients: Dict[ModelChoice, OpenAI] = {}

    def _get_model_config(self, choice: ModelChoice) -> ModelConfig:
        try:
            return self._settings.model_overrides[choice]
        except KeyError as exc:
            raise KeyError(f"No configuration found for model {choice.value}") from exc

    def _build_client(self, choice: ModelChoice) -> OpenAI:
        if choice in self._clients:
            return self._clients[choice]

        config = self._get_model_config(choice)
        api_key = config.resolve_api_key()
        base_url = config.resolve_base_url()
        organization = config.resolve_organization()
        logger.debug(
            "Initializing OpenAI-compatible client",
            extra={"model": config.model_name, "base_url": base_url, "organization": organization},
        )
        client = OpenAI(api_key=api_key, base_url=base_url, organization=organization)
        self._clients[choice] = client
        return client

    def generate_text(
        self,
        prompt: str,
        *,
        model_choice: Optional[ModelChoice] = None,
        temperature: Optional[float] = None,
        max_output_tokens: Optional[int] = None,
        user: Optional[str] = None,
    ) -> str:
        """Call the configured model and return the generated text."""
        choice = model_choice or self._settings.model_choice
        client = self._build_client(choice)
        config = self._get_model_config(choice)
        temp = temperature if temperature is not None else self._settings.temperature
        max_tokens = max_output_tokens if max_output_tokens is not None else self._settings.max_output_tokens

        response = client.chat.completions.create(
            model=config.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=temp,
            max_tokens=max_tokens,
            user=user,
        )
        return response.choices[0].message.content.strip()
