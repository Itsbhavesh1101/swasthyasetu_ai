# SwasthyaSetu AI — Pre-P10 Clinician & Provenance Specification Pack

**Work unit:** Pre-P10 canonical documentation prerequisites, **not** P10-A implementation.
**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified baseline:** `main @ 08219993e96e2023500370bcaf4057c29f289df6`
**Merge evidence:** P9-C safe Stage 2 PR #28 merged at this exact main commit; reviewed PR head `31f83a421eb3c900528b640d1b5c451e54a8fb02`, run `39280955033` succeeded with all six required jobs.
**Proposed branch:** `phase/pre-p10-clinician-provenance-specifications`
**Scope:** New/reconciled _documentation only_. DO NOT implement P10-A/B/C/D; DO NOT MERGE until independent review.
**Alembic head:** `p7a_0007` — must remain unchanged.

## 0. Why this is the next work unit

`docs/implementation/38_PROGRESS_TRACKER.md` explicitly identifies two **NOT STARTED** prerequisites _Before P10_:

- `docs/12_CLINICAL_PROVENANCE_SPEC.md`
- `docs/24_CLINICIAN_DASHBOARD_SPEC.md`

Both canonical paths are absent at the verified baseline. The P10 implementation plan (`docs/34_MASTER_IMPLEMENTATION_PLAN.md` §18) separates P10-A summary domain/backend, P10-B clinician read model/API, P10-C clinician-web, and P10-D correction/provenance end-to-end. Create **source-aligned, implementable, governance-aware prerequisite specifications** first. This is documentation design; it does not establish clinician authentication, data-sharing approval, clinical validation, patient safety activation, or working clinical functionality.

**Non-negotiable authority boundary:** Existing pseudonymous P7 consent and token-bound session is not an authorized clinician identity. P8-C patient AI is still Stage 3 BLOCKED; P9-C patient safety is still Stage 3 BLOCKED. P10 specifications must not use these blocked features as production data sources, grant AI-extracted candidates confirmed status, derive a triage route from a summary, or expose protected patient data via an unverified clinician UI/API. A clinician's role label alone is not assigned-patient authorization.

## 1. Preflight and repository audit

1. Confirm `git status --short` empty, checked-out `main` and `origin/main` at the exact baseline SHA, PR #28 merged, no incompatible subsequent commits. On drift, STOP and report, do not reset/discard work.
2. Verify paths `docs/12_CLINICAL_PROVENANCE_SPEC.md` and `docs/24_CLINICIAN_DASHBOARD_SPEC.md` are genuinely absent; if newly added under a canonical equivalent, reconcile without duplicates and raise material precedence conflicts.
3. Verify actual `backend/app/modules/summaries/` is `.gitkeep` only, existing `apps/clinician-web/` is a foundation/empty state, current `provenance` and `patients` modules have working read/provenance contracts, and current `identity` authorization has role-level `ENCOUNTER_READ_ASSIGNED` and `SUMMARY_CONFIRM` permission constants but **does not by itself prove actual clinician assignment**.
4. Follow repository `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`; apply canonical/R3 precedence; inspect actual code and tests. Record deviations rather than inventing implementation facts.
5. Create branch `phase/pre-p10-clinician-provenance-specifications` from the baseline only after preflight passes.

### Mandatory canonical reading

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md             # FR-SUM-001..008; FR-CLIN-001..013; FR-PROV-001..007
docs/02_SYSTEM_ARCHITECTURE.md              # summaries/provenance ownership, extensions, RBAC
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md                     # ClinicalFact, VerificationState, FactProvenance, ClinicalSummary
docs/05_DATABASE_SCHEMA.md                 # conceptual clinical_summaries; existing fact/provenance storage
docs/06_API_CONTRACTS.md                    # §§15–16, 26: future fact review/summary/clinician API
docs/07_CLINICAL_INTAKE_SPEC.md
docs/08_SAFETY_AND_TRIAGE_POLICY.md          # DRAFT, NO REAL RULES
docs/13_AI_ORCHESTRATION_SPEC.md
docs/14_LLM_EXTRACTION_SPEC.md
docs/22_UX_AND_USER_FLOWS.md
docs/23_PATIENT_APP_SPEC.md
docs/26_PRIVACY_CONSENT_SPEC.md
docs/29_ENGINEERING_STANDARDS.md
docs/30_TESTING_STRATEGY.md
docs/33_ERROR_HANDLING_POLICY.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md      # §18 P10-A/B/C/D
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md # AC-P10-001..009
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/implementation/P8_C_INTEGRATION_GATE_REVIEW.md
docs/implementation/P9_C_SAFETY_PRESENTATION_GATE_REVIEW.md
docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md
docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md
```

### Required implementation fact-check (read, do not change)

```text
backend/app/modules/identity/{domain,authorization,contracts,public,application}.py
backend/app/modules/sessions/**
backend/app/modules/consent/**
backend/app/modules/patients/{domain,public,application,contracts,infrastructure}.py
backend/app/modules/encounters/{domain,public,application,contracts,infrastructure}.py
backend/app/modules/provenance/{domain,public,application,contracts,api}.py
backend/app/modules/clinical_intake/{domain,contracts,application,public,api}.py
backend/app/modules/ai_orchestration/**
backend/app/modules/summaries/
backend/app/shared/{security,capabilities,modules,errors}.py  # use actual paths
backend/app/main.py
backend/migrations/versions/**
backend/tests/**
apps/clinician-web/app/**
apps/clinician-web/tests/**
apps/patient-web/app/{encounter,intake}/**
.github/workflows/**
```

Inspect the actual populated filenames; the glob list is navigational, not proof that every hypothetical file exists. Explicitly distinguish working read capabilities from conceptual API examples and permission constants from deployed clinician authentication + object-level assignment enforcement.

## 2. Produce the two canonical specs

### A. `docs/12_CLINICAL_PROVENANCE_SPEC.md`

Document ID consistent with repository convention; status `Canonical Pre-P10 Prerequisite — TECHNICAL SPECIFICATION, NOT CLINICAL APPROVAL`; version and scope. Specify precisely:

**1. Fact provenance and trust hierarchy**

- Map the existing `FactProvenance` fields and `ProvenanceSourceType` (`PATIENT_REPORT`, `CAREGIVER_REPORT`, `CLINICIAN`, `OCR`, `DOCUMENT_AI`, `FHIR_IMPORT`, `ABDM_IMPORT`, `HIS_IMPORT`, `MODEL_INFERENCE`, `ADMIN`, `SYSTEM`) to existing code, with source ID/ref, extraction provider/model/prompt/schema versions, confidence where meaningful, UTC created time and created_by; treat `confidence` as _not_ clinical certainty.
- Enumerate exact existing `VerificationState`: `EXTRACTED`, `LOW_CONFIDENCE`, `NEEDS_CONFIRMATION`, `PATIENT_CONFIRMED`, `CLINICIAN_CONFIRMED`, `REJECTED`, `SUPERSEDED` and permitted transitions/guards. Reject silent promotion of candidate or predictive output to confirmed fact; distinguish review _of a claim_ from actual clinical truth and clinician ownership.
- Source evidence is typed and minimum-necessary. No automatically persisted raw prompts, extraction messages, model output, entire OCR blobs, or sensitive source text as provenance payload. Source absence/expired access must be explicitly shown as unavailable rather than fabricated evidence.

**2. Confirm / reject / correct workflow design**

- Define explicit actor authentication, permission, object/encounter assignment and source-data access requirements before protected review; no trust in URL IDs, client-supplied role or consent. Cross-patient/encounter IDOR denied without leaking existence.
- Confirm/reject allowed state transition rules; correction creates distinct linked superseding facts, never in-place overwrite or erasure. Preserve original value, original source, verification state/history, correction actor, time and reason/evidence _only where separately approved for persistence_. Do not overwrite a `CLINICIAN_CONFIRMED` fact with lower-trust `EXTRACTED`, `LOW_CONFIDENCE`, `NEEDS_CONFIRMATION`, or `PATIENT_CONFIRMED` state.
- Resolve stale versions, concurrent reviewers, duplicate submissions, repeat/replay, terminal encounter state, changed consent, transaction failure, partial rollback and retry. State where current P5 functionality ends and P10-D would start; design not automatically implemented.
- Reuse P5 module ownership and public capability exports; do not let `summaries` or `clinician-web` directly mutate P5 fact storage or bypass provenance owner. Model conceptual audit/outbox with explicit content minimization and approved retention; never assume a new table, event or migration is authorized.

**3. Summary provenance / source-traceable read model**

- Every summarized clinically meaningful assertion must be backed by a supplied structured source fact/intake claim, source ID/ref/verification state and version where available. Explicitly distinguish **structured intake answers (patient reported, non-diagnostic)** from verified clinical facts and **P8 extraction candidates (unconfirmed)**. Label absence as unknown/unavailable; never reinterpret missing meds/allergies as _no allergies_ or _no medication_.
- Define how revisions, clinician edits, supersession and newly changed facts impact summary freshness; detect source drift and require user confirmation/review again where appropriate. Versioned snapshots and fact references must not be treated as permanent provenance if source data can change.
- Define source-detail authorization, privacy-safe summaries and error paths; no unbounded raw source exposure. Record future approved document source views as deferred to P11, and FHIR/ABDM source links as deferred to P16/P17.

**4. Traceability and test plan**

- Exact `FR-PROV-001..007`, `FR-SUM-008`, `AC-P10-005/006/007`; current P5 provenance facts, P8 blocked promotion boundary.
- Future negative-case tests: cross-tenant/other-patient/other-encounter denial, unassigned clinician, wrong/expired actor, lower-trust overwrite, contradictory source, missing source, missing/withdrawn consent where applicable, stale version, concurrent correct+reject/confirm, failed transaction rollback, idempotent retries, content-free errors, no PHI in telemetry. Distinguish offline deterministic fixture tests from real PostgreSQL/API/security tests required for implemented phases.

### B. `docs/24_CLINICIAN_DASHBOARD_SPEC.md`

Document ID and status as above; canonical full P10 requirements grounded in real existing app/build contracts.

**1. Audience/authorization and governance gate**

- Clinician identity must originate from a trusted authenticated actor, not a pseudonymous patient bearer, a client-side role string or frontend hiding. `RoleCode.CLINICIAN` + `ENCOUNTER_READ_ASSIGNED` are prerequisites but do not establish assignment alone. Explicitly design assignment/institution scope, permission-checked all-object access, repeat ownership checks, disabled actor behavior, role changes/revocation, least-privilege read model, and no implicit admin data access.
- Existing `apps/clinician-web/` is a foundation, **not** deployed clinician sign-in or permissioned queue. Any institutional IdP, clinician directory, assignment data source, organization/tenant policy, production hosting, identity assurance and UI data-sharing approval that are missing must be marked `OPEN — IDENTITY/SECURITY/PRIVACY DECISION REQUIRED`. Do not make “fake authenticated clinician” production defaults.
- Decide separately the privacy/legal basis and consent scope for clinician access to a pseudonymous P7 intake, and the conditions under which encounter transfer/assignment is lawful/authorized. General product consent is not transitive to unrelated sharing or external AI.

**2. Screen/state inventory and read-model contracts**

- Queue: assigned/available **as authorized** only; filtering/pagination/sort/staleness, minimized count/metadata, row access checks, empty/loading/error/forbidden/degraded states. Never use an unrestricted `patients.list` query as a clinician queue without object-level authorization.
- Encounter overview: current encounter, patient-scoped facts when actually authorized, chief complaint/HPI/history, timeline, **prominent medications/allergies with explicit `UNKNOWN`/`NOT_RECORDED`/`UNVERIFIED` states** (do not fabricate absent/reassuring values), source/verification tags and freshness. P7 drafts remain explicitly non-diagnostic.
- Structured clinical summary: sections following `FR-SUM-002` (chief complaint, HPI, past medical/surgical history, medications/allergies, family history, personal history, ROS, investigations). The existing `ClinicalSummary` conceptual model specifies ID, encounter, version, status (`DRAFT`, `CLINICIAN_EDITED`, `CONFIRMED`, `REJECTED`, `SUPERSEDED`), sections and `generated_from_fact_ids`. Source-backed deterministic draft first; optional AI composition only after separate applicable P8-C/clinical/privacy authorization, never inventing data or diagnosis. Unapproved AI input is not trusted source.
- Review controls: `confirm`, `correct`, `reject` and edit summary are **future P10-D** operations with optimistic concurrency, rollback, per-field/fact provenance and proper access checks. Define safe `READ_ONLY` / unavailable when role/assignment/auth/consent/transaction approval is absent; avoid fake successful controls.
- Read-only extension slots (from system architecture): `PatientHeader`, `CriticalAlerts`, `MedicationAllergyPanel`, `Timeline`, `EncounterSummary`, `DecisionSupport`, `Documents`, `Referrals`, `FeaturePanels`. Explicitly hide/disable panels whose owner is not implemented/approved; no clinical alerts/safety flags from P9 synthetic tokens; no risk predictions/actual referrals from future modules. Extension points are compile-time typed, permissioned; no dynamic untrusted code loading.

**3. API/BFF and clinician-web architecture (DESIGN only)**

- Align future endpoints with `docs/06_API_CONTRACTS.md` §§15, 16, 26: clinician queue/overview, fact review, summary generation/latest/confirm/revise. These examples do not establish an active endpoint or consent. Define authoritative server-side read projections over existing module capabilities and forbid direct cross-module ORM/entity mutation.
- Specify bounded request/response shape, schema/versioning, safe pagination and field minimization; exact authenticated actor and assigned encounter checks on each read/write; cache `no-store`; object-level IDOR protection; safe error envelope; no patient data in query strings, telemetry or browser storage. No raw API credentials in client JS. Approval gates before live clinician API/BFF.
- UI accessibility: keyboard/one `h1`/table headers/landmarks, 44px touch where applicable, 320/390 reflow, forced-colors, reduced motion, clear verification badges not just colors, screen-reader labels, explicit disabled/offline/consent/expired sessions, safe drafts, no fabrication. Preserve app foundation until actual backend authority approved.
- Define future summary revision/persistence lifecycle with consistency/version/retention/audit/outbox/provenance and conceptual `clinical_summaries` schema. No schema is authorized by this specification alone; no invented retention duration; distinguish design from implementation.

**4. Phased implementation and acceptance matrix**

Use the actual plan's four subphases without reassignment:

```text
P10-A: summary domain/backend foundation, source-backed deterministic draft contract and tests;
       only the safe subset permitted without unapproved clinician runtime auth/patient flow.
P10-B: permissioned clinician queue/read models/API (blocked until trusted role binding,
       assignment and privacy/consent agreements are implemented/approved).
P10-C: clinician-web UI wired to authorized read models (blocked for sensitive live data
       until P10-B and role/access design pass); safe shell scaffolding only if separately scoped.
P10-D: clinician confirmation/correction/rejection and provenance integration end-to-end;
       requires authorized review actors, transaction/event retention and real DB evidence.
```

Map every `AC-P10-001..009` and `FR-CLIN-001..013`, `FR-SUM-001..008` to owner, prerequisite, required tests, and current evidence status (`NOT YET IMPLEMENTED` for P10). No “passed” clinical acceptance from a documentation-only change. Clearly list hard blockers for clinician data access and which P10-A domain-only foundation, if any, can safely proceed after specs are reviewed/merged.

## 3. Required companion gate review / decision record

Create `docs/implementation/P10_READINESS_GATE_REVIEW.md` with a compact, independently auditable matrix (not a permission grant). For each gate, record authoritative source path/section, accountable owner, evidence or `NONE RECORDED`, currently approved scope and environment, actual status, actions to unblock and planned P10 subphase impact. At minimum:

- clinical source/summary correctness, source verification and no invented diagnoses;
- authenticated clinician identity, trust in actor, assignment/institution authorization, MFA where policy requires it, audit access;
- lawful/governed clinician access to P7 pseudonymous encounter, purpose/consent and sharing;
- medications/allergies/unknown/unverified visibility and clinical UI content sign-off;
- source document permissions and later P11/P16/P17 availability;
- fact confirmation/correction/rejection and lifecycle, optimistic concurrency and rollback;
- summary/version persistence, provenance/audit/outbox, retention/deletion, migrations;
- clinical/extracted candidate separation, blocked P8-C external AI and P9-C safety;
- threat/privacy/accessibility/security reviews, production activation and rollback.

If a gate lacks authoritative approval, mark `OPEN/BLOCKED`; never infer approval from a current role permission constant, source-code schema, synthetic test, current P7 general consent, or documentation text. Explicitly recommend an isolated domain/test-only P10-A subset if that is the only approvable next code unit.

## 4. Cross-document consistency and hard stop rules

- Preserve code actual states for P5 domain/provenance and P7 deterministic structured intake. Clinical facts and P7 answers are **not interchangeable**. A provisional P8 candidate is not clinician-confirmed; P8-C Stage 3 and P9-C Stage 3 remain BLOCKED.
- `docs/05_DATABASE_SCHEMA.md` `clinical_summaries` is conceptual; the absence of implemented persistence is not a reason to create a migration during spec authoring. Document decisions that need data governance rather than silently setting retention/permission defaults.
- Preserve P9 safety routes synthetic-only and disconnected from real patient/clinician UI; do not show patient urgency classification, clinical advice or an `EMERGENCY` badge from a toy fixture.
- Prevent circular module ownership: `summaries` receives authorized minimal factual/read projections via public protocols; UI/BFF and APIs do not write patient records directly; provenance remains source owner.
- Mark discrepancies between canonical specs and actual code as `DESIGN-IMPLEMENTATION GAP`, with accurate file paths and resolution owner. If a canonical authority conflict cannot be reconciled without changing scope, STOP for user review.

## 5. Allowlisted changes; no production code

Expected paths:

```text
docs/12_CLINICAL_PROVENANCE_SPEC.md
docs/24_CLINICIAN_DASHBOARD_SPEC.md
docs/implementation/P10_READINESS_GATE_REVIEW.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/PRE_P10_CLINICIAN_PROVENANCE_SPECIFICATION_PACK.md
docs/README.md                           # only if actual index needs canonical links
docs/implementation/README.md            # optional index-only correction
```

Do not edit `backend/**`, `apps/**`, `packages/**`, `tests/**`, migrations, schema code, dependency/lockfiles, CI, infrastructure/deployments, active APIs, feature flags, live authentication, consent, safety/AI activation, clinical medical rules, or unrelated documents. No new ADR unless needed to record an explicitly surfaced unresolved conflict, in which case request review instead of unilaterally deciding governance.

## 6. Verification, tracker update, pull request, handoff

- Update tracker to **P9-C Stage 2 safe subset MERGED; P9 PARTIAL; P8 PARTIAL; P10 NOT STARTED**. Mark `12` and `24` **specification completed, subject to review** once written, never claim production approval or P10 acceptance. Recommended P10-A implementation remains conditional on review of specs and gate findings.
- Perform cross-document traceability and contradiction checks; `git diff --check`; ensure **documentation-only diff** and unchanged migrations, Alembic `p7a_0007`, dependencies/lockfiles/CI. Run repository-provided doc validations if any. Preserve all existing tests without weakening/suppressing.
- Commit/push `phase/pre-p10-clinician-provenance-specifications`; open PR against verified `main`. Verify **six required GitHub Actions jobs** succeed on the **exact final remote commit SHA**: Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, Security scans. Report real failures/retries without suppressing tests.
- **DO NOT MERGE** and **DO NOT START P10-A**. Wait for an independent review of the spec/approval/ownership evidence.

### Concise return report

```text
STATUS: COMPLETE / PARTIAL / BLOCKED
BRANCH:
BASE MAIN SHA: 08219993e96e2023500370bcaf4057c29f289df6
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
SPEC 12 STATUS / SOURCE PROVENANCE AND CORRECTION CONTRACT:
SPEC 24 STATUS / CLINICIAN QUEUE, SUMMARY, AUTHZ AND UI DESIGN:
P10 READINESS GATE MATRIX: OPEN / APPROVED ITEM COUNTS, OWNERS, BLOCKERS
P10-A/B/C/D OWNERSHIP AND SAFE NEXT SUBSET:
AC-P10-001..009 MAPPING:
P8-C / P9-C GATES PRESERVED:
CHANGED PATHS / NO RUNTIME DIFF:
TEST/VALIDATION COUNTS AND SIX CI JOB CONCLUSIONS:
CI RUN ID:
ALEMBIC HEAD / DEPENDENCIES:
MERGED: NO
```

**Stop after PR and CI evidence; no automatic merge or patient/clinician activation.**
