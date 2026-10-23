# Pre-P13 Admin Portal Readiness Review

> **UNAPPROVED REVIEW INVENTORY — DOCUMENTATION ONLY; NOT AN OFFICIAL NUMBERED GATE PROGRAM OR AUTHORIZATION.**

**Evidence baseline:** `main @ af32d98061b4605d405e954de5cde3d380974d8e`
**Review date:** `2026-10-23`
**Decision:** **NOT READY FOR LIVE P13-E OR P21 ADMIN WORK**

This review accompanies the unapproved [Admin Portal Specification](../25_ADMIN_PORTAL_SPEC.md).
It records repository gaps and proposed review evidence. It does not approve roles, sources,
identity, clinical authority, consent, privacy, security, pilot, or production use. The original
eight proposed [P13 readiness gates](P13_READINESS_GATE_REVIEW.md) remain 4 OPEN and 4 BLOCKED;
P21 does not acquire a human-approved gate count from this inventory.

# 1. Repository evidence and gap

As built, `apps/admin-web` is an empty foundation page. P4 provides persisted actors/roles,
provider-neutral authentication contracts, server-side permissions, and an MFA boolean gate for
administrative roles, but production authentication is unconfigured and there is no verified actor
provisioning, role assignment, MFA ceremony, institution/source assignment, or admin API. Consent,
events/outbox, safe-off flags, and operational telemetry are adjacent primitives, not an admin
system. Provider/resource/referral/notification/audit modules, records, moderation, clinical review,
and an audit viewer are absent. Alembic remains `p7a_0007`.

P4 technical role/MFA tests do not establish identity assurance, employment, institutional mandate,
source-verifier authority, clinical authority, or human sign-off. Future schemas/endpoints in
canonical documents are not implemented.

# 2. Proposed review inventory

Every status below is **OPEN** or **BLOCKED** evidence inventory, not an approved gate.

## 2.1 Trusted identity and scoped authorization — BLOCKED

- **Accountable reviewer roles:** identity owner; security; privacy; institution owner; application
  owner; operations.
- **Existing evidence:** deny-by-default P4 permissions, trusted `ActorContext` contract, MFA check
  for current administrative role constants, self-subject guard.
- **Missing decisions/artifacts:** IdP; identity proofing; provisioning/deprovisioning; trusted MFA and
  recovery; role/permission assignments; institution/object/source/assignment scope; service actors;
  session assurance; emergency/break-glass policy; authorization matrix and threat review.
- **Risks/tests:** unauthenticated/non-MFA/disabled access; forged roles/headers; wrong institution,
  object, source, or assignment; guessed IDs; privilege escalation; confused deputy; enumeration;
  service-account impersonation.
- **Safe offline work if separately authorized:** synthetic authorization matrix and deny-path
  contracts only, with no production identity claim.
- **STOP:** any production identity, scope, assignment, MFA, recovery, or accountable authority is
  absent or client-controlled.

## 2.2 Provider/resource provenance and verification — BLOCKED

- **Accountable reviewer roles:** source governance; provider/resource owner; privacy/legal;
  security; clinical safety for critical resources; operations; institution owner.
- **Existing evidence:** accepted registry/validated-integration ADR and unapproved Pre-P13 policy.
- **Missing decisions/artifacts:** real sources and rights; field model; proof; verifier assignment;
  cadence/expiry; correction/dispute/appeal; suspension/revocation propagation; public eligibility;
  critical-contact dual control; outage and incident runbook.
- **Risks/tests:** fake source/contact, malicious URL/redirect, stale/future/expired/revoked proof,
  source poisoning, concurrent verification/revocation, synthetic record in protected mode.
- **Safe offline work if separately authorized:** unmistakably synthetic state diagrams or static
  source-warning component contracts.
- **STOP:** source, rights, verifier, freshness, correction, dual-control, warning, or rollback is
  undecided; no generated contact may substitute.

## 2.3 Maker-checker and governing-domain authority — BLOCKED

- **Accountable reviewer roles:** clinical governance; policy owner; model governance; P15 content
  owner; data governance; security; institution owner.
- **Existing evidence:** immutable versioned synthetic policy/model metadata in earlier safe subsets;
  no live approval workflow.
- **Missing decisions/artifacts:** object/state vocabulary; maker/checker eligibility; independence;
  quorum; effective/expiry dates; conflict/rollback; clinical correction authority; policy/model/
  content release owners; signed decision records.
- **Risks/tests:** self-approval, stale-version approval, ordinary-admin promotion, forged approval,
  concurrent approval/revocation, rollback without provenance.
- **Safe offline work if separately authorized:** synthetic transition contracts that cannot activate
  clinical or production state.
- **STOP:** an ordinary admin can acquire clinical/source/policy/model authority or CI/PR status is
  treated as governed approval.

## 2.4 Referral and notification visibility — BLOCKED

- **Accountable reviewer roles:** referral/notification owners; privacy/legal; consent; identity;
  integration/security; operations; patient experience.
- **Existing evidence:** central purpose-specific consent includes `REFERRAL_SHARING`; no live P13
  referral or notification service.
- **Missing decisions/artifacts:** recipient/status authority; minimized field allowlist; purpose and
  notice; mandatory explicit active sharing consent and other applicable requirements; destination
  binding; provider/channel; webhook verification; idempotency/retry/reconciliation; correction and
  withdrawal effects.
- **Risks/tests:** general-consent substitution, revoked/expired consent, recipient substitution,
  duplicate send, spoofed webhook, fabricated `SENT`/`ACKNOWLEDGED`/`SCHEDULED`/`COMPLETED`, raw
  transcript or lock-screen leakage.
- **Safe offline work if separately authorized:** synthetic unavailable/unknown/failed display states
  with no network, recipient, or side effect.
- **STOP:** external sharing lacks explicit active purpose-specific `REFERRAL_SHARING` consent or any
  additional applicable requirement; status evidence is absent or ambiguous.

## 2.5 Audit, privacy, isolation, and incident response — BLOCKED

- **Accountable reviewer roles:** audit/data governance; privacy/legal; security; records/retention;
  institutional owner; operations/incident response.
- **Existing evidence:** outbox/event primitives and content-minimized logging conventions; no audit
  domain, store, viewer, or retention policy.
- **Missing decisions/artifacts:** closed event schema; integrity/tamper model; access and reviewer
  identity; search/index; export rights; retention/deletion/legal hold/backup; cross-institution
  isolation; subject rights; monitoring; breach/incident procedures; break-glass.
- **Risks/tests:** audit tamper/gap, wrong-tenant read, unauthorized export, CSV formula, timing
  enumeration, raw narrative/document/token/signed-link leakage, deletion/hold conflict.
- **Safe offline work if separately authorized:** synthetic event-shape/privacy tests disconnected
  from live data.
- **STOP:** auditability requires raw sensitive content, tenant isolation is unproven, or retention,
  access, export, incident, or legal decisions are missing.

## 2.6 Admin UI/BFF/API accessibility and honest copy — OPEN

- **Accountable reviewer roles:** admin/patient app owners; API/architecture; accessibility;
  content/localization; privacy/security; source governance.
- **Existing evidence:** empty accessible admin shell and patient-web privacy patterns; no admin
  routes/BFF/API/copy.
- **Missing decisions/artifacts:** navigation and journeys; API/BFF contracts; `no-store`; CSRF and
  session design; source/freshness/uncertainty copy; approved locales; focus/dialog/confirmation;
  mobile reflow; browser-storage design; error/degraded states.
- **Risks/tests:** XSS/malicious link, client-authorized operation, false success, stale state,
  sensitive browser cache, missing locale, inaccessible warnings/dialogs, 320/390px overflow.
- **Safe offline work if separately authorized:** static synthetic unavailable/degraded/source-warning
  component tests only.
- **STOP:** real identity/source/API/authority or approved copy is absent, or UI can conceal a safety
  restriction or claim success without authoritative confirmation.

## 2.7 Operations, safe-off release, and independent fallback — BLOCKED

- **Accountable reviewer roles:** operations/SRE; security; clinical safety; privacy; release/pilot;
  product/institution owner.
- **Existing evidence:** safe-off feature configuration and content-free health primitives; P7 manual
  text/touch path and generic urgent-help navigation remain independent.
- **Missing decisions/artifacts:** SLOs/monitoring; runbooks; alerting; backup/restore; rollback;
  feature ownership; source/IdP outage behavior; staged pilot population/environment; incident and
  residual-risk acceptance; production release and re-review expiry.
- **Risks/tests:** feature-flag bypass, unavailable IdP/source, stale cache, partial deployment,
  rollback failure, false healthy state, admin dependency breaking P7/manual help.
- **Safe offline work if separately authorized:** deterministic safe-off/degraded-state design tests.
- **STOP:** safe-off/rollback/manual fallback, incident ownership, pilot scope, or release approval is
  absent.

# 3. Requirement truth

The draft maps all `FR-ADMIN-001..010`, `FR-AUDIT-001..007`, `AC-P21-001..008`, and applicable
`AC-P13-001..011`. All live acceptance is **NOT VERIFIED**. Creating Spec 25 addresses only the
missing-document item in P13 proposed Gate 7; that gate remains **BLOCKED** pending accountable
review, approved roles/copy/source warnings/privacy/accessibility, production identity, and actual
implementation. P13-A/B/C/D/E and P21-A/B/C/D remain **NOT STARTED**.

# 4. Owner and risk register

| Decision area | Accountable role(s), assignment pending | Principal residual risk |
| --- | --- | --- |
| Identity, MFA, authorization | Identity/security and institution owner | Privilege or cross-scope access |
| Sources and public eligibility | Source governance and provider/resource owner | False, stale, or harmful provider information |
| Clinical/policy/model/content authority | Owning clinical/policy/model/content governance | Ordinary admin creates clinical authority |
| Referral/notification/consent | Privacy/legal, consent and integration owners | Unauthorized disclosure or false delivery state |
| Audit/retention/export | Audit/data governance, privacy/legal, security | Sensitive leakage, tamper, or rights failure |
| UI/accessibility/localization | App, accessibility and content owners | Misleading or inaccessible control/warning |
| Operations/pilot/release | Operations, clinical safety and institution owner | Unsafe activation or failed rollback |

# 5. Unsigned decision-record template

```text
Decision ID:
Area / object / version:
Decision and alternatives:
Scope / institution / source / population / environment:
Evidence reviewed:
Requirements and risks addressed:
Maker name/role/date/signature:                 [PENDING]
Independent checker name/role/date/signature:   [PENDING]
Clinical owner, if applicable:                  [PENDING]
Privacy/legal owner, if applicable:             [PENDING]
Security owner, if applicable:                  [PENDING]
Institution/product owner:                      [PENDING]
Effective date / expiry / re-review trigger:    [PENDING]
Rollback / incident owner:
Residual risk and acceptance:
Outcome: APPROVED / REJECTED / DEFERRED          [UNSIGNED]
```

No field in this template is signed by this work. Technical demos, tests, screenshots, PR review,
and green CI may be attached as engineering evidence but cannot replace accountable approval.

# 6. Preserved governance and final STOP rule

- P13 and P12 runtime remain **NOT STARTED**.
- P11 remains **0/9 approved (5 OPEN, 4 BLOCKED)**.
- P10 live remains **0/9 approved**.
- P8-C/P9-C Stage 3 remain **BLOCKED**.
- P21 remains **NOT STARTED** and has no approved gate count.
- P7 deterministic manual text/touch intake remains the supported path.
- Alembic remains `p7a_0007`; no runtime, schema, API, dependency, UI, infrastructure, or accepted
  ADR change is authorized.

**STOP** before P13-E or P21 implementation until an independently reviewed prompt identifies a
narrow authorized scope and all applicable human decisions above are recorded. A documentation PR
cannot authorize admin operation, source verification, clinical review, patient-data access,
external sharing, policy/model/content promotion, pilot, or production release.
