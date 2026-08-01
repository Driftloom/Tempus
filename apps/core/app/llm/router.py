"""LLM router using LiteLLM for multi-provider support."""

from typing import Any

import structlog
from litellm import acompletion

from app.core.config import settings

logger = structlog.get_logger(__name__)


class LLMRouter:
    """Router for LLM provider selection and load balancing."""

    def __init__(self):
        """Initialize LLM router."""
        self.providers = {
            "anthropic": {
                "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                "api_key": settings.anthropic_api_key,
            },
            "openai": {
                "models": ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
                "api_key": settings.openai_api_key,
            },
            "ollama": {
                "models": ["llama2", "mistral", "codellama"],
                "api_base": settings.ollama_host,
            },
        }
        self.routing_policy = "cost_optimized"  # cost_optimized, performance, latency

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> dict[str, Any]:
        """Complete a chat completion request."""
        selected_model, selected_provider = self._select_model(model, provider)

        try:
            response = await acompletion(
                model=selected_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            logger.info(
                "LLM completion successful",
                model=selected_model,
                provider=selected_provider,
                tokens=response.get("usage", {}).get("total_tokens"),
            )

            return response

        except Exception as e:
            logger.error("LLM completion failed", model=selected_model, error=str(e))
            # Fallback to backup provider
            return await self._fallback_completion(messages, selected_provider, temperature, max_tokens)

    async def _fallback_completion(
        self,
        messages: list[dict[str, str]],
        failed_provider: str,
        temperature: float,
        max_tokens: int
    ) -> dict[str, Any]:
        """Fallback to backup provider on failure."""
        for provider_name, provider_config in self.providers.items():
            if provider_name != failed_provider and provider_config.get("api_key"):
                try:
                    backup_model = provider_config["models"][0]
                    response = await acompletion(
                        model=backup_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    logger.info("Fallback successful", provider=provider_name, model=backup_model)
                    return response
                except Exception as e:
                    logger.warning("Fallback failed", provider=provider_name, error=str(e))

        raise Exception("All LLM providers failed")

    def _select_model(self, model: str | None, provider: str | None) -> tuple[str, str]:
        """Select model based on routing policy."""
        if model and provider:
            return model, provider

        if model:
            # Find provider for model
            for provider_name, provider_config in self.providers.items():
                if model in provider_config["models"]:
                    return model, provider_name

        # Select based on routing policy
        if self.routing_policy == "cost_optimized":
            return self._select_cost_optimized()
        elif self.routing_policy == "performance":
            return self._select_performance()
        else:  # latency
            return self._select_low_latency()

    def _select_cost_optimized(self) -> tuple[str, str]:
        """Select cost-optimized model (local Ollama first)."""
        if "ollama" in self.providers and self.providers["ollama"].get("api_base"):
            return "llama2", "ollama"
        return "gpt-3.5-turbo", "openai"

    def _select_performance(self) -> tuple[str, str]:
        """Select high-performance model."""
        if "anthropic" in self.providers and self.providers["anthropic"].get("api_key"):
            return "claude-3-opus-20240229", "anthropic"
        return "gpt-4-turbo-preview", "openai"

    def _select_low_latency(self) -> tuple[str, str]:
        """Select low-latency model."""
        if "ollama" in self.providers and self.providers["ollama"].get("api_base"):
            return "llama2", "ollama"
        return "claude-3-haiku-20240307", "anthropic"

    def get_available_models(self) -> list[str]:
        """Get all available models."""
        models = []
        for provider_config in self.providers.values():
            models.extend(provider_config["models"])
        return models

    def set_routing_policy(self, policy: str) -> None:
        """Set routing policy."""
        if policy in ["cost_optimized", "performance", "latency"]:
            self.routing_policy = policy
            logger.info("Routing policy updated", policy=policy)


# Global LLM router instance
llm_router = LLMRouter()
