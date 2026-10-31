# P14-B Synthetic Backstop Foundation - Design

## Decision

Add only provider-neutral, content-free contracts for a detached safety backstop. Reuse P14-A's
fixed toy signal codes and introduce an equally closed toy evidence vocabulary. Keep the only
executable mapping in test support so production code cannot interpret text or assign clinical
meaning.

## Boundaries

- A request binds an engineering artifact, fixed ordered evidence tokens, and a canonical UTC
  deadline.
- A response binds the complete request identity and is either a consistent matched/no-match result
  or a content-free simulated failure.
- Validation is repeatable after construction and detects mutation, identity drift, invalid
  chronology, duplicates, noncanonical time, and inconsistent outcomes.
- The port has no implementation in application code and is not registered by the API.

## Test adapter

The deterministic mock is importable only from `backend/tests`. It validates a request snapshot
before reading evidence, evaluates the deadline before evidence, and uses a closed toy-token map.
It cannot process narrative content, select a route, access a provider, or be activated at runtime.

## Non-goals

Clinical signals, language/lexicon work, conversations, patient data, scoring, policy, routing,
resources, referrals, providers, APIs, persistence, UI, and runtime activation remain prohibited.
