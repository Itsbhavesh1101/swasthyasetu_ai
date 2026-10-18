# SwasthyaSetu AI — P7-C Review Fix 01: Intake Authority, Typed Controls & Required Regression Evidence

**Status:** REQUIRED BEFORE MERGE. Implement the narrow repair on existing PR #21; do not merge.

- Repo: `Itsbhavesh1101/swasthyasetu_ai`
- Branch: `phase/p7-c-intake-apis-patient-ui`
- Reviewed head: `a7e64c07a43cfedba8f1e5f43a222ce3325706c6`
- Base main: `476f7415de39320f9c5df5bb20c387a2f57a5e88`
- Existing CI run: `39077010935` (all six jobs green); passing CI does **not** establish the missing negative and concurrent scenarios.
- Alembic head must remain `p7a_0007`; no dependencies, new tables, expanded clinical content, QML, AI, or later-phase work.

## 0. Required approach

Read the merged canonical `docs/07_CLINICAL_INTAKE_SPEC.md`, `06_API_CONTRACTS.md`, `22_UX_AND_USER_FLOWS.md`, `23_PATIENT_APP_SPEC.md`, engineering standards, the original `P7_C_INTAKE_APIS_PATIENT_UI.md` prompt, P7-A lifecycle and P7-B question-ID review-fix prompts, and the **current PR #21 implementation and tests**. Check the remote branch and exact head first. Make changes **only** in the current P7-C branch, without merging or pulling P8 forward.

### Review findings tied to actual code

1. **Configured NUMBER questions cannot be successfully submitted through the patient form.** `apps/patient-web/components/intake/answer-control.tsx` displays `question.constraints.unit` as text for NUMBER but submits no `name="unit"` input; `intake-journey.tsx::answerBody()` sends `unit: null`; the existing server engine requires `answer.unit == NumericValidation.unit`. Render a server-derived hidden `unit` value for NUMBER when a unit is configured (no patient-editable arbitrary unit), preserve correct unitless operation, and add UI-to-request-payload-to-backend tests. Do not relax engine validation or change the existing canonical numeric contract. All eight answer types need actual submission-shape/validation tests, not only checks that controls render.

2. **An early known-question answer can bypass server-selected question order.** `backend/app/modules/clinical_intake/application.py::submit_answer()` builds a candidate containing the posted answer and passes it to the pure engine for type validation, but never checks that the question was the *currently server-selected* `NextQuestion`/`ClarificationRequired` or is an **already answered, legitimately editable** question. A client can submit a registered conditional/dependency-blocked question out of order. Re-evaluate **persisted pre-mutation state**; accept only the selected next/clarification question or a previously accepted eligible correction, with a safe typed rejection and zero writes otherwise. Check the candidate with the existing P7-B validator after this eligibility check. Add synthetic multi-question/conditional/dependency tests with a test-only registry; don't invent or activate medical content. Keep legitimate draft corrections and deterministic version/timestamp order working.

3. **Read-only completed-draft access is tied to writable encounter states.** `backend/app/modules/clinical_intake/api.py::_authorize_encounter()` rejects every encounter outside CREATED/IN_PROGRESS for both GET and mutations. Read of an existing COMPLETED intake should still work under the exact same **active session+consent**, including if its encounter was subsequently marked terminal, while START/ANSWER/COMPLETE must reject invalid encounter states. Split policy checks for read versus mutation, preserving rejection for wrong session, missing/withdrawn consent, patient-bound encounters and unsupported encounter types. Do not allow changes to a completed/abandoned intake. Add real HTTP/PostgreSQL regression test (can terminalize encounter via existing allowed transition after intake completion) and cross-session negative proof. If a higher-priority canonical spec explicitly prohibits this read, document the conflict and STOP instead of inventing policy.

4. **Persisted instance/pack integrity must be checked before saying `CompletionReady`.** `ClinicalIntakeService._result()` returns `CompletionReady` immediately for COMPLETED without validating associated persisted pack instances/versions; `complete_snapshot()` repeats that shortcut on retry. For authorized reads/retries, detect empty/duplicated/mismatched instance identities, wrong instance terminal statuses, and unresolvable/deactivated historical packs; return typed safe error rather than synthetic success. Preserve legitimate completed read/replay and pinned versions; do not upgrade historic packs to the current default. Do not change P7-A repository lifecycle protections.

5. **Missing acceptance evidence: concurrent and rollback behavior.** The added `backend/tests/integration/test_postgres_clinical_intake_api.py` contains two tests and a sequential happy path. It does not prove competing start requests, simultaneous answers on the same expected_version, rollback on injected answer/instance/aggregate write failure, or consent/session boundary rejection during continued access. Add **real PostgreSQL** regression tests, including true concurrent tasks/transactions and row counts before/after failures. Prove one intake and one set of instances per encounter on competing starts, exactly one accepted answer/version increment on competing writes, stale conflict with no partial answer/instance side effects, no partial rows after injected stage failures, and negative cross-session/withdrawn-consent/closed-session read+answer+complete. Do not replace these with mocked or sequential-only tests. If exact atomic revocation ordering across modules is architecturally unsupported, document the consistency boundary and test what is guaranteed, rather than claiming serializability.

6. **Strict BFF response validation should include sensitive nested data shapes.** `apps/patient-web/lib/intake/server.ts::validIntake()` checks the outer keys but barely validates nested `answers[].value`, `selected_option_ids`, `unit`, `response_disposition`, `engine_state`, or `current_question.constraints`; a malformed backend payload can be relayed as accepted and exposed to the browser. Narrowly validate the documented typed alternatives and consistency (including bounded text/numbers, arrays and enums), rejecting unexpected objects/extra properties; no raw invalid backend body echo. Keep existing response keys/accepted valid forms. Add negative BFF tests. Do not invent new backend API fields.

7. **Engineering-only content opt-in.** `backend/app/main.py` currently turns on the engineering questionnaire for **every** local/test run by environment alone. The governing prompt requires **explicit enablement limited to local/test**, never staging/pilot/production; add a configuration/flag opt-in with a fail-closed default and a strong environment AND opt-in gate. Update real local/test/Playwright fixtures, CI environment and docs explicitly so test journeys stay runnable; prove production/pilot/staging still return POLlCY_UNAVAILABLE even if opt-in is set, and local/test without opt-in remain unavailable. Do not claim clinical approval. If approved canonical config overrides this, STOP and report instead of guessing. (Use the exact existing ErrorCode spelling `POLICY_UNAVAILABLE`.)

## Tests / scope constraints

- Preserve all existing P1–P7 tests, typed capability public contracts, current six CI gates and existing branch history.
- Test actual **all 8** answer types through their request contract, including valid/invalid NUMBER unit, singleton SINGLE_CHOICE, BOOLEAN false, date, duration units, scale values, unknown/refusal/skip policy, wrong question/version, stale expected_version; use synthetic packs only in tests, no production questions added.
- For page flows verify no clinical data/bearer stored in browser persistent stores, no network retry on ambiguous POST, and PWA Cache Storage remains generic. Add only targeted browser tests that prove corrected behavior.
- Protect POST errors with canonical error envelope + `Cache-Control: no-store`; never echo submitted medical text, session token, internal exceptions, SQL diagnostics, or raw mismatched payloads.
- Update canonical docs only when needed to accurately reflect the final implemented policy; update P7-C progress tracker with actual verification/limitations.
- `ruff`, `mypy`, backend pytest, PostgreSQL integration, frontend tests/type/lint/build, Playwright Chromium, Docker, security and migration checks must pass. **Do not** modify CI to bypass tests.
- Keep existing PR #21 open, push remote head, do not merge, and stop after verification.

## Return only

```
STATUS: COMPLETE / PARTIAL / BLOCKED
BRANCH:
FINAL LOCAL SHA:
REMOTE SHA:
PR #21:
FIXES: (brief proof paths)
TESTS: backend / real PostgreSQL / frontend / Playwright
CI: run ID and results for all six jobs
ALEMBIC HEAD: p7a_0007
LIMITATIONS:
MERGED: NO
```

If any finding above cannot be reconciled with higher-priority canonical docs, report BLOCKED with file/line evidence instead of broadening scope or silently changing behavior.
