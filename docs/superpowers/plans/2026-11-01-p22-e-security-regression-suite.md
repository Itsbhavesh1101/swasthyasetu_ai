# P22-E Security Regression Suite Implementation Plan

> Execute in the isolated `phase/p22-e-security-regression-suite` worktree from exact verified main.

**Goal:** Add a synthetic cross-boundary regression suite for the merged P22-B/C/D foundations
without changing production behavior.

**Architecture:** A single detached pytest module composes public API middleware, retention, restore,
and resilience contracts. Documentation records the bounded evidence and keeps live P22 acceptance
open.

**Tech stack:** Python 3.13, pytest, pytest-asyncio, FastAPI/httpx, existing application contracts.

---

### Task 1: Add adversarial composition tests

**File:** `backend/tests/test_p22_security_regression.py`

1. Add synthetic spies/fakes with call counters.
2. Prove API limiter failure blocks handler execution and sanitizes the response.
3. Prove disabled/tripped capabilities and blocked purge plans make zero downstream calls.
4. Prove control-plane decisions do not cross-authorize one another.
5. Prove an in-flight trip rejects a late result and restore reconciliation reblocks a purged
   generation.
6. Prove hostile canaries remain absent from returned surfaces.
7. Prove no P22 runtime registration, routes, reset, scheduler, or automatic activation exists.
8. Run the focused suite.

### Task 2: Record bounded evidence

**Files:**

- `docs/implementation/P22_E_SECURITY_REGRESSION_SUITE.md`
- `docs/implementation/38_PROGRESS_TRACKER.md`

Record exact scope, results, exclusions, and the continuing PARTIAL status. Do not claim live P22
acceptance or grant any human approval.

### Task 3: Verify and integrate

1. Run backend formatting, lint, typecheck, focused tests, and full backend tests.
2. Run frontend checks, Playwright, migration checks, Docker/PostgreSQL checks, Gitleaks, Trivy, and
   repository hygiene checks using the repository's established commands.
3. Commit and push the feature branch.
4. Open a PR, verify all six CI jobs on the exact SHA, merge only after green review, then verify all
   six jobs on the merge SHA.
