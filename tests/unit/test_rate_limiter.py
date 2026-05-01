import pytest

from finstream.api.security.rate_limiter import RateLimiter


class TestRateLimiter:
    """Unit tests for RateLimiter."""

    def test_first_request_is_allowed(self) -> None:
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        assert limiter.is_allowed("client-1") is True

    def test_requests_within_limit_are_allowed(self) -> None:
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        assert limiter.is_allowed("client-1") is True
        assert limiter.is_allowed("client-1") is True
        assert limiter.is_allowed("client-1") is True

    def test_request_exceeding_limit_is_blocked(self) -> None:
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.is_allowed("client-1")
        limiter.is_allowed("client-1")
        assert limiter.is_allowed("client-1") is False

    def test_different_clients_are_independent(self) -> None:
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        limiter.is_allowed("client-1")
        assert limiter.is_allowed("client-1") is False
        assert limiter.is_allowed("client-2") is True

    def test_expired_requests_are_not_counted(self) -> None:
        limiter = RateLimiter(max_requests=1, window_seconds=1)
        limiter.is_allowed("client-1")
        import time; time.sleep(1.1)
        assert limiter.is_allowed("client-1") is True

    def test_remaining_returns_correct_count(self) -> None:
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        limiter.is_allowed("client-1")
        limiter.is_allowed("client-1")
        assert limiter.remaining("client-1") == 3
