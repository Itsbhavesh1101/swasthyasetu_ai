# SwasthyaSetu AI

## 16 — Multilingual Speech Specification

> **DRAFT — PRE-P12 SPECIFICATION, NOT CLINICAL/PRIVACY/SECURITY/PRODUCTION APPROVAL, NO LIVE P12 IMPLEMENTATION**

**Document ID:** `SSAI-SPEC-016-PRE-P12-DRAFT`

**Evidence baseline:** `main @ 3492481a45e7aae068b521eed555ba829559da77`

**Review date:** 2026-10-23

**Review state:** DRAFT — INDEPENDENT AND ACCOUNTABLE HUMAN REVIEW REQUIRED

**Alembic head:** `p7a_0007` (unchanged)

This specification is a technical proposal for future P12 work. It selects no provider, model,
deployment region, language pack, medical glossary, voice, consent purpose, storage policy, or
clinical wording. It grants no runtime, patient-data, external-egress, pilot, or production
authorization.

---

# 1. Authority, as-built audit, scope, and non-goals

## 1.1 Authority and governing boundaries

The Project Master Specification, System Architecture, Product Requirements, privacy and consent
specification, accepted ADRs, R3 dependency policy, and approved clinical/safety policy outrank this
draft. In particular:

- ADR-002 requires provider-neutral ports and adapters;
- ADR-003 keeps safety decisions deterministic and versioned;
- ADR-007 requires explicit compile-time registration;
- ADR-020 keeps risky optional features controlled and safe-off;
- ADR-022 prohibits invented clinical policy;
- ADR-027 preserves manual intake and safety paths when speech fails;
- ADR-032 isolates research tooling from patient runtime;
- ADR-033 keeps approval in SwasthyaSetu governance rather than model registries;
- ADR-036 makes speech providers benchmark-gated;
- ADR-037 does not authorize a new broker or queue for speech;
- ADR-038 separates the future `language-ai` dependency profile;
- ADR-039 requires immutable, trusted, hashed model artifacts; and
- ADR-040 prevents heavyweight model/runtime infrastructure from entering the default stack merely
  because it is a candidate.

The three files under `docs/research/language/` are research and contract drafts. Their candidate
names, example shapes, proposed weights, and hypotheses are not accepted production policy.

## 1.2 Repository evidence at the baseline

P12 is **NOT STARTED**. Direct inspection found:

| Area | As-built evidence | Honest conclusion |
| --- | --- | --- |
| Patient language choice | `/language` and `LanguageSelector` allow `en` or `hi` when creating a pseudonymous session. The page says the full experience is not yet translated. | First-party session preference only; not full Hindi localization or a language service. |
| Session/BFF privacy | Session bearer remains in transient `HttpOnly`, `SameSite=Strict`, `Path=/` cookies; the BFF forwards it server-side, bounds requests, validates responses, and returns `no-store`. | A reusable security baseline, not voice authorization. |
| P7 manual intake | P7 accepts patient text/touch sources. `IntakeAnswer` records `language_code` and bounded `original_text`; serialization retains them. | Manual evidence preservation exists. It is not ASR, translation, or patient-facing multilingual clinical content. |
| P7 patient UI | The intake client currently sends `language_code: "en"`; no browser translation or speech capture is present. | The connected clinical-intake UI is an English engineering flow. |
| Voice contract hint | `InputMode.VOICE` exists as an enum value, but the public answer request admits only `PATIENT_TEXT` and `PATIENT_TOUCH`. | A dormant type value is not a voice workflow. |
| Backend boundary | `SpeechSettings` is disabled by default with an optional endpoint field. `backend/app/adapters/speech/` and `translation/` contain only `.gitkeep`. | No active STT, TTS, translation, transliteration, or language-detection adapter. |
| Module/composition | No `language` or `speech` bounded-context module is registered. | No language capability is exposed. |
| API | `docs/06_API_CONTRACTS.md` contains a conceptual speech endpoint only; no corresponding FastAPI route exists. | No voice API or BFF exists. |
| Browser/runtime | No microphone capture, `MediaRecorder`, `getUserMedia`, audio upload, voice playback, or patient-specific audio cache exists. | No live audio processing or recording. |
| Localization assets | No application locale/message pack framework or approved Hindi clinical copy pack was found. | UI labels on the selector do not establish localized clinical content. |
| Data/schema | No audio, transcript, translation, voice, or speech-processing tables or migrations exist. | Alembic remains `p7a_0007`; no P12 persistence is approved. |
| Providers/dependencies | No ASR/TTS/translation model dependency or provider SDK is installed. | No provider is implemented, selected, benchmarked, or approved. |

There is no active STT, TTS, translation, provider, recording, transcribed clinical fact, voice
BFF/API, migration, or P12 clinician/safety integration at this baseline.

## 1.3 Future conditional work packages

The implementation-plan labels are future boundaries, not authorization:

- **P12-A — language abstractions:** provider-neutral immutable contracts, explicit module/capability
  design, deterministic synthetic fixtures, and offline contract tests, only after a separate
  reviewed prompt authorizes that engineering subset;
- **P12-B — adapters:** real or hosted ASR/TTS/translation/transliteration/LID adapters only after
  benchmark, license, security, privacy, egress, region, and operational decisions;
- **P12-C — patient voice UI:** microphone permission, capture, review/confirm, playback, BFF/API,
  accessibility, consent, and retention only after the applicable human approvals; and
- **P12-D — regression fixtures:** governed multilingual and safety-critical evaluation evidence,
  with public-licensed/synthetic data and accountable language/clinical review.

Writing this specification does not authorize P12-A. Each work package needs its own scope review.

## 1.4 Clinical authority and non-goals

Speech and translation are optional input/output **evidence layers**. Audio, transcripts,
transliterations, translations, detected language, confidence, and generated audio cannot:

- become a diagnosis, prescription, medication change, confirmed clinical fact, or clinician
  statement;
- trigger or determine a P9 route, crisis disposition, self-care eligibility, P8 clinical AI action,
  or P10 clinician workflow outside the owning approved gate;
- overwrite original patient wording or a higher-trust fact;
- infer consent, identity, assignment, purpose, language preference, or clinical correctness; or
- bypass the blocked P8-C/P9-C Stage 3, P10, or P11 live gates.

This draft does not add code, dependencies, providers, schemas, migrations, APIs, BFFs, UI,
microphone access, locale assets, audio storage, models, benchmarks, clinical copy, feature flags,
or runtime activation.

---

# 2. Language, script, code-switch, and evidence semantics

## 2.1 Distinct concepts

The following concepts must never be collapsed into one field:

| Concept | Meaning |
| --- | --- |
| Language | Linguistic content, initially English (`en`) or Hindi (`hi`), or an explicitly unknown/unsupported value. |
| Script | Written representation such as Latin or Devanagari; script is not proof of language. |
| Romanization/transliteration | Representation change between scripts without claiming semantic translation. |
| Translation | A derived attempt to preserve meaning in another language. |
| Locale/UI copy | A reviewed product-content resource; it is not produced by language detection. |
| Confidence/quality | Provider-specific operational evidence whose semantics must be labeled; never clinical certainty. |

Detecting Hindi must not automatically choose Devanagari output. Romanized Hindi is not English,
and Hinglish is not one fixed model language. English words, Hindi words, named entities, numbers,
and clinical terms can occur in the same utterance and use different scripts.

## 2.2 Closed uncertainty states

Future contracts must distinguish at least:

- `KNOWN`, `MIXED`, `AMBIGUOUS`, `UNKNOWN`, `UNSUPPORTED`, and `LOW_CONFIDENCE` language outcomes;
- segment-level language/script candidates for code-switching;
- `PARTIAL` streaming hypotheses from `FINAL` results;
- provider abstention from technical failure; and
- inaudible/unintelligible spans from silence.

An ambiguous or unsupported result preserves the source and asks the user to choose, edit, or use
text/touch. It must not silently translate, select a script, or fabricate missing speech.

## 2.3 Original and derived representations

Where future policy permits collection and retention, the exact original patient utterance/audio
reference, final original transcript, segment timing/context, normalized form, transliteration, and
translation remain distinct immutable artifacts connected by lineage. A derivative never replaces
the original or becomes “the patient's words.” Patient review of one representation does not
silently confirm every derivative.

Every transformation must preserve or explicitly flag uncertainty in:

- negation, polarity, uncertainty, subject, and temporality;
- numbers, decimals, dates, durations, dose values, frequencies, and units;
- medication, person, facility, and other named entities; and
- code-switch boundaries and source segment order.

Inaudible phrases, silence, background speech, and low-confidence tokens must not create invented
symptoms, medicines, doses, absences, or reassurance.

---

# 3. Proposed replaceable ports and typed versioned contracts — design only

## 3.1 Port separation

Future code should define independent conceptual boundaries:

```text
SpeechToTextPort
LanguageDetectionPort
TransliterationPort
TranslationPort
TextToSpeechPort
```

Batch and streaming ASR have different lifecycles; any `StreamingSpeechToTextPort` must be separate
from the bounded batch port. A `LanguageAIProvider` god interface is prohibited. Provider objects,
SDK exceptions, credentials, and wire formats cannot enter domain/application contracts.

## 3.2 Common contract rules

Every request/result is immutable, strict, bounded, versioned, and rejects unknown fields. Common
metadata should include an opaque operation/correlation ID, contract version, requested operation,
deadline, cancellation state, idempotency identity where applicable, and explicit input/output
language and script metadata. All timestamps are timezone-aware UTC.

The boundary between `source_audio_ref` and actual bytes is security-sensitive. A reference is only
a locator; it grants no read authority. An adapter receives bytes or an authorized, generation-bound
stream only after fresh server-side ownership, purpose, consent, lifecycle, and size/type checks.
Browser-supplied references, URLs, endpoints, models, provider IDs, or headers are not authority.

Accepted audio types, sample rates, channel layouts, durations, byte limits, segment limits,
language sets, confidence thresholds, provider deadlines, retry budgets, and resource quotas are
**UNDECIDED**. They require measured evidence and cannot be inferred from research examples.

## 3.3 Speech-to-text request and result

A future request should identify the authorized audio reference/generation, declared format and
language hints, batch mode, requested final/word alignment, glossary identity if separately approved,
contract version, deadline, and idempotency key. It must not carry an unrestricted patient record,
bearer, consent object, arbitrary provider endpoint, or untrusted executable configuration.

A future result should contain:

```text
status = SUCCEEDED | PARTIAL | LOW_CONFIDENCE | ABSTAINED | FAILED
finality = PARTIAL | FINAL
original_transcript
segments[start, end, text, language/script candidates, optional provider confidence]
detected language/script candidates and uncertainty
duration and bounded warnings
provider + adapter + model/revision/hash + runtime provenance
quality kind and value, only when the provider defines them
source audio reference/generation and request version
```

Partial text is provisional and cannot be persisted or submitted as final clinical evidence.
Confidence must not be fabricated for providers that do not expose it.

## 3.4 Language detection, transliteration, and translation

`LanguageDetectionPort` returns ranked language/script candidates plus explicit uncertainty or
abstention. Short text, medication-only text, numbers, and mixed content can legitimately be
unknown.

`TransliterationPort` accepts source/target script plus protected spans. It returns source and output
segments, protection markers, optional rank/confidence, and provenance. Protected terms may include
numbers, units, medicines, acronyms, URLs, IDs, and English clinical terms, but the registry itself
must be sourced, versioned, and approved.

`TranslationPort` returns source text and translated text together, exact language pair, bounded
warnings/quality metadata, and provenance. Unsupported pairs or uncertainty fail honestly. Domain
hints do not authorize medical inference, and translated text cannot become authoritative safety
copy.

## 3.5 Text-to-speech

`TextToSpeechPort` accepts only approved text identity/version, language, an approved voice-profile
ID, bounded synthesis settings, and deadline. It returns a controlled audio reference, format,
sample rate, duration, status, and model/voice provenance. Normal patient requests must not accept
arbitrary reference audio or enable patient/bystander voice cloning.

Voice profiles require separate permission provenance, asset rights, supported language, version,
approval state, and retirement state. No voice profile is approved by this draft.

## 3.6 Errors, deadlines, cancellation, retry, and idempotency

Future internal failures should distinguish invalid/oversize media, unsupported language/pair,
low confidence, uncertainty/abstention, timeout, cancellation, rate limit, configuration/authentication
failure, unavailable provider/model, policy block, malformed result, resource exhaustion, and unknown
failure. Public mappings require the owning API phase and must remain content-free.

One operation has one total deadline covering attempts, backoff, validation, and finalization. Retry
is bounded and allowed only for explicitly classified transient failures when time remains. Invalid
input, consent/permission failure, unsupported language, malformed deterministic output, cancellation,
and exhausted deadline are not retried. Retry never changes provider, model, region, input scope,
retention, or consent purpose. Mutations require actor/subject-scoped idempotency and authoritative
state refetch after ambiguous outcomes.

Stop/cancel must halt capture, discard uncommitted partials, revoke temporary access, and produce an
honest state. Exact in-flight provider and retention behavior remains a human decision.

## 3.7 Immutable lineage

Each derivative records source artifact/version, operation, contract/schema version, provider,
adapter/model/version/revision/hash, input and output language/script, segmentation/alignment,
quality kind/value, UTC creation time, and approval/verification state. A chain may be:

```text
approved audio generation
 -> final transcript
 -> selective transliteration
 -> translation
```

Every link is independently inspectable and never rewrites its parent. These conceptual contracts
are not approved persistence schemas and authorize no migration.

---

# 4. Trust, security, privacy, and provider boundaries

## 4.1 Consent and purpose are non-transitive

Current `GENERAL_PRODUCT_USE` consent with `clinical_intake` covers the approved first-party
deterministic P7 path only. It does **not** authorize audio capture/retention, hosted ASR,
translation, TTS, external models, provider human review/training, research, clinical promotion, or
new secondary uses.

Privacy/legal, product/institution, accessibility, identity/security, and clinical owners must decide
the exact purpose, population, age/guardian/caregiver/assisted/kiosk handling, recording notice,
affirmative permission, withdrawal, retention, deletion, lawful/governance basis, and user copy.
Authentication or microphone permission is not consent.

## 4.2 Capture and browser boundary

Microphone use must be explicit opt-in with a visible start, recording state, stop, cancel, and
review action. Hidden, automatic, background, or post-navigation recording is prohibited. Audio,
transcripts, translated clinical text, bearers, identifiers, provider payloads, and signed references
must not enter localStorage, sessionStorage, IndexedDB, Cache Storage, service workers, background
sync, URLs/query strings, analytics/session replay, generic logs/traces/metrics, screenshots, or
client error reports. Future clinical responses use `Cache-Control: no-store`.

## 4.3 External processing and models

No patient audio or clinical text may leave the controlled first-party boundary until accountable
owners approve the named operation, minimum payload, endpoint/model, region/transfer, DPA and
procurement, subprocessors, retention/deletion, training and abuse-monitoring use, human access,
credentials, network allowlist, incident duties, withdrawal behavior, and fallback. Tests must prove
zero unapproved egress. A provider adapter, API key, benchmark score, feature flag, or zero-retention
setting is not approval.

Local models also require license/dataset review, immutable revision/hash, inspected code,
dependency/profile isolation, artifact provenance, resource limits, sandboxing where appropriate,
update/rollback controls, and supply-chain validation. Model downloads at runtime from moving
references are prohibited.

## 4.4 P12 threat catalogue and future negative evidence

P11-focused `27_SECURITY_ARCHITECTURE.md` and `28_THREAT_MODEL.md` provide informative patterns for
fresh authorization, isolation, bounded work, provenance, nonenumeration, and failure recovery. They
are P11-only drafts, not completed P12 or platform security policy.

| Threat | Required future control/test | Accountable roles |
| --- | --- | --- |
| Bystander or third-party voice | Explicit recording state and purpose; test multi-speaker/background input, discard/cancel, and no silent attribution. | Privacy/legal, product, clinical, accessibility |
| Replay, deepfake, or speaker impersonation | Speech is evidence, never identity proof; replay/deepfake fixtures cannot establish actor or patient authority. | Identity/security, clinical governance |
| Audio prompt injection/encoded instructions | Treat transcript/audio content as data; instructions cannot change tools, policy, provider, schema, or authorization. | AI/security architecture |
| Ambiguous language/script/code-switch | Preserve segments and abstain; adversarial short, mixed, number-only, and named-entity tests. | Language reviewers, clinical governance |
| Fake confirmations and partial ASR | Partial or UI-spoofed confirmation never becomes final evidence; server validates final lineage. | Application architecture, security |
| Accidental capture/upload | Permission, explicit start, size/time limit, preview, cancel, and cleanup tests. | Product, privacy, security |
| Provider fallback crosses egress boundary | No silent provider/model/region switch; blocked endpoint and zero-egress tests. | Privacy/legal, security, operations |
| Model download/supply-chain compromise | Pin and hash code/model/container; reject moving/tampered/unapproved artifacts. | Security, language engineering, operations |
| TTS cloning/impersonation | Approved fixed voices only; reject arbitrary reference voice and retired/unapproved IDs. | Privacy/legal, content, security |
| Secret or payload leakage | Canary audio/text/token absent from logs, traces, metrics, errors, URLs, browser stores, CI artifacts, and support tools. | Security, operations |
| Retry/cancel/revocation race | Recheck authority at dispatch and result commit; discard late/stale output; test each race boundary. | Privacy, application architecture |
| Malicious/oversized media | Signature/type, decoded-resource, duration, concurrency, CPU/memory, and timeout limits; fail closed. | Security engineering, operations |
| Worker/resource exhaustion | Isolated bounded execution, quotas, cancellation, health, kill switch, and text fallback. | Operations, architecture |
| Cross-session/kiosk residue | Exact-session object checks and full transient cleanup; no browser/device residue. | Identity/security, institution, frontend |
| Emergency-copy translation error | Only versioned pre-reviewed localized text/audio; live translation/TTS cannot become authoritative. | Clinical safety, content/localization, accessibility |

---

# 5. Patient interaction, accessible fallback, and safety copy

## 5.1 Text/touch independence

The existing deterministic P7 text/touch flow remains independently usable when a user declines
microphone permission, cannot speak, uses assistive technology, has noisy audio, uses an unsupported
language, loses connectivity, encounters provider timeout/outage, or cancels voice. Speech is never
required to reach manual intake or generic urgent-help navigation.

## 5.2 Future interaction contract

Any authorized future voice experience requires:

1. explicit user action to start and stop;
2. persistent recording status and a clear cancel action;
3. provisional labeling for streaming partials;
4. an editable presentation of the unverified final transcript;
5. explicit review/confirmation before an authorized submission;
6. an honest low-confidence/unsupported/outage state with immediate text/touch fallback; and
7. server-side authority for session, consent, encounter, source, finality, and mutation.

The client cannot silently resolve contradictions, translate emergency/triage copy, infer that a
symptom was heard, or claim save success after an ambiguous failure. Stop/cancel must not leave
background capture, queued replay, cached audio, or cross-session residue.

## 5.3 Safety-critical copy and audio

Emergency, crisis, triage, contraindication, and helpline wording must use accountable, versioned,
pre-reviewed localized copy and approved audio assets. Live unreviewed TTS or translation cannot be
authoritative. An approved static audio asset may supplement but never replace visible text and
other accessible routes.

Future UI evidence must cover 320px and 390px reflow, keyboard-only operation, logical focus,
screen-reader recording/status/error announcements, 44px representative targets, visible and
non-color-only uncertainty/finality indicators, reduced-motion/forced-colors behavior, quiet mode,
assisted/kiosk privacy, and microphone-denied fallback.

---

# 6. Benchmark and selection evidence — no invented metrics

## 6.1 Required evidence set

The R2 benchmark plan is a proposal, not completed evidence. A future reviewed benchmark must use
public-licensed or separately approved synthetic nonpatient data, with a license/consent manifest,
immutable dataset/artifact hashes, development/selection/held-out splits, representative device and
runtime profiles, reproducible noise mixing, and human clinical/language review.

It must stratify at least:

- Hindi, English, Hinglish/code-switch, native and Romanized scripts;
- clean, quiet/soft/fast/elderly-style speech and noisy OPD/corridor/device conditions;
- silence, breathing, background speech, hallucination, false insertion, and omission;
- negation, polarity, uncertainty, dates, durations, numbers, decimals, units, medicines, anatomy,
  and medically sensitive terms;
- LID uncertainty, script distinction, selective transliteration, named-entity preservation, and
  unsupported pairs;
- TTS intelligibility, pronunciation, fixed-voice governance, and accessibility;
- latency, deadline, throughput, CPU/RAM/VRAM, cold/warm start, offline/edge feasibility, cost,
  resilience, privacy, network/egress, licenses, maintenance, and rollback.

## 6.2 Metrics and review

ASR should report WER/CER and sentence match alongside critical-token omission/false insertion,
number/unit/dose/negation accuracy, terminology preservation, hallucination rate, code-switch
boundaries, final latency, and calibration/abstention. Translation should report suitable automatic
metrics only as supplements to bilingual review of meaning, negation, temporality, uncertainty,
numbers, entities, and dangerous errors. Transliteration needs CER/exact/top-k where available plus
entity/medicine corruption. TTS needs latency/resource measures plus human intelligibility,
pronunciation, mixed-language comprehension, and voice-rights review.

This specification defines no acceptable numeric threshold, benchmark score, winner, production
provider, approved model, or approved voice. Accountable owners must approve thresholds before the
selection run and record disqualifying license/privacy/safety conditions.

## 6.3 Candidate status

BHASHINI, IndicConformer, faster-whisper, whisper.cpp, IndicLID, IndicXlit, IndicTrans2, IndicF5,
legacy Indic-TTS, and evaluation tools mentioned by research remain candidates or hypotheses. None
is selected or approved. Hosted or local activation requires completed benchmark evidence, license
and terms review, exact artifact hashes, deployment/resource/rollback evidence, and explicit
privacy, security, clinical, accessibility, institutional, and production decisions.

---

# 7. Requirement and acceptance traceability

## 7.1 `FR-LANG-001..012`

| Requirement | Proposed design and current evidence | Live status |
| --- | --- | --- |
| `FR-LANG-001` — English | P6 can select `en`; P7 patient intake currently sends English. Full reviewed P12 language behavior is absent. | NOT VERIFIED FOR P12 |
| `FR-LANG-002` — Hindi | P6 can select `hi` and shows a small selector label; no complete approved Hindi clinical pack or connected Hindi intake exists. | NOT VERIFIED FOR P12 |
| `FR-LANG-003` — Hinglish | Section 2 defines mixed segment semantics; no implementation or evaluated fixtures exist. | NOT VERIFIED |
| `FR-LANG-004` — Romanized Hindi | Sections 2–3 separate script and transliteration; no recognizer/transliterator is active. | NOT VERIFIED |
| `FR-LANG-005` — language selection | Existing `/language` creates a session preference for `en`/`hi`; this is partial P6 evidence, not full P12 support. | PARTIAL EXISTING EVIDENCE; LIVE P12 NOT VERIFIED |
| `FR-LANG-006` — language switching | Proposed contracts preserve per-segment language and uncertainty; active-conversation switching is absent. | NOT VERIFIED |
| `FR-LANG-007` — original input preservation | P7 stores bounded `original_text` with language metadata for manual answers; Sections 2–3 extend the proposed immutable derivative lineage. Audio/transcript lineage is absent. | PARTIAL P7 EVIDENCE; LIVE P12 NOT VERIFIED |
| `FR-LANG-008` — ASR confidence | Proposed quality kind/value and abstention semantics prohibit fake confidence. No ASR exists. | NOT VERIFIED |
| `FR-LANG-009` — ASR fallback | Existing P7 text/touch is independent; Section 5 makes it the required fallback. No voice failure path exists to verify. | FALLBACK EXISTS; LIVE ASR FAILURE NOT VERIFIED |
| `FR-LANG-010` — TTS | Proposed port and governed voice profile are design only. No TTS or approved audio assets exist. | NOT VERIFIED |
| `FR-LANG-011` — translation safety | Sections 4–5 require pre-reviewed safety copy and prohibit live authority. No production translation is active or approved. | NOT VERIFIED |
| `FR-LANG-012` — regional expansion | Proposed gate requires language-specific safety/usability/benchmark evidence before release. No additional language is approved. | NOT VERIFIED |

## 7.2 `AC-P12-001..009`

| Criterion | Proposed evidence boundary | Current status |
| --- | --- | --- |
| `AC-P12-001` | Separate `SpeechToTextPort`, explicit adapter registration, shared contract tests. | LIVE NOT VERIFIED |
| `AC-P12-002` | Separate `TextToSpeechPort` if implemented, approved voice profiles, contract tests. | LIVE NOT VERIFIED |
| `AC-P12-003` | Separate `TranslationPort` if implemented, source-preserving result and contract tests. | LIVE NOT VERIFIED |
| `AC-P12-004` | Versioned English/Hindi configuration and reviewed content availability, not merely session preference. | LIVE NOT VERIFIED |
| `AC-P12-005` | Synthetic Romanized Hindi/Hinglish fixtures with segment/script assertions and no invented clinical rules. | LIVE NOT VERIFIED |
| `AC-P12-006` | Immutable original plus normalized/transliterated/translated lineage and round-trip/source-drift tests. | LIVE NOT VERIFIED |
| `AC-P12-007` | Real failure/deadline/cancel/outage UI evidence proving immediate text/touch continuation. | LIVE NOT VERIFIED |
| `AC-P12-008` | API/domain/persistence negative tests proving failed/partial transcription cannot become confirmed fact. | LIVE NOT VERIFIED |
| `AC-P12-009` | Approved-copy registry/static asset checks and tests rejecting live authoritative safety translation/TTS. | LIVE NOT VERIFIED |

No live P12 acceptance criterion is verified by documentation, P6 language choice, P7 original-text
storage, empty adapter directories, or a disabled speech setting.

---

# 8. Gated phase plan and cross-phase dependencies

| Future unit | Separately reviewable minimum | Prerequisites and accountable approvals | Stop condition |
| --- | --- | --- | --- |
| P12-A | Offline synthetic immutable contracts, ports, explicit registration metadata, deterministic mocks, zero-network adversarial tests. | Architecture and security review of contract boundaries; privacy confirmation that fixtures are synthetic/nonpatient; separate implementation prompt. | Any contract implies live bytes, persistence, API, clinical authority, or unapproved dependency. |
| P12-B | One or more explicitly authorized benchmark adapters behind ports, still disabled by default. | Benchmark thresholds/results; license/model/dataset review; provider/region/DPA/egress or local runtime decision; secrets, resource, incident, rollback and artifact-hash approval. | Provider/model/terms/region/egress or benchmark decision missing. |
| P12-C | Explicit microphone UI, BFF/API and review/confirm flow with text/touch fallback. | Purpose/population/notice/consent, audio lifetime, schema/retention/deletion, identity/object authorization, approved localized copy/audio, accessibility and threat/privacy approval. | Any authority, copy, retention, capture, assignment, or failure behavior is undecided. |
| P12-D | Reproducible multilingual regression and clinical/language review pack. | Approved dataset/license/consent manifest, thresholds, reviewers, safety-copy versions, representative devices/populations and release criteria. | Real patient data or unreviewed clinical/safety examples would be used. |

P7 manual intake remains the supported fallback. P8-C patient-facing AI and P9-C patient-facing
safety Stage 3 remain blocked. P10 live remains 0/9 approved. P11 live remains 0/9 approved (5 OPEN,
4 BLOCKED); its security/threat files remain P11-focused drafts, and P11-E is unimplemented. No P12
work may interpret this draft as closing or bypassing those gates.

---

# 9. Open human decisions and STOP conditions

Live design or implementation must stop while any applicable item lacks an authoritative decision:

1. permitted population, purpose, language scope, age/guardian/caregiver/assisted/kiosk treatment;
2. recording notice, microphone permission, consent/lawful basis, withdrawal, subject rights;
3. audio/transcript/translation/TTS storage, schema, retention, deletion, backup, and legal hold;
4. provider/model/artifact, endpoint, region, egress, DPA, subprocessors, training/retention, license;
5. formats, sample rates, duration/size/resource/deadline/retry/concurrency limits;
6. benchmark datasets, thresholds, clinical/language reviewers, and acceptable failure behavior;
7. medical glossary/protected-term source, hotword policy, and false-insertion tolerance;
8. approved localized patient, failure, emergency, helpline, and accessibility copy/audio;
9. server authorization, idempotency, source lineage, persistence, cancellation, and race semantics;
10. operational isolation, telemetry/redaction, incident response, kill switch, rollback, pilot, and
    production approval.

Source ambiguity, a missing approval, or repository drift must be reported as blocked rather than
resolved by selecting a provider, policy, threshold, language pack, region, duration, or clinical
wording.
