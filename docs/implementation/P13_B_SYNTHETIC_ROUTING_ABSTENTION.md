# P13-B - Synthetic Symbolic Routing and Abstention Foundation

**Status:** complete bounded engineering subset; live P13 routing remains partial and unapproved

**Baseline:** stacked on P13-A at `fd1226505a7d0c96c46ab0068bbb120c5594c999`

**Branch:** `phase/p13-b-synthetic-routing-abstention`

## Implemented

- Frozen, slotted `SymbolicRoutingRequest`, `SymbolicRoutingRule`, `SyntheticRoutingPolicy`, and
  `SymbolicRoutingDecision` contracts.
- Reserved synthetic identifiers, strict versions and SHA-256 policy artifact identity.
- Closed `ENGINEERING_ONLY`, `ENGINEERING_SYNTHETIC`, and `UNVERIFIED` authority states.
- A pure exact-match evaluator with explicit `SYMBOLIC_MATCH` or `ABSTAIN` dispositions.
- Fail-closed no-match and ambiguous-match behavior; rule order cannot select among ambiguity.
- Direct-constructor, nested-mutation, UTC, temporal-order, immutability, and forbidden-field tests.

## Deliberate boundary

The evaluator accepts no free text, symptom, clinical fact, patient/subject, model output, clinical
category, threshold, P9 result, urgency, geography, eligibility, or availability. It performs no
provider/resource lookup and returns no provider ID, contact, ranking, or patient-facing content.

No real policy, taxonomy, source query, registry, persistence, migration, API, UI, referral,
notification, event, job, feature flag, dependency, or runtime registration was added. Alembic
remains `p7a_0007`.

## Governance truth

This subset exercises only the Gate 2 allowance for nonmedical symbolic matching and abstention.
It does not resolve P13 Readiness Gates 1-8 or authorize clinical routing, verified provider data,
display, referral sharing, or delivery. `FR-DIR-001..017`, `FR-REF-001..013`, and
`AC-P13-001..011` remain live-not-verified. P7 remains the supported manual path and all P8-C,
P9-C, P10, P11, and P12 live restrictions remain in force.
