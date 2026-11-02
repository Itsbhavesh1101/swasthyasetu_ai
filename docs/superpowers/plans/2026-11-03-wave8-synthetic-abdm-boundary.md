# Wave 8 Synthetic ABDM Boundary Preview Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a working local/test-only synthetic ABDM failure-boundary preview with zero egress and no official or clinical effect.

**Architecture:** A separate engineering module composes the existing P17-A contracts through a private deterministic adapter and exposes a minimized no-store response. Patient web consumes it through an exact-schema same-origin BFF and renders an input-free, non-actionable page. Existing P17-D PostgreSQL tests remain the failure-isolation proof.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, Next.js 16, TypeScript, Vitest, Playwright.

**Spec:** `docs/superpowers/specs/2026-11-03-wave8-synthetic-abdm-boundary-design.md`

## Global Constraints

- Only fixed, content-free synthetic engineering tokens; no real or realistic identifier or data.
- Default off and register only in `LOCAL` and `TEST`; protected environments fail before request construction.
- No official ABDM operation, ABHA behavior, sandbox, credential, network, FHIR payload, consent, persistence, migration, dependency, or production activation.
- Response and UI must make zero egress, no patient processing, no local intake access/mutation, and no conformance or exchange authority machine-verifiable.
- Alembic head remains `p7a_0007`.

## Review Focus

- A forged accepted state must be rejected by backend and BFF literal schemas.
- Added payload, identifier, endpoint, or credential fields must be rejected as extra keys.
- Enabling the flag in staging, pilot, or production must not register the endpoint.
- Missing/hostile backend responses must degrade to a minimized unavailable response.
- Browser presentation must create no storage, input, action control, or external link.

---

### Task 1: Backend composition and strict API

**Files:**
- Create: `backend/app/modules/engineering_abdm_demo/{__init__,application,api,public}.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_engineering_abdm_demo.py`

**Interfaces:**
- Consumes: `SyntheticABDMRequest`, `SyntheticABDMResult`, `ABDMAdapterPort`, validation helpers.
- Produces: `GET /api/v1/engineering-demo/abdm-preview` and `EngineeringABDMPreviewView`.

- [ ] Write backend tests for exact rejection/unavailable results, zero effects, protected denial, registration gating, no-store response, and hostile mutations.
- [ ] Run the focused tests and confirm they fail because the module is absent.
- [ ] Implement the minimal fixed service, private adapter, literal response model, module registration, and main wiring.
- [ ] Run focused P17 and demo tests; expect all pass.
- [ ] Commit the backend task.

### Task 2: Strict BFF and accessible page

**Files:**
- Create: `apps/patient-web/lib/abdm-demo/{contracts,server}.ts`
- Create: `apps/patient-web/app/api/engineering-demo/abdm-preview/route.ts`
- Create: `apps/patient-web/components/abdm-synthetic-preview.tsx`
- Create: `apps/patient-web/app/abdm/page.tsx`
- Test: `apps/patient-web/tests/abdm-demo-{bff,ui}.test.ts{,x}`

**Interfaces:**
- Consumes: the exact backend response from Task 1.
- Produces: same-origin BFF response and `/abdm` presentation.

- [ ] Write BFF/UI tests for exact parsing, hostile stronger claims/extra keys, fail-closed notice, no controls, one home link, and accessible headings.
- [ ] Run focused Vitest and confirm failure because the files are absent.
- [ ] Implement the strict BFF, contracts, route, component, and page.
- [ ] Run focused Vitest; expect all pass.
- [ ] Commit the frontend task.

### Task 3: Browser evidence, configuration, tracker, and whole-branch verification

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `deployments/local/compose.yaml`
- Modify: `tests/e2e/patient.spec.ts`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**
- Consumes: Task 1 endpoint and Task 2 page.
- Produces: enabled local/CI demo, real-browser evidence, and tracker record.

- [ ] Add a Playwright test proving exact failure-boundary copy, no controls/external links, and zero browser storage; run before enabling the feature and confirm failure.
- [ ] Enable only the Wave 8 local/CI feature and add the bounded tracker section.
- [ ] Run focused real API/browser verification; expect pass.
- [ ] Run backend format/lint/type/full tests, frontend format/lint/type/full tests/builds, migration-head and diff checks.
- [ ] Perform one whole-branch security/governance review, fix any important findings test-first, commit, push, open PR, verify six jobs, merge, and verify six post-merge jobs.
