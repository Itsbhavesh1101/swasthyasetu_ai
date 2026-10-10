# SwasthyaSetu AI

Unified multimodal clinical-intake, mental-health triage, document-intelligence, care-navigation, self-care governance, interoperability, and ML/QML research platform.

## Current status

**P1 Repository + Tooling Foundation COMPLETE. P2-B COMPLETE; overall P2 PARTIAL.**

The repository now includes a locked Python 3.12+/FastAPI backend foundation with typed
configuration, health endpoints, request correlation, structured logging, and backend quality
checks. It also includes three strictly typed Next.js application workspaces, shared UI primitives,
frontend unit testing, and a Playwright smoke-test skeleton. No clinical rules, product workflows,
authentication, persistence, external providers, production credentials, or predictive models are
implemented. P1-C adds a non-root backend container, a local PostgreSQL development service,
cross-platform quality gates, real Chromium smoke execution, mandatory security scans, and the
baseline GitHub Actions workflow.

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

P2-A provides shared primitives, errors, and typed configuration. P2-B adds immutable module
manifests, typed capability keys, explicit compile-time module/provider registration, dependency
validation, and sealed per-application registries. All mandatory feature-branch CI jobs passed.
The next coding unit is **P2-C — Observability & Feature Flags**; it is not implemented.
