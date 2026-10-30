# P13-A — Synthetic Provider and Resource Domain Foundation

**Status:** complete bounded engineering subset; P13 live directory and referral scope remains
partial and unapproved

**Baseline:** `origin/main @ 7dc45bf11285e7c061211436f804d4e5f8f5c2dd`

**Branch:** `phase/p13-a-synthetic-provider-resource-domain`

## Implemented

- `SyntheticSourceEvidence` with versioned synthetic source identity, SHA-256 artifact metadata and
  aware-UTC acquisition time.
- `SyntheticProviderRecord` with an unmistakably synthetic label and symbolic nonclinical service
  code.
- `SyntheticCareResourceRecord` with an unmistakably synthetic label and symbolic nonclinical
  resource code.
- Closed single-value authority states: `ENGINEERING_ONLY`, `ENGINEERING_SYNTHETIC`, and
  `UNVERIFIED`.
- Direct-constructor validation for strict types, prefixes, bounds, control characters, hashes,
  versions, timestamps, temporal ordering, nested forced mutation, immutability and unknown fields.

## Deliberate boundary

The contracts cannot carry contacts, URLs, facilities, geography, languages, operating hours,
availability, teleconsultation, eligibility, specialty taxonomy, clinical mapping, ranking,
verification proof, clinical suitability or emergency authority. They are neither a registry nor a
directory query and cannot be selected by application configuration.

No source adapter, real record, persistence, migration, API, UI, referral, consent behavior,
notification, event, job, feature flag, dependency or runtime registration was added. Alembic
remains `p7a_0007`.

## Governance truth

This engineering subset does not resolve P13 Readiness Gates 1–8. It does not authorize real source
data, verification, display, routing, referral sharing or external delivery. `FR-DIR-001..017`,
`FR-REF-001..013`, and `AC-P13-001..011` remain live-not-verified. P7 remains the supported manual
path and every P8-C, P9-C, P10, P11 and P12 live restriction remains in force.
