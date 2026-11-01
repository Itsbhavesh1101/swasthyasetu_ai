# P24-B — Synthetic Safety-Evaluation Planning Foundation

## Status and authority boundary

This unit is a bounded, detached, engineering-synthetic planning foundation only. It does not run a
safety evaluation, create clinical rules, approve a fixture or metric, establish pilot eligibility,
satisfy `AC-P24-008` or `AC-P24-009`, record a release decision, or authorize human participation,
deployment, pilot or production use.

Every plan and manifest is fixed to `ENGINEERING_ONLY`, `ENGINEERING_SYNTHETIC`, `UNVERIFIED`,
`NOT_EXECUTED`, `NOT_ELIGIBLE`, `HUMAN_METRIC_AND_APPROVAL_REQUIRED` and release decision
`NOT_RECORDED`.

## Canonical planning inventory

The contract requires exactly the six evaluation areas named by the Master Implementation Plan:

1. clinician-authored safety set;
2. multilingual safety set;
3. route concordance;
4. critical false negatives;
5. resource correctness; and
6. clarification utility.

The manifest cannot omit, duplicate, rename or reorder an area. Inventory completeness does not
mean that a clinical set, language, resource, route, metric, threshold, denominator, result or
approval exists.

## Integrity mechanics

Each immutable plan binds an exact engineering version, build SHA, synthetic-fixture-plan hash,
oracle-plan hash, metric-plan hash, analysis-plan hash, privacy-plan hash, negative-test-plan hash,
responsible-role-description hash and UTC creation time. The manifest additionally binds the exact
build, configuration hash, proposed-scope hash and UTC generation time.

Constructors and snapshot helpers reconstruct nested inputs, normalize aware clocks to UTC, reject
naive clocks, detect forced mutation, enforce exact build consistency and return stable content-free
error codes. The canonical builder permits only `LOCAL` and `TEST`; it rejects staging, pilot and
production before inspecting supplied plans.

## Deliberately absent behavior

There is no fixture content, patient or clinical data, language corpus, policy, resource, route,
metric value, threshold, denominator, score, result, pass/fail decision, signature, approval,
waiver, clinical inference, runtime evaluation, persistence, migration, API, UI, event, job,
network operation, deployment, module registration or route.

The package cannot convert hashes, inventory completeness, green CI or a synthetic plan into safety
evidence or release authority.

## Verification boundary

The adversarial suite covers the exact six-area inventory, strict types and machine grammars, fixed
safe labels, every bound hash, build mismatch, duplicate/missing/reordered areas, UTC normalization,
chronology, protected-environment short circuiting, forced mutation, content-free failures, absent
evaluation/release authority and absent runtime registration/routes.

Passing tests prove only deterministic metadata integrity for the bounded synthetic planning
schema. All live P24 and product acceptance remain unverified.
