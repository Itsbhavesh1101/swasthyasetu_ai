"""Pure mechanics for detached engineering-synthetic P23 journey evidence."""

from __future__ import annotations

from datetime import datetime

from app.config import Environment
from app.validation.contracts import (
    JourneyEvidenceContractCode,
    JourneyEvidenceContractError,
    SyntheticEvidenceDisposition,
    SyntheticEvidenceReason,
    SyntheticJourneyDefinition,
    SyntheticJourneyEvidenceReceipt,
    SyntheticJourneyManifest,
    SyntheticJourneyObservation,
    SyntheticJourneyReadiness,
    snapshot_journey_definition,
    snapshot_journey_observation,
)

_PROTECTED_ENVIRONMENTS = frozenset(
    {Environment.STAGING, Environment.PILOT, Environment.PRODUCTION}
)


def _error(code: JourneyEvidenceContractCode) -> JourneyEvidenceContractError:
    return JourneyEvidenceContractError(code)


def _check_environment(environment: object) -> None:
    if type(environment) is not Environment:
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE)
    if environment in _PROTECTED_ENVIRONMENTS:
        raise _error(JourneyEvidenceContractCode.PROTECTED_ENVIRONMENT)


def _scope_matches(
    definition: SyntheticJourneyDefinition,
    observation: SyntheticJourneyObservation,
) -> bool:
    return (
        observation.journey_id is definition.journey_id
        and observation.definition_fingerprint == definition.fingerprint
        and observation.fixture_hash == definition.fixture_hash
        and observation.oracle_hash == definition.oracle_hash
    )


def build_synthetic_journey_manifest(
    definitions: tuple[SyntheticJourneyDefinition, ...],
    *,
    manifest_id: str,
    generated_at: datetime,
    environment: Environment,
) -> SyntheticJourneyManifest:
    """Build the exact canonical inventory without executing any journey."""

    _check_environment(environment)
    if type(definitions) is not tuple:
        raise _error(JourneyEvidenceContractCode.INVALID_TYPE)
    safe_definitions = tuple(
        sorted(
            (snapshot_journey_definition(item) for item in definitions),
            key=lambda item: item.journey_id.value,
        )
    )
    return SyntheticJourneyManifest(
        manifest_id=manifest_id,
        generated_at=generated_at,
        definitions=safe_definitions,
    )


def evaluate_synthetic_journey_evidence(
    definition: SyntheticJourneyDefinition,
    observation: object,
    *,
    evaluated_at: datetime,
    environment: Environment,
) -> SyntheticJourneyEvidenceReceipt:
    """Check detached metadata consistency; never pass or execute a journey."""

    _check_environment(environment)
    safe_definition = snapshot_journey_definition(definition)
    if safe_definition.readiness is SyntheticJourneyReadiness.BLOCKED_UNAPPROVED:
        return SyntheticJourneyEvidenceReceipt(
            definition=safe_definition,
            observation=None,
            disposition=SyntheticEvidenceDisposition.ABSTAINED,
            reason=SyntheticEvidenceReason.JOURNEY_BLOCKED,
            evaluated_at=evaluated_at,
        )

    safe_observation = snapshot_journey_observation(observation)
    if _scope_matches(safe_definition, safe_observation):
        disposition = SyntheticEvidenceDisposition.EVIDENCE_CONSISTENT
        reason = SyntheticEvidenceReason.EXACT_SYNTHETIC_METADATA
    else:
        disposition = SyntheticEvidenceDisposition.ABSTAINED
        reason = SyntheticEvidenceReason.SCOPE_MISMATCH
    return SyntheticJourneyEvidenceReceipt(
        definition=safe_definition,
        observation=safe_observation,
        disposition=disposition,
        reason=reason,
        evaluated_at=evaluated_at,
    )


__all__ = [
    "build_synthetic_journey_manifest",
    "evaluate_synthetic_journey_evidence",
]
