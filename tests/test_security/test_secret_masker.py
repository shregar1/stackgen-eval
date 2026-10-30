"""Unit tests for HighEntropySecretMasker."""

import pytest
from src.security.high_entropy_secret_masker import HighEntropySecretMasker


class TestSecretMasker:
    """Class-based test suite verifying regex signature redaction and Shannon entropy secret detection."""

    def test_masks_known_api_keys_and_tokens(self):
        masker = HighEntropySecretMasker()
        fake_aws = "AKIA" + "00000000EXAMPLE0"
        fake_ghp = "ghp_" + "000000000000000000000000000000000000"
        fake_slack = "xoxb-" + "0000000000-" + "0000000000-" + "000000000000000000000000"
        text = (
            f"AWS Key: {fake_aws}\n"
            f"GitHub: {fake_ghp}\n"
            f"Slack: {fake_slack}\n"
            "Normal text without secrets."
        )

        masked = masker.mask_secrets(text)

        assert fake_aws not in masked
        assert "[REDACTED_AWS_KEY]" in masked
        assert fake_ghp not in masked
        assert "[REDACTED_GITHUB_PAT]" in masked
        assert "[REDACTED_SLACK_TOKEN]" in masked
        assert "Normal text without secrets." in masked
        assert masker.redacted_secrets_count >= 3

    def test_shannon_entropy_calculation(self):
        # Low entropy: repetitive characters
        low_entropy = HighEntropySecretMasker.calculate_shannon_entropy("aaaaaaaaaaaaaaaaaaaaaaaa")
        assert low_entropy == 0.0

        # High entropy: pseudo-random base64 key
        high_entropy = HighEntropySecretMasker.calculate_shannon_entropy("dGhpcy1pcy1hLXNlY3JldC1rZXktZXhhbXBsZQ==")
        assert high_entropy > 4.0

    def test_masks_high_entropy_secret_string(self):
        masker = HighEntropySecretMasker(entropy_threshold=3.5)
        text = "Secret token: 9xK7zL2pQ8mR4wV1tY6nB3cE"  # High entropy random string (len 24)
        masked = masker.mask_secrets(text)
        assert "9xK7zL2pQ8mR4wV1tY6nB3cE" not in masked
        assert "[REDACTED_" in masked

    def test_empty_inputs(self):
        masker = HighEntropySecretMasker()
        assert masker.mask_secrets("") == ""
        assert masker.mask_secrets(None) is None
        assert HighEntropySecretMasker.calculate_shannon_entropy("") == 0.0
