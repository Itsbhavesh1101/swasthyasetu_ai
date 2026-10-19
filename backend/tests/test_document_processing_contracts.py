"""Pure synthetic document processing-attempt tests."""

import traceback
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from app.modules.documents.processing import (
    AttemptFailureCode,
    AttemptStage,
    AttemptStatus,
    ProcessingAttempt,
    ProcessingGuardCode,
    ProcessingGuardError,
    RetryClassification,
    build_job_intent,
)
from app.shared.types import OpaqueId

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def oid(n: int) -> OpaqueId:
    return OpaqueId(UUID(int=n))


def queued(**changes: object) -> ProcessingAttempt:
    values: dict[str, object] = {
        "attempt_id": oid(1),
        "document_id": oid(2),
        "request_id": oid(3),
        "generation": 1,
        "source_version": "source.v1",
        "routing_version": "routing.v1",
        "idempotency_ref": "idempotency.v1",
        "stage": AttemptStage.QUEUED,
        "status": AttemptStatus.QUEUED,
        "created_at": NOW,
        "deadline_at": NOW + timedelta(seconds=30),
        "started_at": None,
        "completed_at": None,
        "failure_code": None,
        "retry_classification": RetryClassification.NONE,
        "retry_budget": 2,
    }
    values.update(changes)
    return ProcessingAttempt(**values)  # type: ignore[arg-type]


def test_attempt_start_and_completion_are_immutable_and_utc() -> None:
    started = queued().start(at=NOW + timedelta(seconds=1), generation=1)
    assert started.status is AttemptStatus.RUNNING
    assert started.stage is AttemptStage.RECOGNIZING
    done = started.succeed(at=NOW + timedelta(seconds=2), generation=1)
    assert done.status is AttemptStatus.SUCCEEDED
    assert done.completed_at == NOW + timedelta(seconds=2)


@pytest.mark.parametrize(
    "changes",
    [
        {"generation": 0},
        {"request_id": oid(1)},
        {"created_at": datetime(2026, 1, 1)},
        {"deadline_at": NOW},
        {"retry_budget": 4},
        {"source_version": "has space"},
        {"status": AttemptStatus.RUNNING},
    ],
)
def test_direct_constructor_rejects_malformed_state(changes: dict[str, object]) -> None:
    with pytest.raises(ProcessingGuardError):
        queued(**changes)


@pytest.mark.parametrize(
    ("status", "classification"),
    [
        (AttemptStatus.FAILED, RetryClassification.NEEDS_REVIEW),
        (AttemptStatus.NEEDS_REVIEW, RetryClassification.TERMINAL),
        (AttemptStatus.NEEDS_REVIEW, RetryClassification.RETRYABLE),
        (AttemptStatus.CANCELLED, RetryClassification.RETRYABLE),
        (AttemptStatus.CANCELLED, RetryClassification.TERMINAL),
    ],
)
def test_direct_constructor_rejects_contradictory_terminal_classifications(
    status: AttemptStatus, classification: RetryClassification
) -> None:
    with pytest.raises(ProcessingGuardError) as raised:
        queued(
            stage=AttemptStage.COMPLETED,
            status=status,
            started_at=NOW,
            completed_at=NOW + timedelta(seconds=1),
            failure_code=AttemptFailureCode.REFUSED,
            retry_classification=classification,
        )
    assert raised.value.code is ProcessingGuardCode.INVALID_STATE


def test_direct_constructor_rejects_forged_failure_code_without_echo() -> None:
    canary = "private-canary-failure-code"
    with pytest.raises(ProcessingGuardError) as raised:
        queued(
            stage=AttemptStage.COMPLETED,
            status=AttemptStatus.FAILED,
            started_at=NOW,
            completed_at=NOW + timedelta(seconds=1),
            failure_code=canary,
            retry_classification=RetryClassification.TERMINAL,
        )
    assert raised.value.code is ProcessingGuardCode.INVALID_TYPE
    assert canary not in "".join(traceback.format_exception(raised.value))


@pytest.mark.parametrize("generation", [True, 1.0])
@pytest.mark.parametrize("transition", ["start", "succeed", "fail"])
def test_public_transitions_reject_generation_lookalikes(
    generation: object, transition: str
) -> None:
    attempt = queued()
    if transition != "start":
        attempt = attempt.start(at=NOW, generation=1)
    with pytest.raises(ProcessingGuardError) as raised:
        if transition == "start":
            attempt.start(at=NOW, generation=generation)  # type: ignore[arg-type]
        elif transition == "succeed":
            attempt.succeed(at=NOW, generation=generation)  # type: ignore[arg-type]
        else:
            attempt.fail(
                at=NOW,
                generation=generation,  # type: ignore[arg-type]
                code=AttemptFailureCode.REFUSED,
                classification=RetryClassification.TERMINAL,
            )
    assert raised.value.code is ProcessingGuardCode.INVALID_TYPE


def test_direct_constructor_accepts_only_coherent_failed_and_review_states() -> None:
    running = queued().start(at=NOW, generation=1)
    failed = replace(
        running,
        stage=AttemptStage.COMPLETED,
        status=AttemptStatus.FAILED,
        completed_at=NOW + timedelta(seconds=1),
        failure_code=AttemptFailureCode.ENGINE_UNAVAILABLE,
        retry_classification=RetryClassification.RETRYABLE,
    )
    review = replace(
        running,
        stage=AttemptStage.COMPLETED,
        status=AttemptStatus.NEEDS_REVIEW,
        completed_at=NOW + timedelta(seconds=1),
        failure_code=AttemptFailureCode.MALFORMED_RESULT,
        retry_classification=RetryClassification.NEEDS_REVIEW,
    )
    assert failed.status is AttemptStatus.FAILED
    assert review.status is AttemptStatus.NEEDS_REVIEW


def test_stale_generation_terminal_replay_and_deadline_fail_closed() -> None:
    with pytest.raises(ProcessingGuardError) as stale:
        queued().start(at=NOW, generation=2)
    assert stale.value.code is ProcessingGuardCode.STALE_GENERATION
    done = queued().start(at=NOW, generation=1).succeed(at=NOW, generation=1)
    with pytest.raises(ProcessingGuardError):
        done.succeed(at=NOW, generation=1)
    with pytest.raises(ProcessingGuardError):
        queued().start(at=NOW + timedelta(minutes=1), generation=1)


def test_retry_requires_retryable_terminal_failure_and_new_identity() -> None:
    failed = (
        queued()
        .start(at=NOW, generation=1)
        .fail(
            at=NOW + timedelta(seconds=1),
            generation=1,
            code=AttemptFailureCode.ENGINE_UNAVAILABLE,
            classification=RetryClassification.RETRYABLE,
        )
    )
    retried = failed.retry(
        attempt_id=oid(9),
        idempotency_ref="idempotency.v2",
        created_at=NOW + timedelta(seconds=2),
        deadline_at=NOW + timedelta(seconds=20),
    )
    assert retried.generation == 2
    assert retried.retry_budget == 1
    with pytest.raises(ProcessingGuardError):
        failed.retry(
            attempt_id=failed.attempt_id,
            idempotency_ref="idempotency.v2",
            created_at=NOW,
            deadline_at=NOW + timedelta(seconds=3),
        )
    with pytest.raises(ProcessingGuardError):
        failed.retry(
            attempt_id=oid(8),
            idempotency_ref=failed.idempotency_ref,
            created_at=NOW + timedelta(seconds=2),
            deadline_at=NOW + timedelta(seconds=3),
        )
    terminal = (
        queued()
        .start(at=NOW, generation=1)
        .fail(
            at=NOW,
            generation=1,
            code=AttemptFailureCode.REFUSED,
            classification=RetryClassification.TERMINAL,
        )
    )
    with pytest.raises(ProcessingGuardError):
        terminal.retry(
            attempt_id=oid(7),
            idempotency_ref="idempotency.v2",
            created_at=NOW,
            deadline_at=NOW + timedelta(seconds=3),
        )


def test_job_intent_reuses_generic_contract_and_payload_is_content_free() -> None:
    job = build_job_intent(queued(), job_id=oid(20))
    assert str(job.job_type) == "documents.synthetic_process"
    assert set(job.payload) == {"attempt_id", "document_id", "generation", "routing_version"}
    forbidden = ("source", "text", "object", "patient", "url", "token")
    assert not any(word in repr(job.payload).casefold() for word in forbidden)


def test_processing_errors_do_not_echo_identifiers() -> None:
    with pytest.raises(ProcessingGuardError) as raised:
        queued().start(at=NOW, generation=99)
    assert str(oid(1)) not in repr(raised.value)
