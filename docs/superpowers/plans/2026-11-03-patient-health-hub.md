# Patient Health Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a patient-only SwasthyaSetu product with persistent account access, longitudinal
medical history, a secure local document vault, the existing intake flow, and consented
Gemini/Google-grounded Ayurvedic and home-care education.

**Architecture:** Extend the existing FastAPI modular monolith and PostgreSQL schema. A new
`patient_accounts` module atomically composes PII-bearing local accounts with PII-free actors,
patients, and authenticated opaque sessions; existing patient/provenance contracts own history;
documents use the existing object-storage port; self-care uses a new provider-neutral guidance
port. The Next.js patient BFF keeps every bearer and provider secret server-side.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy async, PostgreSQL 16, Alembic, Argon2id,
`python-multipart`, Google GenAI SDK, Next.js 16, React 19, TypeScript, Vitest, Playwright, Docker
Compose.

**Spec:** `docs/superpowers/specs/2026-11-03-patient-health-hub-design.md`

## Global Constraints

- Patient-only product: no hospital, clinician, counsellor, or administrator account workflow.
- Mental-health diagnosis/screening is deferred and must not be activated by this plan.
- No autonomous diagnosis, prescription, dosage change, emergency replacement, or guaranteed cure.
- Browser credentials remain opaque, `HttpOnly`, `SameSite=Strict`, `Path=/`, and `Secure` outside
  loopback development.
- No session, medical record, document, or guidance content in browser persistence or service-worker
  caches.
- Every patient resource uses trusted self-subject authorization and non-enumerating denial.
- Patient history correction creates a superseding fact; confirmed history is never overwritten.
- Uploaded bytes go through `ObjectStoragePort`, never PostgreSQL or a public web directory.
- Gemini receives only the explicitly disclosed question after active `EXTERNAL_AI_PROCESSING`
  consent; it receives no name, email, history, timeline, or document.
- Gemini output is displayed only with allowed citations and deterministic safety guards.
- Provider calls are faked in automated tests; CI must not require external network or secrets.
- Alembic migrations run explicitly and never on API startup.
- Preserve existing P1-P24 tests and protected-environment fail-closed behavior.

## Review Focus

- Registration rollback: a duplicate email or downstream insert failure leaves no orphan actor,
  patient, role, session, or account (Task 3 PostgreSQL tests).
- Authentication ambiguity: unknown email, wrong password, disabled account, expired session, and
  malformed bearer expose the same bounded public failure where enumeration would otherwise occur
  (Tasks 3-4 HTTP tests).
- Cross-patient object access: guessed patient, fact, timeline, or document IDs always fail before
  existence/content disclosure (Tasks 6, 8, and 9 PostgreSQL/HTTP tests).
- Upload ambiguity: extension/MIME/signature mismatches, traversal names, empty files, oversized
  streams, and delete failures cannot create an advertised readable object (Tasks 8-9 tests).
- External-AI boundary: missing/revoked consent, unsupported query, timeout, uncited answer,
  disallowed source, unsafe copy, malformed annotations, and duplicate submit perform zero or one
  bounded provider calls and never display advice incorrectly (Tasks 10-11 tests).

---

### Task 1: Add locked runtime dependencies and settings

**Files:**
- Modify: `backend/pyproject.toml`
- Modify: `backend/uv.lock`
- Modify: `backend/app/config/sections.py`
- Modify: `backend/app/config/settings.py`
- Modify: `backend/tests/test_settings.py`
- Modify: `deployments/local/.env.example`
- Modify: `deployments/local/compose.yaml`

**Interfaces:**
- Produces: `PatientAccountSettings`, `PatientDocumentSettings`, and `GuidanceSettings` available
  through `Settings`.
- Produces: runtime dependencies for Argon2id, multipart parsing, and the official Google GenAI SDK.

- [ ] **Step 1: Write failing configuration tests**

Assert that authenticated-session TTL is bounded, document storage is disabled without an explicit
root, Gemini is disabled without a key/model, secret representations are redacted, and allowed
source domains reject URLs/paths/wildcards.

- [ ] **Step 2: Run the focused tests and verify failure**

Run: `py -m uv run pytest tests/test_settings.py -q` from `backend`  
Expected: FAIL because the new settings sections do not exist.

- [ ] **Step 3: Add the three dependencies and immutable settings sections**

Add only `argon2-cffi`, `python-multipart`, and `google-genai`. Define exact fields for authenticated
TTL, storage root/10 MiB limit, Gemini enabled/key/model/deadline, and an official-domain allowlist.
Expose environment variables through existing nested-settings conventions and local Compose.

- [ ] **Step 4: Lock and verify**

Run: `py -m uv lock --project backend`  
Run: `py -m uv run pytest tests/test_settings.py -q` from `backend`  
Expected: PASS.

- [ ] **Step 5: Commit**

```text
feat: configure patient product services
```

### Task 2: Create migration `patient_hub_0008`

**Files:**
- Create: `backend/migrations/versions/0008_patient_health_hub.py`
- Create: `backend/tests/integration/test_patient_hub_migration.py`
- Create: `backend/tests/test_patient_hub_schema.py`

**Interfaces:**
- Produces: `patient_accounts` and `patient_documents` tables exactly as specified by the design.
- Preserves: all P1-P7 schema and `p7a_0007` upgrade path.

- [ ] **Step 1: Add migration-shape tests**

Assert one head named `patient_hub_0008`, unique normalized email/actor/patient bindings, supported
account status constraint, indexed patient document ownership, unique object key/digest metadata,
UTC timestamps, and reversible downgrade limited to the two new tables.

- [ ] **Step 2: Verify the tests fail**

Run: `py -m uv run pytest tests/integration/test_patient_hub_migration.py tests/test_patient_hub_schema.py -q`
from `backend` with the configured PostgreSQL test URL.  
Expected: FAIL because revision `patient_hub_0008` is absent.

- [ ] **Step 3: Implement the migration**

Use explicit names for every FK, unique constraint, check constraint, and index. Do not modify old
revisions or create document byte columns.

- [ ] **Step 4: Verify clean and upgrade-from-head paths**

Run Alembic `upgrade head`, `current`, and `check` against a fresh database and a database first
stopped at `p7a_0007`.  
Expected: both reach `patient_hub_0008` with no drift.

- [ ] **Step 5: Commit**

```text
feat: add patient health hub schema
```

### Task 3: Implement atomic patient registration and password login

**Files:**
- Create: `backend/app/modules/patient_accounts/__init__.py`
- Create: `backend/app/modules/patient_accounts/domain.py`
- Create: `backend/app/modules/patient_accounts/contracts.py`
- Create: `backend/app/modules/patient_accounts/passwords.py`
- Create: `backend/app/modules/patient_accounts/infrastructure.py`
- Create: `backend/app/modules/patient_accounts/application.py`
- Create: `backend/app/modules/patient_accounts/public.py`
- Modify: `backend/app/modules/sessions/contracts.py`
- Modify: `backend/app/modules/sessions/infrastructure.py`
- Modify: `backend/app/modules/sessions/application.py`
- Modify: `backend/app/modules/identity/infrastructure.py`
- Modify: `backend/app/modules/patients/infrastructure.py`
- Create: `backend/tests/patient_accounts/test_domain.py`
- Create: `backend/tests/patient_accounts/test_passwords.py`
- Create: `backend/tests/patient_accounts/test_application.py`
- Create: `backend/tests/integration/test_patient_accounts_postgres.py`

**Interfaces:**
- Produces: `PatientAccountService.register(command: RegisterPatient) -> AccountSession`.
- Produces: `PatientAccountService.login(command: LoginPatient) -> AccountSession`.
- Produces: `PatientAccountService.authenticate(token: str) -> ActorContext` using the unique stored
  token verifier.
- Produces: `PatientAccountService.close_session(token: str) -> None` and
  `get_current_account(token: str) -> CurrentAccount`.
- Consumes: caller-owned actor, patient, session, and account repositories inside one database
  transaction.

- [ ] **Step 1: Write domain/password tests**

Assert email normalization, display-name/password bounds, redacted password/hash repr, Argon2id hash
verification, wrong-password rejection, and UTC account timestamps.

- [ ] **Step 2: Verify domain tests fail**

Run: `py -m uv run pytest tests/patient_accounts/test_domain.py tests/patient_accounts/test_passwords.py -q`
from `backend`.  
Expected: FAIL because the module is absent.

- [ ] **Step 3: Implement immutable domain types and `Argon2PasswordHasher`**

Use library-managed salts and parameters. Keep raw passwords in repr-redacted value objects with no
persistence serializer.

- [ ] **Step 4: Write application and real PostgreSQL failure-injection tests**

Assert successful registration creates exactly one account/actor/patient/role/authenticated session;
duplicate normalized email and injected failure at each downstream insert roll back everything;
login is generic for unknown/wrong credentials; disabled account/actor fails; session binds the
exact actor/patient; aware non-UTC clocks normalize and naive clocks fail before mutation.

- [ ] **Step 5: Implement repositories and service composition**

Extend session repository creation with optional `actor_id`/`patient_id`, add token-hash lookup, and
keep public pseudonymous session creation unchanged. Compose all registration writes in the account
service's single caller-owned transaction.

- [ ] **Step 6: Run focused unit and PostgreSQL tests**

Run the four Task 3 test files.  
Expected: PASS with injected rollback proofs.

- [ ] **Step 7: Commit**

```text
feat: add patient account registration and login
```

### Task 4: Expose account APIs and trusted patient authentication

**Files:**
- Create: `backend/app/modules/patient_accounts/api.py`
- Create: `backend/app/api/security/patient_authentication.py`
- Modify: `backend/app/modules/patient_accounts/public.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/api/middleware/rate_limits.py`
- Create: `backend/tests/patient_accounts/test_api.py`
- Create: `backend/tests/integration/test_patient_account_http_postgres.py`
- Modify: `backend/tests/test_module_registry.py`

**Interfaces:**
- Produces routes: `POST /accounts/register`, `POST /accounts/login`, `GET /accounts/me`,
  `POST /accounts/logout`.
- Produces: `authenticate_patient` FastAPI dependency that sets trusted `request.state.actor_context`
  only after exact authenticated-session validation.
- Produces capabilities: `PATIENT_ACCOUNTS_AUTHENTICATE`, `PATIENT_ACCOUNTS_CURRENT`, and
  `PATIENT_ACCOUNTS_LOGOUT`.

- [ ] **Step 1: Write HTTP contract/security tests**

Assert strict request schemas, no raw token/hash/password in `me` or errors, generic login failure,
no-store responses, disabled/expired/closed session rejection, malformed bearer rejection, and rate
limit classification for register/login.

- [ ] **Step 2: Verify failure**

Run the new API/HTTP tests.  
Expected: FAIL because the routes and dependency are absent.

- [ ] **Step 3: Implement router, dependency, registration, and rate-limit hooks**

Return the opaque token only from successful register/login responses. All authenticated account and
patient routers resolve actor context server-side; public requests retain anonymous context.

- [ ] **Step 4: Run focused and registry regression tests**

Expected: PASS; explicit compile-time module registration remains deterministic.

- [ ] **Step 5: Commit**

```text
feat: expose secure patient account APIs
```

### Task 5: Build patient-web registration, login, logout, and authenticated shell

**Files:**
- Create: `apps/patient-web/lib/account/contracts.ts`
- Create: `apps/patient-web/lib/account/server.ts`
- Create: `apps/patient-web/lib/account/client.ts`
- Create: `apps/patient-web/app/api/account/register/route.ts`
- Create: `apps/patient-web/app/api/account/login/route.ts`
- Create: `apps/patient-web/app/api/account/logout/route.ts`
- Create: `apps/patient-web/app/api/account/me/route.ts`
- Create: `apps/patient-web/app/register/page.tsx`
- Create: `apps/patient-web/app/login/page.tsx`
- Create: `apps/patient-web/components/account-form.tsx`
- Create: `apps/patient-web/components/account-menu.tsx`
- Modify: `apps/patient-web/lib/onboarding/server.ts`
- Modify: `apps/patient-web/components/patient-navigation.tsx`
- Modify: `apps/patient-web/components/patient-shell.tsx`
- Modify: `apps/patient-web/app/page.tsx`
- Create: `apps/patient-web/tests/account-bff.test.ts`
- Create: `apps/patient-web/tests/account-ui.test.tsx`

**Interfaces:**
- Produces BFF endpoints `/api/account/{register,login,logout,me}`.
- Reuses: `swasthyasetu_session_id` and `swasthyasetu_session_token` cookie names and shared strict
  origin/cookie options.
- Produces: bounded client account state `{state, displayName, patientId}` with no bearer.

- [ ] **Step 1: Write BFF tests**

Assert origin rejection before parsing, strict backend response validation, server-only bearer,
cookie security, invalid-session cookie clearing, timeout mapping, duplicate submission handling,
and no-store headers.

- [ ] **Step 2: Write registration/login accessibility tests**

Assert labeled name/email/password/confirmation fields, validation summaries, busy-state duplicate
blocking, generic login error, password never repopulated, and successful navigation to dashboard.

- [ ] **Step 3: Verify tests fail**

Run the two new Vitest files.  
Expected: FAIL because account BFF/UI is absent.

- [ ] **Step 4: Implement account server/client/UI and primary navigation**

Retain pseudonymous helpers for regression tests, but make register/login the landing actions and
make logout authoritative before cookie clearing.

- [ ] **Step 5: Run patient-web tests, lint, and typecheck**

Expected: PASS.

- [ ] **Step 6: Commit**

```text
feat: add patient registration and login experience
```

### Task 6: Add authenticated dashboard and editable patient profile

**Files:**
- Modify: `backend/app/modules/patients/contracts.py`
- Modify: `backend/app/modules/patients/application.py`
- Modify: `backend/app/modules/patients/infrastructure.py`
- Modify: `backend/app/modules/patients/api.py`
- Modify: `backend/app/modules/patients/public.py`
- Create: `backend/tests/patients/test_profile_update.py`
- Modify: `backend/tests/integration/test_postgres_p5c.py`
- Create: `apps/patient-web/lib/patient/contracts.ts`
- Create: `apps/patient-web/lib/patient/server.ts`
- Create: `apps/patient-web/app/api/patient/profile/route.ts`
- Create: `apps/patient-web/app/dashboard/page.tsx`
- Create: `apps/patient-web/app/profile/page.tsx`
- Create: `apps/patient-web/components/dashboard.tsx`
- Create: `apps/patient-web/components/profile-form.tsx`
- Create: `apps/patient-web/tests/dashboard-ui.test.tsx`
- Create: `apps/patient-web/tests/profile-bff.test.ts`
- Create: `apps/patient-web/tests/profile-ui.test.tsx`

**Interfaces:**
- Produces: `PatientService.update_profile(patient_id, expected_updated_at, ...) -> Patient`.
- Produces: `PATCH /patients/{patient_id}` protected by `PATIENT_WRITE_SELF`.
- Produces `/dashboard` and `/profile` patient routes.

- [ ] **Step 1: Write stale-write and IDOR tests**

Assert profile updates normalize UTC, reject unknown fields and stale version, preserve account name
separately from demographics, and return identical denial for another/missing patient.

- [ ] **Step 2: Implement optimistic profile update and API**

Use `updated_at` as the explicit expected version; never accept patient/actor IDs from editable
fields.

- [ ] **Step 3: Write dashboard/profile BFF and UI tests**

Assert unauthenticated state links to login, authenticated greeting/count cards render from bounded
responses, empty states have actions, form is keyboard accessible, and mutations validate origin.

- [ ] **Step 4: Implement dashboard/profile UI**

Private pages resolve `me` server-side and redirect to login when authoritative cookies are absent or
invalid.

- [ ] **Step 5: Run focused backend/frontend/PostgreSQL tests**

Expected: PASS.

- [ ] **Step 6: Commit**

```text
feat: add patient dashboard and profile
```

### Task 7: Add patient-entered medical history and corrections

**Files:**
- Modify: `backend/app/modules/patients/contracts.py`
- Modify: `backend/app/modules/patients/application.py`
- Modify: `backend/app/modules/patients/infrastructure.py`
- Modify: `backend/app/modules/patients/api.py`
- Create: `backend/tests/patients/test_patient_fact_writes.py`
- Create: `backend/tests/integration/test_patient_fact_http_postgres.py`
- Create: `apps/patient-web/lib/history/contracts.ts`
- Create: `apps/patient-web/lib/history/server.ts`
- Create: `apps/patient-web/app/api/patient/history/route.ts`
- Create: `apps/patient-web/app/api/patient/history/[factId]/supersede/route.ts`
- Create: `apps/patient-web/app/history/page.tsx`
- Create: `apps/patient-web/components/history-list.tsx`
- Create: `apps/patient-web/components/history-form.tsx`
- Create: `apps/patient-web/tests/history-bff.test.ts`
- Create: `apps/patient-web/tests/history-ui.test.tsx`

**Interfaces:**
- Produces: `add_patient_fact(...) -> ClinicalFact` and
  `supersede_patient_fact(..., expected_current_id) -> FactSupersession`.
- Produces: `POST /patients/{patient_id}/facts` and
  `POST /patients/{patient_id}/facts/{fact_id}/supersede`.

- [ ] **Step 1: Write domain/application tests for every supported fact value**

Assert patient-reported provenance, `PATIENT_CONFIRMED` state, bounded labels, type/value matching,
UTC effective times, duplicate/stale supersession conflicts, preservation of the old fact, and the
existing clinician-confirmed downgrade guard.

- [ ] **Step 2: Write real PostgreSQL/API IDOR and atomicity tests**

Assert self-writes succeed, cross-subject writes fail without existence disclosure, injected
replacement failure leaves the old fact current, and list/timeline order remains deterministic.

- [ ] **Step 3: Implement fact write contracts and endpoints**

Map strict request unions to the existing `Problem`, `MedicationRecord`, `AllergyRecord`,
`ProcedureRecord`, `Observation`, and `InvestigationRecord` values. Do not accept arbitrary JSON.

- [ ] **Step 4: Write and implement history BFF/UI tests**

Cover all categories, empty states, correction flow, status change, stale conflict reload, keyboard
focus, and no browser persistence.

- [ ] **Step 5: Run focused and full patient/provenance regressions**

Expected: PASS.

- [ ] **Step 6: Commit**

```text
feat: add longitudinal patient medical history
```

### Task 8: Add the patient document metadata and storage service

**Files:**
- Create: `backend/app/modules/patient_documents/__init__.py`
- Create: `backend/app/modules/patient_documents/domain.py`
- Create: `backend/app/modules/patient_documents/contracts.py`
- Create: `backend/app/modules/patient_documents/validation.py`
- Create: `backend/app/modules/patient_documents/infrastructure.py`
- Create: `backend/app/modules/patient_documents/application.py`
- Create: `backend/app/modules/patient_documents/public.py`
- Modify: `backend/app/adapters/storage/local.py`
- Create: `backend/tests/patient_documents/test_validation.py`
- Create: `backend/tests/patient_documents/test_application.py`
- Create: `backend/tests/integration/test_patient_documents_postgres.py`

**Interfaces:**
- Produces: `PatientDocumentService.upload/list/read/delete`.
- Consumes: `ObjectStoragePort` with UUID-derived `ObjectKey`.
- Produces immutable `PatientDocument` metadata and `DocumentContent` stream/bytes contract bounded
  to 10 MiB.

- [ ] **Step 1: Write adversarial validation tests**

Cover valid PDF/JPEG/PNG, empty/oversized input, extension/MIME/signature disagreement, truncated
magic, traversal/control-character/Unicode filename cases, executable signatures, digest/object-key
determinism, and no original name in the storage key.

- [ ] **Step 2: Verify failure and implement validation/domain types**

Expected first run: FAIL; after implementation: PASS.

- [ ] **Step 3: Write storage/application/PostgreSQL tests**

Assert upload writes object then metadata, metadata failure compensates object creation, self-owned
list/read, IDOR denial, soft delete before object removal, repeated delete idempotency, and storage
delete failure remains non-downloadable/observable.

- [ ] **Step 4: Implement repository/service and controlled storage composition**

The local root is explicit, resolved, non-symlink escaping, and absent when disabled. Do not activate
OCR or the P11 synthetic processors.

- [ ] **Step 5: Run focused tests**

Expected: PASS.

- [ ] **Step 6: Commit**

```text
feat: add secure patient document storage
```

### Task 9: Expose document APIs and patient document-vault UI

**Files:**
- Create: `backend/app/modules/patient_documents/api.py`
- Modify: `backend/app/modules/patient_documents/public.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/api/middleware/rate_limits.py`
- Create: `backend/tests/patient_documents/test_api.py`
- Create: `backend/tests/integration/test_patient_document_http_postgres.py`
- Create: `apps/patient-web/lib/documents/contracts.ts`
- Create: `apps/patient-web/lib/documents/server.ts`
- Create: `apps/patient-web/app/api/patient/documents/route.ts`
- Create: `apps/patient-web/app/api/patient/documents/[documentId]/route.ts`
- Create: `apps/patient-web/app/api/patient/documents/[documentId]/content/route.ts`
- Replace: `apps/patient-web/app/documents/page.tsx`
- Create: `apps/patient-web/components/document-vault.tsx`
- Create: `apps/patient-web/tests/document-vault-bff.test.ts`
- Create: `apps/patient-web/tests/document-vault-ui.test.tsx`

**Interfaces:**
- Produces authenticated REST/BFF list, multipart upload, download, and delete routes.
- Produces safe download headers using sanitized display name and detected MIME.

- [ ] **Step 1: Write HTTP/BFF security tests**

Assert self-subject authentication before body read, upload rate limit, multipart bounds, no-store,
safe `Content-Disposition`, no path/object key disclosure, cross-patient non-enumeration, and cookie
clearing only for authoritative session failure.

- [ ] **Step 2: Implement backend router and BFF**

Stream/bound the request rather than trusting `Content-Length`. BFF forwards the server-only bearer
and never buffers beyond the same 10 MiB ceiling.

- [ ] **Step 3: Write and implement accessible vault UI**

Cover upload progress/busy state, validation errors, empty/list states, download link, explicit
delete confirmation, failed delete recovery, and focus return.

- [ ] **Step 4: Run unit, PostgreSQL, and patient-web tests**

Expected: PASS.

- [ ] **Step 5: Commit**

```text
feat: add patient document vault experience
```

### Task 10: Implement provider-neutral grounded guidance

**Files:**
- Create: `backend/app/modules/self_care/guidance_contracts.py`
- Create: `backend/app/modules/self_care/guidance_policy.py`
- Create: `backend/app/modules/self_care/guidance_service.py`
- Create: `backend/app/adapters/ai/gemini_guidance.py`
- Create: `backend/app/adapters/ai/fake_guidance.py`
- Create: `backend/tests/self_care/test_guidance_contracts.py`
- Create: `backend/tests/self_care/test_guidance_policy.py`
- Create: `backend/tests/self_care/test_guidance_service.py`
- Create: `backend/tests/adapters/test_gemini_guidance.py`

**Interfaces:**
- Produces: `GuidanceProvider.generate(request: GuidanceProviderRequest) -> GuidanceProviderResult`.
- Produces: `GuidanceService.answer(question: GuidanceQuestion, actor: ActorContext) -> GuidanceAnswer`.
- Produces: closed outcomes `ANSWERED`, `OUT_OF_SCOPE`, `CONSENT_REQUIRED`, `UNAVAILABLE`, and
  `REJECTED`.

- [ ] **Step 1: Write strict contract/policy tests**

Assert bounded question/answer/citation lengths, HTTPS citations, exact allowed-domain matching,
duplicate/overlapping annotation rejection, unsupported high-risk categories, forbidden claim
rejection, stable ordering, no patient context fields, and redacted provider errors.

- [ ] **Step 2: Verify failure and implement contracts/policy**

Expected first run: FAIL; after implementation: PASS.

- [ ] **Step 3: Write fake and Gemini adapter tests**

Mock the official SDK boundary. Assert one Google Search-grounded request, configured model/deadline,
no secret/query in repr/log exceptions, annotation parsing, timeout mapping, cancellation, malformed
response rejection, and no retries that can duplicate a billable search.

- [ ] **Step 4: Implement adapters and consent-first service**

Call `consent.check` for active `ACTOR`-subject `EXTERNAL_AI_PROCESSING` consent with exact scope
`["ayurvedic_guidance"]` and notice `external-ai-v1` before constructing/calling the provider.
Post-validate every provider result; never display raw unvalidated model output.

- [ ] **Step 5: Run focused tests**

Expected: PASS with zero network calls.

- [ ] **Step 6: Commit**

```text
feat: add grounded wellness guidance service
```

### Task 11: Expose guidance consent/API and patient guidance UI

**Files:**
- Create: `backend/app/modules/self_care/guidance_api.py`
- Modify: `backend/app/modules/self_care/public.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/api/middleware/rate_limits.py`
- Create: `backend/tests/self_care/test_guidance_api.py`
- Create: `backend/tests/integration/test_guidance_consent_postgres.py`
- Create: `apps/patient-web/lib/guidance/contracts.ts`
- Create: `apps/patient-web/lib/guidance/server.ts`
- Create: `apps/patient-web/app/api/guidance/consent/route.ts`
- Create: `apps/patient-web/app/api/guidance/route.ts`
- Create: `apps/patient-web/app/guidance/page.tsx`
- Create: `apps/patient-web/components/guidance-form.tsx`
- Create: `apps/patient-web/tests/guidance-bff.test.ts`
- Create: `apps/patient-web/tests/guidance-ui.test.tsx`

**Interfaces:**
- Produces: `POST /guidance/ayurveda` using authenticated actor/patient and active external-AI
  consent.
- Produces exact-query disclosure/consent grant/revoke in the patient BFF.

- [ ] **Step 1: Write consent and provider-call-count tests**

Assert missing/declined/revoked consent means zero provider calls, active exact-purpose consent means
one call, general product consent is insufficient, duplicate browser submission is serialized, and
failure never returns model text.

- [ ] **Step 2: Implement API, registration, and rate limit**

Keep the API private to authenticated patients. Do not persist questions or answers in the initial
release.

- [ ] **Step 3: Write and implement guidance UI tests**

Cover disclosure, explicit consent, question preview, citations, retrieval time, safety copy,
unavailable/rejected/out-of-scope states, no HTML injection, keyboard flow, and consent revocation.

- [ ] **Step 4: Run focused backend/frontend/PostgreSQL tests**

Expected: PASS with fake provider only.

- [ ] **Step 5: Commit**

```text
feat: add grounded home-care guidance experience
```

### Task 12: Integrate authenticated intake and longitudinal timeline

**Files:**
- Modify: `backend/app/modules/sessions/domain.py`
- Modify: `backend/app/modules/encounters/application.py`
- Modify: `backend/app/modules/encounters/api.py`
- Modify: `backend/app/modules/clinical_intake/api.py`
- Create: `backend/tests/test_authenticated_encounters.py`
- Modify: `backend/tests/integration/test_postgres_clinical_intake_api.py`
- Create: `apps/patient-web/lib/timeline/server.ts`
- Create: `apps/patient-web/app/api/patient/timeline/route.ts`
- Create: `apps/patient-web/app/timeline/page.tsx`
- Create: `apps/patient-web/components/timeline.tsx`
- Modify: `apps/patient-web/lib/intake/server.ts`
- Modify: `apps/patient-web/app/encounter/page.tsx`
- Create: `apps/patient-web/tests/timeline-ui.test.tsx`

**Interfaces:**
- Extends general-intake encounter creation to `AUTHENTICATED` sessions bound to their exact patient.
- Preserves pseudonymous behavior and one resumable intake per session.
- Produces patient timeline BFF/UI using the existing provenance API.

- [ ] **Step 1: Write authenticated encounter/intake tests**

Assert the session's bound patient is authoritative, payload cannot substitute another patient,
authenticated and pseudonymous paths remain isolated, exact consent is required, and completed
intake remains a draft.

- [ ] **Step 2: Implement authenticated intake composition**

Use trusted session actor/patient bindings; never infer identity from an arbitrary request body.

- [ ] **Step 3: Write and implement timeline/intake navigation tests**

Assert deterministic order/cursor, categorized accessible entries, dashboard links, authenticated
start/resume, expired-session login redirect, and no loss of existing pseudonymous tests.

- [ ] **Step 4: Run encounter/intake/provenance and patient-web tests**

Expected: PASS.

- [ ] **Step 5: Commit**

```text
feat: connect patient intake and medical timeline
```

### Task 13: Complete product navigation, launcher, and documentation

**Files:**
- Modify: `apps/patient-web/components/patient-navigation.tsx`
- Modify: `apps/patient-web/components/patient-shell.tsx`
- Modify: `apps/patient-web/app/globals.css`
- Modify: `apps/patient-web/app/manifest.ts`
- Modify: `apps/patient-web/public/sw.js`
- Modify: `scripts/demo.py`
- Modify: `backend/tests/test_demo_launcher.py`
- Modify: `README.md`
- Modify: `docs/DEMO_GUIDE.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`
- Modify: `deployments/local/README.md`

**Interfaces:**
- Produces a patient-only primary navigation and one-command local setup.
- Fixes launcher status to probe `/health/ready` for backend health.
- Documents Gemini key configuration without recording a secret.

- [ ] **Step 1: Write navigation/PWA/launcher regression tests**

Assert private data is never cached, obsolete preview links are absent from primary navigation,
backend readiness status is accurate, required directories/config are created safely, and stop still
targets only launcher-owned processes/Compose resources.

- [ ] **Step 2: Implement final product shell and launcher configuration**

Default the demo to the patient URL and preserve admin/clinician packages without requiring them for
the patient-only product.

- [ ] **Step 3: Update documentation and tracker honestly**

Describe account setup, history, document vault, optional Gemini configuration, safety limitations,
and exact start/stop commands. Do not call it production or clinical software.

- [ ] **Step 4: Run formatting/diff checks**

Expected: PASS with only intended files changed.

- [ ] **Step 5: Commit**

```text
docs: complete patient health hub setup
```

### Task 14: Full-stack acceptance, security review, and merge gate

**Files:**
- Modify: `tests/e2e/patient.spec.ts`
- Create: `tests/e2e/patient-account-history.spec.ts`
- Create: `tests/e2e/patient-documents-guidance.spec.ts`
- Modify: `.github/workflows/ci.yml` only if an existing job needs non-secret fake-provider wiring;
  do not add a seventh job.

**Interfaces:**
- Produces browser evidence for the complete acceptance journey against real FastAPI/PostgreSQL.
- Preserves exactly six CI jobs.

- [ ] **Step 1: Add Playwright journeys**

Cover register -> dashboard -> profile -> all history categories -> correction -> timeline -> valid
document upload/download/remove -> intake -> consented fake guidance with citations -> logout ->
login -> persisted record. Add a second account to prove UI/API IDOR denial and add invalid upload,
expired-session, revoked-consent, and provider-unavailable journeys.

- [ ] **Step 2: Run all local quality gates**

Run backend format/lint/mypy/compile/import/full pytest, real PostgreSQL integration, Alembic
upgrade/current/check, frontend format/lint/typecheck/full Vitest/all three production builds,
Playwright Chromium, Compose health, Gitleaks, dependency/config/image scans, and `git diff --check`.

Expected minimum baseline before new tests: 2,351 backend passed, 102 skipped in the non-database
gate, and 322 frontend passed. Final counts must be recorded from fresh output.

- [ ] **Step 3: Perform requirement and privacy audit**

Confirm every acceptance criterion in the design has direct evidence; search built artifacts and
logs for passwords, bearers, API keys, email/medical fixture canaries, object keys, and raw Gemini
responses.

- [ ] **Step 4: Push, open PR, and verify exact-SHA CI**

Require success for Backend quality, Frontend quality, Persistence integration, Docker and
PostgreSQL, Playwright Chromium, and Security scans.

- [ ] **Step 5: Review and merge only after all six jobs pass**

Verify the post-merge `main` run on its exact SHA before deleting the feature branch.

```text
test: verify patient health hub end to end
```
