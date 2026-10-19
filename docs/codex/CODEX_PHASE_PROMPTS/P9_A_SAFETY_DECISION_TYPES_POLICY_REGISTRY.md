# SwasthyaSetu AI — Codex Phase Prompt: P9-A Safety Decision Types & Guarded Policy Registry

**Work unit:** `P9-A` only — immutable, deterministic physical-safety decision *contracts* and fail-closed policy metadata/registration. **Not** clinical rule authoring, P9-B engine, P9-C UI, or P8-C Stage 3.

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified base:** `main @ 9a6f5b1190909ab90aa7c0cc87a160a851d84763` (P8-C Stage 2 PR #25 merged at this exact SHA).
**P8 status:** P8-A/P8-B merged, P8-C engineering integration merged **PARTIAL**; real-patient `/messages`, AI consent/egress, retention, provider role binding, confirmation and patient AI UI remain **BLOCKED**. P9-A must not relax any of these gates.
**Branch:** `phase/p9-a-safety-decision-types-policy-registry`
**Alembic:** `p7a_0007` — **must stay unchanged**.
**Delivery:** Feature branch + PR for independent review. **DO NOT MERGE.**

## 0. Objective & non-negotiable gate

Implement a small framework-independent `safety` domain foundation which accurately represents the **five specified routes**, deterministic reason codes, policy identities/versions, clarification and self-care-block flags, and an **explicit, immutable, fail-closed, environment-safe policy registry**. P9-A establishes contracts and configuration validation so P9-B can later implement deterministic evaluation against a **separately approved** clinical policy. P9-C may later add governed patient result integration. An offline synthetic policy *fixture* may be used for tests only; it cannot guide a patient.

**Clinical-rule gate:** `docs/00_PROJECT_MASTER_SPEC.md` §28 says detailed physical red-flag rules live in `docs/08_SAFETY_AND_TRIAGE_POLICY.md`, but that file is **not present** at the verified base. `docs/34_MASTER_IMPLEMENTATION_PLAN.md` §17 expressly permits engine/schema/synthetic fixtures but marks real clinical rule content **BLOCKED** without clinician approval. `docs/adr/ADR-003-deterministic-safety.md` requires deterministic versioned safety authority but does not specify any clinical thresholds. **Do not generate symptoms, vital thresholds, diagnoses, urgency triggers, contraindications, pregnancy/age rules, risk cutoffs or patient-facing emergency advice from model knowledge.** No P9 activation until the future policy is written, clinically reviewed and approved with a recorded, versioned decision.

**Stop on drift:** Verify local clean working tree and exact `origin/main` base; review actual code/specs. If the base differs or an approved policy/another contributor has changed the boundary, stop with `BLOCKED / DRIFT`, report concrete evidence, and do not reset/rebase/discard user work. If a missing clinical decision blocks a piece of P9-A, implement only the safe neutral type/registry subset and record the blocker instead of inventing policy.

## 1. Required authoritative reading

Read from the actual checked-out repository, rather than relying on summaries:

```text
docs/00_PROJECT_MASTER_SPEC.md          # §§6, 28; precedence, safety invariants
docs/01_PRODUCT_REQUIREMENTS.md        # SAFE-001..010, FR-SAFE-001..012
docs/02_SYSTEM_ARCHITECTURE.md         # §14, safety module/capabilities
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md                # §§29–30, PhysicalSafetySignals/SafetyDecision
docs/05_DATABASE_SCHEMA.md             # §13 conceptual future tables, NOT P9-A migrations
docs/06_API_CONTRACTS.md               # §14 future safety.evaluate HTTP shape (NOT active)
docs/07_CLINICAL_INTAKE_SPEC.md
docs/13_AI_ORCHESTRATION_SPEC.md
docs/14_LLM_EXTRACTION_SPEC.md
docs/22_UX_AND_USER_FLOWS.md
docs/23_PATIENT_APP_SPEC.md
docs/26_PRIVACY_CONSENT_SPEC.md
docs/29_ENGINEERING_STANDARDS.md
docs/30_TESTING_STRATEGY.md
docs/33_ERROR_HANDLING_POLICY.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md # §17, P9-A/B/C ownership
docs/adr/ADR-003-deterministic-safety.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md  # AC-P9-001..008
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/implementation/P8_C_INTEGRATION_GATE_REVIEW.md
docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md
docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md
```

Inspect code conventions before implementation:

```text
backend/app/modules/safety/                  # .gitkeep only at verified base
backend/app/modules/clinical_intake/{domain,contracts,public,engine}.py
backend/app/modules/ai_orchestration/{contracts,providers,public}.py
backend/app/modules/provenance/{domain,public}.py
backend/app/shared/{types,modules,capabilities,errors}.py
backend/app/config/{settings,sections}.py    # Environment LOCAL/TEST/STAGING/PILOT/PRODUCTION
backend/app/main.py
backend/tests/{test_clinical_intake_domain,test_clinical_intake_engine,test_ai_registration_privacy,test_module_registry}.py
.github/workflows/ci.yml
```

Repository source-of-truth precedence remains approved clinical policy > Project Master Spec > Architecture > Product Requirements > implementation convenience. **A new engineering draft is not clinical approval.** If `docs/08_SAFETY_AND_TRIAGE_POLICY.md` has appeared in the working branch, inspect and reconcile its actual status; do not overwrite.

## 2. Architecture / exact subphase scope

- Create the smallest cohesive safety module (e.g. `backend/app/modules/safety/{__init__,domain,policies}.py`, optionally `contracts.py` for a real need). Follow the existing typed, frozen/domain-first style. No FastAPI/HTTP, SQLAlchemy ORM, external AI provider/model, P7 private repository, network API, web frontend, or long-lived global mutable registry in safety-domain code.
- **P9-A owns:** closed domain types/values, strict input and decision invariants, policy metadata/version/approval states, immutable explicit registry, registration and selection validation, safe default unavailability, rejection of fake selection in protected environments, engineering-only synthetic metadata fixture, focused tests and truthful docs.
- **P9-B owns (do not implement):** evaluator, clinical rule/condition DSL if needed, real deterministic routing/hard override precedence, input signal extraction, missing-critical-info determination, persistence of decisions, model-nondowngrade policy tests.
- **P9-C owns (do not implement):** public `/safety/evaluate` route, session/consent/encounter authorizations, BFF, patient results UI, urgent-help presentation and degraded flows.
- P9-A may define *interfaces* for evaluation and self-care eligibility only if useful and **not bound at runtime**; do not claim the capabilities are operational. The P8-C Stage 3 approval gates remain open and unchanged. Avoid registering a P9 module in `main.py` or exposing an HTTP route merely to make architecture look complete.

## 3. Required domain contracts, invariants & typing

Design with dataclasses + `StrEnum` or existing library conventions; keep immutable, bounded, strict and framework-independent.

1. `SafetyRoute` exactly:

```text
EMERGENCY
PRIORITY_REVIEW
ROUTINE_CARE
SUPPORTED_SELF_CARE
CLARIFICATION_REQUIRED
```

2. `SafetyDecision` typed output contains route, immutable bounded **machine-only reason codes** (unique, deterministic ordering), exact `policy_id` + `policy_version`, `requires_clarification`, `blocks_self_care`, and safe UTC `created_at` or decision timestamp as specified. For future persistence, conceptual `decision_id`, authorized encounter linkage and `input_snapshot_ref` belong to later governed application/persistence boundaries. Do not require real patient/encounter identifiers to construct an engineering-only decision test. Decide an appropriate typed separation of domain evaluation result vs persisted record, aligned with `docs/04_DOMAIN_MODEL.md`. **No `diagnosis`, medicine, resource link, predictive score authority, freeform medical explanation, treatment or clinician-confirmed label.**
3. Validate all fields strictly: route enum, non-blank trimmed safe ID/version patterns and limits, closed or machine-pattern reason codes, nonempty reasons for any computed decision, unique stable ordering, UTC-aware times and bounded collection size, strict bool flags, no extra/dynamic metadata or personally identifying input/repr. If future policy supplies a configured code set, registry can validate membership rather than interpret prose.
4. Enforce *only logically policy-independent* invariants now: for example, `CLARIFICATION_REQUIRED` is explicit (not silently interpreted as low risk), all unapproved/degraded decisions must block self-care, and no synthetic policy is a production clinical authority. Document which route/flag combinations require **policy-specific** clinical semantics before implementing hard rules; avoid guessing whether a particular route is medically eligible for self-care.
5. Define `PhysicalSafetySignals` as a **closed, typed nonclinical envelope** only if justified by authoritative fields; otherwise explicitly defer concrete signal fields to an approved policy and P9-B. Avoid generic `dict[str, Any]` or unrestricted patient narrative, free-form LLM output, or fabricated symptoms/vitals/age/pregnancy data. No automatic model-to-signal conversion.
6. Error types must be content-free and typed: invalid registration/version/approval, ambiguous duplicate activation, unavailable policy, rejected environment, malformed decision metadata. No raw patient text, source IDs, exceptions or large payloads in logs/telemetry/repr.

## 4. Immutable registry / synthetic fixture / environment isolation

Implement explicit versioned policy metadata and registry independent of any future persistence or live activation. Metadata should be sufficient for auditing without fake clinical approval: policy type/ID/version, safe metadata/checksum of a **canonical deterministic configuration if one exists**, explicit approval/safety classification, supported environments, activation state or explicit selection key and reason-code namespace. Avoid inventing signatory names, dates, credentials or approval record IDs. Real clinical approval is not a Boolean flag that arbitrary application config can turn on.

Required behavior:

- Registration is compile-time/explicit, not filesystem scanning, dynamic plugin discovery, model-generated policy content or mutable global lookup. Reject duplicate `(policy_id, version)`, inconsistent registry metadata, invalid policy state, unsupported policy type, unversioned configuration, inconsistent checksums and unknown/ambiguous policy selection. If a fixture is metadata-only, define exactly what its checksum attests; **do not imply its hash is a clinical signature**.
- Default registry has **no approved active physical-safety policy**. `get_active_policy` (or equivalent explicit selection operation) safely returns unavailable or raises a typed closed error; **never returns ROUTINE_CARE or SUPPORTED_SELF_CARE on absence/failure**. If an internal safe failure decision is useful, its reason/status must explicitly say `POLICY_UNAVAILABLE`, block self-care and avoid faking a clinical route; do not manufacture an emergency clinical disposition without approved rules.
- Allow a tiny **engineering-only, immutable, nonclinical/synthetic fixture** as test data if needed. Make its identity/version visibly `engineering`/`synthetic`, and its class impossible to activate in `STAGING`, `PILOT` or `PRODUCTION` even when caller explicitly requests it. Permit only explicitly opt-in `LOCAL`/`TEST` use; tests for protected environments must call the actual boundary. Do not rely solely on a UI flag. Be careful not to conflate registry metadata test selection with activating a runnable clinical policy.
- Define policy lifecycle/status narrowly and truthfully. Clinically approved records and patient evaluation are not supported by P9-A. Any future clinical-approved state, effective interval, retirement/supersession, audit, persistence and policy activation require separately verified owner evidence and a later phase. A `status="APPROVED"` string from config is not sufficient.
- No rule thresholds, triage criteria or diagnostic knowledge even in an engineering fixture. An engine demo belongs to P9-B and must be labeled non-clinical.

## 5. Specification gap & governance record

`docs/08_SAFETY_AND_TRIAGE_POLICY.md` is **absent at base** despite the Master Spec naming it as the owner for detailed rules. Handle this explicitly rather than hallucinating content:

- Add a minimal **draft/approval-gated specification** at this canonical path only for *architecture and approval boundaries*, or if repo governance rules forbid introducing that as canonical before sign-off, create `docs/implementation/P9_SAFETY_POLICY_GATE_REVIEW.md` and identify the future canonical path. Clearly label `DRAFT — NOT CLINICALLY APPROVED — NO REAL TRIAGE RULES`. It may specify ownership, types, route precedence **as framework-level behavior**, who must approve clinical content, source/effective-date/versioning, severity of missing information, audit/retirement, test protocol, limitations, and the open decisions. It **must not supply purported emergency triggers or medical cutoffs.**
- Record P8-C remaining block and independence from P9, medical-review requirement, future policy approval owner/decision evidence, runtime activation gate and forbidden patient operations. Do not mark `SAFE-003/009` or `FR-SAFE-001..012` clinically verified merely because metadata exists.
- Update `docs/implementation/38_PROGRESS_TRACKER.md` with P9-A scoped status, precise tests/CI evidence, P9-B/P9-C NOT STARTED, P9 macro PARTIAL, P8-C still PARTIAL and patient AI integration still blocked. Add narrow repository-tree/docs references if appropriate; do not overwrite older history.

## 6. Focused test & quality matrix

Add narrowly owned tests, e.g. `backend/tests/test_safety_domain.py`, `backend/tests/test_safety_policy_registry.py` and optional module privacy/architecture tests. Assert at least:

1. All **five exact** route values; no unknown route, no diagnosis or self-care medication fields.
2. Frozen value immutability, field/ID/version/reason-code validation, malformed/duplicate/unordered reason codes, UTC validation, invariant contradictions and strict primitive types; content-safe errors/repr.
3. Explicit `policy_id + version` identity; duplicate registrations, duplicate active selection, missing/unknown version, malformed checksum/metadata, tamper/identity mismatch, unknown approval class, unsupported config and deterministic ordering all fail closed.
4. Default empty/unconfigured registry **cannot** output a low-risk route or allow self-care. All missing/invalid policy paths are safe and never silently pick a synthetic fixture.
5. `LOCAL`/`TEST` explicitly selected engineering fixture is allowed for metadata/test only; `STAGING`/`PILOT`/`PRODUCTION` selection **always rejects** the same fixture. Cross-environment option/feature manipulation cannot enable it.
6. Synthetic fixture is not clinical authority; no real patient/utterance text, AI model response, invented clinical threshold, live network, ORM/persistence, API, BFF, frontend, external provider or P7 state mutation.
7. P8-A/B/C default-disabled/privacy/zero-egress and P7 deterministic tests remain green. No new safety route in `create_app().openapi()` and no `safety_decisions`/`policy_versions` tables unless already present at base. No current self-care can bypass these future safety gates.
8. Correct status reporting: **AC-P9-001** P9-A evidence, **AC-P9-002** typed-shape portion only, **AC-P9-006/007** policy-unavailable and synthetic distinction portions; **AC-P9-003/004/005/008** and all clinically meaningful outcomes deferred to P9-B/P9-C/clinical approval. Do not claim full P9/P8 acceptance.

Run focused tests, full backend no-network tests, full real PostgreSQL suite, Ruff formatter/check, strict mypy, compile/import, `git diff --check`, frontend format/lint/typecheck/build/tests, Docker migrations/health, Playwright Chromium, scope/privacy/egress/secret audit. **All six GitHub CI jobs must PASS on the exact final branch SHA:** `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. Maintain Alembic `p7a_0007`, no dependency or lockfile changes, no weakened CI, no clinical thresholds disguised as synthetic fixtures. If CI reveals unrelated flakes, report precise reproducible status; do not hide by changing tests.

## 7. Permitted files and forbidden changes

Expected:

```text
backend/app/modules/safety/{__init__,domain,policies}.py   # split only if truly warranted
backend/tests/test_safety_*.py
docs/08_SAFETY_AND_TRIAGE_POLICY.md                         # DRAFT only, or gate-review doc alternative
docs/implementation/P9_SAFETY_POLICY_GATE_REVIEW.md        # optional if needed for clarity
docs/implementation/38_PROGRESS_TRACKER.md
docs/03_REPOSITORY_STRUCTURE.md                             # narrow accurate module entry
docs/codex/CODEX_PHASE_PROMPTS/P9_A_SAFETY_DECISION_TYPES_POLICY_REGISTRY.md
```

**Forbidden without separate independently reviewed authorization:** FastAPI `/safety/evaluate` route; P9-B evaluator or clinical logic; P9-C patient UI/BFF; P8-C messages/AI activation; modifications to P7 answer/encounter/facts; production policies, emergency trigger lists, clinical guidance, medication or self-care recommendations, provider data, external egress, real-patient processing; DB models, Alembic/migrations, `main.py` default module composition, config auto-selection, feature-flag bypass; new dependencies/SDKs/services/lockfiles, changed CI gates or broad P1–P8 rewrites.

## 8. PR & handoff

1. Verify a clean base and create `phase/p9-a-safety-decision-types-policy-registry`.
2. Implement only the above, document any genuine specification gap as **OPEN** rather than silently deciding clinical policy.
3. Run the entire quality matrix and new regression tests; inspect final diff for scope/privacy/approval drift.
4. Commit and push to the feature branch; create PR against `main`. Keep PR **OPEN**. Verify all six remote jobs at exact final head SHA. **DO NOT MERGE.**
5. Return a concise, factual report:

```text
STATUS: COMPLETE / PARTIAL / BLOCKED
BRANCH:
BASE MAIN SHA: 9a6f5b1190909ab90aa7c0cc87a160a851d84763
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
P9-A CONTRACTS / ROUTES / POLICY REGISTRY:
ENGINEERING-ONLY FIXTURE AND PROTECTED ENVIRONMENT GUARD:
MISSING 08 SPEC / CLINICAL APPROVAL GATES:
DEFAULT-OFF / NO-API / NO-PERSISTENCE / NO-EGRESS EVIDENCE:
AC-P9 EVIDENCE VS DEFERRED:
FOCUSED / BACKEND / POSTGRESQL / FRONTEND / PLAYWRIGHT TESTS:
CI RUN ID AND ALL SIX CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCIES:
P8-C BLOCKERS PRESERVED:
UNRELATED CHANGES:
MERGED: NO
```

**Stop at PR handoff. Request independent review. No automatic merge or patient-facing safety use.**
