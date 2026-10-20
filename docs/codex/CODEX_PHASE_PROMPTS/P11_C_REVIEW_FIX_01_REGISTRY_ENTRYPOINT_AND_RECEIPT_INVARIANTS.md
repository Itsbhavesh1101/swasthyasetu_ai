# SwasthyaSetu AI — P11-C Review Fix 01: Registry Boundary & Immutable Receipt Integrity

**Decision:** REVIEW FIX REQUIRED — continue on existing PR #33, **DO NOT MERGE** until independent re-review.

- **Repository:** `Itsbhavesh1101/swasthyasetu_ai`
- **Branch:** `phase/p11-c-synthetic-document-registry`
- **Reviewed PR head:** `375d45f8e14191f651e10778fd28004d3c633e53`
- **Baseline main:** `a8dea0b374017793f119a85daa971b8256881ab4`
- **Reviewed GitHub CI:** `39339394209`; all six jobs successful at reviewed head.
- **Alembic:** must remain `p7a_0007`; no dependencies, migration, API, UI, provider or runtime integration.
- **Approval:** P11 live 0/9 approved (5 OPEN, 4 BLOCKED). P8-C/P9-C Stage 3, P10 live and P11 live restrictions remain intact.

## Findings (verified directly against PR #33 source)

### 1. `ProcessorRegistry.resolve()` trusts a caller-held decision instance without revalidation

**Location:** `backend/app/modules/documents/registry.py` — `ProcessorRegistry.resolve`.

`ClassificationDecision.__post_init__` correctly checks candidate evidence versus selected type and disposition, but `resolve` only checks `type(decision) is ClassificationDecision`. A caller can mutate even a frozen Python instance using `object.__setattr__` after it was validated. For example: obtain a legitimate `LAB_REPORT` selected decision, force `selected_type = DocumentType.PRESCRIPTION` while leaving its underlying `LAB_REPORT` evidence, then pass it to `build_synthetic_processor_registry().resolve(decision)`. As currently written, the resolver can emit a **`PINNED_METADATA` receipt for `PrescriptionProcessor` despite contradictory classification evidence**. This is synthetic-only, not a live clinical routing exploit, but violates the promised fail-closed registry boundary and exact-evidence selection invariant.

**Required:** At the *entry* to `resolve`, reconstruct and revalidate a detached `ClassificationDecision` (or equivalent strict validator) from the supplied fields, including exact candidate identity/context/version and disposition/reason/selected-type coherence. Use only the validated snapshot throughout the function. Reject forged selected types, unsupported values, wrong schema/config and malformed nested candidate state with a **closed content-free error**, never generate a positive receipt from an inconsistent decision. Preserve identical behavior for legitimate selected/unknown/other/conflict/empty cases.

**Tests:** Start with a valid selected `LAB_REPORT` decision; mutate its selected type to `PRESCRIPTION`, its disposition/reason, and one candidate's document type or source/reference; verify `resolve` refuses with a closed error and never issues `PINNED_METADATA`. Test both caller orders and legitimate fresh decisions. Do not mistake standard `FrozenInstanceError` tests for sufficient boundary hardening—`object.__setattr__` intentionally exercises hostile caller-held instances.

### 2. Registry construction trusts previously validated but caller-mutable `ProcessorPin` objects

**Location:** `backend/app/modules/documents/registry.py` — `ProcessorRegistry.__init__`, loop over `pins`.

The registry revalidates and snapshots descriptors, but does not reconstruct/revalidate pins before using their fields in dict membership, tuple hashing and lookup. A caller can mutate a previously created `ProcessorPin` via `object.__setattr__` (for example, change `processor_version` to `['private-canary']`). The `registrations.get((pin.processor_id, pin.processor_version))` lookup can then throw a raw `TypeError: unhashable type: 'list'` instead of the required typed content-free failure. A forged pin's type/validity cannot safely be assumed merely because its class matches.

**Required:** Revalidate/snapshot each pin before any hash/set/dict access, duplicate checks or registry lookup; use type checks before regex or hashing; ensure document type, processor ID/version and legal category are valid. Reject malformed/forged pin fields with `ProcessorRegistryError`, no echo of attacker-provided values in message, `repr` or formatted traceback. Keep order-independence, exact version pins and duplicate/conflicting ownership behavior unchanged.

**Tests:** Mutate existing legitimate `ProcessorPin` fields to list/dict/fake enum/wrong document type/invalid versions; test canary isolation and typed errors, including reversed insertion order and valid positive resolution.

### 3. Direct construction of *unselected* `ProcessorResolutionReceipt` permits mutable and untyped empty collections

**Location:** `backend/app/modules/documents/registry.py` — `ProcessorResolutionReceipt.__post_init__` nonselected branch.

For `ABSTAINED`, `UNAVAILABLE`, or `AMBIGUOUS`, `invalid_empty` checks merely `bool(self.parser_modes or self.ocr_modes or self.input_schema_versions)`. Empty `list`, `dict` or `set` fields therefore pass, although the frozen receipt promises immutable typed tuples. Such a constructed receipt can be mutated after creation by appending an item to a list, contradicting the strictly immutable metadata contract. The selected path has tuple checks, but the nonselected path does not.

**Required:** Enforce **exact tuple types** (and closed item types where applicable) on `parser_modes`, `ocr_modes`, `input_schema_versions` **for every status**, prior to truthiness, hashing or other operations. For nonselected status require all three literally empty tuples and all selection fields `None`. Also validate exact `None`/enum/constant status/reason relationships as presently designed. Do not add executable metadata.

**Tests:** Directly `dataclasses.replace` a legitimate abstained/unavailable/ambiguous receipt with `parser_modes=[]`, `ocr_modes={}`, `input_schema_versions=set()` or hostile falsy objects, and assert a typed content-free `ProcessorRegistryError`. Confirm a normal exact pinned receipt and all nonselected legitimate receipts remain valid and frozen.

## Scope lock and implementation instructions

1. Verify feature head, `main`, original branch and six-success exact-head CI above; clean isolated worktree. STOP if drift, report without force reset.
2. Read `docs/codex/CODEX_PHASE_PROMPTS/P11_C_SYNTHETIC_DOCUMENT_CLASSIFICATION_AND_PROCESSOR_REGISTRY.md`, `docs/15_DOCUMENT_AI_OCR_SPEC.md`, P11 readiness review, and current `classification.py`, `registry.py`, P11-C tests. Keep the repairs minimal and directly tied to these three issues.
3. **Expected allowed paths:**
   - `backend/app/modules/documents/registry.py`
   - `backend/app/modules/documents/classification.py` **only if** a shared pure revalidation helper is necessary
   - `backend/tests/test_document_processor_registry.py`
   - `backend/tests/test_document_classification.py` **only if** justified by boundary tests
   - `docs/codex/CODEX_PHASE_PROMPTS/P11_C_REVIEW_FIX_01_REGISTRY_ENTRYPOINT_AND_RECEIPT_INVARIANTS.md` (track this instruction in repo)
   - `docs/implementation/38_PROGRESS_TRACKER.md` **only if** correcting stale P10-A/P11-B merged status; no approval-state inflation.
4. **Forbidden:** OCR models/providers, clinical content/medical classifier, file uploads/object-store operations, patient or clinician data/access, APIs/UI, dynamic imports, processor callbacks, module registration, jobs/worker activation, ORM/table/migrations, AI/safety/summary activation, provider egress, dependencies/lockfiles, security or CI weakening. P11 remains engineering-only and no AC-P11 live claim becomes complete.
5. Check exact typed failure codes and nonleakage on formatted exceptions. Prefer reusing existing established constructors to revalidate rather than adding a broad new framework. Preserve independent frozen snapshots, deterministic canonical ordering, version-pin semantics and NOOP_ABSTAIN receipts.
6. Run focused P11-C and P11-B regression tests, P7–P10 tests, full backend Ruff/strict mypy/pytest, real PostgreSQL and Alembic checks, frontend test/build, Playwright, Docker non-root/readiness, Gitleaks and Trivy. Disclose any flaky/retried Playwright attempts accurately.
7. Push **same branch** to update **existing PR #33**. Verify the final remote head and **all six** GitHub jobs successful at that **new** exact SHA: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. Never merge it.

## Required Codex handoff

```text
STATUS: COMPLETE SAFE ENGINEERING REPAIR / BLOCKED
PR: #33 — OPEN, NOT MERGED
FINAL LOCAL SHA:
FINAL REMOTE SHA:
FINDING 1 — decision revalidation at registry entry:
FINDING 2 — pin revalidation before hashing:
FINDING 3 — receipt immutability/direct constructor:
FOCUSED P11-C / P11-B / FULL BACKEND / DB / FRONTEND / PLAYWRIGHT:
CI RUN ID / EXACT HEAD / SIX JOB CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCIES / CHANGED PATHS:
P11 LIVE GATES: 0/9 approved, 5 OPEN, 4 BLOCKED
P8-C / P9-C / P10 RESTRICTIONS:
MERGED: NO
```

Stop and return for **independent source and CI re-review**; do not advance P11-A/D/E or P12.
