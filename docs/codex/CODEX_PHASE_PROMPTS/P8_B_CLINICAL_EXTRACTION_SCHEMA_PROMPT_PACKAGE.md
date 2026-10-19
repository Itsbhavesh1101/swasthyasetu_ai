# SwasthyaSetu AI — Codex Phase Prompt: P8-B Clinical Intake Extraction Schemas, Prompt Package & Validation

**Work unit:** `P8-B` only — task-owned, provider-neutral structured *candidate* extraction and offline/adversarial evaluation.
**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified baseline:** `main @ 9d764d381a3c669baac4374ba67dde33536db211`
**Prior evidence:** P8-A PR #23 merged into this commit; reviewed head `1499dc4ada9a5bffbca32be2713c198a00f1ba73`; all six P8-A CI jobs passed at head.
**Create branch:** `phase/p8-b-clinical-extraction-schema-prompts`
**Alembic head:** `p7a_0007` — MUST remain unchanged.
**Merge:** **NEVER merge this branch**. Push and open a PR; wait for independent review.

## 0. Mission

Build a **task-owned** clinical-intake extractor using the existing P8-A `llm.generate_structured` capability, with strict versioned request/candidate schemas; immutable prompt-package metadata and compatibility checks; conservative source/evidence validation; explicit uncertainty, abstention, missing-information and contradiction *candidates*; safe normalized failures; and comprehensive synthetic/adversarial offline tests. The output is a **draft AI-extracted, unconfirmed candidate**, NEVER a canonical or clinician-verified clinical fact. Preserve P7's fully deterministic questionnaire and P8-A's default-disabled AI, privacy safeguards, and provider-neutral interfaces.

**Approval boundary:** `docs/14_LLM_EXTRACTION_SPEC.md` explicitly requires **CLINICAL APPROVAL** for production prompt semantics, extraction schemas and evidence sufficiency. Therefore implement only an **engineering-only, synthetic/offline evaluation package**. All patient-facing/production extraction activation remains **BLOCKED** until documented approvals. Neither this phase prompt nor passing tests grants those approvals.

**Do NOT implement:** P8-C `/api/v1/intakes/{intake_id}/messages`, patient BFF/UI, conversation/utterance persistence, database migrations, intake answer insertion or automated fact promotion, consent changes, provider SDKs, live inference or external egress, P9 safety/triage, P10 summary approval, P12 speech/translation, P14 mental-health routing, P15 self-care/Ayurveda, RAG/agents, networking services, or production clinical question/prompt content. Do not implement diagnosis, treatment, medication change, personalized advice, clinician endorsement, contact/resource generation, or emergency/crisis disposition.

## 1. Preconditions — verify and STOP on drift

1. `git status --short` is empty; current branch `main`; local and `origin/main` equal exactly `9d764d381a3c669baac4374ba67dde33536db211`. Verify PR #23 MERGED and P8-A capability available; Alembic head `p7a_0007`.
2. If branch/base differs, uncommitted user changes exist, required spec differs materially, provider activation is already live, or an approved clinical/privacy policy conflicts, **STOP with `BLOCKED / SPECIFICATION DRIFT`**. Do not reset/rebase/discard automatically.
3. Create `phase/p8-b-clinical-extraction-schema-prompts` from this base. Follow the canonical read → audit → plan → implement → test → diff audit → report workflow. Do not merge.

### Required authoritative reading — actual repository, not memory

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md
docs/06_API_CONTRACTS.md
docs/07_CLINICAL_INTAKE_SPEC.md
docs/13_AI_ORCHESTRATION_SPEC.md
docs/14_LLM_EXTRACTION_SPEC.md
docs/26_PRIVACY_CONSENT_SPEC.md
docs/29_ENGINEERING_STANDARDS.md
docs/30_TESTING_STRATEGY.md
docs/33_ERROR_HANDLING_POLICY.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/research/r3/R3_ARCHITECTURE_RECONCILIATION.md
docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md
docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md
```

Read implementation and tests, at minimum:

```text
backend/app/modules/ai_orchestration/{contracts,providers,application,public}.py
backend/app/adapters/ai/{fake,disabled}.py
backend/app/modules/clinical_intake/{contracts,domain,engine,history,public,content,serialization}.py
backend/app/modules/provenance/{domain,public}.py
backend/app/shared/{modules,capabilities,errors,feature_flags,observability}/**
backend/app/config/**
backend/app/main.py
backend/tests/{test_ai_contracts,test_ai_orchestration,test_ai_registration_privacy}.py
backend/tests/test_clinical_intake_*.py
backend/pyproject.toml
.github/workflows/ci.yml
```

**Verified live integration facts:** P8-A currently exposes `AI_GENERATE_STRUCTURED = CapabilityKey[StructuredGenerationCapability]("llm.generate_structured")`, plus `AI_HEALTH`; `StructuredLLMRequest/Result` and `OrchestrationOutcome` are defined under `app.modules.ai_orchestration`; result `validated_payload` is only a bounded **generic JSON mapping**, not a task-validated clinical schema. P8-A `SourceReference(source_id, source_version, content_hash)` is different from P7 intake's answer/fact `SourceReference`: do not conflate these. P7 `IntakeAnswerSourceType` currently supports `PATIENT_TEXT`, `PATIENT_TOUCH`, `REUSED_HISTORY` only: **do not add or misrepresent an AI-confirmed source there**. P7 question packs are engineering-only (`core.intake@engineering.1`), and patient content routes remain governed by the existing consent/session rules.

## 2. Architecture and ownership

Create a small self-contained package owned by clinical intake, preferably:

```text
backend/app/modules/clinical_intake/extraction/
    __init__.py
    contracts.py      # Strict task input/candidate models, exact version IDs
    prompts.py        # Immutable engineering prompt manifest and compatibility registry
    validation.py     # Evidence, source, domain, provenance, hallucination guards
    application.py    # ClinicalIntakeExtractor using injected P8-A StructuredGenerationCapability
```

Adapt names only if the actual repo conventions require it; document changes. **P8-B must not register a patient API/router or make the default P7 `build_clinical_intake_registration()` depend on the LLM.** The extractor should be constructible for controlled offline tests with an explicitly injected P8-A capability (or a typed provider-neutral test double). No import of concrete provider SDK, adapter or fake into domain models. Never reach across bounded-context private ORM/repositories; obtain future patient context only through approved public capabilities, **deferred to P8-C**. No new global mutable singleton, plugin scanning, runtime-generated unauthorized prompt list or side effects on import.

Do not change P8-A's port/retry/telemetry for task convenience unless a demonstrated contract defect truly blocks P8-B; if so **STOP, document exact evidence and seek separate review** instead of quietly expanding scope.

## 3. Versioned strict input and output schemas

Use installed **Pydantic v2** or an equally strict project-owned typed implementation consistent with `14_LLM_EXTRACTION_SPEC.md` (`extra='forbid'` mandatory on nested models), immutable values, strictly typed fields, bounded arrays/strings/nesting and serialized bytes; no new dependency. Keep field/operation identifiers as closed enums or validated allowlists, with explicit `schema_id/schema_version` and `prompt_id/prompt_version`. All candidate values are **AI-extracted/unconfirmed** and retain immutable provider/model/prompt/schema provenance.

### 3.1 Task input

Support one bounded recent synthetic/source utterance, explicit supported language, a versioned operation ID, immutable source identity/version/content hash and only minimal **authorized** task-specific context if necessary to validate a contradiction. Server-owned identifiers/version metadata are never trusted if supplied by a model. IDs for task correlation are non-patient safe opaque IDs. Input must not contain an entire patient history, identity, session bearer, cookie, consent object, arbitrary provider/model/schema configuration, patient-defined endpoint/headers/tools/system instructions, or another encounter's data. Do not access real persisted encounters or patient sources in P8-B.

Choose clear, **engineering-only maximum limits** satisfying the existing P8-A hard bounds (16 KiB JSON input/output, depth 8, 64 items, 4,096 chars/string, 4,096 max output tokens, max 30 seconds and retry_budget ≤3); mark limits **NOT production approved**, enforce limits in tests, and avoid silent truncation that changes source attribution, negation or temporality. Content must be treated as untrusted *data* and kept separate from prompt/policy/role authority.

### 3.2 Candidate output

Define a closed versioned root envelope with at least:

```text
schema_id + schema_version
prompt_id + prompt_version                 # exact compatibility, no spoofing
candidate_facts[]                        # exact approved field keys/types only
missing_information_candidates[]         # missing-from-submitted-source, not a patient negative
contradiction_candidates[]               # explicit valid source/evidence references on both sides
abstention / refusal / uncertainty        # distinguish lack of support from asserted absence
source/provenance references              # immutable source IDs/versions/hashes
```

Each proposed candidate must have a stable unique candidate ID (prefer deterministic server derivation from exact versioned source/span/field rather than trusting model-generated IDs), a **closed P7-compatible, explicitly allowed** field key/type (e.g., bounded chief-complaint wording / non-inferential descriptive HPI fragment / configured history-section text, not invented medical codes), a bounded literal supported value, source-reference+span/quote, and **only** `AI_EXTRACTED_UNCONFIRMED` or another explicitly unverified state. If confidence exists it must be finite, bounded and non-authoritative; no fabricated clinical probability. A model must never select `CONFIRMED`, `CLINICIAN_VERIFIED`, `APPROVED`, `TRIAGED`, or final routing authority.

Missing-information candidates require a supported bounded field key, source ref(s) and machine reason codes. **Absence in one sentence is not evidence that the underlying clinical condition is absent**. Contradictions require the two distinguishable, valid source/spans (or multiple conflicting spans within a known source), never a model-selected winner. Represent uncertainty and task abstention deterministically and transparently. Unknown nested properties, unrecognized enum values, duplicate candidate IDs, duplicate incompatible claims, oversized counts/text, unsupported language/schema or invalid dates/numbers reject the **entire extraction**, not partial fields.

**Explicitly exclude from all schemas:** diagnosis / diagnosis certainty, treatment recommendation, prescriptions, dose change, provider/referral/contact, emergency or crisis action, final triage category, safety rule override, clinician-approved summary, patient/clinician confirmation, clinical scores and other P9–P15 policy results. Prevent both direct and nested aliases/extra-key smuggling; do not silently drop fields from invalid payloads.

## 4. Evidence, authority, verification and provenance

Build a **conservative source-bound validator** *after* generic P8-A success and *after* strict task-schema validation:

1. Verify exact originating operation, request ID, request-contract version, schema+prompt IDs/versions, and returned P8-A `ResultProvenance` provider/model identity and source references. Reject mismatches, spoofed model metadata, stale or substituted source version/hash, unknown source, wrong session/encounter metadata if ever presented, duplicate IDs and cross-source leakage. The task input source is the only authority for source bytes/normalization/hash; do not trust hashes echoed by generated output.
2. Resolve each evidence `start/end` against **the exact normalized source string** using documented Python character indexing/Unicode rules; require valid half-open span, nonempty content and exact matching quote when a quote is given. Enforce semantic conservative support: the **normalized candidate value must not introduce information absent from that span**. If a mapping would require clinical interpretation (negation/temporal parsing, dose normalization, medical code selection, inferred diagnosis, implied symptom absent), **abstain or reject pending approval**, not guess. Exact substring match alone is not proof of medical truth; the supported engineering subset may permit only literal/extractively copied content.
3. Distinguish subject, negation, temporality and attribution. Historical, hypothetical, third-party, ambiguous negation or double-negation examples must *not* be promoted to asserted current patient facts; represent uncertainty/clarification/abstain where evidence is insufficient. Never infer a negative clinical finding from silence.
4. Verify candidates' source references and immutable prompt/schema/provider/model versions. Keep original/source evidence link for future governed confirmation. No hash/signature claim unless an actual signature scheme exists. Data hashes and source IDs are linkable/sensitive and must NOT be emitted to generic telemetry.
5. Return immutable **candidate objects only**, detached from the canonical clinical-fact/provenance aggregate. **Never** call P7 `answer`, `complete`, patient fact creation/supersession, provenance writes, outbox or any database operation from the extractor. Patient confirmation ≠ clinician confirmation; P8-C must design the governed reconciliation separately.

On any invalid item reject the entire output. Typed failure categories must not echo clinical content, spans, provider raw output, exception strings, secrets or prompts; reject structurally invalid output even if it contains one valid candidate. Do not call clinical rules or attempt to choose a medical safety path.

## 5. Prompt package and injection defense

Define an immutable, compile-time registered **engineering-only** extraction prompt/package manifest containing:

```text
prompt_id / prompt_version; task and supported language(s);
schema_id / schema_version; purpose; content hash;
approval_state = ENGINEERING_ONLY / NOT_CLINICALLY_APPROVED;
strict output contract identity; synthetic fixture IDs; safe fallback semantics
```

Include a minimal *nonproduction* task instruction template sufficient to test role separation, constrained schema, literal evidence, abstention and absence of authority. **Do not invent medically approved questions, thresholds, clinical knowledge, diagnosis or treatment instructions.** Any real clinical prompt approval remains an open gate. The `StructuredLLMRequest.input` currently forbids `system_prompt`/`tools`/`policy_overrides`; do NOT bypass these by embedding authority as patient fields. Keep task instructions in the trusted package/manifest and patient utterances in a separate untrusted structured-data field. Document how a future approved adapter would keep system/task roles separate without adding a real adapter now.

Check prompt/schema/content-hash/version compatibility **before** invoking P8-A and again **after** the response. Unsupported package IDs/languages, tampered registry entries, version mismatch, unknown instruction keys, provider-supplied prompt identity and fake "system" instructions in patient text must fail closed. Tests should cover indirect/quoted/encoded prompt injection, JSON/XML/system-message spoofing, attempts to request secrets/tools, fake schema and model metadata, and nested banned result keys. Patient content must never become execution/configuration/policy.

## 6. P8-A interaction, failure handling and deterministic fallback

Create `ClinicalIntakeExtractor` with an explicit injectable `StructuredGenerationCapability` and immutable prompt registry. Its behavior:

```text
validated engineering-only task input and task approval gate
  -> resolve fixed compatible prompt/schema assets
  -> construct bounded StructuredLLMRequest + P8-A SourceReference(s)
  -> call P8-A `generate_structured` once under its existing deadline/retry policy
  -> if typed provider failure: task-level safe degraded/failure result (no fabricated extraction)
  -> if provider success: verify request/result/provenance metadata, finish_reason and task schema
  -> evidence + source + conservative domain checks
  -> strict immutable AI_EXTRACTED_UNCONFIRMED candidates or safe abstention
```

For the default disabled/unconfigured provider, return a **typed unavailable/degraded** outcome and instruct any future integration to retain deterministic P7 manual text/touch flow. Treat `LENGTH`/incomplete output, wrong root, malformed JSON where a strict-parse helper is used, refusal, content-policy block, schema invalid, invalid provenance, stale source and unexpected dependency exceptions as non-authoritative failure. Never claim the data was saved, never automatically retry an ambiguous/mutating patient POST (there is none in P8-B), and never issue provider calls from an HTTP or browser action.

**Format repair:** do not silently resend malformed output or weaken the schema. Default is **no repair**. Only if canonical task policy explicitly approves a future separately tracked bounded repair operation may it be added later; P8-A does not infrastructure-retry schema failures.

Keep all input, raw outputs and candidate payloads transient in memory; no file/database/event/metrics/log storage of utterances or prompts. No fake-provider selection outside LOCAL/TEST and explicit composition. No live provider, external egress or real patient data in this phase. Respect existing P8-A error taxonomy, attempt/deadline/config limits; do not edit them to make a test green.

## 7. Tests — mandatory synthetic offline adversarial matrix

Use the P8-A `DeterministicOfflineLLMProvider` and/or independent capability doubles with **synthetic, clearly fictional** text. Use fixed injected clocks and exact versioned requests so fake fixtures match; never call an external model, use actual patient data, or rely on probabilistic output. Add focused tests such as `backend/tests/test_clinical_intake_extraction_*.py`.

**Strict schema & versioning**
- Happy path with one evidence-backed literal candidate; empty/abstention path; missing and contradiction *candidate* shape checks.
- Invalid JSON (strict JSON helper if applicable), empty/wrong-root/truncated response, wrong nested types, extra top-level/nested fields, duplicate/oversize arrays, duplicate candidate IDs, malformed dates/numbers, NaN/Inf, unsupported field enum, illegal verification state, unsupported language/schema/prompt/manifest/content hash.
- Wrong request ID, operation, request contract, prompt/schema versions, provider/model identities, missing/forged source refs, `LENGTH` finish and forged successful result; reject as complete failure without retry or partial acceptance.

**Evidence and semantic authority**
- Valid Unicode offsets; out-of-range/start≥end; stale source hash/version; source mismatch; forged/unsupported evidence quote; unrelated span; cross-source reference; value not supported by source; conflicting model statements; truncation that changes "not" or temporality.
- Negation, double negation, historical vs current, third-party reports, hypothetical/quoted statements, uncertainty, missing evidence; choose abstention/clarification or rejection instead of asserting unsupported health claims.
- Missing/contradiction machine reason and reference validation; no automated winner/clinical fact promotion.
- Forbidden diagnosis, dosage changes, medicine/allergy invention, provider contact, emergency route, final triage, mental-health crisis route, treatment/self-care, clinician-confirmed summary — reject even under nested/synonym field attacks.

**Injection and privacy**
- Direct/indirect/encoded role spoofing, fake system/tool instructions, JSON output contamination, instruction in quoted patient data, fake "verified" field and prompt/schema/provider override are inert or cause safe rejection; never modify configured instructions/policy.
- Canary checks in logs, spans, metrics, exceptions, `repr`, reports, disabled/error/timeout paths: synthetic patient content, source spans/IDs, consent/session tokens, model raw content and prompt text never leak. No telemetry high-cardinality personal IDs.
- The extractor does not write P7 answers, patient facts, provenance rows, message tables, outbox or any other persistence; no unintended API route; no new response fields exposed to patient browser.

**Integration/boundary regression**
- Injected P8-A disabled/unconfigured/fake success/schema failure/refusal/rate limit/timeout/unknown failure; correct typed outcomes; no invented candidate, no implicit retry and no loss of deterministic intake.
- The provider-neutral task service imports only project-owned interfaces (no concrete external SDK/fake in production module) and uses explicitly injected capability. Fake must not activate in protected environments; external egress and patient messages remain disabled.
- Existing full P7 session, consent, cross-session IDOR, optimistic concurrency, questionnaire engine, draft-only semantics, browser privacy, urgent help and P8-A retry/contract tests remain green.

Tests must be real assertions for both accepted output **and forbidden behavior**. Do not claim clinicians reviewed a synthetic corpus; mark **CLINICAL EVALUATION/APPROVAL REQUIRED** separately. If product validation requires a real clinical expert, provider, policy or fixture not approved, deliver only the safe tested scaffold and report the gate as BLOCKED rather than inventing authority.

## 8. Exact acceptance mapping

- `AC-P8-003`: P8-B task-specific versioned *engineering-only* schema and strict tests; distinguish schema implementation from deployment/clinical approval.
- `AC-P8-004`: P8-B strict malformed JSON/output/domain rejection, no partial success, no hidden repair; P8-A infrastructure retry already implemented.
- `AC-P8-006`: prompt/schema/model/provider version and source-reference provenance verified end to end *in-memory*.
- `AC-P8-007`: candidate evidence and immutable provenance preserved through the extraction pipeline; persistent governed provenance is future P8-C (not claim completed here).
- `AC-P8-008`: unsupported/hallucinated claims fail closed, and no AI candidate is promoted to trusted fact; semantic evaluation/clinical approval remains open.
- `AC-P8-009`: malicious patient content cannot rewrite prompts/roles/schema/policy or create authority; prove with deterministic adversarial cases.
- `AC-P8-010`: task schemas have no authoritative triage/crisis/emergency routing; explicit forbidden-field and integration-negative assertions.
- `AC-P8-001/002`: preserve passing provider-neutral port/offline mock tests and P8-A regression.
- `AC-P8-005`: preserve P8-A typed degraded behavior and validate P8-B task-level fallback; actual patient UX fallback belongs to P8-C.

**Do not mark P8 macro phase COMPLETE.** P8-C has not begun; real patient integration and clinical/privacy approval remain pending. Report each AC as `P8-B implementation evidence passed` versus `overall partial / subject to future phases or approvals` where applicable.

## 9. Scope, dependencies, files and quality gates

Expected files:

```text
backend/app/modules/clinical_intake/extraction/**   # task-owned only
backend/tests/test_clinical_intake_extraction_*.py # new tests
backend/tests/test_ai_*.py                     # narrowly only if required
backend/app/modules/clinical_intake/__init__.py # optional exports only, no runtime activation
docs/implementation/38_PROGRESS_TRACKER.md
docs/03_REPOSITORY_STRUCTURE.md                # reflect newly created package if applicable
docs/codex/CODEX_PHASE_PROMPTS/P8_B_CLINICAL_EXTRACTION_SCHEMA_PROMPT_PACKAGE.md
README.md / REPOSITORY_TREE.txt                 # narrow index updates if needed
```

**Forbidden changes absent a separately reviewed blocker:** `backend/app/main.py` default composition; `backend/app/modules/clinical_intake/{api,application,domain,contracts,engine,history,serialization,content,public}.py`; `backend/app/modules/ai_orchestration/**`; `backend/app/adapters/ai/**`; P7 intake APIs/UI; `apps/**`; SQL, Alembic, models, migrations, consent/session policy, production providers/SDKs, network/infra/CI jobs, package manifests or lockfiles. No new dependencies/containers/services, production prompt versions or live API. If strict task types genuinely require Pydantic, **use the already installed Pydantic v2**; do not add it again or alter locked versions.

Verification before PR:

```text
git diff --check
Python format/lint (Ruff), strict mypy, compile/import checks
Focused P8-B extractor/schema/adversarial tests
Complete network-free backend tests
Existing P8-A contract/orchestration/privacy tests
Existing P7 domain/engine/API + all other backend tests
Real PostgreSQL integration suite and clean Alembic migration cycle (head p7a_0007)
Frontend formatting/lint/typecheck/tests/production builds
Docker/Compose PostgreSQL health/migration checks
Playwright Chromium (existing journeys)
Security scans and scope/privacy/secret canary audit
```

All **six GitHub CI jobs** must pass on the **exact final SHA**: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. Never weaken/remove/skips existing tests, branch protections, audits or CI jobs. No silent test fixture rewrites to hide failures. Update tracker honestly (CI pending vs verified) and note **P8-A merged; P8-B implementation complete subject to independent review; P8-C NOT STARTED; P8 overall PARTIAL**. Keep production provider, external egress/consent, clinical approval, message retention and governed confirmation unresolved.

## 10. GitHub PR handoff — DO NOT MERGE

Commit scoped files, push feature branch, create PR against `main`. Include objective, exact safety/approval/egress boundary, AC-P8 traceability, synthetic offline regression evidence, full six-job CI run, no migration/dependency changes, and outstanding gates. Leave PR OPEN. Do not merge or start P8-C.

**Report only:**

```text
STATUS: COMPLETE / PARTIAL / BLOCKED
BRANCH:
BASE MAIN SHA:
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
P8-B IMPLEMENTATION:
TASK SCHEMA / PROMPT PACKAGE (engineering-only):
SOURCE EVIDENCE / PROVENANCE / VERIFICATION GUARDS:
ADVERSARIAL / HALLUCINATION / INJECTION RESULTS:
DEFAULT-OFF / NO-EGRESS / NO-PERSISTENCE EVIDENCE:
AC-P8 TRACEABILITY:
FOCUSED / BACKEND / POSTGRESQL / FRONTEND / PLAYWRIGHT TEST COUNTS:
CI RUN ID AND SIX JOB CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCY STATUS:
APPROVAL BLOCKERS / OPEN DECISIONS:
UNRELATED CHANGES:
MERGED: NO
```

**STOP once PR and CI are complete. Await independent GitHub code review before merge.**
