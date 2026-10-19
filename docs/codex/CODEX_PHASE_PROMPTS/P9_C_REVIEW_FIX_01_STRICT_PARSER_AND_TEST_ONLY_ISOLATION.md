# SwasthyaSetu AI — P9-C Review Fix 01: Strict Presentation Parsing & Test-Only Isolation

**Work unit:** Narrow review repair of PR #28 **only**. Do not start Stage 3, P10, clinical policy work, runtime safety integration, or patient AI.

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Branch:** `phase/p9-c-guarded-safety-result-presentation`
**Existing PR:** #28 — https://github.com/Itsbhavesh1101/swasthyasetu_ai/pull/28
**Reviewed head SHA:** `37863d2efeebd87860728d6609d04f7416ee6489`
**Base main SHA:** `541fa9033349162c4bf1abb5d6cdfe7a6cd8d6fd`
**Reviewed CI:** `39277501254` — all six jobs green at the exact reviewed head.
**Alembic:** `p7a_0007`, must remain unchanged.
**Status:** REVIEW FIX REQUIRED, DO NOT MERGE until independent re-review.

## Review conclusion

The clinical approval matrix is honest, the new public routes are unchanged, and the frontend projector refuses protected/unknown environments before reading an untrusted decision. The React preview is not presently imported into an application route. However, the parser does **not** fully enforce its claimed exact and bounded input invariants, and the synthetic presentation component is callable without passing through that parser or its environment gate. Repair these narrowly without introducing clinical activation.

## Finding 1 — Sparse arrays can pass the machine reason-code validator (required)

**File:** `apps/patient-web/lib/safety/presentation.ts`; function `isReasonCodes()`.

The current checks rely on `Array.prototype.some` and `Array.prototype.every`. Both skip *holes*. For a single-element sparse array, `new Array(1)`, `.some(...)` returns `false`, `new Set(value).size === value.length` is `true`, and `.every(...)` returns `true`. The parser therefore accepts an unpopulated reason array, then spreads it into `[undefined]` inside a purportedly frozen, machine-code-only `synthetic_decision.reason_codes`. This violates the explicit requirement that every reason is a valid bounded `SYNTHETIC_` token.

**Fix:** Explicitly require every integer index `0..length-1` to be an **own** array element, and validate every element, its type, namespace, length, sorted order and uniqueness. Preserve 1..16 bound and frozen detached output; reject holes without filling or silently normalizing them. Avoid invoking side-effectful arbitrary callbacks from untrusted values. Ensure invalid data maps to existing content-free `DEGRADED` response rather than throwing or authorizing any state.

**Regression:** A length-one hole (`Array(1)`), a sparse multi-element array (including a leading/trailing hole), `undefined` or `null` element, invalid string, array over 16, duplicated/unsorted elements; assert all degrade, never contain `undefined` in an accepted preview, and never echo canaries. Preserve genuine P9-B synthetic positive cases and the protected-environment before-read check.

## Finding 2 — Hidden properties bypass the exact-key allowlist (required)

**File:** `apps/patient-web/lib/safety/presentation.ts`; `hasExactKeys()`.

`Object.keys` enumerates only enumerable string keys. An untrusted decision with exactly seven expected enumerable keys **plus** a non-enumerable `patient_id` or a symbol-keyed `source_evidence` passes `hasExactKeys` even though the contract claims to reject extra/source/PHI properties. The current output reconstruction doesn't copy those hidden fields, but the strict allowlist itself is incorrect.

**Fix:** Enforce exact **own-key** shape via `Reflect.ownKeys` (or equivalent) including symbols and non-enumerable keys; only the seven documented string keys are allowed. Do not access or serialize rejected extra-property values. Preserve catch-to-`DEGRADED` and zero-content responses for hostile proxy/getter input.

**Regression:** `Object.defineProperty(decision, 'patient_id', { enumerable: false, value: 'privacy-canary' })`, an extra symbol property, and getters that throw. Assert no hidden/symbol property is accepted or echoed. Preserve valid plain-object inputs.

## Finding 3 — Synthetic component is bypassable by forged props (required test-only hardening)

**File:** `apps/patient-web/components/safety/synthetic-safety-preview.tsx`.

`SyntheticSafetyPreview` takes a structurally constructible `SafetyPresentationState`, and renders `ENGINEERING_SYNTHETIC_PREVIEW` **without** calling the parser or checking the environment. A future accidental direct import/mount, or a unit test passing forged props, can display arbitrary reason text and the machine `EMERGENCY`/`SUPPORTED_SELF_CARE` token outside the projector's gate. This is *not an active patient route today*, but weakens the intended engineering-only architecture.

**Preferred repair:** Move this disconnected preview from the production `components/` tree into a clearly test-only helper under `apps/patient-web/tests/` (or an equivalent Vitest-only support directory that is never imported by routes/runtime). Update unit-test imports and backend architecture assertions accordingly. Keep the pure `lib/safety/presentation.ts` projector available for contract tests, but do **not** create a route, public component export, BFF, endpoint, React page, button, source of data, or environment config switch. Add a static test proving no `app/**`, production `components/**`, BFF or application entrypoint imports the test-only preview. Alternatively, if moving the component has a documented compelling reason not to work, enforce an equally strong **non-runtime** isolation boundary without relying merely on an easily forged client-supplied `environment` string; state evidence in the final report.

**Regression:** Forged preview state with `reason_codes: ['privacy-canary']` cannot enter any actual app route or production import graph; standalone valid projector->test preview and unavailable/degraded render tests remain passing. Do not conflate TypeScript static `Readonly` with runtime validation.

## Finding 4 — Calendar-invalid UTC timestamps may pass freshness (required)

**File:** `apps/patient-web/lib/safety/presentation.ts`; `isValidTimestamp()`.

The timestamp regex enforces `Z` syntax, but JavaScript `Date.parse('2026-02-30T12:00:00Z')` normalizes it into March 2 rather than rejecting an impossible calendar date. With a corresponding `observedAt`, the current age comparison can therefore accept a malformed source timestamp.

**Fix:** Require canonical valid UTC calendar instants (e.g., strict parse/round-trip checking against the input precision), while retaining explicitly supported precision formats and a 0..60,000 ms freshness window. Preserve explicit UTC `Z` and fail-closed `DEGRADED` behavior. Reject February 30, invalid leap-day and invalid time components; test both supported normal precisions.

## Scope/verification

1. Verify clean branch and exact PR head before editing; don't reset/discard work. Read the current P9-C prompt, gate review, P9-A/B contracts and frontend/browser architecture. If head/base has drifted, reconcile first.
2. Change only `presentation.ts`, focused P9-C frontend tests, the location of the test-only preview and its imports, the narrow backend static isolation test and repository-tree documentation if those paths move. Maintain the Stage 3 approval matrix and truthful phase statuses; update only if necessary. Include this repair prompt in `docs/codex/CODEX_PHASE_PROMPTS/`.
3. **Do not add** clinical policy/symptoms/thresholds/triage, patient safety assessment, live API/BFF/results route, persistence/migration, medical copy, external egress, runtime activation, self-care permission, dependencies, altered CI, or P7/P8-C changes. `/results` remains unavailable; `/urgent-help` stays generic. Preserve P9 `PARTIAL`, P8-C `PARTIAL`, and all governance approvals `OPEN`.
4. Re-run P9-A/B (127 focused safety tests), full backend and real PostgreSQL suites, frontend format/lint/typecheck/tests/builds, Playwright, Docker/migrations/non-root/health, Ruff, mypy, security scans, privacy/PWA/no-route/no-table checks and `git diff --check`. Document any real flaky retries without weakening coverage. All six GitHub Actions jobs must succeed on the **new final remote SHA**.
5. Push to the **existing** `phase/p9-c-guarded-safety-result-presentation` branch and existing PR #28. **DO NOT MERGE.** Return final local/remote SHA, four findings+regressions, new test counts, new CI run ID and six job conclusions, Alembic head, scope/governance blockers and `MERGED: NO`. Stop for independent review.
