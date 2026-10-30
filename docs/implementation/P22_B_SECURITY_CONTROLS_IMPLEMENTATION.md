# P22-B Security Controls — Bounded Engineering Increment

**Status:** Implemented engineering subset; P22 remains **PARTIAL**

**Baseline:** `origin/main @ d9ce291ebe878834fa3f19cd966975936be933bf`

**Branch:** `phase/p22-b-security-controls`

## 1. Decision boundary

This increment implements controls whose secure behavior follows directly from the current
architecture. It does not invent clinical, legal, retention, deployment-topology, or risk-acceptance
policy. Existing P7 behavior remains available. P8-C/P9-C Stage 3, live P10/P11, P23, P24, pilot,
and production activation remain outside scope.

## 2. Implemented controls

### 2.1 FastAPI response boundary

The application installs one centralized middleware that applies:

- `X-Content-Type-Options: nosniff`;
- `X-Frame-Options: DENY` and CSP `frame-ancestors 'none'`;
- `Referrer-Policy: no-referrer`;
- a restrictive `Permissions-Policy`;
- same-origin opener and resource policies;
- an API CSP that defaults to no resource loading; and
- HSTS only when the typed application environment is `production`.

No CORS middleware or cross-origin credential grant was added. Cross-origin browser reads therefore
remain denied by default.

### 2.2 Browser response boundary

Patient, Clinician, and Admin Next.js applications consume one versioned workspace export for their
response headers. Production denies framing, object embedding, external form targets, external
connections, and unapproved media. HSTS and `upgrade-insecure-requests` are production-only.
Development adds only the script-evaluation and websocket allowances required by the local Next.js
toolchain.

The CSP retains `'unsafe-inline'` for framework-emitted inline bootstrap/style content. Removing it
requires a separately tested nonce/hash integration; the current policy is a material improvement,
not a claim of maximal CSP hardening.

### 2.3 Cookie-authenticated mutation boundary

Every current patient BFF mutation in onboarding and intake now requires an `Origin` header and an
exact canonical-origin match. In production, the server accepts authority only from
`SWASTHYASETU_PUBLIC_ORIGIN`, which must be an exact HTTPS origin. Missing, malformed, plaintext
non-loopback, credential-bearing, path-bearing, query-bearing, or fragment-bearing configuration
fails closed. The request-controlled `Host` header is not a production authority source.

Loopback HTTP and request-derived origin are retained only for local development and tests.

### 2.4 Bounded application abuse controls

The continuation from `origin/main @ 8e6c9a24b84fc09ccbc57bb5eb19a785b854c3d5` adds a
provider-neutral rate-limiter contract and a bounded in-process sliding-window adapter. Every
`/api/v1` request consumes an atomic process-wide and direct-transport-peer budget. A syntactically
valid bearer also consumes a credential budget keyed by a process-secret HMAC fingerprint;
mutations consume tighter peer and credential budgets, and anonymous session creation consumes an
additional peer budget. Raw credentials are neither retained nor logged.

The middleware ignores `Forwarded` and `X-Forwarded-For`. The committed container entrypoint
disables Uvicorn proxy-header rewriting so those values cannot replace the socket peer before the
request reaches application middleware; alternative deployment entrypoints must preserve this
setting. Denials return the canonical `RATE_LIMITED` error with a bounded `Retry-After`, request
correlation, `Cache-Control: no-store`, and the normal security headers. Limiter failure is
fail-closed through the sanitized application error boundary.

This is intentionally defense in depth for one application process. It does not coordinate across
replicas or replace ingress controls. Its bounded key store preserves the global bucket but may
evict per-subject history during high-cardinality churn. Production topology, edge enforcement,
budgets under representative load, monitoring, and operations ownership remain unverified.

## 3. Evidence

Automated evidence covers:

- backend headers on ordinary and sanitized-error responses;
- production-only HSTS and absent permissive CORS headers;
- production versus development browser policy;
- missing, exact, lookalike, internal-host, and unsafe configured origins;
- existing onboarding and intake BFF behavior under the stricter boundary; and
- actual response headers from all three Next.js applications through Playwright;
- atomic multi-layer limit accounting, exact-boundary concurrency, bounded-key churn and
  fail-closed adapter behavior;
- direct-peer trust, forwarding-header spoof resistance and credential-HMAC minimization; and
- read, mutation, anonymous-session, canonical-denial and sanitized-failure middleware behavior.

## 4. Deliberately outstanding controls

| Control | State | Reason |
|---|---|---|
| Rate limiting | Bounded application control implemented; AC-P22-006 live not verified | The adapter is process-local and direct-peer only. Edge/fleet coordination, production topology, representative budgets, monitoring and operations ownership remain undefined. |
| Upload security | No runtime path; AC-P22-005 live not verified | No upload endpoint or document ingestion runtime exists. Absence is not acceptance evidence. |
| Production proxy/header stripping | Not verified | Exact ingress topology is not represented in this repository. |
| Secrets and platform logging review | Not complete | Repository scanning and content-free application logging do not prove production sink/access/retention controls. |
| Retention/purge | P22-C scope | Requires an authoritative schedule, hold semantics, and operational ownership. |
| Kill switches/provider resilience | P22-D scope | Requires an approved feature inventory and deployment-aware rehearsal. |
| Independent regression/closure | P22-E scope | Requires the preceding controls and exact deployed-environment evidence. |

## 5. Acceptance status

No live P22 acceptance criterion is promoted to PASS by this increment. `AC-P22-001..011` remain
**LIVE NOT VERIFIED**. The code and tests provide bounded engineering evidence for later independent
review; they do not authorize a pilot, production release, real patient processing, or clinical
decision activation.
