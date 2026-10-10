"""Minimal actor-context contract tests."""

from dataclasses import FrozenInstanceError

import pytest

from app.shared.security import ActorContext


def test_unknown_actor_context_is_safe_and_has_no_roles() -> None:
    actor = ActorContext()

    assert actor.actor_id is None
    assert actor.session_id is None
    assert actor.request_id is None
    assert actor.is_authenticated is False
    assert not hasattr(actor, "roles")


def test_actor_context_is_immutable() -> None:
    actor = ActorContext()

    with pytest.raises(FrozenInstanceError):
        actor.is_authenticated = True  # type: ignore[misc]
