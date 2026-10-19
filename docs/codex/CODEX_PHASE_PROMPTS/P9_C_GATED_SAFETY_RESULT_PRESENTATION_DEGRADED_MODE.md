# SwasthyaSetu AI — Codex Phase Prompt: P9-C Gated Safety Result Presentation & Degraded-Mode Evidence

**Work unit:** P9-C only — presentation/integration architecture for deterministic physical-safety results and degraded behavior, **only to the extent currently approved**.
**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Independently verified base:** `main @ 541fa9033349162c4bf1abb5d6cdfe7a6cd8d6fd`
**Merge evidence:** P9-B PR #27 merged at this exact commit; independently reviewed implementation head `25fa91597c8a922c8381e8ceb08cae269fc325ca`, with six CI jobs passing on run `39266396959`.
**New branch:** `phase/p9-c-guarded-safety-result-presentation`
**Alembic baseline:** `p7a_0007` (no new migration unless a separately recorded, authoritative approval justifies it; such approval is **not** present at baseline).
**Delivery:** Push a feature branch, open a PR, independently verify all six CI jobs on the **exact final head**; **DO NOT MERGE**.

> **HARD GATE:** At this base, `docs/08_SAFETY_AND_TRIAGE_POLICY.md` is **DRAFT — NOT CLINICALLY APPROVED — NO REAL TRIAGE RULES**, and explicitly blocks real clinical evaluation and **P9-C patient integration**. P9-B's engine can only evaluate compile-time **nonmedical synthetic tokens**; its routes do not mean a patient needs emergency/priority/routine care or qualifies for self-care. The existing `/results` route is an honestly unavailable placeholder. **Do not display an evaluated safety/urgency route to a real patient, activate `/safety/evaluate`, imply that the P7 questionnaire includes safety assessment, or turn a test fixture into clinical authority.** Missing approval is a STOP for activation, not a reason to fabricate one. P8-C real-patient AI remains separately blocked.

## 0. Read → audit → gate decision (before coding)

1. Verify clean worktree; actual `HEAD`/`origin/main` match the exact base SHA. Verify PR #27 **MERGED**, P9-A/P9-B files and tests intact, Alembic head `p7a_0007`, no concurrent branch changes or newly approved safety policy. Do not reset/discard someone else's work. On drift/conflict stop and report `BLOCKED / BASE DRIFT`.
2. Follow `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`. Read actual repository files, preserving source-of-truth precedence and any newly approved governance decisions:

```text
docs/00_PROJECT_MASTER_SPEC.md                # §§6, 28: deterministic safety and clinical authority
docs/01_PRODUCT_REQUIREMENTS.md              # SAFE-001..010; FR-SAFE-001..012
docs/02_SYSTEM_ARCHITECTURE.md               # §14 and safety capability boundaries
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md                      # PhysicalSafetySignals/SafetyDecision, §§29–30
docs/05_DATABASE_SCHEMA.md                   # §13 is CONCEPTUAL, not approval for new tables
docs/06_API_CONTRACTS.md                     # §14 future /safety/evaluate example, NOT activated
docs/07_CLINICAL_INTAKE_SPEC.md
docs/08_SAFETY_AND_TRIAGE_POLICY.md          # DRAFT; does not define real clinical criteria
docs/13_AI_ORCHESTRATION_SPEC.md
docs/14_LLM_EXTRACTION_SPEC.md
docs/22_UX_AND_USER_FLOWS.md                # draft-only; generic urgent help, offline, privacy
docs/23_PATIENT_APP_SPEC.md                 # P7/P6 shell/BFF, /results unavailable
docs/26_PRIVACY_CONSENT_SPEC.md
docs/29_ENGINEERING_STANDARDS.md
docs/30_TESTING_STRATEGY.md
docs/33_ERROR_HANDLING_POLICY.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md       # §17 P9-C: UI/result integration + degraded mode
docs/adr/ADR-003-deterministic-safety.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md  # AC-P9-001..008
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/implementation/P8_C_INTEGRATION_GATE_REVIEW.md
docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md
```

3. Inspect actual active code and routes, including:

```text
backend/app/modules/safety/{__init__,domain,policies,contracts,engine,synthetic}.py
backend/tests/test_safety_*.py
backend/app/main.py
backend/app/modules/clinical_intake/{api,application,contracts,public,engine}.py
backend/app/modules/{sessions,consent,encounters}/public.py
backend/app/api/{errors,security}/**
backend/app/shared/{capabilities,modules,errors,persistence}/**
apps/patient-web/app/{results,urgent-help,offline}/page.tsx
apps/patient-web/app/intake/**
apps/patient-web/app/api/{intake,onboarding}/**
apps/patient-web/lib/{intake,onboarding}/**
apps/patient-web/components/{route-unavailable,urgent-help-link,ui-primitives}.tsx
apps/patient-web/components/intake/**
apps/patient-web/tests/{routes,accessibility-baseline,browser-boundaries,pwa-baseline,intake-ui,intake-bff}.test*
tests/e2e/patient.spec.ts
.github/workflows/**
```

Use actual file names; do not infer nonexistent functions/files from this list. Confirm at least these baseline facts: no real `safety.evaluate` capability, no registered physical-safety FastAPI route, no `safety_decisions`/`policy_versions` persisted tables, no patient safety result, `/results` still uses `RouteUnavailable`, generic `/urgent-help` independently accessible, P7 completed draft does **not** claim diagnosis/urgency assessment, browser has secure server-only session cookies and no clinical storage.

4. **Create first** `docs/implementation/P9_C_SAFETY_PRESENTATION_GATE_REVIEW.md` with a decision matrix: current source path and section, named accountable owner (role, not fabricated person), decision ID/date where recorded or `NONE RECORDED`, approved environment/population/use, status, and action to unblock. At minimum evaluate:

| Gate | Default decision at this verified base |
|---|---|
| Clinician-approved safety-policy source, scope, populations, validated signals and clinical thresholds | **OPEN; real rules prohibited** |
| Clinically approved route precedence, uncertainty semantics and self-care exclusions | **OPEN; symbolic P9-B toy precedence has no medical significance** |
| Approved patient/clinician wording, emergency disclaimers, accessibility, localization and escalation links | **OPEN; reuse only existing generic urgent-help copy** |
| Deployment-specific safety policy identity/version, approval evidence, lifecycle, monitoring, rollback and expiry | **OPEN; P9-A engineering metadata is not approval** |
| Session, consent, encounter/object authorization for new safety result read/evaluate endpoints | **UNIMPLEMENTED; design and real PostgreSQL tests required** |
| Persistence, retention, deletion, audit/outbox and policy/input provenance for `safety_decisions` | **OPEN; no migration allowed yet** |
| API idempotency/concurrency, evaluation consistency, recomputation and ambiguous request recovery | **OPEN; no `/safety/evaluate` activation** |
| Self-care eligibility release and hard fail-closed block across P15 and other future consumers | **NO active self-care workflow or authorization; no implied release** |
| P8-C real-patient AI gates (role binding, consent, egress, retention, confirmation, privacy) | **OPEN unchanged; P9-C cannot circumvent these** |
| Threat/privacy/clinical safety review and explicit production/pilot enablement | **OPEN; local/test fake never production** |

**Decision:** Where authoritative approvals are absent, complete **only Stage 2 below** and return `PARTIAL — SAFE PRESENTATION ENGINEERING SUBSET / PATIENT ROUTING BLOCKED`. If an approved decision suddenly exists, STOP and reconcile it with the canonical repository hierarchy, get precise scope, and then implement only what the recorded decision authorizes; do not infer approval from a flag, JSON value, checksum, documentation draft, user form consent for P7 or tests.

## 1. Stage 2: useful offline result/degraded presentation engineering — no active patient safety workflow

Implement the **smallest safe, deliberately detached** set of capabilities to exercise how an eventual trusted safety decision *could* be represented in a UI without enabling it for real sessions or making medical claims. Prefer static-test/render-contract work to speculative BFF/API. The following are authorized boundaries, not a mandate to add all components:

**A. Versioned, tightly bounded presentation/view-state contract**

- A closed, strongly typed **nonclinical engineering presentation state** with at least `NOT_AVAILABLE` (policy missing/unapproved), `ENGINEERING_SYNTHETIC_PREVIEW` (toy result in isolated tests only), and, only if useful, `INVALID_RESULT`/`DEGRADED` (validated input cannot be presented). Model only the machine states that tests genuinely need. Keep the default `NOT_AVAILABLE` and `blocks_self_care=true` semantics for unavailable/invalid paths. **Do not encode fake clinical approval, diagnosis, treatment, emergency instructions, real patient eligibility or named resources.**
- If representing a toy `SafetyDecision`, validate its exact P9-A shape and route enum, code count/format/order, policy metadata, clarification and self-care-block flags, timestamp, and provenance. Require exact **synthetic P9-B policy identity** and clear `ENGINEERING_ONLY` classification plus explicit local/test guard. In production/unknown environments, reject or return unavailable *before* rendering a toy route. Do not accept an arbitrary caller's `approved:true` or `route:"ROUTINE_CARE"` as permission to show a result.
- Keep a strict allowlist for top-level and nested keys in any data-to-UI conversion, never serialize a raw Python dataclass or arbitrary backend response to a client. A frontend parser, if introduced, must reject unknown route/schema/version, extra nested properties, unbounded arrays, forged identity or clinically meaningful payload fields. Do not surface PHI, provider output, explanations, source evidence or patient/encounter IDs in toy fixtures or UI snapshots.
- Do not add a new patient safety BFF endpoint to obtain these states. A contract or mapper with synthetic in-memory test objects is sufficient; explain the trust boundary and which future authenticated server API must enforce it. Avoid adding unnecessary production code if a test-only fixture/component achieves the evidence more safely.

**B. Isolated accessibility/degraded-view proof**

- Prefer a **pure React result/presentation component used only in unit/component tests** (e.g. `apps/patient-web/components/safety/synthetic-safety-preview.tsx`), or a narrowly owned test-only harness. It must have no import from `apps/patient-web/app/**` route files, no navigation link or server route, no patient data, no clinical advice and no runtime data source. If a production-accessible frontend preview route would be required, **do not add it**; record the UI work as approval-blocked instead.
- A synthetic test state must prominently say **"Engineering test data only — not a medical assessment"**, must not instruct a user to seek a particular urgency route, provide a clinician recommendation, authorize self-care, or imply the route corresponds to real symptoms. Showing literal machine token labels in isolated tests is permissible; creating translated clinical route labels/copy is not.
- A disabled/unavailable state must explain that no safety assessment has been performed, without claiming an answer was saved, evaluated or cleared. For any user-facing copy beyond the existing generic unavailable/urgent-help wording, obtain clinical/content approval first. If this cannot be guaranteed, keep rendering entirely under synthetic component tests and preserve the actual existing user-facing pages unchanged.
- Test semantic headings/statuses, keyboard/focus, reduced motion/forced colors, contrast and 320px/390px reflow using existing primitives/style. No fake active urgent escalation, emergency button, contact list, or self-care CTA. Keep generic urgent-help link present in the **existing shell**, independent of any safety computation.
- Preserve `/results` as an honest **unavailable** page. Preserve `/urgent-help` generic text and `UrgentHelpLink` across the app; do not hijack it for synthetic decisions. Do not modify completed-intake review copy to imply a safety evaluation occurred.

**C. Backend/contract invariants and failure proof**

- Preserve P9-B `SyntheticSafetyEngine` and P9-A registry unchanged where possible. A local/test-only in-memory projection test may evaluate the actual P9-B fixture and assert pure conversion to a bounded/non-actionable representation. No live `safety.evaluate` application service, HTTP endpoint, database write, patient signal parser, real-policy loader or arbitrary input callback.
- Exercise positive **toy** signals, missing active policy, malformed/corrupted policy, malformed/stale/incompatible decision, clarification, hard override, exclusion, unsupported environment and invalid clock. Every absent/invalid/unknown state blocks any hypothetical self-care continuation; failures must not be silently rendered as `ROUTINE_CARE` or `SUPPORTED_SELF_CARE`. In the UI harness, an exception must become a safe unavailable/error state, never an invented successful assessment.
- Demonstrate that model/advisory hints cannot override P9-B hard-stop results and that toy presentation never changes deterministic P7 `NextQuestion`, intake answers, provenance, generic urgent help or P8 extraction states. No external network or LLM calls. Use test-only static data or exact synthetic fixtures; no real patients, medical observations or credentials.
- Do not add new runtime imports of synthetic fixtures into `main.py`, BFF, API handler, patient app server routes or default app composition. Tests should verify such isolation. Guard direct imports/test mounting in staging/pilot/production; no feature-flag bypass. If achieving a robust guard is not possible, **do not create a preview component** and instead provide tests + design-only blocked checklist.

**Stage 2 completion is evidence of *presentation architecture and degraded-state handling*, not evidence of patient safety evaluation, database persistence, backend-to-BFF-to-browser journey or clinical acceptance.** Label it precisely.

## 2. Stage 3: actual authorized P9-C safety integration — DESIGN/STOP checklist only until approved

**Do NOT implement these items on the current base.** Record the exact future contract and approval requirements in the gate document without pretending they are authorized.

1. **Policy and signal authority:** clinician-approved, versioned safety policy with exact typed patient signal inputs, validation, hard rules, patient populations, ambiguity behavior and escalation wording. Never derive clinical eligibility from P8 unconfirmed candidates, LLM prose, unchecked P7 text or an unauthenticated browser-supplied `route`.
2. **Server authorization:** future `POST /api/v1/encounters/{encounter_id}/safety/evaluate` must load verified minimum-necessary structured signals server-side; validate exact bearer and SESSION consent appropriate to the approved processing purpose; enforce encounter ownership and permissions, terminal states and rechecks. Distinguish policy availability from patient status; return minimized common safe error envelope, `Cache-Control: no-store`; never reveal another session's resource.
3. **Decision integrity:** bind and record policy ID/version/checksum/approval provenance, input snapshot reference if approved, evaluation timestamp and result identity. Complete missing data must never default to low risk. Self-care must be gated behind an approved successful safety evaluation and rule exclusions. P9-A metadata digest and P9-B synthetic fixture are not clinical approval. Model hints cannot downgrade hard safety authority.
4. **Persistence design:** `docs/05_DATABASE_SCHEMA.md` lists conceptual `safety_decisions` and `policy_versions`; it does **not** authorize introducing SQLAlchemy models, Alembic migrations, raw snapshots, retention duration, deletion semantics or outbox messages. Obtain data governance/legal/security/clinical sign-off first. Specify idempotency, optimistic concurrency, transactional atomicity, re-evaluation after changes, revocation and denial paths. Prove with real PostgreSQL tests.
5. **BFF and patient UI:** use existing Next.js same-origin BFF, transient `HttpOnly`, `SameSite=Strict` bearer cookies, strict origin/content-type/size, bounded timeout, complete response validation, safe error whitelist, no-store and no automatic ambiguous POST replay. No browser `Authorization`, localStorage/sessionStorage/IndexedDB/Cache Storage/background queue/analytics/URL health data. Only then allow approved route-specific accessible copy and actions; keep generic urgent help even if safety policy unavailable.
6. **Approval/regression:** independent clinician case validation; policy precedence and negative-case evidence; exact-session IDOR/withdrawn consent/expiry; changed intake/version concurrency; policy retirement/rollback; injected DB error atomic rollback; 320/390 reflow, focus/keyboard/forced colors, no cache/storage/PHI leaks, honest degraded and offline behavior. Confirm P7 remains non-diagnostic, P8-C gates remain blocked. Only clinician-authorized route content may become patient-visible.

If no approvals, preserve the original API spec's conceptual future example **as not implemented**, ideally with a small clarification that no real endpoint has been activated; do not falsely change `docs/06_API_CONTRACTS.md` into an approved contract.

## 3. Tests and acceptance-status truthfulness

Minimum stage-2 tests, consistent with actual files added:

- Pure typed/strict result-view contract rejects wrong root, unknown keys, invalid route/version/identity/flags, overlong or unordered reasons and source/PHI-bearing unexpected fields. Demonstrate no optimistic "assessment completed" state.
- Explicit `LOCAL` and `TEST` toy mapping works only when deliberately supplied trusted synthetic data; `STAGING`, `PILOT`, `PRODUCTION` and missing/unknown environment fail closed at the **actual preview/presentation entrypoint**, not merely config settings. Do not hide synthetic test code in a runtime reachable path.
- Full P9-A policy tamper and P9-B mechanics regression; missing/unapproved/invalid/expired policy path yields unavailable and cannot authorize self-care or produce an actionable patient result.
- Existing patient `/results` still unavailable, existing `/urgent-help` still generic and reachable, current P7 intake review says "not an urgency assessment"; no new safety or `/messages` OpenAPI/BFF route.
- Existing session/consent cookies, origin/no-store, offline and PWA shell cache allowlist, no browser clinical persistence, accessibility/mobile journeys unchanged. Test that fixture/test preview is not imported by app routes or bundled as an accidentally accessible public page.
- No real patient data, fake medical thresholds, advice, clinician content, new ORM/table/migration, audit/outbox, provider/egress, third-party package, new language copy, or P7/P8 mutation.
- Security: canary texts/token-looking values cannot appear in rendered output, logs, error traces, metrics, browser storage, URLs or snapshots. Synthetic-only labels must be harmless machine literals.
- If feasible, test rendering states in component tests and optional Playwright **against existing real app flows** for absence/unchanged behavior. Do not claim an end-to-end safety-result journey without an authorized API/policy.

**Acceptance classification** (do not inflate):

| Criterion | Current technical evidence | P9-C Stage 2 evidence | Still blocked |
|---|---|---|---|
| AC-P9-001/002 | P9-A decision contracts, P9-B in-memory toy routes | Nonclinical schema/presentation parsing | Clinically valid patient decision/persistence |
| AC-P9-003/004/005 | P9-B toy override/nondowngrade/clarification | Degraded/preview preserves those machine outcomes | Approved real rules, clinical precedence, patient action |
| AC-P9-006 | P9-A empty-default; P9-B invalid/missing policy fails | Unavailable presentation without invented route | Patient-facing API/UX after approval |
| AC-P9-007 | Exact synthetic classification and protected environment refusal | Test preview is visibly synthetic and **never public** | Approved production policy and enablement |
| AC-P9-008 | P9-B toy self-care exclusion | No actionable self-care CTA and failure default blocks | Real P15/self-care integration + clinical authorization |

P9-C must be marked `PARTIAL — SAFE ENGINEERING SUBSET` if Stage 3 is blocked. **P9 macro remains PARTIAL**. P8-C remains PARTIAL and approval-blocked. Do not mark whole P9 or P8 complete because these unit tests pass.

## 4. Quality gates, scope locks and final PR handoff

Keep changes narrowly scoped. Suggested files (use only where actually warranted):

```text
docs/implementation/P9_C_SAFETY_PRESENTATION_GATE_REVIEW.md           # required approval/evidence matrix
apps/patient-web/lib/safety/presentation.ts                          # optional pure bounded contract, not a BFF
apps/patient-web/components/safety/synthetic-safety-preview.tsx      # optional disconnected engineering-only preview
apps/patient-web/tests/safety-presentation.test.ts[x]                 # focused component/validator tests
backend/tests/test_safety_presentation_boundaries.py                # optional no-route/no-persistence/integration proofs
docs/08_SAFETY_AND_TRIAGE_POLICY.md                                  # only honest P9-C gate/fixture note
docs/03_REPOSITORY_STRUCTURE.md                                      # only if actual new files are added
docs/implementation/38_PROGRESS_TRACKER.md                          # required precise status/approval disclosure
docs/codex/CODEX_PHASE_PROMPTS/P9_C_GATED_SAFETY_RESULT_PRESENTATION_DEGRADED_MODE.md
```

**Forbidden unless separately approved:** `backend/app/main.py` safety registration; real `safety.evaluate`, `/api/v1/.../safety/evaluate` or `/api/.../messages` route; user-accessible safety results, clinician claim, personalized urgent routing/copy; real policy rules, symptom/threshold parsing, production synthetic fixture activation, self-care release; patient result/decision persistence, `safety_decisions`/`policy_versions` migration, patient fact mutation; new live model/network adapter; weakening privacy/consent, P7 forms, P8-C barriers, security tests, or CI; new dependencies/lockfiles if not necessary. The existence of `SafetyRoute.EMERGENCY` in P9-A/B is **not** permission to show a real-user emergency decision.

Quality steps:

```text
git diff --check
Ruff format/lint, strict mypy, backend compile/import
P9-A + P9-B + new P9-C focused tests
Full network-free backend tests (report all skips)
Full real PostgreSQL tests + clean Alembic verification (head p7a_0007)
Frontend formatting/lint/typecheck/tests + all three production builds
Docker build/non-root/migration/liveness/readiness
Playwright Chromium full existing patient journeys
Privacy/egress/secret/no-route/no-table/unapproved-copy checks
All six GitHub Actions jobs green on the exact final SHA
```

Six **mandatory CI jobs**: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. Report any flaky retried test truthfully; never weaken tests for green CI. Ensure clean worktree, remote head equals local final SHA, all changes scoped.

Commit and push `phase/p9-c-guarded-safety-result-presentation`, open a new PR against the verified main SHA, **DO NOT MERGE**, and return:

```text
STATUS: COMPLETE / PARTIAL / BLOCKED  # likely PARTIAL for governance-blocked P9-C
BRANCH:
BASE MAIN SHA: 541fa9033349162c4bf1abb5d6cdfe7a6cd8d6fd
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
MERGE: NO
P9-C GATE REVIEW / CLINICAL APPROVAL STATUS:
STAGE 2 SAFE RESULT/DEGRADED PRESENTATION EVIDENCE:
PATIENT API, BFF, UI / REAL POLICY STATUS:
SYNTHETIC FIXTURE ISOLATION + ENVIRONMENT GUARDS:
P9-A/B REGRESSIONS / NO REAL SAFETY AUTHORITY:
AC-P9 EVIDENCE VS NOT VERIFIED:
FOCUSED / BACKEND / POSTGRESQL / FRONTEND / PLAYWRIGHT COUNTS:
CI RUN ID / SIX JOB CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCIES:
P7/P8-C BOUNDARIES PRESERVED:
UNRELATED CHANGES:
REQUIRED HUMAN APPROVALS:
```

**STOP after PR handoff for independent review. Do not auto-merge or start P10.**
