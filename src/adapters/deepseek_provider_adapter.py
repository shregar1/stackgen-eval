"""DeepSeek Provider Adapter using OpenAI-compatible API with JSON mode and schema validation."""

import os
import json
from typing import Dict, Any, Optional
import httpx
from src.adapters.i_llm_provider_adapter import ILLMProviderAdapter
from src.models.llm_judge_output_schema import LLMJudgeOutputSchema


class DeepSeekProviderAdapter(ILLMProviderAdapter):
    """Adapter connecting to DeepSeek API (deepseek-chat, deepseek-reasoner)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "deepseek-chat",
        temperature: float = 0.0,
        timeout_seconds: float = 45.0
    ):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.model = model
        self.temperature = temperature
        self.timeout_seconds = timeout_seconds

    @property
    def provider_name(self) -> str:
        return "deepseek"

    def generate_evaluation(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        schema_json = json.dumps(LLMJudgeOutputSchema.model_json_schema(), indent=2)
        system_with_schema = (
            f"{system_prompt}\n\n"
            f"You MUST format your output strictly as a JSON object adhering to this JSON Schema:\n"
            f"{schema_json}\n"
            f"Return ONLY valid raw JSON."
        )

        payload = {
            "model": self.model,
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_with_schema},
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
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            parsed_raw = json.loads(content)
            validated = LLMJudgeOutputSchema.model_validate(parsed_raw)
            return validated.model_dump(mode="json")
