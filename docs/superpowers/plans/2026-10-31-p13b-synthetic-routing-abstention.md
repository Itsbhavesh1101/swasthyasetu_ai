# P13-B Synthetic Symbolic Routing and Abstention Implementation Plan

**Goal:** Add detached, deterministic, engineering-only symbolic matching and fail-closed
abstention without real routing authority.

**Architecture:** Immutable contracts feed one pure exact-match evaluator. Closed synthetic states,
reserved identifiers, policy artifact binding, nested revalidation, and UTC guards prevent the
mechanics from representing live or clinical routing.

**Tech stack:** Python standard library, pytest, Ruff, mypy

**Spec:** `docs/superpowers/specs/2026-10-31-p13b-synthetic-routing-abstention-design.md`

## Constraints

- No symptom, clinical fact, clinical category, threshold, model output, P9 interaction, provider
  selection/ranking, contact, geography, eligibility, source query, persistence, API, UI, dependency,
  or runtime registration.
- Zero or multiple exact matches must abstain without a route.
- Only reserved engineering-synthetic identifiers and immutable policy metadata are accepted.

## Tasks

### 1. Write adversarial tests first

- Add focused tests for exact match, no match, ambiguity, order independence, immutability, UTC
  normalization, temporal guards, direct-constructor invariants, forced mutation, strict prefixes,
  and forbidden clinical/provider/contact fields.
- Confirm the focused suite initially fails because the routing module does not exist.

### 2. Implement the minimum detached contracts and evaluator

- Add `backend/app/modules/providers/routing.py`.
- Revalidate snapshots and return only exact symbolic match or fail-closed abstention.
- Run focused pytest, Ruff, formatting, and mypy.

### 3. Document, audit, and verify

- Record the exact implementation and governance boundary in backend documentation and the progress
  tracker while keeping all live P13 criteria unverified.
- Run the full backend suite, compile/import/Alembic checks, scope and drift audits.
- Commit once, push the stacked feature branch, open an unmerged stacked PR, and verify all six CI
  jobs on the exact final SHA.
