import { NextResponse } from "next/server";

import type { EngineeringSummaryResult, EngineeringSummarySection } from "./contracts";

const SECTIONS = [
  "CHIEF_COMPLAINT",
  "HPI",
  "PAST_MEDICAL_HISTORY",
  "PAST_SURGICAL_HISTORY",
  "MEDICATIONS",
  "ALLERGIES",
  "FAMILY_HISTORY",
  "PERSONAL_HISTORY",
  "REVIEW_OF_SYSTEMS",
  "PRIOR_INVESTIGATIONS",
] as const;
const FIELDS = [
  "status",
  "classification",
  "review_state",
  "freshness",
  "affected_sections",
  "drift_reasons",
  "source_count",
  "sections",
  "source_access",
  "can_edit",
  "can_confirm",
  "can_reject",
  "external_egress",
  "notice",
];
const SECTION_FIELDS = [
  "section",
  "readiness",
  "assertions",
  "source_kinds",
  "conflict_review_required",
];

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exactKeys(value: Record<string, unknown>, fields: string[]): boolean {
  const actual = Object.keys(value).sort();
  const expected = [...fields].sort();
  return actual.length === expected.length && actual.every((key, index) => key === expected[index]);
}

function backendUrl(): string | undefined {
  const value = process.env.SWASTHYASETU_BACKEND_URL?.trim();
  if (!value) return undefined;
  try {
    const parsed = new URL(value);
    const loopback = ["localhost", "127.0.0.1", "::1"].includes(parsed.hostname);
    if (
      !["http:", "https:"].includes(parsed.protocol) ||
      parsed.username ||
      parsed.password ||
      parsed.pathname !== "/" ||
      parsed.search ||
      parsed.hash ||
      (parsed.protocol === "http:" && !loopback)
    )
      return undefined;
    return parsed.origin;
  } catch {
    return undefined;
  }
}

function validSection(value: unknown, index: number): value is EngineeringSummarySection {
  if (!record(value) || !exactKeys(value, SECTION_FIELDS) || value.section !== SECTIONS[index])
    return false;
  const populated = index === 0;
  return (
    value.readiness === (populated ? "UNVERIFIED" : "UNKNOWN") &&
    Array.isArray(value.assertions) &&
    Array.isArray(value.source_kinds) &&
    (populated
      ? value.assertions.length === 1 &&
        value.assertions[0] === "SYNTHETIC_REPORTED_COMPLAINT" &&
        value.source_kinds.length === 1 &&
        value.source_kinds[0] === "P7_PATIENT_REPORTED"
      : value.assertions.length === 0 && value.source_kinds.length === 0) &&
    value.conflict_review_required === false
  );
}

export function validEngineeringSummaryResult(value: unknown): value is EngineeringSummaryResult {
  if (!record(value) || !exactKeys(value, FIELDS)) return false;
  if (
    value.status !== "DRAFT" ||
    value.classification !== "ENGINEERING_ONLY" ||
    value.review_state !== "REVIEW_REQUIRED" ||
    value.freshness !== "STALE" ||
    !Array.isArray(value.affected_sections) ||
    value.affected_sections.length !== 1 ||
    value.affected_sections[0] !== "HPI" ||
    !Array.isArray(value.drift_reasons) ||
    value.drift_reasons.length !== 1 ||
    value.drift_reasons[0] !== "NEW_SOURCE" ||
    value.source_count !== 1 ||
    !Array.isArray(value.sections) ||
    value.sections.length !== SECTIONS.length ||
    !value.sections.every(validSection) ||
    value.source_access !== "NOT_AUTHORIZED" ||
    value.can_edit !== false ||
    value.can_confirm !== false ||
    value.can_reject !== false ||
    value.external_egress !== false ||
    typeof value.notice !== "string" ||
    value.notice.length === 0 ||
    value.notice.length > 256
  )
    return false;
  const notice = value.notice.toLowerCase();
  return ["synthetic", "unknown", "source drift", "no clinical action"].every((token) =>
    notice.includes(token),
  );
}

type EngineeringSummaryOutcome =
  { ok: true; result: EngineeringSummaryResult } | { ok: false; status: number; code: string };

export async function loadEngineeringSummaryResult(): Promise<EngineeringSummaryOutcome> {
  const base = backendUrl();
  if (!base) return { ok: false, status: 404, code: "FEATURE_DISABLED" };
  try {
    const response = await fetch(`${base}/api/v1/engineering-demo/summary-review`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(5_000),
    });
    const data: unknown = await response.json().catch(() => undefined);
    if (!response.ok || !validEngineeringSummaryResult(data))
      return {
        ok: false,
        status: response.ok ? 502 : response.status,
        code: "RESULT_UNAVAILABLE",
      };
    return { ok: true, result: data };
  } catch {
    return { ok: false, status: 503, code: "DEPENDENCY_UNAVAILABLE" };
  }
}

export async function readEngineeringSummaryResult(): Promise<NextResponse> {
  const outcome = await loadEngineeringSummaryResult();
  if (!outcome.ok)
    return NextResponse.json(
      { error: { code: outcome.code, message: "The engineering preview is unavailable." } },
      { status: outcome.status, headers: { "Cache-Control": "no-store" } },
    );
  return NextResponse.json(outcome.result, { headers: { "Cache-Control": "no-store" } });
}
