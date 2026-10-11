"""Minimal actor-context contract tests."""

from dataclasses import FrozenInstanceError

import pytest

from app.shared.security import ActorContext


def test_unknown_actor_context_is_safe_and_has_least_privilege_roles() -> None:
    actor = ActorContext()

    assert actor.actor_id is None
    assert actor.session_id is None
    assert actor.request_id is None
    assert actor.is_authenticated is False
    assert actor.roles == frozenset()
    assert actor.mfa_verified is False


def test_actor_context_is_immutable() -> None:
    actor = ActorContext()

    with pytest.raises(FrozenInstanceError):
        actor.is_authenticated = True  # type: ignore[misc]
