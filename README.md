# SwasthyaSetu AI

Unified multimodal clinical-intake, mental-health triage, document-intelligence, care-navigation, self-care governance, interoperability, and ML/QML research platform.

## Current status

**P1-A backend and P1-B frontend engineering foundations are complete; overall P1 remains partial.**

The repository now includes a locked Python 3.12+/FastAPI backend foundation with typed
configuration, health endpoints, request correlation, structured logging, and backend quality
checks. It also includes three strictly typed Next.js application workspaces, shared UI primitives,
frontend unit testing, and a Playwright smoke-test skeleton. No clinical rules, product workflows,
authentication, persistence, external providers, production credentials, or predictive models are
implemented.

## Read first

1. `docs/00_PROJECT_MASTER_SPEC.md`
2. `docs/01_PRODUCT_REQUIREMENTS.md`
3. `docs/02_SYSTEM_ARCHITECTURE.md`
4. `docs/03_REPOSITORY_STRUCTURE.md`
5. `docs/29_ENGINEERING_STANDARDS.md`
6. `docs/34_MASTER_IMPLEMENTATION_PLAN.md`

Backend setup and verification commands are documented in `backend/README.md`.
Frontend setup and verification commands are documented in `docs/frontend/README.md`.

The next coding unit is **P1-C: Docker, local PostgreSQL, CI, and quality-gate foundation**. It
remains separate and has not been implemented.
