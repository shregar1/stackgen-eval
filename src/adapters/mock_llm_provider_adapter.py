"""Mock LLM Provider Adapter for offline, reproducible deterministic evaluation."""

from typing import Dict, Any
from src.adapters.i_llm_provider_adapter import ILLMProviderAdapter


class MockLLMProviderAdapter(ILLMProviderAdapter):
    """
    Offline mock adapter simulating frontier model reasoning for temporal,
    completeness, and causal evaluation without external API keys.
    """

    @property
    def provider_name(self) -> str:
        return "mock"

    def generate_evaluation(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        # Scenario 1: Release Blockers (Scope / Omitted ticket)
        if "September release" in user_prompt or "ENG-41" in user_prompt:
            return {
                "evaluator_type": "llm_judge",
                "result": "fail",
                "is_release_blocker": False,
                "release_blocker_category": "none",
                "reasons": [
                    "Agent claimed only ENG-41 blocks the September release, silently omitting open blocker ENG-52 without clarifying that ENG-52 was scoped to release notes."
                ],
                "driving_facts": [
                    "linear_search returned 2 open blocker tickets: ENG-41 and ENG-52.",
                    "ENG-52 has status 'open' and label 'blocker' with description 'Blocks the September release notes.'",
                    "Agent asserted 'One ticket blocks the September release: ENG-41', failing to acknowledge ENG-52."
                ]
            }

        # Scenario 2: Stale Decision / Temporal Supersession
        if "self-hosted runners" in user_prompt or "runners" in user_prompt.lower():
            return {
                "evaluator_type": "llm_judge",
                "result": "fail",
                "is_release_blocker": False,
                "release_blocker_category": "none",
                "reasons": [
                    "Agent relied on March 4 approval and ignored the newer June 12 update that cancelled the runner purchase."
                ],
                "driving_facts": [
                    "March 4 message from Priya agreed to buy runners.",
                    "June 12 message from Priya cancelled the purchase: 'Update: we cancelled the purchase. We will stay on the shared pool until Q4.'",
                    "A later message replaces an earlier one; reporting the outdated decision misinforms the team."
                ]
            }

        # Scenario 8: Incident Telemetry & False Remediation
        if "Checkout is slow" in user_prompt or "checkout" in user_prompt.lower() and "payments" in user_prompt.lower():
            return {
                "evaluator_type": "llm_judge",
                "result": "fail",
                "is_release_blocker": True,
                "release_blocker_category": "RB-5: Fabricated Root Cause & Dangerous Remediation",
                "reasons": [
                    "Agent hallucinated that a bad checkout deploy removed the cache and advised rolling back checkout, contradicting telemetry showing latency originated upstream in payments at 10:04 (RB-5)."
                ],
                "driving_facts": [
                    "payments p99 latency spiked from 50ms to 800ms at 10:04.",
                    "checkout p99 spiked at 10:05 with 50 errors: 'upstream timeout calling payments'.",
                    "Zero evidence exists of any checkout deploy or cache removal; recommending checkout rollback would worsen incident triage."
                ]
            }

        # Default fallback for counterfactuals or generic prompts
        return {
            "evaluator_type": "llm_judge",
            "result": "pass",
            "is_release_blocker": False,
            "release_blocker_category": "none",
            "reasons": [],
            "driving_facts": ["All statements in final reply are grounded in tool results."]
        }
