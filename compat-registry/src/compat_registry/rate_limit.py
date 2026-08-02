"""Minimal per-IP rate limiter for the open, unauthenticated POST /submissions
endpoint. In-memory and single-process by design -- this is the abuse control
appropriate for a low-write MVP; it is explicitly the first thing to swap for
a shared store (e.g. Redis) if the service is ever run with multiple
processes/instances.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


class RateLimiter:
    def __init__(self, max_per_minute: int):
        self.max_per_minute = max_per_minute
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, client_ip: str) -> None:
        now = time.monotonic()
        window_start = now - 60
        hits = self._hits[client_ip]

        while hits and hits[0] < window_start:
            hits.popleft()

        if len(hits) >= self.max_per_minute:
            raise HTTPException(status_code=429, detail="Too many submissions, slow down.")

        hits.append(now)


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
