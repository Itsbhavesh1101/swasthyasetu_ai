# SwasthyaSetu AI — Pre-P16 FHIR Mapping Specification and Readiness Pack

**Work unit:** `PRE-P16-FHIR-MAPPING-DESIGN` — **documentation and accountable-review preparation only**. No P16-A/B/C implementation, real patient import or export, FHIR validation sidecar, external integration, production profile or clinical authority.

- **Repository:** `Itsbhavesh1101/swasthyasetu_ai`
- **Verified `main` baseline:** `34b3e17df672c68e9677ca3ae88bf07c7711ea0c`
- **Previous PR #45:** MERGED to that SHA; reviewed head `a0a1fb9b6eaf34ac31de5c0f70f2d59ee47cb27c` has a tree-equivalent merge. Superseded PR #44 is CLOSED and unmerged.
- **Proposed isolated branch:** `phase/pre-p16-fhir-mapping-readiness`
- **Current Alembic head:** `p7a_0007` — do not change.
- **Baseline truth:** `docs/20_FHIR_MAPPING_SPEC.md` absent; `backend/app/modules/interoperability/fhir/` and `backend/app/adapters/fhir/` placeholders only. P16 and P17 NOT STARTED. No real FHIR mapper, validation service, transport, approved live export or import, authoritative exchange destination, or implementation-guide profile bundle is installed or authorized. `docs/21_ABDM_INTEGRATION_SPEC.md` absent. Current existing manual P7 text/touch intake continues unchanged.

> **Critical boundary:** An interoperable FHIR representation is not a clinically confirmed fact, a grant to disclose patient records, or an approved ABDM exchange. This task drafts technical contracts and unresolved decision inventory **only**. Technical acceptance, six green CI checks or a reviewer approving a PR cannot substitute for privacy, consent, clinical, source-identity, security, partner, legal, sandbox or production governance.

## 0. Mandatory preflight, evidence and precedence

1. Fetch GitHub origin and verify `main` and `origin/main` both equal exactly `34b3e17df672c68e9677ca3ae88bf07c7711ea0c`. Verify PR #45 is merged/tree-equivalent, PR #44 was not merged, and canonical Spec 20 is absent. If branch baseline changed or the target spec already exists, **STOP** rather than silently reset, overwrite, rebase or force-push. Use a **fresh isolated worktree**, preserving primary checkout and existing untracked files.
2. First read `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md` and the current canonical `docs/{00_PROJECT_MASTER_SPEC,01_PRODUCT_REQUIREMENTS,02_SYSTEM_ARCHITECTURE,03_REPOSITORY_STRUCTURE,04_DOMAIN_MODEL,05_DATABASE_SCHEMA,06_API_CONTRACTS,07_CLINICAL_INTAKE_SPEC,11_PROVIDER_ROUTING_POLICY,12_CLINICAL_PROVENANCE_SPEC,23_PATIENT_APP_SPEC,26_PRIVACY_CONSENT_SPEC,29_ENGINEERING_STANDARDS,30_TESTING_STRATEGY,33_ERROR_HANDLING_POLICY,34_MASTER_IMPLEMENTATION_PLAN}.md`, plus relevant existing P11 safety and privacy materials **as unapproved P11-only drafts, not platform approval**. Verify filenames exist before linking.
3. Read `docs/implementation/{35_PHASE_ACCEPTANCE_CRITERIA,36_DEPENDENCY_MAP,37_DECISION_LOG,38_PROGRESS_TRACKER}.md`, `docs/research/r3/{R3_FINAL_TECHNOLOGY_STACK,R3_CODEX_DEPENDENCY_POLICY}.md`, `docs/research/fhir/{FHIR_INTEROPERABILITY_TECH_EVALUATION,FHIR_CONFORMANCE_SECURITY_BENCHMARK_PLAN,FHIR_ADAPTER_CONTRACT_DRAFT}.md`, `docs/adr/ADR-004-fhir-boundary.md`, and current acceptance and consent records as appropriate. R2-C is research-derived and must not silently override accepted R3/ADRs or current code. Inspect the real P4 consent, P5 patient/encounter/fact/provenance types, P7 intake structures, P11 document domain and absent P16 paths. Do not fabricate patient records.
4. Trace `FR-FHIR-001..011`, `AC-P16-001..010`, and P16-A/B/C master-plan units against **exact text** in the actual current source-of-truth, not assumed summaries. Note `FR-ABDM-001..007` and `AC-P17-001..007` as P17 dependencies, **not** P16 completion evidence. Keep `ADR-004` (FHIR is an interoperability boundary), `ADR-008` (PostgreSQL canonical), `ADR-010` (provenance), `ADR-021` (typed contracts), `ADR-022` (no invented clinical policy), `ADR-035` (HAPI preferred sidecar), `ADR-038` (phase-activated dependencies), consent and feature registration rules intact.
5. Verify current `R3_FINAL_TECHNOLOGY_STACK.md` adopts **FHIR R4 4.0.1** as project baseline. This does **not** select an ABDM profile package, HAPI deployment, endpoint, conformance certificate, standards-validation result, library, vendor, consent purpose, source mapping or external actor. Do not import a new package or select current ABDM API flows from memory.

## 1. Primary deliverable — `docs/20_FHIR_MAPPING_SPEC.md` (NEW, clearly DRAFT)

Title **20 — FHIR R4 Mapping and Validation Boundary Specification**. Prominently mark **DRAFT — PRE-P16 TECHNICAL GOVERNANCE; NO MAPPERS, VALIDATORS, REAL PATIENT EXCHANGE OR PRODUCTION APPROVAL IMPLEMENTED**. Record baseline SHA, date, source hierarchy, unresolved human owners and as-built vs future state. Provide at least these sections:

**A. Scope and authoritative truth.** Internal patient, encounter, clinical fact, document and consent domains are the source of truth (PostgreSQL); FHIR represents a **versioned, replaceable interoperability projection**, not a primary patient datastore. P5/P7 clinical fact states and corrections must not become unqualified external clinical assertions; FHIR transport may not affect core intake. P16 prerequisites and explicit P17-only ABDM flow separate.

**B. Separation of ports and service responsibility.** Reconcile accepted broad `FHIRProvider` sidecar terminology and R2-C's more precise proposed **SwasthyaSetu-owned `FHIRMapper`, `FHIRValidationPort`, optional `FHIRRepositoryPort`, `FHIRRemoteClientPort`, and application-level `FHIRGatewayService`**. Document ownership of mapping, validation, transport, authorizations and orchestration; state the precise ports are *proposed pending architecture review*, not silently accepted API/classes. External HAPI FHIR remains conditional validation/conformance sidecar and optional FHIR projection repository; remote-client candidate `httpx` is not now a new dependency. ABDMProvider remains separate; no real sidecar, external endpoint, credential, route or feature flag in this PR.

**C. Versioned mapping context and provenance contract.** Proposed typed request, result, provenance and error shapes with strict FHIR version R4 (4.0.1), mapping revision, source type and IDs, source version/status and verification, patient/encounter relationship, owner, target profile and implementation guide when selected, institution/tenant scope, purpose/permission checks, source time vs transformation time (RFC3339/UTC), uncertain/unknown/absent data, warning or blocking issue, correlation ID, and explicit no raw narrative leakage in telemetry. Unknown or contradictory data must remain uncertain; no silent inferred facts, unverified clinical confirmation, or overwritten source history. Record lawful ground and consent as separate **preconditions** for an authorized exchange, not automatic properties of a data field.

**D. Traceable resource matrix, without fabricated field-level mappings.** Provide individually scoped future contracts for Patient, Encounter, Observation, AllergyIntolerance, relevant medication resources, DiagnosticReport, DocumentReference, Consent and Provenance; mention Bundle and Composition for future approved packages as applicable. For each: internal authoritative source, transformation eligibility, version and source provenance, absent/unknown representation, security and privacy preconditions, allowed output scope, lossiness/round-trip limitations, profile validation pending, and human decisions needed. All field crosswalks with undefined clinical or identity meaning must be **TBD**, not invented. In particular: P8 unconfirmed extractor candidates cannot automatically become confirmed clinical Observation, and model risk scores cannot become confirmed FHIR Condition. P11 document storage and access gates remain blocked; DocumentReference is **not** a grant to read or share binary documents.

**E. Mapping direction, corrections, and data authority.** Define design-only export and import candidate paths, permitted operations, schema rejection/quarantine handling, source verification, deduplication and identity matching **pending institution policy**, update and deletion/correction provenance, consent revocation, supersession, actor scoping, rollback and idempotency. No automated reconciliation into clinical truth, no overwriting clinician-confirmed records, no patient identity merges without approved policy. Import is a reviewed candidate, not direct write into patient record. Validation status should distinguish structural FHIR validity, selected profile conformance, terminology validation, clinical truth, patient authorization, and recipient eligibility: one does not imply another.

**F. Conformance and profile governance.** State **FHIR R4 4.0.1** only as R3 baseline and qualified HAPI candidate sidecar, not a working validator. Describe proposed layers STRUCTURAL, PROFILE, PROFILE_AND_TERMINOLOGY; owner-defined blocking, warning and informational issue classification (vendor must not control safety policy); versioned implementation-guide package and package license/source/version; no guessed current ABDM packages or URLs. Exact profiles, terminology, consent representation, medication variants and institutional policy are human-review pending. Test expectations for closed-world versions and schema fail-closed, including negative/resource-quality cases.

**G. Security, privacy and exchange prerequisites.** Export flow **trusted actor -> object and institution authorization -> valid purpose-specific consent or other specifically reviewed applicable authority where lawful -> minimal authorized snapshot -> mapper -> profile validation -> approved gateway/destination -> evidence and audit**. Do not assume `GENERAL_PRODUCT_USE` or `clinical_intake` consent authorizes FHIR or ABDM export; `REFERRAL_SHARING` consent applies to actual external referrals independently, not all FHIR exchange. Real data transfer, patient-level reference lookups and external validation require explicit security and privacy review of recipients, region, authentication, minimization, access control, audit, retention, breach response, outbound destinations and revocation. No PHI in general logs, browser persistent state, model prompts, error stacks, CI fixtures or source code. Local P7 path, emergency navigation and valid clinical source remain unaffected if FHIR is unavailable.

**H. Threat and negative-test inventory.** List separately testable future cases: unauthorized patient/encounter, cross-tenant and wrong-institution target, forged authorization, expired/revoked consent, unverified resource, unknown profile and terminology, wrong R4 version, invalid reference, mixed-patient Bundle, mass export, document link/URL leaks, SSRF to configured endpoints, stale identity linkage, replay and idempotency collision, duplicate remote response, import provenance missing, clinician-correction overwrite, inferred diagnosis, observation/model-risk conflation, endpoint timeout, partial transactions, unsafe HAPI defaults, no validator, validation mismatch, raw narrative in logs, scope drift, and ABDM outage isolation. These are **proposed future tests**, not proof of P16 compliance.

**I. Phase ownership and traceability.** Table with each **`FR-FHIR-001..011`** and **`AC-P16-001..010`** showing canonical wording, exact spec section, as-built evidence, required future human or technical artifact, and status **LIVE NOT VERIFIED**. Delineate P16-A DTO/mapping, P16-B validator/gateway and P16-C API/export/import tests as **NOT STARTED, separately scoped and gated**. Distinguish P17 ABHA/ABDM and `21_ABDM_INTEGRATION_SPEC.md` as future and absent. No live clinical export or import is authorized by this draft.

## 2. Companion deliverable — `docs/implementation/P16_READINESS_GATE_REVIEW.md` (NEW)

Create a **proposed, unapproved readiness and human-decision inventory**, not a fabricated official gate program or P16 approved criterion count. Each review area must include accountable **roles only**, actual evidence, what is missing, required future artifact, relevant FR/AC, risk and tests, separately possible synthetic/offline engineering *only if later explicitly scoped*, and STOP conditions:

1. Internal domain stability and trustworthy source/version/provenance, including external import corrections and ambiguity.
2. Qualified source-backed FHIR R4 resource crosswalks and terminology, including Patient, Encounter, Observation, AllergyIntolerance, Medication, reports, documents and Consent.
3. FHIR R4 profile conformance and independent validation evidence; conditional HAPI lifecycle, published package versions and licensing, no presumed ABDM profile approval.
4. Identity, object/institution and field authorization, purpose-specific consent, legal/retention/audit and minimization; deny exports by default.
5. Adapter and outbound endpoint security, network/SSRF, least privilege, authentication, non-authoritative sidecar, traceability and no sensitive logs.
6. Import authority, provenance, clinical confirmation/corrections, lossiness, identity match and versioned reversibility.
7. Synthetic cross-resource, round-trip/validation, negative and timeout/retry/idempotency test plan; meaningful conformance evidence vs merely parseable JSON.
8. P17 ABDM dependency, approved `21_ABDM_INTEGRATION_SPEC.md` absence, sandbox/consent and producer-specific requirements; live rollout and incident/rollback decisions.

Do not assign a new official P16 gate count, invent accountable signatories, or mark any human review as accepted. Provide an unsigned decision template, owner/risk register and next accountable review action. Preserve P8-C/P9-C Stage 3 BLOCKED, P10/P11 live 0/9 approved, P12/P13/P14/P15/P16/P17/P21 runtime NOT STARTED, and unchanged P7 manual intake. P15 clinical/readiness STOP remains intact; Pre-P16 does not grant permission for any P15 engineering.

## 3. Progress tracker and locked changed-path allowlist

Modify **ONLY**:

```text
docs/20_FHIR_MAPPING_SPEC.md                              # NEW; unapproved technical design
docs/implementation/P16_READINESS_GATE_REVIEW.md            # NEW; unsigned review inventory
docs/implementation/38_PROGRESS_TRACKER.md                 # minimal status and section 62
docs/codex/CODEX_PHASE_PROMPTS/PRE_P16_FHIR_MAPPING_SPEC_AND_READINESS_PACK.md # exact byte-identical copy of this prompt
```

- In the tracker `Before P16/P17` table, change ONLY the `20_FHIR_MAPPING_SPEC.md` entry from NOT STARTED to **DRAFT — ACCOUNTABLE ARCHITECTURE, CLINICAL, PRIVACY, SECURITY AND INTEROPERABILITY REVIEW PENDING; NO LIVE P16 APPROVAL**. Leave `21_ABDM_INTEGRATION_SPEC.md` as **NOT STARTED**.
- Add exactly `# 62. Pre-P16 FHIR Mapping Specification and Readiness Pack`, with base main SHA, PR #45 tree-equivalent merge evidence, new files, requirements and AC mapping, unresolved human decisions, no activated infrastructure, safety and privacy restrictions, STOP and next action.
- Preserve past section 61 and earlier historical records verbatim; do not silently edit past PR references, accepted ADRs, dependency choices, runtime phase statuses or official gate counts. Alembic stays `p7a_0007`; Next.js remains pinned at `16.4.2`.

**Prohibited:** backend or web application code, P16 mapper/tests/fixtures/schema/ORM/migrations, imports/exports/API/BFF, new endpoint, adapter implementation, HAPI sidecar, Docker/Kubernetes/CI/network changes, FHIR libraries or lockfile updates, mapping production data, real patients/PII, third-party patient data, credentials, sandbox provisioning, ABHA identity flows, public source downloads, profile package acquisition, vendor selection, consent or policy changes, clinical assertion, model output, feature-flag activation, approval signatures, unrelated documentation, and source-material edits.

## 4. Quality, CI and handoff

1. Validate exact `FR-FHIR-001..011`, `AC-P16-001..010`, source document paths and Markdown links; check R2-C research-vs-R3 accepted architecture and `ADR-004/035` boundaries. Confirm no guessed profile, reference codes, provider authority, real clinical mappings, patient examples or false approval. Validate `git diff --check`, exact 4-path allowlist, precise tracker heading 62, no duplicate headings, no credentials, and recorded-prompt byte equivalence. Run local Gitleaks against the entire new branch history before PR push where possible; avoid slash-heavy lifecycle word clusters that scanners may mistake as keys. Do not suppress or weaken scans to make them green.
2. Run applicable local repo quality checks as feasible and report actual counts, failures and retries. Require **all six** GitHub CI jobs to conclude **SUCCESS on the exact final PR head SHA**: Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, and Security scans. Preserve known Trivy and braces warnings honestly. Do not alter CI or add dependencies in response to unrelated advisories.
3. Commit one clean isolated feature branch from the verified baseline, push and open **one PR**. Verify local SHA, remote SHA, PR head SHA and CI run head are identical. **DO NOT MERGE**. Do not begin P16-A/B/C runtime or P17 work. Stop for independent review.

### Required completion report

```text
STATUS: COMPLETE PRE-P16 DOCUMENTATION ONLY / PARTIAL / BLOCKED
BRANCH: phase/pre-p16-fhir-mapping-readiness
BASE MAIN SHA: 34b3e17df672c68e9677ca3ae88bf07c7711ea0c
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER:
20 FHIR SPEC — AS-BUILT AND PROPOSED MAPPER/VALIDATOR/PORTS:
P16 READINESS — HUMAN DECISIONS AND STOP CONDITIONS:
FR-FHIR-001..011 / AC-P16-001..010 TRACEABILITY:
FHIR R4 4.0.1 / HAPI SIDEcar CANDIDATE / ABDM SEPARATION:
PROVENANCE, PRIVACY, CONSENT, UNSUPPORTED CLINICAL ASSERTIONS:
UPSTREAM GATES / P16 AND P17 NOT STARTED:
CHANGED PATHS / ALEMBIC / DEPENDENCIES / UNRELATED CHANGES:
LOCAL QUALITY / GITLEAKS / RETRIES / WARNINGS:
CI RUN ID / EXACT FINAL SHA / SIX JOB CONCLUSIONS:
MERGED: NO
```

**STOP after opening the PR.** This is a technical mapping and accountable-review pack only, not validated FHIR conformance, permission to process real patient data, production clinical import/export, live ABDM exchange or sign-off for P16/P17 implementation.
