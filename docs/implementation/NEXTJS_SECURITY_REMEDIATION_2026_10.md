# October 2026 Next.js Security Remediation Evidence

Status: **engineering-only dependency security remediation**. This record is not formal security,
privacy, clinical, production, or release approval; it does not complete P22 or activate any blocked
module.

## Lineage and change

- Work unit: `SECURITY-NEXTJS-2026-10`
- Baseline: `main` at `747110bcbecaeb3484fddf68b2eec9038fd43ce1`
- Final branch commit: the immutable PR head identified in GitHub and the completion report. A commit
  cannot embed its own content-derived SHA; those two records are the authoritative exact final SHA.
- Date verified: 2026-10-23
- Branch: `phase/security-nextjs-oct-2026-remediation`
- `next` changed from exact `16.4.0` to exact `16.4.2` in patient-web, clinician-web, and admin-web.
- Root `eslint-config-next` changed from exact `16.4.0` to exact `16.4.2`.
- React and React DOM remain exactly `19.3.0`; Node, pnpm, Python, uv, backend requirements, Docker,
  CI, application code, and configuration are unchanged.
- npm metadata identifies both selected packages as MIT licensed. The change remains within the R3
  core frontend framework/tooling dependency class and is an exact same-minor security patch.

The selected stable release is supported by the official
[Next.js security update](https://nextjs.org/blog/nextjs-security-update-october-14-2026) and the
[Next.js 16.4.2 release](https://github.com/vercel/next.js/releases/tag/v16.4.2). On the verification
date, `16.4.2` was the current stable npm release; no canary, release candidate, or major upgrade was
used.

## Security advisories and scan evidence

The upgrade addresses `GHSA-673q-mjm6-r5xr`, `GHSA-2464-fhr4-w9xw` / `CVE-2026-96889`, and
`GHSA-p3m5-59mp-jv5r`. The baseline `pnpm audit --audit-level high` reported all three against
`next@16.4.0` (two critical and one high). After the upgrade, none is reported and the audit count
fell from two critical/two high to zero critical/one high.

The residual high finding is the unrelated development-tooling path
`eslint-config-next -> @next/eslint-plugin-next -> fast-glob -> micromatch -> braces@3.0.3`, reported
as `GHSA-vfj7-8cjw-p6xm` / `CVE-2026-93687`. npm reports no patched `braces` version. It is recorded
for a separately scoped review and was not hidden or expanded into this repair. A cached local Trivy
0.76.0 filesystem scan of production dependencies and configuration reported zero high/critical
findings in `pnpm-lock.yaml`, zero in `backend/uv.lock`, and zero Dockerfile misconfigurations. Its
initial metadata-update attempt timed out after five minutes; the bounded retry used the existing
cache and completed. The repository's recurrent Trivy `CVE-2026-107891` metadata-load warning is
tracked separately; absence of that warning in the cached local result is not a claim that it is
resolved. The final GitHub Security scans job is authoritative for the committed tree.

No secrets, health data, patient narrative, provider contact, or exploit payload was added.

## Lockfile and exposure review

Pinned pnpm `9.15.4` regenerated the lockfile. All three workspace importers resolve `next@16.4.2`
and the root importer resolves `eslint-config-next@16.4.2`. Required same-package-family lock entries
changed from `16.4.0` to `16.4.2`: `next`, `@next/env`, `@next/eslint-plugin-next`,
`eslint-config-next`, and the eight optional platform-specific `@next/swc-*` packages. Their integrity
values changed accordingly; no unrelated transitive package version changed. `sharp` remains
`0.35.5`, React/React DOM remain `19.3.0`, and frozen installation succeeds.

All three sites use the App Router. No Server Action (`use server`) or explicit `use cache` directive
was found, and no application import of `next/image` was found. Patient-web does contain same-origin
BFF route handlers and server-side backend fetches, so the known-vulnerable direct framework pin was
patched regardless of observed feature usage. Existing `no-store` handling for clinical/session
requests, privacy headers, HttpOnly/SameSite session cookies, browser-storage prohibition, and the
service worker's generic-shell-only caching boundary remain unchanged.

## Regression evidence

- Frozen pnpm install, formatting, ESLint, TypeScript, and all three Next.js 16.4.2 production builds:
  pass.
- Frontend unit/component suites: 145 passed across 15 files (patient 141, shared UI 2, clinician 1,
  admin 1).
- Backend quality gate: formatting/lint/type/import/compile checks passed; 1,238 tests passed and 97
  PostgreSQL tests were skipped in the non-database gate.
- Real PostgreSQL: Alembic upgrade/current/check passed at `p7a_0007`; 97 integration tests passed.
- Playwright: all 13 browser journeys passed; 11 passed initially and 2 passed on their configured
  retry after local parallel startup/navigation timeouts. No test was changed or weakened.
- Local Trivy bounded cached retry: pass with zero high/critical production dependency findings.
- `pnpm audit`: expected nonzero exit solely for the unpatched unrelated `braces` development path
  described above.

## Rollback

Revert the final remediation commit as one unit to restore the four manifest pins, lockfile, evidence
record, tracker entry, and prompt copy. That rollback intentionally restores known-vulnerable
`next@16.4.0` and therefore must not be deployed; prefer a reviewed forward patch if remediation must
change.

Governance remains unchanged: P7 deterministic manual intake is the supported fallback; P8-C and
P9-C Stage 3 remain blocked; P10/P11 live approval remains 0/9; P12/P13/P14/P21 runtime remains not
started. No accepted ADR or Alembic head changed.
