# SwasthyaSetu AI — P8-A Review Fix 01: Fail-Closed Provider Results and Total Deadline

**Work unit:** Focused review repair of **P8-A only**, **not P8-B/P8-C**.
**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Existing branch:** `phase/p8-a-ai-orchestration-provider-ports`
**Existing PR:** #23 — `https://github.com/Itsbhavesh1101/swasthyasetu_ai/pull/23`
**Reviewed branch head:** `47a6010c5bb48b4528ca822c094f153aecdec7ce`
**Base main:** `b510e502f58fbd964f3011f25616a03425c7c347`
**Current Alembic head:** `p7a_0007` — **must remain unchanged**.
**Review evidence:** GitHub Actions run `39155610573` completed successfully with all six required jobs. Passing CI is not proof that the untested negative paths below are safe.

## 1. Mission

Fix the three independently verified resilience gaps below in the P8-A orchestration implementation. Preserve the already correct provider-neutral contracts, explicit fake/disabled composition, privacy-safe telemetry, deadline/retry budget and all P1–P7 behaviors. Keep the repair narrowly scoped; **do not merge** and do not start P8-B.

### Finding 1 — Malformed provider *return value* escapes the typed failure boundary

**Verified location:** `backend/app/modules/ai_orchestration/application.py`, `AIOrchestrationService.generate_structured`, approximately lines 119–141 and `_result_matches` at lines 235–256.

The provider await is protected by a `try/except`, but the post-return `_result_matches(attempted_request, result)` runs in the `else` block and assumes `result` is a `StructuredLLMResult`. A misbehaving adapter returning `None`, a `dict`, or a structurally malformed object will raise `AttributeError` / another exception *outside* the exception-normalization boundary instead of yielding a typed, nonretryable `LLM_SCHEMA_INVALID` outcome. The gateway is supposed to isolate malformed provider responses and prevent raw exceptions from reaching tasks.

**Required:** Validate the runtime result type/contract before dereferencing its fields. Return a typed, nonretryable `SCHEMA_INVALID` when the adapter returns the wrong type/invalid structure or wrong request/provider/provenance correlation. Do not leak provider raw objects, their repr, or exception messages. If a property-access/comparison error is possible from unexpected provider return types, contain it rather than leaking it. Preserve legitimate results exactly and do not invent a candidate or modify the domain schema.

### Finding 2 — Contract validation errors thrown *inside* adapters are misclassified

**Verified location:** `backend/app/modules/ai_orchestration/application.py`, approximately lines 102–118.

The `except Exception` maps all non-`ProviderFailure` errors to `LLM_UNKNOWN`, including `ContractValidationError` raised by `StructuredLLMResult.from_dict(...)` or generic structural parsing/contract enforcement during adapter execution. Such errors are deterministic schema/contract failures and the canonical P8-A specification explicitly requires malformed structured output to be rejected without infrastructure retry.

**Required:** Catch the project-owned `ContractValidationError` separately and return typed, **nonretryable** `SCHEMA_INVALID`, with the correct completed-attempt count. Do not expose `str(error)` or original values through outcome, exception repr, spans, metrics or logs. Keep genuinely unknown provider exceptions mapped to `UNKNOWN` without retry. Continue mapping explicitly raised `ProviderFailure` to its closed category.

### Finding 3 — Backoff/sleeper is outside the total-deadline and exception boundary

**Verified location:** `backend/app/modules/ai_orchestration/application.py`, approximately lines 143–173, especially the unguarded `await self._sleeper(delay)`.

Individual provider calls are protected by `asyncio.wait_for(..., timeout=remaining)`, but the retry sleeper is not. A slow/stuck injected sleeper can wait indefinitely after a retryable failure even though the request's total deadline has expired. A sleeper throwing an unexpected exception also escapes the normalized failure boundary. The canonical contract requires **one total deadline covering attempts, retry delays and validation**; no uncaught provider/dependency errors or silent retry outside the budget.

**Required:** Bound the backoff await by the **remaining total deadline**, with safe, nonretryable `TIMEOUT` on expiry (not a new attempt), and normalize unexpected sleeper errors to a safe closed nonretryable failure such as `UNKNOWN`. Preserve cancellation (`asyncio.CancelledError` must propagate), the bounded retry count/delay, Retry-After semantics, and injected test clock/sleeper compatibility. Check deadline before and after sleeping. Avoid clock-based busy loops and unbounded waits. Do not introduce dependencies or change documented engineering limits.

## 2. Mandatory inspection / authority

Before coding, verify exact current PR branch head and clean worktree; if the branch has moved, inspect its updated diff and reconcile findings, do not clobber other work. Read:

- `docs/13_AI_ORCHESTRATION_SPEC.md` — provider contract, sections 4–9; total-deadline and fail-closed rules.
- `docs/30_TESTING_STRATEGY.md` — P8-A contract/deadline/retry/failure matrix.
- `docs/33_ERROR_HANDLING_POLICY.md` — sections on typed failures, no-retry, no content leakage.
- `docs/26_PRIVACY_CONSENT_SPEC.md` — patient-data/telemetry prohibitions.
- `docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md` — AC-P8-001/002, portions of 004/005/006.
- `docs/implementation/38_PROGRESS_TRACKER.md`, R3 dependency policy, Codex workflow/context rules.
- `backend/app/modules/ai_orchestration/{application,contracts,providers,public,telemetry}.py`
- `backend/app/adapters/ai/{fake,disabled}.py`
- `backend/tests/{test_ai_orchestration,test_ai_contracts,test_ai_registration_privacy}.py`

The reviewed SHA and line numbers identify evidence, not permission to apply blind patches. Use actual current source contracts; keep fixes simple, explicit and strongly typed.

## 3. Required focused regression tests

Add/extend synthetic, network-free tests under existing `backend/tests/test_ai_orchestration.py` and only other directly relevant test files if needed:

1. Provider returns `None` or a `dict` instead of `StructuredLLMResult`: returns `OrchestrationOutcome.failure` with `LLM_SCHEMA_INVALID`, **does not raise**, **does not retry**, attempt_count=1; no raw result content in outcomes or telemetry.
2. Provider returns mismatched prompt/schema/request/provider/provenance or invalid expected type: reject nonretryably without an accidental `AttributeError`; retain existing version-mismatch regression tests.
3. Provider adapter throws `ContractValidationError` during strict result deserialization: typed `LLM_SCHEMA_INVALID`, **not** `LLM_UNKNOWN`, no retries even with retry_budget>0, no raw content in returned/logged error.
4. Provider throws unexpected exception with a synthetic PHI canary: still typed nonretryable `LLM_UNKNOWN`, canary never exposed.
5. Retryable failure followed by a blocking sleeper (`await asyncio.Event().wait()`) with a short real/injected controlled deadline: call terminates within a conservative test bound as typed `LLM_TIMEOUT`; no second provider attempt, no hanging test.
6. Sleeper throws a synthetic exception: safe, typed, nonretryable failure, correct attempt count and canary redaction.
7. Cancellation during backoff: `CancelledError` propagates, with no additional provider attempt and no fabricated result.
8. Existing deterministic retries using the `ControlledClock.sleep` fake continue to pass, including bounded delay, total deadline, retry budget, Retry-After limit, request metadata stability and successful valid response.
9. Assert telemetry remains optional, has no patient text/secret or source IDs, and cannot mutate behavior.

Do not relax existing tests or assert an exact timeout that is too tight for CI. Avoid external network, real patients, real models, or billable APIs.

## 4. Scope, quality, and handoff

**Expected files:** primarily `backend/app/modules/ai_orchestration/application.py`, `backend/tests/test_ai_orchestration.py`, and a narrow tracker/prompt implementation record. Another AI-orchestration file may change only if needed to satisfy a verified finding; justify it in the final report.

**Forbidden:** new provider/model/SDK, new services or network egress, P8-B prompt/extraction rules, P8-C messages/API/browser work, P9 clinical safety logic, consent/auth policy changes, clinical fact promotion, new tables/migrations, dependency/lockfile changes, changes to P7 routes or patient web, weakening CI or tests.

Run focused tests and complete backend tests, Ruff, mypy, compile/import, `git diff --check`, migration head check, privacy/architecture regression; push changes to the **existing** PR #23 and verify all six remote CI jobs succeed **at the new final SHA**. Keep the existing main baseline; no merge.

After completing, update the progress tracker truthfully with the review-fix evidence (CI pending vs passed); keep P8-A subject to independent review, P8-B/C not started, external-provider/clinical/privacy approvals pending.

**Final report (short):** STATUS; BRANCH; FINAL LOCAL SHA; REMOTE SHA; PR #23; 3 FINDINGS FIXED; TEST COUNTS; CI RUN ID AND ALL SIX CONCLUSIONS; ALEMBIC; UNRELATED CHANGES; MERGED: NO.

**Stop after pushing the PR update. Do not merge.**
