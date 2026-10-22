# P12 multilingual speech and language readiness gate review

> **DRAFT — PROPOSED PRE-P12 GATES, NOT A DECISION OR SIGNOFF; NO LIVE P12 ACCEPTANCE VERIFIED**

**Review date:** 2026-10-23

**Evidence baseline:** `main @ 3492481a45e7aae068b521eed555ba829559da77`

**P12 state:** NOT STARTED

**Alembic head:** `p7a_0007`

## 1. Review conclusion

The repository is ready to review a P12 design draft, not to collect or process patient speech.
P6 supplies an English/Hindi session preference and privacy-preserving BFF/cookie/cache patterns;
P7 supplies deterministic manual text/touch intake with bounded original-text metadata. Empty
speech/translation adapter directories and disabled `SpeechSettings` supply no live capability.

There is no implemented or approved ASR, TTS, translation, transliteration, language detection,
microphone capture, audio storage, speech API/BFF, model/provider, benchmark result, medical glossary,
localized clinical/safety copy, P12 persistence, or production activation. Therefore **no live P12
acceptance criterion is verified**.

The matrix below is a proposed P12-specific inventory. The project has not established an official
P12 gate count, and this document does not copy P11's nine-gate status model into P12. Every status
is a request for accountable review, not approval.

## 2. Proposed unapproved gate matrix

| Proposed gate | Accountable role(s) | Present evidence | Missing decision/approval artifact | Principal concerns | Required negative evidence | Separately permitted engineering-only work | Stop condition |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Population and speech consent | Privacy/legal; product/institution; consent owner; accessibility | P4 centralized consent; P6 notice flow; `26_PRIVACY_CONSENT_SPEC.md` says consent is non-transitive. | Allowed populations and languages; purpose; recording notice; affirmative permission; age/guardian/caregiver/assisted/kiosk treatment; withdrawal and subject rights. | Bystander speech, coercion, accessibility exclusion, secondary use, invalid consent inheritance. | Missing/wrong/withdrawn purpose at capture/dispatch/result; child/guardian and assisted-use denial; no hidden capture. | Documentation and synthetic UI-state/contract design only after separate approval. | Any live capture, retention, or processing purpose/population is undecided. |
| Device, capture, audio lifetime, and privacy | Privacy; security engineering; frontend/accessibility; operations | P6 transient cookies, `no-store`, generic-only service-worker cache; no microphone code. | Capture pattern; formats/rates/duration/size limits; temporary buffering; cancellation cleanup; audio retention/deletion/backups; device/kiosk residue policy. | Hidden/background recording, accidental upload, cross-session residue, browser cache, malicious/oversize media, multi-speaker attribution. | Permission denial; cancel/navigation/crash; boundary+1 media; browser-storage/URL/log scans; kiosk session turnover; temp cleanup. | Offline synthetic contract and component-state tests with no audio device access, if separately scoped. | Capture or lifecycle values are unknown, or residue/leakage cannot be bounded. |
| Provider/model, egress, deployment, and licensing | Architecture; privacy/legal/procurement; security; language engineering; operations | ADR-036/R3 list benchmark candidates only; no SDK/model/dependency installed. | Named provider/model/revision/hash; endpoint/region; DPA/subprocessors; retention/training/human review; license/dataset rights; local hardware/isolation; secrets/network; rollback. | Cross-border transfer, silent fallback, supply chain, runtime downloads, credential leak, resource exhaustion, vendor lock-in. | Zero-unapproved-egress; wrong endpoint/region; tampered hash; moving revision; missing secret; provider retention/config drift; outage/OOM. | Provider-neutral synthetic ports/mocks only under a future authorized P12-A prompt. | Any provider/model/region/license/egress or artifact decision is absent. |
| Language/medical benchmark and safe errors | Clinical governance; bilingual language experts; accessibility; data governance; language engineering | R2 benchmark plan defines useful strata and metrics but has no SwasthyaSetu result or approved threshold. | Licensed/synthetic datasets and manifests; splits; device/population profiles; predeclared thresholds; dangerous-error rules; reviewers; calibration/abstention and release criteria. | Negation/number/unit/medicine corruption, silence hallucination, code-switch loss, unrepresentative data, metric gaming. | Silence/noise/background speech; omissions/insertions; short/mixed/unknown text; negation/dose/date/unit; unsupported language; held-out review. | Offline harness planning and synthetic nonmedical fixtures after separate review. | Thresholds, datasets/licenses, reviewers, or dangerous-error treatment are missing. |
| Versioned contracts, record, and provenance | Application/data architecture; privacy; clinical provenance owner; security | P5/P7 provenance/original text; conceptual API only; no P12 schema/migration. | Exact immutable contracts; source/derivative lineage; final/partial semantics; idempotency; authorization; schema, retention and migration decision; public errors. | Original overwritten, stale/late result, cross-subject reference, fake confidence, partial accepted as final, lower-trust promotion. | Direct-constructor/extra-field/version mismatch; stale generation; cross-session/source; partial/failed-to-fact; atomic failure and retry races. | Design-only contract specification; future in-memory synthetic types if separately authorized. | Any live record/API/persistence semantics or ownership boundary is unresolved. |
| Accessibility and patient confirmation | Accessibility; content/localization; product; frontend; privacy | P6/P7 keyboard/reflow/no-store and manual fallback; no voice UI. | Explicit start/stop/review/edit/confirm flow; recording/partial/error copy; 320/390px, keyboard, screen reader, quiet/assisted/kiosk validation; approved language packs. | Speech-only exclusion, false confirmation, inaccessible uncertainty, noisy environment, denied microphone, background recording. | Keyboard/screen-reader flow; permission denied; timeout/outage; unsupported language; no-color state; cancel; text/touch independence. | Static synthetic presentation prototypes only under a reviewed UI scope, not from this document. | Text/touch is not independently usable or copy/accessibility approval is missing. |
| Clinical/safety copy and voice/TTS governance | Clinical safety; content/localization; accessibility; legal/voice-rights owner | Generic urgent-help path exists; P8-C/P9-C Stage 3 remain blocked; no P12 copy/audio pack. | Versioned pre-reviewed translations, emergency/helpline wording, approved audio assets/voice profiles, pronunciation review, retirement and rollback. | Live mistranslation, unsafe reassurance, wrong emergency wording, voice cloning/impersonation, outdated resource audio. | Reject live authoritative translation/TTS; wrong/retired voice; pronunciation/number tests; static asset/version mismatch; fallback to visible text. | Nonclinical synthetic TTS contract design only if separately authorized; no generated safety copy. | Any safety-critical phrase/audio lacks accountable approval or depends on live unreviewed generation. |
| Operations, failure isolation, and rollback | Operations/SRE; security; architecture; privacy | P7 manual fallback; optional features safe-off; no speech worker or provider health. | Deadline/retry/cancel policy; capacity/SLO; sandbox/network; telemetry/redaction; kill switches; provider/model rollback; incident and recovery runbook. | Retry storm, provider outage, worker exhaustion, stale result, leakage, fallback crossing region/provider, manual flow loss. | Deadline exhaustion; cancellation; OOM; outage; kill switch; rollback; telemetry canaries; no silent provider switch; P7 remains available. | Synthetic failure-state tests within a separately authorized engineering unit. | Failure can block manual/urgent flow, leak content, or pretend success. |
| Pilot and production approval | Product/institution release owner; privacy/legal; clinical safety; security; accessibility; operations | Documentation and six-job CI can provide engineering evidence only. | Signed, scoped decision records; approved environment/population/languages; residual-risk acceptance; monitoring/incident/rollback; expiry/re-review; pilot and production release decision. | Engineering evidence misrepresented as clinical/legal approval; scope creep; unmonitored harmful errors. | Protected-environment safe-off; no mock/fake; configuration drift; expired approval; rollback drill; exact-SHA release evidence. | None beyond already separately approved documentation/synthetic work. | Any upstream gate is incomplete or release record lacks scope, owners, date, expiry, and rollback. |

## 3. What may be authored now versus what requires decisions

Permitted now in this work unit:

- this source-grounded draft specification and readiness inventory;
- an honest as-built audit, requirement mapping, proposed contracts, negative-test plan, and STOP
  conditions; and
- a minimal progress-tracker entry that keeps P12 not started.

Not permitted by this pack:

- any code, tests, dependency, model, provider call, benchmark run, network access, audio fixture,
  migration, schema, API/BFF/UI, microphone/camera, storage, recording, locale asset, feature flag,
  Docker/CI/infrastructure, consent-policy change, or runtime activation;
- selection of a provider, model, voice, language pack, dataset, metric threshold, region, endpoint,
  quota, retention period, lawful basis, clinical phrase, or production population; or
- any claim that documentation, CI, a model card, an adapter, or a feature flag is human approval.

## 4. Requirement and acceptance status

`FR-LANG-001..012` and `AC-P12-001..009` are mapped in
`docs/16_MULTILINGUAL_SPEECH_SPEC.md`. Existing evidence is limited to P6 session language choice,
P7 manual text/touch and original-text metadata, safe browser/BFF boundaries, and independent manual
fallback. These do not constitute live P12 acceptance. All `AC-P12-001..009` remain **LIVE NOT
VERIFIED**.

## 5. Preserved cross-phase restrictions

- P8-C Stage 3 remains **BLOCKED**: no patient-facing AI, external clinical egress, message
  persistence, or candidate promotion is authorized.
- P9-C Stage 3 remains **BLOCKED**: no patient safety route, clinical policy, safety API, or live
  presentation is authorized.
- P10 live remains **0/9 APPROVED**: no trusted clinician assignment/review/summary workflow exists.
- P11 live remains **0/9 APPROVED (5 OPEN, 4 BLOCKED)**: P11-A/B/C/D are synthetic-only, P11-E is
  unimplemented, and `27_SECURITY_ARCHITECTURE.md` / `28_THREAT_MODEL.md` remain P11-focused drafts.
- P7 deterministic manual text/touch intake remains the supported fallback and cannot be made
  dependent on speech, translation, OCR, LLM, or a new provider.

P12 must not route speech-derived data into P8, P9, P10, or P11 in a way that bypasses their owners,
consent, source/provenance, clinical, privacy, or release gates.

## 6. Unsigned evidence and decision checklist

Roles below are accountable categories only. No name, signature, date, decision ID, or approval is
recorded by this draft.

- [ ] **Privacy/legal and consent owner:** approve purpose, population, notice/permission, age and
  guardian/assisted/kiosk treatment, egress/processor/region, retention/deletion, withdrawal, rights,
  research separation, and applicable legal/institutional basis.
- [ ] **Security and identity owner:** approve capture trust boundary, object/session authority,
  replay/deepfake non-authority, secrets/network, model supply chain, device residue, telemetry,
  incident response, and adversarial evidence.
- [ ] **Application/data architect:** approve port/stream separation, immutable contracts, lineage,
  idempotency, cancellation, transactions, schema ownership, and any future migration/API boundary.
- [ ] **Language engineering and data-governance owners:** approve dataset/license manifest,
  candidate set, immutable artifacts, reproducibility, representative strata, and benchmark method.
- [ ] **Clinical governance and bilingual subject experts:** approve critical-token/error taxonomy,
  medical semantics, acceptable thresholds, evaluation cases, and the boundary preventing clinical
  authority or fact promotion.
- [ ] **Accessibility/content/localization owner:** approve language packs, recording/failure/
  confirmation states, screen-reader/keyboard/reflow behavior, safety copy, pronunciation, and
  visible text/touch fallback.
- [ ] **Voice-rights/content owner:** approve any fixed voice asset, consent/license provenance,
  allowed languages, retirement, and prohibition on unapproved cloning.
- [ ] **Infrastructure/operations owner:** approve runtime isolation, capacity, SLO/deadline/retry,
  provider/model health, cost, network controls, kill switches, rollback, and recovery drills.
- [ ] **Product/institution release owner:** approve exact environment, population, languages, pilot
  boundaries, monitoring, residual risk, expiry/re-review, and release/rollback decision.

Required evidence includes the scoped human decision records; reviewed threat/data-flow/privacy and
clinical-language assessments; synthetic and licensed-data manifests; benchmark artifacts and
hashes; contract, accessibility, privacy, security, failure, race, egress and rollback tests; and
exact-SHA CI for the applicable future implementation. None is signed off here.

## 7. Current outstanding decisions and stop rule

Outstanding decisions are: purpose/population/consent; capture and audio lifetime; provider/model/
region/egress/license; datasets, thresholds and reviewers; contract/persistence/API ownership;
patient confirmation and accessibility; clinical/safety copy and approved voice assets; operations,
incident and rollback; and pilot/production authorization.

Any affected implementation must stop if its required owner decision, evidence, or scope is absent.
Do not fill the gap with a research recommendation or model knowledge. The next action after this
documentation PR is independent review and explicit disposition of the proposed gates—not P12-A
implementation.
