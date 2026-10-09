# SwasthyaSetu AI — Language Technology Adapter Contract Draft

**Document ID:** `SSAI-OSS-R2B-LANG-003`  
**Status:** Research-derived draft  
**Purpose:** Feed `16_MULTILINGUAL_SPEECH_SPEC.md` and language-related AI orchestration specs.

---

# 1. Port boundaries

Define separately:

```text
SpeechToTextPort
LanguageDetectionPort
TransliterationPort
TranslationPort
TextToSpeechPort
```

Do not use one `LanguageAIProvider` god interface.

---

# 2. SpeechToTextPort

Conceptual interface:

```python
class SpeechToTextPort(Protocol):
    async def transcribe(self, request: TranscriptionRequest) -> TranscriptionResult:
        ...
```

Request:

```text
audio_ref
audio_format
sample_rate?
language_hints[]
mode
enable_word_timestamps
glossary_id?
trace_id
```

Mode:

```text
BATCH
STREAM_FINALIZE
```

Streaming transport may use a separate streaming protocol interface.

---

# 3. TranscriptionResult

```text
status
original_text
segments[]
detected_language?
language_confidence?
duration_ms
warnings[]
engine_metadata
quality_metadata
```

Status:

```text
SUCCEEDED
PARTIAL
FAILED
LOW_CONFIDENCE
```

---

# 4. ASR segment

```text
start_ms
end_ms
text
confidence?
confidence_kind?
language?
words[]
```

Word:

```text
start_ms?
end_ms?
text
confidence?
```

No fake confidence if provider does not expose one.

---

# 5. ASR engine metadata

Mandatory:

```text
provider
adapter_version
model_name
model_version
model_revision?
model_checksum?
runtime
device
VAD_enabled
VAD_configuration?
language_requested?
hotword/glossary_version?
```

---

# 6. Streaming interface

Conceptual:

```python
class StreamingSpeechToTextPort(Protocol):
    async def open_session(self, config: StreamingASRConfig) -> StreamingASRSession:
        ...
```

Events:

```text
PARTIAL_TRANSCRIPT
FINAL_TRANSCRIPT
LANGUAGE_UPDATE
QUALITY_WARNING
ERROR
SESSION_CLOSED
```

Partial text must not be persisted as final clinical evidence until finalized.

---

# 7. LanguageDetectionPort

```python
class LanguageDetectionPort(Protocol):
    async def detect(self, request: LanguageDetectionRequest) -> LanguageDetectionResult:
        ...
```

Request:

```text
text
candidate_languages?
include_script
```

Result:

```text
candidates[]
is_uncertain
provider_metadata
```

Candidate:

```text
language
script
confidence
```

Support native and Romanized language classes.

---

# 8. TransliterationPort

```python
class TransliterationPort(Protocol):
    async def transliterate(self, request: TransliterationRequest) -> TransliterationResult:
        ...
```

Request:

```text
text
source_language?
source_script
target_script
protected_spans[]
```

`protected_spans` is important for:

```text
medication names
numbers
units
URLs
IDs
acronyms
English medical terms
```

---

# 9. Transliteration result

```text
source_text
output_text
segments[]
warnings[]
engine_metadata
```

Segment:

```text
source
output
confidence?
rank?
was_protected
```

---

# 10. TranslationPort

```python
class TranslationPort(Protocol):
    async def translate(self, request: TranslationRequest) -> TranslationResult:
        ...
```

Request:

```text
source_text
source_language
target_language
domain_hint?
protected_terms[]
trace_id
```

`domain_hint` is metadata only unless the model has an approved domain mechanism.

---

# 11. Translation result

```text
source_text
translated_text
source_language
target_language
quality_metadata?
warnings[]
engine_metadata
```

Do not discard `source_text`.

---

# 12. TextToSpeechPort

```python
class TextToSpeechPort(Protocol):
    async def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        ...
```

Request:

```text
text
language
voice_profile_id
speech_rate?
trace_id
```

Do not accept arbitrary user reference audio in the default patient endpoint.

---

# 13. Approved voice profile

```text
voice_profile_id
provider
model
language(s)
reference_asset_ref?
permission_provenance
approval_status
created_at
retired_at?
```

This lets SwasthyaSetu govern voice-cloning-style models safely.

---

# 14. Synthesis result

```text
status
audio_ref
sample_rate
duration_ms
provider_metadata
warnings[]
```

---

# 15. Bhashini adapter family

Prefer a shared low-level authenticated client with separate domain adapters:

```text
BhashiniClient
├── BhashiniASRAdapter
├── BhashiniTranslationAdapter
├── BhashiniTTSAdapter
├── BhashiniTransliterationAdapter
└── BhashiniLanguageDetectionAdapter
```

Do not expose BHASHINI-specific JSON contracts to application/domain modules.

---

# 16. Bhashini credentials

Credentials:

```text
API key
user/account ID
service configuration IDs
```

must live in secrets/configuration.

Never:

- commit keys;
- log keys;
- expose service credentials to browser clients.

Browser calls should go through SwasthyaSetu backend unless an approved direct-client design exists.

---

# 17. Local adapter candidates

```text
IndicConformerAdapter
FasterWhisperAdapter
WhisperCppAdapter
IndicLIDAdapter
IndicXlitAdapter
IndicTrans2Adapter
IndicF5Adapter
```

Each should be independently replaceable.

---

# 18. Worker isolation

Heavy local ASR/translation/TTS should not share the main FastAPI dependency environment if doing so creates GPU/native-package conflicts.

Preferred:

```text
FastAPI modular monolith
     |
internal job/RPC boundary
     |
language worker(s)
```

Logical ownership remains the language/speech bounded context.

---

# 19. Canonical language evidence

Create a value object such as:

```text
LanguageEvidence
```

containing:

```text
original_text
normalized_text?
language_candidates[]
script_candidates[]
romanized_form?
native_script_form?
translations[]
source_audio_ref?
provenance
```

Do not flatten all fields into one final string.

---

# 20. Provenance

For every derived text:

```text
source_artifact_id
operation
provider
model/version
model revision/checksum
created_at
quality/confidence
input_language
output_language
```

---

# 21. Safety processing order

Suggested:

```text
ASR final transcript
   |
preserve original
   |
language/script detection
   |
local safety backstop on original/known variants
   |
normalization/transliteration/translation
   |
structured extraction
   |
deterministic clinical policy
```

Do not make safety depend solely on translated English.

---

# 22. Hinglish normalization service

A SwasthyaSetu-owned application service may orchestrate:

```text
LanguageDetectionPort
TransliterationPort
approved terminology protection
```

but it does not become a diagnosis engine.

---

# 23. Protected-term registry

Potential categories:

```text
medication
unit
lab analyte
medical acronym
provider/facility name
resource/helpline
```

Used to prevent destructive transliteration/translation.

Every registry entry should carry source/version.

---

# 24. Medical glossary use in ASR

Glossary/hotword lists are optional.

Configuration:

```text
glossary_id
version
terms[]
language
scope
```

Never infer a clinical fact simply because an ASR glossary contained a word.

---

# 25. Error codes

Suggested internal codes:

```text
ASR_UNAVAILABLE
ASR_TIMEOUT
ASR_INVALID_AUDIO
ASR_LOW_CONFIDENCE
ASR_UNSUPPORTED_LANGUAGE
LANGUAGE_UNCERTAIN
TRANSLITERATION_UNAVAILABLE
TRANSLATION_UNAVAILABLE
TRANSLATION_UNSUPPORTED_PAIR
TTS_UNAVAILABLE
TTS_INVALID_VOICE
EXTERNAL_LANGUAGE_SERVICE_DENIED
```

Map to stable API errors through platform error policy.

---

# 26. Retry rules

Safe transient operations may retry with bounded exponential backoff.

Do not retry:

```text
invalid input
unsupported language
permission failure
consent failure
```

indefinitely.

---

# 27. External-processing consent

Before hosted speech/translation if policy requires:

```text
consent.check(EXTERNAL_AI_PROCESSING)
```

or the later approved privacy rule.

The adapter must never decide consent itself.

---

# 28. Data minimization

For translation:

send only the text segment needed.

For ASR:

send only required audio segment/session.

Avoid attaching:

```text
full patient profile
unrelated history
identifiers
```

to language-provider requests.

---

# 29. Logging

Allowed:

```text
provider
operation
language
duration
latency
result status
error code
model version
```

Not by default:

```text
raw audio
raw transcript
translated clinical text
API keys
```

---

# 30. Cache policy

Translation/transliteration may use carefully scoped caching only when privacy policy allows.

Cache keys must not expose patient text.

TTS static UI phrases are good cache candidates.

Patient-specific speech/text caching requires privacy review.

---

# 31. Static safety phrases

Critical patient-facing safety copy should preferably use:

```text
pre-reviewed translations
+
pre-generated/approved TTS assets where practical
```

rather than translating/generating emergency copy live on every request.

---

# 32. TTS fallback hierarchy

For critical reviewed text:

```text
approved prerecorded/static asset
  -> approved TTS provider
  -> visible text
```

No workflow should block waiting for TTS.

---

# 33. Feature flags

Recommended:

```text
speech.asr.indicconformer
speech.asr.faster_whisper
speech.asr.bhashini
speech.asr.whisper_cpp
language.indiclid
language.indicxlit
language.indictrans2
language.bhashini
speech.tts.indicf5
speech.tts.bhashini
speech.medical_hotwords
```

Experimental/high-risk features default off.

---

# 34. Adapter contract tests

All ASR adapters:

```text
clean speech
silence
noise
empty audio
unsupported format
timeout
Hindi
English
Hinglish
numbers
medical term
```

All translation adapters:

```text
Hindi -> English
English -> Hindi
negation
numbers
unsupported pair
timeout
```

All transliteration adapters:

```text
Roman Hindi
Devanagari Hindi
protected English term
medication token
empty text
```

TTS:

```text
Hindi
English
numbers
mixed medical phrase
invalid voice
timeout
```

---

# 35. Research-to-production promotion

An adapter becomes production-enabled only after:

```text
benchmark passed
license/terms reviewed
security/privacy review
model revision pinned
failure behavior tested
observability added
feature flag configured
```

---

# 36. Initial implementation recommendation

For early engineering scaffolding, build:

```text
MockSpeechToTextAdapter
MockLanguageDetectionAdapter
MockTransliterationAdapter
MockTranslationAdapter
MockTextToSpeechAdapter
```

first.

Then add benchmark adapters without making them default.

This prevents research dependency selection from blocking the core product architecture.
