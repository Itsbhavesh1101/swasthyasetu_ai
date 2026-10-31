# P14-F Synthetic Adversarial Harness - Design

## Decision

Implement an offline, test-only integration harness over the merged P14-A/B/C engineering contracts.
The harness uses fixed nonmedical tokens to prove boundary composition, deterministic precedence,
fail-closed disagreement, malformed-output rejection, and protected-environment denial. P14-D remains
covered by its disconnected frontend adversarial tests and the full frontend gate.

## Approach

- Build no new production service or adapter. Compose existing immutable contracts directly in tests.
- Keep the corpus as explicit parametrized engineering cases, not text, language samples, clinical
  scenarios, thresholds, scores, or release evidence.
- Assert stable content-free errors and toy machine states only.
- Treat P14-E as blocked: no recipient, consent, payload, referral, resource, network, or side effect.

## Alternatives rejected

- A P14-E referral stub duplicates the already merged P13-E unavailable-state evidence while the
  actual P13/consent/resource decisions remain blocked.
- A production harness package would create runtime surface with no approved consumer.
- Real or pseudo-clinical utterances would invent the clinical corpus the readiness review reserves
  for accountable approval.

## Non-goals

No patient data, narrative, language lexicon, clinical signal, route meaning, crisis guidance,
resource, referral, API, persistence, dependency, feature flag, module registration, or activation.
