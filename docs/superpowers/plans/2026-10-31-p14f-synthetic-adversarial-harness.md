# P14-F Synthetic Adversarial Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add offline engineering-only adversarial integration evidence for the existing P14-A/B/C boundaries without adding runtime behavior.

**Architecture:** One backend test module composes existing strict contracts, the test-only backstop,
and the test-only policy fixture. Documentation records the bounded result and keeps all live P14 and
P14-E gates blocked.

**Tech Stack:** Python 3.13, pytest, existing backend P14 contracts and test-support fixtures.

**Spec:** `docs/superpowers/specs/2026-10-31-p14f-synthetic-adversarial-harness-design.md`

## Global Constraints

- Synthetic nonmedical fixed tokens only; no patient or clinical text.
- Test support only; no runtime import, API, persistence, dependency, or activation.
- Protected environments must fail before reading hostile policy/evidence.
- P8-C/P9-C/P10/P11/P12/P13/P14 governance restrictions remain active.

## Review Focus

- Extra route or prose fields in extraction payloads must fail with content-free errors.
- Conflicting extractor/backstop state must degrade and never select a normal toy route.
- Synthetic override must remain dominant over lower-precedence toy evidence.
- Missing policy and protected environments must fail closed.
- The harness itself must contain no clinical cases, scores, thresholds, contacts, or runtime import.

---

### Task 1: Offline adversarial integration matrix

**Files:**
- Create: `backend/tests/mental_health_support/adversarial_harness.py`
- Create: `backend/tests/test_synthetic_mental_health_adversarial.py`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`
- Create: `docs/implementation/P14_F_SYNTHETIC_ADVERSARIAL_HARNESS.md`

**Interfaces:**
- Consumes: P14-A extraction contracts/parser, P14-B test-only backstop, P14-C evaluator and test-only policy fixture.
- Produces: test-only adversarial evidence; no application interface.

- [ ] Write parametrized failing tests for end-to-end toy outcomes, malformed payloads, conflict,
  override, unavailable policy, and protected-environment short-circuiting.
- [ ] Run the focused file and confirm failure because its harness helpers do not exist yet.
- [ ] Implement only test-local builders and composition helpers.
- [ ] Run all P14 backend and P14-D frontend tests, then full backend/frontend quality gates.
- [ ] Audit scope, Docker configuration, migration head, dependencies, runtime imports, and secrets.
- [ ] Commit, push, open a PR, verify six exact-SHA CI jobs, merge, and verify six main jobs.
