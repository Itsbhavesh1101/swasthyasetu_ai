# SwasthyaSetu AI — Open-Source Research Methodology

**Document ID:** SSAI-OSS-001  
**Status:** Active research standard  
**Review baseline:** 2026-10-09

## Objective

Select third-party components by evidence, not popularity alone. GitHub stars are recorded as an adoption signal, but cannot establish security, licensing, medical suitability, maintainability, or production readiness.

## Required repository review

For serious candidates, inspect as available:

- repository structure and implementation boundaries;
- package/build manifests and lockfiles;
- important source paths and extension interfaces;
- tests and test configuration;
- CI/CD workflows;
- release/tag cadence;
- recent commits;
- open issues and recurring failure themes;
- recent pull requests;
- security policy/advisories;
- source-code license;
- model-weight license;
- dataset license;
- deployment/self-hosting options;
- runtime/resource requirements;
- public API stability;
- failure modes and replaceability.

For very large projects, a deep review means representative inspection of architecture, hot paths, tests, CI, manifests, issues, releases, security and licensing—not pretending to manually read millions of lines.

## Screening weights

| Criterion | Weight |
|---|---:|
| Architecture + requirement fit | 20% |
| Maintenance health | 15% |
| Security/privacy posture | 15% |
| License suitability | 10% |
| Code/test quality | 10% |
| Documentation/operability | 10% |
| Replaceability | 10% |
| Community/adoption | 5% |
| GitHub stars | 5% |

## Decision labels

- **ADOPT** — strong fit and safe to use within our architecture.
- **ADOPT BEHIND ADAPTER** — strong fit, but only through a SwasthyaSetu port/interface.
- **BENCHMARK BEFORE ADOPTION** — promising, but representative evaluation is mandatory.
- **CONSIDER** — viable alternative worth keeping in the shortlist.
- **REFERENCE / INTEGRATE ONLY** — useful system/reference, but not appropriate as our core.
- **REJECT FOR DEFAULT** — not recommended as the default new dependency.

## Non-negotiable architecture rule

SwasthyaSetu owns its domain, workflows, consent, deterministic safety, longitudinal context, provider/referral logic, UI and governance.

External technology is integrated through boundaries such as:

`OCRPort`, `SpeechToTextPort`, `TranslationPort`, `LLMProvider`, `FHIRProvider`,
`IdentityProvider`, `ObjectStorageProvider`, `ModelTrackingProvider`, and `QuantumBackend`.

No dependency may bypass safety, provenance, authorization or consent.

## Technical spikes required before final adoption

**OCR:** prescriptions, labs, discharge summaries, printed/handwritten text, phone-camera scans, Hindi/English/code-mixed samples; measure CER/WER, medical-entity preservation, table extraction, latency and resources.

**ASR:** quiet/noisy OPD audio, Hindi/English/Hinglish; measure WER, negation and medication/symptom retention, latency and memory.

**Translation:** medical negation, temporality, medication names and safety language with bilingual human review.

**FHIR:** round-trip Patient, Encounter, Observation, AllergyIntolerance, medication resources, DiagnosticReport, DocumentReference and Consent through validation.

**LLM gateway:** structured JSON, malformed output, timeout, provider switching, minimal-context use, prompt injection and privacy-safe telemetry.

**QML:** identical target, train/test split, preprocessing and metrics to the classical baseline.

## Clinical-content rule

Open-source popularity is never evidence that medical rules/content are correct. Crisis wording, red flags, contraindications, self-care/Ayurveda guidance, screening thresholds and clinical routing still require SwasthyaSetu's clinical-governance process.
