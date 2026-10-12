# Frontend workspace

P1-B provides three independent Next.js App Router applications and the small shared UI package
they consume. P6-A adds the patient-specific responsive shell and planned route architecture. P6-B
connects the patient onboarding, language, session, and consent journey while the clinician and
admin applications remain foundation surfaces.

## Requirements

- Node.js 20.9 or newer; verification used Node.js 24.18.1.
- pnpm 9.15.4, pinned by the root `packageManager` field.

Install the workspace from the repository root:

```text
pnpm install --frozen-lockfile
```

## Applications

Run one application at a time from the repository root:

```text
pnpm patient:dev
pnpm clinician:dev
pnpm admin:dev
```

The workspace packages are:

- `@swasthyasetu/patient-web` in `apps/patient-web`;
- `@swasthyasetu/clinician-web` in `apps/clinician-web`;
- `@swasthyasetu/admin-web` in `apps/admin-web`;
- `@swasthyasetu/ui` in `packages/ui`.

The patient shell exposes `/`, `/start`, `/consent`, `/language`, `/encounter`, `/documents`,
`/results`, `/urgent-help`, and `/referrals`. P6-B activates the first four onboarding steps and a
non-clinical readiness state at `/encounter`; later workflows remain explicitly unavailable.

Set `SWASTHYASETU_BACKEND_URL` on the Next.js server, for example
`http://127.0.0.1:8000` in local development. Same-origin route handlers bridge to FastAPI and keep
the opaque bearer in a transient `HttpOnly`, `SameSite=Strict` browser-session cookie. Cookies are
`Secure` in production and on non-loopback hosts. Client code
receives only minimized session/consent states. No health information, consent body, or language
text is placed in cookies or browser storage, and no service worker is registered.

The consent bridge controls `GENERAL_PRODUCT_USE`, `clinical_intake`, and `privacy-v1`; client input
cannot replace them. The bounded project notice is not a final jurisdiction-specific privacy
notice, which remains governance-deferred. PWA and offline caching remain P6-C work.
Concurrent matching grants are serialized per session within one BFF process and rechecked before
creation. Cross-instance atomic idempotency would require a future backend contract change.

## Quality gates

```text
pnpm frontend:format-check
pnpm frontend:lint
pnpm frontend:typecheck
pnpm frontend:test
pnpm frontend:build
```

Playwright configuration and test discovery:

```text
pnpm e2e:list
```

The P6-B patient journeys require the existing PostgreSQL Compose service, migrations at head, and
a ready FastAPI process. After installing Playwright's Chromium browser, run:

```text
pnpm exec playwright install chromium
pnpm e2e:test
```

Framework telemetry should be disabled in protected CI/deployment environments with
`NEXT_TELEMETRY_DISABLED=1`. P1-B adds no application analytics or user tracking.
