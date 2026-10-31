# P14-C Synthetic Policy-Routing Mechanics - Design

## Decision

Implement a detached pure evaluator for nonmedical toy symbols. Application code contains generic
contracts and precedence/fail-closed mechanics only. The sole executable mapping belongs to test
support, and protected environments are rejected before any input is read.

## Contracts and integrity

- A policy artifact binds its engineering-only identity, UTC effective interval, test-only state,
  sorted rules, matcher, precedence kind, toy route, and toy reason through one SHA-256 content hash.
- An evaluation keeps extractor and backstop observations separate and fingerprints their exact
  provenance-sensitive snapshot.
- A decision binds the exact evaluation and exact valid policy reference. Missing or invalid policy
  is represented explicitly without fabricating a reference.
- Direct construction and evaluation revalidate nested values so forced mutation fails closed.

## Deterministic mechanics

Toy precedence is fixed as override, clarification, then standard. Multiple winning rules may agree;
different routes at equal winning precedence degrade. Conflicting extractor/backstop state, no
match, policy lifecycle failure, or policy-integrity failure also degrades. No model route, score, or
confidence is accepted as input.

## Non-goals

No clinical policy content, `ROUTE_A/B/C` interpretation, patient-facing fallback, self-care/crisis
meaning, narrative processing, resource/referral behavior, API, persistence, UI, or activation.
