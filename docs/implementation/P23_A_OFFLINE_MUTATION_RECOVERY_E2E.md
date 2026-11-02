# P23-A Offline Mutation-Recovery E2E Evidence

## Status

`PARTIAL` — bounded synthetic engineering evidence for offline answer handling in the existing P7
structured-intake journey only. P23 remains `PARTIAL`; no live P23 or product acceptance criterion
is complete.

## Scope and evidence

A Playwright journey exercises Chromium, the root-scoped service worker, patient-web same-origin
BFF, FastAPI, and real PostgreSQL. It loads an authorized synthetic intake, enters an unsubmitted
answer, takes the browser offline, and explicitly attempts the answer mutation.

The failed network operation produces an honest unconfirmed-request state. The answer remains only
in controlled component memory. The service worker does not intercept, queue, cache, acknowledge,
or replay the `/api/**` mutation. After connectivity is restored, an authoritative read proves that
PostgreSQL still has zero answers, the browser has no background-sync tag, and the POST count has not
increased. Only a later explicit user submission writes the answer once.

## Privacy and integrity properties

- No offline answer is written to localStorage, sessionStorage, IndexedDB, or Cache Storage.
- Cache Storage remains the exact approved public-shell allowlist.
- No background sync, mutation queue, automatic retry, or reconnect replay occurs.
- The UI never reports offline mutation success.
- The unsent value remains transient and visible only in the open component until explicit retry,
  navigation, or reload.
- The successful explicit retry creates exactly one authoritative answer.

## Change boundary

The change adds one synthetic full-stack journey and bounded evidence only. No runtime code,
backend, API contract, schema, migration, dependency, lockfile, service worker, feature flag,
infrastructure, clinical policy, or blocked P8+ capability changed.

## Acceptance truth

This closes one offline mutation/replay evidence gap for the existing P7 technical journey only. It
is not encrypted offline intake, offline clinical operation, broader journey validation, clinical
validation, accessibility certification, performance or disaster-recovery evidence, pilot
authorization, or release evidence. `AC-P23-001..012` and `AC-PROD-001..014` remain
live/product-level `NOT VERIFIED`; all governance restrictions remain.
