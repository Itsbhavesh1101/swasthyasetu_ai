# SwasthyaSetu AI — CODEX_INSTRUCTIONS

**Document ID:** SSAI-CODEX-001  
**Status:** Permanent implementation rules  
**Version:** 1.0.0-draft

## 1. Role

You are implementing SwasthyaSetu AI inside an existing product, safety, architecture, and engineering specification system. Your job is to inspect, understand, plan, implement, test, verify, and report. You are not the clinical authority and must not invent missing clinical or safety policy.

## 2. Mandatory context before code changes

Always read:

1. `docs/00_PROJECT_MASTER_SPEC.md`
2. `docs/02_SYSTEM_ARCHITECTURE.md`
3. `docs/29_ENGINEERING_STANDARDS.md`
4. `docs/34_MASTER_IMPLEMENTATION_PLAN.md`
5. `docs/codex/CODEX_WORKFLOW.md`
6. `docs/codex/CODEX_CONTEXT_RULES.md`

Also read the relevant requirement IDs in `docs/01_PRODUCT_REQUIREMENTS.md`, current phase specification, domain/API/database specs, and phase acceptance criteria.

## 3. Precedence

When instructions conflict, use this order:

1. approved clinical/safety policy
2. Project Master Specification
3. System Architecture
4. Product Requirements
5. privacy/security specifications
6. domain/database/API contracts
7. Engineering Standards
8. Master Implementation Plan
9. phase acceptance criteria
10. current implementation prompt

Do not silently override a higher-priority rule.

## 4. Repository audit before editing

Before changing files:

- run `git branch --show-current`;
- run `git status --short`;
- inspect relevant directories/files;
- inspect tests and migrations;
- locate public contracts;
- check whether the requested work already exists;
- identify any conflict with the requested phase.

Do not code from assumptions.

## 5. Scope discipline

Every implementation task must define `IN SCOPE` and `OUT OF SCOPE`. Implement only the requested phase/sub-phase. Do not opportunistically build later phases or rewrite unrelated working code.

## 6. Requirement traceability

Every implementation must identify the requirement IDs being satisfied. If important behavior has no requirement, flag it before implementing high-impact behavior.

## 7. Module ownership

Every business capability belongs to an explicit module. Do not create a god service.

Other modules may consume only documented public interfaces/contracts/events. Direct access to another module's internal repositories, ORM models, or private helpers is prohibited.

## 8. External systems

External systems must be behind ports/adapters, including LLM, OCR, speech, translation, storage, notifications, FHIR, ABDM, model inference, and quantum backends. Vendor SDKs must not leak into domain/application logic.

## 9. Clinical and AI boundary

LLMs may converse, translate, normalize, extract structured information, summarize, retrieve approved content, identify missing information, and ask clarifying questions.

LLMs must not independently diagnose, prescribe, change medication, decide final emergency/mental-health routing, invent doctors/resources/helplines, invent patient-facing remedies, or override deterministic safety rules.

Priority is:

`Safety Policy > Predictive Model > LLM Output > Convenience`

## 10. Missing clinical policy

If a task needs an undefined threshold, contraindication, crisis rule, screening criterion, or other clinical policy, report:

`STATUS: BLOCKED — CLINICAL POLICY REQUIRED`

You may scaffold interfaces, schemas, policy engines, and synthetic non-production fixtures, but must not invent real policy.

## 11. Missing provider/remedy/dataset decisions

If verified provider data is missing, build the registry and use clearly synthetic records only.

If approved self-care/Ayurveda content is missing, build the engine/schema/review workflow and use synthetic non-medical fixtures only.

If the final ML/QML dataset is undecided, build generic infrastructure and use synthetic/sample data rather than silently choosing an official dataset.

## 12. Structured AI output

Clinical/safety extraction must follow:

`LLM -> parse -> schema validation -> domain validation -> provenance -> domain use`

Malformed or unvalidated AI output must not enter safety logic.

## 13. Provenance

AI-derived facts must preserve source, provider/model, version, prompt/schema version where relevant, confidence/quality where meaningful, and verification state. Never silently promote extracted data to clinician-confirmed data.

## 14. Database rules

Every persistent schema change requires an Alembic migration. Inspect generated migrations. Test upgrades. Do not manually alter production schema outside the migration path.

Cross-module table writes are prohibited.

## 15. Transactions and external calls

Keep transactions explicit. Avoid long external calls inside transactions. Prefer pending state -> commit -> external call -> status update where applicable.

## 16. Errors and degraded modes

Use typed errors. Never swallow important exceptions. Never falsely claim success after dependency failure. Degraded modes must be honest and observable.

## 17. Logging and privacy

Use structured logs with metadata such as request ID, module, operation, duration, error code, policy version, and model version.

Do not log raw patient conversation, document text, tokens, passwords, secrets, full FHIR payloads, or unnecessary identifying data.

## 18. Security

Always consider authentication, authorization, object-level authorization, injection, XSS, CSRF where applicable, SSRF, upload risk, secret leakage, prompt injection, and rate limiting. Frontend hiding is never authorization.

## 19. Tests

Tests are part of implementation. Use appropriate unit, integration, contract, adapter, frontend, E2E, safety, security, multilingual, and ML/QML tests.

Do not delete, skip, or weaken a valid failing test merely to get green CI.

Every confirmed safety defect must receive a regression test before closure.

## 20. Frontend

Use strict TypeScript and typed API clients. Handle loading, empty, error, permission, and feature-disabled states. Do not duplicate backend safety policy in the browser. Do not store sensitive health data in browser storage by default.

## 21. Backend

Keep FastAPI routes thin. Business rules belong in application/domain services. Do not mix request parsing, clinical policy, persistence, and vendor calls in one route handler.

## 22. Dependencies

Before adding a dependency, inspect existing solutions, license, maintenance, security, size/complexity, and replaceability. Do not add competing frameworks casually.

## 23. Feature flags

High-risk or experimental features should be feature-flagged. Risky features default off. Mandatory safety controls default on. Mock adapters must never be selected silently in production.

## 24. Research isolation

Research/training code is separate from production clinical authority. Training a model does not activate it. Production may use only explicitly approved model versions.

Classical baseline comes before QML. Do not claim quantum advantage unless the benchmark actually demonstrates it.

## 25. FHIR and ABDM

FHIR is an interoperability boundary rather than the internal application model. ABDM remains behind an adapter. Do not infer current ABDM flows without the approved integration specification.

## 26. New features

Before implementing a new feature:

1. create/update requirement IDs;
2. classify safety/privacy impact;
3. identify module owner;
4. define public contracts;
5. define data ownership;
6. define APIs/events;
7. define failure behavior;
8. define tests;
9. update implementation/dependency docs;
10. then implement.

## 27. Architecture changes

If implementation requires a material architecture change, report:

`STATUS: BLOCKED — ADR REQUIRED`

Explain the conflict, proposed decision, alternatives, consequences, and migration. Do not silently change architecture.

## 28. Git discipline

Before coding:

- `git branch --show-current`
- `git status --short`

After coding:

- `git status --short`
- `git diff --stat`
- `git diff`

Inspect every changed file and ensure no unrelated modifications or secrets were introduced.

## 29. Verification

Run all checks required by the phase. Typical gates include formatting, linting, type checking, unit/integration/contract tests, frontend checks, migration checks, safety tests, and E2E tests where applicable.

Do not state a command passed unless it was run successfully.

## 30. Result status

Every task ends with one of:

- `COMPLETE`
- `PARTIAL`
- `BLOCKED`
- `FAILED`

`COMPLETE` means all applicable acceptance criteria pass.

## 31. Final report format

Return:

1. Status
2. Summary
3. Requirement IDs implemented
4. Files created
5. Files modified
6. Database migrations
7. APIs/contracts changed
8. Tests added
9. Commands run
10. Results
11. New dependencies
12. Architecture deviations
13. Safety/privacy impact
14. Known limitations
15. Remaining work

Be factual. Never falsify verification.

## 32. Core invariants

- LLM understands; governed systems decide.
- Safety rules outrank models.
- Humans retain clinical authority.
- AI-derived facts retain provenance.
- Providers/resources are verified rather than generated.
- Self-care uses approved knowledge rather than unrestricted generation.
- External providers are replaceable.
- Module ownership is explicit.
- Database changes use migrations.
- Failures degrade honestly.
- New features enter through the extension framework.


---

# R3 Dependency Policy

Before adding a new package, service, model runtime or infrastructure component, read:

```text
docs/research/r3/R3_FINAL_TECHNOLOGY_STACK.md
docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md
docs/implementation/36_DEPENDENCY_MAP.md
```

Do not interpret a researched candidate as permission to install it.

If the current phase does not activate that technology, implement the port/fake/config/test boundary instead.
