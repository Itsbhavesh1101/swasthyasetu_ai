# Codex Documentation Prompt — Pre-P7 Specification Pack

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-PRE-P7-SPECS`
**Work unit:** Pre-P7 prerequisite specifications
**Base branch:** `main`
**Expected base commit:** `ed08ab6109995001821d9bd2b6b305666e045c1d`
**Implementation branch:** `phase/pre-p7-specification-pack`
**Commit message:** `docs: complete P7 prerequisite specifications`

## 0. Mission

P6 is complete. P7 MUST NOT begin until its prerequisite specifications are created and approved.

Create exactly these missing canonical documents:

```text
docs/07_CLINICAL_INTAKE_SPEC.md
docs/22_UX_AND_USER_FLOWS.md
docs/23_PATIENT_APP_SPEC.md
```

This is documentation-only. Do NOT implement P7 code.

Do NOT change:

```text
backend/app/**
backend/migrations/**
apps/**
packages/**
tests/**
package.json
pnpm-lock.yaml
backend/pyproject.toml
backend/uv.lock
.github/workflows/ci.yml
deployments/**
infra/**
```

except documentation/index/tree files where required.

## 1. Preflight

Expected:

```text
branch: main
HEAD: ed08ab6109995001821d9bd2b6b305666e045c1d
working tree: clean
P6 = COMPLETE
P7 = NOT STARTED
Alembic head = p5b_0006
```

Create:

```text
git switch -c phase/pre-p7-specification-pack
```

Do not merge.

## 2. Required Reading

Read completely before drafting:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md
docs/05_DATABASE_SCHEMA.md
docs/06_API_CONTRACTS.md
docs/29_ENGINEERING_STANDARDS.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md
```

Inspect actual merged implementation relevant to future P7:

```text
backend/app/modules/patients/**
backend/app/modules/encounters/**
backend/app/modules/consent/**
backend/app/modules/sessions/**
backend/app/modules/provenance/**
backend/app/shared/**
apps/patient-web/**
```

The new specs must fit the codebase that actually exists.

## 3. Source-of-Truth / Safety Rule

Reconcile and organize existing approved requirements. Do not silently invent medical policy.

Do not invent:

```text
diagnostic logic
red-flag thresholds
emergency criteria
triage rules
medication advice
treatment guidance
Ayurvedic diagnostic rules
Dashavidha clinical interpretation
specialty routing rules
provider recommendations
screening cutoffs
unapproved clinical question content
```

Use explicit markers where applicable:

```text
CLINICAL APPROVAL REQUIRED
DEFERRED TO P<n>
OPEN DESIGN DECISION
```

## 4. Canonical P7 Acceptance

The specs must trace:

```text
AC-P7-001 patient can start structured intake without LLM
AC-P7-002 chief complaint represented
AC-P7-003 HPI fields represented
AC-P7-004 PMH/PSH/medication/allergy/family/personal history represented
AC-P7-005 ROS/prior investigations represented
AC-P7-006 adaptive selection deterministic/config-driven
AC-P7-007 reliable known history can reduce repetition
AC-P7-008 question-pack registration supports future specialties
AC-P7-009 AYUSH extension exists without invented production clinical content
AC-P7-010 completed intake remains draft, not diagnosis
```

P7 units remain:

```text
P7-A intake domain/schema
P7-B deterministic adaptive engine
P7-C APIs + patient UI
```

## 5. FR-INTAKE Traceability

Explicitly map FR-INTAKE-001..032, including:

```text
presenting complaint
text input
voice future boundary
touch input
adaptive questioning
existing-history reuse
chief complaint
HPI: onset/duration/location/character/severity/progression/associated symptoms/aggravating/relieving
past medical/surgical history
medication/allergy history
family/personal history
review of systems
prior investigations
missing information
contradictions
one-question mode
draft status
AYUSH mode
approved Dashavidha-related extension fields
modular specialty questionnaires
```

Also reconcile applicable FR-ENC, FR-LANG, PRIV, NFR-ACCESS, NFR-UX, NFR-SEC and NFR-TEST requirements.

Do not pull P8/P9/P12 implementation into P7.

## 6. Architecture Constraints

Preserve:

```text
modular monolith
clinical_intake owns its domain/application/persistence
cross-module access only through public capabilities
no direct foreign ORM access
PostgreSQL authoritative source of truth
typed/versioned schemas
no unrestricted JSON clinical truth
shared patient context via public interfaces
LLM not required for P7
LLM never authoritative
draft intake != diagnosis
safety/triage separate from intake
provenance first-class
```

Dependency direction remains conceptually:

```text
sessions -> consent -> patients -> encounters -> clinical_intake
```

No competing patient-history silo.

## 7. Existing Persistence Baseline

Reconcile the already-defined future tables in `05_DATABASE_SCHEMA.md`:

```text
clinical_intakes
intake_answers
questionnaire_instances
```

The new spec must define typed/versioned meaning for every JSON field sufficiently for P7-A implementation.

Do not add unrelated tables. If a new table seems necessary, mark it `OPEN DESIGN DECISION` rather than silently making it canonical.

## 8. Existing API Baseline

Reconcile:

```text
POST /api/v1/encounters/{encounter_id}/intake
GET  /api/v1/intakes/{intake_id}
POST /api/v1/intakes/{intake_id}/answers
POST /api/v1/intakes/{intake_id}/complete
```

The already-documented:

```text
POST /api/v1/intakes/{intake_id}/messages
```

must be marked `DEFERRED TO P8` and excluded from P7 completion.

# 9. Create `docs/07_CLINICAL_INTAKE_SPEC.md`

Required sections:

```text
Document control
Purpose / scope / non-goals
Requirement mapping
Terminology
Trust and clinical-authority model
Bounded-context responsibilities
Intake lifecycle
Encounter relationship
Session/consent prerequisites
Structured intake aggregate
Chief complaint schema
HPI schema
History sections
Review of systems
Prior investigations
Missing-information model
Contradiction model
Question-definition schema
Answer schema
Question-pack schema
Questionnaire-instance schema
Deterministic adaptive-engine contract
Reliable-history reuse
Source/provenance semantics
AYUSH extension architecture
Accessibility/input modes
Multilingual boundary
API contracts
Persistence mapping
Concurrency/idempotency
Privacy/logging
Error model
Events/capabilities
Testing requirements
P7-A/P7-B/P7-C ownership
Deferred work
Open decisions
AC-P7 traceability
```

## 10. Intake Lifecycle

Define a minimal deterministic lifecycle distinguishing:

```text
active editable intake
completed draft
abandoned/incomplete intake
```

Must explicitly define:

```text
allowed transitions
terminal states
completed_at semantics
version/optimistic concurrency
relationship to Encounter lifecycle
```

No diagnosis state. No unsupported clinician-approved state.

## 11. Encounter Relationship

Define:

```text
one clinical intake per encounter in P7
clinical_intakes.encounter_id UNIQUE
```

Clarify:

```text
start intake requires suitable encounter
intake does not create competing care episode
intake completion does not mean diagnosis
intake completion does not bypass encounter lifecycle
```

P7 should operate on applicable general/kiosk intake workflows. Do not pull mental-health routing into P7.

## 12. Consent / Session Rule

P6-B currently uses:

```text
subject_type = SESSION
purpose = GENERAL_PRODUCT_USE
scope = ["clinical_intake"]
notice_version = privacy-v1
```

Specify that starting/mutating P7 intake requires centralized consent validation covering `clinical_intake` and valid session authorization.

Do not activate PATIENT consent.

Pseudonymous access must remain tied to exact session bearer through existing session/encounter boundaries. Cross-session access fails closed.

## 13. Structured Intake Aggregate

Define typed state for:

```text
intake_id
encounter_id
status
chief_complaint
hpi
history_sections
missing_information
contradictions
started_at
completed_at
version
```

Do not include diagnosis, treatment recommendation, triage route, or model score.

## 14. Chief Complaint / HPI

Chief complaint must support patient wording and deterministic/configured normalized/display representation without requiring AI.

HPI must support:

```text
onset
duration
location
character
severity
progression/course
associated symptoms
aggravating factors
relieving factors
```

Define optionality/value shapes without clinical interpretation or triage thresholds.

## 15. History Sections

Define versioned typed representation for:

```text
past medical history
past surgical history
medications
allergies
family history
personal history
review of systems
prior investigations
```

Reuse public patient context when sufficiently reliable. Do not duplicate authoritative longitudinal truth into an unrestricted intake JSON silo.

## 16. Reliable-History Reuse

Specify deterministic rules:

```text
use patients public capability only
never direct patient tables
ignore rejected/superseded context
never silently convert reused context into patient-confirmed answer
present/reconfirm reused value where appropriate
patient disagreement creates contradiction/update candidate
never destructively overwrite authoritative history
```

Do not invent clinical trust thresholds.

## 17. Missing Information / Contradictions

Both must be machine-readable and must not contain hidden chain-of-thought.

Missing information should identify at least:

```text
field/question key
reason code
requiredness
source pack/rule
resolution state
```

Contradiction model should identify at least:

```text
conflicting field/answer refs
source refs
status
clarification-needed state
resolution ref
```

Do not silently select a winner.

## 18. Questions / Answers

Define versioned question contract with at least:

```text
question_id
question_version
section
prompt/content key
answer type
requiredness
applicability rule IDs
sensitive flag
input modes
validation constraints
dependencies
```

Define a closed initial answer-type set sufficient for P7, e.g.:

```text
TEXT
SINGLE_CHOICE
MULTI_CHOICE
BOOLEAN
NUMBER
DATE
DURATION
SEVERITY_SCALE
```

Typed domain interface only; JSONB is versioned serialization.

Initial source types should distinguish at least:

```text
PATIENT_TEXT
PATIENT_TOUCH
REUSED_HISTORY
```

Voice remains future-configurable / P12-owned.

## 19. Deterministic Adaptive Engine

Define provider-free deterministic contract.

Input conceptually:

```text
intake state
registered question packs
known reliable context
prior answers
resolved contradictions
```

Output:

```text
next question or completion-ready state
missing information
clarification requirement
applicable pack state
```

Must be deterministic, versioned/config-driven, testable, and LLM-independent.

No diagnosis or final triage.

## 20. Question-Pack Registry

Use explicit compile-time registration consistent with ADR-007.

Support architecture for:

```text
core intake pack
future complaint-specific packs
future specialty packs
AYUSH extension pack
```

Each pack should define:

```text
pack_id
version
questions
applicability/dependency metadata
```

No runtime plugin scanning.

## 21. AYUSH Boundary

Define only extension architecture:

```text
AYUSH pack registration
namespaced schema extension
approval/version metadata
```

Do NOT define diagnostic interpretation, Prakriti/Dosha scoring, treatment/remedies, or thresholds.

For FR-INTAKE-031:

```text
field capability exists
actual deployment-approved field pack = CLINICAL APPROVAL REQUIRED
```

## 22. API Detail

For each P7 endpoint specify:

```text
authorization
consent prerequisite
request schema
response schema
idempotency expectation
error mapping
Cache-Control
state transition
optimistic version expectations
```

Keep `/messages` deferred to P8.

## 23. Public Capabilities / Events

Define candidate capability names consistent with existing style:

```text
intake.start
intake.read
intake.answer
intake.complete
intake.next_question
```

Events only if useful, e.g.:

```text
ClinicalIntakeStarted
ClinicalIntakeAnswerRecorded
ClinicalIntakeCompleted
ClinicalIntakeAbandoned
```

Do not put raw full history into event payloads by default.

# 24. Create `docs/22_UX_AND_USER_FLOWS.md`

This is product-flow focused, not another domain model.

Required sections:

```text
Document control
Purpose / scope
UX principles
User modes
Current P6 baseline
Patient first-contact flow
Pseudonymous onboarding
Consent
Language
Intake start
Structured intake
One-question mode
Known-history confirmation
Contradiction clarification
Review draft
Intake completion
Resume/incomplete flow
Abandon/end-session flow
Error/degraded flow
Offline behavior
Urgent-help behavior
Accessibility
Mobile/kiosk
Multilingual boundaries
Privacy expectations
Future authenticated continuity
Deferred future flows
Screen/state inventory
Acceptance traceability
```

Preserve the real P6 journey:

```text
/ -> /start -> /language -> real pseudonymous session -> /consent -> real SESSION consent -> /encounter
```

P7-C extends after onboarding; do not redesign P6 security/storage behavior.

## 25. P7 UX Flow

Define:

```text
encounter readiness
 -> start encounter/intake
 -> presenting concern
 -> deterministic structured questions
 -> known-history confirmation where applicable
 -> clarification for contradictions/missing information
 -> review draft
 -> complete draft intake
```

Completion means structured draft ready for downstream governed use, NOT diagnosis/treatment/triage/clinician confirmation.

## 26. One-Question / History / Contradiction UX

For sensitive/complex flows:

```text
one primary question at a time
clear context/progress
non-destructive back/review
skip only when configuration allows
"I don't know" / "Prefer not to answer" only where configuration allows
```

Safety-critical requiredness depending on P9 must be marked deferred/approval-required.

Known history:

```text
show concise known value
ask confirm/update where relevant
preserve source/trust distinction
never silently answer for patient
```

Contradictions:

```text
plain non-accusatory wording
focused clarification
minimum necessary conflicting context
allow correction
never claim one value medically correct
```

## 27. Review / Offline UX

Review draft should distinguish:

```text
patient-provided information
known-history reused information
missing information
clarified/changed information
```

No diagnosis summary.

Offline remains generic only:

```text
no intake start/continue offline
no answer queue
no mutation replay
no clinical cache
```

# 28. Create `docs/23_PATIENT_APP_SPEC.md`

Implementation-facing patient web spec.

Required sections:

```text
Document control
Purpose / scope / non-goals
Existing P6 architecture
Routing map
State ownership
BFF boundary
Session handling
Consent handling
PWA/cache boundary
P7 intake route architecture
Component architecture
API client architecture
Form/input patterns
One-question interaction pattern
Review-draft pattern
Loading/error/disabled states
Accessibility
Mobile/kiosk
Language behavior
Privacy/browser-storage rules
Security rules
Telemetry boundaries
Testing strategy
P7-C acceptance mapping
Deferred features
Open decisions
```

## 29. Route Architecture

Reconcile current routes:

```text
/
/start
/language
/consent
/encounter
/documents
/results
/urgent-help
/referrals
/offline
```

Recommended minimal P7-C additions:

```text
/intake/[intakeId]
/intake/[intakeId]/review
```

If choosing another minimal structure, justify it.

Do not activate documents/results/referrals.

## 30. Browser / BFF State Rules

Preserve:

```text
NO clinical intake data in localStorage
NO clinical intake data in sessionStorage
NO IndexedDB intake persistence
NO Cache Storage for intake/API responses
NO bearer in browser JavaScript
```

Authoritative P7 state is server/PostgreSQL. Refresh/resume refetches authorized server state.

Follow P6 same-origin BFF pattern:

```text
patient UI -> Next route handler -> FastAPI
```

BFF:

```text
reads HttpOnly session credentials server-side
forwards bearer in Authorization only
never returns bearer
uses no-store
returns minimized typed JSON
```

## 31. Accessibility / Language

Carry forward P6:

```text
keyboard operation
visible focus
single logical h1
semantic forms
accessible errors
44px targets
320/390px reflow
reduced motion
forced colors
persistent urgent help
```

Current session language choices are `en` and `hi`.

Do not claim fully translated Hindi clinical intake unless approved localized question packs exist.

P12 owns speech/translation infrastructure.

## 32. Privacy / Logging

All three docs must consistently prohibit logging unnecessary sensitive content, especially:

```text
raw clinical answers
full chief complaint/HPI
medication/allergy content
family/personal history
Authorization
session token
consent payload
```

Operational telemetry should prefer:

```text
request_id
operation
status
duration
error code
non-sensitive machine question/pack IDs
version IDs
```

No chain-of-thought.

## 33. Testing Blueprint

Specs must be detailed enough for future implementation prompts.

P7-A future tests:

```text
domain invariants
typed serialization
migration constraints
pseudonymous encounter linkage
optimistic versioning
question-pack registry
AYUSH extension registration without production content
```

P7-B:

```text
deterministic next question
missing-field logic
history reuse
contradictions
repeatability
configuration versioning
no LLM dependency
```

P7-C:

```text
real API + PostgreSQL
real P6 session/consent authorization
patient UI
keyboard/mobile/reflow
no browser sensitive persistence
resume/review/complete
no diagnosis language
```

## 34. Cross-Document Consistency

Before finalizing, cross-check all three docs for identical semantics on:

```text
terminology
status values
routes
API names
source types
question IDs/answer types
consent purpose/scope
lifecycle
P7-A/B/C ownership
P8/P9/P12 deferrals
```

No contradictions are acceptable.

## 35. Decision Log

Only if a material architecture decision is newly settled, add a narrow entry to:

```text
docs/implementation/37_DECISION_LOG.md
```

Do not create ADR churn for ordinary specification detail.

## 36. Progress Tracker

After completion mark prerequisite queue:

```text
07_CLINICAL_INTAKE_SPEC.md = COMPLETE
22_UX_AND_USER_FLOWS.md = COMPLETE
23_PATIENT_APP_SPEC.md = COMPLETE
```

P7 remains:

```text
NOT STARTED
```

Recommended next action:

```text
P7-A — Intake Domain / Schema
```

Do not mark any AC-P7 criterion PASS yet.

## 37. Files Allowed to Change

Expected documentation-only changes:

```text
docs/07_CLINICAL_INTAKE_SPEC.md
docs/22_UX_AND_USER_FLOWS.md
docs/23_PATIENT_APP_SPEC.md
docs/03_REPOSITORY_STRUCTURE.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/implementation/37_DECISION_LOG.md   # only if needed
docs/codex/CODEX_PHASE_PROMPTS/PRE_P7_SPECIFICATION_PACK.md
README.md                                # only if needed
REPOSITORY_TREE.txt
```

No code/schema/dependency/CI changes.

## 38. Verification

At minimum:

```text
git diff --check
```

Audit:

```text
no backend changes
no frontend changes
no migrations
no dependency/lockfile changes
no CI workflow changes
Alembic head remains p5b_0006
P7 remains NOT STARTED
```

Push branch and allow existing six CI jobs to run unchanged. All should stay green.

## 39. Commit / Push

```text
git add docs README.md REPOSITORY_TREE.txt
git commit -m "docs: complete P7 prerequisite specifications"
git push -u origin phase/pre-p7-specification-pack
```

Do not merge.

## 40. Final Report

Return only:

```text
STATUS
BRANCH / GIT
07 CLINICAL INTAKE SPEC
22 UX / USER FLOWS
23 PATIENT APP SPEC
REQUIREMENT TRACEABILITY
ARCHITECTURE RECONCILIATION
CLINICAL / SAFETY DEFERRALS
P7-A READINESS
FILES CHANGED
CODE / SCHEMA / DEPENDENCY STATUS
VERIFICATION
CI
DEVIATIONS
OPEN DECISIONS
PROGRESS TRACKER
MERGE
RECOMMENDED NEXT UNIT
```

`MERGE PERFORMED: NO`

Recommended next:

```text
P7-A — Intake Domain / Schema
```

## 41. Success Definition

Complete only when:

- all three prerequisite docs exist;
- FR-INTAKE-001..032 are traceable;
- AC-P7-001..010 are mapped to future P7-A/B/C;
- clinical/safety decisions not yet approved are explicitly deferred;
- no clinical thresholds/policies are invented;
- P7 remains LLM-independent;
- P8 messages/AI are deferred;
- P9 safety policy is separate/deferred;
- P12 speech/translation remains separate;
- future P7-C preserves P6 BFF/HttpOnly/PWA privacy boundaries;
- no code/schema/migration/dependency/CI changes occur;
- P7 remains NOT STARTED;
- all existing CI jobs are green;
- branch is pushed and not merged.

Stop after the prerequisite specification pack.

## Implementation Record

```text
Executed: 2026-10-12
Branch: phase/pre-p7-specification-pack
Base: ed08ab6109995001821d9bd2b6b305666e045c1d
Created: docs/07_CLINICAL_INTAKE_SPEC.md, docs/22_UX_AND_USER_FLOWS.md, docs/23_PATIENT_APP_SPEC.md
Traceability: FR-INTAKE-001..032 and AC-P7-001..010 mapped; no P7 criterion claimed complete
Clinical/safety boundary: P8/P9/P12 and clinical approvals explicitly deferred
Code/schema/dependencies/CI workflow: unchanged
Alembic head: p5b_0006
P7: NOT STARTED
Remote CI: PASS — GitHub Actions run 38260421591; all six required jobs passed on specification commit c826f2dc1e8852483530958b4ed1f796d6cc412d.
Specification pack: COMPLETE
Next: P7-A — Intake Domain / Schema
```
