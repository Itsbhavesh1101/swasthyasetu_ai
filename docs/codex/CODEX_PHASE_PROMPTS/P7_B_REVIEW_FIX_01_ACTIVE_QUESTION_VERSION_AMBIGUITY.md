# P7-B Review Fix 01 — Active Question-Version Ambiguity Guard

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P7-B-REVIEW-FIX-01`
**Phase:** P7-B — Deterministic Adaptive Engine
**Current branch:** `phase/p7-b-deterministic-adaptive-engine`
**Reviewed head:** `9280523bb76593ee2ee140294329a1ff7e9a86ee`

Do not create a new branch.
Do not merge.
Do not continue into P7-C.

## Review Finding

The active-pack ambiguity guard currently treats question identity as:

```text
(question_id, question_version)
```

while the P7-B rule language and engine state resolve questions/answers primarily by:

```text
question_id
```

Examples include:

```text
RuleEvaluationContext.answers[question_id]
_latest_answers() keyed by question_id
rule operands: question:<question_id>
dependency_question_ids
```

Therefore two simultaneously activated packs can currently contain:

```text
same question_id
different question_version
```

without being rejected.

That creates an ambiguous active engine namespace: one version can overwrite/stand in for another in question-ID keyed evaluation.

This can cause the wrong response to satisfy applicability, dependency, missing-information, or selection logic.

## Required Fix

Eliminate active question-version ambiguity.

Because the rule grammar intentionally addresses questions by `question_id`, enforce:

```text
Within one activated engine pack set, each question_id must be unique,
regardless of question_version.
```

Structural registry storage may still contain different versions in different non-simultaneously-active packs if needed.

But `PackRegistry.activate(...)` must reject any selected set where the same `question_id` appears more than once, even when versions differ.

Do not silently choose one version.

Do not use selected-pack input order to decide precedence.

## Canonical Behavior

Allowed:

```text
registered:
  pack A -> synthetic.duration v1
  pack B -> synthetic.duration v2

activate only pack A -> allowed
activate only pack B -> allowed
```

Rejected:

```text
activate pack A + pack B simultaneously
when both expose synthetic.duration,
even if one is v1 and the other is v2
```

Continue rejecting exact duplicate identities.

## Engine Safety

After enforcing the activation invariant, verify:

```text
_latest_answers()
RuleEvaluationContext.answers
EXISTS / EQUALS / IN
ANSWER_DISPOSITION
dependency resolution
missing-information calculation
next-question selection
```

cannot observe two active versions of the same question ID.

Do not redesign the rule grammar in this repair.

Keep the repair narrow.

## Required Tests

Add focused tests proving:

### Active-pack ambiguity

```text
pack A:
  question_id = synthetic.shared
  question_version = 1.0.0

pack B:
  question_id = synthetic.shared
  question_version = 2.0.0
```

Then:

```text
activate A only -> PASS
activate B only -> PASS
activate A + B -> typed validation failure
activate B + A -> same typed validation failure
```

The rejection must be independent of caller order.

### Engine determinism

Prove no engine evaluation can proceed with two active versions of the same question ID.

### Existing behavior remains

Keep green:

```text
different question IDs across packs
deterministic activation
specialty pack evaluation
complaint pack evaluation
AYUSH structural registration
history reuse
rule evaluation
answer validation
stable tie-breaking
```

## Error Behavior

Use the existing structural/activation error type where appropriate, preferably:

```text
InvalidQuestionPackError
```

or the existing activation eligibility error if that better fits the current contract.

Do not expose answer content.

## Scope Guard

Do NOT change:

```text
engine result variants
rule operator set
database schema
migration
Alembic revision
P7-A lifecycle/persistence
FastAPI
application layer
frontend
BFF
dependencies
production question content
clinical policy
AYUSH production content
AI/LLM
P7-C scope
```

Alembic head remains:

```text
p7a_0007
```

Expected unchanged:

```text
backend/pyproject.toml
backend/uv.lock
package.json
pnpm-lock.yaml
backend/migrations/**
apps/**
```

## Likely Files

Keep changes narrow, likely:

```text
backend/app/modules/clinical_intake/pack_validation.py
backend/app/modules/clinical_intake/contracts.py
backend/tests/test_clinical_intake_pack_validation.py
backend/tests/test_clinical_intake_engine.py
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P7_B_REVIEW_FIX_01_ACTIVE_QUESTION_VERSION_AMBIGUITY.md
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

From repository root:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
git diff --check
```

Audit:

```text
no migrations
no schema changes
no dependencies
no frontend
no API/application layer
no P7-C implementation
Alembic head p7a_0007
```

## Commit / Push

Commit on the same branch:

```text
git add <repair files only>
git commit -m "fix: reject ambiguous active intake question versions"
git push origin phase/p7-b-deterministic-adaptive-engine
```

Do not force-push.

Do not merge.

## Remote CI

Verify the final branch tip.

All six jobs must pass:

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
AMBIGUITY GUARD
ACTIVE QUESTION IDENTITY
TESTS
DEPENDENCY / MIGRATION STATUS
VERIFICATION
CI
P7-B STATUS
MERGE
```

`MERGE`:

```text
MERGE PERFORMED: NO
```

Stop after this repair.
