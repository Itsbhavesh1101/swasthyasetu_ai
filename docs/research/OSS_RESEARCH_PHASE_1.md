# SwasthyaSetu AI — OSS Research Phase 1

**Document ID:** SSAI-OSS-R1-003  
**Status:** Research in progress  
**Research baseline:** 2026-10-09

## What this pass did

The first pass inspected more than project descriptions. For priority candidates it examined combinations of source/package manifests, repository structure, tests/configuration, releases, issues/PR activity, security posture and licensing.

The current results are an engineering shortlist, not final production approval.

## Highest-confidence candidates

### PaddleOCR
Best current starting point for SwasthyaSetu document intelligence. It has a mature Python package, test configuration, permissive source license, frequent development, multilingual OCR and document-parsing capabilities. Use only through `OCRPort`.

**Next:** benchmark prescriptions, labs and discharge summaries, especially handwriting and Hindi/English/code-mixed documents.

### HAPI FHIR
Best current dedicated FHIR-engine fit. Its multi-module architecture includes client/server, JPA persistence, validation and several FHIR versions. Deploy as an interoperability sidecar behind `FHIRProvider`, not as SwasthyaSetu's internal domain.

**Next:** run a hardened JPA-server spike and validate our canonical mappings.

### IndicTrans2
Extremely strong requirement fit for Indian-language translation. Its importance is much greater than its raw star count because it directly covers SwasthyaSetu's localization requirement.

**Next:** build a containerized `TranslationPort` spike and evaluate medical negation/entity preservation.

### IndicConformer + faster-whisper
Do not choose based on stars. IndicConformer has the strongest India-language specialization but weaker repository/deployment maturity. faster-whisper has a more mature engineering/deployment package.

**Next:** compare both on the same Hindi/Hinglish/noisy-OPD test corpus.

### LiteLLM
Strong implementation candidate inside our provider-neutral AI gateway. SwasthyaSetu still owns the `LLMProvider` contract; no domain module imports LiteLLM directly.

**Next:** structured-output/failover/privacy spike with a tightly pinned version.

### pgvector
Architecturally clean choice if/when RAG is actually justified, because PostgreSQL is already the source-of-truth database.

**Next:** defer installation until a concrete retrieval requirement exists.

### MLflow
Strong choice for experiment tracking/model registry for both classical and QML research.

**Next:** adopt in research environment only; no automatic model promotion to patient workflows.

### PennyLane + Qiskit Machine Learning
These are complementary rather than mutually exclusive. PennyLane is a strong primary hybrid-QML abstraction, while Qiskit Machine Learning provides direct VQC/QNN/quantum-kernel tooling and IBM/Qiskit interoperability.

**Next:** implement the same small benchmark in both after the classical baseline is frozen.

## Strong projects that should not become our core

### Medplum
Excellent FHIR-native platform, but it already includes a broad server/application ecosystem. Using it as the core would duplicate or replace parts of our intentional FastAPI modular architecture. Keep it as a serious FHIR-platform alternative/reference.

### OpenMRS and OpenEMR
Both are valuable mature EHRs. They are better treated as integration targets/reference implementations than as the foundation for SwasthyaSetu.

## Important caution

### Surya
Technically attractive OCR/layout candidate, but code and pretrained model licensing are separate concerns. It remains a benchmark candidate until model-license suitability and SwasthyaSetu medical-document performance are verified.

## Next research batches

1. **OCR benchmark design:** PaddleOCR vs Surya vs docTR.
2. **Indian language:** IndicConformer vs faster-whisper; IndicTrans2; TTS/Bhashini path.
3. **FHIR:** HAPI FHIR JPA starter vs Medplum deployment/security trade-off.
4. **Infrastructure:** Keycloak vs Authentik; object storage; jobs/queues.
5. **AI/ML:** LiteLLM, MLflow, PennyLane and Qiskit integration spikes.

The final criterion is not "most stars." It is the most maintainable, secure, license-compatible, replaceable component that demonstrably satisfies SwasthyaSetu's workload.
