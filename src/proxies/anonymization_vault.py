"""AnonymizationVault managing reversible token redaction for DLP compliance."""

import re
from typing import Dict, List, Pattern


class AnonymizationVault:
    """
    Cryptographic vault managing reversible token redactions.
    Replaces sensitive names, emails, credentials, and confidential terms
    with synthetic anonymization tokens before external network transmission.
    """

    def __init__(self, sensitive_terms: List[str] = None):
        self._forward_map: Dict[str, str] = {}
        self._reverse_map: Dict[str, str] = {}
        self._counter: int = 0
        self._custom_terms: List[str] = sensitive_terms or ["Jordan", "Sarah Chen", "Priya"]
        self._email_regex_str: str = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"

    @property
    def redactions_count(self) -> int:
        return len(self._forward_map)

    def _get_email_pattern(self) -> Pattern:
        from src.core.flyweight.flyweight_regex_registry import FlyweightRegexRegistry
        return FlyweightRegexRegistry.get_instance().get_pattern(self._email_regex_str)

    def _get_term_pattern(self, term: str) -> Pattern:
        from src.core.flyweight.flyweight_regex_registry import FlyweightRegexRegistry
        return FlyweightRegexRegistry.get_instance().get_pattern(rf"\b{re.escape(term)}\b", flags=re.IGNORECASE)

    def anonymize(self, text: str) -> str:
        """Replace all sensitive entities and credentials with anonymized surrogate tokens."""
        if not text:
            return text

        # 0. Mask high-entropy credentials & API tokens (OWASP LLM06)
        from src.security.high_entropy_secret_masker import HighEntropySecretMasker
        result = HighEntropySecretMasker().mask_secrets(text)

        # 1. Anonymize emails
        emails = self._get_email_pattern().findall(result)
        for email in emails:
            if email not in self._forward_map:
                self._counter += 1
                token = f"[ANONYMIZED_EMAIL_{self._counter}]"
                self._forward_map[email] = token
                self._reverse_map[token] = email
            result = result.replace(email, self._forward_map[email])

        # 2. Anonymize sensitive named terms
        for term in self._custom_terms:
            pattern = self._get_term_pattern(term)
            if pattern.search(result):
                if term not in self._forward_map:
                    self._counter += 1
                    token = f"[ANONYMIZED_ENTITY_{self._counter}]"
                    self._forward_map[term] = token
                    self._reverse_map[token] = term
                result = pattern.sub(self._forward_map[term], result)

        return result

    def deanonymize(self, text: str) -> str:
        """Restore synthetic surrogate tokens back to their original domain terms."""
        if not text:
            return text

        result = text
        for token, original in self._reverse_map.items():
            result = result.replace(token, original)
        return result

    def clear(self) -> None:
        """Reset vault state."""
        self._forward_map.clear()
        self._reverse_map.clear()
        self._counter = 0
