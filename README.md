# SwasthyaSetu AI

Unified multimodal clinical-intake, mental-health triage, document-intelligence, care-navigation,
self-care governance, interoperability, and ML/QML research platform.

## Current status

**P1 Repository + Tooling Foundation COMPLETE. P2 Shared Platform Kernel COMPLETE. P3 Persistence + Events + Jobs COMPLETE. P4-A Sessions is in progress pending remote CI verification.**

The repository includes a locked Python 3.12+/FastAPI backend with typed configuration, health
endpoints, request correlation, structured logging, an async PostgreSQL persistence runtime,
explicit Alembic migrations, and backend quality checks. It also includes three strictly typed
Next.js application workspaces, shared UI primitives, frontend unit testing, and Playwright smoke
tests. No clinical rules, product workflows, authentication, domain tables, external providers,
production credentials, or predictive models are implemented.

P4-A adds the sessions bounded context: pseudonymous and kiosk session creation, opaque bearer
tokens protected by SHA-256 verifiers at rest, PostgreSQL-authoritative expiry/close state, and
versioned `/api/v1/sessions` create/read/close endpoints. It does not add authenticated identity,
actors, roles, consent, patients, recovery, JWT, cookies, or frontend token storage.

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
