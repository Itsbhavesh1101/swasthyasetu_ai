# P13-C Synthetic Referral Lifecycle Implementation Plan

**Goal:** Implement detached engineering-only referral lifecycle and idempotency mechanics without
live transition or sharing authority.

**Architecture:** Immutable status, aggregate, policy, command, receipt, and result contracts feed
one pure optimistic transition function. No transition graph is bundled; synthetic tests inject
explicit fixture policies.

**Tech stack:** Python standard library, pytest, Ruff, mypy

**Spec:** `docs/superpowers/specs/2026-10-31-p13c-synthetic-referral-lifecycle-design.md`

## Tasks

### 1. Establish the failing contract suite

- Test the canonical closed status vocabulary and absence of a default policy.
- Cover explicit policy application, unsupported pairs, version/identity/chronology failures,
  exact replay, idempotency conflict, no rollback, bounded/scoped receipt history, forced mutation,
  direct construction, UTC normalization, and forbidden sensitive/external fields.
- Confirm initial import failure before implementation.

### 2. Implement pure detached mechanics

- Add the referrals package and immutable contracts.
- Add exact policy-pair application and receipt-backed replay without side effects.
- Run focused pytest, Ruff, formatting, and strict mypy.

### 3. Document and verify

- Record the synthetic-only boundary and leave all live P13 criteria unverified.
- Run full backend, compile/import, migration-head, diff, dependency, schema, and runtime drift checks.
- Commit once, push a stacked branch, open an unmerged stacked PR, and verify all six exact-SHA CI
  jobs.
