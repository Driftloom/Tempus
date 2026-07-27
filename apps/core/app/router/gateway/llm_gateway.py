"""LLM gateway for provider abstraction using LiteLLM."""

from typing import Dict, Optional
from app.core.config import settings
import httpx
from structlog import get_logger

logger = get_logger(__name__)


class LLMGateway:
    """Gateway for abstracting LLM provider interactions using LiteLLM."""
    
    def __init__(self):
        """Initialize LLM gateway with LiteLLM support."""
        self.litellm_base_url = getattr(settings, 'litellm_base_url', 'http://localhost:4000')
        self.ollama_host = settings.ollama_host
        self.anthropic_api_key = settings.anthropic_api_key
        self.openai_api_key = settings.openai_api_key
        self.use_litellm = getattr(settings, 'use_litellm', False)
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def execute(
        self,
        prompt: str,
        provider: str,
        model: str,
        context: Optional[Dict] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict:
        """Execute request with specified provider and model."""
        logger.info("Executing LLM request", provider=provider, model=model, use_litellm=self.use_litellm)
        
        if self.use_litellm:
            return await self._execute_litellm(prompt, provider, model, context, temperature, max_tokens)
        elif provider == "local" or provider == "ollama":
            return await self._execute_local(prompt, model)
        elif provider == "anthropic":
            return await self._execute_anthropic(prompt, model, context, temperature, max_tokens)
        elif provider == "openai":
            return await self._execute_openai(prompt, model, context, temperature, max_tokens)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def _execute_litellm(
        self,
        prompt: str,
        provider: str,
        model: str,
        context: Optional[Dict],
        temperature: float,
        max_tokens: int
    ) -> Dict:
        """Execute request via LiteLLM gateway."""
        try:
            payload = {
                "model": f"{provider}/{model}",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if context and context.get("system_message"):
                payload["messages"].insert(0, {"role": "system", "content": context["system_message"]})
            
            response = await self.client.post(
                f"{self.litellm_base_url}/v1/chat/completions",
                json=payload
            )
            
            if response.status_code != 200:
                logger.error("LiteLLM request failed", status_code=response.status_code)
                return {"content": None, "provider": provider, "model": model, "error": f"HTTP {response.status_code}", "cost": 0.0}
            
            data = response.json()
            choice = data.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content")
            usage = data.get("usage", {})
            
            return {
                "content": content,
                "provider": provider,
                "model": model,
                "cost": self._calculate_cost(provider, model, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)),
                "tokens": {"input": usage.get("prompt_tokens", 0), "output": usage.get("completion_tokens", 0)}
            }
        except Exception as e:
            logger.error("LiteLLM execution failed", error=str(e))
            return {"content": None, "provider": provider, "model": model, "error": str(e), "cost": 0.0}
    
    async def _execute_local(self, prompt: str, model: str) -> Dict:
        """Execute request with local Ollama."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.ollama_host}/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False}
                )
                response.raise_for_status()
                result = response.json()
                return {"content": result.get("response", ""), "provider": "local", "model": model, "cost": 0}
        except Exception as e:
            logger.error("Local LLM execution failed", error=str(e))
            raise
    
    async def _execute_anthropic(self, prompt: str, model: str, context: Optional[Dict], temperature: float, max_tokens: int) -> Dict:
        """Execute request with Anthropic Claude."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.anthropic_api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": model,
                        "max_tokens": max_tokens,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                response.raise_for_status()
                result = response.json()
                input_tokens = result.get("usage", {}).get("input_tokens", 0)
                output_tokens = result.get("usage", {}).get("output_tokens", 0)
                return {
                    "content": result["content"][0]["text"],
                    "provider": "anthropic",
                    "model": model,
                    "cost": self._calculate_cost("anthropic", model, input_tokens, output_tokens),
                    "tokens": {"input": input_tokens, "output": output_tokens}
                }
        except Exception as e:
            logger.error("Anthropic execution failed", error=str(e))
            raise
    
    async def _execute_openai(self, prompt: str, model: str, context: Optional[Dict], temperature: float, max_tokens: int) -> Dict:
        """Execute request with OpenAI."""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}", "Content-Type": "application/json"},
                    json={"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": temperature, "max_tokens": max_tokens}
                )
                response.raise_for_status()
                result = response.json()
                choice = result.get("choices", [{}])[0]
                usage = result.get("usage", {})
                return {
                    "content": choice.get("message", {}).get("content"),
                    "provider": "openai",
                    "model": model,
                    "cost": self._calculate_cost("openai", model, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)),
                    "tokens": {"input": usage.get("prompt_tokens", 0), "output": usage.get("completion_tokens", 0)}
                }
        except Exception as e:
            logger.error("OpenAI execution failed", error=str(e))
            raise
    
    def _calculate_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on provider pricing."""
        pricing = {
            "anthropic": {"claude-3-opus-20240229": (15.0, 75.0), "claude-3-sonnet-20240229": (3.0, 15.0)},
            "openai": {"gpt-4": (30.0, 60.0), "gpt-3.5-turbo": (0.5, 1.5)},
            "ollama": {"llama2": (0.0, 0.0), "mistral": (0.0, 0.0)}
        }
        model_pricing = pricing.get(provider, {}).get(model, (1.0, 1.0))
        return (input_tokens / 1_000_000) * model_pricing[0] + (output_tokens / 1_000_000) * model_pricing[1]
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
