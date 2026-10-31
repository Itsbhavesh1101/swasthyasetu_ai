# P13-E Synthetic Referral Presentation Implementation Plan

**Goal:** Add isolated static presentation evidence for synthetic failure/source-warning states
without activating P13 UI.

**Architecture:** Fixed test-support React components with closed state unions and fail-closed
runtime defaults. Production source trees contain no import or implementation path.

**Tech stack:** React, Vitest, Testing Library, TypeScript

## Tasks

1. Add failing patient and admin presentation tests for closed states, accessibility, no actions,
   no sensitive content, no optimistic claims, and production isolation.
2. Add the two minimal test-support fixtures and adversarial unknown-state defaults.
3. Run focused tests, full frontend/backend quality gates, scope/drift checks, and exact-SHA CI.
