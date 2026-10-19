# SwasthyaSetu AI â€” Codex Phase Prompt: P8-C Guarded Intake Integration, API/BFF/UI & Regression Evidence

**Work unit:** P8-C only â€” integration of the existing P8-A provider-neutral gateway and P8-B clinical-intake extraction package into a governed P7 intake flow **only to the extent authorized by current approved specifications**.

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified baseline:** `main @ ad3bb6cd709e2f403e6e798d1bac31f9477eaf23`
**Merge evidence:** P8-B PR #24 merged at this exact SHA; reviewed head `2a623dd4398ec3b522c01399042475d3864e1a35` had all six CI jobs green.
**Feature branch:** `phase/p8-c-guarded-clinical-intake-integration` (or a clearly named existing equivalent if already created).
**Current Alembic head:** `p7a_0007` unless a separately approved persistence decision explicitly changes it.
**PR discipline:** Push branch and open PR against `main`; **DO NOT MERGE**. Await independent review.

> **NON-NEGOTIABLE GOVERNANCE GATE:** Current authoritative `docs/14_LLM_EXTRACTION_SPEC.md` Â§Â§11â€“12 and `docs/26_PRIVACY_CONSENT_SPEC.md` Â§Â§5â€“7, 9, 12 leave actual message persistence/retention, deletion/withdrawal consistency, external-model data processing, extra consent/notice and clinical confirmation **UNAPPROVED / OPEN DESIGN DECISION**. P8-B's prompt is `ENGINEERING_ONLY` with `ADAPTER_ROLE_BINDING_NOT_VERIFIED`; its semantic validator accepts only a tiny finite set of synthetic example forms, **not arbitrary real patient utterances**. Passing offline tests cannot approve real-patient processing. **Do not turn on patient-facing conversational AI, send patient data to a live model, persist conversation messages, or auto-create clinical answers/facts merely because this is the P8-C phase.** If implementing the full feature requires unresolved authorization, complete only the safe subset below and report **PARTIAL / BLOCKED**, never `COMPLETE`.

## 0. Preflight and required reading â€” stop on drift

1. Verify clean worktree; current local and `origin/main` equal `ad3bb6cd709e2f403e6e798d1bac31f9477eaf23`; confirm PR #24 MERGED at that SHA, P8-A/B imports and tests pass, Alembic head `p7a_0007`. If dirty, baseline differs, specs conflict, or other contributions overlap, **STOP: BLOCKED**, without reset/rebase/discard.
2. Create the feature branch from exact baseline. Follow repository canonical READ â†’ AUDIT â†’ PLAN â†’ IMPLEMENT â†’ TEST â†’ DIFF AUDIT â†’ VERIFY â†’ REPORT.
3. Read *actual current repository files*, preserving source-of-truth precedence:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md
docs/05_DATABASE_SCHEMA.md
docs/06_API_CONTRACTS.md
docs/07_CLINICAL_INTAKE_SPEC.md
docs/13_AI_ORCHESTRATION_SPEC.md
docs/14_LLM_EXTRACTION_SPEC.md
docs/22_UX_AND_USER_FLOWS.md
docs/23_PATIENT_APP_SPEC.md
docs/26_PRIVACY_CONSENT_SPEC.md
docs/29_ENGINEERING_STANDARDS.md
docs/30_TESTING_STRATEGY.md
docs/33_ERROR_HANDLING_POLICY.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md
docs/codex/CODEX_CONTEXT_RULES.md
docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
```

Minimum live architecture audit:

```text
backend/app/main.py
backend/app/modules/ai_orchestration/{contracts,providers,application,public,telemetry}.py
backend/app/adapters/ai/{disabled,fake}.py
backend/app/modules/clinical_intake/{api,application,public,contracts,domain,engine,infrastructure,serialization,content}.py
backend/app/modules/clinical_intake/extraction/{contracts,prompts,validation,application}.py
backend/app/modules/{sessions,consent,encounters,patients,provenance}/public.py
backend/app/api/{errors,security}/**
backend/app/shared/{capabilities,modules,errors,observability}/**
backend/tests/test_clinical_intake_*.py
backend/tests/test_ai_*.py
apps/patient-web/lib/intake/{contracts,server,client}.ts
apps/patient-web/app/api/intake/**
apps/patient-web/app/intake/**
apps/patient-web/components/intake/**
apps/patient-web/tests/{intake-bff,intake-ui,browser-boundaries,pwa-baseline}.test*
.github/workflows/**
```

Audit real file paths before editing; glob names above are inspection hints, not permission to invent nonexistent files.

## 1. Stage-zero REQUIRED: explicit implementation/approval decision matrix

Before editing the application, write a compact evidence table in `docs/implementation/P8_C_INTEGRATION_GATE_REVIEW.md` (new doc in this PR; do not claim acceptance prematurely). For every row name the **authoritative approval** document, owner, decision ID/date, scope and status. **Do not manufacture approvals** or treat current engineering docs, feature flags or `privacy-v1` as consent for AI processing.

| Required gate | Current baseline and expected decision |
|---|---|
| **Clinical extraction semantics and source support** | P8-B synthetic literal-only grammar; **not** approved for arbitrary clinical utterances. Require documented clinical evaluation, schema/prompt approval and confirmation semantics before real-patient use. |
| **Trusted instruction-role binding** | `PromptRoleAssurance.ADAPTER_ROLE_BINDING_NOT_VERIFIED`. No approved live adapter; document test-only offline evidence, NOT production injection assurance. |
| **Data-processing purpose and consent** | `GENERAL_PRODUCT_USE`/`clinical_intake`/`privacy-v1` authorizes existing **first-party deterministic** P7 only; not transitive to third-party model use or a new message-processing purpose without review. Determine whether new first-party conversational collection is covered by an approved notice or needs update; **do not assume**. |
| **Message persistence and retention** | No approved raw utterance/message/candidate storage model, retention or deletion; choose only after privacy/security sign-off; do not add tables yet. |
| **Withdrawal/in-flight behavior** | Explicit cancellation, revalidation and persistence policy required; do not assume completed provider output may be stored after withdrawal. |
| **Mutation/idempotency semantics** | API `POST /api/v1/intakes/{intake_id}/messages` is DESIGN ONLY; define expected_version, message identity, replay/conflict/no-result recovery before enabling. |
| **Object-level auth and ownership** | Reuse P7 exact bearer + SESSION consent, exact encounter/intake ownership, lifecycle and nonenumerating errors. Must be independently proven with real PostgreSQL tests before route activation. |
| **No external patient egress** | Hard ban pending explicit provider/model/deployment/region/security/legal/DPA/consent gate. There is no approved live provider in P8-A/B. |
| **No authoritative clinical writes** | Patient confirmation is not clinician verification; P8 outputs may not create `IntakeAnswer`, canonical `ClinicalFact`, diagnosis, safety/triage route or clinician summary without separately approved reconciliation. |
| **User-facing clinical copy** | No approved live conversational interpretation. UI must not advertise â€œmedical assistantâ€, â€œAI checkedâ€, â€œsafeâ€, â€œtriagedâ€, â€œsavedâ€ or â€œclinician reviewedâ€. Generic fallback/urgent-help is preserved. |

**Decision algorithm:**

- If a required decision has an explicit accepted canonical approval **with compatible implementation details**, proceed **only within that exact approved scope**. Preserve evidence with citations to repository paths/sections.
- If a decision is missing (expected on this baseline), **do not invent it**. Implement the **Stage 2 safe engineering subset** (below), record the rest as `BLOCKED / NOT YET VERIFIED`, and submit a truthful PR for this safe subset only. Do not implement an accessible real-patient `/messages` API or a patient-entered AI chat in this condition.
- If the remaining safe subset cannot be useful without processing arbitrary patient data or inventing clinical policy, leave code unchanged, deliver the decision document plus a narrowly tested integration test plan, and report `BLOCKED` with concrete questions for human approval. This is preferable to a misleading demo.

## 2. Stage 2: safe P8-C engineering subset â€” no patient-facing AI activation

Implement the narrowest **internal, offline synthetic-fixture orchestration/evidence harness** that exercises P8-A + P8-B and P7's **read-only** state boundaries, where feasible without unauthorized production behavior. Prefer existing unit/integration test infrastructure to introducing new app services. No public route, no new web chat, no provider SDK, no external network, no raw utterance storage and no mutation of P7 answers/encounters/facts. Explicit engineering-only feature gating is mandatory for any new opt-in hook: environment LOCAL/TEST, controlled synthetic fixture allowlist, disabled by default, and **never** simply `enabled=True` in staging/pilot/production. Use immutable, compile-time fixture IDs, **not** arbitrary user-entered health free text. A synthetic fixture does not establish a real-world patient's identity, consent or medical meaning.

Required behavior/evidence:

1. Exercise **P8-A `AI_GENERATE_STRUCTURED` -> P8-B `ClinicalIntakeExtractor`** with a deterministic exact-fixture `DeterministicOfflineLLMProvider`; version/hash-correlated prompt/schema/provider/model/source metadata; bounded deadline; no live calls. Do not bypass P8-B's strict allowlist, safety, validator or default-off gates.
2. Ensure `AI_EXTRACTED_UNCONFIRMED` objects remain detached and are **not** persisted, merged into P7's engine answers, used to choose a medical route, or presented as clinically verified. The P7 engine owns deterministic next-question selection; extractor never owns it.
3. Demonstrate **disabled**, **unconfigured**, **invalid evidence**, **wrong provenance**, **injection-like source**, **timeout**, **refusal**, **schema-invalid** and **successful synthetic** cases all preserve existing P7 availability and generic urgent-help UX. No fabricated candidate on failure.
4. Preserve explicit module/capability injection and sealed-module boundaries. Do not import adapters, database repositories or private encounter/session ORM types into task validation/domain. Do not auto-activate P8-B at app startup or make P7 depend on an AI capability.
5. Do not claim provider-level trusted prompt binding or general-patient source understanding: those remain NOT YET VERIFIED. Prohibit patient text, IDs or evidence spans in standard logs/metrics/errors/snapshots.
6. If useful and safe, add non-activated **internal typed interfaces/test fixtures** for future governed message integration, but **not** a public route, fake patient message history, automatic clinical fact updates, or misleading UI controls. Explain why every new file is needed. Prefer tests to speculative framework.
7. Preserve Alembic `p7a_0007`, all existing API contracts and exact P7 behavior in default configuration.

**Important:** This is **partial P8-C integration evidence**, not a fully delivered real-patient conversation. Label it so in the tracker, PR title and report.

## 3. Stage 3: conditional authorized real API/BFF/UI work â€” STOP unless every relevant gate is approved

The following is a **design/implementation checklist** only, not permission to activate. Do not execute Stage 3 on the presently verified baseline while approval rows are missing.

**Backend API / application design**

- Define and approve a versioned `POST /api/v1/intakes/{intake_id}/messages` request/response replacing the illustrative deferred `{"text": ...}` shape in `docs/06_API_CONTRACTS.md`; no conflict with P7 `/answers`, `/complete` semantics. Require strict bounded `text`, supported language/source, server-known current `expected_version`, idempotency strategy (unique operation/message ID, request fingerprint, same-key replay vs conflict) and no automatic ambiguous POST replay. If persistence is approved, define retention/delete/withdrawal/backups and one atomic transaction boundary with no database transaction open across provider await. Without approvals, this endpoint must remain **unimplemented** and `06_API_CONTRACTS.md` must retain an honest *deferred* marker.
- Server-side: exact opaque bearer, `sessions.validate`, active centralized `consent.check` for relevant approved purpose/scope, exact encounter/intake ownership, `IN_PROGRESS` lifecycle, authorized pack/version/current-question, expected-version optimistic concurrency; cross-session IDOR must not disclose resource existence. Recheck consent and authorization before any approved post-call mutation; policy for mid-flight withdrawal is explicit.
- Use the existing project error envelope/status registry with generic safe messages, `Cache-Control: no-store` on success and failure, request correlation, no raw provider output or system prompt returned. Map P8-A/B typed failures to honest optional-degraded states, not success or saved messages. Do not add new public error codes casually.
- Candidate proposals are **unconfirmed** only, retained only under an approved model; deterministic engine controls next questions. No automatic `IntakeAnswer` creation or confirmation, canonical `ClinicalFact` writes, diagnosis/triage/emergency disposition, medication/self-care, referrals or clinician approval. No partially persisted candidates after model/schema/authorization/transaction failure.

**BFF / patient UI design**

- Extend the existing same-origin Next.js App Router BFF (`apps/patient-web/app/api/intake/**`, `apps/patient-web/lib/intake/**`) only after backend contract is approved and implemented. BFF reads transient `HttpOnly`, `SameSite=Strict`, `Secure` where required session cookie server-side; browser sees no bearer. Enforce origin/CSRF-equivalent protection, content type/size, bounded timeout, full response validation, safe error allowlist and `no-store` on every branch. Never forward raw upstream failures or log request bodies.
- Accessible UI on existing `/intake/[intakeId]` journey: clear opt-in/notice once approved, text input kept in ephemeral React memory only, keyboard labels/focus, mobile 320/390 widths, reduced motion, disabled/loading/conflict/consent-withdrawn/error states and persistent generic urgent-help navigation. No clinical HTML rendering; no optimistic â€œsavedâ€ banner. Ambiguous mutation errors must refetch authoritative state before **user-directed** retry. Completed intake read-only.
- NEVER place health text, message history, candidate evidence, session token, consent payload, or API responses into `localStorage`, `sessionStorage`, IndexedDB, Cache Storage, service-worker cache/background sync/replay, URL/query/path parameters, analytics or screenshots containing real PHI. Preserve PWA shell-only cache allowlist and offline nonfunctional clinical state.

**Real integration test requirements** (only once activation approved): unit-contract + real PostgreSQL + FastAPI + Next.js BFF + Playwright; valid and wrong-session bearer, consent grant/withdrawal, expired/closed session, object IDOR, stale version/concurrent mutations, completed/terminal intake, malicious/injection-looking text rendered inert, API timeouts/failures, idempotency/ambiguous request/no replay, DB transaction rollback on injected failure, in-flight revocation, no storage/log/trace/browser leakage, accessible mobile/keyboard, deterministic P7 fallback and urgent-help visibility. Use synthetic patient fixtures, never real PHI. Final AC-P8-005/007/008/009/010 and P8 macro completion demand this and all remaining approvals; offline fake success alone is insufficient.

**If Stage 3 remains blocked:** Create the checklist and detailed authorization/transaction/data lifecycle proposal in the Stage-zero decision document, clearly mark unresolved decisions **OPEN**, and do not silently implement them as defaults.

## 4. Required offline regression matrix (Stage 2)

Use existing P8-A/B tests plus focused P8-C engineering harness tests with synthetic fixtures only:

- Fixed simulated current authorized synthetic-source fixture -> one exact P8-A `StructuredLLMRequest` -> P8-B strict envelope -> immutable unconfirmed candidate; no new canonical P7 answer/fact/write/output authority.
- P8-A `disabled`/`unconfigured` and each closed failure category; P8-B unsupported source, wrong-hash/version/span/provider correlation, wrong schema, `LENGTH`, malformed candidate, abstention/refusal -> no candidate promotion and P7 unchanged.
- Exact P8-B positive allowed synthetic utterances and adversarial negation, third-party, historical, hypothetical, Unicode invalid, fake role, encoded instruction -> failed/abstained under finite engineering grammar. Negative tests cannot be weakened to accept arbitrary speech.
- Proof of zero external egress and zero provider credentials; protected environments cannot select fake even under malicious config/feature toggles.
- Assert no unexpected module/endpoint registration and default P7 start/answer/review/complete still works; no persisted new messages/candidates, Alembic unchanged.
- Safe error/result repr and privacy telemetry canaries; source/IDs/text never emitted by logging/tracing/metrics. Preserve existing browser no-store/cache/cookie security test suite.
- If a realistic simulated end-to-end journey cannot be run without violating source/notice/persistence gates, record it **NOT YET VERIFIED**; do not label test-only internal composition as a production/browser E2E.

## 5. Acceptance/traceability, explicit blocked status

- Preserve existing P8-A AC-P8-001/002/005 evidence and P8-B engineering evidence for AC-P8-003/004/006/007/008/009/010.
- Add evidence for **offline technical integration only**, including exact source linkage, default-off handling and deterministic P7 independence.
- Mark `AC-P8-009` **PARTIAL / adapter role binding NOT YET VERIFIED**. No claim that a live prompt-injection-resistant production adapter exists.
- `AC-P8-005` patient-facing P7 degraded UX, `AC-P8-007` persistence/provenance, and governed real-patient message/candidate/consent/retention acceptance remain **NOT YET VERIFIED** until approved and implemented.
- Record P8-C as `PARTIAL` or `BLOCKED` according to completed safe subset; **do not mark P8 macro COMPLETE** solely because offline tests pass. P8-A and P8-B merged, verified.
- Preserve clear separate status labels: `TECHNICALLY TESTED IN SYNTHETIC MODE` vs `CLINICALLY APPROVED`, `PRIVACY APPROVED`, `PRODUCTION ENABLED`. The latter three are not established by this phase.

## 6. Scope and quality gates

Expected permitted changes **until approvals**:

```text
docs/implementation/P8_C_INTEGRATION_GATE_REVIEW.md         # decision/evidence + blocked-governance matrix
backend/tests/test_clinical_intake_extraction_integration.py # offline fixture harness, if feasible
backend/tests/test_p8c_*                                     # only narrow, meaningful guard tests
backend/app/modules/clinical_intake/extraction/**            # only justified, backward-compatible internal seam
backend/app/modules/ai_orchestration/**                       # AVOID; stop if a genuine P8-A defect requires change
docs/implementation/38_PROGRESS_TRACKER.md
docs/03_REPOSITORY_STRUCTURE.md                                # only if actually adding files
docs/codex/CODEX_PHASE_PROMPTS/P8_C_GATED_INTAKE_INTEGRATION_API_UI.md
```

Absent approvals, **forbidden**: patient-facing `/messages` route; arbitrary free-text patient AI chat UI/BFF; clinical answer/fact writes; new tables/columns/Alembic migrations; storing utterances, source spans or raw provider outputs; real model SDK/provider/egress; new consent purpose/notices, made-up retention durations/deletion guarantees, safety/triage/clinician decisions; P9/P10/P12/P14/P15 features; hidden CI skips; dependency/lockfile or infrastructure changes. Future authorized Stage 3 may require a separate scope/approval PR. Do not replace product limitations with misleading mock clinical content.

Quality: `git diff --check`; Ruff format/lint, strict mypy and compile/import; focused new tests; full network-free backend suite; 97 real PostgreSQL integration tests (or explain current actual count), migrations/head evidence; frontend formatting/lint/tsc/unit/build; Docker/PostgreSQL health; Playwright Chromium; privacy/secret/egress audits. Six required **GitHub Actions jobs on exact final SHA**:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

Do not weaken/change CI to make the branch pass. Document exact counts and any flaky/retried tests candidly. Ensure zero unrelated changes, zero unauthorized APIs and Alembic `p7a_0007` unless approved Stage 3 explicitly authorizes a migration (expected not).

## 7. Commit, PR, report â€” NEVER MERGE

Push `phase/p8-c-guarded-clinical-intake-integration`; open a PR against `main`. PR title/body must call the delivered subset **"P8-C guarded engineering integration / approval-gated"**, not "P8-C fully delivered", unless all gates and real API/BFF/Playwright tests are legitimately complete. Include blocker matrix and precise next required human approvals. Do not automatically progress to P9 or claim P8 complete.

**Report concise and exact:**

```text
STATUS: COMPLETE / PARTIAL / BLOCKED
BRANCH:
BASE MAIN SHA: ad3bb6cd709e2f403e6e798d1bac31f9477eaf23
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
MERGE: NO
P8-C DELIVERED ENGINEERING SUBSET:
UNIMPLEMENTED / BLOCKED PATIENT MESSAGE API, BFF AND UI:
DECISION GATES (CLINICAL, ROLE, CONSENT/EGRESS, RETENTION, CONFIRMATION, IDEMPOTENCY):
P8-A/B INTEGRATION + ZERO-EGRESS PROOF:
P7 REGRESSION / DATA MUTATION PROOF:
FOCUSED / BACKEND / POSTGRESQL / FRONTEND / PLAYWRIGHT TESTS:
CI RUN ID + ALL SIX JOBS:
ALEMBIC HEAD / DEPENDENCIES:
AC-P8 EVIDENCE VS STILL UNVERIFIED:
UNRELATED CHANGES:
REQUESTED HUMAN DECISIONS:
```

**STOP after PR handoff and independent review. No merge, no live patient data, and no unapproved message workflow.**
