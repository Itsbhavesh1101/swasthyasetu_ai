# P3-C Review Fix 01 — Enforce UTC Worker Clock Semantics

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P3-C-REVIEW-FIX-01`
**Phase:** P3-C — Jobs, Worker Abstraction & Object Storage
**Current phase branch:** `phase/p3-c-jobs-object-storage`
**Expected current branch head:** `a8ea9c3a386a5bb205d026527947a7a75990aec0`
**Do not branch from main. Do not merge.**

## Review finding

The P3-C implementation is otherwise acceptable, but one phase contract is not fully enforced.

The phase prompt requires worker clock values and job-state timestamps to be timezone-aware and UTC, and specifically requires naive injected clock values to be rejected.

Current implementation in:

```text
backend/app/jobs/worker.py
backend/app/jobs/in_process.py
```

passes raw `clock()` values directly to `claim_first_due()`, `mark_succeeded()`, and `mark_failed()`.

This allows two incorrect behaviors:

```text
1. a naive injected clock can fail only indirectly during aware-vs-naive datetime comparison;
2. an aware non-UTC clock can be stored directly in started_at/completed_at without UTC normalization.
```

Fix only this issue and its tests/evidence.

## Preflight

From repository root:

```text
git branch --show-current
git rev-parse HEAD
git status --short
```

Expected:

```text
branch: phase/p3-c-jobs-object-storage
HEAD: a8ea9c3a386a5bb205d026527947a7a75990aec0
working tree: clean
```

If the branch has legitimately advanced, inspect first. Preserve legitimate work.

## Required invariant

Enforce:

```text
all worker/backend job-state timestamps are timezone-aware and normalized to UTC
```

This includes:

```text
claim time
started_at
completed_at
```

A naive datetime must raise a deliberate:

```text
ValueError
```

with a safe message mentioning that a timezone-aware datetime is required.

Do not rely on incidental Python comparison `TypeError`.

## Preferred implementation

Use a small private helper, conceptually:

```python
def _aware_utc(name: str, value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value.astimezone(UTC)
```

You may reuse/refactor an existing truly generic helper if the change stays narrow.

Do not import private helpers across inappropriate boundaries.

## Worker clock

`InProcessWorker` should obtain time through a normalized helper such as:

```python
def _now(self) -> datetime:
    ...
```

Requirements:

```text
call injected clock
reject naive datetime
normalize aware datetime to UTC
```

Use the normalized value for claim/failure/success timestamps.

Do not change the public worker contract.

## Backend defensive validation

Also ensure `InProcessJobBackend` cannot store invalid timestamps when its implementation methods are called directly:

```text
claim_first_due(now)
mark_succeeded(..., completed_at)
mark_failed(..., completed_at)
```

Preferred behavior:

```text
validate/normalize these values at the backend boundary too
```

so snapshots can never contain naive/non-UTC job-state timestamps.

## Invalid-clock state safety

Test this exact behavior:

```text
job starts QUEUED
worker uses naive clock
run_once raises ValueError mentioning timezone-aware
job remains QUEUED
started_at is None
completed_at is None
```

Do not convert an invalid infrastructure clock into FAILED.

## UTC normalization test

Use a deterministic non-UTC aware clock, for example:

```text
2026-01-02T08:34:00+05:30
```

Verify stored snapshot timestamps are normalized to UTC while preserving the same instant.

At minimum verify:

```text
started_at.utcoffset() == timedelta(0)
completed_at.utcoffset() == timedelta(0)
expected UTC instant preserved
```

## Existing behavior to preserve

Do not weaken or remove:

```text
worker smoke
future scheduling
FIFO among due jobs
duplicate job ID protection
missing-handler safe failure
handler-exception privacy
worker continues after failed job
object-storage tests/security
P3-A/P3-B regressions
```

## Scope guard

Do NOT change:

```text
ObjectStoragePort / local storage behavior
JobDispatcher protocol
JobRequest fields
JobStatus values
outbox
database schema
Alembic migrations
Docker
Compose
frontend
dependencies
```

Do not implement retries, durable queue, jobs table, worker daemon, Procrastinate, Redis/Valkey, or P4.

## Expected dependency / migration state

These must remain unchanged:

```text
backend/pyproject.toml
backend/uv.lock
package.json
pnpm-lock.yaml
backend/alembic.ini
backend/migrations/**
```

Alembic head remains:

```text
p3b_0002
```

## Verification

From `backend/` run:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest tests/test_jobs.py -q
uv run pytest
uv run python -m compileall -q app tests
uv run alembic -c alembic.ini heads
```

Expected migration head:

```text
p3b_0002
```

From repository root run:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

Also run the explicit PostgreSQL regression when the test DB is available:

```text
uv run pytest -m postgres
```

## Diff audit

Run:

```text
git status --short
git diff --stat
git diff
git diff --check

git diff -- backend/pyproject.toml backend/uv.lock package.json pnpm-lock.yaml
git diff -- backend/alembic.ini backend/migrations/
```

Keep the fix narrowly scoped to the worker/backend timestamp invariant and tests.

## Commit and push

Commit:

```text
fix: enforce UTC job worker timestamps
```

Push the same branch:

```text
git push origin phase/p3-c-jobs-object-storage
```

Do not merge.

Do not force-push.

## Remote CI

Because code changes after the previously green closure SHA, verify a NEW CI run on the new head.

Required jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

All six must pass.

Do not cite the old run as final closure evidence.

## Progress tracker

Before new CI is green, do not claim reviewed closure for the new SHA.

After green CI, keep:

```text
P3-C = COMPLETE
P3 = COMPLETE
next = P4-A — Sessions
```

and record the new final head/run as current closure evidence.

## Final report

Return these sections:

### STATUS

```text
COMPLETE / PARTIAL / BLOCKED / FAILED
```

### REVIEW FINDING FIXED

Report:

```text
naive clock rejection
UTC normalization
backend timestamp invariant
invalid-clock partial-state behavior
```

### BRANCH / GIT

Report:

```text
branch
previous head
new fix SHA
remote SHA
main SHA
working tree
```

### FILES CHANGED

Exact files.

### TESTS

Report:

```text
targeted job tests
full backend tests
PostgreSQL regression
frontend regression
```

### VERIFICATION

Report all required local checks.

### DEPENDENCY / MIGRATION DIFF

Confirm:

```text
dependencies unchanged
migration head p3b_0002
no migration changes
```

### CI

Report NEW run:

```text
run ID
URL
head SHA
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
overall result
```

### P3 ACCEPTANCE

Confirm AC-P3-001 through AC-P3-010 remain PASS.

### MERGE

```text
MERGE PERFORMED: NO
```

Stop after this review fix.
