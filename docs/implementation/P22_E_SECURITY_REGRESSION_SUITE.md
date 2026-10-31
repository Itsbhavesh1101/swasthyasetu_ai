# P22-E Security Regression Suite — Bounded Synthetic Evidence

**Status:** Bounded tests-only engineering evidence implemented; P22 remains **PARTIAL**

**Baseline:** `origin/main @ 75eab2e79e5a86fe19392b5cd5f312b2987d9159`

**Branch:** `phase/p22-e-security-regression-suite`

## 1. Governance decision

The merged P22-B/C/D units provide bounded security, retention and resilience mechanics, but the
canonical readiness review leaves production topology, accountable policies, independent
assessment, operational ownership and release acceptance unresolved. P22-E therefore adds only an
independent synthetic composition suite. It does not convert technical evidence into approval.

## 2. Implemented evidence

The detached regression suite proves that:

- an abuse-control failure blocks route execution and produces a sanitized no-store response with
  the standard security headers;
- unauthorized and held purge plans make zero adapter calls;
- disabled or tripped optional capabilities make no new dependency calls;
- availability or authorization in one subsystem cannot authorize work in another subsystem;
- a trip during an in-flight optional call discards the late result;
- restore reconciliation reblocks a tombstoned generation;
- purge and dependency failures expose only closed error/status values and do not disclose
  exception, locator or result canaries; and
- retention and resilience foundations add no automatic route, module, reset, scheduler or startup
  surface.

All fixtures use artificial opaque identifiers and non-medical canaries. No production package was
changed.

## 3. Deliberately absent

- production identity, consent, clinical policy, patient data or real content;
- live provider, integration, upload, file, edge/WAF or network testing;
- real retention schedule, legal-hold decision, purge adapter, deletion or backup mutation;
- distributed rate limiting or kill-switch state;
- API/UI/admin activation, worker, job, event, persistence, migration or dependency change;
- alerting, incident response, rollback/recovery exercise, penetration test or independent human
  assessment; and
- P23, P24, pilot or release authorization.

## 4. Acceptance status

This suite supplies bounded regression evidence toward P22 control composition only. It does not
fully verify `AC-P22-001..011`, `NFR-SEC-001..014`, `PRIV-001..009`, or `NFR-RES-001..007`.
P22 remains **PARTIAL** until the outstanding accountable policy, deployment, independent review,
operational and release evidence identified in `P22_READINESS_GATE_REVIEW.md` exists.
