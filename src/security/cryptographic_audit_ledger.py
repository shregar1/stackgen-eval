"""CryptographicAuditLedger ensuring tamper-proof evaluation governance via HMAC-SHA256."""

import hmac
import hashlib
import json
from typing import Any, Dict
from src.models.evaluation_batch_result import EvaluationBatchResult
from src.models.trace_evaluation import TraceEvaluation


class CryptographicAuditLedger:
    """
    Cryptographic Governance & Audit Integrity.
    Signs evaluation results with HMAC-SHA256 digital signatures to prevent
    unauthorized post-hoc tampering in CI/CD release gate pipelines.
    """

    DEFAULT_SALT: str = "stackgen-enterprise-governance-salt-v1"

    def __init__(self, secret_key: str = DEFAULT_SALT):
        self.secret_key: bytes = secret_key.encode("utf-8")

    def _canonicalize_dict(self, data: Dict[str, Any]) -> str:
        """Create a deterministic sorted JSON representation for consistent hashing."""
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def sign_evaluation(self, evaluation: TraceEvaluation) -> str:
        """Compute HMAC-SHA256 signature for a single trace evaluation."""
        payload = self._canonicalize_dict(evaluation.model_dump())
        return hmac.new(self.secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def sign_batch(self, batch_result: EvaluationBatchResult) -> str:
        """Compute HMAC-SHA256 signature for an entire batch result."""
        payload = self._canonicalize_dict(batch_result.to_spec_dict())
        return hmac.new(self.secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()

    def verify_batch_signature(self, batch_result: EvaluationBatchResult, expected_signature: str) -> bool:
        """Verify that the batch result matches its expected digital signature."""
        computed = self.sign_batch(batch_result)
        return hmac.compare_digest(computed, expected_signature)
