# SwasthyaSetu AI
## 05 — Database Schema Specification

**Document ID:** `SSAI-DB-005`  
**Filename:** `05_DATABASE_SCHEMA.md`  
**Status:** Foundation / Persistence Contract  
**Version:** `1.0.0-draft`  
**Database:** PostgreSQL  
**ORM:** SQLAlchemy 2.x  
**Migrations:** Alembic

---

# 1. Purpose

This document defines the initial relational persistence design for SwasthyaSetu AI.

Goals:

- preserve module ownership;
- support longitudinal clinical history;
- make provenance explicit;
- avoid one giant patient JSON document;
- support future feature growth without destructive redesign;
- enable FHIR/ABDM mapping;
- keep research data logically isolated from production clinical state.

This is a logical schema specification. Exact SQLAlchemy column declarations and migration files are created incrementally during implementation phases.

---

# 2. Database Principles

- **DB-P-001:** PostgreSQL is the transactional source of truth.
- **DB-P-002:** every table has one owning module.
- **DB-P-003:** modules do not directly write another module's tables.
- **DB-P-004:** every schema change uses Alembic.
- **DB-P-005:** AI/imported clinical facts preserve provenance.
- **DB-P-006:** JSONB is used selectively, not as a substitute for all relational modeling.
- **DB-P-007:** authoritative timestamps are timezone-aware UTC.
- **DB-P-008:** internal primary keys are opaque UUIDs.
- **DB-P-009:** Redis/vector stores are secondary and never sole clinical truth.
- **DB-P-010:** binary medical files live in object storage, not ordinary relational rows.

---

# 3. Schema Strategy

Initial recommendation:

```text
one PostgreSQL database
+
application-enforced module ownership
+
clear table naming
```

Separate PostgreSQL schemas may be introduced later only if they provide concrete value.

---

# 4. Common Column Conventions

Typical mutable table fields:

```text
id UUID PRIMARY KEY
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
version INTEGER ... where optimistic locking matters
```

Soft-delete is not universal. Use domain-specific state.

---

# 5. Identity and Session Tables

## 5.1 `actors`

Owner: `identity`

```text
id UUID PK
actor_type VARCHAR NOT NULL
subject_ref UUID NULL
institution_id UUID NULL
status VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

## 5.2 `actor_roles`

```text
actor_id UUID FK actors(id)
role_code VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
PRIMARY KEY (actor_id, role_code)
```

## 5.3 `sessions`

Owner: `sessions`

```text
id UUID PK
session_type VARCHAR NOT NULL
actor_id UUID NULL
patient_id UUID NULL
language_preference VARCHAR NULL
status VARCHAR NOT NULL
recovery_token_hash TEXT NULL
created_at TIMESTAMPTZ NOT NULL
expires_at TIMESTAMPTZ NOT NULL
closed_at TIMESTAMPTZ NULL
updated_at TIMESTAMPTZ NOT NULL
```

Indexes:

```text
(status, expires_at)
patient_id
actor_id
```

Never store raw recovery tokens.

---

# 6. Consent Tables

## 6.1 `consent_records`

Owner: `consent`

```text
id UUID PK
subject_type VARCHAR NOT NULL
subject_id UUID NOT NULL
actor_id UUID NULL
purpose VARCHAR NOT NULL
scope JSONB NOT NULL
notice_version VARCHAR NOT NULL
status VARCHAR NOT NULL
granted_at TIMESTAMPTZ NOT NULL
revoked_at TIMESTAMPTZ NULL
expires_at TIMESTAMPTZ NULL
metadata JSONB NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Indexes:

```text
(subject_type, subject_id, purpose, status)
actor_id
```

---

# 7. Patient Tables

## 7.1 `patients`

Owner: `patients`

```text
id UUID PK
status VARCHAR NOT NULL
preferred_language VARCHAR NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

## 7.2 `patient_demographics`

```text
patient_id UUID PK/FK patients(id)
date_of_birth DATE NULL
administrative_sex VARCHAR NULL
gender_identity VARCHAR NULL
pregnancy_status VARCHAR NULL
demographics_metadata JSONB NULL
updated_at TIMESTAMPTZ NOT NULL
```

Fields may be refined after privacy review.

## 7.3 `patient_identifiers`

```text
id UUID PK
patient_id UUID FK patients(id)
system VARCHAR NOT NULL
value TEXT NOT NULL
use VARCHAR NULL
verified BOOLEAN NOT NULL DEFAULT FALSE
source VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Candidate uniqueness:

```text
UNIQUE(system, value)
```

subject to final identifier rules.

---

# 8. Encounter Tables

## 8.1 `encounters`

Owner: `encounters`

```text
id UUID PK
patient_id UUID NULL
session_id UUID NOT NULL
encounter_type VARCHAR NOT NULL
status VARCHAR NOT NULL
institution_id UUID NULL
language_context JSONB NULL
started_at TIMESTAMPTZ NOT NULL
completed_at TIMESTAMPTZ NULL
created_by UUID NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
version INTEGER NOT NULL DEFAULT 1
```

Indexes:

```text
patient_id
session_id
(status, started_at DESC)
institution_id
```

---

# 9. Clinical Fact Tables

## 9.1 `clinical_facts`

Owner: `patients` / provenance lifecycle

```text
id UUID PK
patient_id UUID NULL
encounter_id UUID NULL
fact_type VARCHAR NOT NULL
canonical_label TEXT NOT NULL
normalized_code TEXT NULL
coding_system TEXT NULL
effective_at TIMESTAMPTZ NULL
verification_state VARCHAR NOT NULL
structured_value JSONB NOT NULL
source_text TEXT NULL
superseded_by_fact_id UUID NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Indexes:

```text
patient_id
encounter_id
(patient_id, fact_type)
verification_state
effective_at
```

Rules:

- `structured_value` follows type-specific schema;
- model risk does not become a clinical fact of confirmed condition automatically;
- confirmed facts should be superseded rather than silently overwritten.

---

# 10. Clinical Fact Provenance

## 10.1 `clinical_fact_provenance`

Owner: `provenance`

```text
id UUID PK
fact_id UUID FK clinical_facts(id)
source_type VARCHAR NOT NULL
source_id UUID NULL
source_ref TEXT NULL
extractor_type VARCHAR NULL
provider VARCHAR NULL
model_id VARCHAR NULL
model_version VARCHAR NULL
prompt_version VARCHAR NULL
schema_version VARCHAR NULL
confidence NUMERIC NULL
created_by UUID NULL
created_at TIMESTAMPTZ NOT NULL
metadata JSONB NULL
```

Indexes:

```text
fact_id
(source_type, source_id)
(model_id, model_version)
```

Constraint:

```text
confidence IS NULL OR confidence BETWEEN 0 AND 1
```

---

# 11. Frequently Queried Clinical Projections

High-value safety-relevant fact types should have normalized relational projections in addition to canonical fact provenance.

## 11.1 `medications`

```text
id UUID PK
patient_id UUID NOT NULL
source_fact_id UUID NOT NULL
name TEXT NOT NULL
normalized_code TEXT NULL
dose_value NUMERIC NULL
dose_unit TEXT NULL
route TEXT NULL
frequency TEXT NULL
start_date DATE NULL
end_date DATE NULL
status VARCHAR NOT NULL
verification_state VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

## 11.2 `allergies`

```text
id UUID PK
patient_id UUID NOT NULL
source_fact_id UUID NOT NULL
substance TEXT NOT NULL
normalized_code TEXT NULL
reaction TEXT NULL
severity TEXT NULL
status VARCHAR NOT NULL
verification_state VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

## 11.3 `observations`

```text
id UUID PK
patient_id UUID NULL
encounter_id UUID NULL
source_fact_id UUID NULL
observation_type TEXT NOT NULL
value_numeric NUMERIC NULL
value_text TEXT NULL
unit TEXT NULL
normalized_value NUMERIC NULL
normalized_unit TEXT NULL
reference_low NUMERIC NULL
reference_high NUMERIC NULL
abnormal_flag VARCHAR NULL
effective_at TIMESTAMPTZ NULL
verification_state VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

Index:

```text
(patient_id, observation_type, effective_at DESC)
```

Unit-aware interpretation is mandatory.

---

# 12. Clinical Intake Tables

## 12.1 `clinical_intakes`

Owner: `clinical_intake`

```text
id UUID PK
encounter_id UUID UNIQUE NOT NULL
status VARCHAR NOT NULL
chief_complaint JSONB NULL
hpi JSONB NULL
history_sections JSONB NOT NULL DEFAULT '{}'
missing_information JSONB NOT NULL DEFAULT '[]'
contradictions JSONB NOT NULL DEFAULT '[]'
started_at TIMESTAMPTZ NOT NULL
completed_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
version INTEGER NOT NULL DEFAULT 1
```

JSONB is acceptable because this is versioned structured intake state, not unrestricted authoritative truth.

## 12.2 `intake_answers`

```text
id UUID PK
intake_id UUID FK clinical_intakes(id)
question_id VARCHAR NOT NULL
question_version VARCHAR NOT NULL
answer JSONB NOT NULL
source_type VARCHAR NOT NULL
answered_at TIMESTAMPTZ NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

Index:

```text
(intake_id, question_id)
```

## 12.3 `questionnaire_instances`

```text
id UUID PK
encounter_id UUID NOT NULL
questionnaire_id VARCHAR NOT NULL
questionnaire_version VARCHAR NOT NULL
status VARCHAR NOT NULL
responses JSONB NOT NULL
started_at TIMESTAMPTZ NOT NULL
completed_at TIMESTAMPTZ NULL
```

---

# 13. Safety Tables

## 13.1 `safety_decisions`

Owner: `safety`

```text
id UUID PK
encounter_id UUID NOT NULL
route VARCHAR NOT NULL
reason_codes JSONB NOT NULL
policy_id VARCHAR NOT NULL
policy_version VARCHAR NOT NULL
requires_clarification BOOLEAN NOT NULL
blocks_self_care BOOLEAN NOT NULL
input_snapshot_ref TEXT NULL
created_at TIMESTAMPTZ NOT NULL
```

Indexes:

```text
encounter_id
(policy_id, policy_version)
route
```

No hidden chain-of-thought storage.

## 13.2 `policy_versions`

Owner: safety/governance registry

```text
id UUID PK
policy_type VARCHAR NOT NULL
policy_id VARCHAR NOT NULL
version VARCHAR NOT NULL
status VARCHAR NOT NULL
checksum TEXT NOT NULL
effective_from TIMESTAMPTZ NULL
retired_at TIMESTAMPTZ NULL
approval_metadata JSONB NULL
created_at TIMESTAMPTZ NOT NULL
```

Unique:

```text
UNIQUE(policy_id, version)
```

---

# 14. Mental Health Tables

## 14.1 `mental_health_signal_snapshots`

Owner: `mental_health`

```text
id UUID PK
session_id UUID NOT NULL
encounter_id UUID NULL
signal_schema_version VARCHAR NOT NULL
signals JSONB NOT NULL
model_id VARCHAR NULL
model_version VARCHAR NULL
prompt_version VARCHAR NULL
created_at TIMESTAMPTZ NOT NULL
```

Retention may be shorter than route-decision retention.

## 14.2 `mental_health_decisions`

```text
id UUID PK
session_id UUID NOT NULL
encounter_id UUID NULL
route VARCHAR NOT NULL
reason_codes JSONB NOT NULL
policy_version VARCHAR NOT NULL
signal_schema_version VARCHAR NOT NULL
requires_clarification BOOLEAN NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

Indexes:

```text
session_id
route
policy_version
```

---

# 15. Document Tables

## 15.1 `clinical_documents`

Owner: `documents`

```text
id UUID PK
patient_id UUID NULL
encounter_id UUID NULL
document_type VARCHAR NOT NULL
storage_object_key TEXT NOT NULL
original_filename TEXT NULL
mime_type TEXT NOT NULL
size_bytes BIGINT NOT NULL
checksum_sha256 TEXT NOT NULL
status VARCHAR NOT NULL
language VARCHAR NULL
document_date DATE NULL
uploaded_by UUID NULL
uploaded_at TIMESTAMPTZ NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Indexes:

```text
patient_id
encounter_id
checksum_sha256
status
document_date
```

## 15.2 `document_processing_runs`

```text
id UUID PK
document_id UUID NOT NULL
processor_type VARCHAR NOT NULL
processor_version VARCHAR NOT NULL
provider VARCHAR NULL
status VARCHAR NOT NULL
started_at TIMESTAMPTZ NULL
completed_at TIMESTAMPTZ NULL
confidence_summary NUMERIC NULL
error_code VARCHAR NULL
metadata JSONB NULL
created_at TIMESTAMPTZ NOT NULL
```

## 15.3 `document_extractions`

```text
id UUID PK
document_id UUID NOT NULL
processing_run_id UUID NOT NULL
extraction_schema_version VARCHAR NOT NULL
payload JSONB NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

Accepted candidate facts also flow through `clinical_facts` + provenance.

---

# 16. Clinical Summary Tables

## 16.1 `clinical_summaries`

Owner: `summaries`

```text
id UUID PK
encounter_id UUID NOT NULL
version INTEGER NOT NULL
status VARCHAR NOT NULL
sections JSONB NOT NULL
generated_from_fact_ids JSONB NOT NULL
generated_by_type VARCHAR NOT NULL
generated_by_ref TEXT NULL
confirmed_by UUID NULL
confirmed_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Unique:

```text
UNIQUE(encounter_id, version)
```

---

# 17. Self-Care Tables

## 17.1 `self_care_guidance`

Owner: `self_care`

```text
id UUID PK
guidance_key VARCHAR NOT NULL
version VARCHAR NOT NULL
title TEXT NOT NULL
eligible_context JSONB NOT NULL
supportive_actions JSONB NOT NULL
contraindications JSONB NOT NULL
medication_conflicts JSONB NOT NULL
age_rules JSONB NULL
pregnancy_rules JSONB NULL
duration_limit JSONB NULL
escalation_conditions JSONB NOT NULL
source JSONB NOT NULL
review_status VARCHAR NOT NULL
verified_at TIMESTAMPTZ NULL
expires_at TIMESTAMPTZ NULL
translations JSONB NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Unique:

```text
UNIQUE(guidance_key, version)
```

## 17.2 `self_care_decisions`

```text
id UUID PK
patient_id UUID NULL
encounter_id UUID NOT NULL
eligible BOOLEAN NOT NULL
reason_codes JSONB NOT NULL
policy_version VARCHAR NOT NULL
matched_guidance_ids JSONB NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

---

# 18. Provider and Resource Tables

## 18.1 `providers`

Owner: `providers`

```text
id UUID PK
display_name TEXT NOT NULL
provider_type VARCHAR NOT NULL
specialties JSONB NOT NULL
qualifications JSONB NULL
registration_metadata JSONB NULL
facility_id UUID NULL
location JSONB NULL
languages JSONB NOT NULL
teleconsultation_available BOOLEAN NULL
hours JSONB NULL
source JSONB NOT NULL
verified_at TIMESTAMPTZ NULL
expires_at TIMESTAMPTZ NULL
status VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

## 18.2 `provider_contacts`

```text
id UUID PK
provider_id UUID NOT NULL
contact_type VARCHAR NOT NULL
value TEXT NOT NULL
is_primary BOOLEAN NOT NULL DEFAULT FALSE
verified BOOLEAN NOT NULL DEFAULT FALSE
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

## 18.3 `facilities`

```text
id UUID PK
name TEXT NOT NULL
facility_type VARCHAR NOT NULL
location JSONB NULL
hours JSONB NULL
source JSONB NOT NULL
verified_at TIMESTAMPTZ NULL
status VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

## 18.4 `resources`

Owner: `resources`

```text
id UUID PK
resource_type VARCHAR NOT NULL
display_label TEXT NOT NULL
geography JSONB NULL
languages JSONB NOT NULL
hours JSONB NULL
eligibility JSONB NULL
institution_id UUID NULL
source JSONB NOT NULL
verified_at TIMESTAMPTZ NULL
expires_at TIMESTAMPTZ NULL
approval_status VARCHAR NOT NULL
version VARCHAR NOT NULL
status VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

## 18.5 `resource_contacts`

```text
id UUID PK
resource_id UUID NOT NULL
contact_type VARCHAR NOT NULL
value TEXT NOT NULL
is_primary BOOLEAN NOT NULL DEFAULT FALSE
verified BOOLEAN NOT NULL DEFAULT FALSE
```

---

# 19. Provider Routing Decisions

## 19.1 `provider_routing_decisions`

```text
id UUID PK
encounter_id UUID NOT NULL
care_category VARCHAR NOT NULL
specialty_or_service_type VARCHAR NOT NULL
reason_codes JSONB NOT NULL
policy_version VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
```

Provider contacts are not stored in the routing decision itself.

---

# 20. Referral Tables

## 20.1 `referrals`

Owner: `referrals`

```text
id UUID PK
patient_id UUID NULL
session_id UUID NULL
encounter_id UUID NULL
destination_type VARCHAR NOT NULL
destination_id UUID NOT NULL
priority VARCHAR NOT NULL
reason_codes JSONB NOT NULL
consent_id UUID NOT NULL
status VARCHAR NOT NULL
external_reference TEXT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
version INTEGER NOT NULL DEFAULT 1
```

Indexes:

```text
patient_id
session_id
encounter_id
status
destination_id
```

## 20.2 `referral_status_history`

```text
id UUID PK
referral_id UUID NOT NULL
from_status VARCHAR NULL
to_status VARCHAR NOT NULL
reason_code VARCHAR NULL
actor_id UUID NULL
external_event_ref TEXT NULL
created_at TIMESTAMPTZ NOT NULL
```

## 20.3 `referral_delivery_attempts`

```text
id UUID PK
referral_id UUID NOT NULL
adapter_type VARCHAR NOT NULL
idempotency_key VARCHAR NOT NULL
attempt_number INTEGER NOT NULL
status VARCHAR NOT NULL
error_code VARCHAR NULL
started_at TIMESTAMPTZ NOT NULL
completed_at TIMESTAMPTZ NULL
```

Unique:

```text
UNIQUE(adapter_type, idempotency_key)
```

---

# 21. Notification Tables

## 21.1 `notification_intents`

Owner: `notifications`

```text
id UUID PK
subject_type VARCHAR NOT NULL
subject_id UUID NOT NULL
channel VARCHAR NOT NULL
template_id VARCHAR NOT NULL
template_version VARCHAR NOT NULL
safe_variables JSONB NOT NULL
status VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

## 21.2 `notification_attempts`

```text
id UUID PK
notification_id UUID NOT NULL
provider VARCHAR NOT NULL
attempt_number INTEGER NOT NULL
status VARCHAR NOT NULL
error_code VARCHAR NULL
created_at TIMESTAMPTZ NOT NULL
```

---

# 22. Model Registry and Risk Tables

## 22.1 `model_registry`

Owner: production model gateway / research governance

```text
id UUID PK
model_id VARCHAR NOT NULL
model_version VARCHAR NOT NULL
task VARCHAR NOT NULL
framework VARCHAR NOT NULL
artifact_ref TEXT NOT NULL
artifact_checksum TEXT NULL
input_schema_version VARCHAR NOT NULL
output_schema_version VARCHAR NOT NULL
training_dataset_ref TEXT NULL
metrics JSONB NOT NULL
calibration_ref TEXT NULL
approval_status VARCHAR NOT NULL
created_at TIMESTAMPTZ NOT NULL
promoted_at TIMESTAMPTZ NULL
retired_at TIMESTAMPTZ NULL
```

Unique:

```text
UNIQUE(model_id, model_version)
```

## 22.2 `risk_assessments`

```text
id UUID PK
patient_id UUID NULL
encounter_id UUID NULL
task VARCHAR NOT NULL
model_id VARCHAR NOT NULL
model_version VARCHAR NOT NULL
input_schema_version VARCHAR NOT NULL
risk_probability NUMERIC NULL
risk_band VARCHAR NULL
calibration_version VARCHAR NULL
input_quality VARCHAR NOT NULL
explanation_ref TEXT NULL
created_at TIMESTAMPTZ NOT NULL
```

Constraint:

```text
risk_probability IS NULL OR risk_probability BETWEEN 0 AND 1
```

---

# 23. Research Tables

## 23.1 `experiment_runs`

Owner: research/ML

```text
id UUID PK
run_id VARCHAR UNIQUE NOT NULL
task VARCHAR NOT NULL
dataset_version VARCHAR NOT NULL
code_version VARCHAR NOT NULL
parameters JSONB NOT NULL
seed BIGINT NULL
metrics JSONB NOT NULL
environment JSONB NOT NULL
status VARCHAR NOT NULL
started_at TIMESTAMPTZ NOT NULL
completed_at TIMESTAMPTZ NULL
```

Large artifacts belong in artifact storage, not PostgreSQL.

---

# 24. Interoperability Tables

## 24.1 `fhir_exchange_records`

Owner: `interoperability`

```text
id UUID PK
direction VARCHAR NOT NULL
external_system VARCHAR NOT NULL
resource_types JSONB NOT NULL
bundle_ref TEXT NULL
status VARCHAR NOT NULL
error_code VARCHAR NULL
created_at TIMESTAMPTZ NOT NULL
completed_at TIMESTAMPTZ NULL
metadata JSONB NULL
```

## 24.2 `abdm_exchange_records`

Detailed fields are deferred to the approved ABDM spec.

Minimum generic shape:

```text
id UUID PK
consent_id UUID NULL
external_transaction_ref TEXT NULL
status VARCHAR NOT NULL
error_code VARCHAR NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
metadata JSONB NULL
```

---

# 25. Audit Table

## 25.1 `audit_events`

Owner: `audit`

```text
id UUID PK
actor_id UUID NULL
action VARCHAR NOT NULL
object_type VARCHAR NOT NULL
object_id UUID NULL
outcome VARCHAR NOT NULL
request_id VARCHAR NULL
metadata JSONB NULL
created_at TIMESTAMPTZ NOT NULL
```

Indexes:

```text
created_at
actor_id
(object_type, object_id)
action
```

No raw transcript/body by default.

---

# 26. Event / Outbox Table

## 26.1 `outbox_events`

Owner: platform event infrastructure

```text
id UUID PK
event_type VARCHAR NOT NULL
event_version INTEGER NOT NULL
aggregate_type VARCHAR NULL
aggregate_id UUID NULL
correlation_id VARCHAR NULL
causation_id VARCHAR NULL
payload JSONB NOT NULL
status VARCHAR NOT NULL
attempt_count INTEGER NOT NULL DEFAULT 0
available_at TIMESTAMPTZ NOT NULL
dispatched_at TIMESTAMPTZ NULL
last_error_code VARCHAR NULL
created_at TIMESTAMPTZ NOT NULL
```

Indexes:

```text
(status, available_at)
event_type
aggregate_id
```

---

# 27. Background Job Table

If the chosen job infrastructure persists state in PostgreSQL:

## 27.1 `jobs`

```text
id UUID PK
job_type VARCHAR NOT NULL
payload JSONB NOT NULL
status VARCHAR NOT NULL
attempt_count INTEGER NOT NULL DEFAULT 0
scheduled_at TIMESTAMPTZ NOT NULL
started_at TIMESTAMPTZ NULL
completed_at TIMESTAMPTZ NULL
error_code VARCHAR NULL
correlation_id VARCHAR NULL
created_at TIMESTAMPTZ NOT NULL
```

If an external queue owns job state, persist only business-relevant metadata locally.

---

# 28. Feature Flag Table

## 28.1 `feature_flags`

Owner: `feature_management`

```text
id UUID PK
feature_key VARCHAR UNIQUE NOT NULL
enabled BOOLEAN NOT NULL
environment VARCHAR NULL
institution_id UUID NULL
configuration JSONB NULL
owner VARCHAR NULL
review_at TIMESTAMPTZ NULL
created_at TIMESTAMPTZ NOT NULL
updated_at TIMESTAMPTZ NOT NULL
```

Feature flags do not replace authorization.

---

# 29. Patient Timeline Projection

Optional rebuildable read model:

## 29.1 `patient_timeline_entries`

```text
id UUID PK
patient_id UUID NOT NULL
entry_type VARCHAR NOT NULL
occurred_at TIMESTAMPTZ NOT NULL
source_type VARCHAR NOT NULL
source_id UUID NOT NULL
display_summary JSONB NOT NULL
verification_state VARCHAR NULL
created_at TIMESTAMPTZ NOT NULL
```

Candidate uniqueness:

```text
UNIQUE(source_type, source_id, entry_type)
```

---

# 30. Retention Metadata

Retention is domain-specific.

Where justified, use:

```text
retention_class
purge_after
legal_hold
```

Do not blindly add these to every table before privacy policy is finalized.

---

# 31. Encryption

Infrastructure handles database encryption at rest.

Field-level encryption may be added later for selected direct identifiers through `27_SECURITY_ARCHITECTURE.md`.

Do not implement custom cryptography.

---

# 32. Indexing Strategy

Index based on actual access patterns.

Likely early indexes:

```text
session status/expiry
patient and encounter foreign keys
clinical fact type/state
document status/checksum
provider/resource status/expiry
referral status
timeline patient/date
outbox status/available_at
```

Do not index every JSONB field by default.

---

# 33. JSONB Rules

Use JSONB for:

- versioned structured intake sections;
- reason-code arrays;
- policy/config metadata;
- research metrics;
- source metadata;
- language variants.

Do not use JSONB to avoid modeling core relational ownership.

---

# 34. Foreign Keys

Use foreign keys where lifecycle is clear.

Cross-module FKs may exist physically, but write ownership remains with the owning module.

Avoid broad `ON DELETE CASCADE` for clinical/audit records without domain review.

---

# 35. Optimistic Concurrency

Consider version columns for:

```text
encounters
referrals
policy activation
resource verification
clinician confirmation workflows
```

Exact implementation is phase-specific.

---

# 36. Search / Vector Storage

pgvector may later support approved retrieval.

Possible derived table:

```text
document_embeddings
```

Fields could include:

```text
source_type
source_id
chunk_id
embedding
embedding_model
embedding_version
authorization_scope
```

Vector index remains derived, not authoritative clinical truth.

---

# 37. Migration Sequence Guidance

Approximate order:

```text
0001 platform/outbox foundation
0002 identity/sessions/consent
0003 patients/encounters
0004 clinical facts/provenance
0005 intake
0006 safety
0007 summaries
0008 documents
0009 providers/resources/referrals
...
```

Do not pre-generate migration numbers before implementation state exists.

---

# 38. Migration Safety

- prefer additive changes;
- backfill before destructive removal;
- separate large data backfills from DDL when needed;
- inspect autogenerated migrations;
- test clean DB -> head;
- avoid unexpected multiple heads.

---

# 39. Production Data Prohibitions

Do not commit/seed as production truth:

- real patient data;
- unverified provider/crisis contacts;
- unapproved self-care/remedy content;
- clinical thresholds invented by engineering.

Synthetic development data must be explicitly labeled.

---

# 40. Database Completion Criteria

This design is ready for P3–P5 when:

```text
[ ] module ownership is explicit
[ ] patient/encounter/provenance persistence is defined
[ ] safety/referral/model outputs are separated from diagnosis
[ ] outbox/event persistence exists
[ ] binary documents remain in object storage
[ ] research metadata is separated
[ ] future modules can extend without patient-table explosion
```
