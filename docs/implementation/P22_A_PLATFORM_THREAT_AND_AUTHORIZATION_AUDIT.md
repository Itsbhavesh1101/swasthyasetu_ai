# P22-A Platform Threat and Authorization Audit

## 1. Purpose, revision, status, and evidence tier

**As-of revision:** `main @ 55cbcc9c0ea4680366302919dbacd0240f6a5c5f`, 30 October 2026.
**Status:** unsigned bounded technical audit and synthetic regression evidence only.
**Authority:** this report inventories and tests existing P4-P7 behavior. It is not an institutional,
AppSec, privacy, legal, clinical, production, pilot, or risk-acceptance decision.

This report is new P22-A evidence. It is distinct from the proposal-level Pre-P22 gap assessment and
readiness review, and it does not promote the P11-focused unsigned drafts in
`docs/27_SECURITY_ARCHITECTURE.md` or `docs/28_THREAT_MODEL.md` into a platform approval. Accepted
ADRs, canonical requirements, module contracts, and the as-built source remain authoritative.

Evidence labels used below are **AS-BUILT/VERIFIED**, **PROPOSED/UNAPPROVED**, **ABSENT**,
**UNKNOWN**, and **HUMAN DECISION PENDING**. All live P22 acceptance remains unverified.

## 2. As-built asset, data-flow, and trust-zone map

### 2.1 Current deployed-shaped path (not a deployment assertion)

| Zone / flow | Current asset and boundary | Evidence | Status / limit |
|---|---|---|---|
| Patient browser | Patient Web uses same-origin BFF handlers; opaque session credentials are transient `HttpOnly`, `SameSite=Strict`, `Path=/` cookies and bearer values remain server-side. Browser persistence and service workers are prohibited by the implemented tests. | `apps/patient-web/app/api/`; `apps/patient-web/lib/onboarding/server.ts`; `apps/patient-web/lib/intake/server.ts`; `tests/e2e/patient.spec.ts`; `docs/26_PRIVACY_CONSENT_SPEC.md` | **AS-BUILT/VERIFIED, bounded.** Browser/device compromise and final production headers/topology remain owner-review questions. |
| BFF -> FastAPI | BFF converts the controlled cookie to an `Authorization: Bearer` request with bounded backend requests. The backend bearer parser requires one exact bearer value. | `apps/patient-web/lib/onboarding/server.ts`; `apps/patient-web/lib/intake/server.ts`; `backend/app/api/security/bearer.py` | **AS-BUILT/VERIFIED by source/tests.** Production gateway, proxy, TLS termination, WAF, and rate-limit topology are **UNKNOWN**. |
| HTTP middleware | A generated/validated request ID and content-free method, route template, status, and duration are recorded. Request bodies, cookies, bearer values, and query values are not read for logging. Sensitive-route responses are `no-store`. | `backend/app/api/middleware/request_context.py`; `backend/app/api/errors/handlers.py`; `backend/tests/test_request_context.py` | **AS-BUILT/VERIFIED, bounded.** A platform log-sink and production access-log review is **HUMAN DECISION PENDING**. |
| Sessions / identity | Pseudonymous sessions use high-entropy opaque tokens stored as hashes. Identity has provider-neutral contracts and server-side `ActorContext`; no client header creates that context. A production IdP is unconfigured. | `backend/app/modules/sessions/`; `backend/app/modules/identity/`; `backend/app/api/security/authorization.py`; `backend/app/main.py`; `backend/tests/test_identity.py`; `backend/tests/integration/test_postgres_sessions.py` | Pseudonymous path **AS-BUILT/VERIFIED**. Production IdP, institution assignment, privileged proofing, and clinician MFA are **ABSENT/UNAPPROVED**. |
| Consent | Central records bind subject type/ID, purpose, scope, notice version, status, and optional expiry. Session grant/revoke/list uses the exact session bearer; actor self-access depends on trusted context. | `backend/app/modules/consent/api.py`; `backend/app/modules/consent/application.py`; `backend/tests/integration/test_postgres_consent.py`; `docs/26_PRIVACY_CONSENT_SPEC.md` | `GENERAL_PRODUCT_USE` + `clinical_intake` for a SESSION is **AS-BUILT/VERIFIED**. Consent is non-transitive; external processing, referral, research, and PATIENT-subject activation remain **ABSENT/UNAPPROVED**. |
| Encounter / intake | A pseudonymous general-intake encounter is bound to one session. Every P7 intake start/read/answer/complete loads the object, validates the exact owning session, and checks active exact-subject consent. Writes use explicit versions and PostgreSQL transactions. | `backend/app/modules/encounters/api.py`; `backend/app/modules/clinical_intake/api.py`; `backend/app/modules/clinical_intake/application.py`; `backend/app/modules/clinical_intake/infrastructure.py`; `backend/tests/integration/test_postgres_clinical_intake_api.py` | **AS-BUILT/VERIFIED** for synthetic P7 engineering content. Production clinical content remains governance-deferred. |
| PostgreSQL / outbox | PostgreSQL is the transactional source of truth for sessions, consent, encounters, and intake. The outbox exists, but no background dispatcher is auto-started by FastAPI. | `backend/app/shared/persistence/`; `backend/app/events/outbox.py`; `backend/migrations/`; `.github/workflows/ci.yml`; accepted ADR-006/ADR-008 | Persistence foundation **AS-BUILT/VERIFIED**. Production HA, backup/restore, retention, purge, and durable worker operation are **ABSENT/UNKNOWN**. |
| Inactive boundaries | Clinician/admin portals are shells; real privileged APIs, IdP, document upload/storage/OCR, provider/referral, external AI activation, speech, FHIR/ABDM, research runtime, durable workers, and production deployment are not active P4-P7 behavior. | `apps/clinician-web/`; `apps/admin-web/`; `docs/implementation/38_PROGRESS_TRACKER.md`; P8-P24 readiness documents | **ABSENT, BLOCKED, or PROPOSED/UNAPPROVED**. They are not represented here as deployed controls. |

### 2.2 Data classes and present collection boundary

| Data class | Present handling | Future/nonexistent boundary |
|---|---|---|
| Credentials / opaque session bearer | Returned once at session creation, transported by BFF cookie/server request, persisted only as a hash, excluded from response errors/log assertions. | Production IdP/JWT/OIDC, password, OTP, and real clinician credentials are **ABSENT**. |
| Consent metadata | PostgreSQL record of exact subject, purpose, scope, notice, status, timestamps and actor/session linkage. | Jurisdiction-specific notice approval, external processing, referral/research purposes, and final retention are **HUMAN DECISION PENDING**. |
| Structured clinical narrative | P7 answers and deterministic draft fields are stored under encounter/session authorization and consent. Test content is synthetic. | Approved production question content and real-patient processing are not authorized by this audit. |
| Raw documents | No current upload API, document table, or activated storage path. | P11 upload/storage/OCR remains blocked; no future raw-document flow is claimed as present. |
| Extracted candidates | Detached synthetic P8/P11 contracts exist, but no live clinical authority or patient runtime activation. | Real extraction/provider/model processing is blocked. |
| Audit / telemetry traces | Request correlation, content-free access metadata, metrics primitives, and transactional consent/outbox events exist. | A complete tamper-evident audit product, production exporter, access policy, retention, purge, and reviewed dashboards are absent/unapproved. |

## 3. Current API attack surface and authority matrix

| Current route group | Available authority | Subject/object and consent enforcement | Mutation | Expected denial / evidence | Missing or unapproved |
|---|---|---|---|---|---|
| `POST /api/v1/sessions` | No prior identity; creates a pseudonymous session | Strict request schema; server generates opaque token and ID | Create session | Validation envelope; `no-store`; session lifecycle tests in `test_postgres_sessions.py` | Abuse rate limit, device binding, production gateway controls |
| `GET /sessions/{id}`, `POST /sessions/{id}/close` | Exact opaque bearer | `sessions.validate` binds token hash to path session and checks lifecycle | Close only | Missing/wrong token -> authentication failure; lifecycle tests | Recovery and production identity are absent |
| `POST /consents`, `GET /consents`, `POST /consents/{id}/revoke` | Exact session bearer for SESSION; trusted server `ActorContext` for ACTOR self | Exact subject; listing must be scoped; purpose/scope checked by consumers | Grant/revoke | 401/403/404 safe envelope depending contract; Postgres consent tests include cross-subject/revoke/atomicity | PATIENT management, research purpose, referral sharing, external processing unapproved |
| `POST /encounters/general-intake`; pseudonymous `GET` and terminal routes | Exact bearer for the encounter's stored session | Existing encounter is loaded, then owning session token is validated | Create/find, complete, abandon | Cross-session bearer -> 401; P22-A test proves GET/abandon denial and no version/state change | Institution assignment and production clinician authority absent |
| Patient-linked encounter routes | Trusted `ActorContext` and self-subject permission | `identity.authorize.require_self_subject`; session must still validate at create | Create/read/transition | Anonymous/other subject -> 401/403; `test_postgres_p5c.py` | Production IdP, clinician role/MFA and institution tenancy unconfigured |
| `POST /encounters/{id}/intake`, `GET /intakes/{id}`, answer/complete | Exact owning-session bearer | Load encounter/intake; validate stored session; exact active `GENERAL_PRODUCT_USE` + `clinical_intake`; exact encounter/intake binding | Start, answer, complete | 401/403/404/409 by typed contract; current Postgres integration suite | Production clinical pack and PATIENT-subject continuity unapproved |
| Patient self/profile/timeline and provenance reads | Trusted `ActorContext` with self-subject permission | Server context subject must equal path patient; provenance service reads source-backed records | Patient create and reads; fact correction per route | Existing identity/P5C tests cover basic IDOR and correction authority | No production authentication provider or clinician queue |

The backend does not parse `X-Actor-ID`, `X-Roles`, or `X-MFA-Verified` into authority. Tests may
send them only to prove they remain inert. Frontend visibility is not treated as authorization.
Institution assignment, clinician MFA, a production IdP, and research-purpose authority are
**ABSENT/UNAPPROVED**, not working controls.

## 4. Threat and control-gap table

STRIDE terms are descriptive tags only; they are not proof or a risk score.

| Threat | Evidence | Actual behavior | Missing proof | Owner class | Separate mitigation, if later authorized | Remaining risk / STOP |
|---|---|---|---|---|---|---|
| Stolen bearer (spoofing) | Sessions domain and Postgres tests | A valid bearer has bearer semantics until close/expiry; only its hash is stored | Device compromise/replay controls and production expiry policy validation | Identity/institution + AppSec | **PROPOSED/UNAPPROVED:** reviewed session hardening and incident revocation design | Human risk decision required; STOP production claims |
| Missing/invalid bearer | Bearer parser; P22-A test | Fails 401 with safe, non-cacheable envelope | Edge/proxy behavior in a real topology | AppSec/platform | **PROPOSED/UNAPPROVED:** deployment-edge negative tests | STOP if any upstream creates trusted identity from headers |
| Cross-session IDOR: session/consent/encounter/intake | Session, consent, P5C, P7C tests; new pre-intake P22-A test | Exact stored subject/session is revalidated; tested denials do not mutate target | Exhaustive route/property fuzzing and production IdP subjects | AppSec + domain owners | **PROPOSED/UNAPPROVED:** separately scoped comprehensive object matrix | Bounded evidence is not AC-P22-002 live acceptance |
| Guessed object identifiers (information disclosure) | UUID objects and typed error handlers | Guess alone grants no authority | Enumeration equivalence across unknown versus foreign IDs is not exhaustively proven | AppSec/privacy | **PROPOSED/UNAPPROVED:** approved enumeration contract tests | Owner must decide acceptable disclosure contract |
| Forged actor/role/MFA headers (elevation) | `get_actor_context`; identity test; P22-A test | Headers are ignored; only server-injected context is authority | Future reverse-proxy/IdP integration trust boundary | Identity/AppSec | **PROPOSED/UNAPPROVED:** signed issuer/topology and header-stripping design | No production IdP/MFA; STOP privileged activation |
| Revoked consent (elevation/privacy) | Consent service and `test_continued_access_rechecks_session_consent_and_exact_subject` | Protected intake rechecks consent; revoke blocks later operations | In-flight cross-service consistency and future purposes | Privacy/consent + platform | **PROPOSED/UNAPPROVED:** transaction/consistency decision per operation | No inference from authentication/session creation |
| Closed/expired session | Sessions service and P7 continued-access test | Validate rejects non-active/expired sessions | Production clock/expiry operations and fleet consistency | Identity/platform | **PROPOSED/UNAPPROVED:** operational expiry/revocation rehearsal | STOP production assurance |
| Malformed/hostile schema (tampering) | Pydantic `extra="forbid"`, error handlers, unit/API tests | Invalid structures fail with stable validation envelope without submitted values | Broad fuzzing, request-size/rate boundaries | AppSec/API owners | **PROPOSED/UNAPPROVED:** bounded schema fuzz and edge size tests | Upload/parser paths do not exist; AC-P22-005 unverified |
| Stale/versioned writes (tampering) | Encounter/intake repositories and concurrency tests | Optimistic versions and transactions reject stale writes | Full multi-instance/chaos evidence | Domain/platform | **PROPOSED/UNAPPROVED:** concurrency and recovery review | No exactly-once claim |
| BFF cookie/storage/error leak (disclosure) | Patient BFF; E2E storage tests; error/middleware tests; P22-A log assertion | HttpOnly/Strict cookies, no browser persistence, no-store errors; content-free request logger | Production browser/proxy/access logs, CSP and third-party scripts | Frontend/AppSec/privacy | **PROPOSED/UNAPPROVED:** production header/topology and manual browser review | Current evidence is bounded to repository behavior |
| Optional AI/model/provider (spoofing/tampering/disclosure) | P8/P9 synthetic isolated contracts; flags safe-off | No approved patient-facing activation; P7 deterministic path is independent | Real provider trust, egress, retention, failure and clinical approval | Clinical/privacy/vendor/AppSec | **PROPOSED/UNAPPROVED:** owner-approved staged gate only | Preserve P8-C/P9-C blockers; STOP activation |
| Outbox/worker (tampering/repudiation/availability) | Transactional outbox and process-local job contracts | Atomic event persistence exists; no worker auto-start, no exactly-once claim | Durable dispatch identity, retry abuse, payload retention, operations | Platform/SRE/AppSec | **PROPOSED/UNAPPROVED:** P22-D operational threat tests | No durable worker/deployment proof |
| Logging/audit (disclosure/repudiation) | Request middleware, consent events, unit tests | Generic logger records content-free request metadata | Platform-wide production sink/access/retention review and audit completeness | Privacy/AppSec/audit/SRE | **PROPOSED/UNAPPROVED:** P22-B logging review and approved audit scope | AC-P22-004 remains unverified |
| Retention/purge and holds (disclosure/denial) | Requirements/readiness documents only | No implemented platform purge workflow | Schedule, legal holds, backup deletion, failure recovery | Privacy/records/data/SRE | **PROPOSED/UNAPPROVED:** P22-C after signed policy | AC-P22-007/008 unverified; STOP deletion claims |
| Abuse/flood (denial) | Canonical requirement only | No application rate limiter identified | Approved endpoint budgets and deployment-edge topology | AppSec/SRE/product | **PROPOSED/UNAPPROVED:** P22-B rate-limit design/tests | AC-P22-006 unverified; no load/flood performed |

No CVSS or arbitrary severity is assigned. Any disposition requires the owner docket below.

## 5. Test and evidence matrix

### 5.1 New evidence

| Test | Isolated setup | Operations and expected result | Non-mutation/privacy proof | Command/result |
|---|---|---|---|---|
| `test_cross_session_cannot_start_read_or_transition_another_encounter` | Existing `intake_client` uses `SWASTHYASETU_TEST_DATABASE_URL`, migrates a dedicated local PostgreSQL database, truncates governed tables around the test, and creates two synthetic sessions with distinct consent/encounters. | B attempts A's pre-intake start, encounter GET, and abandon; missing/invalid bearer and forged actor/role/MFA headers also attempt start. All fail exact current contract with 401. A then starts and reads successfully. | Target encounter status/version unchanged; zero A intake/questionnaire rows and zero answer rows; safe canonical error, `Cache-Control: no-store`, no token/canary/admin-role reflection in responses or `swasthyasetu.http` capture. | `python -m pytest tests/integration/test_postgres_clinical_intake_api.py::test_cross_session_cannot_start_read_or_transition_another_encounter -q` -> **1 passed** on dedicated disposable PostgreSQL. |

No security failure or reproduction ID was produced. The test proves this exact synthetic boundary,
not exhaustive platform authorization or live deployment behavior.

### 5.2 Existing evidence reused, not duplicated

- `test_real_http_flow_is_atomic_versioned_idempotent_and_session_bound`: cross-session read of an
  already-created intake plus atomic/version behavior.
- `test_continued_access_rechecks_session_consent_and_exact_subject`: exact-subject consent,
  revocation, and closed-session rechecks.
- `test_completed_draft_remains_readable_after_encounter_is_terminal`: terminal-state read contract.
- `test_real_permission_guard_enforces_auth_permission_and_mfa` and
  `test_real_self_subject_guard_prevents_basic_idor`: server-context permission/MFA and subject IDOR.
- PostgreSQL session/consent/P5C integration suites: token lifecycle, consent atomicity/scoping, and
  patient/encounter/provenance authorization boundaries.
- `test_request_context.py` and `tests/e2e/patient.spec.ts`: content-free logging and bounded browser
  cookie/storage behavior.

Full-suite and exact-feature-SHA CI results belong in the PR/final execution report; passing them
does not turn the unsigned technical audit into live acceptance.

## 6. Acceptance traceability

| Criterion (exact canonical text) | Present bounded evidence | Missing live acceptance / owner need |
|---|---|---|
| AC-P22-001 — Threat model exists and reflects current architecture. | This current-source audit supplies an unsigned platform threat/control-gap draft. | Qualified AppSec, architecture, privacy and institutional review/signoff; deployed topology validation. **LIVE NOT VERIFIED.** |
| AC-P22-002 — Backend authorization/object-level access tests pass. | Existing suites plus the new pre-intake cross-session PostgreSQL HTTP regression. | Approved comprehensive route/role/object matrix and exact deployed-identity evidence. **LIVE NOT VERIFIED.** |
| AC-P22-003 — Secrets are absent from repository. | CI/local Gitleaks may provide point-in-time scanner evidence. | Qualified review, history/scope decision and credential governance. **LIVE NOT VERIFIED.** |
| AC-P22-004 — Sensitive logging review completed. | Source and bounded logger assertions show content-free application request logging. | Platform-wide production logs, sinks, access, retention, proxy/runtime logs and signed review. **LIVE NOT VERIFIED.** |
| AC-P22-005 — Upload security controls tested. | No upload runtime is active. | Approved upload architecture/controls and adversarial tests after separate authorization. **LIVE NOT VERIFIED.** |
| AC-P22-006 — Rate limits exist for abuse-prone endpoints. | Requirement and gap identified. | Endpoint budgets, implementation and tests in approved topology. **LIVE NOT VERIFIED.** |
| AC-P22-007 — Retention/purge workflow executes successfully. | No workflow exists. | Signed schedule/hold policy, implementation and execution evidence. **LIVE NOT VERIFIED.** |
| AC-P22-008 — Purge failure is observable. | Metric name/design prose is not execution proof. | Implemented failure path, alert ownership and rehearsal evidence. **LIVE NOT VERIFIED.** |
| AC-P22-009 — LLM/OCR/provider/integration failure modes are tested. | Synthetic isolated component tests exist; live integrations are disabled. | Approved integration inventory, full deployed failure matrix and owner acceptance. **LIVE NOT VERIFIED.** |
| AC-P22-010 — Kill switches work for defined high-risk optional features. | Safe-off feature flags and isolated tests exist for some synthetic features. | Owner-defined high-risk inventory and exact deployed switch rehearsal. **LIVE NOT VERIFIED.** |
| AC-P22-011 — High/critical security findings are resolved or formally accepted before pilot. | This audit does not assign severity or accept findings. | Approved rubric, independent assessment, accountable dispositions and release-board evidence. **LIVE NOT VERIFIED.** |

All **LIVE AC-P22-001..011 remain NOT VERIFIED**. P23 and P24 remain **NOT STARTED** and no
release/pilot is authorized.

## 7. Unsigned owner decision docket

| Accountable reviewer class | Required decision and evidence | Status |
|---|---|---|
| Identity / institution | Deployment identity model, issuer trust, session policy, privileged actor proofing, institution/tenant assignment, MFA requirement and recovery | **PENDING — no signer named** |
| AppSec / security architecture | Exact attack-surface scope, object matrix, proxy/header boundary, enumeration contract, rate limits, risk rubric, scanner scope, finding disposition and review interval | **PENDING — no signer named** |
| Privacy / consent / legal | Purpose, lawful/governance basis, notice, consent granularity, recipient/egress, logging, retention, deletion, data-subject and incident obligations | **PENDING — no signer named** |
| Data governance / records | Authoritative records, classification, minimization, retention schedule, holds, backup deletion, purge verification and audit preservation | **PENDING — no signer named** |
| Clinical / safety | Which future clinical flows may be assessed, safe-off behavior, approved content/policy authority, escalation and evidence limitations | **PENDING — no signer named** |
| Platform / SRE / incident | Exact deployment topology, secret custody, network controls, observability access, HA/recovery objectives, incident ownership, rollback/kill-switch rehearsal | **PENDING — no signer named** |
| Independent reviewer / release | Time-bound independent review, evidence SHA/environment, residual-risk dispositions, expiry/re-review conditions and separation from pilot decision | **PENDING — no signer named** |

No name, signature, decision, severity, disposition, validity window, or approval is invented.

## 8. Residual risks, separated next steps, and final STOP

Owner-review questions, ranked by dependency and blast radius rather than invented severity:

1. Identity/institution and AppSec: what exact production issuer, proxy/header trust, session lifetime,
   privileged actor proofing, institution boundary and MFA policy will govern every route?
2. Privacy/records/AppSec: which data purposes, recipients, logs, retention/hold/deletion rules and
   breach duties apply, and what proof closes consent and purge gaps?
3. AppSec/platform: which endpoints are abuse-prone, what budgets apply, where are limits enforced,
   and how are failure/lockout/availability effects tested without harming users?
4. AppSec/domain owners: what complete route-role-subject-object matrix and enumeration contract
   must pass beyond the bounded current P4-P7 suite?
5. Platform/SRE/incident: what deployed topology, secret manager, backup/restore, telemetry access,
   kill-switch, provider outage and recovery evidence is required?
6. Clinical/privacy/vendor/release: which optional provider or clinical path, if any, may advance only
   after its independent content, safety, privacy, security and human approvals?

Potential P22-B (control implementation), P22-C (retention/purge), P22-D (switch/resilience), and
P22-E (full regression/independent closure) are separate requests requiring new authorization and
owner decisions. P7 deterministic/manual operation is unchanged. P23/P24 remain not started.

**FINAL STOP:** This report authorizes no runtime change, remediation, deployment, external scan,
real-data activity, optional integration, clinical activity, retention policy, finding acceptance,
P23/P24 work, pilot, or release decision. Human approvals: **NONE**.
