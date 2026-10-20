# SwasthyaSetu AI — P11-A Review Fix 01: Lifecycle Provenance, Revalidation and Idempotency

**Independent review decision: REVIEW FIX REQUIRED.** Continue on **existing PR #34** (`phase/p11-a-synthetic-document-domain`); **DO NOT MERGE** until the new exact SHA is independently reviewed.

| Item | Verified value |
| --- | --- |
| Repository | `Itsbhavesh1101/swasthyasetu_ai` |
| Baseline main | `d3c2125ebdb2c927f254b913a890b411ccc971e5` |
| Reviewed PR head | `e012a10460d785f829ff37ee0a004e67cb84d6b8` |
| Reviewed CI run | `39396955656`, six required jobs SUCCESS at exact head |
| Alembic | `p7a_0007`; unchanged required |
| Live P11 gates | 0/9 APPROVED; 5 OPEN; 4 BLOCKED |

This is a **synthetic-only contract-integrity repair**, not production file ingestion authorization. No actual document/patient bytes or operational systems may be activated.

## Finding 1 — Direct state construction bypasses explicit synthetic validation

**File:** `backend/app/modules/documents/domain.py` — `SyntheticDocumentState.__post_init__`, `transition`, `create_synthetic_document_state`.

**Observed:** The frozen state constructor checks field coherence but does not establish its lifecycle provenance. A caller can create the initial uploaded state and call `dataclasses.replace(uploaded, status=DocumentStatus.ACCEPTED)`. With empty attempts and equal descriptor/generation, this satisfies current `__post_init__` even though there was **no** `UPLOADED -> VALIDATING -> ACCEPTED` sequence and **no** `SyntheticValidationDecision`. The forged state then permits `ACCEPTED -> QUEUED` with a new attempt. Similarly, direct construction can forge plausible `SUCCEEDED` or `FAILED` states by arranging compatible fields. This contradicts the P11-A promise that synthetic acceptance only follows an explicit test decision and that direct constructors cannot bypass state guards.

**Required:** Ensure the only supported way to obtain an advanceable, valid synthetic lifecycle state is `create_synthetic_document_state()` followed by guarded `transition()` operations. Prevent an arbitrary public constructor/`replace()` from manufacturing a later status without its required simulated decision/history. Design a small **internal-only construction mechanism, verified immutable transition lineage, or equivalent constrained factory** consistent with repository conventions. Do not pretend this is an authorization token, cryptographic attestation, durable audit log, or protection against arbitrary Python introspection; the goal is correct, fail-closed API invariants for ordinary and adversarial caller-held objects. Keep all canonical state edges and the existing public function semantics usable. If factory-only construction is necessary, make the intended serializable/restoration boundary explicit and leave DB hydration for future approved P11-A work.

**Tests:** `replace(initial, status=ACCEPTED)` rejected; direct forged state with `state_version=3` and no validation history rejected; manufactured `SUCCEEDED/FAILED/PROCESSING` with a syntactically coherent attempt list rejected; legitimate complete simulation `UPLOADED -> VALIDATING -> ACCEPTED -> QUEUED -> PROCESSING -> SUCCEEDED -> QUEUED` succeeds with explicit decisions/new attempt; `REJECTED` terminal. No scanner/real upload claim.

## Finding 2 — Caller-held state/validation decision is not revalidated at transition entry

**File:** `backend/app/modules/documents/domain.py` — `SyntheticDocumentState.transition` and `_validate_decision`.

**Observed:** `transition()` operates directly on `self` without checking whether the previously frozen fields were mutated using `object.__setattr__`. For example, set `initial.status=ACCEPTED` after factory construction, then request `QUEUED`, bypassing validation. For the simulation decision, checks use `decision.decided_at > occurred` and `< self.occurred_at` without revalidating its current timestamp/type. Mutating `decided_at` to a list can trigger raw `TypeError` instead of `DocumentDomainError`. The decision was valid **when constructed**, not necessarily at use.

**Required:** Revalidate/detach the complete current state at the transition entry *before* checking its status, version, attempt tuples or provenance. Do not rely on frozen annotations or `type(...)` alone; validate nested source/owner/opaque ID fields, chronology, generation, status and any provenance/lineage guard introduced for Finding 1. Reconstruct/detach and revalidate a supplied `SyntheticValidationDecision` before comparing datetime/enum/identity fields. Reject mutated source/owner/version/disposition/decided_at fields and malformed/unhashable values with fixed, content-free `DocumentDomainError`, not raw `TypeError`/`AttributeError` or leaked canaries. Do not allow the regenerated snapshot to heal an invalid transition or silently infer approval.

**Tests:** Mutate a legitimate `UPLOADED`/`VALIDATING` state with `object.__setattr__` (status, state_version, current ID, nested descriptor/source where practical) and verify no advance to `ACCEPTED/QUEUED`; mutate previously valid decision timestamp to a list/naive datetime, mutate nested scope/version/disposition to unsupported forms, and assert closed typed errors and no canary in formatted exceptions. Include valid control cases in both caller orders.

## Finding 3 — Same-document, different-idempotency-key is incorrectly classified as DISTINCT

**File:** `backend/app/modules/documents/ingestion.py` — `compare_owner_scoped_idempotency`.

**Observed:** After confirming the same synthetic owner scope, the comparator immediately returns `DISTINCT` whenever idempotency keys differ—even if the **same `document_id`** is supplied on both sides. This permits a single document identity to appear as two distinct independent requests purely by changing a key. The canonical Spec 15 §3.3 requires same-document concurrency with different keys to be **rejected or serialized** under a future policy; this synthetic-only comparator cannot authorize a separate attempt.

**Required:** For two supplied descriptors of the **same owner and same document ID**, return `CONFLICT` for different idempotency keys, never `DISTINCT`. Keep `MATCH` only for identical owner, key, document identity, and metadata; same key but incompatible source/version/digest/claims remains `CONFLICT`. Reserve `DISTINCT` for genuinely separate document identities with distinct keys within one owner, and keep `OWNER_SCOPE_MISMATCH` across owners before any digest comparison. Treat this as a pure comparison outcome, not a durable concurrency/lookup guarantee. No new cache, state, persistence or cross-owner probing.

**Tests:** Same owner+document ID+differing keys => `CONFLICT` in both argument orders; same owner+different IDs+different keys => `DISTINCT`; same key+different IDs => `CONFLICT`; same owner+same ID/key+one changed claim => `CONFLICT`; exact equality => `MATCH`; cross owner+same SHA => `OWNER_SCOPE_MISMATCH`. Preserve existing tests and report any documented semantic disagreement explicitly rather than silently relaxing the requirement.

## Scope and execution controls

1. Verify clean **isolated worktree**, exact baseline/main, PR #34 head `e012a10460d785f829ff37ee0a004e67cb84d6b8`, approved previous review scope and six passing jobs. Do not discard primary worktree modifications; STOP for drift or merge.
2. Read tracked phase prompt `docs/codex/CODEX_PHASE_PROMPTS/P11_A_SYNTHETIC_DOCUMENT_LIFECYCLE_AND_INGESTION_GUARDS.md`, `docs/15_DOCUMENT_AI_OCR_SPEC.md` §3.3/§4.5, P11 readiness gate, and the current domain/ingestion implementation and tests. Implement narrow fixes; avoid needless new machinery.
3. **Allowed paths only:** `backend/app/modules/documents/domain.py`; `backend/app/modules/documents/ingestion.py`; `backend/tests/test_document_domain.py`; `backend/tests/test_document_ingestion.py`; `backend/tests/test_document_ingestion_boundaries.py` only if necessary; and `docs/codex/CODEX_PHASE_PROMPTS/P11_A_REVIEW_FIX_01_LIFECYCLE_PROOF_ENTRYPOINT_AND_IDEMPOTENCY.md` (commit this instruction). A concise tracker correction only if strictly required; do **not** change gate status.
4. Reject unbounded attempt arrays before iterating/hashing in any touched constructor as part of fail-closed state hardening (limit tied to `MAX_DOCUMENT_GENERATION`); do not increase unrelated scope.
5. **Forbidden:** real file/stream handling, upload route/API/BFF/UI, source preview, scanner/quarantine integration, storage read/write, ORM/table/migration, provider, OCR execution, processor runtime, job handler/scheduler, consent or clinician authority, P5/P7/P8/P9/P10 activation, new dependencies/locks, infrastructure/CI modifications, patient records, real medical data or external egress. P11 live gates remain **0 APPROVED, 5 OPEN, 4 BLOCKED**; P8-C/P9-C Stage 3 and P10 live remain blocked.
6. Run focused P11-A with added adversarial tests and unchanged P11-B/C regressions; P7–P10; full backend Ruff/format/strict mypy/pytest/compile; PostgreSQL + Alembic upgrade/check/downgrade recovery (`p7a_0007`); frontend format/lint/typecheck/145+ tests and three builds; Docker non-root/readiness; Playwright Chromium (disclose local retries); Gitleaks; Trivy filesystem and image. `git diff --check`, scope and privacy audit. Do not weaken skip/CI policies.
7. Push **existing branch** `phase/p11-a-synthetic-document-domain`, update **existing PR #34**. Verify final local and remote SHA identical, and all **six** GitHub Actions jobs (`Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`) SUCCESS **on the new exact final SHA**. DO NOT MERGE.

### Required completion report

```text
STATUS: COMPLETE SAFE ENGINEERING REPAIR / BLOCKED
PR: #34 — OPEN, NOT MERGED
FINAL LOCAL SHA:
FINAL REMOTE SHA:
FINDING 1 — lifecycle provenance/direct constructor bypass:
FINDING 2 — state/decision transition entry revalidation:
FINDING 3 — owner-scoped idempotency identity conflict:
FOCUSED P11-A / P11-B+C / FULL BACKEND / DB / FRONTEND / PLAYWRIGHT:
CI RUN ID / FINAL HEAD SHA / SIX JOB CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCIES / CHANGED PATHS:
P11 LIVE GATES: 0/9, 5 OPEN, 4 BLOCKED
P8-C / P9-C / P10 RESTRICTIONS:
MERGED: NO
```

**Stop for independent re-review.** No live P11 acceptance criterion is satisfied by this repair.
