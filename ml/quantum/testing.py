"""Deterministic no-quantum fake for isolated contract tests only."""

from __future__ import annotations

from ml.quantum.contracts import (
    SyntheticQuantumReceipt,
    SyntheticQuantumRequest,
    build_synthetic_quantum_receipt,
)


class DeterministicNoQuantumBackend:
    """Validate metadata without a simulator, circuit, provider, or result."""

    def validate_contract(self, *, request: SyntheticQuantumRequest) -> SyntheticQuantumReceipt:
        return build_synthetic_quantum_receipt(
            request=request,
            backend_id="syn_qml_backend_no_quantum",
            backend_version="engineering.v1",
        )


__all__ = ["DeterministicNoQuantumBackend"]
