# SwasthyaSetu AI — P11-B: Parser/OCR Ports, Deterministic Mock & Synthetic Processing Contracts

**Work unit:** P11-B, **SAFE ENGINEERING SUBSET ONLY** — inert provider-neutral interfaces, bounded synthetic/OCR-shaped values, deterministic mock, offline processing-attempt/job contracts and synthetic benchmark smoke harness. **This is not P11-B clinical/OCR-provider completion or live document processing.**

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified baseline:** `main @ 449cd917f8a79baf30b7a90fc04cd32d131fb318`
**Pre-P11 PR:** #31, **MERGED** at the baseline above; reviewed PR head `37302a9b419ff49a6f673521b48808e8b92815e3` has the same tree.
**Proposed branch:** `phase/p11-b-synthetic-ocr-ports-mock`
**Canonical spec:** `docs/15_DOCUMENT_AI_OCR_SPEC.md`, especially §§1–8, 10–14.
**Readiness:** `docs/implementation/P11_READINESS_GATE_REVIEW.md`: **0/9 approved for live use, 5 OPEN, 4 BLOCKED**.
**Alembic head:** `p7a_0007` — **must remain unchanged**.
**Delivery:** Branch → push → PR against `main` → exact-head six-job CI → **DO NOT MERGE**. Wait for independent review.

> **Non-negotiable safety boundary:** There is no authorized live document upload, lawful real-file processing flow, malware-scan/quarantine policy, patient/clinician source access, production OCR adapter, provider selection, model download, medical extraction, candidate promotion, or patient/clinician UI. P8-C and P9-C Stage 3 remain BLOCKED; P10 live clinician approval remains 0/9. This work implements **no real medical OCR** and processes **only synthetic nonmedical data provided directly to tests**. Technical success is not clinical/privacy/security/production approval.

## 0. Preflight: audit exact baseline and STOP on drift

1. Confirm `git status --short` clean, local `main`, `origin/main` and remote `main` all equal `449cd917f8a79baf30b7a90fc04cd32d131fb318`. Verify PR #31 is merged at this commit. Do not reset/discard other work. STOP and report if baseline, approvals or repository implementation changed materially.
2. Read the repository governance: `docs/codex/CODEX_INSTRUCTIONS.md`, `CODEX_WORKFLOW.md`, `CODEX_CONTEXT_RULES.md`, `docs/00_PROJECT_MASTER_SPEC.md`, `docs/02_SYSTEM_ARCHITECTURE.md`, `docs/03_REPOSITORY_STRUCTURE.md`, `docs/04_DOMAIN_MODEL.md` §§33–36, `docs/05_DATABASE_SCHEMA.md` §15 **(conceptual only)**, `docs/06_API_CONTRACTS.md` §§17–18 **(conceptual only)**, `docs/01_PRODUCT_REQUIREMENTS.md` FR-DOC-001..023 and FR-PROV-001..007, `docs/29_ENGINEERING_STANDARDS.md`, `docs/30_TESTING_STRATEGY.md`, `docs/33_ERROR_HANDLING_POLICY.md`, `docs/34_MASTER_IMPLEMENTATION_PLAN.md` §19, `docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md` AC-P11-001..011, `docs/implementation/36_DEPENDENCY_MAP.md`, `docs/implementation/37_DECISION_LOG.md`, `docs/implementation/38_PROGRESS_TRACKER.md`.
3. Read `docs/15_DOCUMENT_AI_OCR_SPEC.md`, `docs/implementation/P11_READINESS_GATE_REVIEW.md`, `docs/26_PRIVACY_CONSENT_SPEC.md`, `docs/12_CLINICAL_PROVENANCE_SPEC.md`, `docs/24_CLINICIAN_DASHBOARD_SPEC.md`, `docs/implementation/P8_C_INTEGRATION_GATE_REVIEW.md`, `docs/implementation/P9_C_SAFETY_PRESENTATION_GATE_REVIEW.md`, `docs/implementation/P10_READINESS_GATE_REVIEW.md`, `docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md` §12, `docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md` §14, `docs/research/ocr/{OCR_TECHNOLOGY_EVALUATION,OCR_BENCHMARK_PLAN,OCR_ADAPTER_CONTRACT_DRAFT}.md`.
4. Inspect actual code, not imagined locations: `backend/app/modules/documents/` is currently `.gitkeep` only; inspect `backend/app/jobs/{contracts,in_process,worker}.py`; `backend/app/shared/storage/{port,types}.py`; `backend/app/adapters/storage/local.py`; `backend/app/events/{envelope,outbox}.py`; relevant P8 provider port/mock and P10 synthetic domains; `backend/app/main.py`, `backend/tests/`, CI workflows, Python dependency policy/locks. Generic process-local jobs and local object storage are existing engineering primitives, **not** a document processing pipeline. P10 summary domain is inert; P11 must not activate it.
5. Record a compact before-code audit, intended file list and dependencies. If any item requires a previously unapproved upload/storage/provider/real-records decision, **exclude it and record its gate**. No broad “helpful” integration. Create branch only after preflight.

## 1. Exact objective and strict architectural scope

Implement a standalone **pure documents engineering package**, optionally organized as:

```text
backend/app/modules/documents/__init__.py               # inert; no import/registration side effects
backend/app/modules/documents/contracts.py              # frozen strictly validated source/request/result types
backend/app/modules/documents/ports.py                  # provider-neutral DocumentParserPort and OCRPort
backend/app/modules/documents/processing.py             # pure attempt/job-intent values and guards, if justified
backend/tests/test_document_ocr_contracts.py
backend/tests/test_document_ocr_mock.py
backend/tests/test_document_processing_contracts.py
backend/tests/test_document_ocr_benchmark.py
backend/tests/test_document_ocr_boundaries.py
backend/tests/ocr_support/                              # test-only mock + in-memory benchmark helpers, if useful
```

Follow actual project conventions and use fewer files when sensible. Do **not** create an `application.py`, `public.py` capability manifest, ORM model, API router, runtime worker handler, source downloader or document storage client in this phase. **MockOCRAdapter must remain in test-only support and must not become a selectable runtime provider**. If a shared protocol type must live in `documents`, importing that type may not start a provider, worker or operation.

### A. Distinct, provider-neutral ports

- Create explicit typed `DocumentParserPort` for **born-digital/native content** and `OCRPort` for **raster/scanned pages**. Use `typing.Protocol` (async functions where consistent with other ports) and immutable contract types; do not bind either port to PaddleOCR/Docling/Tesseract/HTTP or generic AI providers.
- Requests are versioned and bounded and contain only **synthetic** `request_id`, `document_id`, `processing_attempt_id`, a **non-dereferenceable synthetic object/source reference**, requested page range, allowlisted processing mode, language/script hints, adapter/routing contract versions, caller-supplied UTC deadline, bounded resource profile and safe correlation metadata if needed. Use project `OpaqueId` where appropriate. Do not include patient name, patient ID, real clinical identifier, session/actor bearer, arbitrary URL/path, raw file bytes or object-storage credentials.
- Source reference and versions are **linkage only**, never identity, consent, storage read authority, a security scan or real-world provenance. The port does not authorize itself; the future P11-A/application boundary must do this before live use.
- Validate directly in constructors **and** any conversion boundary, not only in a high-level builder. Reject malformed IDs, mixed document/attempt identity, unsupported mode, unknown version, empty/duplicate page requests, invalid hints, unbounded collections and naive/future-invalid deadline semantics as appropriate. Stable typed **content-free** failure codes; no input values/identifiers in errors.

### B. Strict OCR/native-parser result values

- Define a finite versioned result schema suitable for both ports, with closed processing statuses **`SUCCEEDED`, `PARTIAL`, `FAILED`, `NEEDS_FALLBACK`** as appropriate to spec 15 §5 (not document lifecycle or clinical verification states).
- Include stable request/document/attempt linkage; page-level coverage and explicit per-page success/failure; bounded reading-order text blocks, typed block IDs/kinds, optional table/row/column/cell structure and geometries, language/script descriptors, confidence with explicit **UNKNOWN/unavailable** semantics, provenance for mock provider/adapter/version and routing config, closed warning/error codes, and bounded nonnegative elapsed/resource metadata. Avoid unnecessary speculative fields.
- Use immutable tuples/frozen dataclasses for nested values; enforce **total and per-page/per-table caps**, unique identity, deterministic ordering and no dangling cross-page block/table-cell references. Page numbers start at 1, requested page coverage must reconcile with returned success/partial/failure states, and out-of-range pages/coordinates must fail closed. If supporting normalized boxes or polygons, require finite values and ordered bounds within `[0,1]`; reject NaN/Inf, negative size, invalid rotations, invalid confidence kind/value and malformed table spans.
- `SUCCEEDED` must not silently omit requested pages; missing/failed pages must yield explicit `PARTIAL`, `FAILED` or a bounded fallback state. Failed results must not carry a deceptively successful clinical/text payload. No implicit unit/label inference, hallucinated text, medical flags or confidence synthesis.
- Restrict this work's recognized text to deliberately nonmedical bounded **`SYNTHETIC_*` machine tokens** in the test mocks/fixtures. Do not add real prescriptions, medical terminology, patient data, image samples, raw pages, external corpora or model outputs. Hide potentially sensitive source or recognized text from `repr`, exception and telemetry surfaces; limit serialization strictly.
- Record that output evidence is **not** a `ClinicalFact`, P8 accepted candidate, P9 safety decision, P10 clinical summary, document status, clinician confirmation or signed note.

### C. Deterministic mock — strictly test-only

- Implement `MockOCRAdapter` in `backend/tests` support (or equivalently isolated test-only path) against `OCRPort`. Optionally add a minimal `MockDocumentParserAdapter` only if necessary to contract-test the separate parser port; never fetch or parse a file.
- Use exact versioned **in-memory** request-to-result fixture mapping with caller-supplied stable identifiers, synthetic labels and time. Same input/config/order must reproduce identical output. Input insertion order must not create nondeterministic page or block order.
- Make deterministic scenarios for success, explicit missing page/partial, mock timeout/deadline exceeded, refusal, unsupported or unavailable engine, fallback required, malformed provider result and raised exception. No sleeps, network, filesystem, subprocess, model import/download, environment credential inspection or object-store access.
- Ensure mock selection is **impossible through FastAPI, production module registry, app configuration or patient/clinician UI**. Static/import-graph tests should prove no production `app/` module imports the test-only adapter and no mock adapter is installed as a runtime fallback. `TEST`-named fixtures are not permission grants.
- Keep injected failure exceptions content-free and not wrapped into a success result. Check exceptions/traces/logs for a privacy canary.

### D. Offline processing attempt and job-intent contracts ONLY

- Introduce the smallest useful **pure values** for document processing attempt identity, source/routing version, generation, stage, status, idempotency reference, UTC start/deadline, and closed failure/retry classification. Preserve distinctions between `UPLOADED/VALIDATING/ACCEPTED/...` document lifecycle (P11-A, **not implemented**) and generic P3 `JobStatus`.
- Model allowable phase-local synthetic request/attempt transitions and rejection of stale/mismatched generations, terminal attempt replay, duplicate IDs, overflow/backoff budgets and cross-document/attempt result mixups. Changes must be immutable, deterministic and data-free. **Do not invent a permanent production retry policy, TTL, idempotency store, patient authorization or live approval.** Define limits as engineering input caps, not approved clinical/operational limits.
- Inspect and **reuse/compose** existing `JobRequest`, `JobType`, `JobDispatcher` and `InProcessWorker` contracts where appropriate for test-only evidence. Any test-only in-process dispatch must require an explicit test invocation. Existing process-local queues remain **volatile**, not crash-recovering/durable. Do not add worker daemon, cron, background scheduler, storage ingestion, DB/outbox writes or runtime handler binding.
- Keep job payloads **content-free metadata** only: no source text, OCR blocks, object key, signed URL, patient identifier, clinical data or credentials. No automatic retry after an ambiguous side-effect. Future P11-A/P11-B production orchestration and cancellation rules stay gate-bound.

### E. Benchmark smoke harness — no provider comparison or clinical accuracy claim

- Create a small **in-memory, deterministic benchmark contract/harness** under test-only support. Consume only synthetic fixture expected output and supplied typed mock results. Prefer source/page/block identity, page coverage, exact synthetic token retention, failure transparency and reproducibility checks; if calculating numerical rates, define denominators/undefined states explicitly and never round to a fabricated threshold.
- Benchmark fixture records identify **synthetic origin**, fixture version, expected source/page layout and test configuration. If a future external dataset manifest is modeled, distinguish its required license/provenance fields but **do not download/read actual datasets or commit real/de-identified patient records** in this branch.
- Do not select/rank a production OCR engine, hard-code medical accuracy cutoffs, claim supported languages/handwriting clinically reliable, install PaddleOCR/Docling/Surya/docTR/Tesseract/RapidOCR or report benchmark success for those engines. The repository benchmark plan and R3 approval/benchmark gates remain open.
- Tests must show order-independent metrics, explicit missing-page/error accounting, and refusal of ambiguous or unsupported versions/fixtures.

## 2. Adversarial regression and non-activation evidence

Add focused **synthetic-only** tests for these independently reviewable invariants:

1. Both `DocumentParserPort` and `OCRPort` contract tests, strict request/result version and identity binding, separate native vs raster modes, injected deterministic IDs/UTC times, no implicit now/randomness in outputs.
2. Immutable nested values and direct constructors; unbounded/duplicate pages, blocks, cells, table spans, wrong kinds, incorrect page linkage, oversize text, invalid normalized coordinates, NaN/Inf/negative confidences, invalid status/error combinations and invalid timezones fail with **typed content-free** errors.
3. Success with exactly all requested pages, partial or failed pages explicitly accounted for, failed output cannot masquerade as `SUCCEEDED`; undefined confidence is not zero or a false measured score.
4. Deterministic test-only mock success, partial, timeout, refusal, unavailable, fallback, wrong-version or forged response; does not retain mutable inputs or leak textual canaries in `repr`, exceptions, formatted traceback, logs or metrics.
5. Job/attempt intent uniqueness, scope/generation binding, retry/idempotency/replay guards, terminal-state and stale response rejection. Existing process-local P3 worker is only manually run in unit tests, if used.
6. Pure synthetic benchmark golden cases including expected outputs, order independence, missing items and explicit metric denominators. No engine winner or clinical pass claims.
7. Architecture: no document imports in `backend/app/main.py`/existing runtime public registry, no `/api/v1/documents` or clinician source route, no patient document page change, no P5/P7/AI/safety/summaries mutation, no OCR/provider import or dependency, no new `clinical_documents`/processing/extraction ORM/table/migration, no content egress, no persistence or new production worker. Import `documents` should be inert.
8. Negative tests for misleading authority tokens/fields (`CLINICIAN_CONFIRMED`, `APPROVED`, `MEDICALLY_CLEARED`, treatment/triage or safety keys); OCR text is evidence only, never clinician-confirmed or patient guidance.
9. Existing P7 intake and manual fallback, P8-C/P9-C restricted behavior and P10 summary/test isolation must continue to pass. Avoid brittle superficial source scanning as sole proof; verify actual runtime registry/routes and source dependency graph in addition to file content.

**Acceptance honesty:** This subset can supply **partial engineering evidence** toward `AC-P11-004` and `AC-P11-005` and the offline-processing mechanics of `AC-P11-003/009`, but **no P11 acceptance criterion is fully satisfied for a real document workflow**. P11 macro is **PARTIAL / IN PROGRESS only upon independent acceptance**. The other AC-P11-001..011 remain not implemented/not accepted for live uses. Do not claim P11-B fully complete or clinical OCR supported.

## 3. Scope lock / allowed changes

Expected changed paths only (narrow refinements within these directories):

```text
backend/app/modules/documents/{__init__,contracts,ports,processing}.py
backend/app/modules/documents/.gitkeep                     # remove placeholder if needed
backend/tests/test_document_ocr_*.py
backend/tests/test_document_processing_*.py
backend/tests/ocr_support/**                               # test-only mock/harness, if needed

docs/03_REPOSITORY_STRUCTURE.md                           # actual inventory, no live claims
docs/implementation/38_PROGRESS_TRACKER.md                # update stale P10-A header; P11 safe subset status
docs/implementation/P11_READINESS_GATE_REVIEW.md          # optional precise engineering-evidence footnote only
docs/codex/CODEX_PHASE_PROMPTS/P11_B_OCR_PORTS_DETERMINISTIC_MOCK_AND_SYNTHETIC_PROCESSING_CONTRACTS.md
```

**Explicitly forbidden:** P11-A secure upload implementation/API, object storage usage, signed upload/download, scanner or quarantine vendor, new database migrations/tables, document association to actual patients, P11-C classifier/processor registry, P11-D medical entity extraction/candidate fact persistence, P11-E frontend/clinician source viewer, any production OCR adapter, `app/main.py` or runtime capability registration, changed clinical policy, new artifact/dataset, network/service/provider/model calls, `P8-C`/`P9-C` Stage 3 changes, `P10-B/C/D` live flows, dependencies/lockfiles, CI security relaxation, Docker/infra changes. No other application module changes unless an independently reportable unavoidable incompatibility is found; STOP rather than expand silently.

## 4. Quality gates and independent PR handoff

1. Record preflight/audit, implement only the scoped files and run `git diff --check` plus changed-path allowlist and secret/source/PHI/clinical text audit.
2. Run focused `document` contract/mock/processing/harness/boundary tests and all existing P7/P8/P9/P10 regression tests. Run full backend Ruff format/lint, **strict mypy**, Python compile/import and network-free pytest (report database skips accurately).
3. Run the **real PostgreSQL integration** suite, Alembic upgrade/current/check and downgrade/recovery with unchanged `p7a_0007`; 3 frontend build targets + tests/lint/typecheck/format; Docker/PostgreSQL non-root/readiness; Playwright Chromium (disclose retries/timing); source secret and filesystem/image vulnerability scans.
4. Push `phase/p11-b-synthetic-ocr-ports-mock` and open PR against **unchanged main**. Verify **all six required GitHub Actions jobs at the exact final remote SHA**, not a prior commit: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. If red/inconclusive/new head, **do not request approval**.
5. Do **not merge, start P11-A/C/D/E or claim any live approval**. Return for independent review with precise implementation summary, test counts, CI run ID, final local/remote SHA, commit scope, unchanged Alembic/dependencies, remaining 0/9 P11 gates and P8/P9/P10 blockers.

### Required response format

```text
STATUS: COMPLETE SAFE ENGINEERING SUBSET / PARTIAL / BLOCKED
BRANCH: phase/p11-b-synthetic-ocr-ports-mock
BASE MAIN SHA: 449cd917f8a79baf30b7a90fc04cd32d131fb318
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
PARSER PORT / OCR PORT CONTRACTS:
DETERMINISTIC TEST-ONLY MOCK AND NEGATIVE CASES:
SYNTHETIC PROCESSING/JOB-INTENT CONTRACT:
SYNTHETIC BENCHMARK HARNESS / NO PROVIDER SELECTION:
ARCHITECTURE ISOLATION / NO LIVE FILES OR APIS:
FOCUSED / FULL BACKEND / POSTGRESQL / FRONTEND / PLAYWRIGHT TEST COUNTS:
CI RUN ID / SIX JOB CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCIES:
FR/AC-P11 ENGINEERING EVIDENCE VS LIVE GATES:
P8-C / P9-C / P10 GOVERNANCE:
CHANGED PATHS / UNRELATED CHANGES:
MERGED: NO
```

**Stop after this report and await independent source/CI review.**
