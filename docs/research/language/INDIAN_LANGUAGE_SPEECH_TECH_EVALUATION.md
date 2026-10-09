# SwasthyaSetu AI — Indian Language Speech, Translation, Transliteration & TTS Technology Evaluation

**Document ID:** `SSAI-OSS-R2B-LANG-001`  
**Status:** Deep research / pre-benchmark decision  
**Review date:** 2026-10-09  
**Scope:** Indian-language ASR, noisy-OPD speech, Hinglish/code-switching, language ID, transliteration, translation, TTS, BHASHINI integration.

---

# 1. Executive conclusion

The correct SwasthyaSetu design is **not one multilingual model doing ASR + translation + Hinglish + TTS**.

Use separate capabilities:

```text
SpeechToTextPort
LanguageDetectionPort
TransliterationPort
TranslationPort
TextToSpeechPort
```

with multiple replaceable adapters.

The strongest current direction is:

```text
SpeechToTextPort
├── BhashiniASRAdapter            # hosted/pilot option
├── IndicConformerAdapter         # India-specialized local/server benchmark
├── FasterWhisperAdapter          # mature local/server fallback
└── WhisperCppAdapter             # edge/kiosk/offline benchmark

LanguageDetectionPort
├── IndicLIDAdapter               # local India-specific language/script hint
└── BhashiniLIDAdapter            # hosted option

TransliterationPort
├── IndicXlitAdapter              # Roman <-> Indic scripts
└── BhashiniTransliterationAdapter

TranslationPort
├── IndicTrans2Adapter            # preferred local India-focused candidate
└── BhashiniTranslationAdapter    # hosted/pilot option

TextToSpeechPort
├── BhashiniTTSAdapter            # broad hosted coverage candidate
├── IndicF5Adapter                # quality benchmark; governance constraints
└── LegacyIndicTTSAdapter         # reference/benchmark only
```

The most important architectural finding is that **Hinglish is a pipeline problem, not an ASR language setting**.

---

# 2. Requirements being evaluated

SwasthyaSetu requires language technology for:

- patient speech in English, Hindi and Hinglish;
- noisy hospital/OPD and kiosk environments;
- elderly users and low-literacy users;
- code-switched speech;
- local-language confirmation;
- preserving original patient wording;
- structured clinical-history extraction;
- safety-critical language such as negation, self-harm language, urgency and duration;
- Romanized Hindi;
- future Indian-language expansion;
- audio feedback / TTS;
- graceful fallback to text/touch;
- privacy-conscious local processing where feasible.

The language layer must never become final clinical authority.

---

# 3. Core safety invariants

## LANG-INV-001 — Preserve original evidence

Where policy permits retention, preserve:

```text
original audio reference
original ASR transcript
normalized transcript
language/script labels
transliteration output
translation output
```

as distinct artifacts.

Do not silently replace the source transcript with translation.

## LANG-INV-002 — Translation is derived evidence

Translated text is not the same thing as the patient's original wording.

## LANG-INV-003 — Low-confidence language identification is not truth

A language-ID model may guide routing but must not silently reinterpret ambiguous patient text.

## LANG-INV-004 — Safety checks should see original and normalized forms

Where practical, deterministic safety backstops should consider:

```text
original text
normalized text
Romanized/native-script variants
```

rather than only translated English.

## LANG-INV-005 — No forced Hinglish through English ASR mode

Do not set the ASR language to English merely to get Latin-script output from Hindi speech.

That can translate or distort Hindi rather than transliterate it.

## LANG-INV-006 — ASR failure falls back to text/touch

Speech is an accessibility channel, not a hard dependency for safety.

---

# 4. AI4Bharat IndicConformerASR

## 4.1 Requirement fit

Very strong.

The project provides ASR models for all 22 official Indian languages, including:

- Hindi;
- Marathi;
- Bengali;
- Gujarati;
- Kannada;
- Malayalam;
- Tamil;
- Telugu;
- Punjabi;
- Urdu;
- and others.

It offers:

```text
600M multilingual model
+
language-specific monolingual models
```

and is built around hybrid RNNT/CTC-style NeMo models.

## 4.2 Repository engineering maturity

This is the key trade-off.

The repository itself is extremely small compared with mature inference libraries.

It mainly provides:

- documentation;
- model links;
- AI4Bharat NeMo dependency instructions.

It does not provide the same level of polished package/API/runtime abstraction as faster-whisper.

The documented installation path requires AI4Bharat's NeMo fork.

Community issue evidence shows practical environment friction:

- CUDA / torchaudio compatibility;
- NeMo setup;
- Python/version pinning;
- community-provided working deployment recipes.

## 4.3 Architecture implication

Do not make the FastAPI application import AI4Bharat NeMo directly.

Use:

```text
SpeechToTextPort
    |
IndicConformerAdapter
    |
isolated ASR worker/container
```

Pin:

```text
AI4Bharat/NeMo commit
model artifact
model checksum
CUDA/PyTorch/Torchaudio versions
Python version
```

## 4.4 Why it remains important despite low stars

Its value comes from direct language fit, not community popularity.

Generic speech packages can have tens of thousands of stars and still be less appropriate for Indian language speech.

## 4.5 Code-switching uncertainty

The source material confirms 22-language coverage, but the repository does not establish that Hindi-English intra-utterance code-switching is reliable enough for SwasthyaSetu.

Therefore code-switching is a required benchmark axis.

## 4.6 Decision

**BENCHMARK BEFORE ADOPTION — preferred India-specialized local ASR candidate.**

---

# 5. faster-whisper

## 5.1 Engineering maturity

Strong.

The project provides:

- CTranslate2-based Whisper inference;
- CPU/GPU support;
- INT8 quantization;
- batching;
- VAD;
- word-level timestamps;
- multilingual mode;
- hotword support;
- CI with formatting/lint/tests;
- PyPI packaging.

This makes it operationally much easier than IndicConformer.

## 5.2 Why it matters for SwasthyaSetu

Potential roles:

```text
general local ASR baseline
server fallback
developer-friendly local inference
English speech
Hindi benchmark comparator
```

## 5.3 Hinglish limitation

A repository issue demonstrates a critical point:

Hindi speech with Hindi language configuration is transcribed in Devanagari.

Changing the ASR language to English can produce English translation rather than Romanized Hindi.

Therefore:

```text
Hindi audio
  != set language=en
  -> Hinglish
```

For Romanized Hindi, use a separate transliteration step.

## 5.4 Hotword risk

Medical vocabulary boosting sounds attractive, but hotwords can create false-positive output.

A repository issue reports configured hotwords appearing even in silent audio.

Therefore medical hotwords such as:

```text
metformin
amlodipine
warfarin
insulin
```

must not be treated as evidence merely because the decoder emitted them.

If hotwords are used:

```text
VAD
+
confidence/quality checks
+
benchmarking
+
original audio preservation
+
human review for consequential fields
```

are required.

## 5.5 Decision

**ADOPT AS BENCHMARK + ROBUST FALLBACK CANDIDATE.**

Final primary-vs-fallback role depends on the India-specific benchmark.

---

# 6. whisper.cpp

## 6.1 Why it belongs in the research set

whisper.cpp is a mature C/C++ Whisper implementation with strong edge/mobile/CPU deployment characteristics.

Potential SwasthyaSetu fit:

- offline kiosk;
- low-connectivity environment;
- CPU-only edge deployment;
- Android/native future clients;
- local privacy-preserving transcription.

## 6.2 Strengths

Typical ecosystem capabilities include:

- quantization;
- multiple hardware backends;
- streaming examples;
- server example;
- VAD integration;
- very broad platform support.

## 6.3 Limitation

Its speech quality is still fundamentally tied to the Whisper model family.

A more efficient runtime does not automatically improve Hindi/Hinglish accuracy.

## 6.4 Decision

**BENCHMARK FOR EDGE/KIOSK/OFFLINE.**

Do not choose it as primary server ASR purely because of stars or portability.

---

# 7. AI4Bharat IndicVoices — evaluation dataset opportunity

IndicVoices is especially valuable for our benchmark design.

The current public dataset describes:

- 22 Indian languages;
- natural/spontaneous speech;
- read, extempore and conversational speech;
- broad geographic coverage across India;
- thousands of speakers;
- a CC BY 4.0 license.

This is much more relevant to real patient conversation than only reading clean studio sentences.

## Recommended use

Do not download the entire corpus unnecessarily.

Create a documented evaluation subset covering:

```text
Hindi
English-accented Indian speech where licensed sources exist
regional Hindi accents
conversational speech
elderly-like / slower speech where metadata permits
background noise augmentation
```

Add separate SwasthyaSetu-specific synthetic medical utterances.

---

# 8. AI4Bharat IndicTrans2

## 8.1 Requirement fit

Very strong for Indian translation.

The model family supports translation among English and the scheduled Indian-language ecosystem.

Public Hugging Face model cards are currently MIT licensed.

Available classes include:

```text
1B models
distilled ~200M / 320M models
English -> Indic
Indic -> English
Indic -> Indic
```

## 8.2 Prefer the Hugging Face-compatible path

The root training repository still carries a heavy research-oriented environment path involving:

- Fairseq;
- older Transformers pins;
- Indic NLP resources;
- source cloning.

The newer `huggingface_interface` is a better production-inference starting point.

## 8.3 Versioning caution

Current model documentation warns that the old high-level `translation` pipeline is not supported in Transformers v5.

Therefore production must pin:

```text
model revision
IndicTransToolkit version
Transformers major/minor version
tokenizer code revision
```

Do not use `trust_remote_code=True` without pinning the exact model revision.

## 8.4 Medical translation risk

IndicTrans2 is a general translation model, not a clinically validated medical translator.

It must be tested on:

```text
negation
temporal phrases
dose expressions
medication names
anatomy
symptom severity
self-harm statements
conditional statements
```

## 8.5 Decision

**ADOPT BEHIND `TranslationPort`, subject to medical-language benchmark.**

Use distilled models first for latency experiments, then compare the larger model if quality gains justify cost.

---

# 9. AI4Bharat IndicLID

## 9.1 Why it is highly relevant

IndicLID handles both:

```text
native-script Indian languages
romanized Indian languages
```

including Romanized Hindi.

It exposes 47 classes across native/romanized variants plus English/other.

This makes it unusually well aligned with Hinglish input routing.

## 9.2 Benchmark results from its own documentation

Native-script identification is reported as very strong.

Romanized language identification is materially harder.

The full two-stage Romanized model is reported around:

```text
accuracy ~0.80
F1 ~0.75
```

on the project's benchmark.

That is useful, but not sufficient to treat its result as clinical truth.

## 9.3 Safe use

Use IndicLID to produce:

```text
language_hint
script_hint
confidence
```

not:

```text
authoritative_patient_language
```

When confidence is low:

- preserve original;
- allow user correction;
- ask clarification where clinically important.

## 9.4 Decision

**ADOPT/CONSIDER AS LOCAL `LanguageDetectionPort` CANDIDATE.**

Benchmark on actual Hinglish and short medical phrases before final adoption.

---

# 10. AI4Bharat IndicXlit

## 10.1 Requirement fit

Strong for Romanized/native-script conversion.

The project supports Roman-to-Indic and Indic-to-Roman transliteration across a broad set of Indian languages.

This addresses a major Hinglish UX need that ASR itself does not solve.

## 10.2 Important accuracy limitation

Published project benchmark results show that top-1 transliteration is far from perfect for named entities.

That matters because healthcare has many names that should not be transliterated incorrectly:

```text
drug names
doctor names
hospital names
brands
technical terms
abbreviations
```

## 10.3 Safe strategy

Do not transliterate every token.

Preferred flow:

```text
token / segment classification
   |
   +-- native Hindi -> optional Romanization
   +-- Romanized Hindi -> optional native normalization
   +-- English word -> preserve
   +-- medication / acronym -> preserve unless validated
```

## 10.4 Performance

Issue history includes CPU slowness concerns.

Because this is an ~11M model, a production adapter should test:

- batched token processing;
- warm model reuse;
- cache for repeated tokens;
- CPU latency.

## 10.5 Decision

**ADOPT/CONSIDER BEHIND `TransliterationPort`, benchmark required.**

---

# 11. Hinglish architecture

Hinglish should not be treated as one official language model.

Use a staged representation:

```text
audio
  |
ASR
  |
original transcript
  |
language/script/segment analysis
  |
selective transliteration
  |
normalized Hinglish/native-script representation
  |
optional translation
```

Example:

Patient says:

```text
"mujhe kal se chest pain ho raha hai"
```

The system may preserve:

```text
original_asr_text
romanized_hindi_normalized
native_script_normalized
english_translation
```

but none of the derived representations may erase the original source.

## Why this matters clinically

A translation can alter:

```text
negation
duration
severity
uncertainty
temporality
```

Therefore source text remains accessible to downstream review.

---

# 12. BHASHINI / ULCA ecosystem

## 12.1 Strategic fit

BHASHINI is extremely relevant because it provides an India-focused ecosystem around:

- ASR;
- translation;
- TTS;
- transliteration;
- language detection;
- other language services;
- models/datasets;
- hosted inference.

The ULCA repository is MIT licensed and defines standardized datasets/model contribution and benchmarking concepts.

## 12.2 Integration model

Treat BHASHINI as an **external provider**, not as the platform architecture.

Use individual adapters:

```text
BhashiniASRAdapter
BhashiniTranslationAdapter
BhashiniTTSAdapter
BhashiniTransliterationAdapter
BhashiniLanguageDetectionAdapter
```

all implementing SwasthyaSetu-owned ports.

## 12.3 Privacy implication

Sending:

```text
audio
patient statements
clinical text
```

to a hosted provider is external processing of sensitive data.

Before real deployment, require:

- explicit approved privacy design;
- appropriate consent/disclosure;
- minimum necessary payload;
- contractual/terms review;
- retention/data-handling review;
- network/security review.

## 12.4 Terms / access caution

Current BHASHINI platform terms state that API/service access may require registration, authentication and approval, and unauthorized commercial use requires prior written approval.

Therefore:

**do not assume a hackathon/PoC API key equals unrestricted production authorization.**

Treat BHASHINI initially as:

```text
research
sandbox
demo
pilot candidate
```

until deployment rights and data-handling terms are confirmed.

## 12.5 Value even if not used in production

BHASHINI remains useful for:

- benchmarking alternative models;
- service discovery;
- access to India-language models;
- evaluating streaming API patterns;
- interoperability with the national language ecosystem.

## 12.6 Decision

**ADOPT AS OPTIONAL EXTERNAL PROVIDER / PILOT INTEGRATION, not hard dependency.**

---

# 13. AI4Bharat Dhruva Evaluation Suite

The Dhruva evaluation repository is not mature enough to become our benchmark platform wholesale, but it provides useful reference patterns:

- ASR WER evaluation;
- NMT SacreBLEU;
- transliteration CER;
- REST load testing;
- WebSocket load testing;
- task-oriented YAML configuration.

## Decision

**REFERENCE / BORROW EVALUATION PATTERNS.**

Build the SwasthyaSetu benchmark harness around our own safety/medical metrics.

---

# 14. TTS requirement decomposition

TTS is an accessibility capability, not a cosmetic extra.

We care about:

- intelligibility;
- Hindi pronunciation;
- medical-term pronunciation;
- speed;
- naturalness;
- predictable volume;
- low latency;
- offline/hosted privacy;
- no accidental voice impersonation.

---

# 15. AI4Bharat IndicF5

## 15.1 Strengths

IndicF5 is a modern multilingual Indian TTS model.

Its public model materials describe support for 11 Indian languages, including Hindi.

It uses reference audio + reference transcript conditioning and can reproduce speaker characteristics.

## 15.2 Governance concern: voice cloning

The current model terms explicitly say voice cloning should only be done with explicit permission.

For SwasthyaSetu:

**do not clone the patient's voice by default.**

If IndicF5 is used, preferred configuration is:

```text
fixed approved system voice prompt
+
documented rights/consent
+
no user-supplied reference voice in normal patient workflow
```

## 15.3 Engineering maturity

The repository is relatively small and issue reports show significant inference-latency and environment questions.

One issue reports extremely slow Hindi generation on a T4 for a long paragraph.

This makes it unsuitable to assume as the default kiosk TTS before benchmarking.

## 15.4 Decision

**BENCHMARK BEFORE ADOPTION.**

Evaluate quality against latency and operational cost.

---

# 16. Older AI4Bharat Indic-TTS

## 16.1 Strengths

- 13 Indian-language focus;
- FastPitch + HiFi-GAN-era models;
- research provenance;
- models exposed through the BHASHINI ecosystem.

## 16.2 Engineering limitations

The repository setup reflects an older research stack and includes custom forks/manual patches.

That increases maintenance cost for a new 2026 production system.

## 16.3 Decision

**REFERENCE / BENCHMARK ONLY for self-hosting.**

If the same models are available through a maintained BHASHINI service, hosted adapter evaluation may be more practical.

---

# 17. Recommended SwasthyaSetu language pipeline

```text
Microphone
   |
Audio validation / resampling / VAD
   |
SpeechToTextPort
   |
ASRResult
   |-- original transcript
   |-- timestamps
   |-- ASR confidence/quality metadata
   |-- language hint
   |
LanguageDetectionPort
   |
Segment/token classification
   |
+-----------------------+
|                       |
TransliterationPort     TranslationPort
|                       |
native/Roman form       target-language meaning
+-----------+-----------+
            |
      Canonical language evidence
            |
      Clinical extraction
            |
  Deterministic safety / workflows
```

The LLM may later assist with structured extraction, but should consume labeled source variants rather than one overwritten normalized string.

---

# 18. ASR result contract requirements

Every result should record:

```text
provider
adapter_version
model_name
model_version
model_checksum?
language_requested?
language_detected?
language_confidence?
segments
word timestamps where available
overall quality/confidence if available
VAD configuration
hotwords/glossary configuration
runtime backend
device
warnings
```

If confidence semantics differ between models, label the confidence kind.

---

# 19. Hotword / medical glossary policy

Medical-term biasing is potentially useful but dangerous.

Rules:

1. never consider a hotword match proof the patient said the term;
2. VAD before decoding;
3. maintain glossary provenance/version;
4. test silence and noise;
5. test phonetically similar medication names;
6. track false-insertion rate;
7. feature-flag medical hotword boosting initially.

---

# 20. Translation evidence model

Store:

```text
source_text
source_language
target_text
target_language
translation_provider
model/version
translation_quality?
created_at
```

Never mutate the source field into the translated text.

---

# 21. Romanization/transliteration evidence model

Store:

```text
source_token/segment
source_script
target_script
candidate_output
confidence/rank if available
provider
model/version
```

Preserve named entities when the model is uncertain.

---

# 22. TTS contract requirements

TTS output metadata:

```text
provider
model/version
language
voice_id / approved voice profile
sample_rate
duration
reference_voice_id?   # system-owned only where applicable
created_at
```

Do not expose raw patient voice as a cloning prompt unless an explicitly approved future feature exists.

---

# 23. Local vs hosted deployment decision

## Local ASR/translation advantages

- patient data remains within deployment boundary;
- predictable retention;
- offline operation possible;
- no per-request external dependency.

## Local disadvantages

- GPU/runtime maintenance;
- model updates;
- capacity planning;
- language-model complexity.

## Hosted/BHASHINI advantages

- broad language coverage;
- lower model operations burden;
- potential streaming APIs;
- national language ecosystem alignment.

## Hosted disadvantages

- external sensitive-data processing;
- network dependency;
- terms/access dependency;
- provider availability;
- deployment authorization.

Therefore SwasthyaSetu must support both through ports.

---

# 24. Recommended pre-benchmark shortlist

## ASR

```text
IndicConformer        India-specialized primary challenger
faster-whisper        mature local fallback/baseline
whisper.cpp           edge/kiosk baseline
BHASHINI ASR          hosted/pilot option
```

## Language ID

```text
IndicLID              primary local candidate
BHASHINI LID          hosted alternative
```

## Transliteration

```text
IndicXlit             primary local candidate
BHASHINI transliteration
```

## Translation

```text
IndicTrans2           preferred local candidate
BHASHINI translation  hosted alternative
```

## TTS

```text
BHASHINI TTS          broad hosted candidate
IndicF5               local quality benchmark
Indic-TTS             legacy benchmark/reference
```

---

# 25. Model/data license manifest requirement

Every adopted language model or dataset receives:

```text
component_id
repository
model_repository
model_revision
source_code_license
model_license
dataset_license(s)
terms_of_use
commercial_use_notes
attribution_requirements
artifact_checksum
reviewed_at
reviewed_by
```

Do not assume repository MIT license automatically covers every training dataset or model artifact.

---

# 26. `trust_remote_code` rule

Some Hugging Face model integrations use custom model code.

If `trust_remote_code=True` is required:

- pin immutable model revision;
- inspect downloaded code;
- disable moving-main references;
- cache approved artifacts;
- compute checksums;
- scan dependencies;
- no uncontrolled model update in production.

---

# 27. Failure/degraded modes

## ASR unavailable

```text
show text/touch input
retain urgent-help controls
do not block deterministic crisis resources
```

## Language ID uncertain

```text
preserve original
ask user language preference / clarification
do not silently translate
```

## Transliteration unavailable

```text
display original script
allow manual text
```

## Translation unavailable

```text
keep original
avoid claiming translated output
```

## TTS unavailable

```text
show readable text
do not block patient workflow
```

---

# 28. Accessibility implications

TTS and speech input help:

- low literacy;
- motor accessibility;
- elderly patients;
- kiosk use.

But accessibility must still provide:

```text
text fallback
touch fallback
large text
high contrast
keyboard/screen-reader support
```

Speech-only UI is not acceptable.

---

# 29. Preliminary R2-B decisions

| Capability | Candidate | Decision |
|---|---|---|
| Local India ASR | IndicConformer | **BENCHMARK BEFORE ADOPTION** |
| Local generic ASR | faster-whisper | **ADOPT AS BASELINE/FALLBACK CANDIDATE** |
| Edge ASR | whisper.cpp | **BENCHMARK FOR KIOSK/OFFLINE** |
| Hosted India ASR | BHASHINI | **OPTIONAL PILOT PROVIDER** |
| Translation | IndicTrans2 | **ADOPT BEHIND ADAPTER, BENCHMARK MEDICAL TEXT** |
| Language ID | IndicLID | **ADOPT/CONSIDER BEHIND ADAPTER** |
| Transliteration | IndicXlit | **ADOPT/CONSIDER BEHIND ADAPTER** |
| Hosted translation/transliteration/LID | BHASHINI | **OPTIONAL PROVIDER** |
| Local TTS | IndicF5 | **BENCHMARK BEFORE ADOPTION** |
| Older local TTS | Indic-TTS | **REFERENCE/BENCHMARK** |
| Hosted TTS | BHASHINI | **PRIMARY HOSTED TTS CANDIDATE** |
| Evaluation reference | Dhruva Evaluation Suite | **REFERENCE / BORROW PATTERNS** |

---

# 30. Final pre-benchmark recommendation

Do not choose one "language AI stack."

Build the ports first, then use the benchmark to decide per capability.

The likely first implementation targets are:

```text
FasterWhisperAdapter
IndicConformerAdapter
IndicLIDAdapter
IndicXlitAdapter
IndicTrans2Adapter
BhashiniLanguageServicesAdapter
Mock language adapters
```

TTS can be integrated after input/safety workflows are stable.

The exact winner remains benchmark-dependent.
