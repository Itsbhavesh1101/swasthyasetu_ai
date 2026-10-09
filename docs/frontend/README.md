# Frontend workspace

P1-B provides three independent Next.js App Router applications and the small shared UI package
they consume. These are foundation surfaces only; they intentionally contain no product,
clinical, authentication, persistence, analytics, or API-integration behavior.

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

## Quality gates

```text
pnpm frontend:format-check
pnpm frontend:lint
pnpm frontend:typecheck
pnpm frontend:test
pnpm frontend:build
```

Playwright configuration and smoke-test discovery:

```text
pnpm e2e:list
```

After installing Playwright's Chromium browser in a suitable P1-C/CI environment, run:

```text
pnpm exec playwright install chromium
pnpm e2e:test
```

Framework telemetry should be disabled in protected CI/deployment environments with
`NEXT_TELEMETRY_DISABLED=1`. P1-B adds no application analytics or user tracking.
