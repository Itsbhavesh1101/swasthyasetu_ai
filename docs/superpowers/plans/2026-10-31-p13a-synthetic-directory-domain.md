# P13-A Synthetic Directory Domain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add strict engineering-synthetic provider and resource domain contracts without live
directory authority.

**Architecture:** Provider-owned source evidence is shared by separate immutable provider and
resource records. Closed single-value authority/classification/verification enums make live or
verified construction unrepresentable while direct-constructor validation fails closed.

**Tech Stack:** Python standard library, pytest, Ruff, mypy

**Spec:** `docs/superpowers/specs/2026-10-31-p13a-synthetic-directory-domain-design.md`

## Global Constraints

- No dependency, schema, migration, API, persistence, registry query, source adapter, contact, URL,
  routing, referral, job, event, UI, feature flag, or runtime registration.
- No real or realistic provider/resource data.
- Frozen, slotted, bounded, direct-constructor-safe contracts only.
- Naive timestamps fail; aware timestamps normalize to UTC.

## Review Focus

- Forced mutation of nested source evidence must be revalidated by record construction.
- Strings must not substitute for closed enums or booleans for integers.
- Source acquisition cannot occur after record creation.
- Unmistakably synthetic prefixes must be enforced for IDs, labels, and symbolic codes.
- Extra contact, URL, verification, availability, or routing fields must be rejected.

---

### Task 1: Synthetic provider/source contracts

**Files:**
- Create: `backend/app/modules/providers/__init__.py`
- Create: `backend/app/modules/providers/domain.py`
- Test: `backend/tests/test_provider_directory_domain.py`

**Interfaces:**
- Produces `SyntheticSourceEvidence` and `SyntheticProviderRecord` plus closed authority enums.

- [ ] Write failing tests for valid construction, immutability, UTC normalization, strict enums,
  synthetic prefixes, bounds, hashes, versions, temporal ordering, nested mutation, and extra fields.
- [ ] Run the focused test and confirm failure because the domain module is absent.
- [ ] Implement only the contracts required by the tests.
- [ ] Run focused pytest, Ruff, and mypy.

### Task 2: Synthetic resource contract

**Files:**
- Create: `backend/app/modules/resources/__init__.py`
- Create: `backend/app/modules/resources/domain.py`
- Test: `backend/tests/test_resource_directory_domain.py`

**Interfaces:**
- Consumes `SyntheticSourceEvidence` from Task 1.
- Produces `SyntheticCareResourceRecord`.

- [ ] Write failing tests for valid construction, source snapshotting, UTC behavior, strict symbolic
  codes, direct-constructor failures, and absence of contact/routing authority.
- [ ] Run the focused test and confirm failure because the resource domain module is absent.
- [ ] Implement the minimum resource contract.
- [ ] Run both focused suites, Ruff, and mypy.

### Task 3: Boundary documentation and verification

**Files:**
- Create: `docs/implementation/P13_A_SYNTHETIC_DIRECTORY_DOMAIN.md`
- Modify: `backend/README.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

- [ ] Record the exact synthetic-only boundary and keep all live P13 criteria unverified.
- [ ] Run full backend checks and proportionate frontend/migration/security regression gates.
- [ ] Audit dependency, lockfile, migration, registration, API/UI, and generated-file drift.
- [ ] Commit, push, open an unmerged PR, and verify all six exact-SHA CI jobs.
