"""Unit tests for TokenBucketRateLimiter."""

import time
import pytest
from src.resilience.token_bucket_rate_limiter import TokenBucketRateLimiter


class TestRateLimiter:
    """Class-based test suite verifying token bucket rate limiter and bursting control."""

    def test_immediate_acquire_within_burst_capacity(self):
        limiter = TokenBucketRateLimiter(requests_per_minute=600.0, burst_capacity=5)
        # Should allow 5 immediate token acquisitions
        for _ in range(5):
            assert limiter.acquire(1) is True
        # 6th should fail immediately without blocking
        assert limiter.acquire(1) is False

    def test_tokens_refill_over_time(self):
        # 120 RPM = 2 tokens per second
        limiter = TokenBucketRateLimiter(requests_per_minute=120.0, burst_capacity=2)
        assert limiter.acquire(2) is True
        assert limiter.acquire(1) is False

        # Sleep 0.6 seconds -> should accumulate at least 1 token
        time.sleep(0.6)
        assert limiter.acquire(1) is True

    def test_wait_and_acquire_timeout(self):
        # Very low refill rate: 6 RPM = 0.1 tokens/sec
        limiter = TokenBucketRateLimiter(requests_per_minute=6.0, burst_capacity=1)
        assert limiter.acquire(1) is True

        # Waiting 0.05 seconds with 0.1 token/sec refill will time out
        granted = limiter.wait_and_acquire(tokens=1, timeout=0.05)
        assert granted is False
