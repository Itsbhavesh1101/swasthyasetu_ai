# SwasthyaSetu AI — Pre-P11-A Security, Threat and Privacy Drafts

**Work unit:** `PRE-P11-A-SECURITY-PRIVACY-DRAFTS` — documentation/review preparation ONLY. No live P11-A/P11-E implementation, clinician workflow, migration, storage integration, OCR execution, medical extraction, or clinical capability.

- **Repository:** `Itsbhavesh1101/swasthyasetu_ai`
- **Verified starting main:** `2b2d9036c7fe9941bc90bb55d4130dabb6571263`
- **PR #37:** merged at the above SHA; reviewed head `d0c72aef0fcff002bde46a1efe997d0485ec15a4` is tree-equivalent to merged main.
- **Proposed branch:** `phase/pre-p11-a-security-threat-privacy-drafts`
- **Alembic:** `p7a_0007`, unchanged.
- **Live gates:** P11 0/9 APPROVED (5 OPEN, 4 BLOCKED); P10 0/9 APPROVED; P8-C/P9-C Stage 3 BLOCKED. P11-E NOT IMPLEMENTED.

**Authorization distinction:** Writing proposed, clearly marked **DRAFT** documents does not require prior human signoff. Approving controls, laws, vendors, storage, consent, deployment, clinical behavior, or lifting live gates DOES require accountable human authorization. Missing approval is a document finding, not a reason to block safe draft-only authoring.

## 0. Mandatory preflight and evidence

1. Fetch and verify `origin/main` and GitHub `main` exactly at the base SHA above. Use a **new clean isolated worktree** from that remote ref; local `main` may be stale. Do not reset, overwrite or modify the primary worktree or preexisting untracked user prompt files. If the remote base has drifted, STOP and report. Track a copy of this exact prompt inside the isolated worktree only.
2. Read `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`; `docs/{00_PROJECT_MASTER_SPEC,01_PRODUCT_REQUIREMENTS,02_SYSTEM_ARCHITECTURE,03_REPOSITORY_STRUCTURE,04_DOMAIN_MODEL,05_DATABASE_SCHEMA,06_API_CONTRACTS,12_CLINICAL_PROVENANCE_SPEC,15_DOCUMENT_AI_OCR_SPEC,23_PATIENT_APP_SPEC,24_CLINICIAN_DASHBOARD_SPEC,26_PRIVACY_CONSENT_SPEC,29_ENGINEERING_STANDARDS,30_TESTING_STRATEGY,33_ERROR_HANDLING_POLICY,34_MASTER_IMPLEMENTATION_PLAN}.md`; `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER,P11_READINESS_GATE_REVIEW,P11_E_SOURCE_ACCESS_AND_UI_READINESS_DESIGN,PRE_P11_E_ARCH_PRIVACY_TECH_ASSESSMENT_AND_DECISION_TEMPLATE,P10_READINESS_GATE_REVIEW,P8_C_INTEGRATION_GATE_REVIEW,P9_C_SAFETY_PRESENTATION_GATE_REVIEW}.md`; `docs/research/r3/{R3_FINAL_TECHNOLOGY_STACK,R3_CODEX_DEPENDENCY_POLICY}.md`; relevant OCR benchmark research. Actual repository evidence outranks outdated snapshot wording; accepted ADRs are binding.
3. Inspect the *actual implementation*, without changing it: P4–P7 sessions/consent/identity, patients and provenance, `backend/app/modules/documents/{domain,ingestion,contracts,ports,processing,classification,registry,candidates,evidence}.py`, object storage port/local adapter, generic jobs/outbox, runtime `app.main`, patient `/documents` unavailable route, clinician foundation, and the absence of document ORM/routes/persistent worker/production OCR. No patient documents or real credentials may be collected.
4. `docs/implementation/38_PROGRESS_TRACKER.md` §5 marks canonical `27_SECURITY_ARCHITECTURE.md` and `28_THREAT_MODEL.md` NOT STARTED. The merged P11-A approval-readiness package calls out these gaps; it DOES NOT grant any human decision. Confirm missing paths and avoid replacing existing documents if the remote tree has changed.

## 1. Produce three documents, each clearly a **DRAFT — HUMAN REVIEW REQUIRED**

### A. `docs/27_SECURITY_ARCHITECTURE.md`

Title as platform-numbered specification, but prominently state: **DRAFT — P11-FOCUSED SECURITY DESIGN ONLY; NOT COMPLETE PLATFORM-WIDE SECURITY ARCHITECTURE; NO POLICY/PRODUCTION APPROVAL.** Identify repository baseline and actual as-built security primitives separately from future requirements and undecided choices. All other platform security domains remain out of scope/pending separate review.

Minimum content:
- Security goals and trust-boundary/data-classification inventory; actor classes patient, pseudonymous session, caregiver, kiosk, clinician, administrator, institution, worker, and system. Existing vs absent identity, ownership, permission, assignment and consent capabilities.
- Explicit conceptual flows and zones: patient UI and same-origin BFF, future document API, quarantine and scan, private object storage, PostgreSQL metadata, transactional outbox, durable jobs, future OCR and unconfirmed candidates, provenance, future viewer. Label every future/absent element.
- Undecided upload Pattern A streamed multipart vs Pattern B quarantine-only intent/finalize, and safeguards for pre-byte authorization, actual stream limits, signature/MIME mismatch, active PDFs, malware/quarantine, sandbox, cancellation, timing and no downstream read before release. Do not choose a pattern, format quotas or vendor.
- ADR-009: object storage holds bytes, PostgreSQL minimizes metadata. Proposed private IAM/tenant isolation, encryption/key/region, retention/deletion/backup/legal hold, temporary file cleanup, signed-view expiry/revocation; **all actual provider/values undecided**.
- Patient/encounter/institution/source per-request authorization, scope-specific consent, role is not assignment, identity is not consent, guessed IDs and cross-owner digests reveal nothing, server-only source permission checks.
- Proposed transactional/idempotent race protections for object/DB partial failure, attempt/generation freshness, stale results, revoke-delete-reprocess races, at-least-once jobs and recovery. No exactly-once claims.
- Privacy-safe browser/cache/session/BFF, CSP/preview isolation and content delivery, telemetry/audit redaction, secrets and incident/rollback/kill-switch requirements; P7 manual fallback and cross-phase P8/P9/P10 isolation.
- Security control register containing **ID, threat/asset, current reality, proposed control, status (AS-BUILT / UNDECIDED / DEFERRED), human owner, negative test and gate dependency**. No test can be claimed run if it has not been run. Reference exact specs and accepted ADR IDs.

### B. `docs/28_THREAT_MODEL.md`

Prominently: **DRAFT — P11 THREAT MODEL ONLY; NO COMPLETE PLATFORM THREAT MODEL; NOT SECURITY SIGN-OFF.** Include an ASCII or Mermaid text-only future data-flow diagram, trust boundaries, actors, asset inventory, attacker capability/assumption list; clearly tag future/absent components.

Deliver a STRIDE-style threat register, with stable IDs `P11-T-001...`, each row identifying asset/trust boundary, attack precondition, impact, existing evidence, *proposed unapproved* mitigation, accountable human, P11 gate, negative test and residual risk. Cover at least:
- guessed patient/encounter/document IDs, wrong role/institution/assignment/consent, enumeration and cross-owner checksum leak;
- forged MIME/signature, polyglot, executable/archive, active PDF/JS/SSRF/external links, decompression/image/page bombs, malicious file, scanner outage, quarantine escape;
- presigned-intent theft/replay, object replacement/TOCTOU, ambiguous finalize, orphan and partial DB/object/outbox operations;
- stale attempt/result, duplicate job, withdraw/delete/revoke during processing, worker crash/retry/poison and quota exhaustion;
- storage misconfiguration/key compromise/wrong region, signed-preview replay, resurrected deleted data after backup restore, inaccessible/quarantined files;
- source leakage through URLs, logs, caches, service workers, analytics, tracing, BFF upstream errors and support tooling;
- OCR/LLM prompt injection, provider egress/retention, forged provenance, unconfirmed candidate as clinical truth, bypass of P8-C/P9-C/P10 authority;
- insider/service-account abuse, compromised dependency/CI, incident response and rollback failures.

Add **proposed for review, NOT accepted** risk rubric, prioritized adversarial/negative test matrix, 9-gate mapping, nonenumeration and failure isolation evidence, remediation ownership and specific re-review triggers. **No live penetration test, patient bytes or security approval.** Never say a risk was mitigated just because it has a proposed control.

### C. `docs/implementation/P11_PRIVACY_DATA_FLOW_ASSESSMENT_DRAFT.md`

Prominently: **DRAFT — PRIVACY/DATA-FLOW ASSESSMENT; NOT LEGAL ADVICE, COMPLETED DPIA, INDIA DPDP COMPLIANCE ASSERTION, PRIVACY APPROVAL, OR RELEASE AUTHORIZATION.**

Define a tabular FUTURE data-flow/lifecycle inventory: upload; quarantine/scan; accepted original; metadata and provenance; async jobs; derived OCR/candidates; authorized source read/preview; withdrawal; deletion; backups/legal hold. Each row must specify origin/actor, sensitivity, purpose (UNDECIDED), exact authority/consent and allowed population (UNDECIDED), recipient/region/provider (UNDECIDED), data minimization, lifecycle, retention (UNDECIDED), deletion/backup, human owner, evidence/tests and pending human decision. Distinguish nonmedical synthetic engineering refs from real patient content. Address anonymous/pseudonymous, verified patient, caregiver, kiosk, clinician/institution and administrator separately without assuming they are approved actors.

Require explicit discussion of: `GENERAL_PRODUCT_USE`/`clinical_intake` consent **not transitive to P11**; legal basis/notice/India DPDP/guardian questions for counsel; external processor egress/DPA/retention/training/subprocessors/region not approved; purpose limitation, leakage in BFF/browser/cache/analytics/logging; deletion vs consent withdrawal vs legal hold/backups and in-flight work; incident/breach and subject rights; minimization/retention and research separation. Map requirements `PRIV-001..009`, relevant `FR-DOC-001..023`, `FR-PROV-001..007`, `AC-P11-001..011`, gates 1–9 and P10/P8/P9 restrictions. Include human-owned unsigned decision checklist and STOP conditions, never fictitious decisions/dates/signatures/vendors/populations.

## 2. Traceability and status rules

- Evidence can show **AS-BUILT TECHNICAL CONTROL**, **PROPOSED CONTROL — UNAPPROVED**, **HUMAN DECISION PENDING**, or **NOT IMPLEMENTED**; never silently promote a design suggestion to approved policy or a security control.
- Historical Pre-P11 gate review is dated 2026-10-20 and its old `.gitkeep` statements are snapshots. New merged P11-A/B/C/D technical subsets remain synthetic and no live P11 acceptance criterion passes.
- `27_SECURITY_ARCHITECTURE.md` and `28_THREAT_MODEL.md` are platform-numbered files but **only P11 sections are drafted**. In tracker §5 update their status at most to `P11-FOCUSED DRAFT — PLATFORM-WIDE COVERAGE AND HUMAN REVIEW PENDING`, not COMPLETE. Add a narrowly scoped new tracker section for the work unit.
- P11 gate matrix **0 APPROVED / 5 OPEN / 4 BLOCKED**, P10 **0/9**, P8-C/P9-C Stage 3 blocked. Patient `/documents` unavailable; P11-E not implemented; manual P7 preserved.
- Do not change accepted ADRs or select providers, regions, storage encryption/key custody, quotas, retention periods, lawful bases, medical reviewer or actual release controls. If a source conflicts, explicitly log the unresolved conflict for humans.

## 3. Locked changed-path allowlist

```text
docs/27_SECURITY_ARCHITECTURE.md
docs/28_THREAT_MODEL.md
docs/implementation/P11_PRIVACY_DATA_FLOW_ASSESSMENT_DRAFT.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/PRE_P11_A_SECURITY_THREAT_PRIVACY_DESIGN_DRAFTS.md
```

No other files. **No application/test code, ORM or migrations, API/BFF/frontend, jobs/worker/storage bindings, executable scanners or providers, external service/egress, real patient data, clinician workflows, infrastructure/deployments, dependency/lockfiles, CI/security changes, governance approvals or ADR modifications.** Leave the user's primary worktree unchanged.

## 4. Checks, PR and independent handoff

1. Validate all links and exact claims against current repository; ensure all three files exist with explicit DRAFT status, no mistaken implemented/approved/vendor/legal/compliance wording, complete matrices, reviewer/decision register, and no clinical/source access inference. No real patient data, secrets, identifiers or logs in documentation. `git diff --check`; changed-path allowlist; no runtime/dependency/migration changes; all existing gate counts unchanged.
2. Run applicable local repository quality checks as feasible; record actual counts and any retries honestly. The existing GitHub pipeline **must complete all six jobs SUCCESS at the same new final feature SHA**: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. Do not skip or weaken CI because the changes are documentation-only.
3. Commit this *exact prompt* at the listed tracked path. Push a single new feature branch and open **one PR** based on verified `main`. Verify local SHA == remote SHA == PR head and CI run head. **DO NOT MERGE**; stop for independent review. Do not start another implementation phase.

### Required Codex completion report

```text
STATUS: COMPLETE DRAFT DOCUMENTATION ONLY / PARTIAL / BLOCKED
BRANCH: phase/pre-p11-a-security-threat-privacy-drafts
BASE MAIN SHA: 2b2d9036c7fe9941bc90bb55d4130dabb6571263
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER:
27 SECURITY ARCHITECTURE DRAFT — AS-BUILT VS FUTURE:
28 THREAT MODEL DRAFT — THREATS / NEGATIVE TESTS:
P11 PRIVACY / DATA-FLOW DRAFT — OPEN HUMAN DECISIONS:
SOURCE-OF-TRUTH / LINKS / NO-HALLUCINATED-APPROVAL AUDIT:
P11/P10/P8-C/P9-C GOVERNANCE STATUS:
CHANGED PATHS / ALEMBIC HEAD / DEPENDENCIES:
LOCAL QUALITY COUNTS / RETRIES:
CI RUN ID / EXACT FINAL SHA / SIX JOB CONCLUSIONS:
HUMAN REVIEW / APPROVALS STILL PENDING:
UNRELATED CHANGES:
MERGED: NO
```

**Stop.** Draft threat/security/privacy documentation is preparatory engineering evidence—not human clinical, legal, privacy, security, institutional or production authorization.
