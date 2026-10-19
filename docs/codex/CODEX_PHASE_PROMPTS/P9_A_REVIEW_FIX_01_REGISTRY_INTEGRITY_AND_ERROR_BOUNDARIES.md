# SwasthyaSetu AI — P9-A Review Fix 01: Registry Integrity and Safe Lookup Boundaries

**Work unit:** Narrow independent-review repairs to **P9-A only**, not P9-B/P9-C.
**Repo:** `Itsbhavesh1101/swasthyasetu_ai`
**Existing PR:** #26 — `https://github.com/Itsbhavesh1101/swasthyasetu_ai/pull/26`
**Existing branch:** `phase/p9-a-safety-decision-types-policy-registry`
**Independently reviewed SHA:** `6dd860d58e2b036d245f32857c4f7a68a199d7ba`
**Base main:** `9a6f5b1190909ab90aa7c0cc87a160a851d84763`
**Verified remote CI:** `39240292695` — all six required jobs successful on the reviewed SHA.
**Alembic:** `p7a_0007` — must remain unchanged.
**Merge:** **DO NOT MERGE** before a new independent review.

## Mission and confirmed review issues

The new `safety` module is correctly detached, metadata-only, engineering-only, and not publicly activated. Preserve those boundaries. The issues below are **uncovered negative paths**, not claims that existing CI is failing or that real patient safety routing is active.

### Finding 1 — Registered/selected policy metadata is not revalidated when read (registry integrity)

**File:** `backend/app/modules/safety/policies.py`, `SafetyPolicyRegistry.require` and `get_active_policy`.

`SafetyPolicyRegistry.__init__` revalidates metadata once, but `_policies` and `_selections` retain references to `SafetyPolicyMetadata` objects supplied by the caller. Although the dataclass is frozen, `object.__setattr__` can change the referenced instance after registration. The existing test `test_registry_revalidates_a_tampered_metadata_instance` only covers **tampering before registry construction**, not tampering **after registration**. `get_active_policy` currently checks activation/approval/environment fields but **does not check the metadata checksum or registration identity again**. It can return a mutated policy ID/version/namespace/checksum as if it were the originally selected policy; `require` can likewise hand back tampered registered metadata.

**Required:** Make registry reads fail closed on post-registration mutation (or defensively snapshot metadata so a caller cannot affect registered entries), including exact registered-key/selected-identity invariants and checksum validation. Avoid introducing mutable caches or dynamic policy loading. Keep the protected-environment block and default-empty behavior unchanged. Treat checksum strictly as a metadata integrity check, **not clinical approval or cryptographic authorization**. Error messages must be content-free and typed.

**Regression:** register a selected engineering metadata instance; mutate its version or namespace via `object.__setattr__` *after* registry creation (test-only adversarial simulation); assert that active selection **cannot** return the tampered metadata (either typed rejection or original intact snapshot). Do the equivalent for `require`. Verify no protected environment can select the synthetic policy, no low-risk fallback, and both normal `LOCAL/TEST` selections still work. If choosing defensive copies, ensure mutable caller references cannot modify registry state and returned references do not compromise later reads.

### Finding 2 — Failed `require` lookup chains the caller-controlled policy identity into an exception cause (error privacy)

**File:** `backend/app/modules/safety/policies.py`, `SafetyPolicyRegistry.require`.

Current logic uses `try: self._policies[(policy_id, policy_version)]` then `except KeyError as exc: raise UnknownPolicyError("unknown policy identity") from exc`. This creates an exception chain with a `KeyError` containing the **raw submitted key tuple**. A logger printing the traceback of an `UnknownPolicyError` can therefore expose an arbitrary caller-provided, potentially sensitive string in a supposedly content-free failure boundary.

**Required:** Resolve unknown keys without preserving raw caller-controlled lookup content in chained exceptions (e.g. use `.get` + explicit typed error). Bound and validate caller-supplied IDs/versions consistently. Avoid interpolating values into errors, logging, spans, or audit messages. Do not change expected typed `UnknownPolicyError` for a valid but unknown identity.

**Regression:** invoke `require` with an adversarial synthetic privacy canary (`policy_id` contains a marker) and assert that no canary is present in the rendered traceback/exception cause, not only `str(error)`. Test malformed/overlong lookup inputs return safe typed failures; ordinary unknown well-formed IDs still return `UnknownPolicyError` without raw details. Retain legitimate inactive-policy metadata audit lookup if intended by design.

### Finding 3 — Active selection ID/version fields are not length-bounded

**File:** `backend/app/modules/safety/policies.py`, `ActivePolicySelection.__post_init__`.

`SafetyPolicyMetadata` bounds `policy_id` to 128 characters and `policy_version` to 64, but `ActivePolicySelection` only checks regexes without imposing the same maxima. Thus arbitrarily large syntactically matching selection values are constructible, contrary to P9-A's stated strict bounded metadata contracts, and later passed to registry lookup.

**Required:** Mirror the canonical policy ID/version length constraints in selection construction and related external lookup boundaries. Preserve current ASCII-only machine syntax and typed, content-free errors. Add boundary tests for exact maximum and maximum+1, including large otherwise syntactically valid inputs.

### Minor consistency update (non-blocking)

`docs/implementation/38_PROGRESS_TRACKER.md` still lists `08_SAFETY_AND_TRIAGE_POLICY.md` as `NOT STARTED` under *Before P9*, although this PR adds a **draft** file. Adjust that row to identify `DRAFT — NOT CLINICALLY APPROVED / real clinical rules NOT STARTED`, without suggesting clinical sign-off or P9 macro completion. If the final CI SHA differs from the tracker, record accurate CI evidence without retroactively pretending approvals occurred.

## Required preflight, scope and tests

1. Verify branch and clean worktree; inspect actual latest PR diff and canonical sources (`docs/08_SAFETY_AND_TRIAGE_POLICY.md`, `docs/00_PROJECT_MASTER_SPEC.md`, `docs/34_MASTER_IMPLEMENTATION_PLAN.md`, `docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md`, original P9-A prompt, `backend/app/modules/safety/{domain,policies}.py`, the two safety test files). If branch moved, reconcile rather than overwrite.
2. Fix only `backend/app/modules/safety/policies.py` and narrowly relevant safety tests, plus `38_PROGRESS_TRACKER.md` and this prompt file. Add no patient signal extraction, evaluator, clinical rules, new route, P9-B/C, migration, API, UI/BFF, external provider/egress, policy activation, new dependency, CI change, or P8-C patient-facing AI work.
3. Preserve five exact `SafetyRoute` values; empty-default registry, explicit synthetic policy, `LOCAL/TEST` selection only, protected-env rejection; typed content-free failure classes; checksums are **not** clinician approval.
4. Run P9-A focused regressions plus full network-free backend, 97 existing real PostgreSQL integration tests (or verified current actual count), Ruff format/lint, strict mypy, import/compile, `git diff --check`, frontend checks/build/tests, Docker/PostgreSQL migration/health, Playwright, security scan, zero-egress/privacy/architecture checks. Do not weaken other tests.
5. Push changes to **existing branch and PR #26** only. Verify all six GitHub Actions jobs on the **new exact final SHA**: Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, Security scans. Leave PR open and unmerged.

**Final concise report:** STATUS; branch; final local/remote SHA; PR #26; finding 1/2/3 and tracker correction; focused/backend/PostgreSQL/frontend/Playwright counts; new CI run ID and six conclusions; Alembic/dependencies; preserved P8-C and clinical approvals; unrelated changes; `MERGED: NO`.

**Stop after push and CI. Do not merge.**
