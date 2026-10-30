"""SecureLLMProviderProxy implementing DLP/PII filtering proxy for LLM adapters."""

from typing import Any, Dict, Optional
from src.adapters.i_llm_provider_adapter import ILLMProviderAdapter
from src.proxies.anonymization_vault import AnonymizationVault


class SecureLLMProviderProxy(ILLMProviderAdapter):
    """
    Protection Proxy that intercepts prompts destined for third-party LLMs,
    strips PII / confidential entities through the AnonymizationVault,
    forwards sanitized text to the provider, and de-anonymizes results.
    """

    def __init__(self, target_adapter: ILLMProviderAdapter, vault: Optional[AnonymizationVault] = None):
        self._target_adapter: ILLMProviderAdapter = target_adapter
        self._vault: AnonymizationVault = vault or AnonymizationVault()
        self.total_proxied_requests: int = 0

    @property
    def provider_name(self) -> str:
        return f"secure_proxy({self._target_adapter.provider_name})"

    @property
    def vault(self) -> AnonymizationVault:
        return self._vault

    def generate_evaluation(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Intercept, sanitize, forward to target provider, and restore tokens."""
        self.total_proxied_requests += 1

        # 1. Scrub outbound prompts
        sanitized_system = self._vault.anonymize(system_prompt)
        sanitized_user = self._vault.anonymize(user_prompt)

        # 2. Forward sanitized payload to real LLM provider
        raw_result = self._target_adapter.generate_evaluation(sanitized_system, sanitized_user)

        # 3. Restore deanonymized tokens in returned reasons and driving facts
        cleaned_reasons = [self._vault.deanonymize(r) for r in raw_result.get("reasons", [])]
        cleaned_facts = [self._vault.deanonymize(f) for f in raw_result.get("driving_facts", [])]

        output = dict(raw_result)
        output["reasons"] = cleaned_reasons
        output["driving_facts"] = cleaned_facts
        output["dlp_anonymization_applied"] = self._vault.redactions_count > 0
        return output
