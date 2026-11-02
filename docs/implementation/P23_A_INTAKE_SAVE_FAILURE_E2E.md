# P23-A Intake Save-Failure E2E Evidence

## Status

`PARTIAL` — bounded synthetic engineering evidence for save-failure handling in the existing P7
structured-intake journey only. P23 remains `PARTIAL`; no live P23 or product acceptance criterion
is complete.

## Scope and evidence

Two Playwright journeys exercise Chromium, the patient-web same-origin BFF, FastAPI, and real
PostgreSQL with repository-owned synthetic text:

1. A simulated dependency failure rejects the answer request before it reaches the BFF. The UI
   retains the generic failure notice and the unsent answer in ephemeral component memory, a real
   BFF read proves that PostgreSQL still has zero answers, and only an explicit user retry performs
   the successful write. The resulting draft contains exactly one answer.
2. A simulated lost response forwards one answer request through the real BFF/backend and then
   substitutes a generic failure response at the browser boundary. A real BFF read proves that the
   answer was committed exactly once. The client does not replay the POST, and the user can review
   the authoritative saved value.

Component regression tests independently prove that a post-failure authoritative refetch no longer
erases the visible failure notice, that unchanged state preserves the unsent control value, and that
refetched saved state is rendered without a mutation replay.

## Privacy and integrity properties

- No mutation is automatically retried after an ambiguous response.
- Save success is shown only from authoritative server state.
- Unconfirmed input remains browser-memory-only and is not persisted to browser storage.
- Error copy contains no answer, bearer, cookie, or internal exception detail.
- Existing `Cache-Control: no-store`, session, consent, and object-authorization boundaries remain
  unchanged.

## Change boundary

The verified defect was limited to client state handling: the required post-failure refetch cleared
the failure notice immediately on a successful GET. The refetch now preserves the mutation failure
notice while still replacing intake state with the authoritative response. No API, backend, schema,
migration, dependency, lockfile, feature flag, service worker, infrastructure, clinical policy, or
blocked P8+ capability changed.

## Acceptance truth

This closes the failed-save negative-oracle gap for the existing P7 technical journey only. It is
not broader journey validation, clinical validation, accessibility certification, performance or
recovery evidence, pilot authorization, or release evidence. `AC-P23-001..012` and
`AC-PROD-001..014` remain live/product-level `NOT VERIFIED`; all governance restrictions remain.
