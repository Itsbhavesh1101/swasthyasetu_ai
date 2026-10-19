# SwasthyaSetu AI — Codex P11-C: Synthetic Document Classification & Explicit Processor Registry

**Work unit:** `P11-C` — **SAFE ENGINEERING SUBSET ONLY**: immutable document-type and processor-descriptor contracts, an inert explicit registry, and deterministic synthetic evidence/abstention tests. **No medical document classification or extraction, no live document workflow.**

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified starting branch:** `main @ a8dea0b374017793f119a85daa971b8256881ab4`
**P11-B merged:** PR #32; reviewed branch head `3c9bed8836ac0a672e9f9054e7c10d9458bf08ab`; merge commit `a8dea0b374017793f119a85daa971b8256881ab4` has an identical tree to the reviewed head.
**New branch:** `phase/p11-c-synthetic-document-registry`
**Canonical technical spec:** `docs/15_DOCUMENT_AI_OCR_SPEC.md`, especially §§3.1, 5–8, 10–11.
**Approval matrix:** `docs/implementation/P11_READINESS_GATE_REVIEW.md`: **0 of 9 approved, 5 OPEN, 4 BLOCKED** for live P11 operation. The matrix's dated repository snapshot predates P11-B and must not be mistaken for present-code inventory.
**Alembic head:** `p7a_0007`, unchanged.
**Delivery:** feature branch → push → PR against `main` → all six GitHub CI jobs green **on the exact final remote SHA** → **DO NOT MERGE**. Await independent review.

> **Hard scope restriction:** P11-A live upload/storage is not authorized; P11-B only implemented pure OCR-shaped contracts, test-only mock, and synthetic attempts, not real OCR. No production classifier, medical-content inference, model/OCR engine, external dataset, real patient file, approved clinical extractor or clinician review capability exists. P8-C, P9-C Stage 3 and P10-B/C/D live gates remain blocked. Never transform a registry descriptor, mock OCR result, opaque ref or declared document label into a clinically verified fact, upload permission, provider selection, or production capability.

## 0. Preflight, governance and repository reconnaissance

1. Verify `git status --short` clean, current `main`, `origin/main`, and GitHub remote main all **exactly** `a8dea0b374017793f119a85daa971b8256881ab4`; confirm PR #32 merged with this merge SHA and tree-equivalent reviewed head. Refuse base drift and avoid resetting/discarding user work. Confirm no P11-C branch conflicts before creation.
2. Read exact canonical documentation: `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`, `docs/00_PROJECT_MASTER_SPEC.md`, `docs/01_PRODUCT_REQUIREMENTS.md` (`FR-DOC-001..023`, especially `FR-DOC-010`, `FR-DOC-023`), `docs/02_SYSTEM_ARCHITECTURE.md`, `docs/03_REPOSITORY_STRUCTURE.md`, `docs/04_DOMAIN_MODEL.md` §§33–36, `docs/05_DATABASE_SCHEMA.md` §15 **conceptual only**, `docs/06_API_CONTRACTS.md` §§17–18 **conceptual only**, `docs/12_CLINICAL_PROVENANCE_SPEC.md`, `docs/15_DOCUMENT_AI_OCR_SPEC.md`, `docs/26_PRIVACY_CONSENT_SPEC.md`, `docs/29_ENGINEERING_STANDARDS.md` §71, `docs/30_TESTING_STRATEGY.md`, `docs/33_ERROR_HANDLING_POLICY.md`, `docs/34_MASTER_IMPLEMENTATION_PLAN.md` §19 P11-C, `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER}.md`, `docs/implementation/P11_READINESS_GATE_REVIEW.md`, `docs/implementation/P10_READINESS_GATE_REVIEW.md`, `docs/implementation/P8_C_INTEGRATION_GATE_REVIEW.md`, `docs/implementation/P9_C_SAFETY_PRESENTATION_GATE_REVIEW.md`, and R3 OCR/dependency policies.
3. Inspect actual merged code: `backend/app/modules/documents/{__init__,contracts,ports,processing}.py` and all `backend/tests/test_document_*`, `backend/tests/ocr_support/**`; existing registry idioms in `backend/app/modules/safety/policies.py`, `backend/app/modules/clinical_intake/pack_validation.py`, and `backend/app/shared/modules/registry.py`. Their patterns are **examples**, not authority to register document providers or reuse safety policy activation.
4. Verify `backend/app/main.py` and module capability wiring have **no** documents registration, no real OCR adapter, no document database ORM/migration, no patient/clinician document routes, and the patient `/documents` remains unavailable. Existing P11-B tests must stay green. Verify actual Alembic head `p7a_0007`.
5. Record the precise proposed file list and key design decisions before editing. If the requested subset needs an unapproved real-file source, clinical classifier, scanner, storage, provider, patient/clinician actor, integration, or schema decision, **STOP that portion**, state the blocker; do not silently widen P11-C.

## 1. Objective: a closed type vocabulary and a no-IO classification decision

Create a small pure `documents` package addition, preferably `backend/app/modules/documents/classification.py` and `backend/app/modules/documents/registry.py` (choose minimal actual filenames following conventions). **Nothing here may execute a processor or classify actual medical page text.**

### A. Canonical `DocumentType` and classification outputs

1. Use precisely the technical spec's closed document categories: `PRESCRIPTION`, `LAB_REPORT`, `DISCHARGE_SUMMARY`, `DIAGNOSTIC_REPORT`, `IMAGING_REPORT`, `REFERRAL_LETTER`, `OTHER`, `UNKNOWN`. These are **type labels**, not evidence that any clinical content is genuine. Distinguish `UNKNOWN` (no reliable single label), `OTHER` (explicitly outside six registered processor classes), ambiguous/conflicting proposals, unsupported declaration, and absent evidence; none selects a medical processor.
2. Any classification proof must consume **only explicitly supplied synthetic machine-labeled input** (e.g. a closed `DocumentType` proposal or bounded synthetic nonmedical reason code). It must not inspect OCR text blocks, filenames, file extensions/MIME signatures, screenshots, bytes, image geometry, natural language, or source URLs; it must not implement heuristics, keyword rules, ML or LLM inference. If a pure classifier function is not justified, implement only a strict classification **decision validator/normalizer** and explicit abstention result.
3. Make any decision immutable, versioned and bounded, with `ENGINEERING_ONLY` fixed classification; explicit `SELECTED`, `ABSTAINED`, `CONFLICT`, `UNSUPPORTED` machine dispositions (or an equally clear closed vocabulary); preserve the exact caller-supplied synthetic candidates/source IDs without upgrading trust. Require any selected type to be **exactly one** of the six recognized categories from coherent valid evidence, never `OTHER`/`UNKNOWN`, never a default for empty/duplicate/conflicting inputs.
4. For synthetic nonmedical duplicate, tie, invalid type, unknown schema, mismatched version, unsupported routing mode, wrong request/document/attempt context (if included), or oversized list: either return an explicit abstention/conflict or fail with a **closed typed, content-free** error as the situation warrants. Never silently choose the first/last/highest-confidence label; do not invent confidence or “safe” medical meaning. **No default document type.**
5. Deterministic outputs independent of caller ordering, with fixed canonical type ordering and explicit tie-breakers **only for output ordering**, not for overriding clinical ambiguity. No global state, time, random, network or filesystem access.

### B. Strict type and sensitivity boundary

- No free-text clinical observations or diagnosed terms in production contracts or tests; use `SYNTHETIC_*` nonmedical machine tokens. Any optional evidence/reference is a **non-dereferenceable** synthetic handle with strict syntax/length; never a patient ID, actual storage key, URL, bearer, clinical PDF or document OCR content.
- Do not copy P5 `VerificationState`, P8 extracted candidates, P9 safety states or P10 summary statuses into the classification outcome. No unconfirmed OCR output is elevated to source truth. No raw input value in `repr`, errors, formatted tracebacks, audit, logging, cache or job payload.
- Direct constructors and registry entry points must validate **actual runtime types** before hashing, `set`, sorting, regex, comparisons or mapping conversion (including unhashable/hostile inputs, bool-as-int, fake enums and subclass lookalikes). Use frozen dataclasses and immutable detached collections; reject shadow/duplicate metadata with closed failure codes.
- Versioning: explicit bounded schema/config/processor versions only. Unrecognized versions must fail closed or abstain; no auto-upgrade, provider activation or fallback to unrelated schema.

## 2. Explicit compile-time processor metadata registry — no execution

Implement a **pure, inert registry** of processor metadata. This is not a FastAPI module registry, plugin mechanism, execution graph, handler map, patient route or provider factory.

### A. Descriptor contract

Provide a frozen, validated `ProcessorDescriptor` (naming adaptable) with at least:

- stable bounded `processor_id` and `processor_version` (machine identifiers only);
- closed, nonempty, canonical tuple of accepted **one or more of the six** document categories (no `OTHER`, `UNKNOWN`); document type collision policies must be explicit;
- supported **synthetic processing modes/capabilities** referencing existing P11-B `ParserMode`, `OCRMode` and/or a small project-owned capability enum, never live engine capability claims;
- explicit bounded `input_schema_version` and `output_schema_version` / contract compatibility, with supported versions tied to actual existing P11-B contracts where appropriate (do not pretend that P11-D clinical candidate schemas have been implemented);
- finite canonical supported language/script hints only if defensible as **declared engineering metadata**, not evidence of actual Hindi/handwriting OCR capability;
- closed `MOCK_ONLY` or `NOOP_ABSTAIN` disposition and fixed `ENGINEERING_ONLY` authority; **no executable callable**, import path, handler, class instance, callback, provider object, arbitrary Python module, type-based dynamic dispatch, URL, model/version artifact or plugin discovery.

The six canonical future processor names from the plan are: `PrescriptionProcessor`, `LabReportProcessor`, `DischargeSummaryProcessor`, `DiagnosticReportProcessor`, `ImagingReportProcessor`, `ReferralLetterProcessor`. They may appear as **inactive metadata identities/descriptors only** in test fixtures or an explicitly invoked pure factory; they **must not** become working extractors. If an accurate contract requires deferring some descriptor/version, document deferral rather than inventing code.

### B. Registry construction and lookup

1. Require explicit caller-supplied immutable `tuple[ProcessorDescriptor, ...]`; never use entry points, reflection, importlib, dynamic modules, environment lookup, filesystem enumeration or side-effect registration. Define stable deterministic lookup by **exact `(processor_id, processor_version)`** and compatible **exact `DocumentType`** only; reject duplicates and ambiguous ownership (including multiple versions that could both activate for same type without an explicit **version-pinned** decision).
2. In a strictly synthetic **non-activated** context, an exact singleton category can select at most one matching inactive descriptor, otherwise return `UNAVAILABLE`/`AMBIGUOUS` or raise content-free typed error. No “best matching” fallback, unspecified latest version, downgrade, auto-choice, priority resolution, fuzzy classifier, runtime configuration or hidden implicit active selection. `UNKNOWN` and `OTHER` always abstain.
3. A registry may contain separately registered versions for comparison, but no selection by type without an **explicit pinned version/registry selection** satisfying uniqueness. Reject duplicate ID/version and conflicting chosen category/version in both caller orders. If registry `finalize`/`seal` is used, prove post-finalization mutation fails and that caller-owned input changes cannot affect it.
4. Registry metadata must not grant authorization, schema/medical validation, deployment permission, clinical status, document ownership or access to a source. Do not expose a `process()`, `.extract()`, `.parse()`, `execute()`, `dispatch()` or runtime handler that can actually access a file/provider. A processor title/name is never evidence a parser works.
5. Include a **deterministic mock/no-op decision** to indicate a synthetic route *would require* a parser or OCR mode; this is a classification/registry resolution **receipt** only, not execution. If consuming a P11-B typed request/result at all, merely validate references/declared contract compatibility without touching pages' text, converting it to a candidate or copying raw OCR output. Prefer avoiding coupling to result content entirely.
6. Preserve per-type provenance of the **declaration and exact requested version**, but never claim real model checksum, benchmark approval, supported clinical languages, or clinical document type accuracy.

## 3. Required focused tests (nonmedical and adversarial)

Write deterministic direct-constructor, registry and pure-decision tests, with synthetic tokens only:

1. Closed eight-type vocabulary; names of all six future processors represented as **inactive metadata**; `OTHER`/`UNKNOWN` abstain, no silent default/executable registration.
2. Empty, unsupported, wrong enum, malformed, unhashable, overflow, negative/bool numerical tokens, duplicate descriptor identity, wrong schema/mode, unexpected extra fields or forbidden authority fields are rejected with typed, content-free errors **before** Python `TypeError`/`AttributeError` escapes.
3. Exact eligible selection with pinned version succeeds as a **non-executing metadata receipt** only; unknown type, no matching processor, duplicate, simultaneous versions, cross-type collision and ambiguous inputs fail closed; registration and candidate input order must not alter outputs or ambiguity decisions.
4. Immutable snapshot/collections; mutation of caller-owned list/dict/source after construction cannot alter registry, decision, flags, or version. Direct construction cannot claim production, `APPROVED`, `CLINICIAN_CONFIRMED`, ``SIGNED`` or mock-activated functionality. Preserve no private input in `repr`, exceptions, tracebacks or telemetry; use privacy canaries.
5. Distinguish conflicting vs unknown classification and never resolve via alphabetic type order or numeric fake confidence. No OCR-text/file/mime/natural-language classifier, never infer medical type from `SYNTHETIC_*` text; missing/unavailable source causes abstention.
6. Versioned contract mismatch, incompatible declared parser/OCR mode, ambiguous registration, unknown processor/version, duplicate declaration/re-registration, and wrong declared category must not produce positive selection. Future P11-D schemas cannot be assumed to exist.
7. Document production package remains inert: no `public.py` registration, `app/main.py` import, API/BFF/frontend, storage I/O, real OCR provider/model, ORM/table/migration, generic worker binding, document upload/mutation/preview, dynamic runtime plugin loading. Inspect runtime OpenAPI/registry and import graph, not source-string scanning alone.
8. Existing P11-B port/mock/processing/benchmark tests remain unchanged and passing; P7 deterministic manual intake, P8/P9 stage restrictions and P10 safe summary domain remain unchanged. Validate zero provider selection, zero patient-data egress, zero clinical advice/routing/canonical fact mutation.
9. Metadata limits/identity guard tests should include both ordered insertion permutations, 0/1/many candidates, conflicting versions across the same category, copy/replace constructors where applicable, and absolute deterministic type/version/canonical-order checks.

**Traceability honesty:** Can provide **partial synthetic engineering evidence** toward `AC-P11-006`, `FR-DOC-010`, and `FR-DOC-023` (pure type and registry metadata); does **not** satisfy clinical document classification or a working parser registry for live workflows. `AC-P11-001..011` remain **NOT VERIFIED for live document use**. P11-A/D/E live capabilities and P11-B real providers remain blocked.

## 4. Narrow change allowlist and forbidden changes

Permissible only as actually necessary:

```text
backend/app/modules/documents/classification.py     # synthetic decisions / closed type vocabulary
backend/app/modules/documents/registry.py           # inert strict metadata registry; no runtime binding
backend/app/modules/documents/contracts.py          # narrowly required shared type extension, if justified
backend/tests/test_document_classification.py       # synthetic decision and hostile-input proof
backend/tests/test_document_processor_registry.py   # immutable explicit registry/adversarial proof
backend/tests/test_document_classification_boundaries.py  # optional nonactivation proof
backend/tests/ocr_support/**                     # optional synthetic-only fixture reuse, no changes to mock semantics

docs/03_REPOSITORY_STRUCTURE.md                 # update actual file inventory, not live claims
docs/implementation/38_PROGRESS_TRACKER.md      # add P11-C narrow status/evidence; correct stale P10-A/P11-B headers
docs/implementation/P11_READINESS_GATE_REVIEW.md  # OPTIONAL concise dated P11-B/C engineering snapshot; do not change approval counts
docs/codex/CODEX_PHASE_PROMPTS/P11_C_SYNTHETIC_DOCUMENT_CLASSIFICATION_AND_PROCESSOR_REGISTRY.md
```

Do not change existing P11-B port/result contract semantics merely to make a registry easier. Any incompatibility: report, isolate and seek independent decision rather than broad rewrite.

**Forbidden:** new `app/main.py` or `public.py` activation, FastAPI route/Next BFF/UI, upload/camera/source viewer, object-storage file read/write, worker scheduling or backend job handler, database model/migration/outbox, live P11-A storage, real classifier, medical keyword heuristics, model/LLM calls, OCR/provider adapters, P11-D candidate/clinical extraction, P11-E review/timeline, patient/clinician access, P5 fact creation or overwrite, P7 intake change, P8/P9/P10 activation, training datasets, downloaded artifacts, dependencies/lockfiles, CI/Docker/infra, feature toggles to turn on documents, external egress, new clinical policy or approval assertions.

No import of production P11 registry into the application composition root. No new operational capabilities in staging/pilot/production or hidden test fallbacks in live code.

## 5. Quality gates, documentation updates, exact-head PR handoff

1. Record exact starting base, plan, and scope/allowlist evidence. Run `git diff --check` and a path-by-path architecture/privacy/clinical label audit; ensure all outputs remain machine tokens and all negative errors content-free.
2. Run focused new P11-C tests, all P11-B focused tests and existing P7/P8/P9/P10 regression suites. Full backend `pytest` excluding gated DB tests (record skip count); Ruff format/lint, strict mypy, Python compile/import checks; report numbers, not estimates.
3. Run real PostgreSQL integration pytest suite and Alembic upgrade/current/check/downgrade recovery. Head must remain `p7a_0007`. Run full frontend format/lint/typecheck/tests and **all three** production builds, Docker compose/build/migration/non-root/liveness/readiness, Playwright Chromium (disclose retry/flaky results), Gitleaks, Trivy filesystem and backend image security scans. Do not disable/update skip/xfail or CI security thresholds to make tests green.
4. Update the progress tracker accurately: P10-A PR #30 and P11-B PR #32 are **MERGED**, with P11-B engineering-only subset accepted; `P11` macro **PARTIAL**. P11-C is **implemented pending independent review** on the feature branch, then only mark safe subset accepted after reviewer/merge. Record P11 live matrix unchanged (**0 APPROVED / 5 OPEN / 4 BLOCKED**) and P10 live 0/9, P8/P9 Stage 3 blocked. The previous readiness snapshot predates P11-B and must not falsely describe `documents` as `.gitkeep`-only *today*; a dated footnote is acceptable but not a fabricated approval. All P11 criteria remain incomplete for live use.
5. Push `phase/p11-c-synthetic-document-registry`, create **one** PR into exact main base. Independently query GitHub: verify PR head equals final local/remote SHA; six required jobs on exact head all **SUCCESS** — `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, and `Security scans`. Any new commit, even docs-only, requires CI on the *new* SHA. If base drift, failed jobs or unrelated changes, stop and report.
6. **DO NOT MERGE**. Never automatically begin P11-A/D/E, real P11-B OCR provider work, or P12. Return evidence and wait for independent review.

### Exact completion report

```text
STATUS: COMPLETE SAFE ENGINEERING SUBSET / PARTIAL / BLOCKED
BRANCH: phase/p11-c-synthetic-document-registry
BASE MAIN SHA: a8dea0b374017793f119a85daa971b8256881ab4
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
DOCUMENT TYPE AND SYNTHETIC CLASSIFICATION DECISIONS:
PROCESSOR DESCRIPTORS / VERSION-PINNED REGISTRY:
UNKNOWN/OTHER/AMBIGUITY/NO-EXECUTION EVIDENCE:
DIRECT CONSTRUCTOR / PRIVACY / DETERMINISM TESTS:
P11-B COMPATIBILITY / ZERO RUNTIME REGISTRATION:
FOCUSED P11-C / P11-B / FULL BACKEND / REAL POSTGRESQL / FRONTEND / PLAYWRIGHT COUNTS:
CI RUN ID / EXACT HEAD SHA / ALL SIX JOB CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCY / LOCKFILE / CHANGED PATHS:
FR-DOC-010/023 AND AC-P11-006 PARTIAL ENGINEERING EVIDENCE VS LIVE ACCEPTANCE:
P11 LIVE APPROVAL GATES (0/9, 5 OPEN, 4 BLOCKED):
P8-C / P9-C / P10 GOVERNANCE:
UNRELATED CHANGES:
MERGED: NO
```

**STOP after reporting.** This is a source/CI-reviewable synthetic registry, not a release authorization, model/medical classifier, active processor, or working patient/clinician document pipeline.
