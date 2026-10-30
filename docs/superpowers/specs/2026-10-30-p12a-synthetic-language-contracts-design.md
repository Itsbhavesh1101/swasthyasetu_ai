# P12-A Synthetic Language Contracts Design

## Intent

Create the earliest safe P12 engineering unit: strict provider-neutral language and speech
contracts, five separate ports, explicit engineering-only provider metadata, deterministic test-only
mocks, and offline adversarial tests. This supplies replaceable boundaries without collecting audio,
processing patient data, selecting a provider, or activating a runtime capability.

## Goals

- Define independent `SpeechToTextPort`, `TextToSpeechPort`, `TranslationPort`,
  `TransliterationPort`, and `LanguageDetectionPort` protocols.
- Preserve original and derived representations as distinct immutable artifacts with versioned,
  UTC-aware provenance.
- Represent uncertainty, abstention, partial results, unknown quality, code-switch segments, and
  protected spans without inventing clinical certainty.
- Reject malformed, unbounded, authority-bearing, mismatched, or extra-field data.
- Provide explicit, version-pinned, engineering-only registration metadata with no import-time or
  application-composition side effect.
- Provide exact-mapping deterministic mocks below `backend/tests` only.

## Non-goals and anti-goals

- No audio bytes, real audio fixtures, microphone/device access, browser work, API/BFF, persistence,
  migration, job, event, telemetry exporter, feature flag, or runtime registration.
- No model/provider SDK, network call, model download, benchmark claim, language pack, medical
  glossary, voice asset, clinical copy, clinical inference, or safety routing.
- No provider, language, format, duration, confidence threshold, region, retention period, retry
  budget, or production deadline is selected or approved.
- No P8-C/P9-C Stage 3, live P10/P11, or live P12 gate is closed.

## Constraints

- Base is `origin/main @ 7dc45bf11285e7c061211436f804d4e5f8f5c2dd` in an isolated worktree.
- Python 3.12 and existing standard-library/project dependencies only.
- Contracts are frozen, slotted, strict at direct construction, bounded, and versioned.
- Timestamps are aware UTC; aware non-UTC values normalize to UTC and naive values are rejected.
- Source references are opaque identifiers plus immutable generation/hash metadata, never URLs or
  access authority.
- Provider metadata is descriptive engineering evidence only and cannot claim clinical approval.

## Approaches considered

### 1. One generic language-operation envelope and provider

This is compact, but it recreates the prohibited `LanguageAIProvider` god interface and makes it
easy to send an ASR request to a translation implementation. Rejected.

### 2. Pydantic models for every internal contract

This gives convenient parsing, but the P12-A boundary is an inert internal engineering domain, not
an API. It also encourages treating future wire schemas as already approved. Rejected for this unit.

### 3. Operation-specific immutable dataclasses plus shared primitives

Selected. Each operation owns its request/result type and port while reusing narrow language,
artifact, provenance, quality, and operation-context value objects. This is explicit, directly
constructor-testable, framework independent, and consistent with the existing synthetic document
and summary foundations.

## Architecture

`backend/app/modules/language/contracts.py` owns strict immutable value objects and the five
operation request/result pairs. Every result revalidates and snapshots its nested inputs, preserves
source identity, and provides `assert_matches()` to reject stale or cross-operation fixtures.

`backend/app/modules/language/ports.py` owns five independent async protocols. No combined provider
protocol exists.

`backend/app/modules/language/registry.py` owns immutable provider descriptors and an explicit
version-pinned registry. Only `ENGINEERING_ONLY` and `MOCK_ONLY` metadata is accepted in P12-A. The
registry stores no adapter instances and is never imported by application composition.

`backend/tests/language_support/` owns deterministic exact-mapping mocks. Unknown request IDs,
injected failures, wrong result types, and request/result mismatches fail with content-free test
codes. Production imports cannot select these mocks.

## Failure and privacy behavior

- Unknown or malformed data fails closed with bounded machine-readable exceptions.
- Partial text remains provisional; no contract state represents clinician confirmation.
- Confidence is optional and must carry an explicit quality kind; unknown quality has no numeric
  value.
- Requests cannot carry URLs, endpoints, credentials, headers, consent objects, patient records, or
  arbitrary provider/model selection.
- Tests use synthetic nonmedical text and opaque metadata only; no network or filesystem I/O occurs.

## Verification

Focused contract/port/registry/mock tests, direct-constructor mutation tests, Ruff formatting and
lint, strict mypy, full backend tests, migration-head drift checks, frontend quality/build tests,
Docker/PostgreSQL checks, Gitleaks/Trivy CI, and all six GitHub CI jobs on the final SHA.

## Honest completion boundary

P12-A may be reported as a complete **safe engineering subset** only. `P12` remains `PARTIAL` or
`NOT STARTED` for live purposes, and `AC-P12-001..009` remain live-not-verified except for bounded
engineering evidence explicitly described in the completion record.
