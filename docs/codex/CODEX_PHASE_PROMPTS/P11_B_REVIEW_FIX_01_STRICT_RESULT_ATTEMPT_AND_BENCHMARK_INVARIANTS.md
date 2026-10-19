# SwasthyaSetu AI — P11-B Review Fix 01: Result, Attempt, and Test-Only Benchmark Invariants

**Decision:** REVIEW FIX REQUIRED. Continue work on existing **PR #32**. **DO NOT MERGE** until independent re-review.

- **Repository:** `Itsbhavesh1101/swasthyasetu_ai`
- **Branch:** `phase/p11-b-synthetic-ocr-ports-mock`
- **Reviewed final head:** `5f78a1f96ca891a6b58566cced3aaefa79fe1ebe`
- **Base `main`:** `449cd917f8a79baf30b7a90fc04cd32d131fb318`
- **Reviewed CI run:** `39328910133` — six required GitHub Actions jobs SUCCESS at the reviewed head.
- **Alembic head:** `p7a_0007` — must not change.
- **Governance:** P11 approval matrix remains **0/9 approved (5 OPEN, 4 BLOCKED)**. P8-C/P9-C Stage 3 and P10 live clinician/source access remain blocked. No production OCR, medical processing, patient upload, clinician UI or clinical authority is granted.

## Why a repair is required

The implementation correctly provides an inert synthetic-only OCR domain and CI-clean mock tests. However, reviewing the **actual final-head constructors** revealed state and input-integrity gaps not exercised by the current focused suite. These are not deployment findings; they are **merge-blocking for the claimed strictly validated, content-free synthetic contracts**.

### Finding 1 — Untrusted result/page error codes can bypass closed enums and leak arbitrary content

**Files:** `backend/app/modules/documents/contracts.py` — `PageResult.__post_init__`, `DocumentProcessingResult.__post_init__`, and related strict input validation.

**Observed:** A `PageResult` with `status=FAILED` merely checks that `error_code` is non-`None`; it does **not** check `isinstance(error_code, ResultErrorCode)`. Similarly, `DocumentProcessingResult(status=FAILED or PARTIAL)` only requires a non-`None` `error_code`, not the closed enum. Thus arbitrary string content can be stored in an object represented/logged with default dataclass `repr`, contradicting typed content-free failure design. Independent type boundaries also need tightening: `LanguageDescriptor` calls `_HINT.fullmatch` before checking that language and script are `str`; `PageResult.rotation_degrees` accepts numerically equal non-integers (e.g. `0.0` or `False`) due to tuple-membership equality; malformed unhashable language/script hint elements can raise raw `TypeError` during `set(...)` before the intended typed validation.

**Required:**
1. Enforce `error_code is None or isinstance(error_code, ResultErrorCode)` at **both** page and top-level result constructor boundaries, with existing status-specific presence/absence rules; reject raw strings, booleans, unknown enums, and objects with only `DocumentContractError`/closed codes, never reflected input values.
2. For language/script descriptors, perform strict `str` checks **before regex calls**; for request hints, validate element types/regex **before** duplicate detection so unhashable hostile inputs fail closed rather than escape as raw exception.
3. Require `type(rotation_degrees) is int` before membership in `(0,90,180,270)`, rejecting bool/float lookalikes. Preserve typed bounded geometry and UTC semantics.
4. Add direct-constructor regressions creating a failed page and failed/partial result with a private-canary `error_code`; assert content-free `DocumentContractError`, and absence of canary in formatted traceback/exception. Include malformed hint types and nonstring `LanguageDescriptor` fields, and invalid rotation types. Do **not** blanket-swallow unrelated exceptions or weaken tests.

### Finding 2 — Direct `ProcessingAttempt` construction accepts contradictory status/retry classifications

**File:** `backend/app/modules/documents/processing.py` — `ProcessingAttempt.__post_init__` and generation guards.

**Observed:** For **all** statuses other than QUEUED/RUNNING/SUCCEEDED, constructor applies one generic rule: stage COMPLETED, timestamps present, any non-`None` failure code and any retry classification except NONE. This permits e.g. `status=FAILED` + `retry_classification=NEEDS_REVIEW`, `status=NEEDS_REVIEW` + `retry_classification=TERMINAL`, and potentially an arbitrary `CANCELLED` state with a retryable failure. The `fail()` factory produces coherent combinations, but a direct frozen constructor can forge incoherent ones. Also, `_check(generation)` uses Python equality (where `True == 1`), so booleans can masquerade as generation 1.

**Required:**
1. At the frozen constructor, enforce exact status ↔ retry classification invariants: `NEEDS_REVIEW` iff `RetryClassification.NEEDS_REVIEW` for a completed failed/review attempt; `FAILED` requires `RETRYABLE` or `TERMINAL`; QUEUED/RUNNING/SUCCEEDED retain their existing specific constraints. Define a conservative explicit `CANCELLED` rule if it must be directly constructible; otherwise reject unsupported CANCELLED construction in this subset. Do not introduce live cancellation orchestration.
2. Validate that non-`None` `failure_code` is an actual `AttemptFailureCode`, not a user-supplied string, and keep its representation/error handling content-free (for example, `repr=False` on potentially sensitive strings/identities when useful). Preserve all existing time and ID invariants.
3. Require `type(generation) is int` on public transition generation arguments (`start`, `succeed`, `fail`) to prevent bool/float equivalence; avoid making a `bool` a valid generation.
4. Add **direct-constructor** negative tests for the contradictory combinations, forged failure-code string and boolean generation; retain positive lifecycle, retry, stale, deadline and replay tests unchanged.

### Finding 3 — Page/table reference and bounded-grid invariants need direct validation

**File:** `backend/app/modules/documents/contracts.py` — `PageResult`, `TableResult`, `TableCell`.

**Observed:** `PageResult` does not reject duplicate `table_id` values among its tables. It only requires each cell's `block_id` to be present in the page blocks, without confirming that the target block is a `TABLE_CELL` block. `TableCell` enforces only nonnegative row/column and positive spans; arbitrarily large indices/spans pass despite the claimed bounded table geometry. Two tables with the same ID and a cell pointing at a general text block make source evidence ambiguous.

**Required:**
1. Reject duplicate table IDs **within one page**, and reject an ambiguous/dangling cell-to-block linkage, with a clear closed typed code. If a table cell must reference a `TextBlock`, require a compatible `TABLE_CELL` kind (unless an existing canonical spec explicitly documents another mapping; cite any exception).
2. Bound row/column indices and spans to a defensible engineering cap consistent with `MAX_CELLS_PER_TABLE`; avoid false claims that these provisional engineering limits are approved medical-page/resource limits. If explicitly chosen limits would break legitimate sparse table semantics, document the alternate bounded coordinate rule and test it.
3. Add tests for duplicate tables, wrong block kind, oversized indices and overflowing spans, while retaining valid ordered tables/cells and zero-I/O mock behavior.

### Finding 4 — Test-only benchmark fixture constructor is not bounded/typed fail-closed

**File:** `backend/tests/ocr_support/benchmark.py`.

**Observed:** `SyntheticBenchmarkFixture` invokes regex on unchecked values and unpacks/iterates unvalidated fields, so malformed primitives can escape as `TypeError`/`AttributeError`. It also places no count/length caps on `expected_pages`, tokens-per-page or token lengths; a very large or malformed test fixture can consume arbitrary memory/time, inconsistent with the work unit's bounded synthetic benchmark contract. The benchmark must remain test-only; do not add a real dataset runner.

**Required:**
1. Validate all fixture scalar/tuple/nested-tuple types, canonical sorted unique page IDs, bounded page/token counts, exact `SYNTHETIC_*` bounded token syntax, and the expected page ↔ tokens association **before** regex, hashing, iteration and set operations. Reuse appropriate existing maxima where sensible.
2. Reject malformed fixture types, oversize/duplicate/unbounded tokens and out-of-range pages with only a fixed content-free `BenchmarkContractError`; no raw exception or canary echo. Preserve meaningful **explicit page/token denominators**, failed-page accounting, deterministic order-independent hashes, and no pass/selection threshold.
3. Add adversarial test cases; do not add provider evaluation, file reads, actual OCR, downloads or real/document text.

## Scope and preflight

First verify `main` and PR #32 base/head are still the exact values above, worktree is clean, previous six jobs passed and readiness gates remain unchanged. Read the tracked P11-B phase prompt, `docs/15_DOCUMENT_AI_OCR_SPEC.md`, `docs/implementation/P11_READINESS_GATE_REVIEW.md`, and the actual current code/tests. **STOP on base/head drift and report**, never discard unrelated work.

Allowed paths for the narrow repair:

```text
backend/app/modules/documents/contracts.py
backend/app/modules/documents/processing.py
backend/tests/test_document_ocr_contracts.py
backend/tests/test_document_processing_contracts.py
backend/tests/test_document_ocr_benchmark.py
backend/tests/test_document_ocr_boundaries.py          # only if needed
backend/tests/ocr_support/benchmark.py
backend/tests/ocr_support/fixtures.py                  # only if needed
backend/tests/ocr_support/mock_ocr.py                  # only if needed

docs/codex/CODEX_PHASE_PROMPTS/P11_B_REVIEW_FIX_01_STRICT_RESULT_ATTEMPT_AND_BENCHMARK_INVARIANTS.md
```

**Forbidden:** P11-A upload/storage/DB/schema/migration, any live file/patient record access, P11-C/D/E classifier/extraction/UI, live OCR provider/model/dependency, OCR source URL, actual scans, LLM/AI, network/filesystem egress, production runtime binding or background worker, clinician confirmation, P8/P9/P10 stage activation, weakened CI/strict tests or new clinical approval claims. Keep `p7a_0007`, lockfiles and dependency manifests unchanged. Do not extend beyond the four findings for opportunistic refactoring.

## Verification and handoff

1. Implement the smallest direct-constructor safeguards and targeted regression tests, without breaking the inert synthetic-only architecture. Test content-free formatted exceptions and stable reproducibility.
2. Run focused P11-B tests; full network-free backend (record PostgreSQL skips); real PostgreSQL suite and Alembic upgrade/current/check/downgrade recovery; P7/P8/P9/P10 regressions; Ruff format/lint and strict mypy; frontend tests/three builds; Playwright Chromium (disclose retries/flakiness); Docker/PostgreSQL non-root/readiness; Gitleaks/Trivy; `git diff --check`, scope/privacy/import/route/egress audits.
3. Push **same** `phase/p11-b-synthetic-ocr-ports-mock` branch and update **existing PR #32**. Verify all six CI jobs are **SUCCESS on new exact final head**: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`.
4. **DO NOT MERGE**. Return new local/remote SHA, PR URL, CI run ID and six exact job outcomes, focused/full/integration/frontend/Playwright counts, outcomes for all four findings, Alembic/dependency invariants, and outstanding P11 **0/9 approvals (5 OPEN, 4 BLOCKED)** and P8/P9/P10 gates. Wait for independent re-review.

**End state:** Reviewable engineering-only repair, not live OCR or clinical approval.
