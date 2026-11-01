# P21-A Synthetic Admin Authorization Contracts Design

## Intent

Create a detached, content-free engineering preflight for the future P21-A admin backend. The
preflight proves that an operation can be bound to one actor, action, object, institution, source,
purpose, version, MFA state, and active grant without creating a live administrator, role policy,
API, audit record, or governance approval.

## Goals

- Define immutable, strictly validated synthetic request, grant, and decision contracts.
- Require exact actor/action/object/institution/source/purpose matching and current MFA.
- Bind evaluation to UTC time, grant validity, object version, and a deterministic contract version.
- Fail closed for absent, stale, mismatched, ambiguous, mutated, or protected-environment input.
- Keep P21 and every live acceptance criterion partial and unverified.

## Non-goals and anti-goals

- No production roles, permissions, identity provider, credential, MFA ceremony, or role grant.
- No provider/resource, patient, clinical, policy, model, feature-flag, referral, or audit operation.
- No route, API, UI, persistence, migration, event, job, module registration, or runtime activation.
- No human approval, maker-checker policy, source truth, institution authority, or release evidence.
- A synthetic match must never be usable as runtime authorization.

## Constraints

- Use closed engineering-only identifiers and opaque hashes; accept no free text or sensitive data.
- Reject staging, pilot, and production before inspecting request or grant contents.
- Reconstruct frozen inputs at the evaluator boundary so forced mutation cannot bypass validation.
- Produce stable content-free failure codes only.
- Add no dependency and leave Alembic head `p7a_0007` unchanged.

## Approaches considered

1. **Extend P4 roles and permissions.** Rejected because it would invent production admin policy and
   make staged identity primitives appear authoritative.
2. **Build P21-A APIs and services.** Rejected because trusted identity, object/source authority,
   audit policy, and accountable approvals remain blocked.
3. **Detached synthetic contract preflight.** Selected because it tests exact scope binding and
   fail-closed mechanics without acquiring runtime or clinical authority.

## Design

`app.modules.admin_governance.contracts` owns closed enums, strict frozen dataclasses, canonical
ordering, UTC normalization, a request fingerprint, snapshot reconstruction, and content-free
errors. All identifiers are restricted to a small synthetic namespace.

`evaluate_synthetic_admin_preflight()` first rejects protected environments. It then reconstructs
the request and every grant, rejects duplicate or ambiguous grants, requires MFA, and matches every
scope dimension exactly. It returns either `MATCHED_SYNTHETIC_CONTRACT` or `ABSTAINED`; neither is a
runtime authorization result. Expired or not-yet-effective grants abstain rather than matching.

The module remains absent from the application registry and HTTP route table. Tests prove direct
constructor invariants, forced-mutation resistance, action and scope isolation, temporal behavior,
protected-environment denial, deterministic ordering/fingerprints, and lack of activation surfaces.

## Governance result

This is engineering evidence for a proposed P21-A boundary only. `FR-ADMIN-*`, `FR-AUDIT-*`, and
`AC-P21-*` remain live and not verified. P21-B/C/D and every real admin capability remain blocked.
