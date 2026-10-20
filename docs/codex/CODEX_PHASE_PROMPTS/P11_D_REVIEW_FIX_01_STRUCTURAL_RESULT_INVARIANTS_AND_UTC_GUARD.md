# SwasthyaSetu AI — P11-D Review Fix 01: Structural Result Integrity and UTC Contract Guard

**Independent review verdict:** **REVIEW FIX REQUIRED** for **PR #35**. Repair the **existing** feature branch and PR. **DO NOT MERGE** until fresh independent re-review of the exact final SHA.

| Item | Verified value |
|---|---|
| Repository | `Itsbhavesh1101/swasthyasetu_ai` |
| PR and branch | `#35` — `phase/p11-d-synthetic-candidate-evidence-contracts` |
| Reviewed PR head | `141b3fa00ff7699f23e6e4e0c8db8bc78d4b8135` |
| Base `main` | `87f87e0a454db86bcdf67569fa1e6ab2061ee46c` |
| Reviewed CI | `39412454043`, **all six jobs SUCCESS** on exact reviewed head (push-triggered) |
| Alembic | `p7a_0007` — unchanged |
| Governance | P11 live **0/9 approved, 5 OPEN, 4 BLOCKED**; P8-C/P9-C Stage 3 and P10 live restrictions intact |

**Authorization boundary:** Only pure synthetic/nonmedical P11-D detached evidence and structural candidate contract repairs. No real extraction, uploaded content, source access, clinical inference, verification, patient/clinician runtime, OCR execution, storage, API or migration. A positive **`STRUCTURALLY_MATCHED_UNCONFIRMED`** result can attest only to the *integrity of structural references that were actually checked*; it is neither clinical truth nor source authorization.

## Finding 1 — `verify_structural_evidence()` can return a positive match from an invalid, mutated structural result

**Location:** `backend/app/modules/documents/evidence.py` — `_result_index`, `verify_structural_evidence`.

**Observed from reviewed source:** `_result_index` checks context IDs, page ordering/status, block IDs/kinds/boxes, table/cell ID links and overall technical result status, but leaves other **non-text structural contract invariants** unchecked. `DocumentProcessingResult`, `PageResult`, `TextBlock`, `TableResult`, and `TableCell` are frozen only under ordinary assignment: a caller can mutate a previously valid object via `object.__setattr__` before passing it to this verifier. Examples that the current structural index does not guard before positive matching:

- Change a succeeded `PageResult.width` to `-1`, `height` to `0`, or `rotation_degrees` to `45`, retaining page/block identity. The page is not structurally valid under P11-B, yet a referenced block can still receive `STRUCTURALLY_MATCHED_UNCONFIRMED`.
- Change a referenced `TableCell.row` to `-1`, `column` to a non-integer or span beyond the P11-B grid extent, without changing its `cell_id`, `block_id`, or box. The index will still match the cell.
- Change `DocumentProcessingResult.resource_usage.processed_pages` to a count inconsistent with succeeded pages, or mutate `TextBlock.reading_order` into a negative or untyped value. Structural indexing currently ignores these constraints.
- Mutate a table into a noncanonical/duplicate-cell graph (for example, duplicate cell ID across distinct block IDs) while keeping one referenced cell matchable. Full relevant table uniqueness and ordering invariants are not rechecked.

**Required:** At the *verifier's use boundary*, validate and detach (or defensively check) the **full relevant non-text structural graph** against the actual P11-B bounds and invariants, including **page dimensions/rotation, page/blocks/tables limits and canonical ordering, block kind/ID/order/geometry, table cell IDs/row/column/span/ordering and linkage, requested page coverage, status/error/warnings consistency, resource-usage processed-page count, provenance identity/schema/routing**. Avoid unbounded work; use fixed P11-B limits before iterating/hashing. Reject mutated graph invariants with `CandidateContractError` and closed, content-free codes before emitting any positive result. No invalid result may silently become a positive match.

**Critical text-blind exception:** **NEVER inspect, copy, compare, hash, format, serialize, log, reconstruct or validate `TextBlock.text`** or any free-text value-bearing OCR content. Do **not** pass whole text-bearing `TextBlock`/`PageResult` into their original constructors if doing so would read text. Instead check only necessary **non-text** structural fields, and document the intentionally unverified text/content validity. Continue to support the existing `ExplodingText` test and preserve `SourceAccessStatus.NOT_VERIFIED` without opening or reading sources. If full deep verification cannot be achieved without text, confine the positive claim to checked structure and **ABSTAIN** on uncheckable/inconsistent structure rather than inventing validity.

**Required tests:** Build an initially valid P11-B synthetic result; individually mutate page width/height/rotation, cell row/column/span, duplicate cell identity/noncanonical order, block reading order/ordering, or `resource_usage.processed_pages`. Each attempt to verify a matching candidate must refuse with a typed content-free failure (or clearly defined unverified abstention), never `STRUCTURALLY_MATCHED_UNCONFIRMED`. Prove ordinary valid block and table-cell references still match, `PARTIAL`/`FAILED` never produce positive, and malicious `ExplodingText`/privacy canaries are **never accessed or rendered**. Check hostile unhashable and wrong-type nested structural values before unsafe hashing, sorting, arithmetic, and regex.

## Finding 2 — candidate timestamp acceptance misses `utcoffset() is None`

**Location:** `backend/app/modules/documents/candidates.py` — `SyntheticDocumentCandidate.__post_init__`, handling of `created_at`.

**Observed:** The constructor verifies `type(created_at) is datetime` and `created_at.tzinfo is not None`, then calls `.astimezone(UTC)`. That check does **not** establish that the datetime is timezone-aware. Python permits a `tzinfo` object whose `utcoffset()` returns `None`; such a datetime is *naive by datetime semantics* despite a non-None `tzinfo`. `.astimezone(UTC)` may treat this as system-local time, violating the promised explicit timezone-aware UTC normalization and host-independent determinism. An exceptional custom timezone object can also produce a raw non-domain exception.

**Required:** Require `created_at.tzinfo is not None` **and** `created_at.utcoffset() is not None` before UTC conversion, with appropriately bounded handling for malformed/exceptional timezone objects to produce a closed, content-free `CandidateContractError`. Preserve valid timezone conversions, fixed UTC normalization, and existing candidate constraints. Do not add wall-clock reads or system-local fallback.

**Required tests:** Build a custom `tzinfo` subclass returning `None` from `utcoffset` and verify direct construction fails with `CandidateContractError`; verify naive datetimes fail, proper offset-aware datetimes normalize to UTC, and malformed/exceptional custom timezone behavior cannot expose secrets or raw `ValueError`/`TypeError` to the caller. Include regression for `snapshot_candidate` revalidating a mutated previously valid `created_at`.

## Repair constraints and scope lock

1. **Preflight:** Verify open PR #35 still at reviewed head `141b3fa00ff7699f23e6e4e0c8db8bc78d4b8135`, main exactly `87f87e0a454db86bcdf67569fa1e6ab2061ee46c`, all six previous checks green. Use a clean **isolated worktree** and preserve user primary-worktree modifications. If base/branch drift or unrelated edits exist, STOP and report; do not reset or force-push away work.
2. Read `docs/codex/CODEX_PHASE_PROMPTS/P11_D_SYNTHETIC_DETACHED_EVIDENCE_AND_UNCONFIRMED_CANDIDATE_CONTRACTS.md`, `docs/15_DOCUMENT_AI_OCR_SPEC.md` §§2,5–8, P11 readiness gate review, actual P11-B `contracts.py`, P11-C classification/registry, P11-D candidates/evidence and their tests. Keep the fix narrowly targeted; prefer helpers only where necessary.
3. **Allowed changed paths only:**
   - `backend/app/modules/documents/evidence.py`
   - `backend/app/modules/documents/candidates.py`
   - `backend/tests/test_document_candidate_evidence.py`
   - `backend/tests/test_document_candidate_contracts.py`
   - `backend/tests/test_document_candidate_boundaries.py` only for justified new boundary evidence
   - `docs/codex/CODEX_PHASE_PROMPTS/P11_D_REVIEW_FIX_01_STRUCTURAL_RESULT_INVARIANTS_AND_UTC_GUARD.md` (track this exact instruction)
   - `docs/implementation/38_PROGRESS_TRACKER.md` **only** if strictly correcting already misleading technical wording, never live gate/status inflation.
4. **Forbidden:** modifying P11-A/B/C production contracts or interfaces, touching text-bearing OCR content, adding clinical values, medication/lab/diagnosis extraction, source read/preview, patient identifiers/actual documents, API/BFF/UI, ORM/migrations/outbox, production worker/provider/model, runtime module registration, filesystem/network/egress, dependency or lockfile changes, CI/security threshold changes, any P5/P7/P8/P9/P10 activation, and any live approval statement. Preserve `NOOP_ABSTAIN`/`ENGINEERING_ONLY` and `UNCONFIRMED`/`ABSTAINED` semantics.
5. Strict adversarial runtime types **before** hashing, membership, sorting, geometry/numeric arithmetic or nested traversal; bounded snapshots, no recursive/unbounded traversals. Typed content-free errors and privacy-canary nonleakage. An allowed failed/partial case must not become positive. Maintain permutation/order determinism and avoid any `TextBlock.text` access; assert this with the existing exploding-text fixture.
6. Run focused P11-D and P11-A/B/C tests, P7–P10 regressions, full backend pytest/Ruff/strict mypy/compile, real PostgreSQL integration plus Alembic migration recovery at `p7a_0007`; frontend format/lint/typecheck/145+ tests and three production builds; Docker build/health/non-root/migration, Playwright Chromium (disclose retries), Gitleaks, and Trivy filesystem/image scans. No skip/threshold weakening. `git diff --check`, approved path allowlist and privacy/governance audit.
7. Push the **same branch** and update **existing PR #35**. Independently confirm final local SHA = remote SHA = PR head and that all six named CI jobs are **SUCCESS on the NEW exact final head**: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. Do not reuse checks from reviewed old SHA. **DO NOT MERGE**. Return for independent re-review.

### Required completion report

```text
STATUS: COMPLETE SAFE ENGINEERING REPAIR / BLOCKED
PR: #35 — OPEN, NOT MERGED
FINAL LOCAL SHA:
FINAL REMOTE SHA:
FINDING 1 — text-blind structural result integrity at verification entry:
FINDING 2 — timezone-aware UTC enforcement on candidate:
P11-D FOCUSED / P11-A+B+C / P7-P10 / FULL BACKEND / DB / FRONTEND / PLAYWRIGHT:
CI RUN ID / EXACT FINAL HEAD SHA / SIX JOB CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCIES / LOCKFILES / CHANGED PATHS:
NO TextBlock.text ACCESS / NO SOURCE OR CLINICAL AUTHORITY:
P11 LIVE GATES: 0/9 APPROVED, 5 OPEN, 4 BLOCKED
P8-C / P9-C / P10 LIVE RESTRICTIONS:
MERGED: NO
```

**Stop after reporting.** No live P11 medical extraction or source/clinical review is unlocked by these synthetic contracts.
