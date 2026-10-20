# SwasthyaSetu AI — P11-A: Synthetic Document Lifecycle and Ingestion Boundary Contracts

**Work unit:** `P11-A` — **SAFE ENGINEERING SUBSET ONLY**. Pure, inert synthetic document metadata, deterministic lifecycle and ingestion-decision *contracts/tests*. This is **not** patient upload, secure-file validation, storage or real document-processing implementation.

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified baseline:** `main @ d3c2125ebdb2c927f254b913a890b411ccc971e5`
**PR #33:** merged at that SHA; reviewed feature head `b3469adcaeb86e03d3e0b82ef1bdabdf7a11e7cf` is tree-equivalent.
**Proposed branch:** `phase/p11-a-synthetic-document-domain`
**Canonical requirements:** `docs/15_DOCUMENT_AI_OCR_SPEC.md` §§1–4, 6, 8, 10–13; `docs/04_DOMAIN_MODEL.md` §§33–36; `docs/05_DATABASE_SCHEMA.md` §15 (CONCEPTUAL ONLY); `docs/34_MASTER_IMPLEMENTATION_PLAN.md` §19; `docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md` AC-P11-001..011.
**Readiness:** `docs/implementation/P11_READINESS_GATE_REVIEW.md` — **0/9 live gates APPROVED; 5 OPEN and 4 BLOCKED**.
**Alembic:** `p7a_0007` — must remain unchanged.
**Delivery rule:** Isolated clean feature branch → push → existing six CI jobs succeed on exact remote final SHA → open PR → **DO NOT MERGE**; await independent review.

> **Authorization boundary.** This is a separately bounded **subset of P11-A**, not permission to execute P11-A's actual upload/storage/migration scope. P11-A live patient flows are blocked by missing lawful upload, consent/ownership/assignment, scanner/quarantine approval, approved object-store encryption/region/retention and schema decisions. A synthetic test object or synthetic state named `ACCEPTED` is **not** a malware-scan result, consent grant, operational clearance or clinical approval. Do not close any P11 acceptance criterion for live use.

## 0. Mandatory preflight and STOP criteria

1. Confirm clean isolated worktree; local/remote `main`, `origin/main`, and GitHub main exactly `d3c2125ebdb2c927f254b913a890b411ccc971e5`. Confirm PR #33 merged at that commit and its tree matches reviewed head; no newer drift. Do not reset/discard unrelated work or touch the user's pre-existing primary worktree changes. If the base has moved or there is a scope conflict, STOP and report.
2. Read governance `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md` and canonical `00_PROJECT_MASTER_SPEC`, `01_PRODUCT_REQUIREMENTS` FR-DOC-001..023 / FR-PROV-001..007, `02_SYSTEM_ARCHITECTURE`, `03_REPOSITORY_STRUCTURE`, `04_DOMAIN_MODEL` §§33–36, `05_DATABASE_SCHEMA` §15, `06_API_CONTRACTS` §§17–18, `12_CLINICAL_PROVENANCE_SPEC`, `15_DOCUMENT_AI_OCR_SPEC`, `23_PATIENT_APP_SPEC`, `26_PRIVACY_CONSENT_SPEC`, `29_ENGINEERING_STANDARDS`, `30_TESTING_STRATEGY`, `33_ERROR_HANDLING_POLICY`, `34_MASTER_IMPLEMENTATION_PLAN` §19, implementation `35_PHASE_ACCEPTANCE_CRITERIA`, `36_DEPENDENCY_MAP`, `37_DECISION_LOG`, `38_PROGRESS_TRACKER`, P11 readiness review and the P8-C/P9-C/P10 gate reviews. Read accepted R3 dependency/architecture rules. Canonical upload Pattern A vs B remains **OPEN**.
3. Inspect actual merged `backend/app/modules/documents/{contracts,ports,processing,classification,registry}.py`, P11-B/C tests and their boundary suites. Inspect existing `backend/app/shared/storage/{port,types}.py`, local storage adapter, `backend/app/jobs/`, PostgreSQL outbox, relevant existing P5/P7 immutable domain transition patterns, `backend/app/main.py` and module registry. Existing generic primitives are **not** an authorized document pipeline. No `clinical_documents` table or document API exists.
4. Before coding, state an explicit allowed changed-file list and a non-activation/no-PHI design. Any design requiring real file bytes, scanning, lawful authority, real actor identity, key custody, retention/deletion promise, production storage, schema migration, page parser, external service or provider **must be excluded and reported as a blocker**, never guessed.

## 1. Objective and clear boundaries

Implement **pure domain contracts** suitable for reasoning about a hypothetical synthetic uploaded document without ever accepting an uploaded file. Use the smallest cohesive file layout, e.g.:

```text
backend/app/modules/documents/domain.py       # synthetic identity/metadata and lifecycle (new)
backend/app/modules/documents/ingestion.py    # pure, simulation-only validation decisions (optional)
backend/tests/test_document_domain.py         # new focused lifecycle/constructor tests
backend/tests/test_document_ingestion.py      # new synthetic boundary/negative tests (optional)
backend/tests/test_document_ingestion_boundaries.py   # absence of runtime integration
```

Prefer one or two production-domain files, not a framework. Every new callable must be pure and side-effect free. Package import must remain inert. Explicitly separate this metadata/lifecycle **document aggregate** from P11-B `ProcessingAttempt` and generic P3 `JobStatus`; do not rewrite or import their states as an implicit equivalence. Preserve P11-C `DocumentType` vocabulary and existing P11-B non-dereferenceable `SyntheticSourceRef` where useful; never fork conflicting document type enums.

### A. Closed immutable synthetic document metadata

- Create strictly frozen, versioned values for an **engineering-only** document identity and bounded metadata. Use project `OpaqueId` with strict runtime validation, P11-C closed `DocumentType`, non-dereferenceable `SYNTHETIC_*` source/owner-scope handles *only if necessary*, and explicit engineering-only authority marker. Patient IDs, encounter IDs, actor identities, consent grants, bucket keys, filesystem paths, URLs, signed tokens and real file names are **not available** in this subset.
- Model limited **synthetic descriptor** fields such as declared document category (may be UNKNOWN), fixed synthetic representation kind (`SYNTHETIC_PDF`, `SYNTHETIC_PNG`, `SYNTHETIC_JPEG`, or equivalent explicit test token; **not** real MIME acceptance), bounded byte-count and page-count **claims** (not observed/verified measurements), and a syntactically valid SHA-256 checksum **as hypothetical metadata only** where useful. Decide a defensible engineering cap for test metadata and state clearly it is **not** an approved patient upload file-size/page-count policy. No real input bytes, checksum computation over uploaded content or file signature recognition in runtime code.
- Optional timestamp fields must be timezone-aware and normalized to UTC; version and generation counters must be exact positive integers (reject bool/float lookalikes); use exact enums/tuples, canonical ordering and typed content-free error codes. Direct constructors must enforce all invariants, not just helper builders. Hide all sensitive-looking identity/source metadata from `repr` and errors; never store arbitrary original filenames or OCR text.
- Source ID, digest and synthetic owner-scope are linkage/comparison metadata, **not authorization, proof of malware clearance, document authenticity, patient equivalence or permission to deduplicate across owners**. No automatic classification from file metadata; preserve `UNKNOWN` and `OTHER` semantics from P11-C.

### B. Canonical pure lifecycle transitions with explicit simulation boundaries

- Define exact canonical document states from Spec 15 §3.3: `UPLOADED`, `VALIDATING`, `ACCEPTED`, `QUEUED`, `PROCESSING`, `NEEDS_REVIEW`, `SUCCEEDED`, `FAILED`, `REJECTED`. Keep typed status distinct from P11-B attempt state and OCR `ResultStatus`. `REJECTED` terminal for same hypothetical object. Reprocessing from `FAILED`, `NEEDS_REVIEW` or `SUCCEEDED` toward `QUEUED` requires an **explicit new synthetic attempt/generation**; do not automatically reuse a completed result. Do not invent a live cancellation/delete policy.
- Permit **only** canonical transitions, with deterministic immutability, monotonic version/generation where applicable and UTC occurred-at chronology. Do not permit backdating, terminal-state replay, invalid direct-constructor state, cross-document transition, duplicate attempt IDs, stale source/version, or status advance based on P11-C metadata-only `NOOP_ABSTAIN` receipts. Reject invalid transitions with closed content-free typed errors. Avoid automatic retries, queues, storage and side effects.
- Treat `VALIDATING → ACCEPTED` solely as an **explicitly supplied simulation/test decision**, never an automatic scanner-pass assertion. A simulated decision must be typed as `ENGINEERING_ONLY`/`SYNTHETIC_*` and incapable of representing a real scanner verdict, consent authorization or patient-data acceptance. If this distinction cannot be encoded clearly, leave ACCEPTED/processing transitions as pure externally asserted hypothetical states rather than fabricating security evidence.
- Status means technical state of a hypothetical **synthetic fixture**, not clinical reliability, confirmation, source access or patient-facing progress. Preserve exact semantics in code comments and tests.

### C. Synthetic ingestion assessment: no bytes and no fake scanner

- Optionally add a pure, versioned `SyntheticIngestionAssessment` that compares *only caller-supplied synthetic descriptors*, with strict closed dispositions (e.g. `SYNTHETIC_COMPATIBLE`, `REJECTED`, `UNKNOWN_REQUIRES_REVIEW`) and fixed bounded reason codes. Do **not** accept `bytes`, file objects, streams, local paths, filenames, MIME signatures from untrusted files or URLs. Do not parse PDF/image, sanitize real filenames, scan malware, verify cryptographic authenticity or claim that a synthetic descriptor passed real security controls.
- Unknown/unsupported representation, mismatch of declared vs expected engineering claims, missing/ambiguous checksum, mismatched synthetic source/owner-scope, oversize fixture metadata, invalid version or prohibited authority field must fail closed. If an engineering-only match is returned, it is a *mock simulation receipt* without permissions; it must never authorize `ObjectStoragePort`, `JobDispatcher`, or document processing.
- Model owner-scoped synthetic **idempotency comparison** only if implementable purely without retained state: same explicitly supplied synthetic owner/identity/idempotency key/metadata may compare equal; mismatches fail closed. Absolutely no cross-owner lookup, global digest cache, existence probe, persistence, production duplicate resolution or cross-patient hash-sharing. A SHA-256 is not consent or source authority.
- Write down intentionally **DEFERRED**: real file/stream validation, content signature vs declared MIME, executable/polyglot/zip-bomb/PDF active-content defenses, virus scanning, quarantine, retention/deletion, storage key generation, checksums over real bytes, upload Pattern A/B, patient/clinician authorization and compliance. Future P11-A live implementation needs human security/privacy/schema approvals and independent hostile-input validation.

### D. Compatibility and non-escalation

- P11-A synthetic metadata may **reference** P11-B processing attempt IDs and P11-C document type labels but cannot trigger mock OCR, execute processor registry, select a live provider, or promote OCR output to facts. `ProcessorResolutionReceipt` is intentionally `NOOP_ABSTAIN`, never an ingestion permit.
- Do not add a live `DocumentParserPort` adapter, P11-B mock to production, P11-C runtime execution, P11-D clinical extraction or P11-E review UI. Do not touch P5/P7/P8/P9/P10 application behavior.
- No text or test fixture may represent patient names, actual prescription details, diagnoses, medications, real health documents, live clinician decisions, therapeutic advice or clinical truth.

## 2. Independent adversarial proof and acceptance discipline

Add thorough **direct-constructor** tests (not solely happy-path builder tests) covering:

1. Closed statuses, source/owner-scope tokens, immutable nested state, strictly validated OpaqueId/document identity/type/version/size/page/date fields, bool/float/unhashable/fake enum/subclass/oversized input rejection with typed content-free errors; `repr`, exception and formatted-traceback canary non-leakage.
2. Every allowed state edge and every forbidden edge of Spec 15 §3.3, deterministic state/version ordering, backward UTC, stale generation, cross-document/attempt mismatch, terminal REJECTED replay, repeated completion and authorized new synthetic attempt invariants. Distinguish document status, processing-attempt status and OCR result status with explicit assertions.
3. Simulated verification cannot be forged as `MALWARE_CLEARED`, `APPROVED`, `CONSENT_GRANTED`, `CLINICIAN_CONFIRMED`, `SIGNED`, a real security scanner result or patient upload permission; no result from this phase sets P5 verification or P9 safety state.
4. Pure unknown/unsupported/mismatched/oversize synthetic descriptor decisions; explicit negative cases for hypothetical MIME/representation disagreement (without inspecting files), duplicate synthetic identifiers and digest-only cross-owner comparison; no filename/path/URL/bytes/file parser ingestion in this phase.
5. Source authority isolation: P11-B `SyntheticSourceRef` does not grant access; P11-C selection receipts still abstain and never execute; OCR mock remains under tests only. Manually inspect actual FastAPI OpenAPI and module registry: no documents API, `public.py`, upload route, worker binding or BFF/UI upload surface.
6. Zero P11-A ORM model/table/Alembic migration, no object read/write (even local adapter), no scanner/dependency/egress/feature flag, no provider/classifier execution; unchanged P7 deterministic/manual intake and P8-C/P9-C/P10 boundaries.
7. Run all P11-B and P11-C regression tests unchanged, P7–P10 regressions and full project CI. Never weaken tests/skip policies for convenience.

**Traceability:** This phase can contribute *synthetic engineering reasoning evidence* about future `FR-DOC-001`, `FR-DOC-003`, `FR-DOC-022`, and `AC-P11-001/003/010` boundaries, **not** a passed secure-upload, persisted-metadata, live-status or duplicate-document acceptance criterion. `AC-P11-001..011` remain **NOT VERIFIED for live document workflows**. P11 remains PARTIAL. Record negative tests and unresolved live gates; do not inflate completion.

## 3. Scope lock — allowed files only

```text
backend/app/modules/documents/domain.py            # pure synthetic document values/status, if used
backend/app/modules/documents/ingestion.py         # pure synthetic assessment, if justified
backend/tests/test_document_domain.py
backend/tests/test_document_ingestion.py            # optional
backend/tests/test_document_ingestion_boundaries.py # optional
backend/tests/ocr_support/**                        # fixture-only additions if unavoidable; report why

docs/03_REPOSITORY_STRUCTURE.md                     # exact inventory update
docs/implementation/38_PROGRESS_TRACKER.md          # P11-A safe subset; correct stale merged P11-C state
docs/implementation/P11_READINESS_GATE_REVIEW.md    # OPTIONAL dated technical-footnote; 0/9 unchanged
docs/codex/CODEX_PHASE_PROMPTS/P11_A_SYNTHETIC_DOCUMENT_LIFECYCLE_AND_INGESTION_GUARDS.md
```

Do **not** modify `contracts.py`, `ports.py`, `processing.py`, `classification.py`, or `registry.py` unless an independently reportable compatibility defect blocks pure contracts; STOP and seek review rather than broad rewrites. No changes anywhere under `backend/app/main.py`, `backend/app/api`, `backend/app/adapters`, P5/P7/P8/P9/P10 modules, `apps/`, `migrations/`, `alembic/`, `infra/`, `workers/`, packages, dependencies/lockfiles, CI/Docker, production feature flags or clinical policies. No upload controller/BFF/UI, private object store, malware scanner, storage provider, patient/session/clinician access, ORMs, migration, outbox events, job handlers, production OCR, files, research datasets, model inference, egress or dynamic plugins.

## 4. Quality gates and exact-head PR handoff

1. Verify branch/base SHA, record a short preflight and scoped design; inspect code and governance *before* writing. Keep progress tracker accurate: P10-A PR #30, P11-B PR #32 and P11-C PR #33 were merged; P11-A is only engineering subset **pending independent review**. P11 live gates remain **0 APPROVED / 5 OPEN / 4 BLOCKED**, P10 live clinician gates remain 0/9, P8-C and P9-C Stage 3 remain blocked. P11 readiness document originally described an older Pre-P11 snapshot; if changing it, add a dated engineering note without falsifying approval dates or altering historical evidence.
2. Execute focused new tests; P11-B/C, P7–P10 regressions; complete network-free pytest (report skipped DB tests separately), Ruff formatting/lint, strict mypy, compile/import, `git diff --check`, file allowlist, clinical-text/privacy/egress/import-graph checks. Test requirements include adversarial direct constructors and no runtime route/registry.
3. Execute real PostgreSQL tests, Alembic upgrade/current/check and downgrade/re-upgrade with head `p7a_0007`; frontend format/lint/typecheck/tests and all three production builds, Docker build/health/non-root/migration, Playwright Chromium journeys (report any intermittent failures/retries), Gitleaks and Trivy filesystem/image high/critical checks. No CI/policy relaxation.
4. Push `phase/p11-a-synthetic-document-domain` and open **one** PR into unchanged base `main`. Independently confirm PR head equals final local/remote SHA; six jobs all completed **SUCCESS at exact final SHA**: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. Any later commit invalidates earlier exact-head approval until CI reruns.
5. **DO NOT MERGE** or automatically begin P11-D/E, real P11-A uploads, OCR-provider activation or P12. Report the final PR URL, exact SHA, CI ID and blockers for independent review.

### Required Codex completion format

```text
STATUS: COMPLETE SAFE ENGINEERING SUBSET / PARTIAL / BLOCKED
BRANCH: phase/p11-a-synthetic-document-domain
BASE MAIN SHA: d3c2125ebdb2c927f254b913a890b411ccc971e5
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
SYNTHETIC DOCUMENT METADATA / CLOSED TYPES:
PURE DOCUMENT LIFECYCLE / REPROCESS GUARDS:
SYNTHETIC INGESTION ASSESSMENT / NO REAL SCANNER OR FILES:
OWNER-SCOPE / IDEMPOTENCY / NO CROSS-PATIENT DEDUP:
P11-B/C COMPATIBILITY / RUNTIME NON-ACTIVATION:
FOCUSED / P11-B/C / FULL BACKEND / POSTGRESQL / FRONTEND / PLAYWRIGHT TEST COUNTS:
CI RUN ID / FINAL HEAD / SIX JOB CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCIES / CHANGED PATHS:
FR/AC-P11 PARTIAL ENGINEERING EVIDENCE VS LIVE ACCEPTANCE:
P11 LIVE GATES: 0/9 APPROVED, 5 OPEN, 4 BLOCKED
P8-C / P9-C / P10 LIVE RESTRICTIONS:
UNRELATED CHANGES:
MERGED: NO
```

**STOP after opening the PR and reporting.** This work is an isolated technical foundation, not a functional patient document upload feature, privacy or security approval, clinical validation or production-readiness milestone.
