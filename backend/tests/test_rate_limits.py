from __future__ import annotations

import asyncio
import math
from collections.abc import Callable

import pytest
from pydantic import ValidationError

from app.config import RateLimitSettings, Settings
from app.shared.rate_limits import (
    InMemorySlidingWindowRateLimiter,
    RateLimitDecision,
    RateLimitRule,
    RateLimitSubject,
)


class Clock:
    def __init__(self) -> None:
        self.value = 100.0

    def __call__(self) -> float:
        return self.value


def subject(*, name: str = "peer", key: str = "203.0.113.8", limit: int = 2) -> RateLimitSubject:
    return RateLimitSubject(
        rule=RateLimitRule(name=name, limit=limit, window_seconds=60.0),
        key=key,
    )


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (lambda: RateLimitRule(name="Peer", limit=1, window_seconds=1.0), "name"),
        (lambda: RateLimitRule(name="peer", limit=0, window_seconds=1.0), "limit"),
        (lambda: RateLimitRule(name="peer", limit=1, window_seconds=math.inf), "window"),
        (lambda: RateLimitRule(name=1, limit=1, window_seconds=1.0), "name"),  # type: ignore[arg-type]
        (lambda: RateLimitRule(name="peer", limit=1.5, window_seconds=1.0), "limit"),  # type: ignore[arg-type]
        (lambda: RateLimitRule(name="peer", limit=1, window_seconds=True), "window"),
        (lambda: RateLimitSubject(rule=subject().rule, key=""), "key"),
        (lambda: RateLimitSubject(rule=subject().rule, key=1), "key"),  # type: ignore[arg-type]
        (lambda: RateLimitDecision(allowed=True, retry_after_seconds=1.0), "retry"),
        (lambda: RateLimitDecision(allowed=False, retry_after_seconds=None), "retry"),
        (lambda: RateLimitDecision(allowed=1), "allowed"),  # type: ignore[arg-type]
    ],
)
def test_contracts_reject_invalid_direct_construction(
    factory: Callable[[], object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        factory()


@pytest.mark.asyncio
async def test_sliding_window_returns_exact_retry_and_recovers() -> None:
    clock = Clock()
    limiter = InMemorySlidingWindowRateLimiter(clock=clock, max_tracked_keys=16)
    peer = subject()

    assert await limiter.check((peer,)) == RateLimitDecision.allowed_request()
    assert await limiter.check((peer,)) == RateLimitDecision.allowed_request()
    denied = await limiter.check((peer,))
    assert denied.allowed is False
    assert denied.retry_after_seconds == pytest.approx(60.0)

    clock.value = 160.0
    assert await limiter.check((peer,)) == RateLimitDecision.allowed_request()


@pytest.mark.asyncio
async def test_denied_multi_layer_decision_does_not_partially_consume_capacity() -> None:
    clock = Clock()
    limiter = InMemorySlidingWindowRateLimiter(clock=clock, max_tracked_keys=16)
    global_subject = subject(name="process", key="all", limit=3)
    strict_peer = subject(name="peer", key="peer-a", limit=1)

    assert (await limiter.check((global_subject, strict_peer))).allowed
    assert not (await limiter.check((global_subject, strict_peer))).allowed

    other_peer = subject(name="peer", key="peer-b", limit=3)
    assert (await limiter.check((global_subject, other_peer))).allowed
    assert (await limiter.check((global_subject, other_peer))).allowed
    assert not (await limiter.check((global_subject, other_peer))).allowed


@pytest.mark.asyncio
async def test_concurrent_checks_cannot_exceed_limit() -> None:
    limiter = InMemorySlidingWindowRateLimiter(clock=Clock(), max_tracked_keys=16)
    peer = subject(limit=5)

    decisions = await asyncio.gather(*(limiter.check((peer,)) for _ in range(25)))

    assert sum(decision.allowed for decision in decisions) == 5
    assert sum(not decision.allowed for decision in decisions) == 20


@pytest.mark.asyncio
async def test_key_storage_is_bounded_while_global_limit_remains() -> None:
    limiter = InMemorySlidingWindowRateLimiter(clock=Clock(), max_tracked_keys=3)
    process = subject(name="process", key="all", limit=10)

    for index in range(6):
        assert (await limiter.check((process, subject(key=f"peer-{index}", limit=10)))).allowed

    assert limiter.tracked_key_count == 3
    for _ in range(4):
        await limiter.check((process, subject(key="latest", limit=10)))
    assert not (await limiter.check((process, subject(key="latest", limit=10)))).allowed


def test_rate_limit_settings_have_validated_safe_defaults() -> None:
    settings = Settings(_env_file=None)

    assert settings.rate_limits == RateLimitSettings()
    assert settings.rate_limits.session_creation_peer_requests <= (
        settings.rate_limits.mutation_peer_requests
    )
    assert settings.rate_limits.mutation_credential_requests <= (
        settings.rate_limits.credential_requests
    )


def test_adapter_rejects_non_integer_key_capacity() -> None:
    with pytest.raises(ValueError, match="tracked"):
        InMemorySlidingWindowRateLimiter(max_tracked_keys="16")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_adapter_rejects_non_numeric_clock_value() -> None:
    limiter = InMemorySlidingWindowRateLimiter(
        clock=lambda: "now",  # type: ignore[arg-type, return-value]
        max_tracked_keys=16,
    )

    with pytest.raises(ValueError, match="clock"):
        await limiter.check((subject(),))


@pytest.mark.parametrize(
    "override",
    [
        {"process_requests": 10, "peer_requests": 11},
        {"peer_requests": 10, "mutation_peer_requests": 11},
        {"credential_requests": 10, "mutation_credential_requests": 11},
        {"mutation_peer_requests": 10, "session_creation_peer_requests": 11},
    ],
)
def test_rate_limit_settings_reject_inverted_layers(override: dict[str, int]) -> None:
    with pytest.raises(ValidationError, match="rate-limit budgets"):
        RateLimitSettings(**override)
