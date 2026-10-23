# SwasthyaSetu AI — Pre-P13 Admin Portal Specification & Readiness Pack

**Work unit:** `PRE-P13-ADMIN-GOVERNANCE-DESIGN` — documentation and accountable-review preparation **ONLY**. This is a missing prerequisite for future P13-E admin-governance work; it is **not** P13-E, P21-A/B/C/D, or permission to implement admin operations.

- **Repository:** `Itsbhavesh1101/swasthyasetu_ai`
- **Verified starting GitHub `main`:** `af32d98061b4605d405e954de5cde3d380974d8e`
- **PR #40:** merged at that exact SHA; reviewed PR head `212a6765e2e6b6450591a70498b0924ef6281d0b` is tree-equivalent to merged main.
- **Suggested branch:** `phase/pre-p13-admin-portal-spec-readiness`
- **Current Alembic head:** `p7a_0007` — MUST remain unchanged.
- **Current state:** P13 and P12 runtime NOT STARTED; P11 0/9 approved (5 OPEN, 4 BLOCKED); P10 live 0/9 approved; P8-C/P9-C Stage 3 BLOCKED; P7 deterministic text/touch intake preserved. P21 implementation NOT STARTED.

> **Boundary:** A proposal, an app shell, a permission constant, or green CI is neither an administrative authorization nor a clinical, privacy, security, provider-verification, pilot, or production approval. Do not invent signoffs, roles, identity providers, source verifiers, MFA enforcement beyond current code, provider records, approved patient-facing copy, or feature activation.

## 0. Mandatory preflight, repository evidence, and working tree

1. Fetch GitHub `main` and `origin/main`, confirm both equal the exact starting SHA. Confirm PR #40 merged and its reviewed head is tree-equivalent, and `docs/25_ADMIN_PORTAL_SPEC.md` does **not** already exist. If the remote baseline drifted or a conflicting file exists, **STOP and report**; do not silently overwrite or reset. Create a **clean isolated worktree** from verified remote main. Leave primary worktree and all pre-existing untracked files untouched.
2. Read governance first: `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`; `docs/{00_PROJECT_MASTER_SPEC,01_PRODUCT_REQUIREMENTS,02_SYSTEM_ARCHITECTURE,03_REPOSITORY_STRUCTURE,04_DOMAIN_MODEL,05_DATABASE_SCHEMA,06_API_CONTRACTS,11_PROVIDER_ROUTING_POLICY,12_CLINICAL_PROVENANCE_SPEC,23_PATIENT_APP_SPEC,24_CLINICIAN_DASHBOARD_SPEC,26_PRIVACY_CONSENT_SPEC,27_SECURITY_ARCHITECTURE,28_THREAT_MODEL,29_ENGINEERING_STANDARDS,30_TESTING_STRATEGY,33_ERROR_HANDLING_POLICY,34_MASTER_IMPLEMENTATION_PLAN}.md`; `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER,P13_READINESS_GATE_REVIEW,P12_READINESS_GATE_REVIEW,P11_READINESS_GATE_REVIEW,P10_READINESS_GATE_REVIEW,P11_PRIVACY_DATA_FLOW_ASSESSMENT_DRAFT}.md`; `docs/research/r3/{R3_FINAL_TECHNOLOGY_STACK,R3_CODEX_DEPENDENCY_POLICY}.md`. Existing accepted ADRs and higher-priority clinical/privacy requirements govern; P11-focused security/threat documents are **unapproved P11-only drafts**, not a complete platform admin-security design.
3. Inspect **actual** code and composition for `apps/admin-web/` (foundation/empty state only), `backend/app/modules/identity/{authorization,contracts,public,application}.py`, `backend/app/api/security/authorization.py`, actor MFA/role permissions, central consent, audit/events/outbox, current module registrations, and placeholder provider/resource/referral/audit/notification paths. Verify the unconfigured production IdP, absent admin APIs/records/moderation/audit viewer, and no active P13-E/P21 runtime. Distinguish P4 technical role/MFA checks from verified production identity, role assignment, institutional authority, and human signoff.
4. Check `docs/01_PRODUCT_REQUIREMENTS.md` **exact wording** of `FR-ADMIN-001..010`, `FR-AUDIT-001..007`; `docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md` `AC-P21-001..008` and relevant `AC-P13-001..011`; `docs/34_MASTER_IMPLEMENTATION_PLAN.md` P13-E/P21; and `docs/implementation/P13_READINESS_GATE_REVIEW.md` Gate 7. Reconcile concepts, do not manufacture implemented acceptance evidence.

## 1. Primary deliverable — `docs/25_ADMIN_PORTAL_SPEC.md` (NEW; clearly UNAPPROVED DRAFT)

Title as **25 — Admin Portal Specification**, with a prominent **DRAFT — PRE-P13/P21 GOVERNANCE DESIGN ONLY; NO LIVE ADMIN, CLINICAL, PRIVACY, SECURITY, OR PRODUCTION AUTHORIZATION** status, evidence SHA, date, owners pending, and an as-built vs future inventory. It is a platform-numbered technical specification but only a governance-readiness design, not an approved implementation or deployed admin system.

Cover all of the following as *proposed/conditional* requirements:

**A. Scope and phase ownership.** Separate P13-E provider/resource source moderation and accessible warnings from P21-A admin backend, P21-B admin web, P21-C governed clinical review queues, and P21-D audit/maker-checker. Clarify where self-care (P15), clinical review (P10), model governance (P18/P19), policy management (P9/P14/P15), notification/referral (P13), and feature flags are future owners. Admin visibility does not create ownership of clinical or patient data.

**B. Actors, trust, and access matrix.** Inventory patient, resource admin, system admin, clinical reviewer, clinician, source verifier/moderator, data-governance reviewer, institutional owner, operations, and service actor; distinguish current role/permission constants from **unapproved future role/permission assignments**. Include actions `view`, `propose`, `verify`, `approve`, `publish`, `suspend`, `revoke`, `correct`, `audit`, `restore`, `export` where relevant, with required object/institution/source scoping and explicit forbidden actions. Authentication is not authorization; client UI/headers cannot assert identity, role, assignment, MFA, clinical governance, or consent. Current P4 requires trusted actor context and MFA for administrative roles, but no production IdP/admin workflow is configured. Role alone never permits clinical source access, patient record reads, clinician confirmation, model promotion, or policy overrides.

**C. Source-backed provider/resource administration.** Proposed source/rights intake, provenance, field-level verification, timestamps/expiry, lifecycle, amendments, corrections, dual control for critical contacts, source disputes, suspensions, rollbacks, and visible stale/unknown/revoked states. No invented doctors, clinic contacts, helplines, specialties, verification proofs, source import vendor, or real provider data. Do not label synthetic providers as verified. Govern malicious links, URL redirects, source impersonation, source expiry/outage, and safe public-display eligibility. Align with `11_PROVIDER_ROUTING_POLICY.md` without approving its proposed taxonomies or statuses.

**D. Governance surfaces and safe state diagrams.** Conceptual routes/panels for providers, resources, referrals, policy versions, model versions, self-care content approval state, feature flags, audit, operational status, and later clinician review. Label every element **FUTURE / NOT IMPLEMENTED**. Specify read-only and disabled/empty/degraded states wherever the backing verified source, approval, IdP, or authority is absent. Administrative toggles cannot bypass server authorization, clinical policy, provenance, consent, human approval, or a release gate. No button or disabled panel may misleadingly claim an operation succeeded.

**E. Review and maker-checker boundaries.** A proposed versioned decision workflow may distinguish draft/proposed, under review, approved, rejected, superseded, suspended and rolled back, but final vocabulary and authority remain human decisions. Record authorship, reviewers, separation of duties, scoped authorization, reason, version, time, evidence and re-review triggers. For safety-critical content, provider crisis contacts, policy and model approval, and clinician corrections, specify the independent owning governance domain; ordinary admins must not promote unsafe content or override clinical authority. Distinguish a PR approval, technical CI, and actual governed approval.

**F. Referral/notification operational views.** P13 statuses are authoritative only when validated by owning service or external evidence; no fabricated `SENT`, `ACKNOWLEDGED`, `SCHEDULED`, or `COMPLETED`. No direct unapproved referral send, impersonation, provider substitution, or bypass of mandatory **explicit active purpose-specific `REFERRAL_SHARING` consent**, in addition to other applicable legal/governance requirements. Minimal authorized display and non-sensitive notification status; no raw transcript search/export by default, no inferred sharing consent or unapproved destinations.

**G. Audit, privacy, observability, and retention.** Propose audit metadata and access controls for resource changes, consent, sensitive admin actions, policy/model promotions, clinician review/correction, referral status, failed auth and source revocation. Use closed, minimal, access-controlled event fields, not raw patient narrative/transcripts, clinical documents, credentials, bearer tokens, consent bodies, signed links or personal data in generic logs/errors/analytics. Separate audit history from clinical record and from operational telemetry. Audit retention, subject-rights/legal-hold procedures, export rights, break-glass, reviewer identities, cross-institution isolation and incident response are **HUMAN DECISIONS PENDING**; do not select values. Map source corrections/revocations and resulting public display or downstream reference invalidation.

**H. Security and accessibility.** Threat inventory and concrete future negative tests: unauthenticated and non-MFA admin; guessed IDs; wrong institution or object; privilege escalation, role spoof, confused deputy, source poisoning, malicious URL/XSS/CSV formula; stale approval/version; forged verification; concurrent approval/revocation; maker-checker self-approval; unauthorized bulk export, timing/enumeration; audit tamper; exposed error contents; feature-flag bypass; absent IdP, source outage, CI-only approvals and rollback. Accessible keyboard/focus/screen-reader, 320/390px mobile reflow, non-color-only status, safe confirmation/dialog behavior, honest unavailable copy, and locale-review requirements. Future BFF/API has strict `no-store`, safe error mapping, no clinical browser persistence, and backend-owned permission checks. P7 manual path and generic urgent-help navigation must not depend on admin/providers/AI.

**I. Traceability and phase plan.** One source-grounded table mapping **all** `FR-ADMIN-001..010`, `FR-AUDIT-001..007`, **`AC-P21-001..008`**, applicable **`AC-P13-001..011`** and Pre-P13 gate 7 to exact drafted sections, as-built technical evidence if any, required human decision and **LIVE NOT VERIFIED** status. Distinguish the future P13-E/P21 implementations and any safe separately authorized documentation/synthetic UI-contract work; no signed decisions, migration, API or module registration. List open owner/reviewer decisions, explicit STOP triggers, and no inference of clinical production readiness.

## 2. Companion readiness deliverable — `docs/implementation/PRE_P13_ADMIN_PORTAL_READINESS_REVIEW.md` (NEW)

Document the as-built/admin-governance gap and a **proposed unapproved review inventory**, not an official new numbered gate program or an approval. Map each to named **roles only**, existing evidence, missing decisions, required artifacts, risks and adversarial tests, safe possible offline-only work if separately scoped, and STOP conditions:

1. Trusted identity, MFA, role/permission assignment, institution/source/object authorization, separation of duties.
2. Provider/resource provenance, verified sources, correction, expiry, suspension, crisis-source dual control.
3. Maker-checker, clinical/safety/model/policy approval authority versus ordinary administration.
4. Referral and notification operation visibility, required explicit sharing consent, minimization, webhook/external status truth.
5. Audit integrity, privacy, search/export/retention/deletion, tenant isolation, monitoring and incidents.
6. Admin UI/BFF/API accessibility, localization and source freshness/uncertainty copy, no false success.
7. Operations, safe-off defaults, rollback, independent manual path, staged pilot and production release.

Include a decision-record **unsigned template**, owner/risk register and a distinction between technical demo evidence and accountable approvals. P13 readiness's original eight proposed gates (4 OPEN, 4 BLOCKED) remain unchanged, and P21 does **not** suddenly acquire a human-approved gate count. Explicitly note live `AC-P21-001..008` and `AC-P13-001..011` remain unverified where relevant.

## 3. Progress tracker and locked changed-path allowlist

Modify **only**:

```text
docs/25_ADMIN_PORTAL_SPEC.md                                  # new unapproved draft
docs/implementation/PRE_P13_ADMIN_PORTAL_READINESS_REVIEW.md    # new draft review inventory
docs/implementation/38_PROGRESS_TRACKER.md                      # minimal status and §58 record
docs/codex/CODEX_PHASE_PROMPTS/PRE_P13_ADMIN_PORTAL_SPEC_AND_READINESS_PACK.md  # exact prompt copy
```

In tracker §5 mark `25_ADMIN_PORTAL_SPEC.md` **DRAFT — PRE-P13/P21 GOVERNANCE REVIEW PENDING; NO LIVE ADMIN IMPLEMENTATION/APPROVAL**; add new **`# 58. Pre-P13 Admin Portal Specification and Readiness Pack`**. Preserve historical records: do not retroactively overwrite the Pre-P13 (#57) baseline statement that Spec 25 was missing *then*; accurately record it is drafted **now**. Keep P13/P12 runtime NOT STARTED; P11 0/9 (5 OPEN, 4 BLOCKED), P10 0/9, P8-C/P9-C Stage 3 BLOCKED; P21 NOT STARTED; Alembic `p7a_0007`; accepted ADRs unchanged. All source/provider and release approvals remain pending.

**Prohibited in this PR:** application or test code, UI components, scripts, fixtures, API/OpenAPI, auth/MFA wiring, roles/policies/consent changes, ORM/migrations, real data, source ingestion/scraping, admin or clinical decisions, resource publication, clinical copy, providers/models, network/egress, referral send/webhook/notification, feature flags, infrastructure, Docker/CI changes, dependency/lockfile changes, fabricated approvals, provider contacts or synthetic records. No live P13-A/B/C/D/E or P21-A/B/C/D work.

## 4. Quality, PR, and handoff

1. Validate each requirement against canonical text (do not guess paraphrases), exact repository paths, internal Markdown links, document headings/sequence, permissions-as-built, source-of-truth/ADR precedence, privacy/consent, source verification, no fake clinical or admin activation, no patient data/secrets, status language and STOP conditions. Check prompt byte equivalence, four-path allowlist, `git diff --check`, and absence of runtime/dependency/migration changes.
2. Run repository-appropriate local quality checks and report actual results and retries. Wait for **all six** GitHub jobs on the *exact final PR head* to conclude **SUCCESS**: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. Never modify/disable CI to force a pass; report scan warnings separately.
3. Commit and push a **single new isolated feature branch**, open **one PR**, and verify local SHA = remote SHA = PR head = CI run SHA. **DO NOT MERGE**. Do not start other implementation work without independent review.

### Required completion report

```text
STATUS: COMPLETE PRE-P13 ADMIN DOCUMENTATION ONLY / PARTIAL / BLOCKED
BRANCH: phase/pre-p13-admin-portal-spec-readiness
BASE MAIN SHA: af32d98061b4605d405e954de5cde3d380974d8e
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER:
25 ADMIN PORTAL SPEC — AS-BUILT/FUTURE AND P13-E/P21 BOUNDARIES:
PRE-P13 ADMIN READINESS — REVIEWERS, DECISIONS, STOP CONDITIONS:
FR-ADMIN-001..010 / FR-AUDIT-001..007 / AC-P21-001..008 / P13 TRACEABILITY:
MFA/OBJECT AUTHZ / SOURCE VERIFICATION / MAKER-CHECKER / AUDIT / PRIVACY FINDINGS:
HUMAN DECISIONS PENDING:
UPSTREAM GATE STATUS AND NO RUNTIME ACTIVATION:
CHANGED PATHS / ALEMBIC / DEPENDENCIES / UNRELATED CHANGES:
LOCAL TESTS / WARNINGS / RETRIES:
CI RUN ID / EXACT FINAL SHA / SIX JOB CONCLUSIONS:
MERGED: NO
```

**STOP after opening the PR.** This is documentary readiness evidence, not permission to operate an admin console, approve providers/policies/clinical content, change patient records, or send patient information.
