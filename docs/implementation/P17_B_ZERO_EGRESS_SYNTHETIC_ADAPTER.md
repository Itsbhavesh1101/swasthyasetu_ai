# P17-B Zero-Egress Synthetic Test Adapter

**Status:** BOUNDED TEST-ONLY ENGINEERING-SYNTHETIC FOUNDATION
**Baseline:** `origin/main @ 8f9617f575508c28ea75a5cb481c57759b9624d5`
**Branch:** `phase/p17-b-zero-egress-test-adapter`

## Decision

The current repository still cannot support an official ABDM sandbox adapter. Spec 21 remains an
unapproved draft, current official protocol and sandbox sources have not been adopted, and partner,
identity, consent, FHIR-conformance, privacy, security, legal and release decisions remain open.

The separately authorized P17-B subset therefore adds only a deterministic adapter under backend
test support. It implements the opaque P17-A port for offline contract testing without introducing a
production import path, official workflow semantics, external traffic or runtime configuration.

## Implemented engineering evidence

- Exact request-fingerprint-to-scenario fixture mapping copied into an immutable snapshot.
- Closed accepted, rejected and unavailable scenarios mapped only to existing content-free P17-A
  result states and issues.
- Strict request reconstruction before fixture lookup and exact result/request validation before
  return.
- Deterministic unknown-request degradation to unavailable; no fallback acceptance.
- Canonical UTC result clocks, naive-clock rejection and content-free clock-failure containment.
- Constructor denial for staging, pilot and production before fixture or clock access.
- Adversarial tests for hostile fixture containers, caller mutation, malformed entries, forced
  nested request mutation, fingerprint drift, clock failures and protected environments.

## Deliberately absent

- Official ABDM/ABHA operation, identifier, payload, callback, authentication or consent semantics.
- Official sandbox, endpoint, credential, HTTP client, DNS, socket, file, database or other I/O.
- Realistic identifiers, patient/clinical data, FHIR resources or import/export behavior.
- Retry, reconciliation, callback ordering, idempotent remote mutation or conformance claims.
- Production adapter/gateway, application import, dependency, configuration, feature flag, module
  registration, persistence, migration, API/BFF, UI, event, job or runtime activation.

## Acceptance truth

This test adapter provides bounded engineering evidence toward mock-boundary design only. It is not
an approved or official sandbox path and does not satisfy `AC-P17-004`. A test implementation of the
port does not establish live ABDM access for `AC-P17-002`. There is no exchange, local clinical-data
mutation, import/export or supported official operation, so `AC-P17-003` and `AC-P17-005..007` also
remain unverified. Spec 21 is still unapproved, so `AC-P17-001` remains unverified.

Every `FR-ABDM-001..007` and `AC-P17-001..007` outcome remains **LIVE NOT VERIFIED**. All P8-C/P9-C
Stage 3, P10/P11 live, P15 clinical, P16 live-conformance and P17 live-integration restrictions stay
active.

## Next gate

P17-C live synchronization/use-case work remains blocked. The next safe unit, if separately bounded,
is P17-D offline failure-isolation evidence proving this detached test adapter cannot affect P7 local
intake. Any official sandbox or live path still requires current official sources and all decisions
listed in the P17 readiness review.
