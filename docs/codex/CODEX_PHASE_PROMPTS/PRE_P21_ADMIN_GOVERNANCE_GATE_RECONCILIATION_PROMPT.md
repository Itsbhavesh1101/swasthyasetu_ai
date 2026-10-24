# SwasthyaSetu AI — Pre-P21 Admin/Governance Authority & Readiness Reconciliation

**Work unit:** `PRE-P21-ADMIN-GOVERNANCE-GATE-RECONCILIATION` — **DOCUMENTATION AND ACCOUNTABLE-REVIEW PREPARATION ONLY**.

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`

**Verified starting `main`:** `06d51e5f29a486c9bc13b6d1d65d5ec82239f2ac`

**Predecessor:** PR #50 merged; reviewed head `8755fcdc48232e9571978aa3b3560bb685c89be3`, merge tree equivalent at the starting main SHA.

**Branch:** `phase/pre-p21-admin-governance-gate-reconciliation`

> **Critical no-duplicate rule.** The canonical `docs/25_ADMIN_PORTAL_SPEC.md` **ALREADY EXISTS** as an **UNAPPROVED** Pre-P13/P21 draft, accompanied by `docs/implementation/PRE_P13_ADMIN_PORTAL_READINESS_REVIEW.md` and `docs/codex/CODEX_PHASE_PROMPTS/PRE_P13_ADMIN_PORTAL_SPEC_AND_READINESS_PACK.md`. Do **NOT** generate another root Spec 25, replace these files, re-run Pre-P13, claim Spec 25 is missing, or invent a new admin specification. This phase provides a **dated P21-specific delta and accountable-decision reconciliation** against the current repository and upstream restrictions. Its result is not approval or implementation.

**Absolute STOP:** No administrative APIs, web/BFF screens, production IdP/MFA, role/permission changes, actual privileged action, provider/resource verification, self-care content/policy/model promotion, clinical review/confirmation, audit viewer, maker-checker state machine, feature-flag modification, referral/notification, patient-data access/export, real source/credentials, infrastructure, new dependency, schema/migration, or runtime implementation. No governance signature or clinical/legal determination may be fabricated by an AI agent.

## 0. Preflight and source precedence

1. `git fetch` and verify `main` and `origin/main` both point **exactly** to `06d51e5f29a486c9bc13b6d1d65d5ec82239f2ac`; PR #50 merged at that SHA and its tree is identical to reviewed head. Verify `docs/25_ADMIN_PORTAL_SPEC.md`, `docs/implementation/PRE_P13_ADMIN_PORTAL_READINESS_REVIEW.md`, `docs/implementation/P20_UNIFIED_CARE_ORCHESTRATION_SPEC.md`, and `docs/implementation/P20_READINESS_GATE_REVIEW.md` already exist, and the new P21 reconciliation file below does not. On conflict, new unexpected commits, missing sources, or dirty/unrelated work: **STOP and report**; no silent rebase/reset/clean/overwrite/force-push.
2. Create a **new clean isolated worktree** and one new branch from the verified baseline. Preserve primary worktree and other PRs.
3. Read `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md` and canonical `docs/{00_PROJECT_MASTER_SPEC,01_PRODUCT_REQUIREMENTS,02_SYSTEM_ARCHITECTURE,03_REPOSITORY_STRUCTURE,04_DOMAIN_MODEL,05_DATABASE_SCHEMA,06_API_CONTRACTS,08_SAFETY_AND_TRIAGE_POLICY,09_MENTAL_HEALTH_POLICY,10_SELF_CARE_AYURVEDA_POLICY,11_PROVIDER_ROUTING_POLICY,12_CLINICAL_PROVENANCE_SPEC,13_AI_ORCHESTRATION_SPEC,15_DOCUMENT_AI_OCR_SPEC,17_RAG_KNOWLEDGE_SPEC,18_CLASSICAL_ML_SPEC,19_QUANTUM_ML_SPEC,20_FHIR_MAPPING_SPEC,21_ABDM_INTEGRATION_SPEC,22_UX_AND_USER_FLOWS,23_PATIENT_APP_SPEC,24_CLINICIAN_DASHBOARD_SPEC,25_ADMIN_PORTAL_SPEC,26_PRIVACY_CONSENT_SPEC,27_SECURITY_ARCHITECTURE,28_THREAT_MODEL,29_ENGINEERING_STANDARDS,30_TESTING_STRATEGY,33_ERROR_HANDLING_POLICY,34_MASTER_IMPLEMENTATION_PLAN}.md` as applicable; confirm paths before citing. Read `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER,P13_READINESS_GATE_REVIEW,PRE_P13_ADMIN_PORTAL_READINESS_REVIEW,P20_UNIFIED_CARE_ORCHESTRATION_SPEC,P20_READINESS_GATE_REVIEW}.md` and P8/P9/P10/P11/P12/P14/P15/P16/P17/P18/P19 readiness records where relevant. **Accepted ADRs and canonical requirements outrank earlier proposal notes**, and the dated P13 Gate 7 statement that Spec 25 was absent is **historical**: subsequent Pre-P13 work created that draft, but did not approve Gate 7.
4. Inspect actual current code before making any as-built claims: `apps/admin-web/`, existing P4 actor/authz/MFA interfaces and permissions, feature-flag configuration, PostgreSQL/outbox/audit primitives; P5/P7; P8/P9 detached synthetic scope; P10/P11 source and clinician gates; P13 provider/resource/referral placeholders; P15 knowledge; P18/P19 model governance. Do not equate `.gitkeep`, architecture drawings, role constants, passing tests, or a frontend shell with a live capability or production-ready identity. Do not access user/patient data or external systems.
5. Canonical P21 scope: `FR-ADMIN-001..010`, `FR-AUDIT-001..007` (`docs/01_PRODUCT_REQUIREMENTS.md`), and `AC-P21-001..008` (`docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md`); P21 units `P21-A` admin backend, `P21-B` admin web, `P21-C` clinical review queues, `P21-D` audit/maker-checker. Map P13-E ownership and `AC-P13-001..011` only as prerequisites/related scope. **Do not invent `FR-P21-*` IDs or an official P21 human gate count.**
6. Preserve independent approved architecture: ADR-001 modular ownership; ADR-002 ports/adapters; ADR-003 deterministic safety; ADR-005 research isolation; ADR-006 transactional outbox; ADR-007 explicit registration; ADR-008 PostgreSQL authority; ADR-010 clinical provenance; ADR-012 shared governed longitudinal context; ADR-013 no universal score; ADR-014 approved self-care knowledge; ADR-015 verified provider truth; ADR-020 controlled risky features; ADR-021 typed internal contracts; ADR-022 no invented clinical policy; ADR-023 no fabricated contacts/remedies; ADR-027 optional AI failure isolation; ADR-028 structured authoritative record; ADR-029 preserved corrections; ADR-032/033 research/model governance; ADR-038/039 dependency and artifact boundaries; ADR-040 phase-gated infrastructure. Verify numbers/text against current `37_DECISION_LOG.md`; do not silently supersede any ADR.

## 1. Deliverable A — new dated **P21 differential gate reconciliation**

Create **only** `docs/implementation/P21_ADMIN_GOVERNANCE_GATE_RECONCILIATION.md` (NEW).

Title: **Pre-P21 — Admin, Governance, Clinical Review: Existing-Spec Reconciliation and Accountable Decision Docket**.

Prominent header: **DRAFT — NOT A NEW ADMIN SPECIFICATION; NOT AN OFFICIAL GATE COUNT; NO HUMAN APPROVAL; P21-A/B/C/D NOT STARTED; NO LIVE ADMIN OR CLINICAL AUTHORITY**. Record the exact baseline SHA and date, existing earlier Spec 25/readiness file paths, review-owner **roles only**, and documentation-vs-as-built limitations.

Write the following substantive sections:

### A. Existing artifacts vs present implementation: no duplicate

- Establish dated source hierarchy: **Spec 25 was created during Pre-P13**; P13 historical Gate 7 once listed it missing, but that particular artifact now exists as an **unapproved draft**. Distinguish document-exists from gate-reviewed, owner-approved, technically implemented, and live-validated. Do not retroactively alter historical documents or claim P13 Gate 7 is now APPROVED. Do not relabel P21 as PARTIAL.
- Table for: existing Spec 25; Pre-P13 admin readiness; P13 provider/referral readiness and Gate 7; P20 composition spec and readiness; existing `apps/admin-web` shell; P4 role/authorization/MFA primitives; P3 outbox/audit foundations; P10/P11 clinician/document boundaries; P13 registry/referral/source moderation; P15 knowledge; P18/P19 governance; and P22 review. State **actual current evidence**, unimplemented parts, ownership, and whether authority/approval is missing. Cite repo paths/sections, not guessed behavior.
- Separate **implemented platform primitives**, **synthetic/detached evidence**, **unapproved designs**, **upstream blocked runtime**, **human decisions**, **future P21 engineering**. No live inference from documents or CI.

### B. Scope and responsibility reconciliation: P13-E versus P21-A/B/C/D

- Provide owner/separation table. P13 owns verified provider/resource truth, routing and referral side-effects; P13-E is its bounded moderation/source-warning UI where subsequently authorized. P21-A owns only separately authorized administrative application/API contracts and server-enforced object/role/institution permissions; P21-B owns admin web/BFF and honest inaccessible/degraded states; P21-C requires independently approved P10 assignment/source/provenance/correction authority; P21-D owns only authorized audit views and maker-checker **mechanics** under source-domain approval control. Clinical policy P9/P14/P15, model approvals P18/P19, source validation P13, clinician decisions P10, consent P4 and retention P22 **do not transfer to generic admin**.
- Describe the P4 identity trust gap precisely: server-side authorization and MFA-verified flag checks **do not establish** trusted production IdP, enrollment/identity proof, actual MFA ceremony, assigned institution, permitted object/source, maker-checker independence, or credential governance.
- Deny privilege from frontend state, route hiding, feature flags, usernames/headers/opaque IDs, CI, staged tokens, or PR reviews. Explicitly require server-side actor/institution/object/source/assignment/purpose and independently verified reviewer authority.

### C. Accountable decision docket (not signatures): split into eight descriptive domains

For **each** domain, record **as-built proof**, status `OPEN`/`BLOCKED` with reason, roles needing assignment, missing accountable **decision**, required signed/source-backed evidence, dependent P21-A/B/C/D and P13-E units, negative/adversarial tests, safe-off/unavailable behavior, and explicit STOP. These are **descriptive categories**, not a project-approved P21 gate count or `0/8` arithmetic.

1. **Production identity, MFA, role/object/source/institution authorization.** Trusted provider/IdP, actor lifecycle and revocation, role assignment, service accounts, privileged MFA, relationship/assignment and tenant isolation; staged P4 primitives are not production identity proof.
2. **Source-backed provider/resource verification and freshness.** P13 source rights, immutable provenance, verification owner/proof, fields, expiry, suspension/correction, urgent contact dual-control and public eligibility; no real resource or fabricated contact.
3. **Governing-domain decisions, maker-checker, conflict of interest.** Separate proposer/verifier/approver; who can approve P9/P14 safety, P15 content, P18/P19 models, clinical correction, version activation; prevention of ordinary admin self-promotion, audit bypass, self-check, rollback abuse. Draft policy vocabulary does not appoint signatories.
4. **P10 clinical review queue and P11 document-source authority.** Assignment, record access, provenance, review/confirmation/correction and supersession, concurrency and audit; both live 0/9 and their source gates remain BLOCKED/OPEN as recorded.
5. **P13 referral/notification visibility, purpose-specific consent, external side effects.** `REFERRAL_SHARING` active and explicit for actual external sharing, minimally scoped recipient/purpose/fields, valid recipient evidence, in-flight revocation, idempotency, honest statuses; admin visibility never means send/delivery authority. General product consent is not transferable.
6. **Audit/event integrity, privacy, retention, export and threat model.** Minimal append-only/tamper-evident metadata where approved; audience, actor/object access and audit-of-audit, log/redaction, incidents, deletion/hold, no raw transcript/document/prompt/secret search, no unrestricted bulk export. Do not assume retention duration or DPDP compliance.
7. **Admin API/BFF/UI, accessibility and fail-closed operational states.** Existing shell versus future screens, backend authoritative responses, safe CSRF/XSS/IDOR scope, no-store, copy/locale/accessibility (keyboard, focus, screen reader, reflow), no misleading approval badge or false success; failure must not break P7 manual intake or urgent help.
8. **Environment, credential/feature controls, incident/rollback and P22/P24 release governance.** No preview-to-production elevation, audited changes and rollback, independent approvals, P22 incomplete, bounded pilot/release evidence not inferred from CI, disaster/recovery and safe-off kill switch responsibilities.

### D. Exact normative traceability and STOP crosswalk

- **Verbatim** `FR-ADMIN-001..010`, `FR-AUDIT-001..007`, `AC-P21-001..008` from canonical sources. For each ID: exact wording, existing Spec 25 paragraph/section, current repo implementation proof (or absent), missing human evidence and future technical artifact, responsible domain, status **LIVE NOT VERIFIED**. Respect `MUST`, `SHALL`, `SHOULD`, `MAY` semantics; don't upgrade optional requirements.
- Relevant **P13 `AC-P13-001..011`** and Pre-P13/P13 Gate 7 in a clearly separate crosswalk. Mark it **historical missing-document gap addressed by unapproved draft; gate itself still BLOCKED/not approved**. Do not edit the old P13 gate document or claim closure of live ACs.
- Include `AC-P20-001..010` and `AC-PROD-001..014` only as relevant integrated/product upstream work, with status unverified. Do not manufacture acceptance evidence from finished P7.
- Explicit P4 authorization and consent, P5 provenance, P7 functional manual intake, P8-C/P9-C Stage 3 BLOCKED, P10/P11 live 0/9 approved (P11 5 OPEN/4 BLOCKED), P12–P21 runtime NOT STARTED where applicable, P15 clinical/source STOP, P16/P17 unauthorized, P18 no approved baseline/P19 no comparator, P20 live NOT STARTED, P22 NOT COMPLETE. If fresh source truth differs, STOP and report rather than quietly 'fixing' roadmap.

### E. Review-ready decision template, owner/risk register and explicit next action

- Add an **UNSIGNED**, unpopulated bounded decision template with: decision ID; affected phase/unit and domain; exact use/action/object, institution, population, recipient, purpose, environment, excluded scope; official/source version and checkable immutable evidence; data classification and per-purpose consent/authority; reviewer assignment/segregation and qualified role; approved resource/clinical policy evidence when relevant; identity/MFA and institution proof; attack/negative tests; risk acceptance; expiry and reevaluation triggers; rollback/incident/withdrawal actions; signatures **PENDING**. Don't silently mark any field approved or fabricate people.
- Brief role/owner risk register with status and reason. **Human action checklist**: assign named qualified decision-makers outside Codex; verify upstream clinical/privacy/security sources; review and sign narrow decisions; then request a **new** separately bounded prompt. This phase itself cannot conduct approvals or bypass them.
- Clearly state potential future **nonclinical synthetic P21-A authorization-contract preflight** is only a **proposal**, requiring explicit owner-reviewed scope and another prompt; it cannot create runtime, routes, persistence, real role grants, or live acceptance. P21-B/C/D, P13-E and releases remain STOP.
- Mark as a **documentation delta** to existing Spec 25, not a replacement. Do not introduce a new canonical root numbered spec, invented gate count or ADR.

## 2. Tracker update — exact minimal delta

Modify `docs/implementation/38_PROGRESS_TRACKER.md` only as follows:

1. Preserve the `P21 | Admin + Governance + Review | NOT STARTED` **status** exactly. Replace only that row's **Notes** with a concise truthful value such as: `Spec 25 exists as unapproved Pre-P13/P21 draft; Pre-P21 decision reconciliation prepared; P21-A/B/C/D runtime NOT STARTED and live acceptance NOT VERIFIED; accountable decisions pending.` Do not alter other phase rows or macro summary.
2. Append exactly **`# 67. Pre-P21 Admin Governance Gate Reconciliation and Owner Decision Docket`** after section 66, with one bounded block recording verified main SHA, PR #50 lineage, prior Spec 25/readiness already present, newly created reconciliation, 8 descriptive domains (not an official count), exact FR/AC crosswalk, P13 Gate 7 historical status, all upstream STOPs, zero runtime/approval changes, unchanged infrastructure, and human owner/next-action obligations.
3. Do not rewrite historical P13 Gate 7, earlier tracker sections, accepted ADRs, previous approval counts or source specifications.

## 3. Strict path allowlist and prohibited work

**Exactly three authorized documentation paths (no fourth path required):**

```text
docs/implementation/P21_ADMIN_GOVERNANCE_GATE_RECONCILIATION.md          # NEW; review delta only
docs/implementation/38_PROGRESS_TRACKER.md                              # minimal P21 note + #67
docs/codex/CODEX_PHASE_PROMPTS/PRE_P21_ADMIN_GOVERNANCE_GATE_RECONCILIATION_PROMPT.md  # exact byte-for-byte copy of this file
```

Leave existing `docs/25_ADMIN_PORTAL_SPEC.md`, `PRE_P13_ADMIN_PORTAL_READINESS_REVIEW.md`, all previous specs and readiness documents, `docs/implementation/37_DECISION_LOG.md`, all source material, dependencies/lockfiles, Alembic, CI, Docker and runtime **unchanged**. Alembic stays `p7a_0007`; Next.js and root `eslint-config-next` remain `16.4.2`.

**Forbidden:** any new code/tests/fixtures/scripts; local/real/synthetic actor credentials, demo role assignment, source provider listings, model promotion, clinical decisions or medical copy; admin UI/API/routing/data models or migrations; service/provider/IdP activation; new policies or acceptance changes; telemetry carrying secrets or PHI; network/API probes to provider/government systems; legal signoff/qualified reviewer impersonation; performance/security downgrade; more than the exact 3-path allowlist; unrelated cleanup or scanner suppressions.

## 4. Verification, PR, and handoff

1. Compare every requirement/criterion string against canonical sources and every as-built claim against code. Verify prior Spec 25 genuinely exists, cross-references are resolvable, scope and eight descriptive domains are clear, historical P13 status is distinguished from current truth, no invented approval/owner, **all live P21 ACs NOT VERIFIED**, P21 macro `NOT STARTED`, and P7 continues independent.
2. Check Markdown formatting with repository Prettier, links, `git diff --check`, section `# 67.` uniqueness, **exactly three changed paths**, byte-identical prompt, no altered original specs/ADRs/manifests/CI, correct Alembic baseline, no realistic personal identifiers or secrets. Run Gitleaks against clean source tree and exact new commit history; do **not** suppress scanners. Never commit generated assets, environment files or caches.
3. Run existing relevant local backend/frontend/PostgreSQL/Playwright/Docker checks as feasible, reporting exact outcomes, retries, timeouts, environment values and residual warnings truthfully. After push, verify the **six mandatory GitHub CI jobs all SUCCESS on the exact final PR head SHA**: Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, Security scans. No documentation CI result counts as clinical, institutional, or privacy approval.
4. Use one clean isolated branch, one clean commit from the exact verified base, one PR. Confirm local/remote/PR/CI SHAs identical. **DO NOT MERGE**. No P21-A/B/C/D, P13-E or other runtime phase. Stop and return this exact concise report:

```text
STATUS: COMPLETE PRE-P21 DECISION RECONCILIATION DOCS ONLY / PARTIAL / BLOCKED
BRANCH: phase/pre-p21-admin-governance-gate-reconciliation
BASE MAIN SHA: 06d51e5f29a486c9bc13b6d1d65d5ec82239f2ac
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER:
PR #50 MERGE BASE/TREE VERIFIED:
EXISTING SPEC 25 AND PRE-P13 READINESS — NO DUPLICATE / CURRENT TRUTH:
PRE-P21 REVIEW DELTA / EIGHT DOMAINS / ROLE DECISIONS / STOP:
FR-ADMIN-001..010 / FR-AUDIT-001..007 / AC-P21-001..008 EXACT TRACEABILITY:
P13 GATE 7 HISTORICAL GAP VS CURRENT APPROVAL STATUS:
IDENTITY / AUTHZ / MFA / SOURCE / CLINICAL / REFERRAL CONSENT / AUDIT BOUNDARIES:
UPSTREAM BLOCKERS / P21-A/B/C/D NOT STARTED / HUMAN SIGNATURES PENDING:
TRACKER HEADING #67 / EXACT THREE-PATH ALLOWLIST / PROMPT BYTE EQUIVALENCE:
ALEMBIC / DEPENDENCIES / LOCKFILES / SOURCE / CI UNCHANGED:
LOCAL CHECKS / GITLEAKS / WARNINGS / RETRIES:
CI RUN / EXACT FINAL SHA / SIX JOB CONCLUSIONS:
MERGED: NO
```

> **FINAL STOP:** This PR prepares an actionable review dossier of existing P21 design and source gaps. It grants **no** actor, doctor, admin, model, clinical, policy, privacy, legal, institutional, referral, patient-data, pilot, production or system authority. Accountable human owners — not Codex — must make, record and sign any real decisions before a new specifically approved engineering phase.
