"""Unit tests for the Circuit Breaker Pattern."""

import pytest
from src.resilience.circuit_state import CircuitState
from src.resilience.circuit_breaker import CircuitBreaker
from src.resilience.circuit_breaker_open_exception import CircuitBreakerOpenException


class TestCircuitBreaker:
    """Class-based test suite for CircuitBreaker."""

    def test_initial_state_closed(self):
        cb = CircuitBreaker(failure_threshold=2)
        assert cb.state == CircuitState.CLOSED

    def test_transitions_to_open_after_threshold_failures(self):
        cb = CircuitBreaker(failure_threshold=2, reset_timeout_seconds=10.0)

        class FailingOperation:
            def execute(self):
                raise ConnectionError("Upstream timeout")

        op = FailingOperation()

        with pytest.raises(ConnectionError):
            cb.call(op.execute)
        assert cb.state == CircuitState.CLOSED

        with pytest.raises(ConnectionError):
            cb.call(op.execute)
        # Should now be OPEN
        assert cb.state == CircuitState.OPEN

        # Subsequent call should fast-fail with CircuitBreakerOpenException
        with pytest.raises(CircuitBreakerOpenException):
            cb.call(op.execute)

    def test_recovery_cycle_half_open_to_closed(self):
        # Very short timeout for testing
        cb = CircuitBreaker(failure_threshold=1, recovery_threshold=1, reset_timeout_seconds=0.01)

        class FlakyOperation:
            def __init__(self):
                self.should_fail = True

            def execute(self):
                if self.should_fail:
                    raise RuntimeError("Downstream 500")
                return "SUCCESS"

        op = FlakyOperation()

        # Trigger failure
        with pytest.raises(RuntimeError):
            cb.call(op.execute)
        assert cb._state == CircuitState.OPEN

        # Wait for timeout to elapse
        import time
        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN

        # Successful probe call in HALF_OPEN recovers circuit to CLOSED
        op.should_fail = False
        res = cb.call(op.execute)
        assert res == "SUCCESS"
        assert cb.state == CircuitState.CLOSED

    def test_half_open_failure_reopens_circuit(self):
        import time
        cb = CircuitBreaker(failure_threshold=1, recovery_threshold=2, reset_timeout_seconds=0.01)

        def raise_err():
            raise RuntimeError("failure")

        with pytest.raises(RuntimeError):
            cb.call(raise_err)
        assert cb._state == CircuitState.OPEN

        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN

        with pytest.raises(RuntimeError):
            cb.call(raise_err)
        assert cb._state == CircuitState.OPEN
