# SwasthyaSetu AI — Pre-P13 Provider Routing Policy and Readiness Pack

**Work unit:** `PRE-P13` — **DOCUMENTATION/REVIEW PREPARATION ONLY.** This is not implementation of P13-A/B/C/D/E; not an approved care-routing policy, verified provider directory, referral service, clinical/safety pathway, source-integration, pilot, or production release.

- Repository: `Itsbhavesh1101/swasthyasetu_ai`
- Verified starting `main`: `568ad42047d6671971a9de3834c47b9de0687641`
- Pre-P12 PR #39: merged at starting main; reviewed head `36baaf4ef3687083b2e389579cfacaab17d10413`, merge tree-equivalent (`files=[]`).
- Alembic head (expected, verify): `p7a_0007`.
- Source truth: P13 is **NOT STARTED**; P12 runtime **NOT STARTED**; P11 live **0/9 approved** (5 OPEN, 4 BLOCKED), P10 live **0/9 approved**; P8-C/P9-C Stage 3 remain **BLOCKED**. P7 manual intake remains available.
- Suggested branch: `phase/pre-p13-provider-routing-policy-readiness`.

> **Authorization:** The task authorizes drafting *review documents* only. It does **not** authorize selecting specialty/triage rules, contact records, provider sources, verified status, consent/policy text, clinical thresholds, production integrations, outbound communication, or release. No human approval may be invented, marked as granted, or inferred from CI.

## 0. Preflight — source-of-truth and worktree

1. Fetch `origin/main`; verify GitHub `main` and `origin/main` both equal the exact starting SHA. Verify PR #39 merged and reviewed head → merged tree diff contains zero file differences. If remote main has changed, **STOP, report drift**, and do not silently rebase. Create a fresh **isolated worktree** based on the remote SHA. Do not reset, overwrite, clean, or modify the primary worktree or its preexisting untracked prompt files.
2. Read the three Codex governance documents `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`. Read canonical requirements and decisions: `docs/{00_PROJECT_MASTER_SPEC,01_PRODUCT_REQUIREMENTS,02_SYSTEM_ARCHITECTURE,03_REPOSITORY_STRUCTURE,04_DOMAIN_MODEL,05_DATABASE_SCHEMA,06_API_CONTRACTS,12_CLINICAL_PROVENANCE_SPEC,23_PATIENT_APP_SPEC,24_CLINICIAN_DASHBOARD_SPEC,26_PRIVACY_CONSENT_SPEC,29_ENGINEERING_STANDARDS,30_TESTING_STRATEGY,33_ERROR_HANDLING_POLICY,34_MASTER_IMPLEMENTATION_PLAN}.md`; `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER,P8_C_INTEGRATION_GATE_REVIEW,P9_C_SAFETY_PRESENTATION_GATE_REVIEW,P10_READINESS_GATE_REVIEW,P11_READINESS_GATE_REVIEW,P12_READINESS_GATE_REVIEW}.md`; R3 final stack/dependency policy in `docs/research/r3/`. `docs/16_MULTILINGUAL_SPEECH_SPEC.md` is **draft only** and confers no P12 authorization.
3. Inspect actual relevant repository paths and module composition: `backend/app/modules/{providers,resources,referrals}/` (currently only placeholders), `clinical/policies/provider_routing/`, `apps/patient-web/app/referrals/page.tsx` (currently honest unavailable state), admin-web foundation, `backend/app/main.py`, P4 consent/session/identity, P5 patient/encounter, P7 intake, P8/P9/P10 boundaries, outbox/job ports, and any current provider or referral artifacts. Document discrepancies rather than trusting historical snapshots. **Do not** confuse `backend/app/modules/ai_orchestration/providers.py` (LLM provider adapters) with the future verified clinician/provider directory.
4. `docs/11_PROVIDER_ROUTING_POLICY.md` and `docs/25_ADMIN_PORTAL_SPEC.md` were absent at the starting main. Verify their current absence. `25_ADMIN_PORTAL_SPEC.md` is a separate prerequisite and **not in this work unit**; flag its dependency for later planning, do not fabricate its completion. If either target output path already exists on the current remote, STOP rather than overwrite.
5. Binding ADRs include **ADR-003** deterministic safety authority; **ADR-006/008** events/PostgreSQL authority; **ADR-015** provider/resource contact truth must originate only from a verified registry or validated integration; **ADR-016** care category/specialty *before* provider selection; **ADR-020/022/023/027** safe-off, no invented clinical policy/providers and independent fallback; and ADR-002/007/019/037/038/040 on ports, activation, jobs, profiles, and infrastructure. Do not silently alter an accepted ADR; if a real incompatibility is found, record a proposed ADR issue for human review.

## 1. Primary deliverable — `docs/11_PROVIDER_ROUTING_POLICY.md` (NEW)

Create a comprehensive **DRAFT — PRE-P13 POLICY DESIGN, UNAPPROVED; NO CLINICAL/PRIVACY/SECURITY/PRODUCTION AUTHORIZATION**. This is a proposal for accountable review, not a clinical routing algorithm or real verified directory. Include an evidence baseline, document-control/review state, in/out of scope, exact as-built inventory, and numbered sections covering:

### 1.A Ownership, trust, and terminology
- Separate: verified provider registry, resource registry (crisis/hospital/counselling/public support/institution resources), care category, specialty/service type, facility, contact method, scheduling link, referral, notification, clinical/safety triage, and source provenance. The directory is not an LLM output field; speculative specialty suggestions are not approved triage policy.
- Record current P13 modules/registry/status as **NOT IMPLEMENTED**. P7 deterministic intake is not a clinical diagnosis and must not silently determine specialty, urgency, or suitability. P8-C/P9-C Stage 3 and P10 clinician access remain blocked; P12 language is draft-only.
- State each module's authoritative owner (`providers`, `resources`, `referrals`, `notifications`), compile-time capability/port boundaries, no module-local shadow consent, and no cross-module persistence coupling. Use accepted conceptual schemas/contracts only as draft design evidence, not approved migrations/APIs.

### 1.B Source-of-truth provider/resource lifecycle
- Propose *versioned* source record, source license/permission, author/publisher and institution, last verified time, expiry/recheck cadence (**undecided**), verifier role/proof, status (`UNKNOWN`, `UNVERIFIED`, `VERIFIED`, `STALE`, `EXPIRED`, `SUSPENDED`, `REVOKED` or proposed equivalent), safe correction/appeal and audit lineage. Do **not** silently equate `ACTIVE` status to current verified truth. Mark all proposed enumerations **UNAPPROVED** if not already canonical.
- Define provider fields and validated contact/booking provenance from PRD and architecture, with exact qualifiers for optional fields (facilities, geography, languages, teleconsultation, hours, accessibility, eligibility). Presence of a nonempty URL/phone number is not proof of validity. A link to a provider site is not necessarily a verified booking link. No real provider contacts or crisis helplines may be invented, scraped, or represented as validated.
- Distinguish synthetic fixture records with unmistakable nonreal identifiers from **verified production** records. Require expiration, clock/UTC, revoked sources, record supersession and disallowed external data/PII protections. Stale/unknown cannot silently be served as current verified; where policy permits disclosure of stale data in future, require approved warnings, safety and fallback policy.
- Future import adapters, source validation, review/moderation, dual control for sensitive resource changes, source refresh, and audit are conceptual only. Avoid source-vendor selection.

### 1.C Specialty-first routing — **no invented clinical policy**
- Show conceptual and explicitly **UNAPPROVED** sequence: approved upstream care-category signal/policy → normalized specialty or service type → verified eligible directory query → transparent user-controlled filters → options/source freshness/limitations. Prohibit opaque LLM ranking, fabricated doctor details and reverse mapping an LLM suggestion into a verified contact.
- Define proposed typed decision/metadata contract and versioning (`care_category`, `specialty_or_service_type`, `reason_codes`, `policy_version`, `source`, `created_at`, `abstain/unknown`), without inventing taxonomy, symptoms-to-specialty clinical mappings, urgency thresholds, triage cutoffs or provider ranking weights. No P9 safety decision may be inferred by directory policy. If upstream authority, safety policy, source, or eligibility is missing, abstain and preserve governed/manual options; never fabricate contact or claim success.
- Discuss authorized geography/service coverage, specialty mapping stewardship, age/guardian/institution restrictions, disabled clinicians/facilities, language/availability uncertainty, and conflict/expiry; all actual values and release criteria require human decisions.

### 1.D Referral aggregate and consent boundary — design only
- Reconcile canonical domain's states: `OFFERED`, `CONSENTED`, `SENT`, `ACKNOWLEDGED`, `SCHEDULED`, `COMPLETED`, `DECLINED`, `UNREACHABLE`, `EXPIRED`, `FAILED`, `CANCELLED`. Distinguish intent, consent, *delivery attempt*, delivered/acknowledged external event and appointment completion; do not invent transitions or external confirmations. Produce **proposed** transition matrix and rejection/terminal-state/race invariants, marked for human/app-owner review.
- Explicitly require `REFERRAL_SHARING`-purpose consent or other explicitly governed lawful basis: `GENERAL_PRODUCT_USE`/`clinical_intake` does not authorize external referral disclosure. Required recipient, purpose, per-field minimization, sharing notice, subject/guardian/institution authority, exact active consent, permission checks and expiry are **human decisions pending**. No raw transcript by default; no unrestricted patient history, health-sensitive logs, bearer, contact data outside approved scope. An offered referral does not itself authorize sending.
- Specify future idempotency, outbox, retries, ambiguous side-effect recovery, cancellation/withdrawal races, signed webhook validation, replay defense, duplicate external messages, destination identity, fallback and status correction. No real email/SMS/webhooks/referral sends, contact sharing, or jobs in this phase.

### 1.E Resource and urgent-help failure isolation; notifications
- Verified emergency/crisis resources and any bundled fallback require accountable source, approval, jurisdiction, validity and maintenance. **Do not draft actual helpline numbers, clinical crisis scripts, unsupported urgent routing or translations.** A missing registry/provider/LLM must never make a false promise that help is available, nor break existing generic urgent-help navigation or P7 manual intake.
- Conceptual notifications must be user-authorized, configurable where required, template/version controlled, privacy-safe (no unnecessary lock-screen detail), delivery-adapter based and bounded/idempotent. Do not select channels, providers, messages, recipients, timing or retention without approval.

### 1.F Security, privacy, operational and accessibility threats
- Cover IDOR and cross-subject leakage; unverified/fake contact injection, source impersonation and malicious URLs, stale/expired/crisis resource misinformation, SQL/filter/injection/SSRF issues, malicious imported data, admin/moderator abuse, source poisoning, external-recipient substitution, consent withdrawal, webhook spoof/replay, duplicate send, provider outage, cross-institution disclosure, logs/analytics/notification privacy leakage, link previews, and localized copy. Map to *future synthetic negative tests* and accountable roles.
- Define governance open questions for registry/institution/clinician identity, patient/guardian/caregiver consent, contact/source rights, source licensing/verification frequency, specialty taxonomy and clinical review, local geography, data protection, retention/deletion, access, notifications, integrations, operational incident/rollback, pilot and production release. No legal/compliance claims.

### 1.G Traceability and future phase plan
- Map **all exact** `FR-DIR-001..017`, `FR-REF-001..013`, applicable `FR-NOTIF-001..006`, `FR-AUDIT-002..004`, `PRIV-*`, and `AC-P13-001..011` to document sections, present repository evidence vs missing implementation, human owner, and live status **NOT VERIFIED**. Read exact source wording; never substitute guessed text.
- Map P13-A (providers/resources domain), P13-B (directory query and specialty routing), P13-C (referral domain/state), P13-D (notification adapters), and P13-E (patient/admin UI) to conditional, separately scoped approvals and tests. Only future independently reviewed, nonmedical synthetic contracts/fixtures may be proposed for safe engineering; this draft **does not authorize P13-A** or other implementation.
- Do not use P14 mental-health crisis or P15 self-care use cases to silently authorize clinical routes or patient-facing content. Identify `25_ADMIN_PORTAL_SPEC.md` as a **missing separate pre-P13 prerequisite** for relevant P13-E governance/admin work.

## 2. Companion deliverable — `docs/implementation/P13_READINESS_GATE_REVIEW.md` (NEW)

Create a dated review snapshot with **proposed, UNAPPROVED P13 gates**; do not borrow P11's 9-gate count as an officially established P13 approval model. For every proposed gate include: as-built evidence, what remains undecided, accountable reviewer roles (not invented people), artifacts needed to decide, critical security/privacy/clinical/operational risks, required negative/failure tests, possible separately-authorized synthetic engineering scope, and STOP conditions. Cover at least:
1. verified provider/resource sources, licenses and freshness governance;
2. approved care-category/specialty taxonomy and policy/clinical authority;
3. identity/institution/ownership and patient/guardian consent/sharing;
4. provider/resource registry models, APIs and persistence schema;
5. referral status/consent, minimization, idempotency and side effects;
6. notification/webhook privacy, signatures, retries and incident response;
7. patient/admin UI, copy, accessibility, source warnings, and missing Admin Portal spec;
8. resilience, urgent-help verified fallback, source incidents, rollback and pilot/production release.
Include unsigned human-decision/evidence checklist, current gate statuses, future negative-test catalogue and cross-phase block preservation. This **does not** approve a clinical policy, provide provider verification, or pass a P13 acceptance criterion.

## 3. Progress tracker and exact changed-path allowlist

Only change these **four documentation paths**:

```
docs/11_PROVIDER_ROUTING_POLICY.md
docs/implementation/P13_READINESS_GATE_REVIEW.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/PRE_P13_PROVIDER_ROUTING_POLICY_AND_READINESS_PACK.md
```

Track a copy of **this exact prompt** under the prompt path; verify its content/hash matches the supplied source. In `38_PROGRESS_TRACKER.md`, minimally update the Before P13 `11_PROVIDER_ROUTING_POLICY.md` status to **DRAFT — HUMAN REVIEW REQUIRED, NO LIVE P13 APPROVAL**; retain `25_ADMIN_PORTAL_SPEC.md` as missing where appropriate; add a uniquely numbered Pre-P13 documentation entry following existing section **56**, with verified PR #39 merge tree-equivalence and precise base SHA. Keep **P13 NOT STARTED**. Preserve P11 0/9 approved, P10 0/9 approved, P8-C/P9-C Stage 3 blocked, P12 runtime NOT STARTED, and P7 manual fallback. Do not mark any existing live acceptance as verified.

**Forbidden in this work unit:** application/test code; fixtures; APIs/OpenAPI/BFF/UI; admin changes; provider records/real contacts; clinical mapping/policy activation; real referral/notification; scraping, live network calls, egress or provider evaluation; schema/ORM/Alembic migrations; feature flags; services/queues/storage; dependencies/lockfiles; Docker/CI; accepted ADR changes; patient data; credentials; approvals/signatures, or production-ready claims. Keep the primary worktree untouched.

## 4. Audit, quality, PR and handoff

1. Check exact branch base, changed-path allowlist, references/headings/IDs, factual as-built claims and source hierarchy; every proposed rule clearly unapproved. Verify 11/25 preflight path truth and exact FR/AC status, no real identities/contact numbers/URLs/health data, no fictional verified sources, no invented governance approval. `git diff --check`; no runtime/dependency/migration changes; P13 still NOT STARTED and upstream gate matrix unchanged.
2. Run existing quality checks without weakening workflows. All six GitHub CI jobs **must SUCCESS on the final exact PR head SHA**: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. Report actual counts, warnings/retries and unchanged Alembic head.
3. Commit, push a single scoped branch, open **one PR**, compare local head = remote head = PR head = CI SHA. **DO NOT MERGE**; do not begin live P13 or any adjacent phase. Stop for independent review.

### Required Codex completion report

```
STATUS: COMPLETE PRE-P13 DOCUMENTATION ONLY / PARTIAL / BLOCKED
BRANCH:
BASE MAIN SHA:
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER:
11 PROVIDER ROUTING POLICY DRAFT — AS-BUILT/UNAPPROVED DESIGN:
P13 READINESS GATES / REVIEWER DECISIONS:
FR-DIR / FR-REF / FR-NOTIF / FR-AUDIT / AC-P13 COVERAGE:
VERIFIED-SOURCE VS SYNTHETIC & NO-FABRICATION AUDIT:
CONSENT / PRIVACY / REFERRAL SIDE EFFECTS / STALE RESOURCE GUARDS:
UPSTREAM GATE STATUS / P13 NOT STARTED:
PATH ALLOWLIST / DOC LINKS / PROMPT EQUIVALENCE:
ALEMBIC / DEPENDENCIES / LOCAL CHECKS:
CI RUN ID / EXACT FINAL SHA / SIX JOB CONCLUSIONS:
UNRESOLVED HUMAN DECISIONS / MISSING ADMIN SPEC:
UNRELATED CHANGES:
MERGED: NO
```

**Stop for independent review.** Draft documentation does not authorize clinical policy, actual provider truth, referrals, consent/sharing, external integrations or patient-facing features.
