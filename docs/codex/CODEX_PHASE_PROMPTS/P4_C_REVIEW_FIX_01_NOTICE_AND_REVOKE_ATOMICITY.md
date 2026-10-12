# P4-C Review Fix 01 — Notice-Version Validation & Revoke/Outbox Rollback Proof

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P4-C-REVIEW-FIX-01`
**Phase:** P4-C — Consent Domain & APIs
**Current branch:** `phase/p4-c-consent-domain-apis`
**Expected current branch head:** `81e19218b4210210d78c0a88b21f6dece2e46139`
**Do not branch from main. Do not merge.**

## Review finding

The P4-C implementation is structurally sound and all six CI jobs are green, but two exact phase requirements are not fully enforced/proven yet:

```text
1. NoticeVersion is bounded/printable, but not strictly machine-readable.
   For example, "privacy v1" is currently accepted.

2. P4-C required a real PostgreSQL proof that an outbox failure during revoke rolls back both:
   - the consent REVOKED mutation, and
   - the ConsentRevoked outbox insert.
   Current PostgreSQL rollback injection covers grant, not revoke.
```

Fix only these two items.

## 1. Preflight

Run:

```text
git branch --show-current
git rev-parse HEAD
git status --short
```

Expected:

```text
branch: phase/p4-c-consent-domain-apis
HEAD: 81e19218b4210210d78c0a88b21f6dece2e46139
working tree: clean
```

If the branch legitimately advanced, inspect first and preserve valid work.

## 2. Harden NoticeVersion

P4-C promised:

```text
non-empty
trimmed/canonical
bounded
machine-readable
```

Use a stable ASCII machine-code grammar.

Recommended:

```regex
^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$
```

This should allow examples such as:

```text
privacy-v1
privacy_v2
notice.2026-10
V1
```

and reject:

```text
privacy v1
 privacy-v1
"privacy-v1 "
privacy/v1
empty
control characters
arbitrary Unicode whitespace
>64 chars
```

Do not silently normalize or lowercase malformed values.

Keep maximum length 64.

A different equally narrow grammar is acceptable if it remains machine-readable and supports `privacy-v1`.

## 3. NoticeVersion tests

Add/update tests proving valid and invalid examples above.

HTTP DTO validation for an invalid notice version must still return:

```text
422 VALIDATION_ERROR
```

without echoing the submitted value.

Do not change legal/privacy notice content.

## 4. Real PostgreSQL revoke rollback proof

Add a real PostgreSQL integration test proving revoke/outbox atomicity under an injected outbox failure.

Required flow:

```text
1. Grant a consent with normal OutboxRepository.
2. Confirm it is persisted GRANTED.
3. Create ConsentService with the same real DatabaseRuntime and a test OutboxRepository
   that raises only when enqueuing ConsentRevoked.
4. Call revoke_consent(...).
5. Expect the synthetic exception.
6. Open a fresh DB session.
7. Assert the consent is still:
      status = GRANTED
      revoked_at IS NULL
      revocation_reason IS NULL
8. Assert outbox contains:
      the committed ConsentGranted event
      ZERO ConsentRevoked events for that consent.
```

This test must use real PostgreSQL and `pytest.mark.postgres`.

Do not mock the DB transaction.

## 5. Failure injection

Use a narrow test helper. A valid pattern is:

```python
class FailOnConsentRevokedOutbox(OutboxRepository):
    async def enqueue(...):
        if str(event.event_type) == "ConsentRevoked":
            await super().enqueue(...)
            raise RuntimeError("synthetic revoke outbox rollback")
        return await super().enqueue(...)
```

The failure must happen after the outbox row is added/flushed, so rollback must remove both the consent update and event insert.

Avoid double enqueue on the normal path.

Equivalent clean implementations are acceptable.

## 6. Preserve current revoke tests

Keep current coverage for:

```text
successful revoke
repeat revoke -> INVALID_STATE_TRANSITION
concurrent revoke -> one success / one conflict
revoked consent fails consent.check
```

Do not weaken them.

## 7. Scope guard

Do NOT change:

```text
ConsentPurpose
ConsentStatus
ConsentSubjectType
scope semantics
subject authorization
API routes
module capabilities
schema/migration
actor FK
outbox envelope
P4-A sessions
P4-B identity/authz
Docker
Compose
frontend
dependencies
```

No new migration.

Alembic head remains:

```text
p4c_0005
```

## 8. Expected files

Keep repair narrow. Likely:

```text
backend/app/modules/consent/domain.py
backend/tests/test_consent.py
backend/tests/integration/test_postgres_consent.py
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P4_C_REVIEW_FIX_01_NOTICE_AND_REVOKE_ATOMICITY.md
```

Only add another test file if clearly cleaner.

No unrelated refactor.

## 9. Local verification

From `backend/`:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest tests/test_consent.py tests/test_consent_service.py -q
uv run pytest
uv run python -m compileall -q app tests
uv run pytest -m postgres
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini check
```

Expected head:

```text
p4c_0005
```

From repository root:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
```

## 10. Diff audit

Run:

```text
git status --short
git diff --stat
git diff
git diff --check

git diff -- backend/pyproject.toml backend/uv.lock package.json pnpm-lock.yaml
git diff -- backend/alembic.ini backend/migrations/
git diff -- deployments/local/compose.yaml infra/docker/backend.Dockerfile
```

Expected dependency/migration/Docker/Compose diffs:

```text
empty
```

## 11. Progress tracker

Before new remote CI is green, do not treat the repaired SHA as final verified closure.

After all six jobs pass, record:

```text
P4-C = COMPLETE
P4 = COMPLETE
review repair = VERIFIED
new final branch head
new CI run ID/URL
```

Preserve historical phase evidence.

## 12. Commit and push

Commit:

```text
fix: harden P4-C consent verification
```

Push the same branch:

```text
git push origin phase/p4-c-consent-domain-apis
```

Do not force-push.

Do not merge.

## 13. Remote CI

Because code/tests changed, verify a NEW GitHub Actions run on the new final head.

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

Do not use run `38157215896` as final closure evidence after this repair.

## 14. Final report

Return:

### STATUS

```text
COMPLETE / PARTIAL / BLOCKED / FAILED
```

### REVIEW FINDINGS FIXED

```text
NoticeVersion machine-readable validation
revoke/outbox PostgreSQL rollback proof
```

### BRANCH / GIT

```text
branch
previous head
repair commit
closure commit if any
remote head
main SHA
working tree
```

### NOTICE VERSION

Report:

```text
validation grammar
valid examples tested
invalid examples tested
HTTP validation behavior
```

### REVOKE / OUTBOX ATOMICITY

Report exact PostgreSQL evidence:

```text
pre-failure state
injected failure point
exception
post-failure status
revoked_at
revocation_reason
ConsentGranted count
ConsentRevoked count
```

### FILES CHANGED

Exact files.

### TESTS

Report focused, full backend, PostgreSQL, and P4-A/P4-B regression.

### DEPENDENCY / MIGRATION DIFF

Confirm:

```text
no dependency change
no migration change
head p4c_0005
```

### VERIFICATION

Report all local gates.

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
overall
```

### P4 FINAL ACCEPTANCE

Confirm AC-P4-001 through AC-P4-010 remain PASS.

### MERGE

```text
MERGE PERFORMED: NO
```

Stop after this review repair.
