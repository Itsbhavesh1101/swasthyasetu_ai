# P23-A Intake Conflict-Recovery E2E Evidence

## Status

`PARTIAL` — bounded synthetic engineering evidence for stale-version recovery in the existing P7
structured-intake journey only. P23 remains `PARTIAL`; no live P23 or product acceptance criterion
is complete.

## Scope and evidence

A Playwright journey uses two pages in one authorized private session to exercise Chromium, the
patient-web same-origin BFF, FastAPI, and real PostgreSQL. Both pages load the same version of a
synthetic intake. The first page commits one answer. The second page then submits a distinct stale
answer and receives `RESOURCE_CONFLICT`.

The browser refetches authoritative state, removes the unconfirmed stale control value, disables
further submission from the stale view, and requires the user to review the latest saved draft.
The conflict response is content-free and `no-store`. A real BFF read proves that PostgreSQL holds
exactly the first accepted answer at the incremented version and contains no stale value.

Component regression coverage independently proves the conflict-specific state transition and
that exactly one mutation request is made. Existing coverage continues to prove that a pre-write
dependency failure preserves memory-only input for explicit retry and that an ambiguous response
is never replayed automatically.

## Privacy and integrity properties

- Every answer mutation remains bound to the version the user actually viewed.
- A stale mutation never writes partially and is never automatically resubmitted.
- Unconfirmed stale input is removed from the rendered control and is not persisted to browser
  storage.
- The user must explicitly review authoritative saved information before taking another action.
- Conflict copy contains no answer, bearer, cookie, identifier, or internal exception detail.
- Existing session, consent, object-authorization, and cache-control boundaries remain unchanged.

## Change boundary

The change is limited to patient-web conflict-state presentation, component regression coverage,
and a synthetic full-stack E2E journey. No API, backend, schema, migration, dependency, lockfile,
feature flag, service worker, infrastructure, clinical policy, or blocked P8+ capability changed.

## Acceptance truth

This closes the stale-version negative-oracle gap for the existing P7 technical journey only. It
is not broader journey validation, clinical validation, accessibility certification, performance
or recovery evidence, pilot authorization, or release evidence. `AC-P23-001..012` and
`AC-PROD-001..014` remain live/product-level `NOT VERIFIED`; all governance restrictions remain.
