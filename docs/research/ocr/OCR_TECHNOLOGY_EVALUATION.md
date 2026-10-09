# SwasthyaSetu AI — OCR & Document Intelligence Technology Evaluation

**Document ID:** `SSAI-OSS-R2A-OCR-001`  
**Status:** Deep research / pre-benchmark decision  
**Review date:** 2026-10-09  
**Scope:** OCR, document parsing, layout, tables, handwriting, Indian-language support, medical-record ingestion.

---

## 1. Executive conclusion

The current best architecture is **not one OCR repository doing everything**.

The strongest design for SwasthyaSetu is:

```text
SwasthyaSetu Documents Module
        |
        +-- DocumentParserPort
        |      `-- Docling adapter (candidate for native PDFs / Office / structural parsing)
        |
        +-- OCRPort
        |      +-- PaddleOCR adapter         <-- primary candidate
        |      +-- RapidOCR adapter          <-- optional CPU/edge candidate
        |      `-- Tesseract adapter         <-- baseline / fallback
        |
        +-- VLMDocumentParserPort
               +-- PaddleOCR-VL adapter      <-- preferred hard-page fallback candidate
               `-- Surya adapter             <-- benchmark competitor, license constrained
```

**Current primary recommendation:** PaddleOCR behind a dedicated worker/service adapter.

**Important refinement:** use Docling as a *document normalization/parser candidate*, not as SwasthyaSetu's medical OCR authority and not as the domain model.

No OCR engine may directly create confirmed clinical facts. OCR outputs remain candidate evidence with provenance and verification state.

---

## 2. SwasthyaSetu requirements being evaluated

The OCR stack must support the SIH-derived document workflow:

- prior prescriptions;
- laboratory reports;
- discharge summaries;
- diagnostic/other medical records;
- scanned and photographed documents;
- printed and handwritten text;
- multilingual documents;
- Hindi/Devanagari and English;
- mixed Hindi-English pages;
- medication name/dose/frequency preservation;
- diagnoses/problems;
- lab analyte/value/unit/reference-range preservation;
- procedures/surgeries/dates;
- table/layout preservation;
- chronological downstream timeline construction;
- low-confidence review;
- source/provenance links;
- no autonomous diagnosis.

The OCR layer itself should output text/layout evidence. Medical entity interpretation belongs to a separate extraction layer.

---

## 3. Research method

The review inspected, where available:

- repository architecture and source paths;
- package manifests;
- model/runtime dependencies;
- tests and test configuration;
- release cadence;
- current issues;
- security policy/advisories;
- source and model licenses;
- multilingual/Devanagari implementation;
- handwriting claims/issues;
- deployment model;
- integration surface.

Reviewed default-branch snapshots included:

```text
PaddleOCR  commit family observed: dab3fe353790...
Surya      commit family observed: a2363d331177...
docTR      commit family observed: 434145cdd7dc...
Docling    commit family observed: 0e1567bbb8a5...
```

Exact production adoption must pin a released version/tag, not a moving branch.

---

## 4. Pre-benchmark engineering score

Weights come from `OSS_RESEARCH_METHODOLOGY.md`. Scores are engineering-screening values, not clinical accuracy scores.

| Candidate | Weighted screening score |
|---|---:|
| Docling | 9.10/10 |
| PaddleOCR | 8.80/10 |
| Tesseract | 7.95/10 |
| RapidOCR | 7.78/10 |
| Surya | 7.48/10 |
| docTR | 7.33/10 |

Do **not** interpret this as a direct accuracy leaderboard: Docling is primarily a document-processing framework; Tesseract is a baseline; PaddleOCR/Surya/docTR are closer OCR competitors.

---

# 5. PaddleOCR — primary OCR candidate

## 5.1 Repository maturity

Observed characteristics:

- roughly 90k GitHub stars and 11k+ forks at review time;
- very active 2026 release cadence;
- current package version line around 3.7.x;
- Apache-2.0 source license;
- Python package, CLI, deployment code, configs, tests, docs and multiple inference modes;
- official model ecosystem and model cards.

This is materially different from a paper-demo repository.

## 5.2 Current source architecture

The current `PaddleOCR` class is a wrapper over a PaddleX pipeline rather than a completely independent OCR implementation.

Important source behavior:

```text
PaddleOCR
  -> PaddleXPipelineWrapper
  -> pipeline name "OCR"
  -> document preprocessor
  -> text detection
  -> text-line orientation
  -> text recognition
```

The package manifest currently depends on a bounded PaddleX range (`paddlex[ocr-core]`).

### Consequence for SwasthyaSetu

Do **not** install the OCR stack indiscriminately into the main FastAPI environment.

Prefer:

```text
documents module
  -> OCRPort
      -> isolated PaddleOCR worker image/process
```

Benefits:

- isolates heavy native/ML dependencies;
- simplifies version pinning;
- keeps FastAPI dependency graph stable;
- makes replacement easier;
- permits GPU/CPU worker variants;
- limits crash/resource impact.

## 5.3 Document-structure capability

`PPStructureV3` exposes configuration for:

- layout detection;
- document orientation;
- document unwarping;
- text detection/recognition;
- table classification;
- wired/wireless table structure;
- table cell detection;
- seal recognition;
- formula recognition;
- chart recognition;
- region detection.

This is highly aligned with lab reports, discharge summaries and structured medical pages.

### Important version nuance

The reviewed `PPStructureV3` source currently lists supported OCR versions through **PP-OCRv5**, while the general `PaddleOCR` wrapper supports **PP-OCRv6**.

That means we should not assume "latest OCR version" applies uniformly across every document-structure pipeline.

## 5.4 Hindi / Devanagari support

This is one of PaddleOCR's strongest advantages for SwasthyaSetu.

The repository has:

- explicit `DEVANAGARI_LANGS`;
- Hindi (`hi`) language routing;
- a dedicated `devanagari_PP-OCRv5_mobile_rec` model;
- training/config files for Devanagari;
- model documentation listing Hindi, Marathi, Nepali, Bihari, Maithili, Bhojpuri, Sanskrit and other Devanagari languages;
- official Devanagari model card.

The Devanagari recognizer also lists **English** in its supported-language set, which is promising for Indian medical records containing English medication names alongside Hindi.

## 5.5 Mixed Hindi-English caveat

A 2026 PaddleOCR discussion specifically requests better automatic mixed-language handling within the same PDF/page and notes the current single-language initialization behavior.

Therefore:

**Do not assume mixed Hindi-English performance from the language list alone.**

This becomes a mandatory benchmark stratum.

Potential routing strategies to test:

1. Devanagari model for mixed pages because it includes English;
2. page-level language/script routing;
3. region-level script routing;
4. PaddleOCR-VL fallback on mixed pages;
5. dual-pass reconciliation only when confidence/quality is poor.

## 5.6 Handwriting

Current PaddleOCR materials state that PaddleOCR-VL handles challenging content including handwritten text and supports Hindi/Devanagari.

The classic line recognizer should still be treated differently from the VLM parser.

Recommended strategy:

```text
printed / clean page
    -> classical PaddleOCR / PPStructure

hard handwriting / irregular document
    -> PaddleOCR-VL fallback
    -> mark source_type = DOCUMENT_AI / VLM-derived
    -> require review for low-confidence/critical fields
```

Do not replace confidence-bearing conventional OCR with VLM-only parsing for every page.

## 5.7 PaddleOCR-VL

Advantages:

- official model card currently Apache-2.0;
- multilingual;
- document layout/text/table/formula/chart parsing;
- 0.9B-class model family;
- handwritten/historical-document claims;
- JSON/Markdown-oriented structured output.

Risks:

- VLM generation can produce omission/substitution behavior unlike conventional OCR;
- confidence semantics may not be equivalent to detector/recognizer confidence;
- heavier model/runtime;
- downstream facts still require provenance and validation.

### Recommendation

Use as **selective fallback/escalation**, not automatic clinical truth.

## 5.8 Security posture

The GitHub repository did not expose a dedicated `SECURITY.md` in the reviewed snapshot.

This does not imply the project is insecure, but it reduces our security-governance score.

Mitigations:

- pin exact versions;
- scan container/dependencies;
- run untrusted parsing in isolated worker;
- no network egress unless model download/update is explicitly enabled;
- enforce file/page/time/memory limits;
- maintain our own vulnerability review process.

## 5.9 Preliminary decision

**ADOPT BEHIND ADAPTER — subject to benchmark.**

---

# 6. Surya — high-quality benchmark competitor, not current default

## 6.1 Maturity

Observed:

- ~21k stars;
- 1k+ commits;
- active 2026 releases;
- tests and modern package configuration;
- OCR, layout, reading order and table recognition;
- 90+ language positioning.

## 6.2 Architecture

Surya 2 uses:

```text
SuryaInferenceManager
      |
      +-- RecognitionPredictor
      +-- LayoutPredictor
      `-- TableRecPredictor
```

OCR/layout/table recognition share a ~650M vision-language model.

Inference is served through:

- vLLM on NVIDIA GPU; or
- llama.cpp on CPU / Apple Silicon.

A separate lightweight text-detection model remains.

This is a coherent architecture and is easy to place behind our adapter.

## 6.3 Strengths

- full-page OCR;
- layout;
- tables;
- reading order;
- handwritten examples;
- multilingual scope;
- modern local inference options.

## 6.4 Weaknesses relevant to healthcare

Repository issue evidence shows:

- a user reported unsatisfactory handwritten fine-tuning results;
- a 2026 bug reports text inside `Diagram` regions being skipped by the normal full-page path despite lower-level detection/recognition seeing the text;
- custom fine-tuning has had breaking/runtime issues;
- language-control behavior has changed across versions.

These are not reasons to dismiss Surya, but they reinforce our "benchmark, don't trust marketing" approach.

## 6.5 License concern

Surya source code is Apache-2.0, **but model weights use a modified AI/OpenRAIL-style license with commercial conditions**.

This is a major distinction from PaddleOCR's official Apache-licensed models.

For an academic prototype it may be usable, but architecture should not depend on a model whose future commercial deployment may need additional licensing.

## 6.6 Decision

**BENCHMARK BEFORE ADOPTION.**

Use Surya as a serious competitor for:

- handwriting;
- layout;
- full-page OCR;
- structured tables.

Do not make it the default production dependency until model-license and benchmark questions are resolved.

---

# 7. docTR — excellent engineering library, weaker requirement fit

## 7.1 Maturity

Observed:

- ~6.3k stars;
- 1k+ commits;
- active 2026 releases;
- Apache-2.0;
- dedicated package, API, scripts, docs and tests;
- PyTorch OCR pipeline with detection + recognition abstractions.

## 7.2 Source architecture

The public `ocr_predictor(...)` cleanly composes detection and recognition architectures.

This makes docTR attractive for:

- experimentation;
- custom training;
- printed OCR;
- lightweight model research;
- clean adapter design.

## 7.3 Why it is not the primary SwasthyaSetu choice

Two long-running open feature areas matter directly:

- multilingual pretrained-model support;
- handwritten-text support.

The project has a Devanagari vocabulary definition, but a vocabulary definition is not equivalent to a strong pretrained Hindi/handwriting model.

For SwasthyaSetu, multilingual Indian medical documents are core rather than optional.

## 7.4 Security posture

No dedicated GitHub security policy was detected in the reviewed state.

## 7.5 Decision

**CONSIDER / benchmark baseline**, especially for clean printed text or custom-model research.

Not current primary OCR.

---

# 8. Docling — strong complementary document parser

## 8.1 Why it matters

Docling is not merely an OCR model.

It is a high-level document conversion and structure pipeline with:

- PDF/document backends;
- layout;
- tables;
- OCR engine abstraction;
- threaded processing;
- structured document representation;
- Office/document conversion;
- numerous tests;
- active releases.

At review time the main project had ~68k stars.

## 8.2 Architecture fit

The current pipeline code explicitly separates OCR options/engines and supports several OCR backends such as:

- EasyOCR;
- Tesseract;
- RapidOCR;
- other optional engines.

It also exposes PDF-aware vs full-page OCR modes and language mapping.

This is conceptually close to what our `DocumentParserPort` needs.

## 8.3 Why it should not replace our documents module

SwasthyaSetu still needs to own:

- upload state;
- medical-document classification;
- object-storage metadata;
- provenance;
- patient/encounter association;
- clinical candidate facts;
- review workflow;
- retention;
- authorization.

Docling can normalize documents; it should not own our clinical domain.

## 8.4 Security findings

Docling has a formal security policy and active vulnerability handling.

It also published several 2026 advisories involving hostile document/path/archive handling.

This is actually useful evidence: document parsing is a high-risk attack surface.

### Architecture consequence

Whether we choose Docling or not, **all untrusted document parsing should run in a constrained worker sandbox**:

- no broad filesystem access;
- bounded temp directory;
- network disabled by default;
- CPU/memory/time/page limits;
- file-type allowlist;
- archive recursion limits;
- updated dependencies;
- no automatic remote URL fetching from uploaded content.

## 8.5 Decision

**ADOPT/CONSIDER as `DocumentParserPort` implementation**, pending a small integration spike.

It is complementary to PaddleOCR, not necessarily a competitor.

---

# 9. RapidOCR — important edge/kiosk candidate

## 9.1 Maturity

Observed:

- ~8k stars;
- 1.5k+ commits;
- active 2026 development;
- Apache-2.0;
- ONNX Runtime/OpenVINO/MNN/Paddle/TensorRT/PyTorch backends;
- Docker variants;
- cross-platform focus.

## 9.2 Why it is interesting

RapidOCR converts/deploys PaddleOCR-family models into more portable inference runtimes.

This may be valuable for:

- CPU-only kiosk;
- Windows deployment;
- low-resource workers;
- future edge/offline mode.

Docling's current OCR configuration also integrates RapidOCR.

## 9.3 Caveat

A 2026 issue tracks license/notices for bundled ONNX models. The project now documents upstream model licensing, but we should still pin model hashes and retain model-attribution metadata.

PP-OCRv6 support was also still an active discussion around its release.

## 9.4 Decision

**BENCHMARK as CPU/edge adapter**, not primary server OCR until our tests prove parity.

---

# 10. Tesseract — baseline and emergency fallback

Observed:

- ~76k stars;
- long-lived C++ project;
- Apache-2.0;
- current 5.5.x release line;
- broad language ecosystem.

Strengths:

- mature;
- offline;
- CPU-friendly;
- deterministic;
- easy to sandbox;
- useful for clean printed documents.

Weaknesses:

- no modern document intelligence;
- weak fit for complex handwriting;
- layout/table extraction requires surrounding logic;
- not a strong primary choice for medical prescriptions.

**Decision:** retain as benchmark/fallback, not primary OCR.

---

# 11. Why stars do not decide this

If stars decided:

```text
Tesseract / Docling
```

could appear "better" than every specialist solution.

But SwasthyaSetu needs:

- medical handwriting;
- Devanagari;
- English-Hindi mixing;
- table structure;
- mobile-photo robustness;
- provenance;
- confidence/abstention;
- safe deployability.

Therefore stars are only one signal.

---

# 12. Recommended processing architecture

```text
Upload
  |
  v
File Security Validation
  |
  +-- MIME/signature validation
  +-- size/page limits
  +-- checksum / duplicate check
  +-- malware/content policy
  |
  v
Document Type Probe
  |
  +-- born-digital PDF / Office
  |       |
  |       v
  |   DocumentParserPort
  |       `-- Docling candidate
  |
  +-- scanned PDF / image / poor native text
          |
          v
       OCR Routing
          |
          +-- English/Latin -> PaddleOCR conventional
          +-- Hindi/Devanagari -> PP-OCRv5 Devanagari
          +-- Mixed Hindi-English -> benchmarked policy
          +-- table-heavy -> PPStructureV3
          +-- hard handwriting/irregular -> PaddleOCR-VL fallback
          +-- edge CPU -> RapidOCR candidate
          |
          v
Canonical DocumentParseResult
          |
          v
Medical Document Classifier / Entity Extractor
          |
          v
Candidate Clinical Facts
          |
          v
Provenance + Confidence + Human Review
```

---

# 13. Critical architectural separation

Do **not** combine these into one interface:

```text
OCR
medical entity extraction
clinical fact confirmation
```

They have different trust levels.

Correct separation:

```text
OCRPort
  -> evidence

MedicalDocumentExtractor
  -> candidate structured facts

ClinicalFactReview
  -> confirmed/rejected/superseded facts
```

---

# 14. Proposed OCR routing modes

```text
TEXT_ONLY
LAYOUT
TABLE_AWARE
HANDWRITING_FALLBACK
NATIVE_DOCUMENT
```

Routing should be configuration/policy driven and observable.

Every result records:

- provider;
- model;
- model version;
- runtime/backend;
- language hint;
- processing mode;
- confidence availability;
- fallback reason;
- warnings.

---

# 15. Mixed Hindi-English strategy to benchmark

Candidate strategy A:

```text
devanagari_PP-OCRv5
```

because the model explicitly includes English.

Candidate strategy B:

```text
page/region script classifier
 -> Devanagari recognizer
 -> English recognizer
```

Candidate strategy C:

```text
PaddleOCR-VL multilingual fallback
```

Candidate strategy D:

```text
dual pass
 -> confidence/consensus reconciliation
```

Do not implement D by default unless the benchmark shows meaningful gain because it doubles cost and increases reconciliation complexity.

---

# 16. Medical-specific risks that general OCR benchmarks miss

A visually "good" OCR output can still be clinically dangerous if it changes:

```text
5 mg  -> 50 mg
0.5   -> 5
no fever -> fever
Na+ 135 -> 185
OD -> BD
once daily -> twice daily
```

Therefore our benchmark must separately score:

- numerals;
- decimals;
- units;
- medication names;
- dose/frequency;
- negation;
- reference ranges;
- dates.

Generic CER/WER alone is insufficient.

---

# 17. Security design required regardless of engine

Untrusted medical files must not be parsed in the main web process.

Worker hardening:

```text
non-root container
read-only root filesystem where feasible
bounded /tmp
no host mounts
network egress off by default
CPU/memory limits
document page limit
pixel/decompression limit
timeout
file-type allowlist
library version pinning
SBOM / dependency scan
temporary artifact cleanup
```

---

# 18. Model artifact governance

Store model metadata:

```text
provider
model_name
model_version
source
license
artifact_checksum
downloaded_at
approved_status
benchmark_run_id
```

Do not silently download a different model into production.

---

# 19. Preliminary selection

## Default server path

```text
PaddleOCR 3.7.x family
 + PP-OCRv5 Devanagari where required
 + PPStructureV3 for structured pages
```

## Hard-document fallback candidate

```text
PaddleOCR-VL
```

## Native document normalization

```text
Docling
```

## Benchmark challengers

```text
Surya
docTR
Tesseract
RapidOCR
```

---

# 20. Decision still pending

The primary stack is **not final** until the benchmark in `OCR_BENCHMARK_PLAN.md` is run.

The most important unresolved question is:

> Which pipeline preserves critical medical entities most reliably on handwritten and mixed English-Hindi Indian records while still failing transparently enough for safe human review?

That cannot be answered from GitHub stars, README benchmarks, or generic OCR leaderboards.
