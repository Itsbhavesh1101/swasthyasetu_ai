# SwasthyaSetu AI — Pre-P14 MannSetu Mental-Health Policy Framework and Readiness Pack

**Work unit:** `PRE-P14-MANNSETU-POLICY-READINESS` — **DOCUMENTATION / HUMAN-REVIEW PREPARATION ONLY.** No P14-A/B/C/D runtime or safety activation, no clinical rule or crisis copy authoring, no patient-data processing, no real referrals, and no policy approval.

- **Repository:** `Itsbhavesh1101/swasthyasetu_ai`
- **Required starting `main`:** `8a313aabab31bffbbddfa3d94b79aa045cc7a19c`
- **PR #41:** merged at that SHA; reviewed head `5f81e9440ab0c6b1d965ecf952e194ac56001035` must be tree-equivalent to merged `main`.
- **Suggested branch:** `phase/pre-p14-mannsetu-policy-readiness`
- **Alembic head:** `p7a_0007` — must remain unchanged.
- **Baseline truth:** P14 NOT STARTED; `docs/09_MENTAL_HEALTH_POLICY.md` absent; P13 and P12 runtime NOT STARTED; P21 NOT STARTED; P11 live **0/9 APPROVED (5 OPEN, 4 BLOCKED)**, P10 live **0/9 APPROVED**, P8-C and P9-C Stage 3 **BLOCKED**; P7 deterministic text/touch intake remains available. Existing `docs/08_SAFETY_AND_TRIAGE_POLICY.md` is an unapproved **physical-safety** framework; it is not a mental-health clinical policy.

> **Strict distinction:** A draft policy *framework* can record scope, authority, proposed mechanics, unresolved decisions, and acceptance evidence. **Do not write, simulate as approved, recommend, or activate any real clinical rules, thresholds, questionnaire cutoffs, self-harm/suicide risk classification, crisis helpline details, triage dispositions, psychotherapy, diagnoses, medicines, or patient-facing crisis scripts.** Clinical policy content itself requires accountable source review and prior human clinical governance, as required by Spec 08 and accepted ADR-022. No physician, clinical reviewer, or legal approval is supplied by this prompt or by green CI.

## 0. Mandatory preflight, scope, and source hierarchy

1. Verify GitHub `main` and `origin/main` are both exactly `8a313aabab31bffbbddfa3d94b79aa045cc7a19c`, and PR #41 is merged/tree-equivalent. Confirm canonical `docs/09_MENTAL_HEALTH_POLICY.md` does not exist on that tree. If the baseline changed or the file already exists, **STOP** and report; do not overwrite or silently rebase. Use a **new clean isolated worktree** based on verified remote `main`. Do not touch, clean, reset, or rewrite the user's primary worktree or preexisting untracked files. Track an **exact byte-equivalent copy** of this prompt inside the isolated worktree only.
2. Read source-of-truth and governance before authoring: `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`; `docs/{00_PROJECT_MASTER_SPEC,01_PRODUCT_REQUIREMENTS,02_SYSTEM_ARCHITECTURE,03_REPOSITORY_STRUCTURE,04_DOMAIN_MODEL,06_API_CONTRACTS,08_SAFETY_AND_TRIAGE_POLICY,11_PROVIDER_ROUTING_POLICY,13_AI_ORCHESTRATION_SPEC,14_LLM_EXTRACTION_SPEC,16_MULTILINGUAL_SPEECH_SPEC,23_PATIENT_APP_SPEC,25_ADMIN_PORTAL_SPEC,26_PRIVACY_CONSENT_SPEC,29_ENGINEERING_STANDARDS,30_TESTING_STRATEGY,33_ERROR_HANDLING_POLICY,34_MASTER_IMPLEMENTATION_PLAN}.md`; `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER,P8_C_INTEGRATION_GATE_REVIEW,P9_C_SAFETY_PRESENTATION_GATE_REVIEW,P10_READINESS_GATE_REVIEW,P11_READINESS_GATE_REVIEW,P12_READINESS_GATE_REVIEW,P13_READINESS_GATE_REVIEW,PRE_P13_ADMIN_PORTAL_READINESS_REVIEW}.md`; `docs/research/r3/{R3_FINAL_TECHNOLOGY_STACK,R3_CODEX_DEPENDENCY_POLICY}.md`; and relevant existing P11 privacy, security, and threat-model drafts **as unapproved P11-specific examples, not approved P14 controls**. Verify real paths and titles before writing links.
3. Review the existing MannSetu source-material inventory in `docs/source_material/mannsetu/` (including the blueprint and competitive-landscape documents, if readable using existing local tools). Treat historical proposals and screening instruments as **source proposals, not evidence of adopted clinical standards, approved questionnaires, thresholds, or crisis resources**. Note unavailable or unreadable material accurately; never guess its contents. Do not copy copyrighted external material wholesale. Do not use live public crisis information, real patient examples, or external medical guidelines to fill approval gaps in this work unit.
4. Inspect the actual repo only (do not modify code): `backend/app/modules/mental_health/` and `clinical/policies/mental_health/` placeholders, `clinical/test_cases/mental_health/`, P4 session/consent and P6 patient shell, P7 text/touch, P8 provider gateway / structured extractor **non-authority**, P9 synthetic safety boundary, P13 and resources/referrals placeholders, `apps/patient-web/app/urgent-help/` and reusable generic urgent-help control. Check `app.main` composition, settings/flags, absent P14 API/BFF/UI/state/ORM/model/approved lexicon/provider. Exact current code outranks older documentation snapshots. No real mental-health data, patients, model calls, LLM chat or unsafe testing.
5. Accepted ADRs are binding, particularly ADR-003 (deterministic safety authority), ADR-006/008 (events/PostgreSQL), ADR-007 (explicit registration), ADR-015/016 (verified resources and specialty authority), ADR-020 (safe-off), ADR-022/023 (no fabricated clinical rules/providers), ADR-027 (independent safety fallback), ADR-028 (raw chat not authoritative clinical record), ADR-031/032/033/036–040 (orchestration, research isolation, approval/model/dependency boundaries). Do not silently edit or supersede ADRs. Clinical content, privacy/legal conclusions, region, source, production population, consent, thresholds, language lexicons, model, provider, risk rubric, or release criteria must remain **UNDECIDED / HUMAN DECISION PENDING**.

## 1. Deliverable A — `docs/09_MENTAL_HEALTH_POLICY.md`

Create canonical **09 — MannSetu Mental-Health Policy Framework** (numbered consistently with the project), prominently labeled:

**DRAFT — PRE-P14 TECHNICAL/CLINICAL-GOVERNANCE READINESS FRAMEWORK ONLY; NO CLINICALLY APPROVED MENTAL-HEALTH POLICY, RISK CLASSIFICATION, CRISIS PROTOCOL, PATIENT-FACING COPY, OR LIVE P14 IMPLEMENTATION.**

Record exact base SHA, date, unresolved accountable roles, evidence sources, and approval status. The word “policy” in the filename must not imply the document contains clinical policy that can be executed. Minimum sections:

**A. Scope, historical source reconciliation, and as-built evidence.** Distinguish patient P7 non-diagnostic intake, existing generic urgent-help navigation, P8-A/B technical extraction contracts and P8-C Stage 2 synthetic boundary, P9 physical-safety synthetic rules, P13 provider/resource/referral drafts, and nonexistent P14 runtime. Explain why P8/P9/P13 source components cannot confer P14 medical authority. Separate MannSetu concept design from current accepted specs and human-reviewed clinical content.

**B. Ownership and trust boundaries.** Proposed `mental_health` bounded context for later P14, distinct from `clinical_intake`, `safety`, `ai_orchestration`, `resources`, `referrals`, and `consent`. Preserve P4 pseudonymous session scope, P7 fallback, authoritative actor/session/consent checks, and the role of appointed clinical, mental-health, privacy/legal, safety, linguistic, accessibility, operations, and institution reviewers. No implied therapist relationship, medical diagnosis or 24/7 human response.

**C. Conceptual (future/absent) signal and decision contracts.** Draw **design-only** data flow: pseudonymous message -> independent language-aware safety backstop -> bounded structured mental-health signal extraction -> strict schema/provenance/uncertainty validation -> **clinician-approved deterministic mental-health policy ONLY IF LATER AUTHORIZED** -> `ROUTE_A`, `ROUTE_B`, `ROUTE_C`, `CLARIFICATION_REQUIRED`, or `DEGRADED_SAFE_FALLBACK` as canonical **route-state vocabulary**, not assigned outcomes. Use `04_DOMAIN_MODEL.md` conceptual `MentalHealthSignals` and `MentalHealthDecision`. Never supply concrete clinical signals-to-routes mappings, thresholds, trigger lexicon, checklist scores, hard overrides, emergency instructions, or patient-facing scripts. Design requirements for identity, version, original-language evidence, bounded reason codes, explicit uncertainty, UTC time, policy ID/revision, rejection on missing/expired/unapproved policy, strict inputs, and no LLM-selected route. `FR-MH-008` requires a high-risk override **under an approved future policy**, not a license to invent high-risk criteria.

**D. Independent backstop, ambiguity, and failures — mechanics, not clinical rules.** Describe future high-level safety-backstop architecture independent of provider availability, source-verifiable lexicons/reviewer approvals, Hindi/English/Hinglish and code-switch/negation/historical/quoted speech constraints, ambiguity/abstention, fake tool instructions, incomplete extraction, malformed JSON, provider latency, outages, and contradiction handling. A backstop signal is not a diagnosis; no actual lexical hit list or clinically authoritative fallback route without human rule approval. Explicitly preserve generic urgent-help navigation even when LLM/DB/providers are unavailable, while stating **verified crisis contacts and approved emergency copy are not configured**. No false promise of live emergency response.

**E. Patient workflow and safe copy governance.** Future AI-assisted disclosure, non-therapy/non-diagnostic/non-emergency framing; persistent accessible urgent-help action; privacy-respecting opt-out/stop; clarification vs uncertainty display; minimal crisis interaction once clinically governed; source-backed human-support navigation; age/guardian/assisted-use boundaries. All actual mental-health, crisis, helpline, questionnaire and triage wording is **PENDING accountable clinical and content approval**. Static generic state descriptions may be discussed conceptually but not drafted as crisis guidance. Do not auto-start chatbot or claim a person will respond.

**F. PHQ-9/GAD-7 and other screening instruments — legal/clinical decision gate only.** If historical MannSetu material proposes instruments, mention them as *candidates requiring* licensing/attribution, suitability, age/population/language validation, score interpretation, psychometric/clinical governance, accessibility, crisis escalation and versioned approval. **Do not implement, reproduce the full questionnaires, assert cutoffs, create scoring/risk classification or equate screening results to diagnosis or route.** The clinical assessor, not an LLM or this document, owns whether/how instruments may contribute to later approved decision policy.

**G. Privacy, consent, security and retention.** Existing `GENERAL_PRODUCT_USE` + `clinical_intake` consent is **not transitive** to P14 conversation/processing/storage/external LLM, mental-health records, crisis escalation, analytics or research. Future purpose-specific notice/consent/legal basis, pseudonymity, minors/guardian/caregiver, session recovery, external processor/region/egress, provider training/retention, de-identification and research separation require actual owners. No real patient data sent externally without privacy decisions. Raw narratives/transcripts must not enter generic logs, analytics, browser persistent storage, support tools, URLs or CI artifacts. Retention/deletion/in-flight/revoke/legal hold/backup/audit policy is undecided; no dates or guarantees.

**H. Verified crisis resources and P13 referrals.** No fabricated numbers, URLs, facilities, counselors, or availability. Future `ROUTE_C` resource selection only from an **approved, currently verified** resource registry or human-maintained bundled fallback with governance/expiry/jurisdiction. Generic urgent-help navigation is not a verified contact list. `ROUTE_B` handoff depends on currently unimplemented P13 referral capabilities and requires **explicit active purpose-specific `REFERRAL_SHARING` consent** and all other applicable lawful/governance conditions; never infer it from P7/P14 engagement. No raw transcript sent by default. Optional resource display must fail safely if evidence is absent/stale; do not silently downgrade risk or offer unverified contacts.

**I. Policy lifecycle, evidence, negative tests and human decisions.** Describe only proposed artifact/approval identity, policy source/reviewer matrix, effective interval, rollback, suspension, monitoring, immutable historical decisions, feedback correction, clinical validation corpus and change control. Require adversarial review cases: current vs historical discussion, negation, quotation/third party, ambiguous language, Hindi/Hinglish, backstop and LLM disagreement, malformed JSON, silence/missing context, false reassurance, prompt injection, LLM unavailability, expired resources, referral consent absent/revoked, P13 outage, minors/guardians, UI access, nonleaking telemetry, impersonation, source/provenance errors, and cross-session races. Tests are *proposed*, not executed P14 clinical evidence. Requirements and acceptance mapping: all `FR-MH-001..020`, all `AC-P14-001..013`, relevant `SAFE-*`, consent/privacy/accessibility, P13 dependency, P8/P9/P10/P11/P12/P21 gates. Explicitly mark live P14 criteria **NOT VERIFIED**.

**J. Conditional phase plan and STOP rule.** Do not invent a new accepted P14 implementation plan. Summarize possible separately reviewed documentation, synthetic/nonmedical contract mechanics, detached deterministic mock/failure tests, later clinically authorized policy, UI, registry and referral integrations. **No work from this PR authorizes P14 implementation**. Stop until approved clinical rules and wording, real resources, privacy/security/identity, model/egress, reviewer authority, validated test evidence, supported population/languages, incident/rollback, and pilot/release decisions are recorded by accountable humans.

## 2. Deliverable B — `docs/implementation/P14_READINESS_GATE_REVIEW.md`

Create a **proposed, unapproved P14-specific human-readiness inventory**, prominently **DRAFT — NOT AN OFFICIAL APPROVAL PROGRAM OR P14 ACCEPTANCE**. Do **not** borrow P11's official nine gates or fabricate an `0/N APPROVED` count for P14; the P14 gate count is not currently accepted.

For each proposed review domain specify accountable *roles*, exact repo evidence, unresolved decisions, required future artifacts, negative tests/risks, separately possible synthetic/offline work *only if later approved*, and STOP conditions. Cover at least these domains:

1. **Clinical policy/source/eligibility:** vetted rule authority and source material; qualified approvers; clear population, inclusion/exclusion, uncertainty, disallowed clinical inference, revalidation and rollback.
2. **Pseudonymous session, sensitive privacy/consent and retention:** separate P14 purpose, notice/consent; minor/guardian/assisted care; cross-session leakage; processor/egress/region and support/analytics restrictions.
3. **Independent backstop and signal extraction:** separate no-LLM safety path, bounded strict typed schema, P8 provider nonauthority, language/code-switch, malformed/timeout/hallucination/contradiction handling.
4. **Deterministic A/B/C/clarify/degraded policy:** source-approved override criteria and precedence only in a future clinically authorized phase; version/rollback, abstention and no invented risk scoring.
5. **Urgent-help resources and operational response:** verified live resources or approved bundled fallback, freshness/owner/region, 24/7 expectations not inferred, outage and resource-expiry evidence, crisis content review.
6. **Professional-support referrals:** P13 not implemented, exact external sharing/recipient and explicit `REFERRAL_SHARING` consent, minimal payload, side effects/idempotency, no invented status.
7. **Patient-facing content, multilingual safety and accessibility:** approved copy/translated assets, P12 dependency, visible non-therapy disclosure, urgent-help control, responsive/keyboard/screen-reader, safe opt-out.
8. **Safety regression / governance / incident / pilot-release:** clinically reviewed held-out corpus, disagreement and harmful-error taxonomy, false-negative review, environment safe-off, audit without transcripts, monitoring, incident/rollback, explicit release scope/expiry.

Include an **unsigned** decision/evidence checklist and owner/risk register, and state no documentation, source proposal, generic urgent-help UI, CI, P9 synthetic test, LLM score, PR review, or model benchmark substitutes for clinical approval. Preserve upstream restrictions: P8-C and P9-C Stage 3 blocked; P10 and P11 live 0/9; P12/P13/P21 runtime not started; P13's eight proposed gates 4 OPEN/4 BLOCKED; P7 manual fallback. No new P14 clinical/test approval.

## 3. Scope and exact changed-path allowlist

Modify **only these four paths**:

```text
docs/09_MENTAL_HEALTH_POLICY.md
docs/implementation/P14_READINESS_GATE_REVIEW.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/PRE_P14_MANNSETU_MENTAL_HEALTH_POLICY_AND_READINESS_PACK.md
```

For the progress tracker:

- Mark `09_MENTAL_HEALTH_POLICY.md` as **PRE-P14 DRAFT — CLINICAL POLICY/SAFETY/PRIVACY REVIEW PENDING; NO ACTUAL CLINICAL RULES OR RUNTIME APPROVAL**.
- Keep P14 phase **NOT STARTED**; add **`# 59. Pre-P14 MannSetu Mental-Health Policy Framework and Readiness Pack`** with exact baseline/PR #41 lineage, documentary deliverables, technical-vs-clinical truth, open decisions, cross-phase blocks and STOP conditions.
- Keep all earlier historical records untouched; do not revise source-of-truth docs, accepted ADRs, earlier policy spec, gate statuses, runtime/dependency counts, or previous PR baseline facts.

**Prohibited:** application/test code; models/fixtures/rule definitions; actual screening items/thresholds/lexicons; API/OpenAPI/BFF/UI, microphone/voice, schemas/ORM/migrations, storage/retention implementations, patients/real data, LLM/provider calls or egress, crisis contacts/URL/copy, source scraping, data downloads, real referrals/notifications, feature flags, approved policies, signed human decisions, dependency/lockfile changes, Docker/CI/infrastructure, or unrelated docs. This PR must not alter `08_SAFETY_AND_TRIAGE_POLICY.md` or imply P9 permission.

## 4. Quality checks, CI, PR and handoff

1. Independently audit the source-of-truth for each claim and exact `FR-MH-001..020`, `AC-P14-001..013` mapping. Check Markdown links, tracker section 59 (no duplication), changed-path allowlist, exact prompt byte equivalence, no names/secrets/crisis contacts/patient examples/clinical cutoffs, no hallucinated citations or approval, `git diff --check`, and unchanged Alembic/dependency/runtime. If MannSetu source materials are unreadable, explicitly report rather than claim reviewed.
2. Run applicable existing repository quality gates as feasible; report exact counts/retries/warnings. All **six** GitHub jobs must conclude **SUCCESS on the exact final PR head SHA**: Backend quality; Frontend quality; Persistence integration; Docker and PostgreSQL; Playwright Chromium; Security scans. Never weaken CI or modify unrelated dependencies because of an existing warning.
3. Commit and push the isolated branch, open **one** PR to verified `main`, confirm local SHA == remote SHA == PR head == successful CI run SHA. **DO NOT MERGE.** Stop for independent review. Do not begin P14 runtime or another coding phase.

### Required completion report

```text
STATUS: COMPLETE PRE-P14 DOCUMENTATION ONLY / PARTIAL / BLOCKED
BRANCH: phase/pre-p14-mannsetu-policy-readiness
BASE MAIN SHA: 8a313aabab31bffbbddfa3d94b79aa045cc7a19c
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER:
09 POLICY FRAMEWORK DRAFT — AS-BUILT/FUTURE/NO CLINICAL RULES:
P14 READINESS GATES / CLINICAL-PRIVACY-HUMAN DECISIONS:
FR-MH-001..020 / AC-P14-001..013 TRACEABILITY:
MANNSETU SOURCE MATERIAL AUDIT / MISSING EVIDENCE:
BACKSTOP / DETERMINISTIC NON-AUTHORITATIVE LLM / SAFE FALLBACK:
VERIFIED CRISIS RESOURCES / P13 REFERRAL CONSENT / P12 LANGUAGES:
UPSTREAM GATES / P14 NOT STARTED:
CHANGED PATHS / ALEMBIC / DEPENDENCIES / UNRELATED CHANGES:
LOCAL CHECKS / RETRIES / WARNINGS:
CI RUN ID / FINAL SHA / SIX JOB CONCLUSIONS:
MERGED: NO
```

**STOP after opening the PR.** This is a pre-implementation governance document, not a clinician-approved mental-health triage policy, crisis protocol, emergency resource list, model release, permission to collect patient mental-health conversations, or production authorization.
