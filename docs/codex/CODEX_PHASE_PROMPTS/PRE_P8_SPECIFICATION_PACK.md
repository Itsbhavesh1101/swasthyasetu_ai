# SwasthyaSetu AI — Pre-P8 Canonical Specification Pack

**Work unit:** Documentation prerequisites for P8 — AI Gateway and Structured Extraction
**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified baseline:** `main @ 926f27a5bda456b616061617dfaf1519e302b9d4`
**P7 evidence:** PR #21 merged at that SHA; reviewed branch head `61d04658fc2a7d1c357b77f3eaf79d75e5f8cc5d`; GitHub Actions run `39148572995`: six successful jobs.
**Branch to create:** `phase/pre-p8-specification-pack`
**Scope:** Specification/reconciliation only. **Do not implement P8-A yet; do not merge.**

## 0. Goal and required audit

P7-A/B/C are merged and P8 is the next macro phase. Before writing new AI application code, reconcile missing canonical context required by `docs/codex/CODEX_CONTEXT_RULES.md`: the AI orchestration specification, LLM extraction specification, privacy/consent controls, testing strategy, and error-handling policy. On verified `main`, the corresponding canonical documents appear absent; **recheck the actual repo first**. If any exists under an equivalent approved path, extend/reconcile rather than duplicate. Report any material precedence conflict as **SPECIFICATION DRIFT DETECTED**.

Create the documentation-only prerequisite pack; **do not claim the P8 acceptance criteria have passed** simply because they are specified.

## 1. Preflight and workflow

1. Confirm clean working tree, branch `main`, exact baseline SHA above, current PR #21 merged, and migration head `p7a_0007`. If baseline has moved or worktree is dirty, stop and report before changing anything. Do not reset/discard user changes.
2. Create `phase/pre-p8-specification-pack` from that main.
3. Follow the repo's `CODEX_INSTRUCTIONS.md`, `CODEX_WORKFLOW.md`, `CODEX_CONTEXT_RULES.md`, specification precedence, and R3 technology precedence.
4. Read canonical material, audit the actual P1–P7 implementation and current tests, document unresolved decisions instead of guessing, then create/verify the documents below.
5. Push branch; allow required CI; do **not** merge.

### Mandatory reading — from the actual repository

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md
docs/05_DATABASE_SCHEMA.md
docs/06_API_CONTRACTS.md
docs/07_CLINICAL_INTAKE_SPEC.md
docs/22_UX_AND_USER_FLOWS.md
docs/23_PATIENT_APP_SPEC.md
docs/29_ENGINEERING_STANDARDS.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md
docs/research/r3/R3_ARCHITECTURE_RECONCILIATION.md
docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md
```

Also locate the approved R2 AI adapter contract/research in `docs/research/` (exact paths via repo audit); treat research drafts as guidance beneath canonical specs and accepted R3 decisions. Inspect: `backend/app/main.py`, `backend/app/config/**`, `backend/app/shared/capabilities/**`, `backend/app/shared/modules/**`, `backend/app/shared/errors/**`, `backend/app/shared/observability/**`, `backend/app/modules/clinical_intake/**`, `backend/app/modules/provenance/**`, `backend/app/adapters/ai/**`, `backend/tests/**`, `apps/patient-web/lib/intake/**`, and CI. Do not infer non-existing APIs/capabilities.

## 2. Required canonical specifications

Create/reconcile **exactly these five** missing documents at canonical paths:

```text
docs/13_AI_ORCHESTRATION_SPEC.md
docs/14_LLM_EXTRACTION_SPEC.md
docs/26_PRIVACY_CONSENT_SPEC.md
docs/30_TESTING_STRATEGY.md
docs/33_ERROR_HANDLING_POLICY.md
```

If a canonical spec already exists, audit whether it covers P8 and update narrowly. Do not silently rewrite unrelated policy. Use `OPEN DESIGN DECISION`, `CLINICAL APPROVAL REQUIRED`, `PRIVACY/SECURITY APPROVAL REQUIRED`, or `DEFERRED TO P<n>` as appropriate. All five must be mutually consistent with the existing approved P7 interface, R3 status, and the current repository state. Keep future-phase requirements clearly marked **future**, not claimed implemented.

### A. `13_AI_ORCHESTRATION_SPEC.md`

Define the **in-process project-owned AI orchestration boundary**, `LLMProvider` Protocol and explicit compile-time provider wiring; task-specific services own prompts/schemas, not the gateway. Specify immutable/bounded `StructuredLLMRequest` and `StructuredLLMResult` types; explicit operation/task, language, request/schema/prompt IDs+versions, model/provider metadata, max output tokens, deadline, retry budget, attempt metadata, safe correlation identifiers, usage and latency, and provenance linkage without raw patient data in telemetry. Provider schema contracts are project-owned; no vendor structures in clinical domain. Specify failure categories (`LLM_TIMEOUT`, `LLM_RATE_LIMIT`, `LLM_AUTH_FAILURE`, `LLM_PROVIDER_UNAVAILABLE`, `LLM_REFUSAL`, `LLM_SCHEMA_INVALID`, `LLM_CONTENT_POLICY_BLOCK`, `LLM_UNKNOWN`) and typed degradation. Timeouts and bounded retries on transient errors only, with explicit non-retry cases, no provider-selected clinical fallback without approval. Specify deterministic offline mock, unconfigured/disabled fail-closed behavior, health/observability, secret-handling, and no raw response persistence by default. Define explicit future direct provider-adapter approval path. **Do not select a production model/provider or require/deploy LiteLLM Proxy/MLflow AI Gateway/another service**; no new production network path by implication.

### B. `14_LLM_EXTRACTION_SPEC.md`

Specify **future P8-B** task-owned clinical extractor contract and safe candidate/fact verification, separate from P8-A provider infrastructure. Inputs: bounded recent patient utterance and minimum necessary approved structured encounter context, never unrestricted patient records. Outputs: versioned strict Pydantic-compatible candidate extraction, evidence/source spans or references, missing-information candidates, contradiction candidates and justified uncertainty/abstention, linked prompt/schema/model versions. Pipeline: prompt/source separation -> provider raw-in-memory -> strict JSON parse -> schema validation (`extra=forbid`) -> domain validation -> provenance references -> explicit confirmation/governance -> candidate only. Define complete rejection of unsupported, hallucinated or invented facts; source attribution failures; stale/mismatched session or encounter; prompt-injection and system-instruction conflicts; abstention/degraded behavior. Candidate observations **must not become confirmed canonical clinical facts, diagnoses, medication changes, final triage/crisis routes, emergency dispositions, self-care advice or clinician-approved summaries automatically**. The P7 deterministic questionnaire remains usable without LLM. Specify `/api/v1/intakes/{intake_id}/messages` as **P8-C design only** unless higher-priority API contract states otherwise; do not activate messages in this documentation work. Detail message retention and third-party transfer decisions needing privacy review, not assumed defaults.

### C. `26_PRIVACY_CONSENT_SPEC.md`

Reconcile existing P4/P6/P7 behavior: exact session bearer; SESSION-scoped `GENERAL_PRODUCT_USE` consent covering `clinical_intake`; notice `privacy-v1` at current implementation boundary; protected BFF with server-only HttpOnly bearer; `no-store`; no clinical data in browser storage/PWA caches, URLs, logs, traces, or exception responses. **Do not assume existing general intake consent authorizes third-party LLM transmission.** Define a privacy/consent decision gate for any future external model egress: data minimization, provider purpose/region/retention/subprocessors, institutional DPA/regulatory review, user information and additional consent where required. Until approved, **no real patient data sent to an external provider**. Specify in-memory minimization, prompt/output retention defaults, redaction of telemetry, access controls, audit-safe metadata and deletion, and compatibility with the eventual India DPDP/healthcare legal review. State unresolved decisions explicitly; do not invent retention periods or legal-compliance guarantees. Do not change working P4–P7 consent contracts in this documentation-only unit.

### D. `30_TESTING_STRATEGY.md`

Define phase-specific test matrix and acceptance evidence for P8-A/B/C and cross-system quality gates: fake-provider offline determinism, provider replacement, disabled/unconfigured fallback, explicit feature policy, strict structured-output shape and versioning, timeout/rate-limit/refusal/auth/5xx handling, bounded retries and no-retry cases, malformed JSON, oversized input/output, non-finite numbers, cross-schema version mismatch, spoofed model result/prompt injection, unsupported fabricated fields, provenance/confirmation chain, patient scope/consent, no PHI logging or browser persistence, high-risk negation, safety authority negative tests, and future P8-C PostgreSQL/API/browser integration. Map exactly AC-P8-001..010 to **future** evidence. Existing P1–P7 CI and real PostgreSQL suites must stay green. State which tests are unit/contract/integration/security/E2E, with explicit fixtures and no patient data.

### E. `33_ERROR_HANDLING_POLICY.md`

Document typed application/dependency exceptions, safe error envelope, HTTP translation only where approved, request correlation without PHI, structured/provider failure classes, retry eligibility, degraded/no-provider behavior, error propagation from adapters to orchestration to consumers, and patient-facing failure copy that never fabricates advice. Preserve existing `ErrorCode`/status mapping and P7's `no-store` protections. **Do not add runtime error-code enums, endpoints or transport mappings in this spec phase**; document proposed new codes distinctly as future design decisions. Invalid LLM output must fail closed without promotion to facts or partial mutation; external timeout must not affect deterministic intake or generic urgent-help availability.

## 3. Traceability and phased ownership

Map **AC-P8-001..010**, relevant `FR-CORE-007/008`, `FR-INTAKE-*`, `FR-MH-005` (architecture boundary only), `NFR-TEST-009`, `NFR-SEC-012/013`, applicable `PRIV`, privacy/security and P7 regression requirements. Use exact existing requirement wording/IDs from canonical documents; do not invent requirement IDs.

Subphase ownership must remain:

```text
P8-A — provider-neutral in-process AI gateway; port/adapters; typed error/degradation;
       timeout/retry/version/telemetry scaffolding; deterministic offline mock.
P8-B — task-specific clinical extraction schemas, prompt package/registry,
       validation/provenance/uncertainty, injection and hallucination regression.
P8-C — authorized session-consented clinical-intake message integration,
       patient BFF/UI, persisted/verified workflow and real end-to-end tests.
```

If the actual approved architecture prescribes a different boundary, explain the discrepancy and stop for review; do not silently broaden P8-A. Mark P9 safety rules, P12 speech/translation, P14 mental-health routing, P15 Ayurveda, provider routing and other downstream clinical/operational features as deferred. LLM cannot overrule the deterministic policy hierarchy.

## 4. Cross-document review

Check alignment on: request/result data ownership, signed/source-based evidence, privacy and egress gate, consent semantics, failure type names, field and schema versioning, timeouts/attempts, allowed retry conditions, adapter registration, no raw payload logging/storage, and P8-A/B/C ownership. Preserve existing P7-C auth, consent, access/terminal reads, optimistic concurrency, pack pinning, UI privacy, and error semantics. Flag any unresolved contradiction rather than choosing a weaker policy.

## 5. Files allowed and forbidden

Documentation-only changes expected:

```text
docs/13_AI_ORCHESTRATION_SPEC.md
docs/14_LLM_EXTRACTION_SPEC.md
docs/26_PRIVACY_CONSENT_SPEC.md
docs/30_TESTING_STRATEGY.md
docs/33_ERROR_HANDLING_POLICY.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/PRE_P8_SPECIFICATION_PACK.md
docs/README.md                        # index only, if required
README.md                             # docs index only, if required
REPOSITORY_TREE.txt                   # generated tree update, if required
```

No modification to `backend/**`, `apps/**`, `packages/**`, `tests/**`, migrations, SQL schema, lockfiles, dependency manifests, CI configuration, `deployments/**` or actual clinical source material. An additional doc or ADR requires explicit justification against scope. No installed SDK/provider and no live external AI calls.

## 6. Progress and verification

Record confirmed P7 merge/CI completion in `docs/implementation/38_PROGRESS_TRACKER.md` (P7-A/B/C **COMPLETE**, P7 **COMPLETE**, with PR #21 merge and exact evidence; correct earlier pre-merge status only where warranted). Record five specification artifacts as **specs complete subject to user review**; keep P8 **NOT STARTED**, P8-A/B/C **NOT STARTED**, and AC-P8-001..010 **NOT YET VERIFIED**. Recommended next work unit after merge of this prerequisite pack: **P8-A — AI gateway + provider ports/mock**.

Verification: exact input/reference audits, cross-doc grep/consistency review, `git diff --check`, no code/schema/migration/dependency/CI diff, migration head `p7a_0007` unchanged. Run existing light validation and required six CI jobs on the docs branch (do not disable/bypass them). If a required real CI gate fails, report PARTIAL/BLOCKED, do not claim COMPLETE.

## 7. Deliverable/report

Push `phase/pre-p8-specification-pack`; create a PR against `main` if repository workflow permits; **leave it open, do not merge**. Include concise objective, traceability, approval/egress blockers and checks. Return **only**:

```text
STATUS: COMPLETE / PARTIAL / BLOCKED
BRANCH:
BASE MAIN SHA:
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
DOCS CREATED/UPDATED:
AC-P8 TRACEABILITY:
R3 / PRIVACY / CLINICAL DECISION GATES:
P7 STATUS / P8 STATUS:
TESTS / CHECKS:
CI RUN ID + SIX JOB RESULTS:
ALEMBIC HEAD:
OPEN DECISIONS:
UNRELATED CHANGES:
MERGED: NO
```

**Stop at the specification handoff. Do not implement P8-A until the prerequisite specifications are reviewed and merged.**
