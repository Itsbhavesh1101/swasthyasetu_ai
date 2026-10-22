# SwasthyaSetu AI — P11-D: Detached Synthetic Evidence and UNCONFIRMED Candidate Contracts

**Work unit:** P11-D **SAFE ENGINEERING SUBSET ONLY** — isolated structural/provenance contracts and adversarial tests. **Not** medical entity extraction, patient data handling, clinical validation, clinician review, persistence, or production capability.

- **Repository:** `Itsbhavesh1101/swasthyasetu_ai`
- **Verified starting `main`:** `87f87e0a454db86bcdf67569fa1e6ab2061ee46c`
- **PR #34:** independently reviewed P11-A safe engineering head `89f304b9ff98e08fb4a45c72177b9fbedbfd5cf8`, merged at the starting `main` SHA with no tree differences.
- **Proposed branch:** `phase/p11-d-synthetic-candidate-evidence-contracts`
- **Alembic head:** `p7a_0007`; keep unchanged.
- **Governance:** P11 live gate matrix **0/9 APPROVED — 5 OPEN, 4 BLOCKED**. P10 live clinician access **0/9**. P8-C/P9-C Stage 3 still blocked. The canonical P11-D *medical extraction* phase is **BLOCKED** by readiness gates 1, 3, 5, 7, and 9. This prompt deliberately excludes it.
- **Delivery discipline:** a single isolated clean feature branch and PR; six exact-head CI jobs green; **DO NOT MERGE**. Stop for independent review.

> **Scope authorization:** This document proposes ONLY a separately bounded, nonmedical **synthetic contract-only** subset contemplated by `docs/implementation/P11_READINESS_GATE_REVIEW.md` §4. It **does not grant or imply human clinical/privacy/security approval**. If implementation of any item needs actual medical field semantics, source access, patient consent/identity, a real OCR/LLM/provider or schema/retention approval, **STOP that item** and report the blocker. Do not silently invent governance decisions.

## 0. Mandatory preflight, source-of-truth inspection, and stop conditions

1. Use a clean isolated Git worktree; preserve the user's unrelated primary-worktree changes. Confirm local `main`, `origin/main`, GitHub `main` exactly `87f87e0a454db86bcdf67569fa1e6ab2061ee46c`. Confirm PR #34 actually merged at that SHA and that `git diff 89f304b9ff98e08fb4a45c72177b9fbedbfd5cf8..main --stat` has no file/tree differences. **STOP for base drift**, conflicting changes, or uncommitted isolated-worktree changes; never reset user work.
2. Read `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`; `docs/{00_PROJECT_MASTER_SPEC,01_PRODUCT_REQUIREMENTS,02_SYSTEM_ARCHITECTURE,03_REPOSITORY_STRUCTURE,04_DOMAIN_MODEL,05_DATABASE_SCHEMA,06_API_CONTRACTS,12_CLINICAL_PROVENANCE_SPEC,15_DOCUMENT_AI_OCR_SPEC,26_PRIVACY_CONSENT_SPEC,29_ENGINEERING_STANDARDS,30_TESTING_STRATEGY,33_ERROR_HANDLING_POLICY,34_MASTER_IMPLEMENTATION_PLAN}.md`; `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER,P11_READINESS_GATE_REVIEW,P10_READINESS_GATE_REVIEW,P8_C_INTEGRATION_GATE_REVIEW,P9_C_SAFETY_PRESENTATION_GATE_REVIEW}.md`; accepted R3 dependency/OCR policies. Prioritize Spec 15 §§2, 5–8, 10–11, and the explicit **P11-D BLOCKED** readiness wording. Conceptual API/table specs are not permission to implement them.
3. Read actual merged P11 code: `backend/app/modules/documents/{contracts,ports,processing,classification,registry,domain,ingestion}.py` and `backend/tests/{test_document_*,ocr_support/**}`. Note P11-B `DocumentProcessingResult`/`PageResult`/`TextBlock`/`TableCell`, `Confidence`, `ConfidenceKind` and `SyntheticSourceRef`; P11-C `DocumentType`, `ClassificationDecision`, `ProcessorResolutionReceipt` (`NOOP_ABSTAIN` only); P11-A `SyntheticDocumentDescriptor`/lifecycle. Inspect actual P5 provenance + fact interfaces solely to **ensure no import/write coupling**, not to call review methods. Inspect `backend/app/main.py`, OpenAPI module registry, Alembic and patient `/documents` unavailable placeholder.
4. Before edits, record proposed file scope, invariant matrix, negative tests, and exactly which clinical/source/approval decisions are deferred. No real patient or document fixtures; no source bytes; no external provider; no file paths/URLs. If a proposed design requires P11-D clinical rules, **STOP** and explain; do not expand the scope to deliver a runnable extractor.

## 1. Objective — inert, detached structural evidence only

Provide a small, pure document-domain foundation for a **hypothetical** future document-AI candidate to be *described and abstained from*, not produced from medical content. No actual OCR text extraction, human review, fact creation or field normalization in this work unit. Prefer `backend/app/modules/documents/candidates.py` and optionally `backend/app/modules/documents/evidence.py`, with no extra framework unless essential.

### A. Closed, versioned synthetic candidate envelope

1. Define immutable frozen/versioned envelope(s) with strict exact-runtime types and explicit engineering-only authority. Fields may include: `candidate_ref` (strict non-dereferenceable `SYNTHETIC_*` token), `document_id`, `processing_attempt_id`, `source` (`SyntheticSourceRef`), a **single eligible** `DocumentType`, exact `processor_id`/`processor_version` as previously declared inert metadata, `candidate_schema_version`, `evidence[]` (see B), `created_at` UTC, `confidence` with explicit UNKNOWN semantics, and fixed, closed abstention/warning reason codes. Include `request_id` or routing/schema version **only if** necessary to make correlation verifiable and traceable to existing contracts.
2. Any field identity must be a **nonmedical machine token only**, such as `SYNTHETIC_FIELD_A`, or omit field identity entirely if it encourages pretending there is a medical extraction schema. **Do not include any original source text, OCR `TextBlock.text`, normalized value, unit, dosage, analyte, diagnosis, date interpretation, medical code, free-form patient narrative, tokenized private content, embeddings, provider payload, or actual model prompt.** Do not invent type-specific medical schemas or real medical mappings. This is a skeleton of a future *unconfirmed proposal*, not a parser.
3. Closed status/disposition must be **`UNCONFIRMED` or `ABSTAINED` only** (exact naming acceptable); never `PATIENT_CONFIRMED`, `CLINICIAN_CONFIRMED`, `APPROVED`, `SIGNED`, `TREATED`, `READY_FOR_CLINICAL_USE`, or a P5 `VerificationState`. Unknown source, unknown/OTHER document type, invalid/conflicting classification, missing evidence and unavailable/failed pages must not become a positive clinical claim. A syntactically valid envelope is **not** approved evidence, permission, a fact, or clinical accuracy.
4. If an envelope carries synthetic confidence, reuse P11-B `Confidence`/`ConfidenceKind`; `UNKNOWN` must use `value=None`. A numeric recognizer confidence is NOT clinical verification or a threshold for promotion. Do not add a low-confidence auto-review/approve rule. If confidence semantics cannot honestly be represented without a provider, prefer **UNKNOWN** only.
5. Zero executable processor implementations, callables/registrations, auto selection, medical value inference, runtime feature switches or write operations. The six canonical processor names remain inactive metadata declarations, not classes with extraction functions. No `extract()`, `parse()`, `promote()`, `confirm()` or new registry executor.

### B. Immutable, bounded source-evidence pointers without authority

1. Define strict structural evidence reference(s): page number, existing synthetic block ID and/or table/cell ID, optionally a `NormalizedBox`, source document and attempt ID, with explicit schema/routing version. Reuse P11-B types and limits (`MAX_PAGES`, `MAX_BLOCKS_PER_PAGE`, bounded table cells, etc.) where applicable; no unbounded page/evidence lists. Evidence is a **reference**, not authorization or proof the referenced source is accessible.
2. Make ordering canonical, references unique, and identity/context checks explicit (document, request/attempt, source). Reject stale/mismatched source versions or unknown evidence ID, invalid page number, out-of-bounds geometry, duplicates, extra enum values and malformed subobjects using stable **content-free typed errors**. Direct dataclass construction must be as strict as helper construction.
3. Optionally provide one **pure verifier** that accepts a caller-supplied, already-valid P11-B `DocumentProcessingResult` and candidate-envelope metadata, revalidates/detaches caller-held nested objects as necessary, and checks **only structural identities**: requested page, succeeded page vs failed page, exact block/table/cell ID and allowed block kind, request/document/attempt/source, output contract/version. This verifier must **never inspect, copy, hash, format, log, return or derive medical semantics from** `TextBlock.text` or any value-bearing OCR content. If deep result revalidation is unsafe or entails touching text/real files, restrict the subset to identity-only handles and report that cross-result linkage remains unverified.
4. A P11-C `ProcessorResolutionReceipt` is `ENGINEERING_ONLY / NOOP_ABSTAIN`, even when `PINNED_METADATA`. It may be checked for declared metadata compatibility but MUST NOT grant access, execute a processor, imply successful extraction or bypass structural source validation. A `ClassificationDecision` is a synthetic caller label only, not OCR-derived document truth.
5. Missing/failed/partial/unavailable/revoked/deleted/superseded source conditions cannot be fabricated as `VALID` or clinician-reviewed. If no live source state is modeled, return a closed **UNVERIFIED/ABSTAINED** engineering outcome instead of claiming that source access or existence was checked. No source-open functions.

### C. Fail-closed boundaries and replay/determinism

- **Runtime type checks BEFORE** regex, set/hash, tuple unpacking, comparison, sorting, mapping, field traversal or arithmetic. Reject `bool` as integer, float-as-int, list/dict/set in tuple fields, `str` pretending to be enum, mutated frozen dataclass internals, forged nested IDs/references, invalid UTC types, unknown versions, overlarge data and unexpected constructor fields where practical. No raw `TypeError`/`AttributeError` leaks from untrusted boundary inputs; do not indiscriminately catch unrelated bugs.
- Bounded deterministic canonical order, no randomness, clock reads, global caches, module registration, reflection, environment-dependent behavior or hidden fallback. A forged/desynchronized envelope/structural result must be rejected at use boundaries, not merely construction time; never rely on `frozen=True` as an unforgeable security boundary.
- Repr-hidden source/opaque IDs/synthetic evidence tokens and **content-free** exception strings and formatted tracebacks; include privacy-canary regressions. No log, HTTP, persistence or telemetry outputs at all. Do not imply privacy approval based on synthetic tests.
- Deliberately separate **structural evidence validity** from **source access authorization**, **clinical correctness**, **medical verification**, and **source retention**; all latter checks are deferred to human-governed future phases.

## 2. Tests — direct-constructor, negative, cross-phase, zero-activation

Add focused tests with synthetic nonmedical identifiers only:

1. Strict value/object/tuple types, max lengths, bounded counts and numeric ranges, timezone-aware UTC, `ConfidenceKind.UNKNOWN`, closed statuses/reasons and immutable detached snapshots. Reject raw strings in enums, bool/float integers, forged authority/confirmation, unhashable hostile nested inputs, wrong/duplicate source identities, unknown schema, missing IDs and oversized references, using closed errors and no canary leaks.
2. Deterministic ordering and idempotent pure verification for same inputs (including permutations). Reject ambiguous or duplicate evidence, stale attempt/source/request, page outside requested coverage, wrong table cell/block kind, nonexistent structural reference, failed/partial page presented as complete, and unavailable source without granting existence/permission. Assert no reason-code leaks OCR text.
3. Positive **synthetic structural** cases only: a matching reference returns strictly `STRUCTURALLY_MATCHED_UNCONFIRMED` or equivalent clearly technical outcome (if this verifier is implemented), never an accepted clinical candidate. Null/unavailable evidence => abstention. No value extraction. Test full-provenance matching rather than a simple count or presence check.
4. Malicious mutation via `object.__setattr__` after construction, including nested source handle/evidence or P11-B result/metadata where relevant; boundary revalidation must reject forged selection, fake version and changed reference. Explicit mismatch must not be silently repaired by reconstructing inconsistent graphs.
5. P11-A/B/C suites unchanged and green; P7 deterministic/manual intake unaffected; P8-C/P9-C Stage 3 and P10 live restrictions unchanged. Patient document UI still unavailable; `app.main` OpenAPI has no document endpoints; no `documents/public.py`, `application.py`, ORM/model, worker registration, migration, BFF route, production OCR mock import or module capability registration.
6. Inspect AST/import graph to prove new files have no filesystem/network/provider/model, browser/API, P5 fact-write, P8/P9/P10 authorization, `JobDispatcher`, object-store operation or dynamic plugin import. All tests use offline synthetic fixtures only.

**Acceptance discipline:** Engineering structural evidence only toward *future* Spec 15 §7/§8 and `FR-DOC-011..018`, `FR-DOC-020..021`/`FR-PROV` design reasoning. **NOT** a real prescription/lab/diagnosis extractor, actual provenance authorized read, stored clinical fact or a passing P11-D acceptance criterion. `AC-P11-001..011` remain **NOT VERIFIED for live use**. No promotion to P5 facts or P10 review.

## 3. Locked allowlist — minimum files only

Expected new files, if justified:

```text
backend/app/modules/documents/candidates.py            # frozen synthetic UNCONFIRMED/ABSTAIN contracts
backend/app/modules/documents/evidence.py              # optional pure structural evidence matching, NO text interpretation
backend/tests/test_document_candidate_contracts.py
backend/tests/test_document_candidate_evidence.py      # optional structural linkage proof
backend/tests/test_document_candidate_boundaries.py    # zero-runtime/clinical/provider proof

docs/03_REPOSITORY_STRUCTURE.md                         # actual inventory only
docs/implementation/38_PROGRESS_TRACKER.md             # merged P11-A evidence and precise P11-D status
docs/implementation/P11_READINESS_GATE_REVIEW.md       # OPTIONAL dated appendix; historical snapshot stays intact, 0/9 unchanged
docs/codex/CODEX_PHASE_PROMPTS/P11_D_SYNTHETIC_DETACHED_EVIDENCE_AND_UNCONFIRMED_CANDIDATE_CONTRACTS.md
```

Tests may reuse `backend/tests/ocr_support/**` only if necessary and existing fixture semantics remain untouched; justify changed paths before editing. **Do not change** P11-A/B/C production modules (`domain.py`, `ingestion.py`, `contracts.py`, `ports.py`, `processing.py`, `classification.py`, `registry.py`) as a convenience; STOP on a genuine blocking incompatibility and request a separate review. No `app/main.py`, `api.py`, `public.py`, `application.py`, migration, ORM, P5/P7/P8/P9/P10, frontend, infra, worker, dependencies/lockfiles, Docker/CI, runtime flags, patient data, file inputs, signed URLs, actual OCR/LLM/medical extraction or external egress.

## 4. Mandatory exact-SHA quality and PR handoff

1. Implement smallest pure contracts only, add negative/direct-constructor tests, no brittle string-only no-activation proof. Run new focused P11-D tests and unchanged P11-A/B/C + P7–P10 regression suites; full Ruff lint/format, strict mypy, compile/import and network-free backend tests (record actual skips). Use `git diff --check`, allowlist and source/privacy/clinical/inactive execution audit.
2. Run real PostgreSQL integration tests and Alembic upgrade/current/check/downgrade/re-upgrade; head must stay `p7a_0007`. Run frontend formatting/lint/typecheck/tests and all three production builds; Playwright Chromium (disclose failures/flakes and retries), Docker build/non-root/readiness, Gitleaks and Trivy filesystem+image high/critical scans. Never weaken thresholds/skips or assume a local Playwright retry is equivalent to green exact-head CI.
3. Update `docs/implementation/38_PROGRESS_TRACKER.md` to recognize P11-A safe engineering PR #34 **MERGED** at `87f87e0a454db86bcdf67569fa1e6ab2061ee46c`; P11-D **implemented pending independent review** (only if actual work is done). Leave P11 PARTIAL, 0/9 live gates, P10 live 0/9, P8-C/P9-C Stage 3 blocked. Do not rewrite historical readiness claims as present-day implementation evidence.
4. Commit the **exact prompt** at the tracked docs path, push `phase/p11-d-synthetic-candidate-evidence-contracts`, open exactly one PR into verified `main`. Verify final local SHA == remote SHA == PR head; all six required GitHub Actions jobs conclude **SUCCESS ON THAT EXACT HEAD**: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`.
5. **DO NOT MERGE** or activate the next phase. No real patient upload, medical extraction or production OCR permitted. Report exact SHA, CI run and evidence for independent review.

### Required Codex report

```text
STATUS: COMPLETE SAFE ENGINEERING SUBSET / PARTIAL / BLOCKED
BRANCH: phase/p11-d-synthetic-candidate-evidence-contracts
BASE MAIN SHA: 87f87e0a454db86bcdf67569fa1e6ab2061ee46c
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER:
SYNTHETIC UNCONFIRMED CANDIDATE CONTRACTS:
STRUCTURAL EVIDENCE AND IDENTITY/PROVENANCE MATCHING:
NO MEDICAL VALUE EXTRACTION / AUTHORITY / SOURCE ACCESS:
DIRECT CONSTRUCTOR, MUTATION, BOUNDS, CONTENT-FREE ERROR EVIDENCE:
P11-A/B/C COMPATIBILITY / RUNTIME NON-ACTIVATION:
FOCUSED P11-D / P11-A/B/C / P7-P10 / FULL BACKEND / DB / FRONTEND / PLAYWRIGHT COUNTS:
CI RUN ID / EXACT FINAL HEAD / SIX JOB CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCIES / LOCKFILES / EXACT CHANGED PATHS:
FR-DOC/AC-P11 DESIGN EVIDENCE VS LIVE ACCEPTANCE:
P11 LIVE GATES: 0/9 APPROVED, 5 OPEN, 4 BLOCKED
P8-C / P9-C / P10 LIVE RESTRICTIONS:
UNRELATED CHANGES:
MERGED: NO
```

**STOP after report.** An inert synthetic envelope cannot validate medications, laboratories, diagnoses, source authorization or production medical-document workflows; P11-D real extraction remains BLOCKED.
