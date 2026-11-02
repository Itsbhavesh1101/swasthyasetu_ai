# P23-A Session-Invalidation Recovery E2E Evidence

## Status

`PARTIAL` — bounded synthetic engineering evidence for session-invalidated recovery in the existing
P7 structured-intake journey only. P23 remains `PARTIAL`; no live P23 or product acceptance
criterion is complete.

## Scope and evidence

A Playwright journey exercises Chromium, the patient-web same-origin BFF, FastAPI, and real
PostgreSQL. It loads an authorized synthetic intake, keeps an unsubmitted answer in component
memory, then closes the same private session through the real backend before the browser submits.

FastAPI rejects the mutation with its established closed-session state. Because that code is also
used for ordinary intake lifecycle conflicts, the BFF performs one bounded, read-only session
recheck. Only the independently proven closed session is converted to minimized
`SESSION_UNAVAILABLE`; both opaque cookies are cleared. The client immediately removes loaded
intake state and unsent input, replaces the route with `/language`, and performs no mutation replay.

Component and BFF regression tests independently prove:

- invalid-session results remove already loaded intake state and redirect;
- a proven closed session clears both cookies;
- an ordinary intake `INVALID_STATE_TRANSITION` with an active session preserves credentials;
- a cross-subject `AUTHENTICATION_REQUIRED` denial with an active session preserves credentials;
- no `409 RESOURCE_CONFLICT` is treated as session invalidation.

## Privacy and integrity properties

- Loaded clinical state is not retained on screen after session authority is lost.
- Unsubmitted text is removed from component memory and never written to browser storage.
- The closed-session response contains no intake value, bearer, cookie, identifier, or internal
  exception detail.
- A side-effecting request is never retried automatically.
- Cookie deletion occurs only after explicit expiry or an independent session-status recheck proves
  lost authority; ordinary intake conflicts and cross-subject denials cannot log out a valid
  session.
- Existing consent, object authorization, no-store, and service-worker boundaries remain unchanged.

## Change boundary

The change is limited to patient-web BFF session-state disambiguation, invalid-session UI recovery,
component/BFF regression coverage, and one synthetic full-stack journey. No backend, API contract,
schema, migration, dependency, lockfile, feature flag, service worker, infrastructure, clinical
policy, or blocked P8+ capability changed.

## Acceptance truth

This closes a session-invalidation recovery gap for the existing P7 technical journey only. It is
not broader journey validation, clinical validation, accessibility certification, performance or
recovery evidence, pilot authorization, or release evidence. `AC-P23-001..012` and
`AC-PROD-001..014` remain live/product-level `NOT VERIFIED`; all governance restrictions remain.
