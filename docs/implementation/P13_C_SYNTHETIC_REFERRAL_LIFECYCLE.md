# P13-C - Synthetic Referral Lifecycle and Idempotency Foundation

**Status:** complete bounded engineering subset; live P13 referrals remain partial and unapproved

**Baseline:** stacked on P13-B at `56c921c2896bb90f91ea928bea0f0452dff27979`

**Branch:** `phase/p13-c-synthetic-referral-lifecycle`

## Implemented

- Closed canonical referral status vocabulary, explicitly without a bundled transition policy.
- Frozen synthetic referral, transition-pair, policy, command, receipt, and application contracts.
- Versioned policy identity, exact transition-pair evaluation, optimistic version guards, and UTC
  chronology validation.
- Exact idempotent replay as a no-op, conflict rejection for key reuse, referral-scoped bounded
  receipt history, and protection against rollback of later state.
- Adversarial direct-constructor, forced-mutation, identity, chronology, stale-state, and
  forbidden-field tests.

## Deliberate boundary

No patient/session/encounter, actor/institution, destination, provider/resource, consent, payload,
reason, priority, contact, transcript, external reference, delivery evidence, retry, correction, or
expiry semantics exist. No transition graph is configured by production code.

No persistence, migration, API, adapter, webhook, notification, outbox event, job, worker, feature
flag, dependency, or runtime registration was added. Alembic remains `p7a_0007`.

## Governance truth

The status tokens and synthetic mechanics do not authorize external sharing or prove consent,
dispatch, acknowledgement, scheduling, completion, failure, or cancellation. `FR-REF-001..013` and
`AC-P13-006..010` remain live-not-verified, as do all other live P13 criteria. P7 and generic
urgent-help navigation remain independent; all P8-C/P9-C/P10/P11/P12 restrictions remain active.
