# P23-A Core-Journey Negative E2E Evidence Design

## Intent

Extend the existing bounded P7 browser journey with the two missing negative oracles named by the
P23 coverage assessment: cross-session IDOR denial and consent withdrawal during an active draft.
The evidence remains synthetic engineering validation of the already implemented P7 path. It is not
clinical validation, production acceptance, or authorization for any blocked module.

## Goals

- Exercise the real patient web, same-origin BFF, FastAPI authorization/consent services, and
  PostgreSQL using repository-owned synthetic text.
- Prove a second pseudonymous session cannot read another session's intake through either the BFF
  response or rendered page.
- Prove withdrawing `GENERAL_PRODUCT_USE` / `clinical_intake` consent blocks a previously accessible
  draft while leaving the pseudonymous session active.
- Keep all responses privacy-minimized and verify no protected draft text is rendered after denial.

## Non-goals

- No new feature behavior, endpoint, schema, migration, dependency, feature flag, or runtime module.
  A verified authorization-error ordering defect may receive the smallest fail-closed correction.
- No patient/clinical data, clinical policy, diagnosis, triage, external provider, or blocked P8+
  capability.
- No production identity, clinician/admin journey, accessibility certification, performance result,
  recovery drill, pilot, or release claim.
- No claim that P23, P23-A, `AC-P23-001`, or `AC-PROD-001` is complete.

## Approaches considered

### 1. Add more backend authorization tests

Rejected as the primary approach because PostgreSQL API tests already cover the backend rules. They
cannot prove that cookies, the BFF, and rendered error states preserve those rules together.

### 2. Add a new journey-evidence runtime

Rejected because the existing P23-A metadata package already provides detached integrity mechanics.
Another abstraction would add code without increasing cross-layer evidence.

### 3. Add two focused Playwright journeys

Selected. The existing CI topology already provides Chromium, patient web, FastAPI, and PostgreSQL.
Two tests close named negative-evidence gaps without adding tooling; a verified authorization defect
may receive only the smallest fail-closed boundary correction.

## Test architecture

The consent-withdrawal test creates one real synthetic intake, withdraws the exact active consent,
then asserts the BFF returns `CONSENT_REQUIRED`, the page renders the bounded unavailable state, the
synthetic draft value is absent, and the session remains active.

The cross-session test creates an intake in one browser context and a separately onboarded session in
another. Existing and unknown intake identifiers must produce the same non-enumerating denial for
the second session. The second context must render the bounded unavailable state and never receive
the owner's synthetic draft value. Both contexts are closed explicitly.

## Governance outcome

This work strengthens bounded evidence for canonical P23 journey 1 only. It does not change the
readiness classification: P23 remains `PARTIAL`, and all live P23/product acceptance remains
unverified. Every P8-C, P9-C, P10-P24, clinical, privacy, security, and release restriction remains
unchanged.
