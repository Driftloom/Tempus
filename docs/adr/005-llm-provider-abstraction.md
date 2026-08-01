# ADR 005: LLM Provider Abstraction

## Status
Accepted

## Context
TEMPUS needs to interact with multiple LLM providers (Ollama, Anthropic, OpenAI) for different use cases. Each provider has different APIs, pricing models, and capabilities. A unified abstraction layer is needed to:
- Switch providers without code changes
- Implement fallback strategies
- Support provider-specific features
- Manage rate limits and quotas

## Decision
Implement a unified LLM provider abstraction with a common interface and provider-specific adapters.

### Architecture
```
LLMManager (Interface)
    ├── OllamaAdapter
    ├── AnthropicAdapter
    └── OpenAIAdapter
```

### Common Interface
```python
class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion for prompt."""
    
    @abstractmethod
    async def stream_complete(self, prompt: str, **kwargs) -> AsyncIterator[str]:
        """Stream completion for prompt."""
    
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
```

### Provider Selection Strategy
1. **Default Provider**: Ollama (local, free)
2. **Complex Tasks**: Anthropic Claude (high quality)
3. **Specific Features**: OpenAI GPT-4 (function calling)
4. **Fallback**: Automatic fallback if primary fails

### Rationale
1. **Flexibility**: Easy to add new providers
2. **Resilience**: Fallback strategies for reliability
3. **Cost Optimization**: Use cheapest provider for each task
4. **Feature Access**: Provider-specific features when needed
5. **Testing**: Mockable interface for tests

### Configuration
```python
LLM_PROVIDERS = {
    "default": "ollama",
    "ollama": {"host": "http://localhost:11434"},
    "anthropic": {"api_key": "...", "model": "claude-3-opus"},
    "openai": {"api_key": "...", "model": "gpt-4"}
}
```

### Alternatives Considered
- **Direct API Calls**: No abstraction, hard to switch providers
- **LangChain**: Overkill for our needs, adds dependency
- **Single Provider**: No fallback, vendor lock-in

## Consequences
### Positive
- Easy provider switching
- Automatic fallback on failure
- Provider-specific feature access
- Testable with mocks
- Cost optimization

### Negative
- Additional abstraction layer
- Need to maintain multiple adapters
- Provider-specific features may be hidden

## Implementation
```python
from app.llm.manager import LLMManager
from app.llm.providers.ollama import OllamaAdapter

llm_manager = LLMManager()
llm_manager.register_provider("ollama", OllamaAdapter())

# Use default provider
response = await llm_manager.complete("Hello, world!")

# Use specific provider
response = await llm_manager.complete("Hello, world!", provider="anthropic")
```

## References
- Anthropic API: https://docs.anthropic.com/
- OpenAI API: https://platform.openai.com/docs/
- Ollama: https://ollama.ai/
