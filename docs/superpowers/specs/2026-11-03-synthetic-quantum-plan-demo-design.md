# Synthetic Quantum Planning Demo Design

## Intent

Provide an executable college demonstration of P19 boundary mechanics without selecting or running
any quantum technology. The offline command must prove exact P18 evidence binding, no-quantum
backend validation, and non-executable planning while preserving every P19 STOP condition.

## Selected approach

Reuse the exact private synthetic P18 bundle already assembled by `ml.research.demo`, then compose
`build_synthetic_quantum_request`, `validate_quantum_contract` with
`DeterministicNoQuantumBackend`, and `build_quantum_experiment_plan`. A new `ml.quantum.demo` command
returns only a strict content-free receipt. This is preferable to a backend/UI path, a duplicated P18
fixture, or adding PennyLane/Qiskit because it preserves isolation and avoids unnecessary code and
dependencies.

## Boundaries

- LOCAL/TEST only; protected environments fail before building the synthetic bundle.
- No encoding, circuit, optimizer, shots, backend, framework, simulator, QPU, experiment, model,
  result, comparison, advantage claim, patient data, API, UI, persistence, network, or dependency.
- Every execution state remains `NOT_EXECUTED`, every approval state remains
  `TEST_ONLY_UNAPPROVED`, and every claim state remains `NO_COMPARATIVE_CLAIM`.
- Canonical P18/P19 acceptance remains unverified.

## Verification

TDD covers deterministic replay, exact P18 fingerprint binding, unselected plan fields, protected
environment denial, forged receipt rejection, canonical JSON, content-free errors, architecture
isolation, and absence of quantum/network imports. Full backend/research, frontend, Docker,
PostgreSQL, browser, and security CI remain mandatory before merge.
