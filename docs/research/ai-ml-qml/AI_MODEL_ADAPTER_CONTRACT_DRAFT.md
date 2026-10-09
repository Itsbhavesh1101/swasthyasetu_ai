# SwasthyaSetu AI — AI / ML / QML Adapter & Boundary Contract Draft

**Document ID:** `SSAI-OSS-R2E-AIML-003`  
**Status:** Research-derived architecture contract draft  
**Version:** `0.1.0-research`  
**Research date:** 2026-10-09

---

# 1. Purpose

Define stable SwasthyaSetu-owned boundaries around:

```text
LLM providers
embeddings/reranking
retrieval
classical model inference
model registry/governance
explanations
QML backends
experiment tracking
```

The goal is to prevent vendor/framework types from leaking into clinical modules.

---

# 2. Package rule

Clinical/domain modules should not import:

```text
openai
google-generativeai
litellm
mlflow
onnxruntime
shap
pennylane
qiskit
langchain
llama_index
haystack
sentence_transformers
```

directly.

Imports belong in:

```text
integrations/
ml/
qml/
infrastructure/
```

according to final repository specification.

---

# Part A — LLMProvider

# 3. Contract

Conceptual:

```python
class LLMProvider(Protocol):
    async def generate_structured(
        self,
        request: StructuredLLMRequest,
    ) -> StructuredLLMResult:
        ...
```

Optional non-clinical text transformation can use another explicit method.

---

# 4. StructuredLLMRequest

```text
operation
schema_id
schema_version
system_instruction_ref
prompt_template_version
messages / normalized inputs
language
max_output_tokens
temperature/config
timeout
provider_policy
correlation_id
```

Do not include clinical routing decisions in provider policy.

---

# 5. StructuredLLMResult

```text
provider
provider_model
request_id?
schema_id
schema_version
validated_payload
usage
finish_reason
latency
attempt_count
raw_retained? = false by default
provenance
```

---

# 6. Raw response

Provider adapter may temporarily hold raw response in memory for parsing.

Default persistence:

```text
false
```

If retained for an approved evaluation workflow, send to research storage under separate policy.

---

# 7. Errors

Normalize:

```text
LLM_TIMEOUT
LLM_RATE_LIMIT
LLM_AUTH_FAILURE
LLM_PROVIDER_UNAVAILABLE
LLM_REFUSAL
LLM_SCHEMA_INVALID
LLM_CONTENT_POLICY_BLOCK
LLM_UNKNOWN
```

No provider-specific exception escapes into domain policy.

---

# 8. Retry policy

Infrastructure may retry:

```text
timeout
429
selected 5xx
schema formatting failure
```

with bounded attempts.

Application handles:

```text
clarification
abstention
fallback
```

---

# 9. Provider adapters

Potential:

```text
OpenAIProviderAdapter
GeminiProviderAdapter
BedrockProviderAdapter
LiteLLMSDKAdapter
LiteLLMGatewayAdapter
```

Only one or few are enabled per deployment.

---

# 10. Gateway neutrality

If LiteLLM Gateway is later introduced, clinical modules remain unchanged.

Only:

```text
LLMProvider configuration
```

changes.

---

# Part B — Prompt & Schema Registry

# 11. PromptTemplateRef

```text
prompt_id
version
purpose
language
status
approved_by?
content_hash
```

Prompt text should be version-controlled.

---

# 12. Schema registry

Structured extraction schema:

```text
schema_id
version
Pydantic model
JSON Schema
domain mapping
```

Provider schema is generated from the project contract, not hand-maintained separately.

---

# 13. Prompt/schema compatibility

A prompt version declares compatible schema versions.

Breaking schema change requires regression evaluation.

---

# 14. Prompt injection boundary

Patient/document text enters as data.

It never becomes:

```text
system instruction
tool permission
policy configuration
```

---

# Part C — EmbeddingProvider

# 15. Contract

```python
class EmbeddingProvider(Protocol):
    async def embed_documents(
        self, texts: Sequence[str], *, model: EmbeddingModelRef
    ) -> EmbeddingBatch:
        ...

    async def embed_queries(
        self, texts: Sequence[str], *, model: EmbeddingModelRef
    ) -> EmbeddingBatch:
        ...
```

Separate query/document methods support asymmetric models.

---

# 16. EmbeddingModelRef

```text
model_id
revision
dimension
distance_metric
normalization
license_ref
local_or_remote
```

---

# 17. EmbeddingBatch

```text
vectors
model_id
revision
dimension
normalization
created_at
```

Do not silently accept dimension mismatch.

---

# 18. SentenceTransformers adapter

Potential:

```text
SentenceTransformersEmbeddingAdapter
```

Model revision is pinned.

Default:

```text
trust_remote_code = false
```

---

# Part D — RerankerProvider

# 19. Contract

```python
class RerankerProvider(Protocol):
    async def rerank(
        self,
        query: str,
        candidates: Sequence[RetrievedCandidate],
        *,
        model: RerankerModelRef,
    ) -> Sequence[RerankedCandidate]:
        ...
```

---

# 20. Reranker provenance

Each reranked result records:

```text
retrieval_score
reranker_score
model/revision
rank_before
rank_after
```

---

# Part E — RetrievalService

# 21. Service contract

```python
class RetrievalService:
    async def retrieve(self, request: RetrievalRequest) -> RetrievalResult:
        ...
```

SwasthyaSetu owns the retrieval orchestration.

---

# 22. RetrievalRequest

```text
knowledge_base_id
query
language
top_k
filters
patient_context_scope?
required_approval_state
as_of_time?
embedding_model_ref
reranker_ref?
```

---

# 23. Hard authorization before similarity

For private patient documents:

```text
authorized document IDs
    -> vector search within authorized set
```

not:

```text
global vector search
    -> remove other patients afterward
```

---

# 24. RetrievalResult

```text
query
knowledge_base_version
embedding_model
candidates[]
retrieval_latency
rerank_latency?
```

Candidate:

```text
chunk_id
source_id
source_revision
text or controlled excerpt
score
metadata
citation/provenance
```

---

# 25. Knowledge chunk

Canonical:

```text
chunk_id
knowledge_base_id
source_id
source_revision
chunk_index
chunk_hash
language
content
content_type
approval_status
valid_from
valid_to?
embedding_model
embedding_revision
embedding
```

---

# 26. pgvector repository

Infrastructure:

```text
PgVectorKnowledgeRepository
```

Domain/RAG service does not issue raw vector SQL directly outside repository.

---

# 27. No generic agent requirement

RetrievalService has no dependency on:

```text
LangChain Agent
LlamaIndex Agent
Haystack Agent
```

A framework adapter may be added later without changing retrieval contract.

---

# Part F — ExperimentTracker

# 28. Contract

Research package may use:

```python
class ExperimentTracker(Protocol):
    def start_run(...): ...
    def log_params(...): ...
    def log_metrics(...): ...
    def log_artifact_ref(...): ...
    def finish_run(...): ...
```

---

# 29. MLflow implementation

Potential:

```text
MLflowExperimentTracker
```

Only research/training code imports MLflow.

---

# 30. Tracking-data classification

Allowed by default:

```text
dataset IDs
model IDs
metrics
hyperparameters
hashes
runtime metadata
```

Prohibited by default:

```text
raw patient records
names
full transcripts
clinical documents
ABHA
contact info
```

---

# Part G — Model Registry & Governance

# 31. ModelRegistryPort

Engineering model registry metadata can be abstracted:

```python
class ModelRegistryPort(Protocol):
    async def register_artifact(...): ...
    async def get_version(...): ...
    async def resolve_artifact(...): ...
```

---

# 32. Governance service is separate

```text
ModelRegistryPort
    = engineering artifact/version lookup

ModelGovernanceService
    = approval/lifecycle policy
```

MLflow implements the former, not the latter.

---

# 33. ModelGovernanceService

Conceptual:

```python
class ModelGovernanceService:
    def assert_inference_allowed(
        self,
        model_version: ModelVersionRef,
        use_context: ModelUseContext,
    ) -> ModelApproval:
        ...
```

Every production inference starts with or depends on a cached, validated governance decision.

---

# 34. ModelVersionRef

```text
model_id
version
artifact_sha256
model_card_version
feature_schema_version
```

---

# 35. Approval

```text
approval_id
model_version_ref
scope
state
approved_by[]
approved_at
expires/review_at?
threshold_version
calibration_version
```

---

# Part H — ModelArtifactLoader

# 36. Loader boundary

```python
class ModelArtifactLoader(Protocol):
    def load(self, approved_artifact: ApprovedModelArtifact):
        ...
```

No loader accepts arbitrary file path from HTTP request.

---

# 37. ApprovedModelArtifact

```text
artifact_uri
sha256
format
runtime
dependency_lock
model_id
version
approval_id
```

---

# 38. Load sequence

```text
resolve approved version
    -> fetch from private artifact store
    -> verify hash
    -> verify format policy
    -> verify runtime/schema
    -> load
    -> health/parity smoke test
```

---

# 39. Serialization adapters

Potential:

```text
OnnxArtifactLoader
SkopsArtifactLoader
TrustedFrameworkArtifactLoader
```

Do not create:

```text
GenericPickleLoader
```

for production.

---

# Part I — ModelInferencePort

# 40. Contract

```python
class ModelInferencePort(Protocol):
    async def predict(
        self,
        request: ModelInferenceRequest,
    ) -> ModelInferenceResult:
        ...
```

---

# 41. ModelInferenceRequest

```text
task
model_ref
feature_schema_version
features
context_ref
correlation_id
```

Avoid passing entire patient object if only 12 features are needed.

---

# 42. Pre-inference validation

Validate:

```text
feature names
types
units
ranges
missingness
schema version
model approval
```

---

# 43. ModelInferenceResult

```text
model_id
model_version
task
raw_score
probability?
calibrated_probability?
risk_band?
calibration_version
threshold_version
input_schema_version
missingness_summary
latency
explanation_ref?
provenance
```

No diagnosis field.

---

# 44. Sklearn adapter

```text
SklearnModelInferenceAdapter
```

for approved trusted scikit-learn artifacts.

---

# 45. ONNX adapter

```text
OnnxRuntimeModelInferenceAdapter
```

Startup:

```text
disable vendor telemetry
load approved artifact
verify expected inputs/outputs
run known-answer smoke test
```

---

# 46. Remote adapter

Future:

```text
RemoteModelInferenceAdapter
```

wraps BentoML/KServe/Triton etc.

Domain code remains unchanged.

---

# 47. Timeout behavior

If inference times out:

```text
ModelInferenceResult = unavailable/error
```

Clinical safety engine continues.

---

# Part J — CalibrationProvider

# 48. Calibration object

Calibration may be part of pipeline or an explicit artifact.

Canonical reference:

```text
calibration_id
model_version
method
fit_dataset_version
parameters/artifact_ref
metrics
```

---

# 49. ThresholdPolicy

```text
threshold_id
model_version
calibration_id
objective
thresholds
risk-band mapping
approval
```

Model inference service does not invent thresholds.

---

# 50. Risk band service

Apply:

```text
calibrated probability
+
approved ThresholdPolicy
```

deterministically.

---

# Part K — ExplanationProvider

# 51. Contract

```python
class ExplanationProvider(Protocol):
    async def explain(
        self,
        request: ExplanationRequest,
    ) -> ExplanationResult:
        ...
```

---

# 52. ExplanationRequest

```text
model_ref
features
prediction_ref
method
```

---

# 53. ExplanationResult

```text
method
model_id/version
baseline/reference
feature_contributions[]
generated_at
explainer_version
background_dataset_version?
```

---

# 54. Feature contribution

```text
feature_name
feature_value
unit
contribution
direction
```

UI wording is non-causal.

---

# 55. SHAP adapter

Potential:

```text
SHAPExplanationAdapter
```

Background/reference dataset is explicit configuration, not arbitrary current patient data.

---

# Part L — Quantum Backend

# 56. QuantumBackendPort

Conceptual:

```python
class QuantumBackendPort(Protocol):
    def execute(self, request: QuantumExecutionRequest) -> QuantumExecutionResult:
        ...
```

This is research infrastructure, not clinical runtime.

---

# 57. QuantumExecutionRequest

```text
framework
backend
circuit/experiment spec
shots
seed
noise spec?
transpilation config?
credentials ref?
```

---

# 58. QuantumExecutionResult

```text
backend
job_id?
shots
result
execution_time
queue_time?
resource_metrics
backend_metadata
```

---

# 59. PennyLane adapter

```text
PennyLaneQuantumBackendAdapter
```

Supports local simulator first.

Provider-specific plugins remain infrastructure choices.

---

# 60. Qiskit adapter

```text
QiskitQuantumBackendAdapter
```

Uses Qiskit primitives/backends.

---

# 61. Quantum model abstraction

Do not flatten every framework into a fake identical API if it hides meaningful experimental settings.

Shared orchestration captures common metadata while framework-specific config remains typed/versioned.

---

# Part M — QML Experiment Contract

# 62. QMLExperimentSpec

```text
experiment_id
dataset_version
split_version
preprocessing_version
feature_reduction
framework
algorithm
encoding
feature_map
ansatz
qubits
shots
optimizer
seeds
backend
noise
transpilation
metrics
```

---

# 63. Supported algorithm enum

Initially:

```text
VQC
QNN
QSVC
QUANTUM_KERNEL
CUSTOM_RESEARCH
```

Do not claim that the enum itself makes experiments equivalent.

---

# 64. QML result

```text
predictive metrics
calibration metrics
resource metrics
run-level metrics
seed distribution
circuit metrics
artifact refs
```

---

# 65. Classical comparator

Every QML experiment references:

```text
classical_baseline_run_ids[]
```

using the same split.

---

# Part N — Model Monitoring

# 66. ModelMonitoringPort

Future/pilot:

```python
class ModelMonitoringPort(Protocol):
    async def record_summary(self, summary: InferenceMonitoringSummary): ...
```

Do not send raw patient features to generic monitoring by default.

---

# 67. Monitoring summary

Could include:

```text
model/version
schema version
missingness rates
score bucket
latency
status
```

Population drift computation should occur inside an approved analytics boundary.

---

# 68. Evidently adapter

Possible future:

```text
EvidentlyMonitoringAdapter
```

not part of MVP.

---

# Part O — Model Download / External Registry

# 69. ExternalModelSourcePort

If Hugging Face or another hub is used during research:

```python
class ExternalModelSourcePort(Protocol):
    def resolve_pinned_artifact(...): ...
```

---

# 70. No floating runtime download

Production runtime should not:

```text
download model "latest" from the internet at startup
```

Preferred:

```text
approved artifact copied into private immutable store during release/promotion
```

---

# 71. External model manifest

```text
source_repository
revision
license
hash
remote_code_required
review_id
```

---

# Part P — LLM Evaluation Interface

# 72. Evaluation case

```text
case_id
category
language
input
expected_structured_output
allowed_variants
forbidden_behavior
safety_tags
```

---

# 73. Evaluation runner

Primary:

```text
pytest-based SwasthyaSetu runner
```

Optional:

```text
Promptfoo export/adapter
```

---

# 74. LLM evaluation result

```text
provider
model
prompt version
schema version
case ID
schema pass
field metrics
forbidden behavior
latency
cost
```

---

# 75. No LLM judge for deterministic assertions

Examples:

```text
route must equal C
provider phone must equal registry record
self-care must be blocked
```

Use exact deterministic assertions.

---

# Part Q — Security & Privacy

# 76. AI credential scope

Different integrations use separate credentials:

```text
LLM provider
embedding provider
model hub
MLflow
QPU
```

Do not share one global "AI_API_KEY".

---

# 77. Egress

Production adapter egress is allowlisted where practical.

Model loaders should not fetch arbitrary URLs supplied by patients.

---

# 78. LLM endpoint validation

Custom LLM endpoint configuration is admin/deployment configuration.

Patients cannot choose:

```text
base_url
proxy
headers
credentials
```

---

# 79. Research worker isolation

QML/ML training workers:

```text
no clinical production credentials
approved research datasets only
separate artifact path
resource limits
```

---

# 80. GPU worker isolation

If CUDA/GPU server is later introduced, place behind private service interface.

No public unauthenticated Triton/BentoML/vLLM endpoint.

---

# 81. Prompt/version secrets

Prompt templates may contain internal logic but not long-lived secret values.

Secrets remain SecretProvider references.

---

# Part R — Failure Semantics

# 82. LLM unavailable

Fallback:

```text
guided structured form / manual input
existing deterministic safety controls
```

Do not fabricate extraction.

---

# 83. Embedding service unavailable

Fallback:

```text
structured/filter search
keyword fallback where implemented
manual navigation
```

Safety policy remains available.

---

# 84. MLflow unavailable

Training experiment logging may fail/degrade according to research workflow.

Patient application should not depend on MLflow availability.

---

# 85. Risk model unavailable

Return:

```text
risk_assessment.status = UNAVAILABLE
```

Do not alter urgent safety route.

---

# 86. QML unavailable

No impact to patient product path.

Research job fails/queues only.

---

# Part S — Dependency Direction

# 87. Allowed

```text
clinical/application
    -> AI/ML ports/contracts

integrations/ml/qml
    -> external libraries
```

---

# 88. Forbidden

```text
clinical safety policy
    -> qiskit.VQC

patient module
    -> mlflow

referral module
    -> langchain

clinical intake
    -> onnxruntime.InferenceSession
```

---

# Part T — Initial Implementations

# 89. Before production providers

Implement/test:

```text
FakeLLMProvider
DeterministicFixtureLLMProvider
Local/MockEmbeddingProvider
PgVectorKnowledgeRepository
InlineModelInferenceAdapter for test model
FakeExperimentTracker
FakeQuantumBackend
```

These enable deterministic test suites.

---

# 90. Research profile

Then add:

```text
MLflowExperimentTracker
Optuna studies
SHAP explanation
PennyLane simulator
Qiskit simulator
SentenceTransformers embedding
```

---

# 91. Production profile

Only after approval:

```text
real LLM provider
approved model inference adapter
approved embedding model
private artifact store
governance service
```

---

# Part U — Adapter Definition of Done

# 92. LLM adapter

```text
[ ] timeout
[ ] retries
[ ] structured schema validation
[ ] normalized errors
[ ] model identity
[ ] usage metadata
[ ] no raw telemetry by default
[ ] prompt-injection tests
[ ] provider outage tests
```

---

# 93. Model inference adapter

```text
[ ] approval check
[ ] artifact hash
[ ] schema validation
[ ] known-answer test
[ ] parity test where converted
[ ] timeout
[ ] no unsafe model loading
[ ] provenance
```

---

# 94. Embedding adapter

```text
[ ] pinned revision
[ ] license reviewed
[ ] dimension verified
[ ] multilingual benchmark
[ ] batch behavior
[ ] no runtime remote code
```

---

# 95. Quantum backend adapter

```text
[ ] framework/version logged
[ ] backend logged
[ ] shots/seed logged
[ ] resource metrics
[ ] reproducibility
[ ] no clinical runtime dependency
```

---

# 96. MLflow adapter

```text
[ ] separate DB/storage
[ ] auth/network controls
[ ] PHI-safe logging
[ ] immutable artifact refs
[ ] registry IDs linked to governance
[ ] backup
```

---

# Part V — Final Boundary Principle

# 97. SwasthyaSetu owns

```text
clinical domain
safety
consent
provenance
model governance
threshold approval
patient-facing interpretation
resource authorization
```

Third-party AI frameworks implement bounded technical capabilities beneath these rules.

That boundary is what allows the project to evolve without a future AI framework rewriting the healthcare product.
