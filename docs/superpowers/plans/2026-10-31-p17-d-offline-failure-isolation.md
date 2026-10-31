# P17-D Offline Failure-Isolation Evidence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Prove with real PostgreSQL transactions that synthetic ABDM rejection, unavailability, and adapter failure cannot erase or block locally committed P7 intake data.

**Architecture:** Add tests only. Persist a minimal synthetic P7 intake and skipped answer through the real PostgreSQL repositories, commit before invoking the test-only P17-B adapter, exercise failure outcomes outside the transaction, reload through a fresh database session, and then complete the intake through a new transaction. Do not add a production orchestrator or any P17-C behavior.

**Tech Stack:** Python 3.12, pytest, SQLAlchemy/PostgreSQL integration fixtures, existing P7 repositories, existing P17-A contracts and P17-B test adapter.

---

### Task 1: Real PostgreSQL failure-isolation tests

**Files:**
- Create: `backend/tests/integration/test_postgres_abdm_failure_isolation.py`

1. Build a database fixture with the existing migration schema and bounded cleanup.
2. Persist a minimal content-free P7 intake and skipped answer in one committed transaction.
3. Exercise P17-B rejected and unavailable results outside the database transaction; reload and assert exact intake/answer preservation.
4. Exercise a content-free adapter clock exception; reload and assert preservation.
5. After each adapter failure, complete and save the same intake in a new transaction and assert the P7 version/status advance.
6. Run collection, Ruff and mypy locally; the test must skip cleanly without a configured database and execute in the mandatory PostgreSQL CI job.

### Task 2: Scope and acceptance documentation

**Files:**
- Create: `docs/implementation/P17_D_OFFLINE_FAILURE_ISOLATION.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

1. Record the exact base SHA, tests-only scope, real transaction boundary and negative scope.
2. State that this is bounded evidence toward `FR-ABDM-005` only and does not satisfy live `AC-P17-005` or any other live P17 criterion.
3. Keep P17 partial and P17-C blocked.

### Task 3: Full verification and integration

1. Run backend format, lint, mypy, complete non-database pytest, compile/import smoke and Alembic-head checks.
2. Run unchanged frontend format, lint, typecheck, tests, builds and Playwright discovery.
3. Validate Compose configuration and diff scope.
4. Commit once, push, open a PR and require all six CI jobs; confirm the PostgreSQL test executes rather than skips.
5. Merge only after feature CI passes, then require all six jobs on the resulting main SHA.

## Review Focus

- Local writes must commit before adapter invocation; no fake remote/local atomicity claim.
- Adapter failure must occur outside the database transaction.
- Verification must use fresh sessions and real repositories, not retained Python objects.
- P7 must remain writable after failure, not merely readable.
- Test data must remain synthetic and content-free.
- No production code, migration, dependency, network, retry, callback, consent or synchronization behavior may be added.
