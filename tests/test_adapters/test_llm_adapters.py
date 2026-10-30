"""Unit tests for the Adapter Pattern (ILLMProviderAdapter)."""

import pytest
from src.adapters.mock_llm_provider_adapter import MockLLMProviderAdapter
from src.adapters.llm_provider_factory import LLMProviderFactory
from src.config import EvaluationConfig


class TestLLMProviderAdapters:
    """Class-based test suite for LLM provider adapters."""

    def test_mock_adapter_provider_name(self):
        adapter = MockLLMProviderAdapter()
        assert adapter.provider_name == "mock"

    def test_mock_adapter_handles_incident_telemetry(self):
        adapter = MockLLMProviderAdapter()
        res = adapter.generate_evaluation(
            system_prompt="Test",
            user_prompt="Checkout is slow. What happened?"
        )
        assert res["result"] == "fail"
        assert res["is_release_blocker"] is True
        assert res["release_blocker_category"] == "RB-5: Fabricated Root Cause & Dangerous Remediation"

    def test_mock_adapter_handles_temporal_stale(self):
        adapter = MockLLMProviderAdapter()
        res = adapter.generate_evaluation(
            system_prompt="Test",
            user_prompt="What did we decide about self-hosted runners?"
        )
        assert res["result"] == "fail"
        assert res["is_release_blocker"] is False

    def test_provider_factory_mock(self):
        cfg = EvaluationConfig(llm_provider="mock")
        adapter = LLMProviderFactory.create(cfg)
        assert adapter.provider_name == "mock"

    def test_provider_factory_openai(self):
        cfg = EvaluationConfig(llm_provider="openai", llm_model="gpt-4o")
        adapter = LLMProviderFactory.create(cfg)
        assert adapter.provider_name == "openai"

    def test_provider_factory_anthropic(self):
        cfg = EvaluationConfig(llm_provider="anthropic", llm_model="claude-3-5-sonnet")
        adapter = LLMProviderFactory.create(cfg)
        assert adapter.provider_name == "anthropic"
