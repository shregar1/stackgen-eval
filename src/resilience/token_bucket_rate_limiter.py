"""Token Bucket Rate Limiter for traffic shaping and API quota protection."""

import time
import threading
from typing import Optional


class TokenBucketRateLimiter:
    """
    Token Bucket Rate Limiter providing smooth traffic shaping and quota enforcement
    for external frontier LLM APIs (OpenAI/Anthropic) to prevent HTTP 429 errors.
    """

    def __init__(self, requests_per_minute: float = 60.0, burst_capacity: Optional[int] = None):
        self.capacity: float = float(burst_capacity or max(1, int(requests_per_minute / 6.0)))
        self.refill_rate: float = requests_per_minute / 60.0  # tokens per second
        self.tokens: float = self.capacity
        self.last_refill_time: float = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        """Calculate newly accumulated tokens based on elapsed monotonic time."""
        now = time.monotonic()
        elapsed = now - self.last_refill_time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill_time = now

    def acquire(self, tokens: int = 1) -> bool:
        """Attempt to immediately consume tokens without blocking. Returns True if granted."""
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_and_acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """Wait until enough tokens are available or timeout expires."""
        start_time = time.monotonic()
        while True:
            with self._lock:
                self._refill()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return True

                missing = tokens - self.tokens
                wait_time = missing / self.refill_rate

            if timeout is not None:
                elapsed = time.monotonic() - start_time
                if elapsed + wait_time > timeout:
                    return False

            time.sleep(min(wait_time, 0.05))
