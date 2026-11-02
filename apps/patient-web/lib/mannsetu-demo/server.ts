import { NextResponse } from "next/server";

import type { EngineeringMannSetuPreview } from "./contracts";

const FIELDS = [
  "classification",
  "authority",
  "verification",
  "extraction_status",
  "extractor_signal",
  "backstop_outcome",
  "backstop_signal",
  "precedence",
  "route",
  "reason_code",
  "policy_state",
  "clinical_meaning_assigned",
  "mental_health_assessment_performed",
  "patient_data_processed",
  "resource_contacts_available",
  "referral_created",
  "external_delivery",
  "notice",
];

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exactKeys(value: Record<string, unknown>): boolean {
  const actual = Object.keys(value).sort();
  const expected = [...FIELDS].sort();
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

export function validEngineeringMannSetuPreview(
  value: unknown,
): value is EngineeringMannSetuPreview {
  if (!record(value) || !exactKeys(value)) return false;
  if (
    value.classification !== "ENGINEERING_SYNTHETIC" ||
    value.authority !== "ENGINEERING_ONLY" ||
    value.verification !== "UNVERIFIED" ||
    value.extraction_status !== "SYNTHETIC_PARSED" ||
    value.extractor_signal !== "SYN_MH_SIGNAL_ALPHA" ||
    value.backstop_outcome !== "SYNTHETIC_MATCHED" ||
    value.backstop_signal !== "SYN_MH_SIGNAL_DELTA" ||
    value.precedence !== "SYNTHETIC_OVERRIDE" ||
    value.route !== "SYNTHETIC_ROUTE_GAMMA" ||
    value.reason_code !== "SYN_MH_POLICY_REASON_DELTA" ||
    value.policy_state !== "TEST_ONLY_ENABLED" ||
    value.clinical_meaning_assigned !== false ||
    value.mental_health_assessment_performed !== false ||
    value.patient_data_processed !== false ||
    value.resource_contacts_available !== false ||
    value.referral_created !== false ||
    value.external_delivery !== false ||
    typeof value.notice !== "string" ||
    value.notice.length === 0 ||
    value.notice.length > 320
  )
    return false;
  const notice = value.notice.toLowerCase();
  return [
    "synthetic engineering symbols only",
    "no mental-health assessment is performed",
    "no clinical meaning is assigned",
    "no resource, referral, or external delivery is available",
  ].every((token) => notice.includes(token));
}

export type EngineeringMannSetuOutcome =
  { ok: true; result: EngineeringMannSetuPreview } | { ok: false; status: number; code: string };

export async function loadEngineeringMannSetuPreview(): Promise<EngineeringMannSetuOutcome> {
  const base = backendUrl();
  if (!base) return { ok: false, status: 404, code: "FEATURE_DISABLED" };
  try {
    const response = await fetch(`${base}/api/v1/engineering-demo/mannsetu-preview`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(5_000),
    });
    const data: unknown = await response.json().catch(() => undefined);
    if (!response.ok || !validEngineeringMannSetuPreview(data))
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

export async function readEngineeringMannSetuPreview(): Promise<NextResponse> {
  const outcome = await loadEngineeringMannSetuPreview();
  if (!outcome.ok)
    return NextResponse.json(
      { error: { code: outcome.code, message: "The engineering preview is unavailable." } },
      { status: outcome.status, headers: { "Cache-Control": "no-store" } },
    );
  return NextResponse.json(outcome.result, { headers: { "Cache-Control": "no-store" } });
}
