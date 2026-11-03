# Patient Health Hub Product Completion Design

**Status:** Proposed for user approval  
**Date:** 2026-11-03  
**Branch:** `phase/patient-health-hub`

## Intent

Turn the existing SwasthyaSetu engineering platform into the patient-only college product the user
intended. A registered patient must be able to sign in, maintain a private longitudinal medical
history, store medical documents, complete the existing intake journey, and request source-grounded
Ayurvedic/home-care education from one coherent dashboard.

This design deliberately removes hospital, clinician, and administrator workflows from the primary
product experience. Their existing packages and contracts remain intact so the implementation does
not destroy reviewed work, but they are not required to run or understand the patient product.

Mental-health diagnosis or screening is not part of this increment. It will be designed only after
the patient record and guidance workflows are complete.

## Product outcome

The default experience becomes:

```text
Landing page
  -> Register or sign in
  -> Patient dashboard
       -> Personal profile
       -> Medical history
       -> Medical documents
       -> Structured health intake
       -> Ayurvedic / home-care education
       -> Longitudinal timeline
```

The dashboard must be useful without visiting the clinician or administration applications.

## Goals

1. Provide persistent patient registration using name, email, and password.
2. Provide secure email/password login, logout, and authenticated-session restoration.
3. Ensure every patient can access only their own profile, history, documents, and timeline.
4. Allow the patient to record and correct conditions, medications, allergies, procedures,
   investigations, and observations.
5. Present all important record changes in a chronological medical-history timeline.
6. Allow PDF, JPEG, and PNG medical-document upload, list, download, and removal in the local demo.
7. Preserve the existing structured-intake workflow and make it accessible from the dashboard.
8. Provide an Ayurvedic/home-care education workflow grounded through Gemini Google Search with
   visible citations and strict safety restrictions.
9. Keep setup understandable: one launcher, one primary URL, and one patient journey.
10. Preserve the repository's modular-monolith, provenance, authorization, and fail-closed design.

## Non-goals

- Hospital, clinician, counsellor, or administrator accounts.
- Organization or multi-tenant management.
- Email verification, password reset, social login, or production account recovery.
- Mental-health diagnosis, screening, or routing in this increment.
- OCR, document classification, or AI extraction from uploaded files.
- Autonomous diagnosis, prescription, medication changes, or emergency routing.
- A production deployment, real-patient authorization, or regulatory compliance claim.
- Unrestricted AI-generated remedies or arbitrary web content presented as medical fact.
- Rebuilding the backend inside Next.js or replacing existing reviewed domain modules.

## Anti-goals

- A dashboard made from disconnected preview cards.
- Fixed fake accounts or browser-only persistence.
- Sending a patient's complete medical record to Gemini.
- Silent overwriting of clinical history.
- Storing raw passwords, session bearers, Gemini keys, or uploaded files in PostgreSQL.
- Making the user navigate the clinician or admin applications to complete a patient task.

## Approaches considered

### 1. Extend the existing FastAPI/PostgreSQL platform — selected

Reuse actors, sessions, patients, clinical facts, encounters, provenance, object-storage ports, the
patient BFF, and the patient web application. Add the missing patient-account, history-write,
document-vault, and grounded-guidance boundaries.

This takes more implementation work than a presentation layer, but it preserves the architecture
and makes registration, ownership, persistence, and documents genuinely work.

### 2. Move the product into Next.js

Implement authentication, persistence, and uploads directly in the patient Next.js application.
This is rejected because it duplicates the existing backend, weakens authorization boundaries, and
abandons most completed work.

### 3. Create a UI-only simulation

Use fixed accounts and synthetic fixtures. This is rejected because the user's main requirement is
a genuinely maintained medical history, not another visual preview.

## Architecture

### Patient accounts

Add a `patient_accounts` bounded context. It owns registration identity and local credentials while
the existing `identity` module continues to own PII-free authorization actors.

One successful registration transaction creates:

- one `PatientAccount` containing normalized email, display name, and an Argon2id password hash;
- one `Actor` with type and role `PATIENT`;
- one `Patient` whose ID becomes the actor's trusted `subject_id`;
- one authenticated opaque session bound to both actor and patient.

Email uniqueness is case-insensitive. Email and display name are trimmed and validated. Passwords
are never logged or returned. Duplicate registration returns a generic conflict without disclosing
credential details.

Login verifies the password in constant-time-compatible library code and creates a new opaque
authenticated session. Failed login uses one generic error for unknown email and wrong password.
The backend stores only the password hash and the existing SHA-256 session-token verifier.

The current pseudonymous-session flow remains available internally for its existing tests, but
registration and login become the normal patient entry points.

### Authentication propagation

The browser receives an `HttpOnly`, `SameSite=Strict`, path-root cookie pair containing the opaque
session ID and bearer. `Secure` remains mandatory outside loopback development. Client JavaScript
never receives the bearer.

Next.js route handlers forward the bearer server-side. A backend authentication boundary resolves
the bearer to an active authenticated session, actor, and patient subject, then installs the trusted
`ActorContext` used by existing self-subject authorization checks. Expired, closed, disabled, or
mismatched sessions fail closed.

Logout closes the authoritative backend session and clears both cookies.

### Database changes

Create one explicit Alembic migration after `p7a_0007` with:

#### `patient_accounts`

- `id` UUID primary key;
- `actor_id` UUID unique foreign key to `actors`;
- `patient_id` UUID unique foreign key to `patients`;
- `email_normalized` bounded string with a unique index;
- `email_display` bounded string;
- `display_name` bounded string;
- `password_hash` bounded string;
- `status` constrained to `ACTIVE` or `DISABLED`;
- UTC `created_at` and `updated_at`.

#### `patient_documents`

- `id` UUID primary key;
- `patient_id` UUID indexed foreign key to `patients`;
- sanitized `display_name`;
- detected MIME type;
- byte size;
- opaque object-storage key, unique;
- SHA-256 content digest;
- UTC `created_at`;
- nullable UTC `deleted_at` for soft deletion.

Existing patient, clinical-fact, encounter, session, actor, and timeline tables remain authoritative.
No medical-document bytes are stored in PostgreSQL.

### Medical history

Reuse the existing canonical clinical fact types and provenance model. Add self-authorized write
APIs for:

- problem/condition;
- medication;
- allergy;
- procedure;
- investigation;
- observation.

New patient-entered facts are explicitly patient-reported and never clinician-confirmed. Editing a
fact creates a replacement fact and records supersession; it never mutates or silently erases the
previous value. The history UI shows active entries by category and a chronological timeline. The
patient can mark applicable problem or medication states inactive through a replacement record.

The first product increment does not attempt automatic terminology coding or diagnosis inference.
Labels are patient-entered bounded text.

### Document vault

Reuse `ObjectStoragePort` and `LocalFilesystemObjectStorage` for the local college build. Uploaded
files are stored below a configured directory outside the web roots under UUID-derived object keys.

Accepted formats:

- PDF;
- JPEG;
- PNG.

The service enforces a 10 MiB maximum, rejects empty files, validates the filename separately from
the detected file signature, rejects path traversal and executable/polyglot signatures covered by
the validation suite, computes a SHA-256 digest, and never uses the original filename as a storage
path. Downloads require the authenticated self-subject check and use safe response headers.

Removal first records a soft-deleted metadata state, then removes the object through the storage
port. Deleted documents disappear from normal lists. Failed storage deletion remains observable and
does not expose the file to another patient.

No OCR or clinical extraction runs automatically.

### Ayurvedic and home-care education

Add a patient-facing `/guidance` workflow backed by a provider-neutral `GuidanceProvider` port. The
live local adapter uses the official Google GenAI SDK with Gemini Google Search grounding. The API
key is read only from server configuration and is never exposed to the browser or committed.

The workflow accepts a bounded general-wellness question. It does not send the patient's name,
email, uploaded documents, timeline, or raw medical history to Gemini. The prompt instructs Gemini
to return educational supportive-care information, avoid diagnosis/prescription/dosage changes, and
use only attributable sources.

Because the question itself may reveal health information, the first provider request requires an
active, purpose-specific `EXTERNAL_AI_PROCESSING` consent grant. The page explains that the exact
question will be sent to Google's Gemini service for search grounding and shows the text before the
user submits it. Declining or revoking that consent keeps the local record usable and prevents the
external request; general product consent is not treated as external-AI consent.

The response is shown only when all of these conditions hold:

1. the provider returns a valid bounded response before the configured deadline;
2. Google Search grounding returns citations;
3. at least one citation belongs to the configured source allowlist;
4. the response contains no forbidden diagnosis, prescription, guaranteed-cure, or emergency-
   replacement claims according to deterministic output guards;
5. the user query is within the supported low-risk educational scope.

The initial allowlist is configuration with project-selected official domains such as Ministry of
AYUSH, CCRAS, and WHO. It can be narrowed through environment configuration, but the application
does not require a human approval workflow for the college demo. An arbitrary search result is not
enough to authorize display.

The UI always displays:

- “Educational information, not a diagnosis or prescription”;
- the generated explanation;
- clickable source citations and retrieval time;
- a note that herbs and household products can interact with conditions or medicines;
- a prompt to seek qualified care for persistent, worsening, severe, pregnancy-related, paediatric,
  or medication-related concerns.

If Gemini is unconfigured, unavailable, uncited, out of scope, or rejected by a guard, the UI shows
a stable unavailable state and does not invent a fallback remedy. Automated tests use a deterministic
fake provider; no test calls Gemini or Google.

Google Search grounding is a metered external service. The UI must not automatically issue requests
while typing; one explicit submission produces at most one provider request.

### Patient web application

The patient application becomes the only required frontend for this product increment.

Primary routes:

- `/` — clear product landing page with register and sign-in actions;
- `/register` — name, email, password, password confirmation;
- `/login` — email and password;
- `/dashboard` — summary cards, recent timeline and primary actions;
- `/profile` — demographics and preferences;
- `/history` — categorized facts with add/correct/state-change workflows;
- `/documents` — upload, list, download and remove;
- `/intake` — entry into the existing structured-intake journey;
- `/guidance` — grounded Ayurvedic/home-care education;
- `/timeline` — unified chronological record.

Unauthenticated access to private routes redirects to `/login`. Authenticated access to `/login` or
`/register` redirects to `/dashboard`. Private API responses remain `no-store`. No sensitive state
is stored in localStorage, sessionStorage, IndexedDB, Cache API, or the service worker.

The navigation contains only patient-relevant destinations. Existing experimental preview routes
may remain addressable for engineering tests but are removed from the primary dashboard and menu.

### Dashboard

The dashboard is the center of the product and includes:

- patient greeting and profile-completion status;
- counts for active conditions, medications, allergies, and stored documents;
- recent medical-history events;
- “Add medical history” primary action;
- “Upload document” action;
- “Start health intake” action;
- “Ayurvedic & home-care education” action;
- account menu with logout.

Empty states explain the next useful action instead of displaying inactive future modules.

## API surface

The exact route naming may follow existing router conventions, but the product exposes these
capabilities:

```text
POST   /api/v1/accounts/register
POST   /api/v1/accounts/login
POST   /api/v1/accounts/logout
GET    /api/v1/accounts/me

GET    /api/v1/patients/{patient_id}
PATCH  /api/v1/patients/{patient_id}
GET    /api/v1/patients/{patient_id}/facts
POST   /api/v1/patients/{patient_id}/facts
POST   /api/v1/patients/{patient_id}/facts/{fact_id}/supersede
GET    /api/v1/patients/{patient_id}/timeline

GET    /api/v1/patients/{patient_id}/documents
POST   /api/v1/patients/{patient_id}/documents
GET    /api/v1/patients/{patient_id}/documents/{document_id}/content
DELETE /api/v1/patients/{patient_id}/documents/{document_id}

POST   /api/v1/guidance/ayurveda
```

Every patient-scoped endpoint performs a server-side self-subject check. Cross-patient access must
return the same non-enumerating denial regardless of whether the target record exists.

## Error handling

- Registration conflict: stable validation/conflict response; no password or account details.
- Login failure: one generic invalid-credentials response.
- Expired session: clear cookie and direct the user to sign in.
- Document validation: field-level message without echoing file bytes or unsafe paths.
- Storage failure: retryable unavailable state; no partial metadata advertised as downloadable.
- Gemini timeout/outage: stable unavailable state with no fallback remedy.
- Gemini unsafe/uncited response: rejected and not displayed.
- Database failure: existing privacy-safe dependency error model.

## Security and privacy

- Argon2id password hashing with per-password salts and library-managed parameters.
- Rate limits on registration, login, document upload, and Gemini submission.
- Generic authentication errors and no email enumeration through login.
- Opaque server-authoritative sessions; no JWT or browser-readable bearer.
- Exact-origin checks for cookie-authenticated mutations.
- File signature validation, bounded size, opaque keys, and safe content disposition.
- No medical content in logs, metrics, traces, filenames, or Gemini request metadata.
- No patient data sent to Gemini in the initial release.
- Exact-query disclosure and purpose-specific `EXTERNAL_AI_PROCESSING` consent before each enabled
  external-AI workflow.
- API key and local storage root supplied through ignored environment configuration.
- All patient reads and writes protected by trusted actor subject identity.

## Testing strategy

### Domain and unit

- email normalization and validation;
- password hashing/verification and redacted representations;
- registration invariants and duplicate handling;
- authenticated-session creation and expiry;
- fact creation and supersession;
- document signature, filename, size, digest, and object-key validation;
- Gemini adapter timeout/error mapping;
- citation allowlist and unsafe-output rejection;
- external-AI consent required before provider invocation;
- dashboard and form components.

### PostgreSQL integration

- registration atomically creates account, actor, role, patient, and session;
- duplicate email rolls back all partial state;
- session bearer resolves the exact actor/patient;
- patient fact replacement preserves the old row;
- document metadata is patient-owned and soft deletion is authoritative;
- migration upgrades from an empty database and from `p7a_0007`.

### HTTP and security

- register/login/me/logout contracts;
- password and bearer never appear in responses or logs;
- cross-patient IDOR denial for profile, facts, timeline, and documents;
- upload rejects invalid MIME/signature, traversal names, oversized and empty files;
- guidance refuses ungrounded, uncited, unsafe, unsupported and timed-out results;
- guidance performs no provider call without active `EXTERNAL_AI_PROCESSING` consent;
- protected routes reject missing, expired, closed and disabled sessions.

### Browser

- register -> dashboard -> profile -> history -> timeline -> logout;
- login restores the persisted account and history;
- upload -> list -> download -> remove document;
- intake remains reachable and functional from the dashboard;
- grounded guidance fake renders citations and safety copy;
- Gemini unavailable state does not display advice;
- keyboard navigation and accessible labels for every core flow;
- browser storage remains free of session and medical data.

## Delivery sequence

### Increment 1 — Account and dashboard foundation

Registration, login, logout, authenticated sessions, account `me`, dashboard shell, migration, and
cross-patient authorization foundation.

### Increment 2 — Profile and longitudinal medical history

Profile editing, clinical-fact creation/supersession, categorized history UI, timeline integration,
and intake dashboard entry.

### Increment 3 — Patient document vault

Validated upload, local object storage, metadata, list/download/remove UI, ownership and negative
security tests.

### Increment 4 — Grounded Ayurvedic/home-care education

Provider port, deterministic fake, Gemini Google Search adapter, citation/safety guards, UI, rate
limits, configuration and unavailable states.

### Increment 5 — Product integration and demo acceptance

Complete browser journey, launcher simplification, current documentation, accessibility check,
security scans, PostgreSQL/Docker verification, and final demo guide.

Each increment must be independently tested and merged only after all six repository CI jobs pass.

## Acceptance criteria

The product increment is complete when:

1. A new user can register with name, email, and password and immediately reach their dashboard.
2. The same user can log out, log back in, and recover their persisted record.
3. Two users cannot read or mutate one another's profile, facts, timeline, or documents.
4. A user can add every supported medical-history category and see it in history and timeline views.
5. Correcting a history item preserves the previous version through supersession.
6. A valid PDF/JPEG/PNG can be uploaded, listed, downloaded, and removed by its owner.
7. Invalid and hostile document inputs fail closed.
8. The existing structured intake remains functional from the authenticated dashboard.
9. The guidance page can render a fake grounded response with visible citations in tests.
10. A configured Gemini adapter uses Google Search grounding and never exposes the API key.
11. No Gemini request occurs without explicit external-AI disclosure and active purpose-specific
    consent.
12. Uncited, disallowed-source, unsafe, timed-out, or unavailable Gemini responses show no remedy.
13. The complete patient journey passes against real FastAPI and PostgreSQL in Playwright.
14. Backend, frontend, persistence, Docker, Playwright, and security CI jobs pass.
15. The launcher and documentation describe only the patient product needed for the college demo.

## Builder decisions already made

- Extend the current modular monolith; do not rebuild in Next.js.
- Use local email/password accounts for the college product.
- Use Argon2id rather than reversible or general-purpose password hashing.
- Reuse opaque database-backed sessions and server-only cookies.
- Keep clinician/admin applications out of the primary workflow without deleting them.
- Store uploaded bytes through `ObjectStoragePort`, not PostgreSQL.
- Do not run OCR automatically.
- Use Gemini Google Search grounding behind a provider port with citations and an authoritative-domain
  allowlist.
- Do not send patient history to Gemini in the initial release.
- Defer mental-health functionality until the patient record product is complete.

## Remaining operator input

Before live Gemini testing, the operator must provide a Gemini API key through ignored local
configuration. The repository supplies a conservative official-domain allowlist that the operator
may narrow. Implementation and automated tests do not require the key because they use the
deterministic fake provider.
