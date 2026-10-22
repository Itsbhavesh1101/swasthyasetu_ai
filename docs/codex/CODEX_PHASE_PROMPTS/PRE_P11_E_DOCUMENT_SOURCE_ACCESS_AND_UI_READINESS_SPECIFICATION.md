# SwasthyaSetu AI — Pre-P11-E Document Source-Access & UI Readiness Specification

**Work unit:** `PRE-P11-E` — **DOCUMENTATION / READINESS DESIGN ONLY**. This is **not** P11-E implementation, clinician or patient document enablement, a new API, or permission to expose document data.

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified starting `main`:** `f71662322b27ec79004745ec6217283887700ac8`
**Reviewed P11-D head:** `963f5e11eccec4d1ef7a80386ae49f61833bc28e`
**PR #35:** confirmed **MERGED**, merge SHA `f71662322b27ec79004745ec6217283887700ac8`, commit compare reviewed P11-D head → merged main: `files=[]`.
**Suggested branch:** `phase/pre-p11-e-source-access-readiness`
**Alembic:** `p7a_0007` — unchanged.
**Approval truth:** P11 **PARTIAL**, **0/9 live gates approved** (5 OPEN, 4 BLOCKED); P10 live clinician gates **0/9**; P8-C/P9-C Stage 3 real patient AI/safety remains blocked.
**Delivery:** one clean isolated branch and PR, exact-head six CI jobs green, **DO NOT MERGE**, independent reviewer decides.

> **Hard stop / phase choice:** The canonical `P11-E` patient upload/status/review and clinician source/candidate/timeline UI is **BLOCKED** by P11 gates 1, 3, 7, 8, and 9 and upstream P10-B/P10-D live authority. Do **not** implement P11-E UI, a patient document route, clinician screen, preview, read model, permission adapter, or endpoint. The only next permissible work from this prompt is a **source-grounded human-decision / testing-readiness design pack**. If a missing decision could be resolved only by an accountable human, record it as **UNRESOLVED**, never invent an approval or fake a provider.

## 0. Preflight and source-of-truth hierarchy

1. Use a clean **isolated worktree**; preserve all uncommitted primary-worktree user edits. Check local/remote GitHub main exactly `f71662322b27ec79004745ec6217283887700ac8`; PR #35 merged and tree-identical to reviewed head; there is no conflicting new PR. If main drifted, STOP and report, don't reset/force-push.
2. Read repository governance first: `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`; canonical `docs/{00_PROJECT_MASTER_SPEC,01_PRODUCT_REQUIREMENTS,02_SYSTEM_ARCHITECTURE,03_REPOSITORY_STRUCTURE,04_DOMAIN_MODEL,05_DATABASE_SCHEMA,06_API_CONTRACTS,12_CLINICAL_PROVENANCE_SPEC,15_DOCUMENT_AI_OCR_SPEC,23_PATIENT_APP_SPEC,24_CLINICIAN_DASHBOARD_SPEC,26_PRIVACY_CONSENT_SPEC,29_ENGINEERING_STANDARDS,30_TESTING_STRATEGY,33_ERROR_HANDLING_POLICY,34_MASTER_IMPLEMENTATION_PLAN}.md`; `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER,P11_READINESS_GATE_REVIEW,P10_READINESS_GATE_REVIEW,P8_C_INTEGRATION_GATE_REVIEW,P9_C_SAFETY_PRESENTATION_GATE_REVIEW}.md`, and accepted R3 dependencies/OCR governance. If document paths differ, inspect actual tree and cite correct ones instead of assuming.
3. Inspect actual merged code and runtime composition: `backend/app/modules/documents/{contracts,ports,processing,classification,registry,domain,ingestion,candidates,evidence}.py`, P11 focused tests and `backend/tests/ocr_support/`, `backend/app/main.py`, module capabilities, API paths; patient `/documents` unavailable placeholder; `apps/clinician-web/` foundations; P5 provenance/owner read interfaces; patient shell/BFF and service worker; existing identity/role/assignment/consent primitives and P7 manual intake. Read **as evidence of what exists**, not to activate anything. Verify no document ORM, migration, upload, source read/preview, clinician assignment authority, live OCR provider, runnable medical extractor, or production module registry.
4. Separate **current code truth** from historically dated docs: `docs/15_DOCUMENT_AI_OCR_SPEC.md` and `P11_READINESS_GATE_REVIEW.md` were written before P11-A/B/C/D synthetic subsets, so their old statements about `.gitkeep`/no contracts are **dated baseline snapshots**. Don't silently rewrite historical facts or claim the synthetic subsets closed live gates. `38_PROGRESS_TRACKER.md` must acknowledge merged P11-D #35 with exact merge SHA.
5. Treat accepted architecture/ADRs as binding. The real upload Pattern A vs B, private storage provider, source preview scheme, institutional clinician IdP, assignment policy, live clinical reviewer capability, permission granularity, retention and release policy remain **OPEN or BLOCKED** unless a verifiable current human decision record proves otherwise. Do not silently supersede an ADR; propose explicit ADR review if necessary.

## 1. Produce a complete Pre-P11-E readiness and source-access design pack

Create one new standalone file:

`docs/implementation/P11_E_SOURCE_ACCESS_AND_UI_READINESS_DESIGN.md`

Minimum sections:

### 1A — As-built inventory versus conceptual future state

- Table with concrete path, symbol, purpose, current authorization, and remaining dependency. Cover synthetic P11-A/B/C/D foundations, patient unavailable document route, absent document API/BFF/storage/ORM/worker/provider, no active clinical extractor, P5 provenance ownership, P10 clinician identity/assignment gap and P7 fallback.
- State exact `main` SHA and Alembic head. Document that `ENGINEERING_ONLY`, `NOOP_ABSTAIN`, `UNCONFIRMED`, `ABSTAINED`, `STRUCTURALLY_MATCHED_UNCONFIRMED`, and `SourceAccessStatus.NOT_VERIFIED` mean **no clinical or source-access authority**. Candidate structural matches do not imply that a patient file exists, was scanned, is viewable, or has validated medical meaning.
- Do not report P11-E as started, implemented, or accepted.

### 1B — Human decision / blocker register for all nine P11 gates

Mirror the **exact nine gates**, statuses and accountable owners in `P11_READINESS_GATE_REVIEW.md` without silently changing them. For every gate record: current status, specific missing approval, accountable human owner, decision artifact/evidence required, permitted synthetic evidence so far, dependencies, negative tests needed, and what **must stay disabled** until approval. Include **0 APPROVED / 5 OPEN / 4 BLOCKED** and dated source citations as relative repo paths with heading references.

Required critical gates: (1) lawful document ownership/upload/read/share/consent/assignment; (2) file signature/quarantine/malware/active PDF; (3) private storage encryption/region/key/retention/revocation; (4) reviewed metadata/processing schema/outbox/idempotency; (5) measured OCR/provider/language/resource/egress; (6) registry/source-version contracts; (7) medical extraction/clinical reviewer authority; (8) preview/UI/accessibility/clinician assignment; (9) threat/incident/pilot/monitoring/rollback/release approval.

**No sign-off template may itself record `APPROVED`**, and no document may give reviewers invented signatures, decisions, timestamps, selected vendors, byte quotas or pilot population. Use `NOT RECORDED`/`HUMAN DECISION REQUIRED` placeholders, not invented facts. Existing synthetic engineering evidence may be credited accurately while every live P11 AC remains **NOT VERIFIED**.

### 1C — Threat and authorization boundary matrix (design, not code)

Describe future request-by-request server-authoritative checks, *without building them*: trusted actor identity and active status, role permission **plus** exact encounter/patient/institution assignment, lawful purpose and scope-specific consent, source-state and retention/withdrawal checks, same-owner idempotency, object version/freshness, and content-free cross-object denial. Distinguish independent patient, caregiver, pseudonymous session, kiosk, clinician, and admin actors; **do not assume all exist or are authorized**.

Include deny-by-default threat cases: source ID guessed, another patient's ID, another institution, clinician role without assignment, revoked role/consent, expired session, stale queue reference, deleted/quarantined/superseded object, mismatch between source and candidate, token/key leakage, browser cache or logs, SSRF/unsafe document preview, signed URL replay, BFF error disclosure, repeated ambiguous upload mutation. Each should map to future negative evidence and responsible human decision. Avoid promising a specific HTTP 403/404 response without policy review; ensure non-enumeration.

### 1D — Purely conceptual presentation inventory and safe copy rules

Design a **non-executable screen/state specification** for future patient and clinician document experiences: unavailable/disabled, loading, unknown, unsupported, simulated lifecycle, processing/error, stale, consent/assignment denied, revoked, quarantined, source inaccessible/deleted, and unconfirmed candidate. Show the distinction between “no record,” “cannot verify,” “not authorized,” “unknown,” and “no clinically confirmed assertion”; never use reassuring absent-diagnosis/medication wording or diagnosis/treatment advice. **Do not author an approved clinical copy pack**. Any example labels must be nonclinical generic placeholders and explicitly **DRAFT — CONTENT/A11Y REVIEW REQUIRED**.

State exact browser privacy rules (no original bytes, OCR text, medical candidate, bearer, signed URL, source ref, patient identifier in localStorage/sessionStorage/IndexedDB/Cache Storage/service worker/analytics/URLs or client errors). BFF/auth cookie rules reference current spec; not implementation. Touch-only/manual P7 intake remains available when document or OCR is unavailable. Never infer permission from `STRUCTURALLY_MATCHED_UNCONFIRMED` or a `NOOP_ABSTAIN` processor receipt.

### 1E — Review/preview and accessibility security plan

Document prerequisites for sanitized viewer and renewed per-request source permission, lifecycle freshness, time-limited delivery, object isolation, anti-XSS/content-disposition, origin isolation, CSP, PDF active content, revocation behavior and source-copy restrictions; don't select actual libraries or approved streaming design. Avoid showing a clinical preview in current UI. Define test matrix for keyboard/screen reader/focus/320px/390px reflow, camera permission denial and text/touch fallback, visible unknown/unconfirmed/unavailable labels, noncolor-only errors, asynchronous state announcement, CSRF/session expiry and network degradation. Separate automated testable engineering checks from manual clinical/privacy/a11y approval.

### 1F — Requirements traceability and **future** phase sequencing

Map `FR-DOC-002`, `FR-DOC-017`, `FR-DOC-020`, `FR-DOC-021`, `FR-DOC-022`, `FR-PROV-001..007`, `AC-P11-007/008/009/011` and cross-cutting requirements to existing evidence and **not-yet-met** live acceptance, with negative test obligations. Don't claim this planning document passes ACs.

Propose **conditional, non-authorized future work packages** with hard entry conditions:

1. Live P11-A upload/storage/security/schema and P11-B real OCR/provider only after accountable gate decisions and benchmarks (potentially different ordering depending on decisions).
2. Live P10-B/D identity/assignment/source-review authority only after P10 independent approvals.
3. Live P11-D medical extraction and candidate review only after independent clinical field-schema validation, privacy/retention/source authority.
4. P11-E UI/service read models/preview/review only after applicable P11 and P10 gates, security/clinical/accessibility copy approvals, real backends, and independent PR review.
5. Optionally identify a **future separately reviewed synthetic-only P11-E presentation-contract subset**, *but do not implement or authorize it*. It must not modify existing patient/clinician routes, introduce a fake clinician, or visually imply that uploaded documents work.

Give an **objective decision list** of which human-owned approvals block each future work package. Define a STOP condition for unknown consent, source authority, retention, IdP, assignment and clinical claim requirements. Note that a future approved provider or schema decision must be recorded in the decision log / appropriate ADR before implementation; don't silently choose one in this pack.

### 1G — A concrete manual gate-review checklist and evidence ledger

Use a table with evidence IDs, owner, expected artifact (security threat model, pen-test/hostile fixtures, preview review, IdP/assignment policy, approved clinical schema/copy, data handling/retention, production readiness, monitoring rollback etc.), source link/path **when already existing**, test plan, approval state and blocker. Cross-reference Spec 15 §12. Placeholders `HUMAN OWNER TO COMPLETE` are allowed; don't fill with fake outcomes. Include engineering test criteria that can be assessed now vs approvals that only a human can grant.

## 2. Scope allowlist, documentation rules and prohibited changes

Allowed only:

```text
docs/implementation/P11_E_SOURCE_ACCESS_AND_UI_READINESS_DESIGN.md    # new, docs-only
docs/implementation/38_PROGRESS_TRACKER.md                        # minimal status truth: P11-D #35 merged; pre-P11-E design pending review
docs/implementation/P11_READINESS_GATE_REVIEW.md                   # OPTIONAL dated appendix, retain original matrix/0 of 9
docs/codex/CODEX_PHASE_PROMPTS/PRE_P11_E_DOCUMENT_SOURCE_ACCESS_AND_UI_READINESS_SPECIFICATION.md  # this exact prompt
```

**Do not change:** application/test code, migrations/ORM, API OpenAPI schema, BFF routes, patient/clinician/Admin UI, upload page, login/identity/consent/assignment policy, object-store/provider/model wiring, P11-A/B/C/D contracts, fixture mocks, job/worker, frontend build, Docker/CI, security/dependency configuration, R3 policy, canonical architecture/specs/ADRs, gate status or any P8/P9/P10 approval. Do not add imported external clinical data or dependency files. Documentation must be self-contained, link to existing repo evidence and **not silently decide unresolved policies**.

Avoid rewriting dated foundational docs as if their historical snapshot were a live status report. Any optional `P11_READINESS_GATE_REVIEW.md` change should be a clearly dated note referencing merged synthetic subsets, **without** modifying signoff count/status.

## 3. Required audit, CI and handoff

1. Verify initial main SHA and clean isolated worktree; inspect `git diff --name-status`, `git diff --check`, git status and exact changed-path allowlist. Ensure repo docs links and section references resolve; evidence isn't invented. Run a dedicated prohibited-activation/approval-language audit (P11 remains 0/9 and P10 remains 0/9; AC-P11-001..011 remain NOT VERIFIED live).
2. Because this is **documentation only**, no test or migration code should be modified. Run reasonable local markdown/reference checks and any mandatory repository checks. **All six** existing GitHub CI jobs must complete SUCCESS at the **exact new PR head** even for documentation-only changes: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. If CI is not triggered automatically, do not weaken workflows or misstate completion; report the blocker for independent review.
3. Progress tracker: P11-D synthetic subset **MERGED** in PR #35 at main `f71662322b27ec79004745ec6217283887700ac8`; reviewed P11-D head `963f5e11eccec4d1ef7a80386ae49f61833bc28e`, tree-equivalent. `PRE-P11-E` design is **documentation-only / independent review pending**. P11 live remains PARTIAL/blocked with 0/9 gate approvals; P10 live 0/9; P8-C/P9-C Stage 3 blocked. Do not label P11-E started or P11 implemented.
4. Create one branch and PR based on unchanged main. Push, confirm local==remote==PR head, exact CI run ID and success jobs, and demonstrate **no runtime files changed**. **DO NOT MERGE**. Return only after all evidence is available; no auto-merge or beginning P11-E/P12.

### Required completion report

```text
STATUS: COMPLETE PRE-P11-E DOCUMENTATION SUBSET / PARTIAL / BLOCKED
BRANCH: phase/pre-p11-e-source-access-readiness
BASE MAIN SHA: f71662322b27ec79004745ec6217283887700ac8
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
AS-BUILT P11-A/B/C/D AND P7/P10 SOURCE EVIDENCE:
NINE-GATE DECISION REGISTER AND ACCOUNTABLE OWNERS:
SOURCE ACCESS / NONENUMERATION / REVOKED-ACCESS THREAT MATRIX:
PATIENT/CLINICIAN UX STATE AND ACCESSIBILITY DESIGN (NO CODE):
EVIDENCE LEDGER / FR-DOC, FR-PROV, AC-P11 TRACEABILITY:
OPEN HUMAN DECISIONS AND STOP CONDITIONS:
DOC LINKS / SCOPE / GOVERNANCE AUDIT:
CI RUN ID / EXACT FINAL SHA / SIX JOB CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCIES / CHANGED PATHS:
P11 LIVE GATES: 0/9 APPROVED, 5 OPEN, 4 BLOCKED
P8-C / P9-C / P10 LIVE RESTRICTIONS:
UNRELATED CHANGES:
P11-E IMPLEMENTED: NO
MERGED: NO
```

**STOP** for independent review. This design pack is the prerequisite to discussion with accountable owners; it grants zero new file, clinician, clinical or production capabilities.
