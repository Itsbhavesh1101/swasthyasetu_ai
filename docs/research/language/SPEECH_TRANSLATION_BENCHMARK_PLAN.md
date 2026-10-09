# SwasthyaSetu AI — Speech, Language & TTS Benchmark Plan

**Document ID:** `SSAI-OSS-R2B-LANG-002`  
**Status:** Benchmark specification  
**Review date:** 2026-10-09

---

# 1. Purpose

Select and configure SwasthyaSetu's language technology using medical/intake-specific evidence rather than generic model leaderboards.

The benchmark covers:

```text
ASR
language identification
transliteration
translation
TTS
streaming/runtime performance
privacy/failure behavior
```

---

# 2. ASR candidates

Initial benchmark:

```text
AI4Bharat IndicConformer multilingual
AI4Bharat Hindi monolingual IndicConformer
faster-whisper large-v3 / turbo candidate
whisper.cpp equivalent Whisper checkpoint
BHASHINI Hindi/multilingual ASR service
```

Where resource limits apply, include smaller Whisper variants as explicit latency/quality trade-offs.

---

# 3. Evaluation data policy

Use:

- publicly licensed datasets;
- synthetic speech;
- consented/de-identified research audio if later approved.

Never commit real patient conversations.

Recommended public research source:

```text
IndicVoices licensed subset(s)
```

plus a SwasthyaSetu synthetic medical corpus.

---

# 4. Core speech strata

At minimum:

```text
clean Hindi
clean English
Hindi with English medical terms
Hinglish code-switching
Romanized-Hindi target representation cases
slow elderly-style speech
fast speech
quiet voice
hesitation / self-correction
numbers/dates
medication lists
symptom narratives
mental-health safety phrases
```

---

# 5. Noise strata

Create controlled mixtures:

```text
quiet room
40 dBA-ish office background
OPD conversation background
fan/AC noise
keyboard/touch noise
announcement noise
multiple speakers in background
corridor/reverberation
mobile-phone compression
microphone clipping
```

Record exact SNR or reproducible mixing parameters where possible.

---

# 6. Device strata

Test representative:

```text
laptop microphone
budget Android phone
mid-range Android phone
USB kiosk microphone
Bluetooth headset where relevant
```

Do not optimize only on studio WAV files.

---

# 7. ASR metrics

Generic:

```text
WER
CER
sentence exact match
real-time factor
p50/p95 latency
```

Medical/safety:

```text
medication-name recall
dose-value recall
dose-unit recall
frequency recall
symptom term recall
anatomical term recall
duration/time expression recall
negation accuracy
self-harm phrase preservation
number substitution rate
decimal substitution rate
critical omission rate
false insertion rate
```

---

# 8. Code-switch metrics

For Hindi-English code-switching:

```text
token-level language accuracy
English token preservation
Hindi token preservation
switch-boundary accuracy
medical English term preservation
```

Track script separately from language.

Example:

```text
"mujhe chest pain kal se hai"
```

must not be considered wrong merely because one system emits Devanagari Hindi and another emits Romanized Hindi.

Evaluate semantic/token preservation before output-script preference.

---

# 9. ASR hallucination tests

Test:

```text
silence
breathing only
background speech
non-speech hospital noise
music
very low-volume speech
```

Measure:

```text
non-empty hallucination rate
hotword hallucination rate
fabricated medication rate
```

---

# 10. Hotword/glossary benchmark

If medical vocabulary biasing is tested:

Create categories:

```text
common medications
confusable medication names
rare diseases
hospital departments
local proper names
```

Test with:

```text
spoken hotword present
spoken similar word
word absent
silence
noise
```

Report gain in recall versus false-insertion increase.

Do not enable hotwords by default unless net safety benefit is demonstrated.

---

# 11. Streaming ASR metrics

For BHASHINI or future streaming adapters:

```text
first partial latency
stable partial latency
final transcript latency
revision count
final-vs-partial divergence
disconnect recovery
packet-loss behavior
```

Patient UI must clearly distinguish partial from final text.

---

# 12. Language-ID benchmark

Candidates:

```text
IndicLID
BHASHINI LID
simple script heuristic baseline
```

Test:

```text
native Hindi
Romanized Hindi
English
Hinglish
short 1-3 word utterances
medical terms only
numbers
drug names
mixed punctuation
typos
```

Metrics:

```text
accuracy
macro F1
confidence calibration
abstention coverage
short-text accuracy
Romanized Hindi F1
Hinglish ambiguity rate
```

A model should be allowed to return/trigger `UNCERTAIN`.

---

# 13. Transliteration benchmark

Candidates:

```text
IndicXlit
BHASHINI transliteration
deterministic dictionary/rules baseline for selected medical terms
```

Evaluate both directions:

```text
Romanized Hindi -> Devanagari
Devanagari -> Romanized Hindi
```

Metrics:

```text
CER
word exact match
top-k recall where available
named-entity accuracy
medical-term preservation
medication-name corruption rate
```

Important token classes:

```text
English medical word
drug brand/generic
person name
hospital name
abbreviation
number
unit
native Hindi
```

---

# 14. Selective transliteration benchmark

Compare:

```text
A. transliterate entire sentence
B. language-aware selective transliteration
C. entity-aware selective transliteration
```

Expected safest strategy is likely C, but benchmark it.

---

# 15. Translation candidates

```text
IndicTrans2 1B
IndicTrans2 distilled model
BHASHINI translation service
```

Focus initial benchmark on:

```text
Hindi -> English
English -> Hindi
```

and later extend to more Indian languages.

---

# 16. Translation automatic metrics

Use:

```text
COMET or suitable learned metric where licensing permits
chrF
SacreBLEU
```

Do not make final healthcare selection from BLEU alone.

---

# 17. Medical translation human review

Create bilingual review rubric for:

```text
meaning preservation
negation
temporality
severity
uncertainty
medication names
dosage
numbers
anatomy
self-harm/crisis wording
respectful/local language
```

Each item can be scored:

```text
0 dangerous error
1 major error
2 minor error
3 acceptable
```

Any dangerous error category receives separate analysis.

---

# 18. Translation adversarial cases

Examples:

```text
"I do not have chest pain now."
"I had chest pain yesterday but not today."
"I take 0.5 mg, not 5 mg."
"I thought about hurting myself last year, not now."
"I don't know whether I am pregnant."
"I stopped the medicine two weeks ago."
```

Evaluate whether meaning changes.

---

# 19. TTS candidates

```text
BHASHINI hosted TTS
IndicF5
legacy Indic-TTS
```

Focus first on Hindi and English.

---

# 20. TTS quality metrics

Automatic where useful:

```text
generation latency
real-time factor
failure rate
audio duration
loudness consistency
```

Human:

```text
intelligibility
naturalness/MOS
medical-word pronunciation
number pronunciation
Hindi-English code-switch pronunciation
elderly listener comprehension
```

---

# 21. TTS medical pronunciation list

Build a governed test list containing:

```text
common medication generics
mg / mL
blood pressure values
temperature
dates/times
department names
common symptoms
helpline/resource language
```

Do not use a generated voice for emergency instructions until intelligibility is verified.

---

# 22. Voice cloning policy test

IndicF5 requires reference audio.

For normal SwasthyaSetu evaluation use:

```text
approved fixed system reference voice
```

Do not collect patient voice as a cloning reference.

Validate that:

- reference audio cannot be changed by normal patient API;
- only approved voice IDs are selectable;
- voice asset provenance/permission is documented.

---

# 23. Runtime environments

At minimum:

```text
CPU developer machine
single NVIDIA T4-class GPU if available
single modern NVIDIA GPU if available
Windows developer environment where feasible
Linux production-like container
edge/kiosk CPU for whisper.cpp
```

---

# 24. Performance metrics

ASR:

```text
cold start
warm start
real-time factor
p50/p95 final latency
memory
VRAM
throughput
```

Translation:

```text
tokens/s
sentence latency
batch throughput
RAM/VRAM
```

TTS:

```text
time to first audio
total generation time
real-time factor
memory/VRAM
```

---

# 25. Privacy/network tests

For local adapters:

- pre-download models;
- block outbound network;
- verify inference still works;
- record attempted network access;
- inspect cache/temp files.

For BHASHINI:

- record exact endpoint/service;
- record payload fields;
- verify TLS;
- ensure logs do not retain raw payload unnecessarily;
- confirm current account/terms/approval status before pilot.

---

# 26. Fault tests

ASR:

```text
corrupt WAV
wrong sample rate
empty audio
too-long audio
timeout
model unavailable
GPU OOM
```

Translation:

```text
empty input
oversized input
unsupported language
invalid Unicode
timeout
```

TTS:

```text
unsupported language
empty text
very long text
invalid voice ID
model failure
```

All produce typed failure, not fabricated output.

---

# 27. Dataset partitioning

Recommended:

```text
development subset
selection/benchmark subset
held-out final validation subset
```

Do not tune adapters repeatedly against final validation.

---

# 28. Reproducibility manifest

Every run records:

```text
candidate
repository commit
package versions
model ID
model revision
model checksum
dataset revision
hardware
OS
container digest
CUDA/cuDNN
configuration
language settings
VAD settings
hotwords
timestamp
```

---

# 29. Proposed ASR selection weighting

| Category | Weight |
|---|---:|
| Critical medical/safety token preservation | 25% |
| Hindi quality | 15% |
| Hinglish/code-switch quality | 15% |
| Noise robustness | 15% |
| Hallucination/omission safety | 10% |
| Latency/resources | 10% |
| Deployment/privacy | 5% |
| Maintenance/license | 5% |

License/terms incompatibility can still disqualify regardless of score.

---

# 30. Translation selection weighting

| Category | Weight |
|---|---:|
| Medical meaning preservation | 30% |
| Negation/temporality/safety preservation | 25% |
| Hindi-English general quality | 15% |
| Numbers/entities | 10% |
| Latency/resources | 10% |
| Deployment/privacy | 5% |
| Maintenance/license | 5% |

---

# 31. TTS selection weighting

| Category | Weight |
|---|---:|
| Intelligibility | 25% |
| Medical-term/number pronunciation | 20% |
| Hindi-English mixed pronunciation | 15% |
| Naturalness | 10% |
| Latency | 15% |
| Operational complexity | 10% |
| License/voice governance | 5% |

---

# 32. Acceptance principle

A provider wins only if it performs safely on the **actual patient-intake language distribution**.

No choice should be finalized because:

- it has more GitHub stars;
- it supports "22 languages" on a model card;
- a demo sounds impressive;
- generic WER is low.

---

# 33. Benchmark output artifacts

Produce:

```text
LANGUAGE_BENCHMARK_RESULTS.md
asr_results.parquet
translation_results.parquet
transliteration_results.parquet
lid_results.parquet
tts_results.csv
failure_taxonomy.csv
runtime_profiles.csv
selected_language_stack.json
```

---

# 34. Current hypothesis to test

Likely architecture:

```text
Server/local:
IndicConformer or faster-whisper
+
IndicLID
+
IndicXlit
+
IndicTrans2

Edge/kiosk:
whisper.cpp / smaller local runtime

Hosted/pilot:
BHASHINI adapters

TTS:
BHASHINI initially if terms/privacy permit,
or an approved local TTS after benchmark
```

This is a hypothesis, not the final production selection.
