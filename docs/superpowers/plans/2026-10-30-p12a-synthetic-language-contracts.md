# P12-A Synthetic Language Contracts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an inert, synthetic-only P12-A language/speech contract foundation with five independent ports and deterministic offline mocks.

**Architecture:** Operation-specific frozen dataclasses share narrow value objects but never a god-provider interface. An explicit metadata-only registry is version pinned and engineering-only; exact-mapping adapters remain under tests and nothing is registered in FastAPI or the platform capability registry.

**Tech Stack:** Python 3.12 standard library, existing pytest/Ruff/mypy toolchain

**Spec:** `docs/superpowers/specs/2026-10-30-p12a-synthetic-language-contracts-design.md`

## Global Constraints

- No new dependency, model, provider, network access, audio bytes/fixture, persistence, API, UI, job, event, feature flag, or runtime activation.
- Preserve all P8-C, P9-C, P10, P11, and live P12 gates.
- Every contract is frozen, slotted, strict, bounded, versioned, and direct-constructor safe.
- Naive timestamps fail; aware timestamps normalize to UTC.
- Mocks remain test-only and deterministic.

## Review Focus

- Mutated nested objects must be revalidated/snapshotted instead of smuggling invalid authority.
- Stale generation, request-version, operation-ID, or artifact references must not match results.
- Partial/abstained/failed outcomes must not carry authoritative derived content.
- Unknown quality must not fabricate numeric confidence; numeric quality must be finite and bounded.
- Registry ambiguity, duplicate identities, wrong capability pins, and non-engineering authority must fail closed.

---

### Task 1: Strict shared and operation-specific contracts

**Files:**
- Create: `backend/app/modules/language/__init__.py`
- Create: `backend/app/modules/language/contracts.py`
- Test: `backend/tests/test_language_contracts.py`

**Interfaces:**
- Produces: value objects plus `SpeechToTextRequest/Result`, `LanguageDetectionRequest/Result`, `TransliterationRequest/Result`, `TranslationRequest/Result`, and `TextToSpeechRequest/Result`, each with `assert_matches()`.

- [ ] Write failing tests for valid synthetic construction, immutability, strict types/fields, UTC normalization, lineage, uncertainty/finality invariants, bounded text/collections, protected spans, quality semantics, and request/result mismatch.
- [ ] Run `py -m uv run pytest tests/test_language_contracts.py -q` and verify failure because the module is absent.
- [ ] Implement the minimum contract code that satisfies those tests without persistence or provider choices.
- [ ] Run the focused tests and Ruff/mypy for the new production/test files.

### Task 2: Five independent ports

**Files:**
- Create: `backend/app/modules/language/ports.py`
- Test: `backend/tests/test_language_ports.py`

**Interfaces:**
- Consumes: Task 1 request/result types.
- Produces: five runtime-checkable async protocols with one operation each.

- [ ] Write failing structural-protocol tests proving a correctly shaped adapter matches only its intended port and no god interface exists.
- [ ] Run the focused test and verify failure because ports are absent.
- [ ] Implement the five narrow protocols.
- [ ] Run focused tests, Ruff, and mypy.

### Task 3: Explicit engineering-only registration metadata

**Files:**
- Create: `backend/app/modules/language/registry.py`
- Test: `backend/tests/test_language_registry.py`

**Interfaces:**
- Produces: `LanguageCapability`, `ProviderAuthority`, `ProviderDisposition`, `LanguageProviderDescriptor`, `LanguageProviderPin`, `LanguageProviderRegistry`, and `build_synthetic_language_registry()`.

- [ ] Write failing tests for exact pins, deterministic lookup, duplicate/ambiguous metadata, incompatible capabilities, invalid versions, mutated inputs, and rejection of any authority/disposition beyond engineering/mock-only.
- [ ] Run the focused test and verify failure because the registry is absent.
- [ ] Implement immutable snapshot-based metadata registration with no adapter instances or import side effects.
- [ ] Run focused tests, Ruff, and mypy.

### Task 4: Deterministic test-only mocks

**Files:**
- Create: `backend/tests/language_support/__init__.py`
- Create: `backend/tests/language_support/mocks.py`
- Create: `backend/tests/test_language_mocks.py`

**Interfaces:**
- Consumes: Tasks 1 and 2.
- Produces: five exact-mapping mock adapters and content-free `MockLanguageFailure` codes.

- [ ] Write failing async tests for deterministic results, unknown IDs, injected failures, malformed types, cross-request/stale-result rejection, and zero I/O behavior.
- [ ] Run the focused test and verify failure because mocks are absent.
- [ ] Implement five test-only adapters using immutable fixture snapshots and `assert_matches()`.
- [ ] Run all P12-A tests, Ruff, and mypy.

### Task 5: Documentation, tracker, and full verification

**Files:**
- Create: `docs/implementation/P12_A_SYNTHETIC_LANGUAGE_CONTRACTS.md`
- Modify: `backend/README.md`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`

**Interfaces:**
- Records the engineering-only boundary and outstanding live approvals without changing canonical gate truth.

- [ ] Document contracts, non-activation, privacy/safety boundary, tests, and limitations; mark only P12-A safe engineering evidence complete and keep live P12 criteria unverified.
- [ ] Run full backend quality, frontend quality/build, migration drift, PostgreSQL/Docker where applicable, privacy/secret scans, and `git diff --check`.
- [ ] Audit the diff for dependency, lockfile, migration, runtime registration, API/UI, and generated-file drift.
- [ ] Commit, push the feature branch, open an unmerged PR, and verify all six CI jobs on the exact SHA.
