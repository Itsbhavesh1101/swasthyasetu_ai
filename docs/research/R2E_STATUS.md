# R2-E Status

**Status:** COMPLETE — deep research / pre-technical-spike.

## Current direction

- Keep a SwasthyaSetu-owned `LLMProvider`; do not deploy a central LLM gateway in MVP.
- LiteLLM is a strong conditional gateway/SDK candidate, not a default dependency.
- Adopt MLflow for isolated research experiment tracking and registry metadata.
- SwasthyaSetu owns model governance and clinical approval states.
- Prefer ONNX Runtime for portable inference only when parity passes; disable vendor telemetry in healthcare deployment profile.
- Prefer skops over arbitrary pickle-style persistence for compatible scikit-learn models.
- Use SHAP for compatible explainability and Optuna for governed HPO.
- Keep pgvector; use a narrow project-owned RetrievalService and evaluate Sentence Transformers for local multilingual embeddings/reranking.
- Do not make LangChain or LlamaIndex core dependencies; Haystack remains a conditional advanced-pipeline option.
- Use project-native pytest regression as primary LLM evaluation; Promptfoo is optional isolated red-team/evaluation tooling.
- PennyLane is the primary QML research framework; Qiskit Machine Learning is the secondary VQC/QSVC/QNN comparison stack.
- QML remains simulator-first and outside the clinical safety path.

## Gate

All production model adoption remains subject to:
model card + dataset manifest + immutable artifact hash + validation + calibration/threshold review + explicit SwasthyaSetu approval.
