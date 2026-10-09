# SwasthyaSetu AI — CODEX_WORKFLOW

**Document ID:** SSAI-CODEX-002  
**Status:** Permanent implementation workflow  
**Version:** 1.0.0-draft

## 1. Standard loop

Every implementation task follows:

`READ -> AUDIT -> PLAN -> IMPLEMENT -> TEST -> DIFF AUDIT -> VERIFY ACCEPTANCE -> REPORT`

Do not jump directly from prompt to code.

## 2. READ

Read the context pack specified by the prompt.

Always include:

- `docs/00_PROJECT_MASTER_SPEC.md`
- `docs/02_SYSTEM_ARCHITECTURE.md`
- `docs/29_ENGINEERING_STANDARDS.md`
- `docs/34_MASTER_IMPLEMENTATION_PLAN.md`
- `docs/codex/CODEX_INSTRUCTIONS.md`
- `docs/codex/CODEX_CONTEXT_RULES.md`

Then read relevant PRD requirement sections, phase/module specs, database/API/domain specs, and acceptance criteria.

Produce a concise internal understanding of the requested scope.

## 3. AUDIT

Inspect the actual repository:

- current branch;
- `git status --short`;
- relevant directories/files;
- module public interfaces;
- tests;
- migrations;
- config;
- dependencies;
- current progress status.

Classify the requested functionality as absent, partial, complete, or conflicting.

Before editing, summarize:

- current state;
- relevant modules;
- what is missing;
- potential conflicts;
- likely files affected.

## 4. PLAN

Map the requested work through the architecture:

`requirement -> module -> contracts -> domain -> persistence -> API -> UI -> tests`

State:

`IN SCOPE`

and

`OUT OF SCOPE`

Identify database migrations, external adapters, dependencies, safety implications, privacy implications, and rollback/degraded behavior.

## 5. STOP CONDITIONS

Stop and return `BLOCKED` when:

- clinical policy is missing for real behavior;
- a material architecture conflict requires an ADR;
- required external data/credentials are unavailable and a safe mock cannot satisfy scope;
- a lower-priority prompt conflicts with higher-priority safety/specification;
- repository state is unsafe to modify.

Do not guess.

## 6. IMPLEMENT

Implement the smallest coherent change that fully satisfies the requested scope.

Preferred order where applicable:

`contracts/types -> domain -> persistence -> application service -> adapters -> API -> frontend -> tests`

Preserve architecture and existing behavior.

## 7. DATABASE WORKFLOW

For persistent changes:

1. inspect current schema;
2. update models/domain persistence;
3. create migration;
4. inspect migration;
5. run migration;
6. run relevant integration tests;
7. update schema documentation.

Check for accidental drops, nullability changes, indexes, constraints, and multiple Alembic heads.

## 8. API WORKFLOW

For API changes:

1. update typed request/response contracts;
2. update application service;
3. update route;
4. verify OpenAPI;
5. update typed frontend/client contracts;
6. add contract tests.

Do not let frontend behavior become the undocumented API specification.

## 9. EXTERNAL ADAPTER WORKFLOW

For external integrations:

1. define/confirm port;
2. implement adapter;
3. map provider-specific errors;
4. configure explicit timeout;
5. configure bounded retry where appropriate;
6. implement mock/sandbox adapter;
7. add contract tests;
8. add telemetry;
9. define degraded behavior.

Provider-specific objects must not leak into domain logic.

## 10. LLM WORKFLOW

For LLM tasks:

`task contract -> prompt version -> structured schema -> adapter call -> parse -> validation -> provenance -> domain use -> regression tests`

Do not pass unvalidated model output into safety logic.

## 11. SAFETY WORKFLOW

For safety work:

`structured input -> deterministic policy -> hard overrides -> reason codes -> policy version -> output`

Tests must cover trigger, non-trigger, ambiguity, precedence, and failure mode.

## 12. FRONTEND WORKFLOW

For frontend changes:

`typed API -> loading/error/empty states -> UI -> auth/feature state -> accessibility -> responsive behavior -> tests`

Do not implement backend clinical policy in React.

## 13. TEST

Run the phase-specific quality gates.

Typical order:

1. formatting;
2. lint;
3. typecheck;
4. unit tests;
5. integration tests;
6. contract tests;
7. frontend tests;
8. safety/E2E tests where applicable.

Targeted tests may be used during debugging, but final relevant gates must run before completion.

## 14. TEST FAILURES

When a test fails:

1. understand root cause;
2. determine whether implementation or test is wrong;
3. fix the correct side;
4. rerun;
5. run the relevant suite.

Do not delete, skip, or weaken a valid test just to pass CI.

Safety-test failure blocks completion.

## 15. DIFF AUDIT

After implementation run:

- `git status --short`
- `git diff --stat`
- `git diff`

Inspect all changed files, migrations, dependency files, config, and generated artifacts.

Look for unrelated edits, secrets, debug code, accidental schema changes, dead code, or unsafe TODOs.

## 16. DEPENDENCY AUDIT

If a dependency changed, report:

- name;
- version;
- purpose;
- why existing dependencies were insufficient.

Ensure lockfile is updated.

## 17. VERIFY ACCEPTANCE

Open the phase acceptance criteria and mark each required criterion:

- PASS
- FAIL
- NOT APPLICABLE
- BLOCKED

A phase cannot be COMPLETE if a mandatory criterion is FAIL or BLOCKED.

## 18. REPORT

Return:

`STATUS: COMPLETE | PARTIAL | BLOCKED | FAILED`

Then:

1. Summary
2. Requirement IDs
3. Files created
4. Files modified
5. Migrations
6. API/contract changes
7. Tests added
8. Commands run
9. Results
10. Dependencies changed
11. Architecture deviations
12. Safety/privacy impact
13. Known limitations
14. Remaining work

## 19. BUG-FIX WORKFLOW

`reproduce -> failing regression test -> root cause -> minimal fix -> targeted test -> relevant suite -> diff audit -> report`

Safety defects always get a regression test.

## 20. REFACTOR WORKFLOW

Refactor only when explicitly requested or required for current scope. Capture existing behavior in tests first. Preserve external behavior unless an intentional contract change is part of scope.

## 21. NEW-FEATURE WORKFLOW

`feature proposal -> requirement IDs -> module ownership -> architecture/dependency review -> safety/privacy review -> acceptance criteria -> implementation prompt -> standard workflow`

Do not start with random coding.

## 22. MODEL WORKFLOW

`dataset spec -> validation -> split -> preprocessing -> classical baseline -> train -> evaluate -> artifacts -> model card -> registry`

QML additionally requires quantum encoding/backend/circuit metadata and fair comparison.

No model becomes production-active automatically.

## 23. EXTERNAL-INTEGRATION WORKFLOW

`approved integration spec -> port -> mock -> sandbox -> contract tests -> failure/security/privacy review -> production config`

Do not begin from hard-coded live credentials.

## 24. CLINICAL-POLICY WORKFLOW

`approved policy source -> machine-readable policy -> schema validation -> evaluator -> reason codes -> golden tests -> version activation -> rollback`

Codex implements policy; it does not invent policy.

## 25. DOCUMENT/OCR WORKFLOW

`upload validation -> object storage -> processing state -> OCR adapter -> parser -> candidate facts -> provenance -> human confirmation`

OCR never silently overwrites clinician-confirmed information.

## 26. SELF-CARE WORKFLOW

`safety -> eligibility -> contraindications -> approved knowledge -> patient-context filtering -> output -> escalation advice`

If required safety information is unavailable, choose clarification/safer behavior.

## 27. MENTAL-HEALTH WORKFLOW

`urgent-help shortcut -> local safety backstop -> structured extractor -> schema validation -> deterministic policy -> verified resources/referral`

LLM outage must not remove crisis fallback.

## 28. RELEASE WORKFLOW

Later release flow:

`CI -> migration validation -> security scan -> safety suite -> staging -> E2E -> clinical/config approval -> deployment -> observation -> rollback if needed`

## 29. Final principle

Behave like a disciplined engineer maintaining a long-lived healthcare platform, not like a generator maximizing the number of changed files.
