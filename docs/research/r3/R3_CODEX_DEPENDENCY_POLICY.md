# SwasthyaSetu AI — R3 Codex Dependency & Technology Policy

**Document ID:** `SSAI-R3-CODEX-001`  
**Status:** Mandatory for implementation prompts that add dependencies or infrastructure  
**Version:** `1.0.0-r3`  
**Date:** 2026-10-10

---

# 1. Why this file exists

Codex must not interpret the research repository as a shopping list.

R2 evaluated many candidates. R3 decides when each one may be implemented.

The default rule is:

> A researched technology is not an implementation dependency until the current phase explicitly activates it.

---

# 2. Required read order

Before any prompt that changes dependencies, deployment, AI providers, model runtimes, storage or interoperability, Codex must read:

```text
00_PROJECT_MASTER_SPEC.md
01_PRODUCT_REQUIREMENTS.md
02_SYSTEM_ARCHITECTURE.md
29_ENGINEERING_STANDARDS.md
34_MASTER_IMPLEMENTATION_PLAN.md
36_DEPENDENCY_MAP.md
37_DECISION_LOG.md
R3_FINAL_TECHNOLOGY_STACK.md
this file
current phase/module spec
```

Safety/policy specifications outrank implementation convenience.

---

# 3. Dependency classes

Every new dependency must be assigned exactly one implementation class:

```text
CORE_RUNTIME
FEATURE_RUNTIME
INTEGRATION_RUNTIME
RESEARCH_ONLY
DEV_TEST_ONLY
OPS_ONLY
FUTURE_NOT_ALLOWED
REJECTED_DEFAULT
```

---

# 4. CORE_RUNTIME

May be added during foundation when required:

```text
FastAPI
Pydantic v2
SQLAlchemy 2.x
Alembic
PostgreSQL driver
httpx-style async HTTP client
structured logging dependencies
OpenTelemetry API/SDK when observability phase activates
```

Frontend:

```text
Next.js
React
TypeScript
Tailwind
```

Do not add unrelated AI packages to core runtime.

---

# 5. FEATURE_RUNTIME

Allowed only when the relevant feature phase begins.

Examples:

```text
pgvector          -> RAG/retrieval phase
OCR package       -> document AI phase
ASR package       -> multilingual speech phase
translation model -> multilingual phase
```

The phase prompt must name the package or explicitly authorize the benchmark spike.

---

# 6. INTEGRATION_RUNTIME

External infrastructure/service clients belong here:

```text
OIDC/Keycloak client
HAPI FHIR sidecar client
ABDM adapter
object-storage SDK
notification provider SDK
```

They must sit behind a project-owned port.

No provider SDK import in domain modules.

---

# 7. RESEARCH_ONLY

Must live outside normal patient API dependency closure:

```text
MLflow
Optuna
SHAP training stack where not needed for online inference
PennyLane
Qiskit
Qiskit Machine Learning
experimental dataset tooling
Promptfoo
```

A research dependency must not be imported from clinical/safety modules.

---

# 8. DEV_TEST_ONLY

Examples:

```text
pytest
pytest-asyncio
Ruff
mypy/pyright
test factories
security test utilities
```

---

# 9. OPS_ONLY

Examples:

```text
Trivy
Gitleaks
Prometheus deployment
Grafana deployment
OTel Collector
OpenBao
```

They are not Python application imports unless an adapter specifically requires a client.

---

# 10. FUTURE_NOT_ALLOWED

Do not add without an explicit architecture-change prompt:

```text
Kubernetes
KServe
Triton
vLLM
NATS
Kafka
RabbitMQ
service mesh
LangChain core platform
LlamaIndex core platform
Haystack general pipeline runtime
LiteLLM Proxy
```

A future spike prompt may temporarily evaluate one.

---

# 11. REJECTED_DEFAULT

Do not choose as the new standard implementation:

```text
MinIO
arbitrary pickle/joblib/dill/cloudpickle model upload
```

Integration with an institution's existing system is a separate decision.

---

# 12. AI Gateway rule

Codex must implement the project-owned AI orchestration layer first.

Do not interpret:

```text
AI Gateway
```

as permission to deploy LiteLLM Proxy.

Default:

```text
Task service
 -> LLMProvider
 -> direct provider adapter
```

---

# 13. LLM provider rule

Do not hard-code one vendor across the domain.

Do not choose the production LLM provider unless the phase prompt names it.

A mock/fake provider should be available for deterministic tests.

---

# 14. OCR rule

Codex may:

```text
create OCRPort
create MockOCRAdapter
create benchmark harness
create PaddleOCR adapter during approved document phase/spike
```

Codex may not:

```text
declare PaddleOCR clinically/production approved
delete benchmark challengers from plan
hard-wire document domain to PaddleOCR types
```

---

# 15. Speech rule

Codex may scaffold all ports.

Real model adapters require the language phase/spike.

Do not install every ASR/TTS model in the default application environment.

---

# 16. FHIR rule

Internal domain remains authoritative.

HAPI is a sidecar/integration.

Codex must not:

```text
rewrite Patient/Encounter domain to be HAPI entities
make HAPI DB the canonical app DB
expose HAPI starter defaults to public network
```

---

# 17. RAG rule

Default:

```text
project-owned RetrievalService
pgvector
EmbeddingProvider
optional RerankerProvider
```

Do not add LangChain/LlamaIndex "because RAG."

If complex RAG orchestration later justifies a framework, that requires a new phase decision.

---

# 18. Model governance rule

MLflow state is not SwasthyaSetu approval.

Before online model inference:

```text
approved model version
artifact hash
feature schema
calibration version
threshold version
approval scope
```

must be resolvable.

---

# 19. Model serialization rule

Codex must never create a generic production endpoint like:

```text
POST /models/upload
```

that accepts arbitrary executable Python model files.

Production loader reads only approved artifacts from private trusted storage.

---

# 20. ONNX rule

If ONNX is introduced:

```text
native-vs-ONNX parity test
known-answer test
input/output signature validation
telemetry-disable configuration
```

are mandatory.

---

# 21. QML rule

QML may be implemented only in research packages/workflows until a later explicit deployment decision.

No patient request route should import Qiskit/PennyLane.

---

# 22. Queue rule

Do not add Redis/Valkey merely because background jobs exist.

Sequence:

```text
in-process test/local abstraction
PostgreSQL-native durable queue spike
fallback only if requirements demand
```

---

# 23. Cache rule

Adding a cache requires a named use case and degraded-mode test.

If deletion of cache content breaks clinical correctness, the design is invalid.

---

# 24. Object storage rule

Implement `ObjectStoragePort` before concrete storage.

Local development can use filesystem.

SeaweedFS activation requires its phase/spike.

---

# 25. Identity rule

Do not install Keycloak during unrelated foundation work.

Pseudonymous sessions are implemented independently.

OIDC/Keycloak appears when authenticated identity is the active phase.

---

# 26. Secrets rule

Do not require OpenBao in local development.

Use secret abstraction/config first.

Activate dedicated secret manager for protected deployment when specified.

---

# 27. Default Docker Compose rule

Early default Compose should remain small.

Do not automatically add:

```text
keycloak
seaweedfs
valkey
openbao
mlflow
prometheus
grafana
hapi-fhir
paddleocr
vllm
```

A phase-specific Compose override/profile can add required services.

---

# 28. Dependency placement rule

A dependency must be installed in the narrowest valid environment/profile.

Example:

```text
Qiskit -> qml-research
MLflow -> ml-research
PaddleOCR -> document worker image/profile
HAPI -> separate Java sidecar
Next.js -> frontend workspace
```

Do not solve dependency conflicts by putting everything into one Python virtual environment.

---

# 29. License rule

Before a new production dependency:

```text
record upstream repository
record license
check model/data license separately
record exact version/revision
```

"Open-source framework" does not imply "all associated model weights are equally licensed."

---

# 30. Security rule

Before enabling remote code or executable artifacts:

```text
stop
document reason
security review
pin exact revision
sandbox/allowlist
```

Default `trust_remote_code` for downloaded ML models is false.

---

# 31. Telemetry rule

External framework telemetry must be reviewed.

Generic telemetry must not contain:

```text
patient names
ABHA
full transcripts
raw medical document text
raw prompts/responses
```

unless a specific approved data-flow says otherwise.

---

# 32. Benchmark-gated provider rule

For OCR/ASR/TTS/embeddings and similar candidates:

Codex must distinguish:

```text
implemented adapter
benchmark winner
production approval
```

These are three different states.

An adapter existing in code does not mean it is selected.

---

# 33. Package-addition report

Whenever Codex adds a dependency, final implementation report must state:

```text
dependency
version/range
R3 classification
why needed
where imported
license
security notes
runtime profile
tests added
failure behavior
```

---

# 34. Service-addition report

Whenever Codex adds infrastructure:

```text
service
phase
port/capability
persistent data?
network exposure?
secrets?
health check?
backup?
failure behavior?
local/pilot/prod profile?
```

---

# 35. No silent architecture upgrade

Codex must not "improve" architecture by adding:

```text
microservices
message broker
Kubernetes
agent framework
gateway
vector DB outside PostgreSQL
new auth platform
```

without explicit instruction.

---

# 36. Research branch behavior

During technical spikes, Codex may add temporary dependencies.

A spike must finish with:

```text
benchmark result
decision
dependencies to retain
dependencies to remove
docs update
```

Temporary spike packages must not silently remain in core lockfiles.

---

# 37. Safe scaffold behavior

If the real provider is unresolved, implement:

```text
port
fake adapter
config model
error types
tests
benchmark harness
```

rather than guessing the vendor.

---

# 38. Definition of Done for a dependency change

```text
[ ] R3 class identified
[ ] phase permits it
[ ] adapter boundary respected
[ ] version pinned/locked
[ ] license checked
[ ] security reviewed
[ ] failure mode implemented
[ ] tests pass
[ ] docs updated
[ ] no unrelated runtime profile polluted
```

---

# 39. Final instruction to Codex

The technology repository is a set of **approved options and boundaries**, not permission to install everything.

Prefer the smallest implementation that satisfies the current phase and preserves the ports required for later replacement.
