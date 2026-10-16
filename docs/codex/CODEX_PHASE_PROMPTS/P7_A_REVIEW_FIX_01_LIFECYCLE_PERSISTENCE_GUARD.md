# P7-A Review Fix 01 — Lifecycle Persistence Guard

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P7-A-REVIEW-FIX-01`
**Phase:** P7-A — Intake Domain / Schema
**Current branch:** `phase/p7-a-intake-domain-schema`
**Reviewed head:** `258c64905fc26ba8729cfc9f6b404cc07f3f199a`

Do not create a new branch.
Do not merge.
Do not continue into P7-B.

## Review Finding

`PostgresClinicalIntakeRepository.save()` can currently persist a manually constructed intake state without independently validating the transition against the authoritative persisted status.

This allows the persistence layer to bypass the canonical P7-A lifecycle if a caller constructs an invalid aggregate state manually.

Canonical lifecycle:

```text
IN_PROGRESS -> COMPLETED
IN_PROGRESS -> ABANDONED
```

Terminal states:

```text
COMPLETED
ABANDONED
```

Normal editable state:

```text
IN_PROGRESS -> IN_PROGRESS
```

## Required Fix

Harden `PostgresClinicalIntakeRepository.save()` so it validates the requested mutation against the authoritative persisted row before changing any stored fields.

Required behavior:

```text
IN_PROGRESS -> IN_PROGRESS   ALLOWED
IN_PROGRESS -> COMPLETED     ALLOWED
IN_PROGRESS -> ABANDONED     ALLOWED

COMPLETED -> COMPLETED       REJECT
COMPLETED -> IN_PROGRESS     REJECT
COMPLETED -> ABANDONED       REJECT

ABANDONED -> ABANDONED       REJECT
ABANDONED -> IN_PROGRESS     REJECT
ABANDONED -> COMPLETED       REJECT
```

A terminal intake must be immutable through this repository path.

That includes rejecting attempts to modify:

```text
chief_complaint
hpi
history_sections
missing_information
contradictions
completed_at
status
```

after the persisted intake is already `COMPLETED` or `ABANDONED`.

## Implementation Rule

Do not trust only the incoming `ClinicalIntake`.

After loading the row using:

```text
intake_id
expected_version
FOR UPDATE
```

the repository must use the persisted authoritative status to validate the mutation before changing any record field.

Prefer reusing the canonical domain lifecycle semantics rather than introducing a second weaker transition policy.

A small internal helper is acceptable if needed, but it must remain consistent with `ClinicalIntake.transition_to()`.

Do not weaken optimistic concurrency.

## Error Behavior

Use a deterministic typed/domain error for invalid lifecycle persistence.

Prefer the existing:

```text
InvalidClinicalIntakeTransitionError
```

if it cleanly represents this failure.

Do not leak clinical payload values in error messages.

Do not introduce a new public HTTP error because P7-A has no API layer.

## Required PostgreSQL Tests

Add real PostgreSQL integration coverage proving:

### Invalid terminal transitions

```text
ABANDONED -> COMPLETED      rejected
ABANDONED -> IN_PROGRESS    rejected
COMPLETED -> IN_PROGRESS    rejected
COMPLETED -> ABANDONED      rejected
```

### Terminal mutation protection

Persist a terminal intake, then attempt to manually modify one or more structured fields while keeping/reusing a terminal status.

The write must be rejected.

Verify from a fresh session:

```text
stored status unchanged
stored structured content unchanged
stored completed_at unchanged
stored version unchanged
```

### Valid behavior remains

Prove:

```text
IN_PROGRESS -> IN_PROGRESS structured edit succeeds
IN_PROGRESS -> COMPLETED succeeds
IN_PROGRESS -> ABANDONED succeeds
version increments exactly once for valid saves
```

### Rollback / concurrency regression

Existing:

```text
stale-write rejection
caller transaction behavior
atomic rollback
identity immutability
UTC validation
```

must remain green.

## Scope Guard

Do NOT change:

```text
domain lifecycle states
database schema
migration
Alembic revision
question/answer contracts
question-pack registry
serialization versions
module capabilities
runtime registration
API layer
application layer
frontend
dependencies
P7-B adaptive engine
clinical question content
AYUSH content
safety logic
AI logic
```

Alembic head must remain:

```text
p7a_0007
```

Expected dependency files unchanged:

```text
backend/pyproject.toml
backend/uv.lock
package.json
pnpm-lock.yaml
```

Expected migration diff:

```text
none
```

## Likely Files

Keep the repair narrow.

Likely:

```text
backend/app/modules/clinical_intake/infrastructure.py
backend/tests/integration/test_postgres_clinical_intake.py
backend/tests/test_clinical_intake_domain.py
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P7_A_REVIEW_FIX_01_LIFECYCLE_PERSISTENCE_GUARD.md
```

Do not modify unrelated files.

## Verification

Run:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run pytest -m postgres
uv run python -m compileall -q app tests
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini check
```

Expected Alembic head:

```text
p7a_0007
```

From repository root:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
git diff --check
```

Audit:

```text
no dependency changes
no migration changes
no frontend changes
no P7-B implementation
```

## Commit / Push

Commit on the same branch:

```text
git add <repair files only>
git commit -m "fix: enforce P7-A intake lifecycle persistence"
git push origin phase/p7-a-intake-domain-schema
```

Do not force-push.

Do not merge.

## Remote CI

Verify a new final-tip CI run.

All six required jobs must pass:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

## Final Report

Return only:

```text
STATUS
BRANCH / GIT
LIFECYCLE GUARD
TERMINAL MUTATION PROTECTION
POSTGRESQL TESTS
DEPENDENCY / MIGRATION STATUS
VERIFICATION
CI
P7-A STATUS
MERGE
```

`MERGE` must be:

```text
MERGE PERFORMED: NO
```

Stop after this repair.
