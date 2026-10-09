# ADR-001 — Modular Monolith First

**Status:** ACCEPTED

## Context
SwasthyaSetu has many logical domains but does not yet justify distributed-service complexity.

## Decision
Use one FastAPI modular-monolith backend initially with strict bounded modules.

## Consequences
Simpler development and transactions; module boundaries must be enforced so services can later be extracted.
