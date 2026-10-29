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

        # Negation
        safe_spec = ~composite_violation
        assert safe_spec.is_satisfied_by(t1)
        assert not safe_spec.is_satisfied_by(t2)
