"""Boundary tests for the deterministic no-quantum P19-A fake."""

from __future__ import annotations

import ast
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from ml.quantum.contracts import (
    QuantumBoundaryCode,
    QuantumBoundaryError,
    QuantumClaimState,
    QuantumExecutionState,
    SyntheticQuantumReceipt,
    SyntheticQuantumRequest,
    synthetic_quantum_request_fingerprint,
    validate_synthetic_quantum_receipt,
)
from ml.quantum.gateway import validate_quantum_contract
from ml.quantum.port import QuantumBackendPort
from ml.quantum.testing import DeterministicNoQuantumBackend
from ml.research.contracts import ResearchEnvironment
from ml.tests.test_quantum_contracts import request

ROOT = Path(__file__).resolve().parents[2]


class HostilePort:
    def __getattribute__(self, name: str) -> object:
        raise RuntimeError("private-canary")


class ExplodingPort:
    def validate_contract(self, *, request: SyntheticQuantumRequest) -> SyntheticQuantumReceipt:
        raise RuntimeError("private-canary")


class ForgedReceiptPort:
    def validate_contract(self, *, request: SyntheticQuantumRequest) -> SyntheticQuantumReceipt:
        value = DeterministicNoQuantumBackend().validate_contract(request=request)
        object.__setattr__(value, "request_fingerprint", "f" * 64)
        return value


class SyntheticQuantumBackendTests(unittest.TestCase):
    def test_fake_conforms_to_port_and_returns_no_execution_receipt(self) -> None:
        backend = DeterministicNoQuantumBackend()
        value = request()

        self.assertIsInstance(backend, QuantumBackendPort)
        receipt = validate_quantum_contract(
            backend=backend,
            request=value,
            environment=ResearchEnvironment.TEST,
        )

        self.assertEqual(
            receipt.request_fingerprint,
            synthetic_quantum_request_fingerprint(value),
        )
        self.assertIs(receipt.execution_state, QuantumExecutionState.NOT_EXECUTED)
        self.assertIs(receipt.claim_state, QuantumClaimState.NO_COMPARATIVE_CLAIM)
        self.assertEqual(receipt.recorded_at, value.requested_at)
        self.assertFalse(hasattr(receipt, "prediction"))
        self.assertFalse(hasattr(receipt, "metric"))
        self.assertFalse(hasattr(receipt, "statevector"))
        self.assertFalse(hasattr(receipt, "shots"))

    def test_fake_is_deterministic(self) -> None:
        backend = DeterministicNoQuantumBackend()
        value = request()

        first = backend.validate_contract(request=value)
        second = backend.validate_contract(request=value)

        self.assertEqual(first, second)
        with self.assertRaises(FrozenInstanceError):
            first.receipt_fingerprint = "f" * 64  # type: ignore[misc]

    def test_receipt_validator_rejects_forced_mutation(self) -> None:
        receipt = DeterministicNoQuantumBackend().validate_contract(request=request())
        object.__setattr__(receipt, "execution_state", "EXECUTED")

        with self.assertRaises(QuantumBoundaryError) as error:
            validate_synthetic_quantum_receipt(receipt)

        self.assertIs(error.exception.code, QuantumBoundaryCode.INVALID_TYPE)

    def test_gateway_rejects_forged_receipt(self) -> None:
        with self.assertRaises(QuantumBoundaryError) as error:
            validate_quantum_contract(
                backend=ForgedReceiptPort(),
                request=request(),
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, QuantumBoundaryCode.IDENTITY_MISMATCH)

    def test_gateway_rejects_request_from_a_different_safe_environment(self) -> None:
        with self.assertRaises(QuantumBoundaryError) as error:
            validate_quantum_contract(
                backend=DeterministicNoQuantumBackend(),
                request=request(environment=ResearchEnvironment.TEST),
                environment=ResearchEnvironment.LOCAL,
            )

        self.assertIs(error.exception.code, QuantumBoundaryCode.IDENTITY_MISMATCH)

    def test_gateway_sanitizes_unexpected_backend_failure(self) -> None:
        with self.assertRaises(QuantumBoundaryError) as error:
            validate_quantum_contract(
                backend=ExplodingPort(),
                request=request(),
                environment=ResearchEnvironment.TEST,
            )

        self.assertIs(error.exception.code, QuantumBoundaryCode.BACKEND_FAILURE)
        self.assertNotIn("private-canary", str(error.exception))

    def test_protected_environment_rejects_before_port_or_request_inspection(
        self,
    ) -> None:
        with self.assertRaises(QuantumBoundaryError) as error:
            validate_quantum_contract(
                backend=HostilePort(),  # type: ignore[arg-type]
                request=object(),  # type: ignore[arg-type]
                environment=ResearchEnvironment.PILOT,
            )

        self.assertIs(error.exception.code, QuantumBoundaryCode.PROTECTED_ENVIRONMENT)

    def test_backend_package_imports_no_quantum_framework_or_network_library(
        self,
    ) -> None:
        forbidden_roots = {
            "pennylane",
            "qiskit",
            "cirq",
            "braket",
            "httpx",
            "requests",
            "socket",
            "urllib",
        }
        violations: dict[str, set[str]] = {}
        for path in (ROOT / "ml" / "quantum").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            roots: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots.update(alias.name.split(".", 1)[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    roots.add(node.module.split(".", 1)[0])
            if blocked := roots & forbidden_roots:
                violations[path.name] = blocked

        self.assertEqual(violations, {})

    def test_fake_has_no_provider_or_execution_surface(self) -> None:
        backend = DeterministicNoQuantumBackend()
        forbidden = {
            "execute",
            "run",
            "submit",
            "connect",
            "train",
            "infer",
            "predict",
            "promote",
        }

        self.assertTrue(forbidden.isdisjoint(dir(backend)))


if __name__ == "__main__":
    unittest.main()
