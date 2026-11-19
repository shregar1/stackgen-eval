"""OpenAI / Compatible Provider Adapter with Structured JSON Schema."""

import os
import json
from typing import Dict, Any, Optional
import httpx
from src.adapters.i_llm_provider_adapter import ILLMProviderAdapter
from src.models.llm_judge_output_schema import LLMJudgeOutputSchema


class OpenAIProviderAdapter(ILLMProviderAdapter):
    """Adapter connecting to OpenAI or OpenAI-compatible endpoints with strict structured schema."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.0,
        timeout_seconds: float = 30.0
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = model
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "openai"

    def generate_evaluation(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "llm_judge_evaluation",
                    "strict": True,
                    "schema": LLMJudgeOutputSchema.model_json_schema()
                }
            },
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }

        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            parsed_raw = json.loads(content)
            validated = LLMJudgeOutputSchema.model_validate(parsed_raw)
            return validated.model_dump()
