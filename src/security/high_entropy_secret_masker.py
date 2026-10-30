"""HighEntropySecretMasker protecting against OWASP LLM06 Sensitive Information Disclosure."""

import math
import re
from typing import Dict, List, Pattern


class HighEntropySecretMasker:
    """
    OWASP LLM06 Sensitive Information Disclosure Defense.
    Scans trace payloads for credentials, API tokens, private keys, and high-entropy secrets,
    redacting them prior to external LLM evaluation and report generation.
    """

    SECRET_SIGNATURES: Dict[str, str] = {
        "AWS_KEY": r"\b(AKIA[0-9A-Z]{16})\b",
        "GITHUB_PAT": r"\b(ghp_[a-zA-Z0-9]{36})\b",
        "SLACK_TOKEN": r"\b(xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,32})\b",
        "BEARER_JWT": r"\b(eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})\b",
        "PRIVATE_KEY": r"(-----BEGIN (?:RSA )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA )?PRIVATE KEY-----)"
    }

    def __init__(self, entropy_threshold: float = 4.2):
        self.entropy_threshold: float = entropy_threshold
        self._compiled_patterns: Dict[str, Pattern] = {
            name: re.compile(pat) for name, pat in self.SECRET_SIGNATURES.items()
        }
        self.redacted_secrets_count: int = 0

    @classmethod
    def calculate_shannon_entropy(cls, text: str) -> float:
        """Calculate Shannon entropy for a string to identify cryptographic randomness."""
        if not text:
            return 0.0
        entropy = 0.0
        length = len(text)
        frequency = {}
        for char in text:
            frequency[char] = frequency.get(char, 0) + 1
        for count in frequency.values():
            p = count / length
            entropy -= p * math.log2(p)
        return entropy

    def mask_secrets(self, text: str) -> str:
        """Scan and redact all matching secret signatures from text."""
        if not text:
            return text

        masked_text = text

        # 1. Regex signature matching
        for secret_type, pattern in self._compiled_patterns.items():
            matches = pattern.findall(masked_text)
            for match in matches:
                self.redacted_secrets_count += 1
                masked_text = masked_text.replace(match, f"[REDACTED_{secret_type}]")

        # 2. Entropy scanning on candidate alphanumeric token blocks (min length 24)
        tokens = re.findall(r"\b[A-Za-z0-9+/=_-]{24,}\b", masked_text)
        for token in tokens:
            if not token.startswith("[REDACTED_"):
                if self.calculate_shannon_entropy(token) >= self.entropy_threshold:
                    self.redacted_secrets_count += 1
                    masked_text = masked_text.replace(token, "[REDACTED_HIGH_ENTROPY_TOKEN]")

        return masked_text
