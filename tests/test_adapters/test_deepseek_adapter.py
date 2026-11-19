"""Unit tests for DeepSeekProviderAdapter adhering to strict single-class OOP design."""

from unittest.mock import MagicMock
import httpx
from src.adapters.deepseek_provider_adapter import DeepSeekProviderAdapter
from src.adapters.llm_provider_factory import LLMProviderFactory
from src.config import EvaluationConfig


class TestDeepSeekAdapter:
    """Class-based test suite for DeepSeekProviderAdapter."""

    def test_deepseek_adapter_initialization(self):
        adapter = DeepSeekProviderAdapter(
            api_key="sk-deepseek-test",
            model="deepseek-chat",
            temperature=0.1,
            timeout_seconds=20.0
        )
        assert adapter.provider_name == "deepseek"
        assert adapter.api_key == "sk-deepseek-test"
        assert adapter.model == "deepseek-chat"
        assert adapter.temperature == 0.1
        assert adapter.timeout_seconds == 20.0
        assert adapter.base_url == "https://api.deepseek.com/v1"

    def test_factory_creates_deepseek_adapter(self):
        cfg = EvaluationConfig(llm_provider="deepseek", llm_model="deepseek-reasoner")
        adapter = LLMProviderFactory.create(cfg)
        assert adapter.provider_name == "deepseek"
        assert isinstance(adapter, DeepSeekProviderAdapter)
        assert adapter.model == "deepseek-reasoner"

    def test_factory_creates_deepseek_with_default_model(self):
        cfg = EvaluationConfig(llm_provider="deepseek")
        adapter = LLMProviderFactory.create(cfg)
        assert adapter.provider_name == "deepseek"
        assert isinstance(adapter, DeepSeekProviderAdapter)
        assert adapter.model == "deepseek-chat"

    def test_deepseek_generate_evaluation_success(self, monkeypatch):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"evaluator_type": "llm_judge", "result": "pass", "is_release_blocker": false, "release_blocker_category": "none", "reasons": ["All checks passed"], "driving_facts": []}'
                    }
                }
            ]
        }
        mock_resp.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.post.return_value = mock_resp
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None

        monkeypatch.setattr(httpx, "Client", lambda **kwargs: mock_client)

        adapter = DeepSeekProviderAdapter(api_key="sk-test-deepseek")
        result = adapter.generate_evaluation("system prompt", "user prompt")

        assert result["result"] == "pass"
        assert result["is_release_blocker"] is False
        assert result["reasons"] == ["All checks passed"]
        mock_client.post.assert_called_once()
        call_kwargs = mock_client.post.call_args.kwargs
        assert "Authorization" in call_kwargs["headers"]
        assert call_kwargs["headers"]["Authorization"] == "Bearer sk-test-deepseek"
        assert call_kwargs["json"]["model"] == "deepseek-chat"
        assert call_kwargs["json"]["response_format"] == {"type": "json_object"}

    def test_deepseek_generate_evaluation_markdown_block(self, monkeypatch):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '```json\n{"evaluator_type": "llm_judge", "result": "fail", "is_release_blocker": true, "release_blocker_category": "RB-5: Fabricated Root Cause & Dangerous Remediation", "reasons": ["Telemetry contradiction"], "driving_facts": ["payments 10:04"]}\n```'
                    }
                }
            ]
        }
        mock_resp.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.post.return_value = mock_resp
        mock_client.__enter__.return_value = mock_client
        mock_client.__exit__.return_value = None

        monkeypatch.setattr(httpx, "Client", lambda **kwargs: mock_client)

        adapter = DeepSeekProviderAdapter(api_key="sk-test-deepseek")
        result = adapter.generate_evaluation("system prompt", "user prompt")

        assert result["result"] == "fail"
        assert result["is_release_blocker"] is True
        assert result["release_blocker_category"] == "RB-5: Fabricated Root Cause & Dangerous Remediation"
