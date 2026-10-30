"""Abstract interface for LLM provider adapters."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ILLMProviderAdapter(ABC):
    """Adapter interface standardizing interactions with frontier model backends."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the model provider (e.g. 'mock', 'openai', 'anthropic')."""
        pass

    @abstractmethod
    def generate_evaluation(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Generate structured evaluation dictionary conforming to AgentEvaluationResult schema.
        """
        pass
