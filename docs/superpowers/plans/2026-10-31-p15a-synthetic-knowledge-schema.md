# P15-A Synthetic Knowledge Schema Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an immutable, hash-bound, strictly parsed synthetic knowledge-pack schema that cannot represent approved or patient-facing self-care content.

**Architecture:** A new detached `self_care` module owns pure contracts and a mapping parser. Closed
engineering tokens replace all content and source data; no runtime consumer is registered.

**Tech Stack:** Python 3.13 standard library, dataclasses, enums, SHA-256, pytest.

**Spec:** `docs/superpowers/specs/2026-10-31-p15a-synthetic-knowledge-schema-design.md`

## Global Constraints

- Only fixed nonmedical engineering tokens and `TEST_ONLY_UNAPPROVED` are representable.
- No dependency, persistence, migration, API, UI, file/network I/O, or runtime registration.
- No real or synthetic remedy/advice text, clinical exclusion, source, URL, score, or threshold.
- P8-C/P9-C/P10/P11/P12/P13/P14/P15 governance restrictions remain active.

## Review Focus

- Unknown prose/authority/source fields fail closed without echoing their values.
- Forged `APPROVED` or nonengineering state cannot be parsed or directly constructed.
- Nested mutation or pack-hash mismatch is detected at validation boundaries.
- Duplicate, unsorted, sparse, or oversized items/tags are rejected deterministically.
- Noncanonical/naive/future timestamps and hostile mappings return stable content-free errors.

---

### Task 1: Immutable pack and item contracts

**Files:**
- Create: `backend/app/modules/self_care/__init__.py`
- Create: `backend/app/modules/self_care/contracts.py`
- Test: `backend/tests/test_synthetic_self_care_knowledge.py`

**Interfaces:**
- Produces: `SyntheticKnowledgeItem`, `SyntheticKnowledgePack`, `create_synthetic_knowledge_pack`, `validate_synthetic_knowledge_pack`, and stable error/token enums.
- Consumes: Python standard library only.

- [ ] Write failing direct-constructor tests for strict tokens, ordering, limits, UTC, immutability,
  deterministic hash, mutation revalidation, and the absence of any approved state.
- [ ] Run the focused file and verify it fails because `self_care.contracts` does not exist.
- [ ] Implement the minimal immutable contracts and hash validation.
- [ ] Run focused tests and static checks.

### Task 2: Strict mapping loader and boundary evidence

**Files:**
- Create: `backend/app/modules/self_care/loader.py`
- Modify: `backend/tests/test_synthetic_self_care_knowledge.py`
- Modify: `docs/implementation/38_PROGRESS_TRACKER.md`
- Create: `docs/implementation/P15_A_SYNTHETIC_KNOWLEDGE_SCHEMA.md`

**Interfaces:**
- Consumes: Task 1 contracts and exact public constructors.
- Produces: `parse_synthetic_knowledge_pack(payload: object, *, observed_at: datetime) -> SyntheticKnowledgePack`.

- [ ] Write failing parser tests for exact fields, unknown content/source/approval fields, hostile
  mappings, canonical timestamps, forged hashes, and nested mutation.
- [ ] Implement the minimal strict mapping parser with content-free errors.
- [ ] Run focused, full backend/frontend, migration, Compose, scope, and security checks.
- [ ] Commit, push, open a PR, verify six exact-SHA CI jobs, merge, and verify six main jobs.
