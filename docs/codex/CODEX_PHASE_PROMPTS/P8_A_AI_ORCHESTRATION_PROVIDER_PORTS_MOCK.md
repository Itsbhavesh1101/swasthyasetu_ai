# SwasthyaSetu AI — Codex Phase Prompt: P8-A AI Orchestration, Provider Port & Offline Mock

**Work unit:** `P8-A` only — provider-neutral, in-process AI orchestration infrastructure.

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Required baseline:** `main @ b510e502f58fbd964f3011f25616a03425c7c347`
**Evidence:** Pre-P8 PR #22 was merged at the baseline SHA. P7 complete.
**Branch to create:** `phase/p8-a-ai-orchestration-provider-ports`
**Migration baseline/head:** `p7a_0007` (must remain unchanged).
**Merge:** **DO NOT MERGE**. Create/update a PR and stop after CI and report.

## 0. Mission and non-negotiable boundaries

Implement a reusable, **in-process**, project-owned P8-A orchestration service with a provider-neutral asynchronous `LLMProvider` Protocol; strict, immutable, bounded generic request/result contracts; explicitly composed **disabled/unconfigured** and deterministic **offline fake** adapters; safe normalized failures, bounded deadlines/retries, version correlation, and privacy-safe health/telemetry. Implement complete unit/contract tests and preserve all P1–P7 behavior.

**Do not implement:** P8-B task-specific clinical prompts, extraction domain schemas, evidence/fact promotion, P8-C messages APIs/UI/persistence, P9 safety/triage, provider selection, any live/hosted LLM adapter, patient-data egress, RAG, agent frameworks, LangChain/LiteLLM Proxy, new services/containers, additional dependencies or migrations, or a patient-facing AI route. No fabricated diagnosis, medical advice, provider contacts, or clinical decision rules. An offline fake is exclusively an engineering/testing tool, never a production provider.

The current P7 deterministic intake and urgent-help shell must operate identically when P8-A is disabled, unavailable or fails. **Do not send or persist real patient data to/from any AI provider.**

## 1. Preflight: STOP on drift

1. Check `git status --short` empty; `git branch --show-current` is `main`; `git rev-parse HEAD` equals the exact baseline above; `git fetch origin`; verify `origin/main` matches. Confirm PR #22 merged and Alembic head `p7a_0007`.
2. If baseline moved, dirty worktree exists, or authoritative specs disagree, **STOP / report BLOCKED**; do not reset or discard changes and do not silently rebase.
3. Create branch `phase/p8-a-ai-orchestration-provider-ports` from verified main. Use repo's READ → AUDIT → PLAN → IMPLEMENT → TEST → DIFF AUDIT → VERIFY ACCEPTANCE → REPORT workflow.

## 2. Mandatory source-of-truth reading

Read the **actual repository files** before design/coding:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/06_API_CONTRACTS.md
docs/07_CLINICAL_INTAKE_SPEC.md
docs/13_AI_ORCHESTRATION_SPEC.md
docs/14_LLM_EXTRACTION_SPEC.md
docs/26_PRIVACY_CONSENT_SPEC.md
docs/29_ENGINEERING_STANDARDS.md
docs/30_TESTING_STRATEGY.md
docs/33_ERROR_HANDLING_POLICY.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/research/r3/R3_ARCHITECTURE_RECONCILIATION.md
docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md
docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md
```

Audit live implementation and established patterns, especially:

```text
backend/app/main.py
backend/app/config/{settings,sections}.py
backend/app/shared/{modules,capabilities,errors,feature_flags,observability}/**
backend/app/modules/clinical_intake/{public,application,contracts}.py
backend/app/adapters/ai/**
backend/tests/**
backend/pyproject.toml
.github/workflows/ci.yml
```

Read the accepted R2 AI adapter-contract draft only as subordinate research. Respect precedence: canonical docs and accepted R3 over research, current verified code over stale tracker. If any new dependency seems necessary, stop and seek approval rather than adding it; standard library + existing dependencies should suffice.

## 3. Domain-neutral API contracts (P8-A ownership)

Create an appropriate narrow module, e.g. `backend/app/modules/ai_orchestration/` with `contracts.py`, `application.py`, `public.py` (adapt to existing repository conventions). Keep fake/unconfigured provider adapters in `backend/app/adapters/ai/`. No provider SDK imports in domain/clinical modules.

Define and validate `StructuredLLMRequest` and `StructuredLLMResult` as **immutable project-owned objects** with strict types, explicit supported versions, machine-ID formats, finite numerical fields, maximum lengths/nesting/collection counts and serialized byte limits. Reject unknown fields in serialized input/output. The request must carry **only bounded, task-supplied** structured input; no unrestricted patient data, patient-defined endpoints, arbitrary headers, bearer, credentials, tools, policy overrides, chain-of-thought, or provider-supplied authority.

Request fields/semantics (follow `13_AI_ORCHESTRATION_SPEC.md`, not ad-hoc naming):

- safe opaque correlation `request_id` (not patient/session/encounter ID), `operation_id`, `language_code`, request-contract version;
- `schema_id`/`schema_version`, `prompt_id`/`prompt_version` (task-owned; not invented production clinical content);
- bounded structured input and source-reference-only `provenance_context`;
- total `deadline_at` **or** explicit timeout, positive `max_output_tokens`, nonnegative `retry_budget`, positive controlled attempt count;
- approved operational `provider_policy_id`/version identifiers (not clinical routing policies).

Result fields/semantics:

- exact originating safe request/operation/version/prompt/schema identities;
- bounded provider/model IDs/versions and optional safe provider request ID;
- bounded parsed candidate JSON value (generic structural validation only), normalized finish reason and optional usage;
- finite nonnegative latency, valid attempt count, versioned provenance; `raw_retained=False` by default.

**Crucial separation:** P8-A may check JSON syntax/shape, generic limits, version/correlation integrity and provider-contract compatibility; **P8-B alone** will define and validate *clinical extraction schemas, prompts, evidence sufficiency and domain meaning*. An adapter saying “success” cannot establish any medical fact. No automatic partial acceptance of malformed/unknown nested structures; do not claim a future task-specific schema is already present.

Set *bounded engineering-only* defaults for fake/unit-test calls where necessary, document their exact values and rationale, and label them **not production-approved**. Do not invent production operation limits, model policies or clinical approvals.

## 4. Provider port, adapters and explicit composition

Define `LLMProvider(Protocol)` with asynchronous `generate_structured(request) -> StructuredLLMResult` (or typed provider outcome consistent with the spec). Provide:

1. **Disabled/unconfigured adapter**: the only safe default; makes **zero network calls** and returns a typed unavailable outcome, never a fabricated success.
2. **Deterministic offline fake**: exact versioned request→configured response/failure matching; supports controlled timeout/transient/permanent faults and attempt sequences using injectable clocks/sleepers (or equivalent); rejects unexpected requests; no randomness, wall-clock dependence or network/PHI persistence; synthetic fixtures only. Test-only exposure/selection; prevent fake being registered in staging/pilot/production even if flags/overrides are supplied.
3. **No live provider implementation or selection**. No API keys or external service endpoints introduced.

Wire via **explicit compile-time composition** through existing per-app sealed module/capability registry, consistent with `ModuleManifest`, `ModuleRegistration`, `CapabilityKey`, and `create_app`. The AI service/port must be injectable for deterministic unit tests **without a mutable global singleton** or implicit auto-discovery. Keep default runtime disabled/unconfigured; if an activation flag is introduced, validate its name and ensure explicit safe-off, environment-gated fake selection that cannot bypass auth, consent or clinical authority. If custom module-registration injection is already used by tests, preserve that behavior. Keep duplicate/missing providers deterministic and typed.

The service is not to be invoked by P7 routes or patient app. Do **not** change `clinical_intake` composition, schemas, endpoints or transaction semantics to add an AI dependency.

## 5. Orchestration, failures and degraded operation

The orchestration service must:

- own **one total deadline** for all attempts, delays and result validation; promptly respect cancellation; never hold a PostgreSQL transaction during model operation;
- retry **only** explicitly classified transient timeout/rate-limit/selected 5xx **when a bounded policy allows and time remains**; cap attempts, backoff and any `retry_after` values; support deterministic test clocks/sleep without excessive wall-clock timing assertions;
- **never infrastructure-retry** auth/config errors, refusal, content-policy block, schema-invalid output, deterministic version/input failures, cancellation/exhausted deadline or unknown failure (default no retry); no secret/raw-provider data in errors;
- not silently switch providers, prompts, schema, model, region, context or policy between attempts; never upgrade candidate output to a domain fact;
- ensure operation failure returns typed **failure/degraded** behavior; no invented output, no hidden automatic call or ambiguous success;
- isolate provider exceptions; normalize to closed internal categories: `LLM_TIMEOUT`, `LLM_RATE_LIMIT`, `LLM_AUTH_FAILURE`, `LLM_PROVIDER_UNAVAILABLE`, `LLM_REFUSAL`, `LLM_SCHEMA_INVALID`, `LLM_CONTENT_POLICY_BLOCK`, `LLM_UNKNOWN`.

Do not add public HTTP error enums/status mappings or a patient endpoint. Internal error classification remains separate from existing application `ErrorCode`; only future task/API owners map to HTTP. Structured-output format repair is **not** a hidden gateway retry; at most document the future P8-B task-specific explicit bounded repair boundary. Keep P7 deterministic fallback and urgent-help independent.

## 6. Privacy, safety, health and observability

- **No real patient egress**; no live provider or production model; only synthetic/fake data. No raw prompts, input/outputs, source spans, context, credentials, cookies, bearers, ID-bearing metadata, exceptions or full payloads in logs, spans, metrics, test outputs or public errors. Use allowlisted safe correlation/operation IDs, status/category, attempt count, duration and compatible prompt/schema/model versions. Avoid high-cardinality IDs as metric dimensions.
- Implement minimal *programmatic* AI service health/status `disabled` / `unconfigured` / `configured` / `degraded` if meaningful; health must not issue a network request or impact core API readiness. Do **not** invent a new external health/public route unless canonical spec specifically mandates it.
- Ensure safe `repr`/exception handling and redacted output. Provider failures may only degrade optional AI; P7 session/consent/intake and urgent-help must remain available.
- Reuse existing OpenTelemetry/logging abstractions only with an explicit allowlist and appropriate tests. Do not export sensitive payloads or add exporters/services by default.

## 7. Mandatory tests (synthetic fixtures, no external requests)

Write targeted unit/contract/security regression tests under `backend/tests/` for:

1. strict frozen contracts, unknown fields, nested oversize/depth, disallowed values, wrong data types, NaN/Inf, missing IDs, invalid versions and source references;
2. true provider neutrality and replaceability via at least two independent test doubles satisfying the same public contract; no provider/vendor types leaking into domain;
3. fake exact-match repeatability, configured deterministic failure/success, unexpected-request rejection and zero network access;
4. disabled/unconfigured and production-fake-rejection tests (including malicious feature/override attempts);
5. matching request/result IDs, prompt/schema/request/provider/model metadata; reject version mismatch, spoofing and invalid usage/latency;
6. each closed provider failure category and exception sanitization; no-fabricated-success behavior;
7. total-deadline enforcement, cancellation, bounded retry under budget, transient/timeout/429 handling; all **no-retry** cases, bad Retry-After, exhausted deadline, constant provider/model/context across attempts;
8. redaction canaries across errors, logs, spans, metrics and object `repr` (no synthetic PHI, bearer, secret, rendered prompt or raw provider result);
9. module composition/sealed capability registry: explicit default, no auto-registration, duplicate prevention, isolated app instances and no route/feature drift;
10. P7 regression: existing deterministic intake and generic urgent-help accessible when AI disabled/degraded, no new patient browser state/caching, no runtime external egress.

Use controlled injection for time and provider transport. Do not use billable APIs or real patient fixtures. Cover `AC-P8-001` and `AC-P8-002` and the **P8-A evidence portion** of `AC-P8-004/005/006`; leave `AC-P8-003/007/008/009/010` and the P8-B/C portions **NOT YET VERIFIED**. Distinguish newly passing criterion from partial future evidence in tracker.

Run all repository-standard quality and CI checks, including Python formatting/lint/typecheck/import/compile, complete backend tests, real PostgreSQL migration/integration tests where environment supports them, frontend lint/tests/builds, Docker/Compose checks, Playwright Chromium, security scans and `git diff --check`. Required remote six jobs: **Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, Security scans**. Do not weaken CI to make tests pass.

## 8. Scope / migrations / governance

Expected changes:

```text
backend/app/modules/ai_orchestration/**   # new, exact module path may follow repo conventions
backend/app/adapters/ai/**               # offline fake/unconfigured only
backend/app/main.py                     # narrow explicit composition, only if required
backend/app/config/**                    # only strict optional config if required
backend/tests/test_ai_*.py              # contract/orchestration/registration/privacy tests
backend/tests/test_*.py                 # narrow existing test updates if necessary
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P8_A_AI_ORCHESTRATION_PROVIDER_PORTS_MOCK.md
README.md / REPOSITORY_TREE.txt          # index updates only if needed
```

Avoid changes to `apps/**`, `packages/**`, SQL/Alembic/migrations, `06_API_CONTRACTS.md`, `07_CLINICAL_INTAKE_SPEC.md`, clinical/safety policy, existing P7 interfaces, deployment manifests/CI, dependency manifests or lockfiles. Any genuinely necessary extra file/change must be explained with a direct P8-A justification, and must not broaden behavior. Alembic stays `p7a_0007`.

No new ADR unless a material unresolved decision must be approved; if so **STOP and present the decision** rather than inventing provider/clinical/privacy policy. Follow R3 dependency policy strictly. Do not copy or incorporate future P8-B/C implementations into P8-A.

## 9. Documentation, completion and review handoff

Update progress tracker **only after verified evidence**: P7 COMPLETE, Pre-P8 merged; P8-A COMPLETE only after tests + exact remote CI + review; P8 overall PARTIAL; P8-B/C NOT STARTED. If CI pending, record implementation complete / verification pending rather than preemptively marking phase complete. Preserve all open approvals for model/provider, clinical prompts, outbound patient-data consent and message persistence/retention; do not imply approval.

Commit with an appropriate scoped message, push to `origin/phase/p8-a-ai-orchestration-provider-ports`, open PR to `main`, **do not merge**. Capture branch/base/final local/remote SHA, PR URL, test counts, Alembic head, six CI jobs with run ID, scope/dependency audit, outstanding limitations and recommended P8-B next (after independent review/merge).

**Final report format (concise, no long narrative):**

```text
STATUS: COMPLETE / PARTIAL / BLOCKED
BRANCH:
BASE MAIN SHA:
FINAL LOCAL SHA:
REMOTE SHA:
PR URL / NUMBER:
P8-A SCOPE DELIVERED:
DEFAULT PROVIDER / FAKE GUARD:
CONTRACT & RETRY LIMITS (engineering only):
SECURITY / PRIVACY:
AC-P8 EVIDENCE / DEFERRED CRITERIA:
TESTS / QUALITY CHECKS:
CI RUN ID + SIX JOB RESULTS:
ALEMBIC HEAD / DEPENDENCIES:
UNRELATED CHANGES:
OPEN DECISIONS:
MERGED: NO
```

**Stop at the P8-A implementation + PR handoff; await independent review.**
