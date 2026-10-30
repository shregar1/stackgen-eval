"""LLM Provider Factory Pattern."""

from src.config import EvaluationConfig, default_config
from src.adapters.i_llm_provider_adapter import ILLMProviderAdapter
from src.adapters.mock_llm_provider_adapter import MockLLMProviderAdapter
from src.adapters.openai_provider_adapter import OpenAIProviderAdapter
from src.adapters.anthropic_provider_adapter import AnthropicProviderAdapter


class LLMProviderFactory:
    """Factory creating appropriate ILLMProviderAdapter based on configuration."""

    @staticmethod
    def create(config: EvaluationConfig = default_config) -> ILLMProviderAdapter:
        provider = config.llm_provider.lower()
        if provider == "openai":
            return OpenAIProviderAdapter(
                model=config.llm_model,
                temperature=config.llm_temperature,
                timeout_seconds=config.llm_timeout_seconds
            )
        elif provider == "anthropic":
            return AnthropicProviderAdapter(
                model=config.llm_model,
                temperature=config.llm_temperature,
                timeout_seconds=config.llm_timeout_seconds
            )
        return MockLLMProviderAdapter()
