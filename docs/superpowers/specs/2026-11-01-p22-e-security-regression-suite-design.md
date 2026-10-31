# P22-E Security Regression Suite Design

**Date:** 2026-11-01

**Status:** Bounded engineering design; not an accountable approval

**Scope:** Synthetic tests and evidence only

## Objective

P22-E adds an independent adversarial regression layer over the already merged P22-B security
controls, P22-C retention/purge foundation, and P22-D optional-dependency resilience foundation.
It verifies that those controls compose fail-closed and do not accidentally authorize one another.

This is not a production-security acceptance, penetration test, clinical approval, retention-policy
approval, or pilot authorization.

## Architecture

The suite is a detached pytest module under `backend/tests`. It invokes existing public contracts
and application composition points without adding a production package, endpoint, worker, job,
configuration flag, dependency, persistence model, or migration.

The test harness uses only synthetic opaque identifiers and canary strings. It verifies:

1. API abuse-control failures block route work and return sanitized no-store responses with the
   standard security headers.
2. An unavailable or tripped optional capability and an unauthorized/held purge both make zero
   downstream calls.
3. Availability in one control plane never grants authority in another: resilience availability
   does not authorize purge, and purge authorization does not enable optional capabilities.
4. A kill-switch trip during in-flight work discards the late result, while restore reconciliation
   keeps a purged generation reblocked.
5. Exceptions, locators, credentials, and operation results do not appear in HTTP errors or bounded
   result representations.
6. P22 foundations remain unregistered and expose no route, reset, scheduler, or automatic-runtime
   activation surface.

## Security properties

- **Default deny:** absent explicit bounded inputs, no optional or destructive downstream work runs.
- **Non-interference:** a positive decision in one subsystem cannot substitute for authorization,
  consent, policy, or approval in another.
- **Privacy-safe failure:** only closed error/status values cross the tested boundaries.
- **Irreversibility integrity:** late optional results cannot bypass a trip, and restored purged
  generations cannot silently return to use.
- **Honest evidence:** the suite proves process-local synthetic mechanics only.

## Explicit exclusions

No live provider, upload, patient data, clinical content or decision, real retention schedule,
legal hold policy, distributed rate limiter, edge/WAF control, distributed kill switch, real purge
adapter, storage deletion, audit service, alerting, incident workflow, recovery drill, production
identity, release decision, or P23/P24 implementation is included.

`AC-P22-001..011` remain live and not fully verified. P22 stays PARTIAL because accountable policy,
deployment, independent assessment, operational, and release evidence remains outstanding.
