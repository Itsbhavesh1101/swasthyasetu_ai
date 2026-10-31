# P14-A Synthetic Signal Schema Implementation Plan

**Goal:** Implement content-free engineering-only extraction contracts and parsing mechanics without
clinical meaning or routing authority.

**Architecture:** Frozen fixture metadata and fixed toy signal tokens pass through one strict parser
and explicit request-binding validator. A detached protocol has no adapter or runtime integration.

**Tech stack:** Python standard library, pytest, Ruff, mypy

## Tasks

1. Establish failing tests for strict parsing, direct constructors, chronology, exact artifact
   binding, abstention, non-echoing errors, forced mutation, forbidden authority fields, and port
   isolation.
2. Implement the immutable contracts, parser, binding validator, content-free failures, and detached
   provider-neutral protocol.
3. Document the synthetic-only boundary; run full backend/frontend, schema/drift, security, Docker,
   PostgreSQL, Playwright, and exact-SHA CI verification.
