# P24-A — Synthetic Release Evidence Planning Foundation

## Status and authority boundary

This unit is a bounded, detached, engineering-synthetic planning foundation only. It does not start
P24, establish pilot eligibility, satisfy `AC-P24-001..013`, record a release decision, or authorize
deployment, recruitment, human participation, real-data processing, an operational rehearsal, a
pilot or production use.

Every record is fixed to:

- `ENGINEERING_ONLY`;
- `ENGINEERING_SYNTHETIC`;
- `UNVERIFIED`;
- `NOT_EXECUTED`;
- `NOT_ELIGIBLE`;
- `HUMAN_APPLICABILITY_AND_APPROVAL_REQUIRED`; and
- `NOT_RECORDED` for the release decision.

## Canonical inventory

The contract requires exactly the 13 pre-pilot evidence categories named by the Master
Implementation Plan:

1. clinical policy sign-off;
2. mental-health policy sign-off;
3. self-care content approval;
4. verified resource registry;
5. privacy notice;
6. consent text;
7. threat model;
8. incident runbook;
9. data retention policy;
10. release checklist;
11. pilot protocol;
12. model cards; and
13. dataset cards.

The inventory cannot omit, duplicate, rename or reorder a category. Inclusion does not decide
whether an item is applicable to a future human-approved scope and does not claim that any artifact
exists or is approved.

## Integrity mechanics

Each immutable requirement binds an exact engineering version, build SHA, requirement hash,
acceptance-criteria hash, negative-test-plan hash, accountable-role-description hash and UTC
creation time. The manifest additionally binds its exact build, configuration hash, proposed-scope
hash and UTC generation time.

Constructors and snapshot helpers reconstruct all inputs, normalize aware clocks to UTC, reject
naive clocks, detect forced mutation and produce content-free stable error codes. The builder
canonicalizes order and rejects staging, pilot and production before inspecting supplied evidence
requirements.

## Deliberately absent behavior

There is no artifact body, signature, reviewer identity, approval, waiver, eligibility assessment,
GO/CONDITIONAL GO/NO-GO selection, result, deployment, promotion, operational drill, persistence,
migration, API, UI, event, job, network, feature flag, module registration or runtime route.

The package is an unregistered pure contract under `app.validation`. It cannot convert green CI,
hash presence or inventory completeness into release authority.

## Verification boundary

The adversarial suite covers the exact 13-category inventory, strict types and machine grammars,
fixed authority labels, every bound hash, build mismatch, duplicate/missing/reordered categories,
UTC normalization, chronology, protected-environment short circuiting, forced mutation,
content-free failures, absent operational authority and absent runtime registration/routes.

Passing tests prove only deterministic metadata integrity for this bounded synthetic schema. All
live P24 criteria and all product-level acceptance remain unverified.
