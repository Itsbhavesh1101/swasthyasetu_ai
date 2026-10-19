# SwasthyaSetu AI — Codex Phase Prompt: P10-A Source-Backed Summary Domain (Safe Engineering Subset)

**Work unit:** `P10-A` — pure domain contracts and deterministic, source-backed **synthetic/offline** summary draft mechanics only.
**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified base:** `main @ 9498972eceaa1ec6c647fd8e4dcb7f2e84748583`
**Merge evidence:** Pre-P10 PR #29 MERGED at that SHA; reviewed feature head `e3adfe24eabd88de339b99ac55905e7f062001ee`; all six GitHub CI jobs passed in run `39289065582`.
**New branch:** `phase/p10-a-source-backed-summary-domain`
**Existing Alembic head:** `p7a_0007` — **no migration in this work unit**.
**Delivery:** Commit the narrow implementation, push, open PR against `main`, verify CI on its **exact final SHA**, **DO NOT MERGE** until independent review.

> **HARD APPROVAL GATE:** The Pre-P10 review records **0/9 approvals for live clinician access** (6 OPEN, 3 BLOCKED). Neither trusted clinician authentication/assignment nor lawful access to pseudonymous encounters, clinical summary validation, clinical copy, data lifecycle/retention, persistence or production enablement is authorized. P10-A may therefore implement **domain/test-only mechanics** using entirely synthetic data. It may **not** implement patient- or clinician-facing summaries, real medical synthesis, data reads from actual P5/P7 APIs/DB, actual clinical confirmation, or a production workflow. Engineering tests do not constitute clinical approval.

## 0. Preconditions — verify and stop on drift

1. Confirm `git status --short` is clean and checked-out `main`, `origin/main` and remote main equal `9498972eceaa1ec6c647fd8e4dcb7f2e84748583`. Verify PR #29 merged exactly at that SHA. Do not reset/discard unrelated work. If baseline moved or a conflicting branch exists, report **BASE DRIFT** and stop until reconciled.
2. Verify both specifications exist at `docs/12_CLINICAL_PROVENANCE_SPEC.md` and `docs/24_CLINICIAN_DASHBOARD_SPEC.md`, plus `docs/implementation/P10_READINESS_GATE_REVIEW.md`. Confirm readiness gates still show 0/9 live approvals and **P10-A only conditionally eligible for isolated domain/test work**. If authoritative recorded approvals unexpectedly changed, stop and request a fresh scope decision; do not silently expand implementation.
3. Confirm existing `backend/app/modules/summaries/` is a `.gitkeep` placeholder; `apps/clinician-web` is an empty-state foundation; there is no summary ORM/table/migration or active summary/clinician read/review API. Confirm Alembic head `p7a_0007`.
4. Follow `docs/codex/CODEX_INSTRUCTIONS.md`, `CODEX_WORKFLOW.md` and `CODEX_CONTEXT_RULES.md`, with a written audit and small implementation plan before modifying files. New dependency or cross-module authority drift is a STOP, not a shortcut.

### Read canonical source-of-truth documents (actual files, not inferred contracts)

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md                 # FR-SUM-001..008, FR-CLIN-001..013, FR-PROV-001..007
docs/02_SYSTEM_ARCHITECTURE.md                 # summary owner and domain boundary
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md                        # §37 ClinicalSummary, status, sections and source ownership
docs/05_DATABASE_SCHEMA.md                     # §16 conceptual clinical_summaries — NOT migration approval
docs/06_API_CONTRACTS.md                       # §§15/16/26 future APIs — NOT active

docs/07_CLINICAL_INTAKE_SPEC.md
docs/08_SAFETY_AND_TRIAGE_POLICY.md            # DRAFT — no clinical rules
docs/12_CLINICAL_PROVENANCE_SPEC.md             # newly merged authoritative P10 prerequisite
docs/13_AI_ORCHESTRATION_SPEC.md
docs/14_LLM_EXTRACTION_SPEC.md
docs/24_CLINICIAN_DASHBOARD_SPEC.md            # newly merged P10 section/summary/status design
docs/26_PRIVACY_CONSENT_SPEC.md
docs/29_ENGINEERING_STANDARDS.md
docs/30_TESTING_STRATEGY.md
docs/33_ERROR_HANDLING_POLICY.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md          # §18 P10-A/B/C/D
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md   # AC-P10-001..009
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/implementation/P10_READINESS_GATE_REVIEW.md
docs/implementation/P8_C_INTEGRATION_GATE_REVIEW.md
docs/implementation/P9_C_SAFETY_PRESENTATION_GATE_REVIEW.md
docs/adr/ADR-003-deterministic-safety.md
docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md
```

### Audit existing actual implementation and tests before designing new types

```text
backend/app/modules/patients/{clinical,domain,contracts,public}.py
backend/app/modules/provenance/{domain,contracts,public}.py
backend/app/modules/clinical_intake/{domain,contracts,public}.py
backend/app/modules/identity/{authorization,public}.py
backend/app/modules/ai_orchestration/{contracts,public}.py
backend/app/modules/safety/{domain,policies,contracts,engine,synthetic}.py
backend/app/modules/summaries/
backend/app/shared/{types,capabilities,modules,errors}.py
backend/app/main.py
backend/tests/**
apps/clinician-web/**
.github/workflows/**
```

**Important real-code nuance:** `ClinicalFact`, `FactProvenance`, `VerificationState`, `FactType` and explicit `supersede_fact` exist in P5, whereas P7 `ClinicalIntake`, answers, history and source references are **different patient-reported types**, **not** confirmed `ClinicalFact`. Current `RoleCode.CLINICIAN`, `ENCOUNTER_READ_ASSIGNED` and `SUMMARY_CONFIRM` permission constants do **not** supply a trusted clinician or encounter assignment. P8 candidate outputs are unconfirmed/disabled for real patient workflows, and P9 synthetic routes cannot enter a clinician summary. Use these distinctions throughout.

## 1. Objective and allowed implementation shape

Build the smallest **pure, deterministic, testable** `summaries` domain package that constructs a **source-traceable, immutable draft representation from explicitly supplied, already-minimized synthetic structured items**; supports strict validation, abstention/unknown states, conflict handling, and source-version drift detection **without** generating new clinical claims.

Suggested organization (adapt to repository conventions with a brief justification):

```text
backend/app/modules/summaries/__init__.py        # inert package, no runtime registration
backend/app/modules/summaries/domain.py          # frozen types, section/status/source invariants
backend/app/modules/summaries/contracts.py       # narrow typed input/projection contracts, if needed
backend/app/modules/summaries/projection.py      # pure deterministic draft builder and drift checker
backend/tests/test_summary_domain.py
backend/tests/test_summary_projection.py
backend/tests/test_summary_boundaries.py
```

Only create files that make sense for the actual repository. `summaries` should be **inert unless explicitly imported by tests**; no `app/main.py` registration, no live capability binding, FastAPI router, app service, patient/encounter query, database or provider. Reuse enums/types through stable P5/P7/provenance contracts when justified; do not copy or redefine their authority. No cross-module ORM imports. Do not implement speculative all-purpose clinical summarization or unrestricted free-text transformations.

## 2. Required typed P10-A contracts

### A. Immutable draft and closed section vocabulary

- Model exactly the standard summary sections from `FR-SUM-002` / spec 24: **chief complaint, HPI, past medical/surgical history, medications/allergies, family history, personal history, review of systems, prior investigations**. A clear split between medical/surgical or medication/allergy sections is acceptable **if mapped explicitly** to these requirements and validated through tests. Fixed canonical ordering, stable machine identifiers, no caller-defined arbitrary sections.
- Model `DRAFT` as the **only creatable P10-A summary status**. You may define the canonical future status names (`DRAFT`, `CLINICIAN_EDITED`, `CONFIRMED`, `REJECTED`, `SUPERSEDED`) as enums to align with spec 24, but must **not** provide a permissive P10-A factory/transition/route that lets callers fabricate clinician editing/signature/confirmation or audit credentials. All other state changes belong to approved P10-D.
- The draft contains a bounded set of **immutable assertions/section entries**, each with its supplied original source linkage, verification/source type, optional source version/snapshot token, and explicit _engineering-only/non-authoritative_ classification. No diagnosis, medical inference, treatment, risk score, triage, medication change, recommendation or signed document generation.
- Require bounded counts, string/identifier lengths and immutable detached collections (including nested mappings if any); defend against type-confusion (`bool` as `int`), forged enums, duplicates, out-of-order inputs and post-construction mutation. Use `repr=False` for any potentially sensitive source/claim text. Avoid dumping input/PHI in `ValueError`, exceptions, test snapshots, logs or telemetry.
- Dates, if necessary, are timezone-aware and normalized to UTC. Snapshot/version/source fields are meaningful only as **supplied engineering metadata**, not signatures, authorization, audit evidence or validated provenance. No implicit `now()`/randomness in output; inject stable time/identities when needed for repeatability.

### B. Strict source identity, separation and provenance

- Input is a **bounded, explicitly synthetic, previously authorized-by-hypothetical-caller projection**; it is **not** a generic unsafe `dict` of clinical observations nor a function that reads live patient data. The domain must not claim it itself performed authorization: that future responsibility belongs to the P10-B server boundary.
- Maintain distinct machine `source_kind`/trust categories for (1) P5 typed fact/provenance, (2) P7 structured **patient-reported draft/answer**, and (3) optionally **not-present**/unknown source coverage. P8 `AI_EXTRACTED_UNCONFIRMED` candidates and any P9 `SYNTHETIC_*` safety decisions are **prohibited inputs** in this phase; do not invent their promotion path.
- Require each included claim to be traceable to a supplied matching source ID + section + snapshot/version token when available, and carry the exact P5 verification status or P7 patient-reported marker **without upgrading it**. Source identifiers alone are not permissions; do not implement source-detail fetch or click-through.
- Validate per-input source identity and scope _consistency_ within the synthetic batch (e.g. encounter/snapshot supplied to caller, if modeled). Reject mixed unrelated sources, duplicates or conflicting identity/version data. Do not choose between contradictory source claims by guessed medical priority; preserve an explicit conflict/needs-review/abstention indicator, with both safe source references when provided.
- For source-backed output, **copy only exact supplied structured labels/items** and necessary bounded reference metadata; no NLP rewriting, synonym inference, translation, negation, normalization into diagnoses, causal inference, implied absence, LLM call, fallback clinical boilerplate, or free-text generation. If an input cannot be mapped without semantic interpretation, abstain or mark section unavailable/unknown.

### C. Missing data, medications/allergies and sections

- Separate `UNKNOWN`, `NOT_RECORDED`, `UNVERIFIED`, `RECORDED`, `UNAVAILABLE` as **machine display/readiness states** only where actual completeness evidence permits. `NOT_RECORDED` requires an explicit trusted coverage/completeness assertion in this _synthetic input_; zero entries or an omitted field must **not** be interpreted as verified absence. A missing/partial source must produce `UNKNOWN`/`UNAVAILABLE`, not reassuring copy.
- In particular, NEVER output **“no known allergies,” “none,” “no medications,” “negative,” “cleared”** or equivalent based on empty lists or absence of a data source. An explicitly source-backed textual claim does not become newly clinically verified through summarization.
- Missing standard summary sections should be represented as named abstained/missing/unknown states, not fabricated narratives. Conflicting entries should remain distinct and visibly unresolved, not silently collapsed to the first or latest entry.
- Preserve provenance per assertion and provenance visibility by machine source code/verification; do **not** expose raw source text in error objects or metadata.

### D. Deterministic draft construction and drift

- Pure builder: same input snapshot, ordering, injection clock and source list yield exactly equal output. Sorting must be canonical and deterministic independent of caller insertion order, with explicit bounded tie-breakers; no hidden global state/registration.
- Use only explicitly provided source projections. Refuse unknown section, wrong snapshot/version, malformed or unsupported source kind, contradictory duplicate identity, detached provenance mismatch, and oversized input **with typed content-free failures**; never partially return an apparently successful draft after rejected validation.
- Provide a pure **freshness/source-drift check** taking the draft's referenced source identities/versions and a caller-supplied **synthetic current snapshot**. Classify unchanged/current versus **STALE**/**SOURCE_UNAVAILABLE**/**REVIEW_REQUIRED** as a non-persisted projection flag (not a new canonical ClinicalSummary persisted status), including bounded affected section IDs. Deleted/superseded/rejected/inaccessible/changed/newly conflicting sources must not leave a falsely fresh draft. Never auto-update/silently rewrite old draft assertions.
- Opaque patient, encounter and session IDs must not be embedded in generic logs/errors, and no real subject data is used in fixtures. A supplied source version token is not authorization to view that source.

### E. Strict non-clinical classification / no authority

- All outputs in this subset are **synthetic engineering draft proof only**; not clinician-signed, not patient-facing, not approved for a clinical note. Consider a fixed `ENGINEERING_ONLY` classification and/or an internal-only named factory; reject attempts to supply `APPROVED`, `CONFIRMED`, `ACTIVATED` or other fictitious approval via input.
- No clinician review, confirm/reject/correct mutation, persisted version creation, summary revision, audit/outbox, consent logic or authentication claim in P10-A. Any future clinician-edited assertions must travel through the governed P10-D provenance workflow.
- If actual canonical documents require an authorization-sensitive detail to be resolved before a pure contract can safely be designed, implement the smallest schema/test proof and record the gap as **OPEN — HUMAN APPROVAL REQUIRED**; never invent an approval.

## 3. Tests — exhaustive synthetic and negative-case matrix

Use artificial/nonmedical machine strings only (e.g. `SYNTHETIC_COMPLAINT_A`, `SYNTHETIC_HISTORY_A`), with fake opaque identifiers/versions. No genuine patient data or clinical observations.

**Domain and source invariants**

1. All standard section IDs/order, every allowable synthetic source category, valid synthetic source-backed draft shape, `DRAFT`-only construction, exact reference binding.
2. All nested dataclasses immutable and detached, no mutable nested input retained; rejects wrong primitive/enum, unknown/extra fields when decoding any mapping, malicious/oversize lists, source text, IDs, versions, timestamps.
3. P5 fact verification/source classifications are carried through **unchanged**; P7 patient-reported items stay patient reported and **not** P5 confirmed facts. P8 unconfirmed candidate and P9 toy safety source forms are refused even when their tokens resemble benign data.
4. Unknown source, source-scope mismatch, wrong identity, duplicate source/claim, contradictory versions, repeated fact reference across contradictory sections, unsupported future schemas fail closed; no source is invented.
5. Golden positive fixtures for all populated sections are deterministic; reversing input order produces equal output; multiple independent calls equal exactly; no id/time/random nondeterminism.

**Abstention, consistency, failure**

6. Missing/unknown/partial source coverage, no meds, no allergies, unreadable source and empty authorized list result in safe states; absence **never** becomes a clinically meaningful negative claim.
7. Contradictory and disagreeing synthetic claims remain distinct with conflict/review-required evidence, without auto-resolve, hallucinated narrative, or trust promotion.
8. Source drift: unchanged snapshot → current; changed version, removal, supersession, rejection, unavailable access, outdated snapshot, newly conflicting source → stale/unavailable/review-required per the chosen bounded contract. Source-drift computation **does not** mutate original draft.
9. Invalid input, overflow, bad clock, unexpected exception and wrong type yield content-free typed failure; privacy canary absent from errors, formatted tracebacks and any log lines. No optimistic `CONFIRMED` or complete clinical summary on exceptions.

**Architecture and governed boundaries**

10. Static/import tests show no `summaries` runtime binding, FastAPI summary/clinician endpoints, real clinician-web data route, ORM, summary table/Alembic migration, provider/LLM, network, file egress, P7/P8 mutation or P9 synthetic decision inclusion. It must not import concrete ORM records or act on backend `ClinicalFact` repositories directly.
11. Existing 127 P9 focused safety tests and P8 synthetic tests still pass; P7 user flow remains the current non-diagnostic intake and generic urgent help. P8-C and P9-C Stage 3 approval gates remain explicitly blocked.
12. No unapproved source content in debug `repr`, JSON/error envelopes, test snapshots, metrics, logs or browser storage. Tests prove invalid attempts to confer `clinician_confirmed`, `signed`, `approved`, `medically_cleared`, `self_care_allowed` via malicious inputs fail.

**Acceptance honesty:** A domain-only synthetic draft may provide **partial engineering evidence** toward `AC-P10-004` (and domain provenance aspects of `AC-P10-007`), but it **does not satisfy full AC-P10-004** without authorized source data/validation. `AC-P10-001..009` overall remain **NOT YET VERIFIED / NOT ACCEPTED** for working live clinical workflows. P10 macro remains **PARTIAL** once P10-A engineering subset lands, not COMPLETE.

## 4. Scope boundaries and deliverables

**Allowed changes only where justified:**

```text
backend/app/modules/summaries/{__init__,domain,contracts,projection}.py  # choose minimal actual set
backend/tests/test_summary_*.py                            # new focused unit/security/boundary tests
docs/03_REPOSITORY_STRUCTURE.md                            # honest new-file inventory
docs/implementation/38_PROGRESS_TRACKER.md                # status + scope + evidence
docs/implementation/P10_READINESS_GATE_REVIEW.md          # optional narrow Stage 2 status note only
docs/codex/CODEX_PHASE_PROMPTS/P10_A_DETERMINISTIC_SOURCE_BACKED_SUMMARY_DOMAIN_SYNTHETIC_FOUNDATION.md
```

**Forbidden in this branch:** `app/main.py` activation; production imports/application services; clinician/patient API/BFF/route; real `clinical_summaries` ORM/table/migration, clinical notes storage, audit/outbox writes; live P5/P7 database read; populated clinician-web result panel; clinician authentication/assignment simulations treated as authority; real patients or medical labels in fixtures; unconfirmed P8 promotion, external LLM/AI/egress, generated medical narratives, P9 synthetic route visibility, clinical decision support, P15 self-care or emergency copy; new dependency/lockfile/infrastructure/CI changes; changes to P7/P8/P9 runtime behavior. Avoid unnecessary modification to P5/provenance/clinical_intake existing code.

If tempted to add source-to-domain adapter, live public capability or database layer because `P10-A` contains the word "backend," **do not do so**: this is explicitly the **isolated safe subset**, not the full P10-A clinical service. Do not use incomplete docs as authority for real patient processing.

## 5. Required quality gates and exact-SHA CI

Report actual, not estimated, counts and failures. Run:

```text
git diff --check
Ruff format + lint, strict mypy, Python compile/import
Focused new summary-domain/projection/boundary tests
Full network-free backend suite (record expected PostgreSQL skips)
Full real PostgreSQL integration suite and clean Alembic upgrade/current/check/downgrade recovery; head stays p7a_0007
Frontend format/lint/typecheck, all workspace tests and all three production builds
Docker Compose config/build/migration/non-root/liveness/readiness with actual PostgreSQL
Playwright Chromium all existing journeys, disclose retries/flakiness truthfully
Security scans (secrets/dependencies/image), source/PHI/privacy-scope, API/table/route/egress/isolation checks
```

**All six GitHub Actions jobs on the final pushed SHA MUST pass:** `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. New commits, even documentation-only, require CI on the **new exact head**. No test deletion, xfail, skip or workflow weakening to force green. Preserve migration head and existing dependency locks.

## 6. Tracker and truthful phase classification

Update progress tracker to record that **Pre-P10 specs PR #29 is merged**, with merge SHA `9498972eceaa1ec6c647fd8e4dcb7f2e84748583`. For P10-A record **engineering domain subset implemented/pending review** when code is ready. Keep P10-B, sensitive P10-C and P10-D **BLOCKED** until the specific 9-gate approvals are recorded; P10 macro **PARTIAL** only if the subset is independently accepted (otherwise NOT STARTED/IN PROGRESS as appropriate), never COMPLETE. Keep P8 and P9 **PARTIAL** with all Stage 3 gates open. Keep `12` and `24` as technical specifications, **not clinical/institutional approvals**.

If the safest useful outcome is smaller than specified due to a discovered incompatibility, explain and stop that portion. Never fabricate source fields, facts, approvals or implementation evidence.

## 7. Branch, PR, no-merge rule and return format

Create branch `phase/p10-a-source-backed-summary-domain` from exact base, commit only scoped files, push remote, open PR against `main`. Include provenance/section semantics, synthetic-only scope, acceptance evidence, test numbers, unchanged dependency/migration status and explicit unapproved clinician API/identity/clinical-content gates in PR body. **Do not merge, do not start P10-B/C/D.** Wait for independent code/CI review.

Return:

```text
STATUS: COMPLETE SAFE ENGINEERING SUBSET / PARTIAL / BLOCKED
BRANCH:
BASE MAIN SHA: 9498972eceaa1ec6c647fd8e4dcb7f2e84748583
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
SUMMARY DOMAIN / DRAFT CONTRACT:
SOURCE PROVENANCE AND P5/P7 SEPARATION:
MISSING/UNKNOWN / MEDICATION-ALLERGY SEMANTICS:
CONFLICT / DETERMINISM / DRIFT EVIDENCE:
CLINICAL APPROVAL / NO LIVE PATIENT DATA / NO APIs / NO PERSISTENCE PROOF:
FOCUSED SUMMARY / FULL BACKEND / REAL POSTGRESQL / FRONTEND / PLAYWRIGHT COUNTS:
CI RUN ID AND ALL SIX JOB CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCY CHANGES:
P8-C / P9-C GOVERNANCE PRESERVED:
AC-P10 ENGINEERING EVIDENCE VS OPEN GATES:
UNRELATED CHANGES:
MERGED: NO
```

**STOP after this report.** P10-B/C/D and clinical use remain independently approval-gated.
