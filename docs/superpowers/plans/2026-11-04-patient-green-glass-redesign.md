# Patient Green Glass Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the patient frontend with the supplied green glass dashboard aesthetic without changing its working product behavior.

**Architecture:** Update the shared patient shell and navigation structure, then replace global design tokens and component styles so all routes inherit the redesign. Keep page and feature logic unchanged.

**Tech Stack:** Next.js 16 App Router, React 19, TypeScript, global CSS, Vitest, Testing Library

**Spec:** `docs/superpowers/specs/2026-11-04-patient-green-glass-redesign-design.md`

## Global Constraints

- Use the exact palette `#051F20`, `#0B2B26`, `#163832`, `#235347`, `#8EB69B`, and `#DAF1DE`.
- Preserve existing patient behavior, routes, safety copy, storage boundaries, and accessibility affordances.
- Add no dependency, remote font, external image, API change, or backend change.
- Keep urgent and error states semantically red.

## Review Focus

- Anonymous users must still see login, registration, urgent help, and accessible navigation.
- Long navigation labels and account names must not overflow the sidebar or mobile shell.
- Forms and disabled controls must remain readable on dark glass surfaces.
- Keyboard focus must remain clearly visible throughout the shell and form controls.
- Reduced-motion and forced-color users must retain usable states.

---

### Task 1: Semantic dashboard shell

**Files:**

- Modify: `apps/patient-web/tests/shell.test.tsx`
- Modify: `apps/patient-web/components/patient-shell.tsx`
- Modify: `apps/patient-web/components/patient-navigation.tsx`
- Modify: `apps/patient-web/components/account-menu.tsx`

**Interfaces:**

- Consumes: existing route links, `AccountMenu`, and `UrgentHelpLink`
- Produces: semantic `.patient-sidebar`, `.patient-workspace`, and labeled navigation markup

- [ ] Add a failing shell test for the patient workspace sidebar, privacy reassurance, and preserved landmarks.
- [ ] Run the shell test and confirm the missing-sidebar failure.
- [ ] Implement the minimal shell and navigation markup.
- [ ] Run the shell test and confirm it passes.

### Task 2: Accessible green glass design system

**Files:**

- Modify: `apps/patient-web/tests/accessibility-baseline.test.ts`
- Modify: `apps/patient-web/app/globals.css`

**Interfaces:**

- Consumes: Task 1 shell class names and all existing component class names
- Produces: palette tokens, responsive glass layout, component styling, and accessibility fallbacks

- [ ] Update the accessibility test to parse the actual CSS tokens and assert the new contrast relationships.
- [ ] Run the test and confirm it fails against the old palette.
- [ ] Implement the global tokens, shell layout, responsive styles, controls, panels, lists, and fallbacks.
- [ ] Run the accessibility and complete patient test suites.

### Task 3: Verification and visual QA

**Files:**

- Modify only files required to fix verified visual or regression defects.

**Interfaces:**

- Consumes: complete redesigned patient app
- Produces: verified desktop/mobile UI and production-safe branch

- [ ] Run formatting, lint, type checking, tests, and production build.
- [ ] Start the redesigned frontend against the existing local backend.
- [ ] Capture and inspect desktop and mobile screenshots for the landing, dashboard, and profile routes.
- [ ] Correct only verified defects, rerun affected checks, and inspect the final diff.
