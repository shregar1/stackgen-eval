"""Circuit Breaker state enumeration."""

from enum import Enum


class CircuitState(str, Enum):
    """Lifecycle states of the Circuit Breaker."""
    CLOSED = "closed"        # Normal execution; calls pass through
    OPEN = "open"            # Failing; calls fast-fail immediately
    HALF_OPEN = "half_open"  # Probing recovery with limited canary calls
