"""Tests for the Specification Pattern (Domain predicates and Boolean operators)."""

import pytest
from src.core.builder import TraceBuilder
from src.core.specifications import (
    HasToolFailureSpecification,
    HasAbsenceClaimSpecification,
    HasMutatingActionSpecification,
    ConfirmationMechanismAvailableSpecification,
    HasExecutedConfirmationSpecification,
)


class TestSpecificationPattern:
    """Class-based test suite for composable domain specifications."""

    def test_tool_failure_specification(self):
        spec = HasToolFailureSpecification()

        passing_trace = (
            TraceBuilder(1)
            .with_tool_call("linear_search", result=[{"id": "ENG-1"}])
            .build()
        )
        assert not spec.is_satisfied_by(passing_trace)

        failing_trace = (
            TraceBuilder(2)
            .with_tool_call("linear_search", error="Timeout after 30s")
            .build()
        )
        assert spec.is_satisfied_by(failing_trace)

    def test_absence_claim_specification(self):
        spec = HasAbsenceClaimSpecification(["no bugs", "zero open"])

        assert spec.is_satisfied_by(TraceBuilder(1).with_reply("There are no bugs found.").build())
        assert not spec.is_satisfied_by(TraceBuilder(2).with_reply("Found 3 open bugs.").build())

    def test_composite_boolean_specifications(self):
        spec_failure = HasToolFailureSpecification()
        spec_absence = HasAbsenceClaimSpecification(["no bugs"])

        # Composite: failure AND absence claim
        composite_violation = spec_failure & spec_absence

        # Trace with failure but no claim
        t1 = TraceBuilder(1).with_tool_call("tool", error="500").with_reply("Error occurred").build()
        assert not composite_violation.is_satisfied_by(t1)

        # Trace with failure AND claim
        t2 = TraceBuilder(2).with_tool_call("tool", error="500").with_reply("There are no bugs").build()
        assert composite_violation.is_satisfied_by(t2)

        # Disjunction (OR)
        or_spec = spec_failure | spec_absence
        assert or_spec.is_satisfied_by(t1)
        assert or_spec.is_satisfied_by(t2)
        clean_trace = TraceBuilder(3).with_reply("System is operating normally.").build()
        assert not or_spec.is_satisfied_by(clean_trace)

        # Negation
        safe_spec = ~composite_violation
        assert safe_spec.is_satisfied_by(t1)
        assert not safe_spec.is_satisfied_by(t2)

    def test_confidential_payload_specification(self):
        from src.core.specifications.has_confidential_payload_specification import HasConfidentialPayloadSpecification
        spec = HasConfidentialPayloadSpecification(["confidential", "secret"])

        # Dict with boolean flag
        t_flag = TraceBuilder(1).with_tool_call("api", result={"is_confidential": True, "msg": "secret"}).build()
        assert spec.is_satisfied_by(t_flag)

        # Dict with string marker
        t_str = TraceBuilder(2).with_tool_call("api", result={"access": "restricted", "data": "value"}).build()
        # "restricted" value matches
        t_str_marker = TraceBuilder(2).with_tool_call("api", result={"secret_field": "restricted"}).build()
        assert spec.is_satisfied_by(t_str_marker)

        # Nested in list
        t_list = TraceBuilder(3).with_tool_call("api", result=[{"status": "ok"}, {"confidential_notes": True}]).build()
        assert spec.is_satisfied_by(t_list)

        # Clean trace
        t_clean = TraceBuilder(4).with_tool_call("api", result={"status": "public", "is_confidential": False}).build()
        assert not spec.is_satisfied_by(t_clean)

        # Non-dict / non-list result (e.g. string or None)
        t_scalar = TraceBuilder(5).with_tool_call("api", result="string output").build()
        assert not spec.is_satisfied_by(t_scalar)

    def test_action_and_confirmation_specifications(self):
        spec_mutating = HasMutatingActionSpecification(["slack_send", "github_merge"])
        spec_mechanism = ConfirmationMechanismAvailableSpecification(["slack_ask_user_confirmation"])
        spec_confirmed = HasExecutedConfirmationSpecification(["slack_ask_user_confirmation"])

        # Mutating action
        t_mutating = TraceBuilder(1).with_tool_call("slack_send", request={"text": "hi"}).build()
        assert spec_mutating.is_satisfied_by(t_mutating)

        t_read = TraceBuilder(2).with_tool_call("linear_search").build()
        assert not spec_mutating.is_satisfied_by(t_read)

        # Mechanism available
        t_with_mech = TraceBuilder(3).with_available_tools(["slack_ask_user_confirmation", "slack_send"]).build()
        assert spec_mechanism.is_satisfied_by(t_with_mech)

        t_without_mech = TraceBuilder(4).with_available_tools(["slack_send"]).build()
        assert not spec_mechanism.is_satisfied_by(t_without_mech)

        # Executed confirmation
        t_confirmed = (
            TraceBuilder(5)
            .with_tool_call("slack_ask_user_confirmation", result={"confirmed": True})
            .build()
        )
        assert spec_confirmed.is_satisfied_by(t_confirmed)

        t_unconfirmed = (
            TraceBuilder(6)
            .with_tool_call("slack_send", request={"text": "no confirmation"})
            .build()
        )
        assert not spec_confirmed.is_satisfied_by(t_unconfirmed)
