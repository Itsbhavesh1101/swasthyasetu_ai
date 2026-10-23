# SwasthyaSetu AI — October 2026 Next.js Security Remediation

**Work unit:** `SECURITY-NEXTJS-2026-10` — tightly scoped dependency security repair, not a new clinical, patient-facing, or platform feature.

**Repository:** `Itsbhavesh1101/swasthyasetu_ai`
**Verified starting `main`:** `747110bcbecaeb3484fddf68b2eec9038fd43ce1`
**Prior PR #42:** merged, merge tree identical to reviewed head `ea92537abc036943073c850283d2b5bfd4d0a43a`.
**Proposed branch:** `phase/security-nextjs-oct-2026-remediation`
**Current manifest pins:** `next@16.4.0` in all three Next.js apps, `eslint-config-next@16.4.0` in root. `pnpm-lock.yaml` currently resolves `sharp@0.35.5` (already fixed for the upstream image issue) but still resolves vulnerable `next@16.4.0`. `react@19.3.0` and `react-dom@19.3.0` are pinned; do not assume they need changing.
**Toolchain:** Node `24.18.1`, pnpm `9.15.4`, Python `3.12.13`, uv `0.12.20`; Alembic `p7a_0007`.

> **Security evidence:** Next.js upstream release on 2026-10-14 identifies two critical remote-code-execution advisories and one high-severity DoS, patched in `next@16.4.1`. The subsequent stable `next@16.4.2` (released 2026-10-15) incorporates these fixes and normal bug fixes. Sources: https://nextjs.org/blog/nextjs-security-update-october-14-2026 and https://github.com/vercel/next.js/releases/tag/v16.4.2 . Advisories: `GHSA-673q-mjm6-r5xr`, `GHSA-2464-fhr4-w9xw` / `CVE-2026-96889`, `GHSA-p3m5-59mp-jv5r`. **Update even when specific vulnerable app patterns are not found; scanners and feature absence are not sufficient reasons to retain a known-vulnerable direct pin.** Re-check upstream advisories and published stable patched releases before editing; if the facts differ, report clearly rather than assume these values remain current.

## 0 — Preflight and safe worktree

1. Fetch origin and verify its `main` SHA equals the exact baseline above and PR #42 is merged/tree-equivalent. If baseline drift occurred, STOP and report instead of silently proceeding or rebasing. Work in a new clean isolated worktree/branch. Preserve the primary worktree and all pre-existing untracked files. Do not reset, force-push, or auto-merge.
2. Read `docs/codex/{CODEX_INSTRUCTIONS,CODEX_WORKFLOW,CODEX_CONTEXT_RULES}.md`, `docs/research/r3/R3_CODEX_DEPENDENCY_POLICY.md`, the pinned root/three-app manifests, `pnpm-lock.yaml`, `.github/workflows/ci.yml`, `scripts/quality_gate.py`, Next config files, frontend tests and privacy controls. Check `docs/implementation/{37_DECISION_LOG,38_PROGRESS_TRACKER}.md`, `docs/26_PRIVACY_CONSENT_SPEC.md`, and the latest P8–P14 readiness records for governance truth.
3. Do not treat `27_SECURITY_ARCHITECTURE.md` or `28_THREAT_MODEL.md` as completed whole-platform reviews: they remain P11-specific drafts. This change is dependency remediation, **not** a P22 completion, security sign-off, or permission to activate any blocked modules.

## 1 — Narrow security dependency repair

1. **Pin the three app dependencies** (`apps/patient-web/package.json`, `apps/clinician-web/package.json`, `apps/admin-web/package.json`) from exact `next@16.4.0` to exact stable `next@16.4.2` (or to a later **verified stable, patched** same-minor release only if available and demonstrably warranted). Avoid canary/RC/major upgrades.
2. **Align root** `eslint-config-next` with the selected exact Next.js patch (`16.4.2` if Next is `16.4.2`). Do not change unrelated direct dependencies, React, Node, pnpm or backend versions without a specific demonstrated security/compatibility requirement; if a wider change becomes necessary, STOP and explain.
3. Using **pinned pnpm 9.15.4**, regenerate `pnpm-lock.yaml` deterministically. Verify every workspace importer and the resolved package entries; reject stale `next@16.4.0` / `eslint-config-next@16.4.0` references and verify `sharp` resolves to `>=0.35.5` where used. The lockfile may update required transitive dependencies: classify each change and confirm it follows from the patched Next.js package (or record and justify any exception). Do not manually fabricate lock entries.
4. Verify clean/frozen install (`pnpm install --frozen-lockfile`), resolved Next.js and `eslint-config-next` across all three apps, image processing dependency, Node engine, and all required builds. Check actual Next App Router/cache/Server Action/next/image usage and configs to document **exposure context**, **not** as a reason to skip the patch. If a build fails because of an advisory, do not bypass the warning or weaken an audit/CI; repair with the patched release. Don't assume `sharp`'s fixed current pin addresses the two other advisories.
5. Review the pinned lock for upstream React Server Components / Next / sharp advisories using official notices and available security scanners. If a direct React or related package actually needs an independent patch beyond this allowlist, report a **BLOCKED or explicit separate-review request**, not a silent scope expansion.

## 2 — Scope, privacy and security evidence

Allowed changed paths (new file indicated):

```text
package.json
apps/patient-web/package.json
apps/clinician-web/package.json
apps/admin-web/package.json
pnpm-lock.yaml
docs/implementation/NEXTJS_SECURITY_REMEDIATION_2026_10.md   # NEW, concise evidence record
docs/implementation/38_PROGRESS_TRACKER.md                # Minimal section #60; preserve history
docs/codex/CODEX_PHASE_PROMPTS/NEXTJS_OCT_2026_SECURITY_REMEDIATION_PROMPT.md # copy of this prompt
```

Create an evidence record containing: exact base and final SHAs, advisory identifiers and fixed versions with official source links, old/new exact manifests and lock resolution including `sharp`, scan and build outcome (including unresolved unrelated warnings), exposure notes based on actual code/config, any required transitive lockfile changes, test outcomes, rollback instruction, and **engineering-only security-remediation status** (not formal privacy/security/clinical/production approval). Do not place secrets, health data, exploit payloads, provider contacts or patient narratives in the record.

In `38_PROGRESS_TRACKER.md`, add **`# 60. October 2026 Next.js Security Remediation`** describing the change and its independently reviewable status. Do not mark P22 or any P8–P14/P21 phase complete or modify historical section records. Earlier P14 draft PR #42 was merged at the baseline. Maintain P7 manual intake; P8-C/P9-C Stage 3 BLOCKED; P10/P11 live 0/9 approved; P12/P13/P14/P21 runtime NOT STARTED. No accepted ADR or Alembic head changes.

**Prohibited:** APIs, schemas/ORM/migrations, backend code or requirements, patient/clinician/admin business logic, new runtime services, providers, models, clinical policy, consent/identity, feature flags, production deployment, external patient-data transfer, UI functionality, test weakening, CI/Docker/config changes, unrelated package upgrades, architecture substitutions, approval/signature fabrication or source-data additions. If minimal compatibility changes beyond the allowlist are absolutely necessary, STOP and report them for independent review instead of expanding silently.

## 3 — Quality, security validation and PR

1. Run `git diff --check`; verify exact allowlist; compare manifests and transitive lockfile resolution before/after; no unrelated changes, no secrets, no diff in `backend/uv.lock`, no migrations, Alembic remains `p7a_0007`.
2. Run clean frozen pnpm installation, frontend formatting/lint/typecheck, **all frontend tests**, **all three production builds**, and Playwright tests. Run the backend quality gate too to catch regressions. Include Postgres checks if the environment permits and always require the GitHub real-Postgres job. Preserve existing privacy headers, no-store, service-worker caching restrictions, cookie/session, CSRF, source boundaries, P7 intake, and generic urgent-help flows. Do not alter tests to hide failures.
3. Compare dependency scan results with baseline; identify **whether these Next.js advisories are resolved**, separately from the recurrent Trivy warning `CVE-2026-107891` (metadata could not be loaded). Do not claim all vulnerabilities are absent based on six green jobs. Record residual warnings and any suspected unrelated findings for a later separately scoped review.
4. Commit, push the isolated feature branch and open **one PR** with only the eight permitted paths. All six GitHub jobs must be **SUCCESS on the exact PR final head**: Backend quality, Frontend quality, Persistence integration, Docker and PostgreSQL, Playwright Chromium, Security scans. Verify local SHA = remote SHA = PR SHA = CI SHA. **DO NOT MERGE**. Do not start P15 or any clinical implementation on this branch.

## Required completion report

```text
STATUS: COMPLETE SECURITY PATCH / PARTIAL / BLOCKED
BRANCH:
BASE MAIN SHA: 747110bcbecaeb3484fddf68b2eec9038fd43ce1
FINAL LOCAL SHA:
FINAL REMOTE SHA:
PR URL / NUMBER:
NEXT / ESLINT-CONFIG-NEXT BEFORE AND AFTER (THREE APPS / ROOT):
LOCKFILE RESOLUTION AND SHARP VERSION:
OFFICIAL SECURITY ADVISORIES ADDRESSED:
EXPOSURE CHECK / REGRESSION AND PRIVACY BOUNDARIES:
CHANGED-PATH ALLOWLIST AND TRANSITIVE DEPENDENCIES:
LOCAL QUALITY / BUILDS / PLAYWRIGHT:
SECURITY SCAN FINDINGS / WARNINGS / RETRIES:
CI RUN ID / EXACT SHA / SIX JOB CONCLUSIONS:
ALEMBIC / BACKEND DEPENDENCIES / GOVERNANCE:
MERGED: NO
```

**STOP for independent review.** This is a narrowly approved dependency-security repair. It grants no clinical/privacy/security/release approval and does not authorize live patient functionality.
