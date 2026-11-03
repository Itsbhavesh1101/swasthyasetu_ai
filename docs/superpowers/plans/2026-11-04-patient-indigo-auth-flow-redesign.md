# Patient Indigo Authentication Flow Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a focused login-first public entry flow and apply the supplied indigo palette without changing account or patient-record behavior.

**Architecture:** Make the shared patient shell route-aware so authentication routes receive a minimal auth shell while protected product routes retain the existing workspace shell. Reuse the existing account forms and profile redirect, and update centralized CSS tokens/styles for the palette.

**Tech Stack:** Next.js 16 App Router, React 19, TypeScript, global CSS, Vitest, Testing Library

**Spec:** `docs/superpowers/specs/2026-11-04-patient-indigo-auth-flow-redesign-design.md`

## Global Constraints

- Use `#12141F`, `#232739`, `#383E5C`, `#4F5580`, `#7B81A8`, `#AFB4CE`, and `#E4E6F0`.
- Preserve account APIs, secure cookies, registration redirect, profile questions, patient records, and urgent-help semantics.
- Add no dependency, remote font, external image, backend change, database change, or new storage.

## Review Focus

- Authentication routes must never expose the full patient menu.
- Product routes must not lose the patient menu because of route matching errors.
- Root landing must contain exactly one account form and retain a reachable registration route.
- Registration must still redirect incomplete profiles to `/profile?setup=1`.
- Indigo text, controls, focus, and disabled states must maintain contrast on desktop and mobile.

---

### Task 1: Route-aware authentication shell

**Files:**

- Modify: `apps/patient-web/tests/shell.test.tsx`
- Modify: `apps/patient-web/components/patient-shell.tsx`

**Interfaces:**

- Consumes: `usePathname()` and existing full patient shell components
- Produces: minimal `.auth-shell` on `/`, `/login`, and `/register`; unchanged full shell elsewhere

- [ ] Add failing tests proving authentication routes omit navigation while product routes retain it.
- [ ] Run the shell tests and confirm the auth-route assertion fails.
- [ ] Implement minimal route-aware shell rendering.
- [ ] Run the shell tests and confirm they pass.

### Task 2: Login-first landing page

**Files:**

- Modify: `apps/patient-web/tests/page.test.tsx`
- Modify: `apps/patient-web/app/page.tsx`
- Modify: `apps/patient-web/app/login/page.tsx`
- Modify: `apps/patient-web/app/register/page.tsx`

**Interfaces:**

- Consumes: existing `AccountForm` modes and registration redirect behavior
- Produces: one-form login landing and matching dedicated auth pages

- [ ] Add a failing landing test for one sign-in form, no create-account form, and a `/register` link.
- [ ] Run the page test and confirm the duplicate-form assertion fails.
- [ ] Implement the focused auth content and concise safety copy.
- [ ] Run page and account UI tests and confirm they pass.

### Task 3: Indigo design system and verification

**Files:**

- Modify: `apps/patient-web/tests/accessibility-baseline.test.ts`
- Modify: `apps/patient-web/app/globals.css`

**Interfaces:**

- Consumes: Task 1 auth-shell class names and existing product component classes
- Produces: indigo tokens, auth presentation, responsive product shell, and accessibility fallbacks

- [ ] Update the palette/contrast test first and confirm it fails against the green palette.
- [ ] Apply the indigo tokens and authentication presentation without changing safety colors.
- [ ] Run the focused accessibility test and complete patient suite.
- [ ] Run formatting, lint, type checking, all frontend tests, production builds, and desktop/mobile visual QA.
