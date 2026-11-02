# P23-A Consent-Invalidation Recovery E2E Evidence

## Status

`PARTIAL` — bounded synthetic engineering evidence for consent-invalidated recovery in the existing
P7 structured-intake journey only. P23 remains `PARTIAL`; no live P23 or product acceptance
criterion is complete.

## Scope and evidence

A Playwright journey exercises Chromium, the patient-web same-origin BFF, FastAPI, and real
PostgreSQL. It loads an authorized synthetic intake, keeps an unsubmitted answer in component
memory, then withdraws the same session's intake consent through the real consent UI before the
original page submits.

FastAPI revalidates consent at the protected mutation and rejects the answer with the established
content-free `CONSENT_REQUIRED` response. The client removes the loaded intake and unsent input,
replaces the route with `/consent`, and performs no mutation replay or intake refetch. The active
private session and both opaque cookies remain available because consent withdrawal is not session
closure.

A component regression test independently proves that a consent-required mutation result clears
already loaded state, enters the controlled consent flow, and issues no automatic retry.

## Privacy and integrity properties

- Loaded clinical state is not retained on screen after consent authority is lost.
- Unsubmitted text is removed from component memory and never written to browser storage.
- The denial contains no intake value, bearer, cookie, identifier, or internal exception detail.
- The rejected side-effecting request is never retried automatically.
- Session credentials are preserved, matching the separate consent and session lifecycles.
- Governed server state remains retained; subsequent protected access stays blocked while consent is
  inactive.

## Change boundary

The change is limited to patient-web consent-recovery presentation, component regression coverage,
and one synthetic full-stack journey. No backend, API contract, schema, migration, dependency,
lockfile, feature flag, service worker, infrastructure, clinical policy, or blocked P8+ capability
changed.

## Acceptance truth

This closes a consent-invalidation recovery gap for the existing P7 technical journey only. It is
not broader journey validation, clinical validation, accessibility certification, performance or
recovery evidence, pilot authorization, or release evidence. `AC-P23-001..012` and
`AC-PROD-001..014` remain live/product-level `NOT VERIFIED`; all governance restrictions remain.
