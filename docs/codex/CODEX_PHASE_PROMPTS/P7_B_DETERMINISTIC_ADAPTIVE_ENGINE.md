# Codex Phase Prompt — P7-B Deterministic Adaptive Engine

**Project:** SwasthyaSetu AI
**Prompt ID:** `SSAI-CODEX-P7-B`
**Phase unit:** P7-B — Deterministic Adaptive Engine
**Base branch:** `main`
**Expected base commit:** `1e4522c9f13309935faed0557ee2654cea54e093`
**Implementation branch:** `phase/p7-b-deterministic-adaptive-engine`
**Commit message:** `feat: implement P7-B deterministic intake engine`

## 0. Mission

Continue P7 from the merged P7-A baseline.

Current state:

```text
P6 = COMPLETE
Pre-P7 specification pack = COMPLETE
P7-A = COMPLETE
P7-B = NEXT
P7-C = NOT STARTED
P7 overall = PARTIAL
Alembic head = p7a_0007
```

Implement only P7-B.

P7-B owns:

```text
deterministic adaptive question engine
strict question-pack validation
rule compilation/evaluation
stable question ordering/tie-breaking
question/answer validation against registered definitions
missing-information calculation
configured skip/refusal handling
contradiction prioritization
reliable-history reuse eligibility
history-confirmation requirement logic
specialty/complaint/AYUSH structural pack extensibility
repeatability / determinism tests
zero-network / zero-LLM guarantees
```

P7-B does NOT own:

```text
FastAPI routes
application orchestration
session/consent enforcement
encounter authorization
patient BFF
patient frontend
real patient workflow
outbox events
new tables/migrations
new runtime module registration
production clinical question wording
production clinical requiredness policy
Hindi clinical content
AYUSH/Dashavidha production content
diagnosis
treatment
safety/triage
LLM/AI
speech/translation
documents/OCR
```

P7-C owns application services, APIs, authorization/consent integration, BFF/UI, resume/review/complete flows, and real E2E.

Do not merge.

---

# 1. Preflight

From repository root:

```text
git branch --show-current
git status --short
git rev-parse HEAD
git log --oneline --decorate -15
```

Expected:

```text
branch: main
HEAD: 1e4522c9f13309935faed0557ee2654cea54e093
working tree: clean
P7-A: COMPLETE
P7: PARTIAL
Alembic head: p7a_0007
```

Create:

```text
git switch -c phase/p7-b-deterministic-adaptive-engine
```

---

# 2. Required Reading

Read completely before coding:

```text
docs/00_PROJECT_MASTER_SPEC.md
docs/01_PRODUCT_REQUIREMENTS.md
docs/02_SYSTEM_ARCHITECTURE.md
docs/03_REPOSITORY_STRUCTURE.md
docs/04_DOMAIN_MODEL.md
docs/05_DATABASE_SCHEMA.md
docs/06_API_CONTRACTS.md
docs/07_CLINICAL_INTAKE_SPEC.md
docs/22_UX_AND_USER_FLOWS.md
docs/23_PATIENT_APP_SPEC.md
docs/29_ENGINEERING_STANDARDS.md
docs/34_MASTER_IMPLEMENTATION_PLAN.md
docs/implementation/35_PHASE_ACCEPTANCE_CRITERIA.md
docs/implementation/36_DEPENDENCY_MAP.md
docs/implementation/37_DECISION_LOG.md
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_INSTRUCTIONS.md
docs/codex/CODEX_WORKFLOW.md
docs/codex/CODEX_CONTEXT_RULES.md
docs/codex/CODEX_PHASE_PROMPTS/P7_A_INTAKE_DOMAIN_SCHEMA.md
docs/codex/CODEX_PHASE_PROMPTS/P7_A_REVIEW_FIX_01_LIFECYCLE_PERSISTENCE_GUARD.md
```

Inspect actual merged P7-A code:

```text
backend/app/modules/clinical_intake/domain.py
backend/app/modules/clinical_intake/contracts.py
backend/app/modules/clinical_intake/serialization.py
backend/app/modules/clinical_intake/infrastructure.py
backend/app/modules/clinical_intake/public.py
backend/tests/test_clinical_intake_domain.py
backend/tests/test_clinical_intake_boundaries.py
backend/tests/integration/test_postgres_clinical_intake.py
```

Also inspect public patient/provenance contracts only:

```text
backend/app/modules/patients/public.py
backend/app/modules/patients/contracts.py
backend/app/modules/provenance/public.py
backend/app/modules/provenance/domain.py
```

Do not import foreign module infrastructure.

---

# 3. Canonical P7-B Acceptance

P7-B must materially close:

```text
AC-P7-006
Adaptive question selection is deterministic/config-driven.

AC-P7-007
Known reliable patient history may reduce repeated questioning.

AC-P7-008
Question-pack registration supports future specialty modules.

AC-P7-009
AYUSH extension mechanism exists without invented production clinical content.
```

P7-B contributes to but does not independently close:

```text
AC-P7-001
AC-P7-010
```

Those require P7-C patient/API evidence.

---

# 4. Existing P7-A Contracts Are the Baseline

Preserve P7-A domain lifecycle:

```text
IN_PROGRESS -> IN_PROGRESS
IN_PROGRESS -> COMPLETED
IN_PROGRESS -> ABANDONED

COMPLETED = terminal
ABANDONED = terminal
```

Preserve P7-A closed answer types:

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

Preserve P7-A response dispositions:

```text
ANSWERED
UNKNOWN
PREFER_NOT_TO_ANSWER
SKIPPED
```

Preserve P7-A source types:

```text
PATIENT_TEXT
PATIENT_TOUCH
REUSED_HISTORY
```

Preserve question-pack kinds:

```text
CORE
COMPLAINT
SPECIALTY
AYUSH_EXTENSION
```

Do not expand these unless required by the canonical specification.

---

# 5. Recommended Package Shape

Extend:

```text
backend/app/modules/clinical_intake/
```

Recommended additions:

```text
engine.py
rules.py
history.py
pack_validation.py
```

Equivalent small separation is acceptable.

Do NOT add:

```text
application.py
api.py
router.py
```

P7-C owns those.

---

# 6. Engine Version

Introduce one immutable machine-readable engine version, for example:

```text
deterministic-intake.v1
```

The engine result/questionnaire state must expose or carry this version where appropriate.

Do not derive version from timestamps or environment.

Equal inputs + equal registry versions + equal engine version must produce equal output.

---

# 7. Adaptive Engine Input

Define a typed immutable engine input.

It must contain only the data needed for deterministic evaluation, conceptually:

```text
ClinicalIntake
registered/selected immutable QuestionPack versions
prior accepted IntakeAnswer values
eligible history context
current contradictions
```

Do not let the engine query:

```text
database
HTTP
filesystem
environment
clock
randomness
patient repository
LLM
external services
```

The engine must be pure/deterministic.

If timestamps or deterministic identifiers are needed, pass them explicitly or derive stable IDs from stable input.

---

# 8. Adaptive Engine Output

Implement explicit immutable result variants matching the canonical spec:

```text
NextQuestion
ClarificationRequired
CompletionReady
Incomplete
```

Recommended fields:

```text
NextQuestion
- question
- pack_id
- pack_version
- reason_rule_ids
- engine_version

ClarificationRequired
- contradiction_id
- question
- pack_id
- pack_version
- reason_rule_ids
- engine_version

CompletionReady
- missing_information = ()
- engine_version

Incomplete
- missing_information
- engine_version
```

Use typed dataclasses / discriminated result classes.

Do not return untyped dictionaries.

Do not return:

```text
diagnosis
clinical interpretation
triage route
risk score
treatment suggestion
```

---

# 9. Deterministic Evaluation Order

Implement the canonical order exactly:

```text
1. validate all input and referenced versions
2. select applicable enabled pack versions
3. surface configured open clarification questions
4. calculate configured missing required information
5. select lowest:
   (pack.order, question.order, pack_id, question_id)
   eligible unanswered question
6. otherwise return CompletionReady
```

Stable sorting must not depend on:

```text
dict insertion from external callers
set iteration
database order
UUID generation
wall clock
randomness
```

---

# 10. Pack Registry Hardening

P7-A created the structural registry.

P7-B must add strict registration/activation validation.

At minimum reject:

```text
duplicate pack_id + version
duplicate question_id + question_version
duplicate question identity across active registered packs when ambiguous
duplicate rule IDs within a pack
missing referenced applicability rule
missing referenced contradiction rule
missing dependency question
dependency cycles
rule-reference cycles
invalid rule arity
invalid rule operands
unsupported answer/validation pairing
duplicate option IDs
duplicate language codes
voice-only active questions
invalid pack ordering metadata
invalid question ordering metadata
unsupported schema version
```

Do not use runtime plugin discovery.

Registration remains explicit and compile-time.

---

# 11. Approval-State Boundary

Current states:

```text
ENGINEERING_APPROVED
CLINICAL_APPROVAL_REQUIRED
APPROVED
```

P7-B must distinguish:

```text
structural registration
runtime activation
```

A structurally valid pack may exist for engineering/tests while still requiring clinical approval.

Production/runtime activation must reject:

```text
CLINICAL_APPROVAL_REQUIRED
```

Do not break the existing ability to construct structural test fixtures.

Do not silently convert:

```text
ENGINEERING_APPROVED -> APPROVED
```

Do not invent clinical approval.

---

# 12. No Production Clinical Content

Do not add a real clinical question pack containing unapproved medical wording or requiredness rules.

Tests may use obvious synthetic fixtures, for example:

```text
synthetic.core
synthetic.complaint
synthetic.specialty
synthetic.ayush
```

Use content keys such as:

```text
synthetic.question.prompt
```

Do not ship production medical thresholds.

Do not add:

```text
red flags
emergency criteria
diagnostic questions with medical interpretation
specialty routing
medication advice
Dashavidha clinical content
Prakriti/Dosha scoring
```

---

# 13. Rule Language

The existing `RuleDefinition` is the canonical source structure.

P7-B must implement a strict safe rule compiler/evaluator.

Supported operators:

```text
EXISTS
EQUALS
IN
AND
OR
NOT
ANSWER_DISPOSITION
HISTORY_AVAILABLE
CONTRADICTION_STATE
```

Do NOT use:

```text
eval()
exec()
dynamic Python expressions
Jinja evaluation
SQL fragments
regex-driven code execution
arbitrary imports
```

All operands must be validated against registered machine IDs.

---

# 14. Rule Semantics Must Be Explicit

Define and test one unambiguous operand grammar.

For example, a strict machine grammar may reference:

```text
question:<question_id>
option:<option_id>
rule:<rule_id>
history:<history_binding_key>
contradiction:<field_key>
disposition:<enum>
state:<enum>
```

This is an example, not a requirement to use those exact prefixes.

Whatever representation is chosen must be:

```text
bounded
closed
validated at registration
deterministic
human-reviewable
non-executable
```

Do not leave operand interpretation as loose convention.

---

# 15. Rule Arity Validation

Each operator must have exact/bounded arity.

Example expectations:

```text
EXISTS                -> one subject
EQUALS                -> subject + configured value
IN                    -> subject + one-or-more configured values
AND                   -> >= 2 rule references
OR                    -> >= 2 rule references
NOT                   -> exactly 1 rule reference
ANSWER_DISPOSITION    -> question + disposition
HISTORY_AVAILABLE     -> exactly one registered history binding
CONTRADICTION_STATE   -> field/rule target + contradiction state
```

If a better strict grammar is chosen, keep the same safety properties.

Invalid arity is a registration error, not runtime false.

---

# 16. No Unresolved Rule References

Registration must fail when:

```text
a question references a missing applicability rule
a contradiction rule references unknown question/binding
AND/OR/NOT references missing rules
a dependency references unknown question
a history rule references an unknown history binding
```

No unresolved reference is tolerated at engine runtime.

---

# 17. Dependency Graph

Validate question dependencies.

Reject:

```text
self-dependency
direct cycle
multi-node cycle
unknown dependency
```

Question dependency order must not override canonical deterministic selection order.

Dependencies only control eligibility/applicability.

---

# 18. Answer Selection

Repeated answers are append-only.

For a question/version, determine the current accepted response deterministically by:

```text
answered_at DESC
answer_id deterministic tie-break
```

Follow the canonical P7 spec.

Do not delete or mutate previous answers.

The engine must validate that referenced answers:

```text
belong to the same intake
reference a registered question
match question_version
match answer_type
match constraints
```

Invalid answer input fails safely.

---

# 19. Answer-vs-Question Validation

P7-B must validate responses against their registered `QuestionDefinition`.

Required checks:

### TEXT

```text
TextValidation min/max
```

### SINGLE_CHOICE

```text
exactly one selected option
option exists in allowed_option_ids
```

### MULTI_CHOICE

```text
all selected options exist
no duplicate selected option IDs
```

### BOOLEAN

```text
bool only
```

### NUMBER

```text
finite Decimal
minimum/maximum
unit behavior per contract
```

### DATE

```text
date within configured bounds
```

### DURATION

```text
finite non-negative value
allowed unit
minimum/maximum
```

### SEVERITY_SCALE

```text
scale_id/version match question validation
value belongs to configured allowed_values
```

No medical interpretation of severity value.

---

# 20. Non-Answer Dispositions

Validate:

```text
UNKNOWN
PREFER_NOT_TO_ANSWER
SKIPPED
```

Rules:

```text
UNKNOWN only if question.allow_unknown
PREFER_NOT_TO_ANSWER only if question.allow_prefer_not_to_answer
SKIPPED only if question is optional/config permits skipping
```

A required question cannot be silently waived unless pack configuration explicitly permits the relevant non-answer behavior.

Do not invent safety-critical exceptions; P9 owns safety policy.

---

# 21. Missing-Information Calculation

Recompute missing information deterministically from:

```text
active packs
applicable questions
current accepted responses
history reuse state
contradictions
```

Use canonical reasons:

```text
REQUIRED_UNANSWERED
CONDITIONAL_UNANSWERED
RECONFIRMATION_REQUIRED
CLARIFICATION_REQUIRED
```

Do not infer medical significance.

Every item must retain:

```text
field/question key
pack ID/version
rule ID
requiredness
resolution state
```

---

# 22. Stable Missing IDs

Equal engine input must produce equal output.

Therefore do NOT create missing-information IDs with random UUID generation during evaluation.

Use a deterministic stable derivation from non-sensitive machine identity, such as:

```text
engine namespace
pack_id
pack_version
question/field key
reason code
rule ID
```

Use a deterministic UUID mechanism or equivalent stable opaque ID compatible with `OpaqueId`.

Do not hash raw patient answer text into IDs.

---

# 23. Clarification Priority

Configured unresolved contradiction clarification has priority before ordinary unanswered questions.

If a contradiction requires clarification and has a configured clarification question:

```text
return ClarificationRequired
```

Stable ordering must be deterministic.

Do not generate clarification wording dynamically.

If no valid configured clarification question exists:

```text
registration/input validation should fail
or return deterministic Incomplete
```

Do not improvise a question.

---

# 24. Contradiction Handling

P7-B may create/recompute contradiction state only from explicitly configured contradiction rules.

It must never:

```text
choose a winning value automatically
delete one side
supersede a patient fact
write patient history
diagnose inconsistency
```

Contradiction output contains references/reason codes only.

No hidden reasoning.

---

# 25. History Context Contract

Create a minimal immutable P7-B history context type.

It should contain only what the engine needs, conceptually:

```text
fact_id
fact_type
verification_state
safe display label/value needed for confirmation
source/provenance marker if required
```

Do not import patient infrastructure.

Prefer either:

```text
a clinical_intake-owned neutral context DTO
```

or imports strictly through stable public exports.

P7-C will adapt `patients.facts.list` output to this engine input.

---

# 26. History Eligibility

Canonical baseline:

```text
REJECTED -> never reusable
SUPERSEDED -> never reusable
```

Other verification states may only suppress a question when explicitly allowed by active approved pack metadata.

Do not invent a global trust ranking.

No hard-coded assumption such as:

```text
CLINICIAN_CONFIRMED always suppresses
PATIENT_CONFIRMED always suppresses
```

unless explicit pack policy says so.

---

# 27. History-Reuse Policy Metadata

P7-A `HistoryBinding` currently identifies:

```text
fact_type
section_key
```

P7-B may extend the pack/question contract with narrowly scoped reuse policy metadata needed to satisfy the canonical spec.

A safe design should express:

```text
which verification states are eligible
whether eligible history may suppress asking
whether confirmation is required
```

Keep it immutable/versioned/closed.

Do not create arbitrary policy dictionaries.

Do not add database columns; this is pack configuration.

---

# 28. Conservative Default

Until an active approved pack explicitly permits suppression:

```text
eligible history may be shown for confirmation
but MUST NOT suppress a required question
```

This is mandatory.

This prevents engineering assumptions from becoming clinical trust policy.

---

# 29. History Confirmation

Reused history is not automatically a patient answer.

If confirmation is required:

```text
history available
-> question/reconfirmation remains required
-> missing reason RECONFIRMATION_REQUIRED where appropriate
```

A separate patient response is needed to mark confirmation.

Do not manufacture a `PATIENT_CONFIRMED` longitudinal fact.

P7-B does not write patient facts.

---

# 30. History Disagreement

If current patient input conflicts with reused history under an explicitly configured contradiction rule:

```text
preserve both references
surface contradiction/clarification
```

Do not overwrite the reused history.

Do not call patient supersession logic.

---

# 31. History Fact-Type Binding

History reuse is allowed only when:

```text
question.history_binding exists
fact_type matches
section binding matches
active pack explicitly supports it
```

Facts from unrelated categories must never suppress or answer another question.

---

# 32. Fact Verification State Input

Use canonical verification-state machine values from the provenance public contract where practical:

```text
EXTRACTED
LOW_CONFIDENCE
NEEDS_CONFIRMATION
PATIENT_CONFIRMED
CLINICIAN_CONFIRMED
REJECTED
SUPERSEDED
```

Do not create a conflicting verification enum inside clinical_intake unless isolation requires a documented adapter.

---

# 33. No Direct Patient Capability Calls in Pure Engine

The engine itself must not call:

```text
patients.read
patients.facts.list
```

P7-C application orchestration will obtain history through public capabilities and pass bounded context into the engine.

This keeps P7-B:

```text
pure
deterministic
offline-testable
zero-I/O
```

---

# 34. Pack Applicability

Pack selection must be deterministic.

Do not auto-activate every registered pack.

The engine should operate on an explicit set of selected/activated pack identities supplied by the caller.

For each requested pack:

```text
identity/version must exist
pack must be structurally valid
pack must be activation-eligible
language compatibility must be checked when language is provided
```

Do not enable AYUSH/specialty packs automatically.

---

# 35. Language Boundary

P7 supports machine language metadata.

Current product session preference may include:

```text
en
hi
```

But no reviewed Hindi clinical content exists.

Pack activation must verify:

```text
requested language is listed in supported_languages
```

Do not machine-translate content.

Do not activate a pack just because session language exists.

---

# 36. Input Mode Boundary

P7 operational input modes:

```text
TEXT
TOUCH
```

`VOICE` is metadata/future capability only.

A question that is only:

```text
VOICE
```

cannot be activated in P7.

A question containing VOICE plus TEXT/TOUCH may remain structurally representable, but P7-B must ensure an operational non-voice mode exists.

---

# 37. Specialty Pack Extensibility

Add tests showing a synthetic:

```text
SPECIALTY
```

pack can be registered and evaluated without changing engine code.

Do not implement a real specialty.

The engine must not use `if specialty == ...` code paths.

---

# 38. Complaint Pack Extensibility

Add tests showing a synthetic:

```text
COMPLAINT
```

pack can be activated through explicit caller-selected pack identity/configuration.

Do not infer complaint type from free text.

No NLP/LLM.

---

# 39. AYUSH Extension

Add tests showing a synthetic:

```text
AYUSH_EXTENSION
```

pack:

```text
registers structurally
uses the same engine
uses same typed answer contracts
does not activate automatically
does not contain production Dashavidha content
```

If approval state is `CLINICAL_APPROVAL_REQUIRED`, runtime activation must fail.

No separate AYUSH engine.

---

# 40. Completion Readiness

Return `CompletionReady` only when:

```text
no unresolved required missing_information
no required contradiction clarification remains
no eligible required unanswered question remains
```

Optional unanswered questions must not block completion unless configuration explicitly says otherwise.

Do not complete the `ClinicalIntake` persistence object here.

P7-B only computes readiness.

P7-C performs lifecycle mutation.

---

# 41. Incomplete Result

Return `Incomplete` when no immediately selectable question exists but configured required information still cannot be resolved.

This protects against:

```text
bad pack dependency state
missing approved confirmation path
unresolved required requirement
```

Do not return false `CompletionReady`.

---

# 42. Deterministic IDs and Time

The engine must not call:

```text
OpaqueId.new()
uuid4()
random.*
datetime.now()
utc_now()
```

during pure evaluation.

If contradiction/missing IDs are produced by engine logic, derive them deterministically.

If an event timestamp is needed, pass it explicitly as input; avoid timestamps entirely in pure decision output where possible.

---

# 43. Immutability

Engine evaluation must not mutate:

```text
ClinicalIntake
QuestionPack
QuestionDefinition
IntakeAnswer
history context
contradiction input
registry
```

Return new immutable result values.

---

# 44. Registry Immutability

After construction, callers must not be able to mutate registry contents.

Current P7-A registry has no public mutation method; preserve/improve this property.

Avoid returning a mutable internal mapping.

---

# 45. Safe Errors

Introduce typed P7-B errors where appropriate, for example:

```text
InvalidQuestionPackError
InvalidRuleDefinitionError
InvalidEngineInputError
InvalidAnswerForQuestionError
PackNotActivationEligibleError
```

Names may vary.

Errors must:

```text
be deterministic
not expose raw sensitive answers
reference machine IDs only where useful
```

No HTTP errors in P7-B.

---

# 46. Boundary Tests

Add AST/runtime guards proving P7-B does not import:

```text
FastAPI
patient infrastructure
encounter infrastructure
session infrastructure
consent infrastructure
network clients
AI gateway
LLM providers
```

No module default runtime registration.

No application/API layer.

---

# 47. Zero-I/O Proof

Tests should be able to instantiate and evaluate the engine using only in-memory immutable objects.

No test should require:

```text
PostgreSQL
Redis
HTTP server
filesystem fixture discovery
internet
model provider
```

P7-A PostgreSQL regression tests still run in CI, but P7-B engine tests themselves are pure.

---

# 48. Repeatability Tests

For identical input evaluate repeatedly, e.g.:

```text
100 iterations
```

Assert exact result equality.

Also prove:

```text
input order perturbation does not change result where ordering is semantically irrelevant
registry construction order does not change canonical selection
answer input ordering does not change newest-answer selection
history input ordering does not change eligibility/result
```

If registry order is semantically represented only by `pack.order`, use that exclusively.

---

# 49. Stable Tie-Break Tests

Create synthetic packs/questions with equal order values.

Verify tie-break exactly:

```text
pack.order
question.order
pack_id
question_id
```

Question/pack tuple order supplied by caller must not change the selected question.

---

# 50. Rule Evaluation Tests

Cover every operator:

```text
EXISTS
EQUALS
IN
AND
OR
NOT
ANSWER_DISPOSITION
HISTORY_AVAILABLE
CONTRADICTION_STATE
```

For each:

```text
true case
false case
invalid registration case
```

No branch may fall back to permissive true on error.

---

# 51. Pack Validation Tests

Cover at minimum:

```text
duplicate pack identity
duplicate question identity
duplicate rule ID
unknown applicability rule
unknown contradiction rule
unknown dependency
self dependency
direct dependency cycle
multi-node dependency cycle
rule cycle
bad rule arity
bad rule operand
unsupported schema_version
voice-only question
clinical-approval-required activation
duplicate language
duplicate option
```

Do not weaken existing P7-A registry tests.

---

# 52. Answer Validation Tests

Cover every answer type and invalid boundary.

At minimum:

```text
text too short/long
unknown choice option
duplicate multi-choice option
number below/above bound
invalid date bound
duration invalid unit
duration outside bounds
severity wrong scale/value
UNKNOWN not allowed
PREFER_NOT_TO_ANSWER not allowed
SKIPPED required question
question version mismatch
answer type mismatch
foreign intake_id
```

Errors must not echo sensitive answer text.

---

# 53. Missing-Information Tests

Prove:

```text
required unanswered -> REQUIRED_UNANSWERED
conditional applicable unanswered -> CONDITIONAL_UNANSWERED
conditional non-applicable -> no missing item
confirmation required -> RECONFIRMATION_REQUIRED
clarification required -> CLARIFICATION_REQUIRED
allowed optional skip -> does not block completion
```

IDs/order must be deterministic.

---

# 54. History-Reuse Tests

Use synthetic history context.

Prove:

```text
REJECTED excluded
SUPERSEDED excluded
unbound fact type excluded
allowed fact type + unapproved suppression policy -> still ask/reconfirm
explicit approved verification allowlist + suppress policy -> question can be reduced
confirmation-required policy -> question remains
history ordering does not affect result
history does not become patient answer automatically
```

No patient module write.

---

# 55. Contradiction Tests

Prove:

```text
open configured contradiction gets clarification priority
resolved contradiction does not block
unrelated contradiction does not affect question
two contradictions use stable deterministic ordering
engine never chooses a winner
```

No medical inference.

---

# 56. Specialty / AYUSH Tests

Prove:

```text
synthetic SPECIALTY pack registers/evaluates
synthetic COMPLAINT pack registers/evaluates
synthetic AYUSH_EXTENSION structurally registers
AYUSH pack requiring approval cannot activate
no engine code change needed per pack kind
```

No clinical content.

---

# 57. No Default Production Pack

Do not register a real production pack in:

```text
create_app
module registry
global singleton
import side effect
```

Tests may create explicit synthetic registries.

P7-C will decide the governed runtime pack composition.

---

# 58. Public Surface

P7-B may export stable pure-engine contracts through:

```text
clinical_intake.public
```

only where P7-C will legitimately consume them.

Do not bind capabilities yet.

`CLINICAL_INTAKE_MANIFEST` may remain structurally declared but must not become part of default application runtime in P7-B.

---

# 59. NextQuestionCapability

Review the existing P7-A placeholder:

```text
NextQuestionCapability
```

If the richer P7-B engine decision type makes the existing protocol too narrow, refine the protocol now in a backward-consistent manner.

Do not create fake application service bindings.

Do not introduce FastAPI.

---

# 60. No Persistence Changes

Expected:

```text
NO new migration
NO table changes
NO ORM column changes
NO Alembic head change
```

Alembic head remains:

```text
p7a_0007
```

P7-B engine state is derived from existing P7-A domain/persistence structures.

If a schema change appears necessary, STOP and report the specification conflict rather than silently adding one.

---

# 61. No Dependency Changes

Expected unchanged:

```text
backend/pyproject.toml
backend/uv.lock
package.json
pnpm-lock.yaml
```

Use Python standard library and existing project code.

Do not add:

```text
rule engines
workflow engines
JSONLogic
Pydantic additions solely for this engine
graph packages
network libraries
AI packages
```

---

# 62. No Frontend Changes

Expected no changes to:

```text
apps/**
packages/ui/**
tests/e2e/**
```

P7-C owns frontend.

---

# 63. No CI Topology Change

Keep exactly six CI jobs:

```text
Backend quality
Frontend quality
Persistence integration
Docker and PostgreSQL
Playwright Chromium
Security scans
```

No seventh job.

No weakening test gates.

Existing migration assertions must remain:

```text
p7a_0007
```

---

# 64. Documentation

Update relevant only:

```text
README.md
backend/README.md
REPOSITORY_TREE.txt
docs/03_REPOSITORY_STRUCTURE.md
docs/07_CLINICAL_INTAKE_SPEC.md only if implementation reveals a genuine non-semantic clarification
docs/implementation/38_PROGRESS_TRACKER.md
docs/codex/CODEX_PHASE_PROMPTS/P7_B_DETERMINISTIC_ADAPTIVE_ENGINE.md
```

Do not rewrite canonical spec to justify implementation shortcuts.

---

# 65. Progress Tracker

Before CI:

```text
P7-A = COMPLETE
P7-B = PARTIAL — REMOTE CI VERIFICATION PENDING
P7-C = NOT STARTED
P7 = PARTIAL
```

After all six CI jobs pass:

```text
P7-A = COMPLETE
P7-B = COMPLETE
P7-C = NOT STARTED
P7 = PARTIAL
recommended next = P7-C — APIs + Patient UI
```

---

# 66. Acceptance Status After P7-B

Expected:

```text
AC-P7-001 PARTIAL
AC-P7-002 PASS
AC-P7-003 PASS
AC-P7-004 PASS
AC-P7-005 PASS
AC-P7-006 PASS
AC-P7-007 PASS
AC-P7-008 PASS
AC-P7-009 PASS
AC-P7-010 PARTIAL
```

Do not mark P7 COMPLETE.

P7-C is still required.

---

# 67. Verification

From backend:

```text
uv lock --check
uv sync --locked --dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m compileall -q app tests
uv run alembic -c alembic.ini heads
uv run alembic -c alembic.ini check
```

Run PostgreSQL regression:

```text
uv run pytest -m postgres
```

From repo root:

```text
python scripts/quality_gate.py backend
python scripts/quality_gate.py frontend
git diff --check
```

Audit:

```text
Alembic head p7a_0007
no migrations changed
no dependency changes
no frontend changes
no API/application layer
no runtime module registration
no network use
no LLM/AI use
no production clinical content
no AYUSH production content
```

---

# 68. Commit / Push

```text
git add <P7-B files only>
git commit -m "feat: implement P7-B deterministic intake engine"
git push -u origin phase/p7-b-deterministic-adaptive-engine
```

Do not merge.

Do not force-push.

---

# 69. Final Report

Return only:

```text
STATUS
BRANCH / GIT
ENGINE
ENGINE RESULT TYPES
DETERMINISM
RULE LANGUAGE
PACK VALIDATION
ANSWER VALIDATION
MISSING INFORMATION
CONTRADICTIONS
HISTORY REUSE
SPECIALTY / COMPLAINT EXTENSIONS
AYUSH EXTENSION
BOUNDARY ENFORCEMENT
FILES CHANGED
DEPENDENCIES
MIGRATION STATUS
TESTS
POSTGRESQL REGRESSION
VERIFICATION
CI
P7 ACCEPTANCE STATUS
DEVIATIONS
BLOCKERS / OPEN DECISIONS
PROGRESS TRACKER
MERGE
RECOMMENDED NEXT UNIT
```

`MERGE`:

```text
MERGE PERFORMED: NO
```

Recommended next:

```text
P7-C — APIs + Patient UI
```

---

# 70. Success Definition

P7-B is complete only when:

- a pure deterministic intake engine exists;
- equal input/version produces exactly equal output;
- no engine path depends on time, randomness, database, network, AI, or filesystem discovery;
- output is one of typed `NextQuestion`, `ClarificationRequired`, `Incomplete`, or `CompletionReady`;
- selection order is exactly deterministic;
- every supported rule operator is strictly validated and evaluated;
- no unsafe expression evaluation exists;
- question-pack registration rejects unresolved/cyclic/invalid structures;
- runtime activation rejects packs still requiring clinical approval;
- repeated answers resolve deterministically;
- answers are validated against their registered question constraints;
- skip/refusal behavior is config-bound;
- missing-information output is deterministic;
- contradiction clarification has configured priority;
- history reuse excludes REJECTED/SUPERSEDED facts;
- no global trust threshold is invented;
- required-question suppression occurs only under explicit approved pack policy;
- reused history is never silently converted to patient confirmation;
- no patient fact is written/superseded;
- specialty and complaint packs work without engine code changes;
- AYUSH extension uses the same engine and contains no production clinical content;
- no migration/schema/dependency/frontend/API/application changes occur;
- Alembic remains `p7a_0007`;
- P7-A lifecycle persistence guard remains green;
- all six CI jobs pass;
- AC-P7-006..009 pass;
- P7-B = COMPLETE;
- P7 remains PARTIAL;
- branch is pushed and not merged.

Stop after P7-B.
