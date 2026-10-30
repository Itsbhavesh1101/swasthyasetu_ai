# P22-B Abuse Controls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add deterministic layered application rate limits for every FastAPI API request without introducing distributed infrastructure or trusting proxy headers.

**Architecture:** A provider-neutral atomic rate-limiter contract is backed by a bounded in-process sliding-window adapter. FastAPI middleware derives global, transport-peer, credential-HMAC, mutation, and session-creation subjects and returns the canonical 429 envelope while existing request-correlation and security-header middleware remain outer boundaries.

**Tech Stack:** Python 3.12, FastAPI/Starlette, Pydantic settings, asyncio, pytest/httpx; no new dependency.

**Spec:** `docs/superpowers/specs/2026-10-30-p22b-abuse-controls-design.md`

## Global Constraints

- Cover every `/api/v1` request; exclude health and non-API paths.
- Never trust `Forwarded` or `X-Forwarded-For`.
- Never retain or emit raw bearer credentials.
- Keep state process-local, bounded, and explicitly non-distributed.
- Add no dependency, service, schema, migration, clinical behavior, P22-C/D/E, P23, or P24 scope.
- Keep `AC-P22-006` and P22 live acceptance unverified for production/fleet deployment.

## Review Focus

- Concurrent requests at the exact limit must not exceed the configured budget.
- A denied multi-layer decision must not partially consume capacity from another layer.
- Malformed authorization values must not create unbounded attacker-selected credential buckets.
- Forwarded-address spoofing must not change the direct-peer subject.
- Middleware failures and 429 responses must retain privacy-safe envelopes, request IDs, no-store, and security headers.

---

### Task 1: Typed settings and atomic limiter contracts

**Files:**
- Create: `backend/app/shared/rate_limits/contracts.py`
- Create: `backend/app/shared/rate_limits/in_memory.py`
- Create: `backend/app/shared/rate_limits/__init__.py`
- Modify: `backend/app/config/sections.py`
- Modify: `backend/app/config/settings.py`
- Modify: `backend/app/config/__init__.py`
- Test: `backend/tests/test_rate_limits.py`

**Interfaces:**
- Produces: `RateLimitRule`, `RateLimitSubject`, `RateLimitDecision`, `RateLimiter.check(subjects)`, `InMemorySlidingWindowRateLimiter`, and `RateLimitSettings`.

- [ ] Write failing direct-constructor, limit/retry, atomic multi-layer, concurrency, bounded-cardinality, and settings-validation tests.
- [ ] Run `python -m uv run pytest tests/test_rate_limits.py -q` and verify failures are caused by missing contracts.
- [ ] Implement immutable validated contracts and the minimal bounded atomic sliding-window adapter.
- [ ] Run the focused tests and verify they pass.

### Task 2: FastAPI middleware and composition

**Files:**
- Create: `backend/app/api/middleware/rate_limits.py`
- Modify: `backend/app/api/middleware/__init__.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_rate_limit_middleware.py`

**Interfaces:**
- Consumes: Task 1 contracts/settings.
- Produces: `RateLimitMiddleware` and optional `rate_limiter` injection in `create_app`.

- [ ] Write failing tests for API coverage, health exclusion, session/mutation layering, credential separation, malformed authorization, forwarded-header spoofing, canonical 429 headers/envelope, and limiter failure.
- [ ] Run `python -m uv run pytest tests/test_rate_limit_middleware.py -q` and verify expected failures.
- [ ] Implement middleware subject derivation, process-keyed HMAC, 429 response, and deliberate middleware ordering.
- [ ] Run middleware plus request-context/security-header tests and verify they pass.

### Task 3: Documentation and complete verification

**Files:**
- Modify: `docs/implementation/P22_B_SECURITY_CONTROLS_IMPLEMENTATION.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`
- Modify: `backend/README.md`

**Interfaces:**
- Consumes: Tasks 1–2 evidence.
- Produces: accurate operator configuration and remaining distributed/production boundary.

- [ ] Document budgets, environment overrides, non-distributed limits, privacy properties, and exact outstanding production evidence.
- [ ] Run backend and frontend quality gates, PostgreSQL integration, Docker/health, Playwright, Gitleaks/Trivy, and `git diff --check`.
- [ ] Request a fresh whole-branch security review and fix every Critical/Important finding with regression evidence.
- [ ] Commit, push the feature branch, open a PR without merging, and verify all six CI jobs on the exact SHA.
