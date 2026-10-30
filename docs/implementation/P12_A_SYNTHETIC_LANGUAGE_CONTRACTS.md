# P12-A — Synthetic Language and Speech Contract Foundation

**Status:** complete safe engineering subset; live P12 remains partial and unapproved

**Baseline:** `origin/main @ 7dc45bf11285e7c061211436f804d4e5f8f5c2dd`

**Branch:** `phase/p12-a-synthetic-language-contracts`

## 1. Scope and authority

This increment implements only the P12-A unit proposed in
`16_MULTILINGUAL_SPEECH_SPEC.md` §8: offline synthetic immutable contracts, five provider-neutral
ports, explicit registration metadata, deterministic mocks, and zero-network adversarial tests.

It does not close or bypass any readiness gate. It selects no provider, model, artifact, endpoint,
region, language pack, medical glossary, voice, format, duration, confidence threshold, retry budget,
retention period, lawful basis, patient population, clinical wording, or production deadline.

## 2. Implemented contracts

`app.modules.language.contracts` defines separate versioned request/result pairs for:

- batch speech-to-text;
- language/script detection;
- transliteration;
- translation; and
- text-to-speech.

Shared value objects enforce:

- opaque generation-bound artifact references with SHA-256 metadata, never URLs or read authority;
- exact operation/correlation/idempotency identities;
- aware UTC creation/deadline timestamps, with aware non-UTC normalization and naive rejection;
- distinct language, script, transliteration and translation semantics;
- ranked `KNOWN`, `MIXED`, `AMBIGUOUS`, `UNKNOWN`, `UNSUPPORTED`, and `LOW_CONFIDENCE` outcomes;
- explicit `PARTIAL` versus `FINAL` speech results;
- source-preserving text artifacts and ordered code-switch segments;
- protected spans for representation-preserving transformations;
- quality values only when an explicit provider quality kind exists; and
- immutable provider/model/revision/hash provenance fixed to `ENGINEERING_ONLY` / `UNVERIFIED`.

No contract state represents clinician confirmation, clinical correctness, safety authority, or
patient consent. Failed or abstained results cannot carry invented derived content. Every result
can revalidate that it matches the exact operation, source generation, contract version, language/
script pair, protected spans, or voice identity of its request.

## 3. Ports and metadata registry

`app.modules.language.ports` defines five independent runtime-checkable async protocols:

- `SpeechToTextPort.transcribe`;
- `LanguageDetectionPort.detect`;
- `TransliterationPort.transliterate`;
- `TranslationPort.translate`; and
- `TextToSpeechPort.synthesize`.

There is no combined `LanguageAIProvider`. Batch and future streaming lifecycles are not collapsed.

`app.modules.language.registry` stores immutable descriptive metadata and exact capability pins. It
accepts only `ProviderAuthority.ENGINEERING_ONLY` and `ProviderDisposition.MOCK_ONLY`. Duplicate
identities, ambiguous pins, unknown providers, incompatible capabilities, mutated inputs and
unversioned metadata fail closed. The registry contains no adapter instance, endpoint, credential,
model runtime, import discovery, or application registration side effect.

## 4. Deterministic test-only mocks

Five exact-mapping adapters exist only under `backend/tests/language_support`. They snapshot valid
fixtures, return a detached result on every call, validate result/request lineage, and use bounded
content-free failure codes for unknown, cancelled, unavailable, refused, malformed or mismatched
outcomes. Tests prove they perform no file or network I/O.

These mocks cannot be selected by application configuration because production composition never
imports or registers them.

## 5. Security, privacy and clinical boundary

- No audio bytes, real audio fixture, microphone, browser capture, patient text, document text,
  bearer, identifier, URL, consent object, provider endpoint, arbitrary header or executable model
  configuration enters the contracts.
- No external egress, runtime model download, provider fallback, persistence, log body, trace body,
  analytics, cache or service worker behavior is introduced.
- Text-to-speech accepts a versioned synthetic text artifact and fixed profile identity only; there
  is no reference-audio or cloning input.
- Translation/TTS cannot generate authoritative safety or emergency copy.
- Speech/language output cannot become a confirmed fact or route into P8, P9, P10 or P11.
- P7 deterministic text/touch intake remains independently available.

## 6. Verification and acceptance truth

The focused suite covers valid contracts plus adversarial direct construction, frozen-shell
mutation, extra fields, strict enum/type/version checks, UTC behavior, size bounds, uncertainty,
partial/final contradictions, empty/invented content, confidence semantics, stale generations,
lineage mismatches, registry ambiguity and mock isolation.

The full backend, PostgreSQL, frontend, Docker, browser, privacy and security gates are recorded in
the feature PR and exact-SHA CI run.

P12-A supplies bounded engineering evidence toward `AC-P12-001..003` and `AC-P12-005..009`, but it
does not satisfy their **live** meanings. `AC-P12-001..009` remain `LIVE NOT VERIFIED`. P12 remains
`PARTIAL`; P12-B, P12-C and P12-D are not authorized by this increment.

## 7. Remaining blockers

All unresolved decisions in `P12_READINESS_GATE_REVIEW.md` remain: population/purpose/consent,
capture and audio lifetime, provider/model/region/egress/license, datasets and thresholds,
clinical-language reviewers, persistence/API ownership, accessibility and patient confirmation,
safety copy and voice assets, operations/incident/rollback, and pilot/production authorization.
