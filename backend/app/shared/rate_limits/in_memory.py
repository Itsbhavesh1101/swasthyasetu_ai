"""Bounded process-local sliding-window rate limiter."""

from __future__ import annotations

import asyncio
import math
from collections import OrderedDict, deque
from collections.abc import Callable, Sequence
from time import monotonic

from app.shared.rate_limits.contracts import (
    RateLimitDecision,
    RateLimitSubject,
)


class InMemorySlidingWindowRateLimiter:
    """Apply layered limits atomically inside one application process."""

    def __init__(
        self,
        *,
        clock: Callable[[], float] = monotonic,
        max_tracked_keys: int = 10_000,
    ) -> None:
        if (
            not isinstance(max_tracked_keys, int)
            or isinstance(max_tracked_keys, bool)
            or max_tracked_keys <= 0
        ):
            raise ValueError("max tracked rate-limit keys must be positive")
        self._clock = clock
        self._max_tracked_keys = max_tracked_keys
        self._buckets: OrderedDict[str, deque[float]] = OrderedDict()
        self._lock = asyncio.Lock()

    @property
    def tracked_key_count(self) -> int:
        return len(self._buckets)

    async def check(self, subjects: Sequence[RateLimitSubject]) -> RateLimitDecision:
        unique = self._unique_subjects(subjects)
        if not unique:
            return RateLimitDecision.allowed_request()

        now = self._clock()
        if not isinstance(now, (int, float)) or isinstance(now, bool) or not math.isfinite(now):
            raise ValueError("rate-limit clock must return a finite value")

        async with self._lock:
            retries: list[float] = []
            for item in unique:
                bucket = self._buckets.get(item.storage_key)
                if bucket is None:
                    continue
                self._prune(bucket, threshold=now - item.rule.window_seconds)
                self._buckets.move_to_end(item.storage_key)
                if len(bucket) >= item.rule.limit:
                    retries.append(bucket[0] + item.rule.window_seconds - now)

            if retries:
                return RateLimitDecision.denied_request(max(retries))

            self._make_capacity(unique)
            for item in unique:
                bucket = self._buckets.setdefault(item.storage_key, deque())
                bucket.append(now)
                self._buckets.move_to_end(item.storage_key)
            return RateLimitDecision.allowed_request()

    @staticmethod
    def _unique_subjects(subjects: Sequence[RateLimitSubject]) -> tuple[RateLimitSubject, ...]:
        by_key: dict[str, RateLimitSubject] = {}
        for item in subjects:
            previous = by_key.get(item.storage_key)
            if previous is not None and previous.rule != item.rule:
                raise ValueError("duplicate rate-limit subject has conflicting rules")
            by_key[item.storage_key] = item
        return tuple(by_key.values())

    @staticmethod
    def _prune(bucket: deque[float], *, threshold: float) -> None:
        while bucket and bucket[0] <= threshold:
            bucket.popleft()

    def _make_capacity(self, subjects: Sequence[RateLimitSubject]) -> None:
        requested = {item.storage_key for item in subjects}
        new_count = sum(key not in self._buckets for key in requested)
        if new_count > self._max_tracked_keys:
            raise ValueError("request requires more rate-limit keys than configured capacity")

        while len(self._buckets) + new_count > self._max_tracked_keys:
            eviction = next((key for key in self._buckets if key not in requested), None)
            if eviction is None:
                raise RuntimeError("rate-limit key capacity cannot preserve active request layers")
            del self._buckets[eviction]
