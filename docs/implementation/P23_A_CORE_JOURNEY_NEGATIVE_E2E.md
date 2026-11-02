# P23-A Core-Journey Negative E2E Evidence

## Status

`PARTIAL` — bounded synthetic engineering evidence for the already implemented P7 patient intake
journey only. P23 remains `PARTIAL`; no live P23 or product acceptance criterion is complete.

## Scope

Two Playwright journeys exercise Chromium through the patient web, same-origin BFF, FastAPI, and a
real PostgreSQL database:

1. A session creates and saves a repository-owned synthetic intake draft, withdraws its exact
   `GENERAL_PRODUCT_USE` / `clinical_intake` consent, and is denied subsequent draft access with
   `CONSENT_REQUIRED`. The draft value is absent from the denied UI, while the session remains
   active and the encounter page returns to the consent step.
2. One session creates a repository-owned synthetic draft and a separately onboarded browser
   context requests its URL. Existing foreign and unknown intake identifiers both receive the same
   non-enumerating `AUTHENTICATION_REQUIRED` boundary, no draft value, and the bounded unavailable
   state. The owner's session and draft remain accessible after the attempt.

Both tests run independently and concurrently. They use fresh sessions and intake identifiers and
do not depend on execution order.

## Security and privacy properties

- Opaque session credentials remain in existing `HttpOnly`, `SameSite=Strict` cookies.
- The cross-session response exposes neither the owner's synthetic answer nor resource details.
- Consent withdrawal is enforced by the authoritative backend, not inferred in the browser.
- Denied pages do not render the protected synthetic value.
- No patient data, clinical rule, diagnosis, triage, external provider, or production identity is
  used.

## Change boundary

The evidence exposed one authorization-order defect: an unknown intake returned
`RESOURCE_NOT_FOUND` while an existing foreign intake returned `AUTHENTICATION_REQUIRED`. The API
boundary now normalizes both cases to the same content-free authentication denial. No successful
flow, endpoint shape, schema, migration, dependency, lockfile, feature flag, runtime registration,
infrastructure, or blocked P8+ module changes.

## Acceptance truth

The evidence closes two negative-oracle gaps for the existing P7 technical journey. It is not
clinical validation, accessibility certification, performance evidence, a recovery drill, pilot
authorization, or release evidence. `AC-P23-001..012` and `AC-PROD-001..014` remain live/product
level `NOT VERIFIED`, and all existing governance restrictions remain unchanged.
