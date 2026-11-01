# P19-A Synthetic Quantum Backend Contracts

**Status:** BOUNDED ENGINEERING-SYNTHETIC FOUNDATION ONLY

**Baseline:** `origin/main @ 638e49003ebf441b15cd8877ef5d2413f0e1d80f`

**Recorded:** 2026-11-02

## Outcome

The isolated `ml.quantum` package now defines a provider-neutral contract-validation port,
immutable request and receipt contracts, a fail-closed gateway, and a deterministic no-quantum
test fake. The boundary binds exact P18 synthetic candidate, card, model, dataset, split, and
preprocessing fingerprints. It permits only `LOCAL` and `TEST` and records only
`METADATA_BINDING_ONLY`, `NOT_EXECUTED`, `TEST_ONLY_UNAPPROVED`, and
`NO_COMPARATIVE_CLAIM` states.

The fake validates metadata and produces a deterministic receipt. It does not execute or emulate a
quantum operation. Protected environments are rejected before request or backend inspection.
Unexpected backend errors are converted to stable content-free failures, and returned receipts are
reconstructed and checked against the exact request and environment.

## Deliberate exclusions

- no PennyLane, Qiskit, Cirq, Braket, simulator, statevector, shots, circuit, encoding values,
  optimizer, QPU, cloud provider, credential, network, queue, or hardware;
- no dataset rows, feature values, labels, patient or clinical data;
- no training, inference, prediction, score, metric, comparison, generalization result,
  explainability output, quantum-performance or quantum-advantage claim;
- no artifact loading, registry promotion, approval, persistence, migration, API, UI, worker,
  runtime registration, feature flag, dependency, or deployment;
- no effect on P7 intake, P9 safety, any patient workflow, or any production path.

## Verification boundary

Adversarial tests cover immutable fingerprints, direct-constructor drift, P18 candidate/card
linkage, UTC normalization, environment replay, protected-environment short circuiting, hostile
inputs, forged receipts, backend exception sanitization, deterministic replay, forbidden execution
surfaces, and absence of quantum-framework or network imports. The existing architecture test still
requires `backend/app` to remain independent of `ml`.

## Acceptance truth

This foundation supplies a provider-neutral abstraction shape relevant to `AC-P19-002`; it does
not satisfy that live criterion because no approved research backend exists. It does not satisfy
`AC-P19-001` or `AC-P19-003..009`. All `FR-QML-001..018` and `AC-P19-001..009` remain **LIVE NOT
VERIFIED**. P18 still has no approved real benchmark, and the P19 readiness STOP remains in force
for experiments, dependencies, simulators, circuits, comparisons, claims, pilots, and production.

## Next safe action

Independently review this metadata-only boundary. Do not implement P19-B or execute any quantum or
comparative workload until the P18 benchmark, scientific protocol, privacy/security controls,
dependency architecture, model governance, and accountable research decisions required by
`P19_READINESS_GATE_REVIEW.md` genuinely exist.
