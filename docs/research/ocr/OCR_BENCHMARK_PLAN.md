# SwasthyaSetu AI — OCR Benchmark Plan

**Document ID:** `SSAI-OSS-R2A-OCR-002`  
**Status:** Benchmark specification  
**Purpose:** Decide the production OCR/document-parsing stack using SwasthyaSetu-specific evidence.

---

# 1. Benchmark candidates

Mandatory first benchmark:

```text
PaddleOCR conventional / PPStructure
PaddleOCR-VL fallback
Surya
docTR
Tesseract
RapidOCR
Docling native document pipeline
```

Docling is assessed as a parser/orchestrator, not only OCR accuracy.

---

# 2. Dataset policy

Use only:

- synthetic records;
- publicly licensed medical-like documents;
- deliberately de-identified records approved for testing.

Do not commit real patient data.

Every benchmark item receives a dataset manifest entry with provenance/license.

---

# 3. Three-stage benchmark

## Stage A — engineering smoke set

~60 pages.

Purpose:

- integration;
- crashes;
- API compatibility;
- output normalization;
- baseline resource measurements.

## Stage B — selection set

Target ~300 pages.

Purpose:

- choose architecture/component versions.

Suggested document distribution:

```text
60  printed prescriptions
60  handwritten prescriptions
80  lab-report pages
50  discharge-summary pages
30  diagnostic/imaging-report pages
20  miscellaneous prior-record pages
```

## Stage C — validation set

Target 800–1,000+ pages once access to appropriate approved data exists.

Purpose:

- confirm selection before pilot;
- characterize rare failure modes.

---

# 4. Language strata

For Stage B, target coverage such as:

```text
English only            ~35%
Hindi / Devanagari      ~20%
English + Hindi mixed   ~30%
other Indic scripts     ~15%  (as project language scope expands)
```

The exact mix can be adjusted, but **mixed English-Hindi must not be omitted**.

---

# 5. Capture-quality strata

Ensure representation of:

```text
native digital PDF
clean flatbed scan
smartphone photo
skewed/rotated photo
uneven illumination
shadow/glare
compression
low resolution
fold/crease
old photocopy
background clutter
```

---

# 6. Handwriting strata

At minimum:

```text
clear block handwriting
cursive handwriting
doctor-like prescription shorthand
mixed handwritten + printed form
handwritten numeric values
handwritten dose/frequency
```

---

# 7. Ground-truth annotation

Each page should have:

```text
page-level language/script labels
line/word text
bounding boxes / polygons where feasible
reading order
table structure
document type
medical entities
critical numeric tokens
negation markers
dates
```

Medical entity labels:

```text
MEDICATION_NAME
DOSE_VALUE
DOSE_UNIT
FREQUENCY
ROUTE
DURATION
DIAGNOSIS_OR_PROBLEM_TEXT
LAB_ANALYTE
LAB_VALUE
LAB_UNIT
REFERENCE_RANGE
PROCEDURE
SURGERY
DATE
ALLERGY
```

These labels are extraction-evaluation labels, not confirmed diagnoses.

---

# 8. Text metrics

Compute by document type, language and capture quality:

```text
CER
WER
line recall
word exact match
normalized Unicode match
```

For Hindi:

- normalize Unicode carefully;
- do not erase meaningful matras/diacritics;
- track Devanagari-specific substitutions separately.

---

# 9. Critical medical-token metrics

Generic OCR accuracy is not enough.

Measure exact/normalized recall for:

```text
drug names
dose values
dose units
frequency abbreviations
lab values
lab units
reference ranges
dates
negation
```

Also report:

```text
critical numeric substitution rate
decimal-point error rate
unit substitution rate
negation inversion rate
```

---

# 10. Entity preservation score

After a fixed deterministic/controlled medical extractor runs on each OCR output, compute:

```text
precision
recall
F1
```

for each entity type.

This measures downstream usefulness while keeping the extractor identical across OCR candidates.

---

# 11. Layout metrics

For pages with annotations:

```text
region precision/recall/F1
reading-order accuracy
region-type accuracy
text-to-region assignment accuracy
```

---

# 12. Table metrics

For lab reports:

```text
table detection recall
row/column structure accuracy
cell exact match
cell position accuracy
TEDS or equivalent structural score
analyte-value-unit alignment accuracy
```

The last metric is especially important clinically.

---

# 13. Confidence / abstention metrics

For engines that provide confidence:

- reliability curve;
- error rate by confidence bucket;
- selective risk vs coverage;
- percentage of critical mistakes occurring above chosen confidence threshold.

For VLMs without equivalent calibrated confidence:

- record that limitation explicitly;
- use fallback provenance/review flags;
- compare page-level quality detector if available.

---

# 14. Reliability metrics

Measure:

```text
page failure rate
silent-empty-output rate
partial-page omission rate
worker crash rate
timeout rate
retry success rate
determinism/repeatability
batch-vs-single consistency
```

Silent omission is penalized more heavily than explicit failure.

---

# 15. Performance metrics

For each environment:

```text
cold start
p50 latency/page
p95 latency/page
pages/minute
CPU utilization
RAM
GPU utilization
VRAM
model artifact size
container image size
```

Test at least:

```text
CPU-only reference machine
single NVIDIA GPU worker (if available)
developer Windows environment where practical
```

---

# 16. Privacy/deployment metrics

Score:

```text
fully offline capable?
unexpected network calls?
remote model fetching?
runtime telemetry?
temporary file behavior?
configurable cache paths?
```

The benchmark environment should block outbound network after models are prepared.

---

# 17. Security robustness tests

Use synthetic hostile/non-sensitive files:

```text
malformed PDF
oversized dimensions
huge page count
nested/complex objects
corrupt image
incorrect extension/MIME
compressed/decompression bomb test fixture
path-like filenames
embedded external references
```

Purpose is controlled failure, not exploit development.

---

# 18. Candidate configuration matrix

Do not compare random defaults only.

## PaddleOCR

At minimum:

```text
PP-OCRv6 English/Latin path
PP-OCRv5 Devanagari
PPStructureV3
PaddleOCR-VL fallback
```

## Surya

```text
full-page OCR
layout + OCR path
table-rec path
```

## RapidOCR

```text
ONNXRuntime CPU
relevant PaddleOCR model packs
```

## Tesseract

```text
eng
hin
eng+hin where supported
```

## docTR

best stable pretrained detector/recognizer configuration.

## Docling

```text
native PDF text
OCR-auto path
RapidOCR/Tesseract path if evaluated
```

---

# 19. No-leakage rule

If candidate-specific preprocessing is tuned on the selection set, final comparison must use a held-out validation subset.

Do not repeatedly optimize against the final test pages.

---

# 20. Benchmark weighting

For SwasthyaSetu, suggested selection weighting:

| Category | Weight |
|---|---:|
| Critical medical token/entity preservation | 30% |
| Overall OCR text quality | 15% |
| Hindi + mixed-language performance | 15% |
| Handwriting performance | 15% |
| Layout/table quality | 10% |
| Reliability/failure transparency | 5% |
| Runtime/resource cost | 5% |
| Privacy/security/deployment behavior | 5% |

License/maintenance suitability is a separate hard engineering screen and can disqualify a candidate regardless of accuracy.

---

# 21. Penalty rules

Apply strong penalties for:

```text
silent page omission
invented text
dropped critical numeric tokens
decimal errors
negation inversion
wrong analyte-value pairing
wrong medication-dose pairing
```

A system that openly marks a page as failed may be safer than one that returns confident-looking incomplete text.

---

# 22. Output normalization

Every candidate must map into the same canonical benchmark schema.

Example:

```json
{
  "page": 1,
  "blocks": [
    {
      "text": "Paracetamol 500 mg",
      "bbox": [0, 0, 100, 20],
      "confidence": 0.94,
      "confidence_kind": "recognizer_probability"
    }
  ],
  "tables": [],
  "warnings": [],
  "engine": {
    "provider": "paddleocr",
    "model": "devanagari_PP-OCRv5_mobile_rec",
    "version": "..."
  }
}
```

Missing confidence must be represented as unavailable, not fabricated.

---

# 23. Reproducibility

Every run records:

```text
git commit
package versions
model versions
model checksums
container digest
hardware
driver/CUDA versions
configuration
seed where relevant
dataset manifest version
```

---

# 24. Decision output

The benchmark produces:

```text
OCR_BENCHMARK_RESULTS.md
ocr_metrics.csv
per_page_results.parquet
error_taxonomy.csv
resource_profile.csv
selected_ocr_stack.json
```

---

# 25. Selection rule

Final decision should be based on:

1. hard license/security suitability;
2. critical medical preservation;
3. Hindi/mixed language;
4. handwriting;
5. reliability;
6. operational cost.

Stars are not used in the technical benchmark score because they were already considered in the repository-screening stage.
