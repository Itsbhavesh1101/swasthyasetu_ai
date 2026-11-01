"""Fail-closed gateway for detached P19-A contract validation."""

from __future__ import annotations

from ml.quantum.contracts import (
    QuantumBoundaryCode,
    QuantumBoundaryError,
    SyntheticQuantumReceipt,
    SyntheticQuantumRequest,
    synthetic_quantum_request_fingerprint,
    validate_quantum_environment,
    validate_synthetic_quantum_receipt,
    validate_synthetic_quantum_request,
)
from ml.quantum.port import QuantumBackendPort
from ml.research.contracts import ResearchEnvironment


def validate_quantum_contract(
    *,
    backend: QuantumBackendPort,
    request: SyntheticQuantumRequest,
    environment: ResearchEnvironment,
) -> SyntheticQuantumReceipt:
    """Validate a synthetic metadata contract; never execute quantum work."""

    validate_quantum_environment(environment)
    safe_request = validate_synthetic_quantum_request(request)
    if safe_request.environment is not environment:
        raise QuantumBoundaryError(QuantumBoundaryCode.IDENTITY_MISMATCH)
    try:
        result = backend.validate_contract(request=safe_request)
    except QuantumBoundaryError:
        raise
    except Exception:  # noqa: BLE001 - provider failures are sanitized at this boundary
        raise QuantumBoundaryError(QuantumBoundaryCode.BACKEND_FAILURE) from None
    receipt = validate_synthetic_quantum_receipt(result)
    if (
        receipt.request_id != safe_request.request_id
        or receipt.request_version != safe_request.request_version
        or receipt.request_fingerprint != synthetic_quantum_request_fingerprint(safe_request)
        or receipt.recorded_at != safe_request.requested_at
        or receipt.backend_kind is not safe_request.backend_kind
        or receipt.execution_state is not safe_request.execution_state
        or receipt.approval_state is not safe_request.approval_state
        or receipt.claim_state is not safe_request.claim_state
    ):
        raise QuantumBoundaryError(QuantumBoundaryCode.IDENTITY_MISMATCH)
    return receipt


__all__ = ["validate_quantum_contract"]
