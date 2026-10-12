# SwasthyaSetu AI

Unified multimodal clinical-intake, mental-health triage, document-intelligence, care-navigation,
self-care governance, interoperability, and ML/QML research platform.

## Current status

**P1 Repository + Tooling Foundation COMPLETE. P2 Shared Platform Kernel COMPLETE. P3 Persistence + Events + Jobs COMPLETE. P4 Identity + Sessions + Consent COMPLETE. P5 Patient + Encounter + Provenance COMPLETE. P6 Patient Web Foundation PARTIAL (P6-A and P6-B COMPLETE).**

The repository includes a locked Python 3.12+/FastAPI backend with typed configuration, health
endpoints, request correlation, structured logging, an async PostgreSQL persistence runtime,
explicit Alembic migrations, and backend quality checks. It also includes three strictly typed
Next.js application workspaces, shared UI primitives, frontend unit testing, and Playwright smoke
tests. No clinical safety rules, real external identity provider, production credentials, or
predictive models are implemented.

P4-A adds the sessions bounded context: pseudonymous and kiosk session creation, opaque bearer
tokens protected by SHA-256 verifiers at rest, PostgreSQL-authoritative expiry/close state, and
versioned `/api/v1/sessions` create/read/close endpoints. It does not add authenticated identity,
authenticated identity activation, consent, patients, recovery, JWT, cookies, or frontend token
storage. P4-B adds PII-free actors and authoritative roles, provider-neutral authentication
contracts, trusted actor context resolution, and deny-by-default server-side authorization with
explicit MFA and self-subject gates. The real IdP remains unconfigured and replaceable; no login or
identity-management HTTP API is exposed.

P4-C adds purpose-specific consent grants for SESSION and ACTOR subjects, centralized exact-purpose
and scope-subset checks, revocation, subject-scoped listing, and minimal transactional outbox
events. SESSION authorization delegates to `sessions.validate`; ACTOR authorization uses trusted
server-side `ActorContext`. PATIENT consent remains deliberately unavailable until P5 establishes
patient ownership and authorization. General product consent never implies referral-sharing
consent, and no public consent-check endpoint is exposed.

P5-A adds the framework-independent Patient, Encounter, provenance, and typed clinical-fact domain.
It includes explicit encounter transitions, UTC and decimal invariants, privacy-safe identifiers,
and explicit fact supersession that fails closed when lower-trust data attempts to replace a
clinician-confirmed fact. This domain-only unit adds no SQLAlchemy model, table, migration, API,
runtime module registration, timeline service, or PATIENT-subject consent activation. P5-B adds the
PostgreSQL persistence adapters, typed/versioned clinical-value mapping, subordinate medication,
allergy, and observation projections, and explicit migration `p5b_0006`. It adds no API or runtime
capability, and PATIENT-subject consent remains deferred.

P5-C activates explicit `patients`, `encounters`, and `provenance` runtime modules. Authenticated
patients can create/read their own profile, read bounded fact summaries, and create/read/transition
self-owned encounters; pseudonymous encounters remain bound to an exact session bearer. The
longitudinal timeline merges bounded fact and encounter reads through public capabilities in
`occurred_at DESC, entry_type ASC, entry_id ASC` order with a versioned opaque cursor. No schema,
migration, dependency, frontend, or PATIENT-consent activation is included.

P6-A replaces the patient placeholder with a responsive, patient-specific application shell,
accessible UI states, honest planned-route shells, and a persistent urgent-help entry point. The
urgent route contains no invented helpline or provider data. This unit adds no backend calls,
browser persistence, working language/consent flow, authentication, PWA behavior, or dependencies;
those capabilities remain phase-gated.

P6-B connects `/start`, `/language`, `/consent`, and `/encounter` through same-origin Next.js route
handlers to the existing FastAPI session and consent contracts. The browser receives only transient
`HttpOnly`, `SameSite=Strict` session cookies; the bearer is forwarded server-side only through the
`Authorization` header and is never returned to client JavaScript. The backend base URL is supplied
server-side as `SWASTHYASETU_BACKEND_URL`. Consent uses fixed `GENERAL_PRODUCT_USE`,
`clinical_intake`, and `privacy-v1` values, with withdrawal and private-session close controls.
Matching grants are rechecked inside a process-local, per-session serialized section before create;
the fixed backend contract does not provide cross-instance consent idempotency.
Jurisdiction-specific final notice approval and all PWA/offline behavior remain deferred.

P1-C provides the non-root backend container, local PostgreSQL service, cross-platform quality
gates, Chromium smoke execution, security scans, and GitHub Actions workflow. P2 provides shared
types/errors/configuration, compile-time module and capability registration, safe/off feature flags,
and privacy-safe in-process OpenTelemetry. P3-A adds only the persistence substrate: zero domain
models, one empty baseline migration, explicit migration commands, PostgreSQL transaction tests,
and database-aware readiness. P3-B adds a versioned internal event envelope, explicit in-process
publisher, PostgreSQL transactional outbox, and manually invoked retry/status dispatcher. It uses
at-least-once delivery semantics, so consumers with side effects remain responsible for
idempotency. No dispatcher starts with FastAPI.
P3-C adds provider-neutral immutable job contracts, a non-durable process-local dispatcher with an
explicit deterministic `run_once` worker, a provider-neutral object-storage port, and a controlled
development/test local-filesystem adapter. No worker daemon or storage service is activated.

## Read first

1. `docs/00_PROJECT_MASTER_SPEC.md`
2. `docs/01_PRODUCT_REQUIREMENTS.md`
3. `docs/02_SYSTEM_ARCHITECTURE.md`
4. `docs/03_REPOSITORY_STRUCTURE.md`
5. `docs/29_ENGINEERING_STANDARDS.md`
6. `docs/34_MASTER_IMPLEMENTATION_PLAN.md`

Backend setup and verification commands are documented in `backend/README.md`.
Frontend setup and verification commands are documented in `docs/frontend/README.md`.
Local container and PostgreSQL commands are documented in `deployments/local/README.md`.
