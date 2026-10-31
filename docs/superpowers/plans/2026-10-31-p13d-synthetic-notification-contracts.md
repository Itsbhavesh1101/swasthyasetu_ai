# P13-D Synthetic Notification Contracts Implementation Plan

**Goal:** Implement detached engineering-only notification intent and simulated-failure mechanics
without message, recipient, provider, or delivery authority.

**Architecture:** Immutable metadata contracts feed one pure exact-binding failure recorder. No
port, adapter, success state, default template, policy, or runtime integration is bundled.

**Tech stack:** Python standard library, pytest, Ruff, mypy

**Spec:** `docs/superpowers/specs/2026-10-31-p13d-synthetic-notification-contracts-design.md`

## Tasks

### 1. Establish the failing contract suite

- Cover strict synthetic identifiers/variables, exact template binding, chronology, UTC
  normalization, immutable construction, nested forced mutation, and stable failure receipts.
- Assert the absence of recipient/channel/copy/provider/retry/referral fields and any send port,
  success state, delivery receipt, or default template.
- Confirm initial import failure before implementation.

### 2. Implement pure detached mechanics

- Add the notifications package and immutable metadata contracts.
- Add exact-binding simulated failure recording without I/O or side effects.
- Run focused pytest, Ruff, formatting, and strict mypy.

### 3. Document and verify

- Record the synthetic-only boundary and leave all live P13 criteria unverified.
- Run full backend, compile/import, migration-head, diff, dependency, schema, and runtime drift
  checks.
- Commit once, push a feature branch, open a pull request, and verify all six exact-SHA CI jobs.
