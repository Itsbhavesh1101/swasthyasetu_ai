from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta, timezone
from typing import Any, cast

import pytest

from app.modules.mental_health.contracts import (
    MentalHealthContractCode,
    MentalHealthContractError,
    SyntheticArtifactReference,
    SyntheticExtractionFailure,
    SyntheticExtractionFailureCode,
    SyntheticExtractionRequest,
    SyntheticExtractionResult,
    SyntheticExtractionStatus,
    SyntheticSignalCode,
    SyntheticSignalObservation,
    SyntheticSignalState,
    parse_synthetic_extraction_result,
    validate_synthetic_result_binding,
)
from app.modules.mental_health.ports import SyntheticSignalExtractorPort

NOW = datetime(2026, 10, 31, 15, 0, tzinfo=UTC)
HASH_A = "a" * 64
HASH_B = "b" * 64


def artifact(
    *,
    artifact_id: str = "syn_mh_input_fixture_alpha",
    content_hash: str = HASH_A,
    created_at: datetime = NOW,
) -> SyntheticArtifactReference:
    return SyntheticArtifactReference(
        artifact_id=artifact_id,
        artifact_version="engineering.v1",
        content_hash=content_hash,
        created_at=created_at,
    )


def schema() -> SyntheticArtifactReference:
    return artifact(
        artifact_id="syn_mh_schema_fixture",
        content_hash=HASH_B,
        created_at=NOW,
    )


def request() -> SyntheticExtractionRequest:
    return SyntheticExtractionRequest(
        request_id="syn_mh_request_alpha",
        input_artifact=artifact(),
        schema_artifact=schema(),
        created_at=NOW + timedelta(seconds=1),
        deadline_at=NOW + timedelta(seconds=10),
    )


def payload(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "contract_version": "synthetic-mh-signal-result.v1",
        "result_id": "syn_mh_result_alpha",
        "request_id": "syn_mh_request_alpha",
        "input_artifact_id": "syn_mh_input_fixture_alpha",
        "input_artifact_version": "engineering.v1",
        "input_artifact_hash": HASH_A,
        "schema_artifact_id": "syn_mh_schema_fixture",
        "schema_artifact_version": "engineering.v1",
        "schema_artifact_hash": HASH_B,
        "status": "SYNTHETIC_PARSED",
        "signals": [
            {"code": "SYN_MH_SIGNAL_ALPHA", "state": "PRESENT"},
            {"code": "SYN_MH_SIGNAL_BETA", "state": "UNKNOWN"},
        ],
        "completed_at": "2026-10-31T15:00:02Z",
    }
    value.update(overrides)
    return value


def parsed_result() -> SyntheticExtractionResult:
    return parse_synthetic_extraction_result(payload())


def test_parses_only_content_free_synthetic_signal_tokens() -> None:
    result = parsed_result()

    assert result.status is SyntheticExtractionStatus.SYNTHETIC_PARSED
    assert tuple(item.code for item in result.signals) == (
        SyntheticSignalCode.ALPHA,
        SyntheticSignalCode.BETA,
    )
    assert result.signals[0].state is SyntheticSignalState.PRESENT
    assert result.completed_at == NOW + timedelta(seconds=2)
    with pytest.raises(FrozenInstanceError):
        result.status = SyntheticExtractionStatus.SYNTHETIC_ABSTAINED  # type: ignore[misc]


def test_request_and_result_bind_exact_artifact_identity_and_chronology() -> None:
    validated = validate_synthetic_result_binding(request(), parsed_result())
    assert validated == parsed_result()

    for changed in (
        replace(parsed_result(), request_id="syn_mh_request_beta"),
        replace(parsed_result(), input_artifact_hash="c" * 64),
        replace(parsed_result(), schema_artifact_version="engineering.v2"),
    ):
        with pytest.raises(MentalHealthContractError) as raised:
            validate_synthetic_result_binding(request(), changed)
        assert raised.value.code is MentalHealthContractCode.IDENTITY_MISMATCH


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("route", "ROUTE_C"),
        ("patient_id", "patient-canary"),
        ("session_id", "session-canary"),
        ("text", "sensitive narrative canary"),
        ("score", 9),
        ("confidence", 0.99),
        ("risk", "HIGH"),
        ("diagnosis", "canary"),
    ],
)
def test_parser_rejects_authority_or_content_fields_without_echo(field: str, value: object) -> None:
    candidate = payload(**{field: value})
    with pytest.raises(MentalHealthContractError) as raised:
        parse_synthetic_extraction_result(candidate)
    assert raised.value.code is MentalHealthContractCode.UNKNOWN_FIELD
    assert "canary" not in str(raised.value)


@pytest.mark.parametrize(
    "signals",
    [
        [{"code": "SUICIDE_RISK", "state": "PRESENT"}],
        [{"code": "SYN_MH_SIGNAL_CRISIS", "state": "PRESENT"}],
        [{"code": "SYN_MH_SIGNAL_ALPHA", "state": "HIGH"}],
        [{"code": "SYN_MH_SIGNAL_ALPHA", "state": "PRESENT", "score": 1}],
        [
            {"code": "SYN_MH_SIGNAL_BETA", "state": "UNKNOWN"},
            {"code": "SYN_MH_SIGNAL_ALPHA", "state": "PRESENT"},
        ],
        [{"code": "SYN_MH_SIGNAL_ALPHA", "state": "PRESENT"}] * 2,
        "SYN_MH_SIGNAL_ALPHA",
    ],
)
def test_parser_rejects_clinical_noncanonical_or_duplicate_signals(signals: object) -> None:
    with pytest.raises(MentalHealthContractError):
        parse_synthetic_extraction_result(payload(signals=signals))


def test_abstained_result_must_be_empty_and_parsed_result_must_not_be_empty() -> None:
    abstained = parse_synthetic_extraction_result(payload(status="SYNTHETIC_ABSTAINED", signals=[]))
    assert abstained.status is SyntheticExtractionStatus.SYNTHETIC_ABSTAINED
    assert abstained.signals == ()

    with pytest.raises(MentalHealthContractError):
        parse_synthetic_extraction_result(payload(signals=[]))
    with pytest.raises(MentalHealthContractError):
        parse_synthetic_extraction_result(
            payload(
                status="SYNTHETIC_ABSTAINED",
                signals=[{"code": "SYN_MH_SIGNAL_ALPHA", "state": "UNKNOWN"}],
            )
        )


@pytest.mark.parametrize(
    "completed_at",
    [
        "2026-10-31T20:30:02+05:30",
        "2026-10-31T15:00:02",
        "2026-02-30T15:00:02Z",
        "2026-10-31T15:00:02.1234Z",
        1,
    ],
)
def test_parser_rejects_noncanonical_or_invalid_utc(completed_at: object) -> None:
    with pytest.raises(MentalHealthContractError):
        parse_synthetic_extraction_result(payload(completed_at=completed_at))


def test_request_rejects_naive_clocks_and_normalizes_aware_non_utc() -> None:
    with pytest.raises(MentalHealthContractError):
        replace(request(), created_at=datetime(2026, 10, 31, 15, 0, 1))

    offset = timezone(timedelta(hours=5, minutes=30))
    normalized = replace(
        request(),
        created_at=(NOW + timedelta(seconds=1)).astimezone(offset),
        deadline_at=(NOW + timedelta(seconds=10)).astimezone(offset),
    )
    assert normalized.created_at.tzinfo is UTC
    assert normalized.deadline_at.tzinfo is UTC


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("artifact_id", "syn_mh_input_fixture_patient"),
        ("artifact_id", "patient-123"),
        ("artifact_version", "production.v1"),
        ("artifact_version", "latest"),
        ("content_hash", "not-a-hash"),
    ],
)
def test_artifact_rejects_semantic_or_nonengineering_identity(field: str, value: object) -> None:
    values: dict[str, object] = {
        "artifact_id": "syn_mh_input_fixture_alpha",
        "artifact_version": "engineering.v1",
        "content_hash": HASH_A,
        "created_at": NOW,
    }
    values[field] = value
    with pytest.raises(MentalHealthContractError):
        SyntheticArtifactReference(**cast(Any, values))


def test_result_must_complete_within_request_window() -> None:
    with pytest.raises(MentalHealthContractError) as early:
        validate_synthetic_result_binding(request(), replace(parsed_result(), completed_at=NOW))
    assert early.value.code is MentalHealthContractCode.INVALID_CHRONOLOGY

    with pytest.raises(MentalHealthContractError) as late:
        validate_synthetic_result_binding(
            request(), replace(parsed_result(), completed_at=NOW + timedelta(seconds=11))
        )
    assert late.value.code is MentalHealthContractCode.INVALID_CHRONOLOGY


def test_failure_contract_is_content_free_and_timeout_obeys_deadline() -> None:
    timeout = SyntheticExtractionFailure(
        failure_id="syn_mh_failure_alpha",
        request_id=request().request_id,
        code=SyntheticExtractionFailureCode.SIMULATED_TIMEOUT,
        occurred_at=request().deadline_at,
    )
    assert timeout.code is SyntheticExtractionFailureCode.SIMULATED_TIMEOUT
    assert not hasattr(timeout, "message")
    assert not hasattr(timeout, "route")

    with pytest.raises(MentalHealthContractError):
        replace(timeout, occurred_at=request().deadline_at - timedelta(seconds=1)).validate_for(
            request()
        )
    assert timeout.validate_for(request()) == timeout


def test_direct_constructors_reject_wrong_types_and_forbidden_fields() -> None:
    with pytest.raises(MentalHealthContractError):
        SyntheticSignalObservation(
            code=cast(Any, "SYN_MH_SIGNAL_ALPHA"),
            state=SyntheticSignalState.PRESENT,
        )
    with pytest.raises(TypeError):
        cast(Any, SyntheticExtractionRequest)(
            request_id="syn_mh_request_alpha",
            input_artifact=artifact(),
            schema_artifact=schema(),
            created_at=NOW + timedelta(seconds=1),
            deadline_at=NOW + timedelta(seconds=10),
            patient_id="canary",
        )


def test_forced_nested_mutation_is_revalidated_at_binding_boundary() -> None:
    result = parsed_result()
    hostile = result.signals[0]
    object.__setattr__(hostile, "code", "SYN_MH_SIGNAL_CRISIS")
    object.__setattr__(result, "signals", (hostile, result.signals[1]))

    with pytest.raises(MentalHealthContractError):
        validate_synthetic_result_binding(request(), result)


def test_hostile_mapping_is_contained_by_content_free_error() -> None:
    canary = "sensitive-payload-canary"

    class Hostile(dict[str, object]):
        def keys(self) -> Any:
            raise RuntimeError(canary)

    with pytest.raises(MentalHealthContractError) as raised:
        parse_synthetic_extraction_result(Hostile())
    assert canary not in str(raised.value)


def test_provider_neutral_port_has_no_route_or_runtime_adapter() -> None:
    import app.modules.mental_health.ports as ports

    class FixtureExtractor:
        async def extract(
            self, extraction_request: SyntheticExtractionRequest
        ) -> SyntheticExtractionResult:
            return validate_synthetic_result_binding(extraction_request, parsed_result())

    assert isinstance(FixtureExtractor(), SyntheticSignalExtractorPort)
    for forbidden in ("DefaultExtractor", "OpenAIExtractor", "route", "triage", "backstop"):
        assert not hasattr(ports, forbidden)
