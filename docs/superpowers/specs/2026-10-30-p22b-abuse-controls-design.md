# P22-B Abuse Controls Design

## Intent

Add bounded, deterministic application-layer rate limiting to every FastAPI `/api/v1` request,
with stricter protection for mutations and anonymous session creation. The control must reduce
single-instance abuse without claiming fleet-wide or edge protection that the repository cannot
provide.

## Goals

- Enforce layered global, direct-peer, credential, mutation, and session-creation limits.
- Return the canonical privacy-safe `RATE_LIMITED` envelope with `Retry-After` and `no-store`.
- Never trust `Forwarded` or `X-Forwarded-For` without an approved proxy topology.
- Never retain or log raw bearer credentials; use a process-keyed HMAC fingerprint in memory.
- Bound limiter key cardinality and keep decisions deterministic under concurrent requests.
- Require no dependency, broker, Redis/Valkey service, schema, migration, or external infrastructure.

## Non-goals

- Fleet-wide quotas, WAF behavior, distributed counters, or production ingress configuration.
- User-visible product policy, billing quotas, clinical prioritization, or authorization decisions.
- Upload security, retention, resilience switches, P22-C/D/E, P23, or P24.

## Approaches considered

1. **Valkey/Redis-backed distributed limits.** This would provide fleet-wide counters, but Valkey is
   optional and not authorized as a default dependency or service. Rejected for this increment.
2. **One process-local counter keyed only by IP.** Simple, but a BFF/proxy can collapse all users to
   one peer and forwarded headers are spoofable without an approved trust chain. Rejected.
3. **Layered in-process limits with explicit deployment boundaries.** A process-wide ceiling always
   protects the instance; direct-peer limits use only the transport peer; valid bearer-shaped
   credentials receive an additional HMAC-scoped limit; mutations and session creation receive
   tighter layers. Chosen because it is useful defense in depth without pretending to be distributed.

## Design

`app.shared.rate_limits` owns immutable rule/subject/decision contracts, a provider-neutral
`RateLimiter` protocol, and an `InMemorySlidingWindowRateLimiter`. One atomic `check()` evaluates all
applicable subjects and records the request only when every layer allows it. The adapter uses a
monotonic injected clock, an async lock, sliding-window timestamp queues, and bounded LRU key storage.
When per-key storage churns, a global bucket remains authoritative for process-wide protection.

`RateLimitSettings` supplies validated, overrideable 60-second budgets with safe defaults:

- 6,000 requests per process;
- 600 requests per direct peer;
- 120 requests per credential;
- 300 mutations per direct peer;
- 60 mutations per credential; and
- 120 anonymous session creations per direct peer.

`RateLimitMiddleware` excludes health and non-API paths. It derives the direct peer only from the
ASGI transport, never forwarded headers. A bearer-shaped Authorization value is HMAC-SHA256
fingerprinted with a random process key; raw values never enter limiter state, logs, errors, or
metrics. A denied request returns the existing canonical error schema and retains request correlation
and security headers through deliberate middleware ordering. The committed Uvicorn container
entrypoint disables proxy-header rewriting so forwarded values cannot replace the socket peer before
the application receives the ASGI scope; alternative entrypoints must preserve this property.

## Failure and privacy behavior

- Missing transport peer uses one shared `unknown` bucket and does not bypass limits.
- Malformed or missing authorization receives peer/global limits but no attacker-controlled
  credential bucket.
- Invalid configuration fails application construction through typed settings validation.
- Limiter exceptions fail closed with the existing sanitized 500 boundary rather than allowing the
  request.
- Rate-limit state is ephemeral and contains only scopes, opaque peer text, HMAC digests, and
  monotonic timestamps.

## Acceptance boundary

This implementation supplies bounded engineering evidence for NFR-SEC-008 and AC-P22-006. Those
requirements remain **LIVE NOT VERIFIED** for a multi-instance or production deployment until an
approved ingress/distributed design and bypass/load evidence exist. P22 remains **PARTIAL**.
