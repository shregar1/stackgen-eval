"""Anthropic Claude Provider Adapter."""

import os
import json
from typing import Dict, Any, Optional
import httpx
from src.adapters.i_llm_provider_adapter import ILLMProviderAdapter


class AnthropicProviderAdapter(ILLMProviderAdapter):
    """Adapter connecting to Anthropic Messages API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.0,
        timeout_seconds: float = 30.0
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.model = model
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def generate_evaluation(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "temperature": self.temperature,
            "system": system_prompt + "\nReturn ONLY valid JSON matching the schema.",
            "messages": [
                {"role": "user", "content": user_prompt}
            ]
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            content = data["content"][0]["text"]
            # Extract JSON block if surrounded by markdown fences
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            return json.loads(content)
