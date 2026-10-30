"""Circuit Breaker Pattern: Protects evaluation pipeline from cascading outages and hung API endpoints."""

import time
from typing import Callable, Any
from src.resilience.circuit_state import CircuitState
from src.resilience.circuit_breaker_open_exception import CircuitBreakerOpenException


class CircuitBreaker:
    """
    Monitors operations for failures and short-circuits execution when failure threshold is reached.

    - CLOSED: Normal operation; failures increment failure counter.
    - OPEN: If failures >= failure_threshold, state flips to OPEN and requests fail fast.
    - HALF-OPEN: After reset_timeout seconds, allows a probe call to check if service recovered.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_threshold: int = 2,
        reset_timeout_seconds: float = 5.0
    ):
        self.failure_threshold = failure_threshold
        self.recovery_threshold = recovery_threshold
        self.reset_timeout_seconds = reset_timeout_seconds

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_state_change = time.time()

    @property
    def state(self) -> CircuitState:
        """Evaluate and return the current state, checking for timeout transition."""
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_state_change >= self.reset_timeout_seconds:
                self._transition_to(CircuitState.HALF_OPEN)
        return self._state

    def _transition_to(self, new_state: CircuitState) -> None:
        self._state = new_state
        self._last_state_change = time.time()
        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._success_count = 0

    def call(self, operation: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Execute operation through circuit breaker protection."""
        current_state = self.state

        if current_state == CircuitState.OPEN:
            raise CircuitBreakerOpenException(
                f"Circuit breaker is OPEN. Fast-failing operation to protect pipeline."
            )

        try:
            result = operation(*args, **kwargs)
            self._on_success()
            return result
        except Exception as exc:
            self._on_failure()
            raise exc

    def _on_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.recovery_threshold:
                self._transition_to(CircuitState.CLOSED)
        elif self._state == CircuitState.CLOSED:
            self._failure_count = 0

    def _on_failure(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)
        elif self._state == CircuitState.CLOSED:
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)
