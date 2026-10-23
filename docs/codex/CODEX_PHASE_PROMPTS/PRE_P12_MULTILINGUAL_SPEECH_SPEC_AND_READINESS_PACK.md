# SwasthyaSetu AI — Pre-P12 Multilingual Speech Specification & Readiness Pack

**Work unit:** `PRE-P12` — DOCUMENTATION / GOVERNANCE READINESS ONLY. Not P12-A/B/C/D implementation, not live audio processing, and not permission to deploy ASR/TTS/translation, collect patients' speech, or activate patient-facing safety/clinical features.

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified starting `main`:** `3492481a45e7aae068b521eed555ba829559da77`
**PR #38:** merged at the above SHA; reviewed head `f2b771761d724c65bcc5140a090e85dff531d9ed` must compare tree-equivalent (`files=[]`).
**Suggested branch:** `phase/pre-p12-multilingual-speech-specification`
**Alembic head:** `p7a_0007` (unchanged).
**Current stage:** P12 NOT STARTED, `docs/16_MULTILINGUAL_SPEECH_SPEC.md` NOT STARTED as of starting main. P11 live 0/9 APPROVED (5 OPEN, 4 BLOCKED), P10 live 0/9 APPROVED, P8-C/P9-C Stage 3 BLOCKED. Security/threat documents 27/28 are **P11-focused drafts only**, not platform-wide approved policy.

> **Why permitted:** Master implementation plan permits scoped planning partially in parallel when dependencies are stable. Authoring an honest Pre-P12 specification with existing P7 fallback is separate from blocked P11 clinical document activation. **This document-only task grants no P12 runtime authorization and closes no P11/P10 safety, clinical, identity, privacy or production gate.** Creating review drafts does not require pretended prior human sign-off; real processing/provider/clinical copy/egress/release decisions do.

## 0. Preflight and source-of-truth hierarchy

1. Verify GitHub and `origin/main` both at `3492481a45e7aae068b521eed555ba829559da77`. Verify PR #38 merged/tree-equivalent and P12 spec does not exist. Use a new **clean isolated Git worktree** based on the verified remote SHA, preserving the primary worktree and every pre-existing untracked file. If remote main has moved, STOP and report; never reset/force-push or silently rebase assumptions.
2. Read governance first: `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`, `docs/{00_PROJECT_MASTER_SPEC,01_PRODUCT_REQUIREMENTS,02_SYSTEM_ARCHITECTURE,03_REPOSITORY_STRUCTURE,04_DOMAIN_MODEL,06_API_CONTRACTS,12_CLINICAL_PROVENANCE_SPEC,13_AI_ORCHESTRATION_SPEC,14_LLM_EXTRACTION_SPEC,23_PATIENT_APP_SPEC,26_PRIVACY_CONSENT_SPEC,29_ENGINEERING_STANDARDS,30_TESTING_STRATEGY,33_ERROR_HANDLING_POLICY,34_MASTER_IMPLEMENTATION_PLAN}.md`; `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER,P8_C_INTEGRATION_GATE_REVIEW,P9_C_SAFETY_PRESENTATION_GATE_REVIEW,P10_READINESS_GATE_REVIEW,P11_READINESS_GATE_REVIEW,P11_E_SOURCE_ACCESS_AND_UI_READINESS_DESIGN,PRE_P11_E_ARCH_PRIVACY_TECH_ASSESSMENT_AND_DECISION_TEMPLATE,P11_PRIVACY_DATA_FLOW_ASSESSMENT_DRAFT}.md`; `docs/{27_SECURITY_ARCHITECTURE,28_THREAT_MODEL}.md` for P11-only **draft** boundaries, not as completed platform review; and `docs/research/r3/{R3_FINAL_TECHNOLOGY_STACK,R3_CODEX_DEPENDENCY_POLICY}.md`.
3. Read **all three** existing language research sources as research/drafts rather than selected production policy: `docs/research/language/{INDIAN_LANGUAGE_SPEECH_TECH_EVALUATION,LANGUAGE_ADAPTER_CONTRACT_DRAFT,SPEECH_TRANSLATION_BENCHMARK_PLAN}.md`. Inspect actual repository: `backend/app/adapters/{speech,translation}/` placeholders; any existing language module, P7 intake original-text storage and safety boundaries, patient `/language` and `language-selector`, BFF/cookie/cache requirements, fallback path and existing locale assets. Identify what exists before describing it. No network/model benchmark, patient audio or actual API provider access should be attempted in this documentation work unit.
4. Accepted ADRs are binding: especially ADR-002, 003, 007, 020, 022, 027, 032, 033, 036–040. R3 dependency policy phase-gates runtime speech packages and hosted integrations. Benchmark hypotheses (BHASHINI, IndicConformer, faster-whisper, whisper.cpp, IndicLID, IndicXlit, IndicTrans2, TTS options) are NOT selections or approvals. Record any genuine conflict as a pending ADR review, never silently select a provider, language pack, storage policy, medical glossary, deployment region or model.

## 1. Primary deliverable: `docs/16_MULTILINGUAL_SPEECH_SPEC.md`

Create this canonical **Pre-P12 technical specification**, explicitly labeled **DRAFT — PRE-P12 SPECIFICATION, NOT CLINICAL/PRIVACY/SECURITY/PRODUCTION APPROVAL, NO LIVE P12 IMPLEMENTATION**. Include numbered sections with at least:

### A. Authority, as-built audit, scope and non-goals
- State starting main SHA, P12 NOT STARTED, Alembic `p7a_0007`, and actual P6/P7 first-party multilingual/text-touch state; no active STT, TTS, translation, provider, recording, transcribed clinical fact, voice BFF/API, migrations, or P12 clinician/safety connection unless direct inspection proves otherwise.
- Record P12-A language abstractions, P12-B adapters, P12-C voice UI, P12-D regression fixtures as **future conditional work packages**. Separate technical draft evidence from authorizations.
- Define that speech/translation is an optional input/output **evidence** layer, not clinical decision authority. Audio, transcripts, translated text and metadata cannot trigger P9 safety decisions, P8 clinical AI, P10 clinician workflows, or clinical fact promotion outside their respective gates.

### B. Language, script and code-switch semantics
- English, Hindi/Devanagari and Hinglish/Romanized Hindi from the roadmap; distinguish **language**, **script**, **romanization/transliteration**, **translation**, **locale/UI copy** and confidence. Do not conflate detecting Hindi with choosing Devanagari output.
- Define ambiguous/mixed/unknown/unsupported/low-confidence language and code-switch segments. Retain exact original patient utterance/transcript and segmented timing/context where approved; normalized/transliterated/translated variants must never overwrite original or become patient-confirmed words.
- Preserve negations, polarity, numbers, units, dates, medications, named entities and uncertainty. Define no inference on inaudible phrases, hallucinated silence, invented symptom, or incorrect medication/dose.

### C. Proposed replaceable ports and typed versioned contracts (design, NO code)
- Independent conceptual `SpeechToTextPort`, `LanguageDetectionPort`, `TransliterationPort`, `TranslationPort`, `TextToSpeechPort`, with optional streaming port separated from batch; no `LanguageAIProvider` god interface.
- Explicit input/output/status/error semantics; source audio reference vs actual bytes security boundary; language/script and segmentation metadata, model/version/hash provenance, alignment, partial vs final result, confidence meaning, unknown/abstain, accepted sample rates/types/limits as **UNDECIDED**, provider deadlines, cancellation, resource bounds, idempotency and retries.
- Preserve immutable source-to-derivative lineage for transcript, transliteration and translation; no clinical outcome from provider confidence. Proposed data contracts are not schemas approved for persistence/egress; don't propose a migration as already authorized.

### D. Trust/security/privacy and provider boundaries
- Current P7 `GENERAL_PRODUCT_USE`/`clinical_intake` consent is **NOT transitive** to audio capture/retention, hosted ASR, translation, TTS, external model providers, research or new clinical uses. Fresh purpose/population/age/guardian/assisted/kiosk/recording notices, explicit user permission, storage and deletion policies require named privacy/legal/product/institution decisions.
- Microphone permissions and capture must be opt-in; no hidden recording, auto-start, background recording, browser-cache/service-worker storage or replay leakage. No raw audio, transcript, translated clinical text, bearer, identifiers, provider payload, or signed references in generic logs, telemetry, URLs or browser persistent storage. No model egress without named operation, allowed endpoint/region, DPA/training/retention/subprocessor decisions, explicit approval and zero-unapproved-egress tests.
- Threat catalogue: bystander/third-party voice, replay/deepfake, audio prompt injection and encoded instructions, language ambiguity, fake confirmations, accidental upload, provider fallback crossing egress boundaries, model download/supply chain, speaker impersonation, TTS voice cloning, transient secrets, retry/cancel/revocation races, malicious or oversized media, worker resource exhaustion, cache/cross-session/kiosk residue, translation of emergency safety guidance. Map to future negative tests and human owners.
- Reuse the platform's existing P11-draft threat/security concepts only as informative design patterns; **do not mislabel those P11-only draft files as fully approved P12/platform policies**.

### E. Patient interaction, accessible fallbacks, safety copy
- Text/touch remains independently usable on mobile/kiosk and for users who decline microphone permission, cannot speak, use screen readers, have noisy audio, unsupported language, provider outage, weak connectivity, or voice timeout.
- Future voice feature requires explicit start/stop, recording status, review/edit/confirm of the unverified transcript before any authorized submission; client does not silently resolve clinical contradictions, translate emergency/triage copy or claim that the app heard a symptom. Treat partial streaming ASR as provisional; stop/cancel must preserve privacy.
- Safety-critical copy and any emergency/helpline wording must use accountable **pre-reviewed localized copy** and approved audio assets; no live unreviewed TTS/translation of crisis guidance. Define 320/390px reflow, keyboard, screen reader announcements, noncolor-only uncertainty indicators, quiet/assisted mode and microphone-denied fallback.

### F. Benchmark and selection evidence, no invented metrics
- Cite the R2 language benchmark plan's real strata: Hindi/English/Hinglish, code-switch, noisy OPD, elderly/soft/fast speech, silence and hallucination, medically sensitive terms, numeric/negation/unit accuracy, script/LID/transliteration, pronunciation/TTS, latency, cost/resources, privacy/egress, offline/edge feasibility and resilience.
- Propose reproducible public-licensed/synthetic nonpatient datasets, stratified splits, license/consent manifest, artifact hashes, representative device profiles and human clinical/language review. Distinguish WER/CER and critical-token omission/false insertions, medical terminology, translation semantic/negation errors, TTS intelligibility and calibration. Do not invent acceptable numeric thresholds, benchmark scores, winners, model performance or pre-authorized voice profiles.
- Conditions for future hosted or local model activation: benchmark evidence, license, artifact hash, resource/rollback and accountable privacy/security/clinical/institution decisions.

### G. Requirement/acceptance traceability & gated phase planning
- Map all `FR-LANG-001..012` accurately from PRD and `AC-P12-001..009` from `35_PHASE_ACCEPTANCE_CRITERIA.md` to proposed designs, existing partial P6/P7 evidence and **live NOT VERIFIED** status. Check exact PRD text—don't map by guessed label.
- Clearly distinguish safe separately reviewed future P12-A **offline synthetic port/contract** work from blocked P12-B real provider, P12-C microphone/UI and P12-D production clinical fixtures. Outline prerequisites and human approval owners for each. A future engineering-only P12-A is not authorized by writing this spec alone.
- Cross-reference P7/P8/P9/P10/P11; no P12 work may bypass those gates or be interpreted as closing them.

## 2. Companion readiness review: `docs/implementation/P12_READINESS_GATE_REVIEW.md`

Create dated source-grounded human-decision inventory, with a **proposed, unapproved P12-specific gate matrix** (do NOT invent that P12 already has an official 9-gate count or copy P11's gate count as P12's). Include for every proposed gate: accountable *role* (not fake name), currently present evidence, missing human decision/approval artifact, privacy/security/legal/clinical concerns, negative tests, permitted engineering-only work if separately approved, and stop condition. At minimum cover: population and speech consent; device/capture/audio lifetime/privacy; provider/model/egress/deployment/licensing; language/medical benchmark and safe errors; versioned contracts/record/provenance; accessibility and patient confirmation; clinical/safety copy and voice/TTS governance; operations/failure/isolation/rollback; pilot/production approval.

Record that **no live P12 acceptance is verified** and the review pack is **not** a decision or signoff. Separate *documentation can be authored now* from *sensitive implementation needs real owner decisions*. Include a short unsigned evidence/decision checklist suitable for future review, never completed signatures or selected providers, quotas, production populations, deployment regions, audio retention durations, legal conclusions, or approved clinical translation.

## 3. Progress tracker and exact scope

Only these paths may change:

```text
docs/16_MULTILINGUAL_SPEECH_SPEC.md                             # NEW, doc-only
docs/implementation/P12_READINESS_GATE_REVIEW.md                # NEW, doc-only
docs/implementation/38_PROGRESS_TRACKER.md                      # MINIMAL status update
docs/codex/CODEX_PHASE_PROMPTS/PRE_P12_MULTILINGUAL_SPEECH_SPEC_AND_READINESS_PACK.md  # tracked exact prompt
```

Tracker updates: mark `16_MULTILINGUAL_SPEECH_SPEC.md` as **DRAFT PRE-P12 SPECIFICATION — SUBJECT TO INDEPENDENT/HUMAN REVIEW; NOT IMPLEMENTED OR APPROVED**, add a new strictly scoped status section noting Pre-P12 documentation pending review, and record that P11 security/threat/privacy documentation PR #38 merged at `main 3492481a45e7aae068b521eed555ba829559da77`, reviewed head `f2b771761d724c65bcc5140a090e85dff531d9ed`, tree-equivalent. Maintain `27_SECURITY_ARCHITECTURE.md` and `28_THREAT_MODEL.md` as P11-FOCUSED DRAFT; P11 0/9 (5 OPEN, 4 BLOCKED), P10 0/9, P8-C/P9-C Stage 3 blocked, P11-E not implemented, P7 manual intake supported. No P12 runtime progress claim.

**Strict prohibitions:** No code/tests, migrations/ORM/DB, API/OpenAPI/BFF/UI/camera/microphone, language assets or locale changes, dependencies/locks, model weights, providers/benchmarks, network calls, storage/recording, CI/Docker/infra changes, feature flags, consent policy changes, accepted ADR edits, egress, fake signoffs, or P8–P11 activation. Preserve primary worktree and untracked files. Do not add these documents to the canonical live approval matrix as approved.

## 4. Audit, CI and independent handoff

1. Confirm exact branch base and changed-path allowlist, status and `git diff --check`. Verify all referenced repository paths, section numbers, ID maps, research-vs-accepted decisions, absent code claims, privacy statements and STOP conditions. Scan for prohibited approval terms, medical examples presented as real, credentials, source excerpts and copied third-party research/license material.
2. Reasonable documentation/link audits plus mandatory repository quality checks. All SIX GitHub CI jobs must complete **SUCCESS on the exact final PR head**: `Backend quality`, `Frontend quality`, `Persistence integration`, `Docker and PostgreSQL`, `Playwright Chromium`, `Security scans`. Never weaken workflows to get green. Retain exact real counts and warnings. Alembic head and dependencies unchanged.
3. Open only one feature PR, verify feature local==remote==PR head and exact CI run SHA, **DO NOT MERGE**. Stop after reporting; do not start P12-A or any P11 live work. If source ambiguity or repository drift prevents honest planning, report BLOCKED instead of guessing.

### Required completion report

```text
STATUS: COMPLETE PRE-P12 DOCUMENTATION ONLY / PARTIAL / BLOCKED
BRANCH: phase/pre-p12-multilingual-speech-specification
BASE MAIN SHA: 3492481a45e7aae068b521eed555ba829559da77
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER:
16 SPEECH SPEC DRAFT AND P7-P12 EVIDENCE:
P12 READINESS GATES / HUMAN DECISIONS:
FR-LANG-001..012 / AC-P12-001..009 TRACEABILITY:
ENGLISH/HINDI/HINGLISH, SAFETY COPY, PRIVACY/EGRESS AND FALLBACK:
RESEARCH CANDIDATES VS SELECTED PROVIDERS:
P11 SECURITY/THREAT DRAFT AND LIVE GATES PRESERVED:
DOC LINKS / CHANGED PATHS / GOVERNANCE AUDIT:
CI RUN ID / EXACT FINAL SHA / SIX JOB CONCLUSIONS:
ALEMBIC HEAD / DEPENDENCIES / UNRELATED CHANGES:
LIVE P12 IMPLEMENTED: NO
MERGED: NO
```

**STOP for independent review.** This is a permitted **parallel documentation** work unit, not live P12 implementation or a substitute for the unresolved P11 gate decisions.
