"""Circuit Breaker open state exception."""


class CircuitBreakerOpenException(Exception):
    """Raised when an operation is attempted while the Circuit Breaker is in OPEN state."""
    pass
