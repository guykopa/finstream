from collections import deque
from datetime import datetime, timedelta, timezone


class RateLimiter:
    """Sliding-window in-memory rate limiter.

    Tracks request timestamps per client. Requests older than the window
    are discarded on every check, so the counter stays accurate over time.
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self._max = max_requests
        self._window = timedelta(seconds=window_seconds)
        self._buckets: dict[str, deque[datetime]] = {}

    def is_allowed(self, client_id: str) -> bool:
        """Return True and record the request if the client is within limits.

        Args:
            client_id: Unique identifier for the client (IP, user id, etc.).

        Returns:
            True if the request is allowed, False if rate-limited.
        """
        now = datetime.now(tz=timezone.utc)
        cutoff = now - self._window

        bucket = self._buckets.setdefault(client_id, deque())

        while bucket and bucket[0] < cutoff:
            bucket.popleft()

        if len(bucket) >= self._max:
            return False

        bucket.append(now)
        return True

    def remaining(self, client_id: str) -> int:
        """Return the number of requests the client can still make in this window.

        Args:
            client_id: Unique identifier for the client.

        Returns:
            Remaining allowed requests. Never negative.
        """
        now = datetime.now(tz=timezone.utc)
        cutoff = now - self._window
        bucket = self._buckets.get(client_id, deque())
        active = sum(1 for ts in bucket if ts >= cutoff)
        return max(0, self._max - active)
