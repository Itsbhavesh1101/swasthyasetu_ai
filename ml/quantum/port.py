"""Provider-neutral metadata-validation port for isolated P19 research."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ml.quantum.contracts import SyntheticQuantumReceipt, SyntheticQuantumRequest


@runtime_checkable
class QuantumBackendPort(Protocol):
    """Validate a synthetic contract without quantum execution."""

    def validate_contract(self, *, request: SyntheticQuantumRequest) -> SyntheticQuantumReceipt:
        """Return a metadata-only, explicitly non-executed receipt."""
        ...


__all__ = ["QuantumBackendPort"]
