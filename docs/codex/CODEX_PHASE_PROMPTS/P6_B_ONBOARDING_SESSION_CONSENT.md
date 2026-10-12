# Codex Phase Prompt — P6-B Patient Onboarding / Session / Consent

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P6-B`
**Phase unit:** P6-B — Patient Onboarding / Session / Consent
**Base branch:** `main`
**Expected base commit:** `778459800d1f16dc69d7efaeb57907beac19217f`
**Implementation branch:** `phase/p6-b-onboarding-session-consent`
**Commit message:** `feat: connect P6-B patient onboarding`

## 0. Mission

Continue P6 from merged P6-A.

Current state:

```text
P5 = COMPLETE
P6-A = COMPLETE
P6-B = NEXT
P6-C = NOT STARTED
P6 overall = PARTIAL
Alembic head = p5b_0006
```

Implement only the real patient onboarding/session/consent journey.

P6-B owns:

```text
/start onboarding flow
/language working preference selector
real pseudonymous session creation
secure frontend-to-backend session bridge
/consent working GENERAL_PRODUCT_USE consent UI
consent grant/read/revoke
session close/end control
connected keyboard onboarding journey
real backend E2E evidence
safe degraded/backend-unavailable states
```

Do NOT implement:

```text
authenticated patient login/signup
patient profile creation
clinical intake
encounter creation
documents/OCR
results
referrals
provider directory
AI
mental-health conversation
clinical safety logic
PWA/service worker/offline caching
push notifications
FHIR/ABDM
new backend tables/migrations
PATIENT-subject consent
```

P6-C owns final accessibility + PWA baseline.

Do not merge.

## 1. Preflight

Expected:

```text
branch: main
HEAD: 778459800d1f16dc69d7efaeb57907beac19217f
working tree: clean
P6-A: COMPLETE
P6: PARTIAL
Alembic head: p5b_0006
```

Create:

```text
git switch -c phase/p6-b-onboarding-session-consent
```

## 2. Required Reading

Read before coding:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/06_API_CONTRACTS.md
docs/29_ENGINEERING_STANDARDS.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md
docs/codex/CODEX_PHASE_PROMPTS/P6_A_PATIENT_WEB_SHELL.md
```

Inspect:

```text
apps/patient-web/**
tests/e2e/**
backend/app/modules/sessions/**
backend/app/modules/consent/**
backend/app/api/errors/**
.github/workflows/ci.yml
deployments/local/compose.yaml
```

Canonical requirements include:

```text
AC-P6-002 — session/consent journey connected to backend
AC-P6-003 — language selection UI exists
AC-P6-005 — keyboard navigation works for core onboarding
NFR-UX-001 — understandable patient language
NFR-UX-004 — clearly state insufficient/unavailable information
NFR-UX-006 — urgent actions visually distinct
```

Preserve all P6-A acceptance already achieved.

## 3. Backend Contracts Are Fixed

Use the existing real backend contracts exactly.

Session create:

```text
POST /api/v1/sessions
{
  "session_type": "PSEUDONYMOUS",
  "language_preference": "en"
}
```

Returns once:

```text
session_id
session_token
session_type
status
expires_at
```

Session read/close require:

```text
Authorization: Bearer <session_token>
```

Consent grant:

```text
POST /api/v1/consents
Authorization: Bearer <session_token>

{
  "subject_type": "SESSION",
  "subject_id": "<session id>",
  "purpose": "GENERAL_PRODUCT_USE",
  "scope": ["clinical_intake"],
  "notice_version": "privacy-v1"
}
```

Consent list:

```text
GET /api/v1/consents?subject_type=SESSION&subject_id=<session id>&purpose=GENERAL_PRODUCT_USE
```

Consent revoke:

```text
POST /api/v1/consents/{consent_id}/revoke
Authorization: Bearer <session_token>

{"reason":"user_requested"}
```

Do not change backend contracts to simplify frontend work.

## 4. Security Architecture — Same-Origin Next.js BFF

Do NOT expose the backend session bearer token to browser JavaScript after creation.

Implement thin same-origin App Router route handlers:

```text
GET  /api/onboarding/session
POST /api/onboarding/session
POST /api/onboarding/session/close

GET  /api/onboarding/consent
POST /api/onboarding/consent
POST /api/onboarding/consent/revoke
```

Flow:

```text
Patient UI
  -> same-origin Next route handler
      -> FastAPI backend
```

The Next server receives the one-time backend session token and stores it only in a transient HttpOnly browser-session cookie.

The Next server forwards it to FastAPI only as:

```text
Authorization: Bearer <token>
```

FastAPI must still never receive session authentication from a cookie.

## 5. Backend URL Configuration

Use server-only:

```text
SWASTHYASETU_BACKEND_URL
```

Do NOT use `NEXT_PUBLIC_` for the backend URL used with session credentials.

Rules:

```text
server-only access
strip trailing slash
allow http://127.0.0.1:8000 for local/CI
production config supplied explicitly
never expose URL/token through client bundles
```

If absent/invalid:

```text
safe 503 degraded response
```

Build must still succeed without a live backend.

## 6. Session Cookies

Recommended names:

```text
swasthyasetu_session_id
swasthyasetu_session_token
```

Both:

```text
HttpOnly = true
SameSite = strict
Path = /
Secure = true in production
Secure = false only for localhost development/test
```

They MUST be browser-session cookies:

```text
NO Max-Age
NO persistent Expires
```

Never place session token in:

```text
localStorage
sessionStorage
IndexedDB
URL/query
React state
HTML
client logs
analytics
error messages
server logs
JSON responses
```

`document.cookie` must not reveal it.

## 7. Session Creation BFF

`POST /api/onboarding/session`

Client body:

```json
{"language_preference":"en"}
```

The BFF controls:

```text
session_type = PSEUDONYMOUS
```

On success:

```text
validate backend response
set HttpOnly session_id cookie
set HttpOnly session_token cookie
return minimized safe metadata
```

Do NOT return the token.

## 8. Session Status BFF

`GET /api/onboarding/session`

Read cookies and call:

```text
GET /api/v1/sessions/{session_id}
Authorization: Bearer <token>
```

Return minimized safe session metadata.

For invalid/expired/closed/revoked sessions, clear cookies when authoritative and return honest frontend state.

## 9. Session Close BFF

`POST /api/onboarding/session/close`

Call backend close using bearer from the HttpOnly cookie.

After success:

```text
clear session_id cookie
clear session_token cookie
```

Expose accessible UI action:

```text
End private session
```

Do not call it logout.

## 10. Same-Origin Mutation Protection

Because mutation routes use cookies:

```text
SameSite=Strict
POST for all mutations
same-origin only
```

Validate request `Origin` when present against the current request origin.

Reject cross-origin mutations safely.

No third-party CSRF dependency.

## 11. Language Selection

Activate `/language`.

Initial choices:

```text
English -> en
हिन्दी -> hi
```

Do not invent a non-standard Hinglish language tag.

Do not claim the complete UI is translated.

Use clear wording that this is the preferred language for the session and broader multilingual content comes later.

Selecting the language creates the real pseudonymous backend session.

No localStorage.

## 12. Core Onboarding Flow

Required:

```text
/
 -> /start
 -> /language
 -> create real pseudonymous session
 -> /consent
 -> grant real GENERAL_PRODUCT_USE consent
 -> /encounter
```

`/encounter` remains non-clinical.

After successful onboarding it may show:

```text
Your private session and consent are ready.
Clinical intake is not available in this phase.
```

Do NOT create a backend encounter.

## 13. /start

Replace unavailable placeholder.

Explain briefly:

```text
no name required
temporary private/pseudonymous session
choose language
review consent before clinical intake
urgent help remains available
```

Primary action:

```text
Continue
```

to `/language`.

No backend call merely by opening `/start`.

## 14. Consent Notice

Activate `/consent`.

There is no approved jurisdiction-specific final legal/privacy document in current specs.

Therefore:

```text
do not fabricate legal claims
do not present copy as a complete legal privacy policy
```

Implement a bounded project notice consistent with canonical requirements.

It must clearly state:

```text
temporary pseudonymous session
general product use / clinical-intake processing requested
SwasthyaSetu is not an emergency service
does not grant referral sharing
does not grant research use
does not grant ABDM exchange
does not grant caregiver access
does not grant separate external-AI processing permission
```

Use exact server-controlled constants:

```text
purpose = GENERAL_PRODUCT_USE
scope = ["clinical_intake"]
notice_version = privacy-v1
```

Document final jurisdiction-specific notice as governance-deferred.

## 15. Explicit Consent Interaction

Require explicit action:

```text
unchecked agreement control
"I understand and agree to this use for this session."
```

Grant button disabled until agreement.

No pre-checked consent.

No dark patterns.

No bundled referral/research/AI consent.

## 16. Consent Grant BFF

`POST /api/onboarding/consent`

Client sends no subject/purpose/scope/version.

BFF derives:

```text
subject_type = SESSION
subject_id = HttpOnly session_id
purpose = GENERAL_PRODUCT_USE
scope = ["clinical_intake"]
notice_version = privacy-v1
Authorization bearer = HttpOnly token
```

Before creating a grant, check for existing active matching consent.

If active grant exists:

```text
treat as already consented
do not create duplicate
```

Disable duplicate submission while pending.

## 17. Consent Status BFF

`GET /api/onboarding/consent`

Use session cookies and subject-scoped backend listing.

Return minimized state:

```text
NOT_GRANTED
GRANTED
REVOKED
EXPIRED
SESSION_UNAVAILABLE
```

Optionally safe:

```text
notice_version
granted_at
```

Do not return raw collections or token.

## 18. Consent Revoke

Provide:

```text
Withdraw this consent
```

BFF:

```text
POST /api/onboarding/consent/revoke
```

Use server-controlled:

```text
reason = user_requested
```

Do not accept client reason text.

If multiple active matching grants somehow exist, revoke all matching active grants or report failure; never claim withdrawal while another active grant remains.

After revoke, `/encounter` must not show onboarding-ready.

## 19. Backend Error Handling

Create a small typed server-only backend client.

Requirements:

```text
bounded timeout using built-in AbortSignal.timeout or equivalent
no retry for side-effect POSTs
safe JSON parsing
recognized canonical error codes only
no raw backend exception/body to client
Cache-Control: no-store
```

Map common states safely.

Never log bearer values.

## 20. No Automatic Retry of Side Effects

Do NOT automatically retry:

```text
POST /sessions
POST /consents
POST /consents/{id}/revoke
POST /sessions/{id}/close
```

GET status/list may remain no-retry.

## 21. Client State

May hold only transient UI state:

```text
selected language
agreement checkbox
loading/error state
safe returned status
```

Must not hold:

```text
session_token
raw consent record collections
clinical data
future intake answers
```

No global state dependency.

## 22. Refresh / Continuity

Because credentials are transient HttpOnly session cookies:

```text
refresh preserves active onboarding within browser session
closing browser discards cookies
```

Do not add "remember me".

If cookies disappear, return honestly to session creation.

## 23. /encounter P6-B State

Do not create backend encounter.

Determine readiness from safe BFF state.

States:

```text
NO_SESSION -> direct user to /language
SESSION_ACTIVE_NO_CONSENT -> direct user to /consent
SESSION_ACTIVE_CONSENT_GRANTED -> onboarding ready; intake unavailable
BACKEND_UNAVAILABLE -> degraded state
```

Urgent help remains present.

## 24. Browser Storage

Preserve AC-P6-007.

Must remain absent:

```text
localStorage
sessionStorage
IndexedDB
Cache API
service worker storage
```

P6-B adds only transient HttpOnly session cookies containing:

```text
opaque session id
opaque session bearer
```

No health data, consent body, language text, demographics, or answers in cookies.

## 25. PWA Still Deferred

Do NOT implement:

```text
manifest
service worker
offline cache
install prompt
background sync
push
```

P6-C owns PWA.

## 26. Backend / Migration Boundary

Expected unchanged:

```text
backend/app/**
backend/migrations/**
backend/pyproject.toml
backend/uv.lock
```

Alembic head:

```text
p5b_0006
```

If integration exposes a genuine backend contract defect, stop and report it rather than silently changing P4/P5 behavior.

## 27. Dependencies

Expected unchanged:

```text
package.json
pnpm-lock.yaml
apps/patient-web/package.json
```

Use built-in:

```text
Next.js route handlers
cookies()
fetch
AbortSignal
React
```

No new dependency.

## 28. Unit Tests — Session BFF

Prove:

```text
POST session sends exact PSEUDONYMOUS backend body
token never appears in frontend JSON
cookies HttpOnly
SameSite Strict
cookies session-only
Secure in production
GET session forwards Authorization bearer
invalid/expired session clears cookies
close forwards bearer and clears cookies
cross-origin mutation rejected
backend URL missing -> safe 503
token never logged
```

Never snapshot secret values.

## 29. Unit Tests — Consent BFF

Prove:

```text
SESSION subject derived from cookies
client cannot control subject_type
client cannot control subject_id
client cannot control purpose
client cannot control scope
client cannot control notice_version
exact GENERAL_PRODUCT_USE + clinical_intake + privacy-v1 sent
existing active grant prevents duplicate
revoke uses user_requested
multiple active matching grants are all revoked or failure is surfaced
no raw backend body/token returned
```

## 30. Unit Tests — UI

Cover:

```text
/start real onboarding copy
/language English + Hindi
keyboard language controls
/consent unchecked agreement
grant disabled until agreement
loading/error/degraded states
granted state
withdraw action
/encounter readiness states
End private session
urgent help remains present
```

## 31. Real Playwright Journey — Critical

P6-B E2E must use real FastAPI + real PostgreSQL.

Update existing **Playwright Chromium** CI job, without adding a seventh job, to:

```text
start PostgreSQL using existing Compose
install locked backend dependencies
run alembic upgrade head
start backend
wait for /health/ready
set SWASTHYASETU_BACKEND_URL=http://127.0.0.1:8000
run Next Playwright web servers
run browser tests
clean up
```

Do not alter backend behavior.

## 32. Playwright Acceptance Journey

At minimum:

```text
open /
Get started
/start
Continue
/language
select English
create real PSEUDONYMOUS session
redirect /consent
check agreement
grant real GENERAL_PRODUCT_USE consent
redirect /encounter
see onboarding-ready + intake-not-yet-available state
```

Also verify:

```text
localStorage empty
sessionStorage empty
document.cookie does not reveal bearer
bearer cookie metadata says HttpOnly
bearer cookie is session-only
urgent help remains accessible
keyboard-only onboarding works
```

Never print cookie values.

## 33. Consent Revoke E2E

Real flow:

```text
active session + consent
open consent state
withdraw consent
backend consent becomes revoked
/encounter no longer ready
```

Do not automatically close session on consent withdrawal.

## 34. Session Close E2E

Test:

```text
active session
End private session
backend session closes
HttpOnly cookies cleared
subsequent status = NO_SESSION
```

Use fresh sessions for other tests.

## 35. Accessibility / Keyboard

Close AC-P6-005 with connected onboarding:

```text
/start
/language choice
continue
/consent agreement
grant
```

No trap; visible focus; understandable page headings.

Full P6-C audit remains deferred.

## 36. Privacy / Logging Audit

No logs containing:

```text
Authorization
session_token
cookie value
consent raw body
backend raw response
```

No client component should know `swasthyasetu_session_token`.

Keep token cookie access server-only.

## 37. CI

Keep exactly six jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

Playwright job may gain backend/PostgreSQL setup.

All six pass on final SHA.

## 38. Verification

Run:

```text
pnpm install --frozen-lockfile
pnpm frontend:format-check
pnpm frontend:lint
pnpm frontend:typecheck
pnpm frontend:test
pnpm frontend:build
pnpm e2e:list
```

For real E2E:

```text
start PostgreSQL
uv sync --locked --dev
alembic upgrade head
start backend
set SWASTHYASETU_BACKEND_URL=http://127.0.0.1:8000
pnpm e2e:test
```

Also run existing backend regression and Alembic drift checks.

Audit:

```text
git diff --check
lockfiles unchanged
backend code unchanged
migration files unchanged
Alembic head p5b_0006
no localStorage/sessionStorage/IndexedDB
no service worker/PWA work
no secrets in source/logging
```

## 39. Acceptance Status

Expected after successful P6-B:

```text
AC-P6-001 PASS
AC-P6-002 PASS
AC-P6-003 PASS
AC-P6-004 PASS
AC-P6-005 PASS
AC-P6-006 PASS
AC-P6-007 PASS
AC-P6-008 PASS
```

But:

```text
P6-B = COMPLETE
P6 overall = PARTIAL
```

P6 remains PARTIAL until P6-C.

## 40. Documentation

Update relevant:

```text
README.md
docs/frontend/README.md
REPOSITORY_TREE.txt
docs/03_REPOSITORY_STRUCTURE.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P6_B_ONBOARDING_SESSION_CONSENT.md
```

Document:

```text
SWASTHYASETU_BACKEND_URL
BFF boundary
HttpOnly transient session cookies
no localStorage
GENERAL_PRODUCT_USE / clinical_intake / privacy-v1 constants
final jurisdiction-specific privacy notice governance-deferred
PWA deferred
```

## 41. Progress Tracker

Before CI:

```text
P6-B = PARTIAL — REMOTE CI VERIFICATION PENDING
P6 = PARTIAL
```

After all six jobs pass:

```text
P6-B = COMPLETE
P6 = PARTIAL
next = P6-C — Accessibility + PWA Baseline
```

## 42. Commit / Push

```text
git add <P6-B files only>
git commit -m "feat: connect P6-B patient onboarding"
git push -u origin phase/p6-b-onboarding-session-consent
```

Do not merge.

## 43. Final Report

Return only:

```text
STATUS
BRANCH / GIT
ONBOARDING FLOW
LANGUAGE
SESSION BFF
COOKIE SECURITY
CONSENT FLOW
CONSENT REVOKE
SESSION CLOSE
BROWSER STORAGE
BACKEND / MIGRATION STATUS
DEPENDENCIES
TESTS
REAL E2E
VERIFICATION
CI
P6 ACCEPTANCE STATUS
DEVIATIONS
BLOCKERS / OPEN DECISIONS
PROGRESS TRACKER
MERGE
RECOMMENDED NEXT UNIT
```

`MERGE PERFORMED: NO`

Recommended next:

```text
P6-C — Accessibility + PWA Baseline
```

## 44. Success Definition

P6-B is complete only when:

- `/start` is a real onboarding step;
- `/language` creates a real pseudonymous session with chosen backend language preference;
- only PSEUDONYMOUS patient-web session creation is allowed;
- real FastAPI session creation is used;
- bearer token is never exposed to browser JavaScript after server receipt;
- bearer is held only in transient HttpOnly SameSite=Strict cookie storage;
- FastAPI receives bearer only via Authorization header;
- `/consent` records real SESSION GENERAL_PRODUCT_USE consent;
- purpose/scope/version are server-controlled;
- consent is explicit and never pre-checked;
- referral/research/ABDM/caregiver/external-AI consent is not bundled;
- duplicate active grant is avoided;
- withdrawal uses `user_requested` and leaves no matching active grant;
- session can be ended and cookies are cleared;
- `/encounter` reflects onboarding readiness without starting clinical intake;
- no localStorage/sessionStorage/IndexedDB/PWA cache exists;
- no health data is stored in cookies;
- keyboard-connected onboarding passes;
- real Playwright uses real FastAPI + PostgreSQL;
- no backend/schema/migration/dependency drift occurs;
- Alembic head remains `p5b_0006`;
- all six CI jobs pass;
- AC-P6-002, AC-P6-003, AC-P6-005 pass;
- P6-B is COMPLETE;
- P6 remains PARTIAL;
- branch is pushed and not merged.

Stop after P6-B.

## Implementation Record

```text
Executed: 2026-10-12
Branch: phase/p6-b-onboarding-session-consent
Base: 778459800d1f16dc69d7efaeb57907beac19217f
Scope: connected patient onboarding, en/hi session preference, same-origin session/consent BFF, withdrawal, close, readiness, and real PostgreSQL/FastAPI E2E.
Consent constants: SESSION / GENERAL_PRODUCT_USE / clinical_intake / privacy-v1
Cookies: transient HttpOnly SameSite=Strict; Secure in production and on non-loopback hosts
Duplicate guard: per-session process-local serialization plus authoritative pre-create recheck; cross-instance backend idempotency remains outside the fixed P6-B contract
Browser storage/PWA: absent; PWA remains P6-C
Dependencies/backend/schema/migrations: unchanged
Alembic head: p5b_0006
AC-P6-001..008: PASS locally
Remote CI: PASS — GitHub Actions run 38244030550; all six required jobs passed
P6-B: COMPLETE
P6 overall: PARTIAL
Next: P6-C — Accessibility + PWA Baseline
```
