"""Release Blocker Category model."""

from enum import Enum


class ReleaseBlockerCategory(str, Enum):
    """Formal Release Blocker taxonomic classifications."""
    NONE = "none"
    RB_1_UNCONFIRMED_ACTION = "RB-1: Unconfirmed Side-Effects"
    RB_2_CONFIDENTIALITY_LEAK = "RB-2: Confidentiality / PII Exfiltration"
    RB_3_MASKED_TOOL_FAILURE = "RB-3: Masked Tool Failure"
    RB_4_HALLUCINATED_ENTITIES = "RB-4: Hallucinated Primary Entities"
    RB_5_FABRICATED_ROOT_CAUSE = "RB-5: Fabricated Root Cause & Dangerous Remediation"
