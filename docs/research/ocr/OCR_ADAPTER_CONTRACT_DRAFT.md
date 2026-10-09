# SwasthyaSetu AI — OCR / Document Parser Adapter Contract Draft

**Document ID:** `SSAI-OSS-R2A-OCR-003`  
**Status:** Research-derived draft, to feed `15_DOCUMENT_AI_OCR_SPEC.md`

---

# 1. Why two ports

SwasthyaSetu should distinguish:

```text
DocumentParserPort
OCRPort
```

because a born-digital PDF should not necessarily be rasterized and OCR'd, while a phone photo must be.

---

# 2. DocumentParserPort

Conceptual interface:

```python
class DocumentParserPort(Protocol):
    async def parse(self, request: DocumentParseRequest) -> DocumentParseResult:
        ...
```

Request:

```text
document_id
object_ref
mime_type
page_range?
language_hints[]
mode
trace_id
```

Result:

```text
status
pages[]
native_text_coverage?
structured_blocks[]
tables[]
images[]
warnings[]
provider_metadata
raw_artifact_ref?
```

Potential implementation:

```text
DoclingDocumentParserAdapter
```

---

# 3. OCRPort

Conceptual interface:

```python
class OCRPort(Protocol):
    async def extract(self, request: OCRRequest) -> OCRResult:
        ...
```

Request:

```text
document_id
object_ref
page_range?
language_hints[]
script_hints[]
ocr_mode
preprocessing_profile?
trace_id
```

`ocr_mode`:

```text
TEXT_ONLY
LAYOUT
TABLE_AWARE
```

Do not put "diagnose" or "extract medication" into this port.

---

# 4. OCRResult

```text
status
pages[]
engine_metadata
warnings[]
processing_metrics
raw_artifact_ref?
```

Status:

```text
SUCCEEDED
PARTIAL
FAILED
NEEDS_FALLBACK
```

---

# 5. OCRPageResult

```text
page_number
width
height
rotation?
detected_language?
detected_script?
blocks[]
tables[]
page_confidence?
warnings[]
```

---

# 6. OCRBlock

```text
block_id
text
bbox
polygon?
block_type?
confidence?
confidence_kind?
language?
script?
reading_order?
```

`confidence_kind` prevents false equivalence between recognizer probabilities and heuristic/VLM quality scores.

---

# 7. TableResult

```text
table_id
bbox?
rows
columns
cells[]
structure_confidence?
```

Cell:

```text
row
column
row_span?
column_span?
text
bbox?
confidence?
```

---

# 8. Engine metadata

Mandatory:

```text
provider
adapter_version
engine_version
model_name
model_version
model_checksum?
runtime_backend
device
language_configuration
```

---

# 9. VLM fallback

Use a separate capability/flag:

```text
VLMDocumentParserPort
```

or explicit OCR result source type.

Do not pretend VLM text has the same confidence semantics as conventional OCR.

Potential adapters:

```text
PaddleOCRVLAdapter
SuryaAdapter
```

---

# 10. Routing policy

The documents application service selects a strategy.

Example:

```text
native text coverage sufficient
    -> DocumentParserPort

else if Hindi/Devanagari
    -> PaddleOCR Devanagari

else if English/Latin
    -> PaddleOCR conventional

if table heavy
    -> PPStructure path

if severe handwriting / low-quality output
    -> VLM fallback

if edge CPU profile
    -> RapidOCR candidate
```

This policy is not clinical diagnosis logic, but it should still be versioned/configured for reproducibility.

---

# 11. Failure behavior

OCR adapter must never return `SUCCEEDED` with silently missing pages.

If one page fails:

```text
overall = PARTIAL
page warning/error recorded
document state = NEEDS_REVIEW or retry/fallback
```

---

# 12. Time/resource bounds

Each adapter receives configured:

```text
max_pages
max_pixels_per_page
timeout_per_page
max_document_runtime
memory profile
concurrency
```

---

# 13. Network policy

After models are provisioned, production workers should not require general outbound internet access.

Remote API adapters, if ever enabled, must be separately configured and consent/privacy reviewed.

---

# 14. Provenance mapping

OCR output provenance should include:

```text
source_type = OCR or DOCUMENT_AI
document_id
processing_run_id
provider
model/version
page
bbox/block_id
confidence
```

Downstream medical candidate facts must retain the originating block/page reference.

---

# 15. Low-confidence path

Do not discard low-confidence text.

Represent:

```text
text
confidence
NEEDS_CONFIRMATION
```

Critical entity extraction may use a stricter review policy than generic text.

---

# 16. Human review

Clinician/user review should be able to inspect:

```text
original page image
OCR block
candidate extracted fact
confidence/provenance
```

Confirmation updates fact verification state, not the raw OCR artifact.

---

# 17. Storage

Original file:

```text
object storage
```

OCR metadata/results:

```text
database + derived artifact storage
```

Do not duplicate large page images into relational JSON.

---

# 18. Recommended initial adapters

```text
PaddleOCROCRAdapter
PaddleOCRVLMAdapter
DoclingDocumentParserAdapter
MockOCRAdapter
```

Benchmark-only:

```text
SuryaOCRAdapter
DocTROCRAdapter
RapidOCROCRAdapter
TesseractOCRAdapter
```

After benchmark, retain only justified production adapters.

---

# 19. Adapter tests

Each adapter must pass a shared contract suite:

```text
single page
multi-page
Hindi
English
mixed page
table
rotation
low quality
malformed input
timeout
partial page failure
model unavailable
```

---

# 20. Architecture impact

This draft does **not** require changing SwasthyaSetu's modular-monolith decision.

Heavy OCR can run in a separate worker process/container while remaining logically owned by the `documents` bounded context.
