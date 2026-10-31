# P18-D Synthetic Candidate Metadata and Model Cards Design

## Intent

Add the smallest offline, engineering-only P18-D mechanics needed to describe and catalogue a
P18-C synthetic baseline without creating an executable artifact, promotion path, or live model
registry. The result is metadata evidence only and cannot satisfy a live P18 acceptance criterion.

## Approaches considered

1. **Free-form model cards.** Flexible, but unsafe: arbitrary text can contain sensitive data and
   unverifiable claims. Rejected.
2. **Cards copied from caller-supplied metric fields.** Simple, but a card could attribute another
   model's result to the candidate. Rejected.
3. **Closed metadata derived from recomputed evidence.** Selected. Reconstruct the P18-B/C inputs,
   rerun the exact synthetic model on the locked test batch, reproduce the evaluation receipt, and
   only then issue a closed, immutable card and candidate record.

## Contracts

- `SyntheticModelCard` binds exact model identity/fingerprint, baseline kind, split and
  preprocessing fingerprints, evaluation receipt fingerprint, content-free counts, a closed
  engineering-only purpose, and a fixed closed limitation set.
- `SyntheticModelCandidate` binds exact model and card identities/fingerprints and can only hold
  `TEST_ONLY_UNAPPROVED` status.
- `SyntheticCandidateRegistry` is immutable and bounded. It resolves exact candidate ID/version
  pairs, rejects duplicate identities and model/card aliasing, and exposes no latest, mutation,
  approval, promotion, activation, save, or load surface.
- Aware non-UTC timestamps normalize to UTC; naive values fail closed.
- All trust boundaries reconstruct nested values and emit stable content-free errors.

## Evidence binding

Card creation accepts an exact P18-C model, P18-B split and preprocessing receipt, locked-test
transformed batch, closed expected labels, and evaluation receipt. It predicts and evaluates again
using the receipt's version. Any fingerprint, membership, partition, count, or result mismatch
rejects card creation. Protected environments reject before caller collections are inspected.

## Governance and security

- Only `LOCAL` and `TEST` are permitted.
- Purpose, metric kind, status, and limitations are closed enums; there is no narrative field.
- No artifact bytes, file path, URI, loader, signature, serialization, network, database, service,
  MLflow, API, worker, backend import, or dependency is introduced.
- Registry presence is not validation or approval. No state transition exists.

## Non-goals

No real data or clinical task, actual research admission, governed model registration, executable
artifact, performance claim, calibration, explainability or fairness claim, approval workflow,
inference, P18-E benchmark, or P19 behavior is implemented.

## Acceptance truth

The closed synthetic records exercise metadata integrity only. `FR-ML-001..017` and
`AC-P18-001..010` remain LIVE NOT VERIFIED, P18 remains PARTIAL, and P19 remains blocked by
`P18_READINESS_GATE_REVIEW.md`.
