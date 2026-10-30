"""Unit tests for the Proxy Pattern (AnonymizationVault & SecureLLMProviderProxy)."""

import pytest
from src.proxies.anonymization_vault import AnonymizationVault
from src.proxies.secure_llm_provider_proxy import SecureLLMProviderProxy
from src.adapters.mock_llm_provider_adapter import MockLLMProviderAdapter


class TestSecureLLMProxy:
    """Class-based test suite verifying enterprise DLP proxy, token anonymization, and prompt security."""

    def test_vault_anonymizes_and_deanonymizes_text(self):
        vault = AnonymizationVault(sensitive_terms=["Jordan", "Sarah Chen"])
        raw = "Do not assign Jordan to the project. Contact jordan@corp.internal or Sarah Chen."

        anonymized = vault.anonymize(raw)
        assert "Jordan" not in anonymized
        assert "Sarah Chen" not in anonymized
        assert "jordan@corp.internal" not in anonymized
        assert "[ANONYMIZED_EMAIL_1]" in anonymized
        assert "[ANONYMIZED_ENTITY_" in anonymized
        assert vault.redactions_count == 3

        restored = vault.deanonymize(anonymized)
        assert restored == raw

    def test_proxy_anonymizes_prompts_and_restores_verdict(self):
        underlying_adapter = MockLLMProviderAdapter()
        vault = AnonymizationVault(sensitive_terms=["Priya"])
        proxy = SecureLLMProviderProxy(underlying_adapter, vault=vault)

        system_prompt = "You are an evaluation judge. Strict evaluation rules apply."
        user_prompt = "Priya cancelled the self-hosted runners purchase on June 12."

        res = proxy.generate_evaluation(system_prompt, user_prompt)

        assert proxy.total_proxied_requests == 1
        assert res["evaluator_type"] == "llm_judge"
        assert res["result"] == "fail"
        assert res["dlp_anonymization_applied"] is True

        # Ensure that restored facts mention the original entity name
        facts = " ".join(res["driving_facts"])
        assert "Priya" in facts

    def test_proxy_provider_name_reflects_wrapping(self):
        underlying = MockLLMProviderAdapter()
        proxy = SecureLLMProviderProxy(underlying)
        assert proxy.provider_name == "secure_proxy(mock)"

    def test_vault_empty_and_clear(self):
        vault = AnonymizationVault()
        assert vault.anonymize("") == ""
        assert vault.anonymize(None) is None
        assert vault.deanonymize("") == ""
        assert vault.deanonymize(None) is None

        vault.anonymize("Jordan")
        assert vault.redactions_count > 0
        vault.clear()
        assert vault.redactions_count == 0
