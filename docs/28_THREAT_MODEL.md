# SwasthyaSetu AI

## 28 — Threat Model

> **DRAFT — P11 THREAT MODEL ONLY; NO COMPLETE PLATFORM THREAT MODEL; NOT SECURITY SIGN-OFF.**

**Document ID:** `SSAI-TM-028-P11-DRAFT`

**Evidence baseline:** `main @ 2b2d9036c7fe9941bc90bb55d4130dabb6571263`

**Review state:** **DRAFT — HUMAN REVIEW REQUIRED**

**Method:** STRIDE-style design review; no live penetration test and no patient bytes

This draft describes risks and proposed mitigations for future P11 document handling. A proposed
control is not a mitigated risk. No row records security acceptance, production suitability, or a
human risk decision.

## 1. Scope, assumptions, and current truth

In scope: future upload/finalize, quarantine/scan, private object storage, PostgreSQL document
metadata, jobs/outbox, parser/OCR, detached unconfirmed candidates, provenance, and source
read/preview. Cross-phase P8-C/P9-C/P10 authority boundaries are included only where P11 might bypass
them. Other platform threats require the later platform-wide threat model.

Current repository truth: only synthetic P11 contracts and tests exist. There is no document route,
table, migration, upload, storage binding, scanner, durable document worker, production OCR,
medical extraction, source viewer, or live clinician workflow. No test in this document was run
against a live P11 system.

Assumptions for review, not approvals:

- Internet clients and uploaded bytes are hostile.
- IDs and checksums can be guessed or observed; opacity is not authorization.
- Browser, BFF, API, worker, storage, database, provider, CI, support, and backup planes can each be
  compromised independently.
- At-least-once delivery, crash/retry, clock skew, stale UI, delayed revocation, and partial external
  failure are normal fault conditions.
- OCR/parser output and document text can be malicious, wrong, incomplete, or prompt-injecting.
- Insiders and service accounts may abuse valid credentials.
- The current P7 manual intake path must survive P11 failure.

## 2. Actors, assets, and attacker capabilities

Actors requiring distinct authority are patient, pseudonymous session, caregiver, kiosk, clinician,
administrator, institution, worker, and system. Caregiver/kiosk/live clinician document authority is
absent. Authentication, role, assignment, institution, consent, ownership, source access, and
clinical approval are separate decisions.

Assets include original/derived files; quarantine/release decisions; metadata and hashes; patient,
encounter, institution, assignment and consent state; object keys and signed grants; job/attempt and
outbox records; OCR text/candidates; provenance; secrets/keys; logs/traces/metrics/audit; backups;
policy/config/model artifacts; and the availability of manual intake.

Attackers may submit crafted bytes and metadata, replay or race requests, enumerate identifiers,
exploit parser/rendering/provider behavior, exhaust resources, steal a token/grant, compromise a
dependency/model/CI artifact, misuse a service identity, influence support tooling, or exploit
restore/incident gaps. This model assumes no trust in client-supplied role, MIME, filename, checksum,
consent, ownership, status, or source permission.

## 3. Future data-flow diagram and trust boundaries

```text
 TB-01                         TB-02
[Browser] --same-origin--> [BFF — FUTURE] --server bearer--> [Document API — FUTURE]
                                                                |          |
                    TB-03                                       |          | TB-05
       [Quarantine + scanner — FUTURE] <-------------------------+          v
                    | TB-04                                      [PostgreSQL/outbox — FUTURE]
                    v                                                       |
       [Private object storage — FUTURE]                                    | TB-06
                    ^                                                       v
                    +---------------- [Durable document worker — FUTURE] <---+
                                              | TB-07
                                              v
                                [Parser/OCR provider — FUTURE]
                                              |
                                              v
                       [Unconfirmed candidates/provenance — FUTURE]
                                              |
                                      TB-08 fresh access
                                              v
                           [Source read/preview UI — FUTURE]

 TB-09: production processing <-> external provider/network, if separately approved
 TB-10: production data <-> support/audit/backup/restore planes
 TB-11: source repository/CI/artifacts <-> deployed services and models
```

`FUTURE` means absent from the baseline. Existing P6/P7 BFF protections, generic object-storage port,
outbox, process-local job primitives, and synthetic P11 contracts are not a live document pipeline.

## 4. Proposed risk rubric — not accepted

**PROPOSED FOR REVIEW, NOT ACCEPTED:** likelihood and impact may each be rated 1–5 by accountable
security/privacy/clinical/operations owners for a specific deployment. Proposed priority is
`likelihood × impact`: 1–4 low, 5–9 moderate, 10–16 high, 17–25 critical. Health/privacy impact,
irreversibility, detection delay, affected population, and fallback availability must be recorded
separately. Engineering must not fill deployment scores without the owners and facts.

Residual risk below is qualitative and means risk remaining if the proposed control were correctly
implemented. Every value still requires human acceptance or further treatment.

## 5. STRIDE-style threat register

| ID / STRIDE | Asset / boundary | Attack precondition and impact | Existing evidence | Proposed unapproved mitigation | Accountable human | Gate | Negative test | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `P11-T-001` S/I/E | Patient/encounter/source, TB-02/08 | Guessed ID or captured link reaches another subject; PHI disclosure or mutation | P4–P7 object checks; no document route | Fresh exact subject/encounter/source authorization and common nonenumerating denial | Identity/security; privacy; app architecture | 1, 8, 9 | Cross-owner guessed UUID/status/source attempts show no existence/timing/count difference | Moderate: authorization defects remain possible |
| `P11-T-002` S/E | Institution and assignment, TB-02/08 | Valid clinician role lacks current assignment or belongs elsewhere; unauthorized access | Permission constants only; no trusted clinician provider/assignment | Trusted actor, institution membership, exact current assignment, revocation and MFA where required | Identity/security; institution; clinical governance | 1, 8 | Wrong institution, role-only, transferred/revoked/disabled actor, stale tab | High until P10 authority exists |
| `P11-T-003` S/E | Consent/purpose, TB-02/06/08 | Existing general intake consent is reused for upload/OCR/share; unlawful processing | Central consent exists; P11 purpose absent | Dedicated approved purpose/scope/notice; recheck before each read/write/work stage | Privacy/legal; product/institution | 1, 9 | Missing/wrong/withdrawn scope during upload, queue, process and preview | High: policy and in-flight decisions pending |
| `P11-T-004` I/D/E | Upload bytes, TB-01/03 | Forged extension/MIME or polyglot reaches parser; code execution or integrity loss | No upload boundary | Stream limits, signature allowlist, mismatch/polyglot/executable/archive rejection | Security engineering; operations | 2 | Spoofed MIME, polyglot, executable/archive, truncated stream | Moderate after independent parser testing |
| `P11-T-005` I/E | PDF/image parser, TB-03/07/08 | Active PDF, JavaScript, launch action, form, link, attachment or embedded URL triggers XSS/SSRF/execution | Research recommendations only | Sandbox with no egress; disable active content; sanitized isolated preview and strict CSP | Security engineering | 2, 8, 9 | PDF JS/actions/forms/attachments/external URL, XSS and SSRF fixtures | High: parser/renderer zero-days |
| `P11-T-006` D | API/scanner/parser resources, TB-01/03/07 | Decompression, page, pixel, nesting or runtime bomb exhausts CPU/memory/disk | Benchmark plan has synthetic hostile cases | Actual-stream and decoded resource quotas, cancellation, sandbox cgroups/limits and rate controls | Security; operations; product | 2, 9 | Boundary+1, decompression/image/page/object/font/nesting bombs, concurrent flood | Moderate: capacity and limit values pending |
| `P11-T-007` T/I/E | Quarantine/release, TB-03/04 | Malware, scanner outage or stale signatures permit release; quarantine escape infects downstream | No scanner/quarantine | Fail closed on scan failure; immutable release bound to hash/generation; restricted quarantine identity | Security; operations | 2, 9 | Malware detected, scanner timeout/unavailable/stale, release tamper and quarantine escape | High: scanner and response policy undecided |
| `P11-T-008` S/T/R | Upload intent, TB-01/03 | Presigned intent stolen/replayed or used for another object/owner | Upload pattern undecided | Short expiry, single purpose/object/audience, nonce, owner binding and authoritative finalize | Architecture; security | 1–4 | Theft/replay, wrong audience/key, expiry, repeated finalize | Moderate; Pattern B-specific |
| `P11-T-009` T/R | Object generation, TB-03/04/05 | Object replaced between scan/finalize/read; ambiguous finalize binds wrong bytes | No live object workflow | Immutable generation and server hash; conditional operations; scan/release/finalize bind same version | Security; data architecture | 2–4 | TOCTOU replacement, checksum mismatch, delayed write, ambiguous response recovery | Moderate |
| `P11-T-010` T/R/D | DB/object/outbox, TB-04/05/06 | Partial success leaves orphan, false status, missing event or unrecoverable object | Generic transaction-scoped outbox only | State machine, atomic DB+outbox, compensation, reconciliation and honest result | Data/application architecture; operations | 4, 9 | Object succeeds/DB fails and inverse; outbox/enqueue failure; crash each boundary | Moderate: distributed atomicity remains imperfect |
| `P11-T-011` T/R/E | Idempotency/checksum, TB-02/05 | Cross-owner checksum query leaks existence; key replay mutates another request | Synthetic owner-scoped comparator only | Owner/actor-scoped key + request fingerprint + uniqueness; no global digest lookup | Data architecture; privacy | 1, 4 | Same key/different content, cross-owner digest, timing/count probing | Low–moderate after verified nonenumeration |
| `P11-T-012` T/R | Attempt/result, TB-05/06/07 | Duplicate delivery or stale attempt commits over new generation | Synthetic immutable attempt contracts; no persistence | Generation/version checks at claim/read/commit; idempotent handler; discard late results | Application architecture; operations | 4, 9 | Duplicate job, concurrent reprocess, stale config/result and reordered completion | Moderate under at-least-once execution |
| `P11-T-013` T/D | Revocation/deletion, TB-02/04/06/08 | Withdraw/delete/assignment revoke races queued/running/preview work; late disclosure | No live workflow | Fresh authority at every boundary; cancellation; tombstone/generation; late-result discard | Privacy; data governance; architecture | 1, 3, 4, 8 | Revoke/delete during upload, scan, queue, processing, result write and preview | High until policy defines in-flight behavior |
| `P11-T-014` D/R | Worker recovery, TB-06/07 | Worker crash, lease expiry, poison input or retry storm causes stuck/duplicate processing | Current queue volatile/process-local | Durable claim/lease/heartbeat, bounded attempts/deadline/backoff, poison isolation and kill switch | Operations; architecture | 4, 9 | Crash before/after side effect, lease expiry, poison job, quota exhaustion | Moderate; durable backend undecided |
| `P11-T-015` I/D | Source accessibility, TB-04/08 | Missing/quarantined/corrupt object is shown as valid or blocks safe workflow | No source viewer; P7 fallback exists | Honest unavailable state, integrity recheck, no fabricated source, manual fallback | Security; product; accessibility | 3, 8 | Deleted/corrupt/quarantined/inaccessible source and storage outage | Low for safety if manual path preserved; availability remains |
| `P11-T-016` I/E | Private storage/IAM, TB-04/10 | Bucket public, wrong tenant, worker over-privileged or key compromised; mass disclosure | Local adapter only and non-production | Deny-public, least privilege, tenant/institution isolation, key custody/rotation and access alerting | Infrastructure; security; institution | 3, 9 | Public listing/read, wrong tenant, worker escalation, key rotation/recovery | High residual blast radius requires explicit acceptance |
| `P11-T-017` I/R | Region/processor, TB-04/09/10 | Data stored/processed in unapproved region or retained by processor | No provider selected | Deployment allowlist, DPA/subprocessor/region verification, egress controls and audit | Privacy/legal; infrastructure | 3, 5, 9 | Wrong endpoint/region, blocked egress, retention/training config drift | High until contractual/technical evidence exists |
| `P11-T-018` I/R | Preview grant/browser, TB-01/08 | Signed URL replay, referrer/history/cache/service-worker leakage exposes source | No source viewer | Short-lived scoped revocable grants or server stream; no-store; isolated origin/CSP; no browser persistence | Security; privacy; frontend | 3, 8, 9 | Replay, wrong object/version/audience, expired/revoked grant, cache/referrer/history/storage scans | Moderate: screenshots/user downloads require policy |
| `P11-T-019` I | Logs/traces/analytics/support, TB-01/02/09/10 | Raw file/OCR/IDs/tokens leak through errors, BFF upstream body, tracing or support tools | Privacy-safe logging/BFF baseline | Strict allowlists, redaction, content-free errors, access-controlled audit and leakage tests | Security; privacy; operations | 9 | Sentinel content/token/source refs absent from all telemetry and error channels | Moderate: third-party tooling/config drift |
| `P11-T-020` T/E | OCR/LLM instructions, TB-07/09 | Document text instructs model/system or forges role/policy; clinical/safety bypass | Prompt-injection rule; strict synthetic contracts | Treat content as data; isolated task/schema; no tool/policy authority; deterministic gates remain authoritative | AI/document security; clinical governance | 5, 7, 9 | Instruction-like OCR text, tool/policy claims, malicious markup, provider raw fields | High for novel attacks; no live activation before validation |
| `P11-T-021` T/R | Provenance/candidate, TB-07/08 | Forged page/block/version or detached candidate presented as evidence/truth | Text-blind structural match, unconfirmed state, P5 guard | Exact source/object/attempt/model/schema lineage plus fresh source permission and separate review | Data architecture; clinical governance | 6–8 | Mismatched IDs/box/version, failed page, stale source, unsupported field | Moderate; semantic truth still requires humans |
| `P11-T-022` E | P8/P9/P10/P5 authority | P11 output activates real AI/safety, signed summary, or overwrites confirmed fact | Cross-phase gates blocked; P5 supersession guard | Compile-time isolation; no direct cross-module ORM writes; governed review transaction only | Clinical governance; architecture | 7–9 | P11 candidate cannot create P5 confirmed fact, P9 route, P10 confirmation or self-care | Low if boundaries stay explicit; high if later integrations regress |
| `P11-T-023` R/I/E | Admin/support/service account, TB-04/06/08/10 | Insider uses valid privilege to browse or alter data without purpose | No P11 production identities/audit | Least privilege, separation of duties, just-in-time access, reason/MFA, immutable minimized audit and review | Institution; security; data governance | 3, 8, 9 | Admin without source scope, support query, bulk export, audit tamper | High residual insider risk; human acceptance required |
| `P11-T-024` T/E | Dependency/model/CI, TB-11 | Compromised package, model, image, action or artifact executes/leaks data | Locked dependencies and six CI jobs; no OCR runtime dependency | Narrow profiles, pin/hash/sign, SBOM, provenance, vulnerability review, isolated build/deploy and rollback | Security; document-AI; operations | 5, 9 | Tampered hash/signature, unapproved dependency/import, compromised config and rollback | Moderate–high supply-chain residual risk |
| `P11-T-025` R/I | Retention/backup/restore, TB-04/05/10 | Deleted data returns after restore or legal hold/purge is misapplied | No P11 retention policy | Tombstone/retention metadata, backup deletion process, restore reconciliation and legal-hold controls | Data governance; privacy/legal; operations | 3, 9 | Purge partial failure, restore resurrection, expired hold, orphan derived data | High until policy and restore drills exist |
| `P11-T-026` D/R | Incident/rollback/kill switch, all | Detection or rollback fails; compromised path remains active or manual intake is lost | Generic CI/telemetry primitives; P7 manual path | P11-specific monitoring, incident playbook, independent kill switches, credential rotation and rehearsed rollback | Security; operations; product/institution | 9 | Simulated compromise/outage, alert failure, kill switch, rollback and fallback drill | High until operational evidence exists |

## 6. Prioritized adversarial and negative-test matrix

Priority is proposed for review, not a risk acceptance decision.

| Priority | Test family | Required cases | Required safe evidence |
| --- | --- | --- | --- |
| P0 | Authorization/nonenumeration | Anonymous/expired session; wrong patient/encounter/institution; role without assignment; revoked actor/consent; guessed ID; cross-owner digest | One content-free policy; no status/count/timing/existence leak; no object or metadata read |
| P0 | Hostile upload/quarantine | Oversize actual stream; mismatch/polyglot/executable/archive; malformed/truncated; bombs; active PDF; malware; scanner outage; escape | Rejected or quarantined before downstream read; bounded resources; cleanup; safe error |
| P0 | Transaction/race | Object/DB/outbox/enqueue failures; repeated/ambiguous finalize; replace/TOCTOU; concurrent delete/reprocess; stale/late result | No false success or partial authoritative state; deterministic reconciliation; no stale commit |
| P0 | Source/preview privacy | Wrong source/object/version/audience; expired/revoked grant; active content; cache/referrer/history/service worker; raw BFF error | Fresh authorization; no bytes; no replay; no browser/telemetry persistence; isolated rendering |
| P0 | Clinical authority isolation | Injection-like text; forged provenance; failed/partial OCR; low confidence; missing unit/date/negation; lower-trust overwrite | No confirmed fact, diagnosis, route, signed summary, self-care or invented value |
| P1 | Worker resilience | Duplicate delivery; crash/lease expiry; poison input; timeout; quota exhaustion; cancellation | Idempotent bounded result, recovery/dead-letter visibility, manual intake remains available |
| P1 | Storage/key/region | Public policy; wrong tenant; service over-privilege; key rotation/recovery; wrong endpoint/region | Access denied/alerted; no fallback to insecure storage or unapproved egress |
| P1 | Retention/restore | Withdraw/delete/legal hold; partial purge; backup restore; orphan original/derived object | Governed state remains consistent; resurrected data reblocked and reconciled |
| P1 | Supply chain | Package/model/image hash mismatch; vulnerable artifact; unapproved import/network | Build/deploy blocked; artifact quarantined; rollback works |
| P1 | Incident response | Scanner/store/provider compromise; telemetry outage; secret exposure; kill switch | Containment, rotation, disabled P11, honest status, P7 fallback, documented evidence |

Test fixtures must be synthetic and non-sensitive. No real patient files, credentials, live
penetration target, or unapproved external service may be used.

## 7. Nine-gate mapping and failure-isolation evidence

| P11 gate | Threat IDs | Current conclusion |
| --- | --- | --- |
| 1 — ownership/identity/consent | 001–003, 008, 011, 013 | BLOCKED; document authority and population are undecided. |
| 2 — file security/quarantine | 004–009 | OPEN; no values, scanner, sandbox, or upload pattern approved. |
| 3 — storage/retention | 008–010, 015–018, 023, 025 | BLOCKED; only provider-neutral port/local adapter exists. |
| 4 — schema/idempotency/processing | 009–014, 021 | OPEN; no document schema, migration, durable worker, or event integration. |
| 5 — OCR benchmark/provider | 017, 020, 024 | OPEN; candidates are benchmark-gated and no live egress is approved. |
| 6 — registry/version contracts | 012, 021 | OPEN; synthetic compile-time mechanics only. |
| 7 — medical extraction/review | 020–022 | BLOCKED; no clinical schemas, validation, or reviewer authority. |
| 8 — source UI/assignment | 001–003, 015, 018, 021–023 | BLOCKED; no trusted clinician/source viewer or approved copy. |
| 9 — threat/privacy/release | All | OPEN; this draft is review input, not acceptance or release approval. |

Existing failure-isolation evidence is limited: P7 manual intake is independent; risky features
default off; document code is synthetic and unregistered; P11 failures cannot currently reach a
patient route; P5 rejects lower-trust overwrite; and P8-C/P9-C/P10 live gates remain closed. These
facts reduce current exposure because P11 is absent; they do not prove future mitigations.

## 8. Remediation ownership and re-review triggers

Threat owners must create governed decision/evidence records rather than editing a status to
“mitigated.” Security engineering owns hostile bytes, sandbox, preview, IAM and incident validation;
identity/security owns actor assurance/nonenumeration; privacy/legal owns purpose, consent, processor,
region, retention, deletion and rights; data/application architecture owns schema, transactions,
idempotency and reconciliation; infrastructure/operations owns storage/keys/workers/capacity/restore;
clinical governance and subject experts own medical extraction/review authority; accessibility and
content owners own user-visible states; product/institution owners own population and release.

Mandatory threat-model re-review triggers include selection/change of upload pattern, supported
format or limit; scanner/parser/OCR/model/provider/version; network egress; object store, region,
encryption or key custody; schema/migration; job backend/worker identity; event payload; actor,
assignment, population, consent, notice or purpose; source viewer/renderer/signed grant; retention,
deletion, backup or legal hold; clinical candidate/promotion rules; dependency/profile; deployment
topology; material incident; or any attempt to activate P8-C, P9-C, P10, P11-E, pilot or production.

## 9. Human review register and conclusion

Required reviewers are security engineering; identity/security; privacy/legal; clinical governance;
application/data architecture; infrastructure/storage; data governance/records; document-AI;
operations; accessibility/content; and product/institution owner. No person, signature, acceptance
date, risk score, or approval is recorded here.

P11 remains **0 APPROVED / 5 OPEN / 4 BLOCKED** and `AC-P11-001..011` remain unverified for live
use. P10 remains **0/9 approved**; P8-C/P9-C Stage 3 remain blocked; `/documents` remains unavailable;
P11-E remains unimplemented; and P7 manual intake remains the supported fallback.
