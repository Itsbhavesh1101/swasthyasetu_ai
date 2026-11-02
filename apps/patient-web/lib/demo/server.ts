import { NextRequest, NextResponse } from "next/server";

import { SESSION_TOKEN_COOKIE } from "../onboarding/server";
import type { EngineeringDemoResult } from "./contracts";

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const TOKEN = /^[A-Z][A-Z0-9_]{0,63}$/;
const SAFE_ROUTES = new Set([
  "EMERGENCY",
  "PRIORITY_REVIEW",
  "ROUTINE_CARE",
  "SUPPORTED_SELF_CARE",
  "CLARIFICATION_REQUIRED",
]);

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exact(value: Record<string, unknown>, expected: string[]): boolean {
  const keys = Object.keys(value).sort();
  const expectedKeys = [...expected].sort();
  return (
    keys.length === expectedKeys.length && keys.every((key, index) => key === expectedKeys[index])
  );
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

function validSafety(value: unknown): boolean {
  if (!record(value)) return false;
  const route = value.route;
  const reasons = value.reason_codes;
  if (
    typeof route !== "string" ||
    !SAFE_ROUTES.has(route) ||
    !Array.isArray(reasons) ||
    reasons.length === 0 ||
    reasons.length > 16 ||
    !reasons.every((item) => typeof item === "string" && TOKEN.test(item)) ||
    new Set(reasons).size !== reasons.length ||
    reasons.some((item, index) => index > 0 && reasons[index - 1] >= item)
  )
    return false;
  const requiresClarification = value.requires_clarification;
  const blocksSelfCare = value.blocks_self_care;
  const routeFlagsMatch =
    typeof requiresClarification === "boolean" &&
    typeof blocksSelfCare === "boolean" &&
    (route === "CLARIFICATION_REQUIRED"
      ? requiresClarification && blocksSelfCare
      : !requiresClarification &&
        (route === "SUPPORTED_SELF_CARE" ? !blocksSelfCare : blocksSelfCare));
  return (
    exact(value, [
      "route",
      "reason_codes",
      "policy_id",
      "policy_version",
      "requires_clarification",
      "blocks_self_care",
      "created_at",
    ]) &&
    value.policy_id === "synthetic-physical-safety-metadata" &&
    value.policy_version === "engineering.1" &&
    routeFlagsMatch &&
    typeof value.created_at === "string" &&
    /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$/.test(value.created_at)
  );
}

export function validEngineeringDemoResult(value: unknown): value is EngineeringDemoResult {
  if (!record(value)) return false;
  if (
    !exact(value, [
      "intake_id",
      "encounter_id",
      "status",
      "classification",
      "extracted_label",
      "verification_state",
      "safety_decision",
      "summary_sections",
      "notice",
    ]) ||
    typeof value.intake_id !== "string" ||
    !UUID.test(value.intake_id) ||
    typeof value.encounter_id !== "string" ||
    !UUID.test(value.encounter_id) ||
    typeof value.status !== "string" ||
    !["SYNTHETIC_PREVIEW", "ABSTAINED"].includes(value.status) ||
    value.classification !== "ENGINEERING_ONLY" ||
    typeof value.notice !== "string" ||
    value.notice.length === 0 ||
    value.notice.length > 256 ||
    !Array.isArray(value.summary_sections) ||
    value.summary_sections.length > 10
  )
    return false;
  const preview = value.status === "SYNTHETIC_PREVIEW";
  if (
    preview !== (value.extracted_label === "SYNTHETIC_PAIN") ||
    preview !== (value.verification_state === "AI_EXTRACTED_UNCONFIRMED") ||
    preview !== validSafety(value.safety_decision)
  )
    return false;
  if (preview !== (value.summary_sections.length === 1)) return false;
  return value.summary_sections.every(
    (section) =>
      record(section) &&
      exact(section, ["section_id", "readiness", "labels", "review_required"]) &&
      section.section_id === "CHIEF_COMPLAINT" &&
      section.readiness === "UNVERIFIED" &&
      Array.isArray(section.labels) &&
      section.labels.length === 1 &&
      section.labels.every((label) => label === "SYNTHETIC_PAIN") &&
      section.review_required === false,
  );
}

export async function readEngineeringDemo(
  request: NextRequest,
  intakeId: string,
): Promise<NextResponse> {
  const token = request.cookies.get(SESSION_TOKEN_COOKIE)?.value;
  const base = backendUrl();
  if (!UUID.test(intakeId) || !token || !base)
    return NextResponse.json(
      { error: { code: "FEATURE_DISABLED", message: "The synthetic preview is unavailable." } },
      { status: 404, headers: { "Cache-Control": "no-store" } },
    );
  try {
    const response = await fetch(
      `${base}/api/v1/engineering-demo/intakes/${encodeURIComponent(intakeId)}/result`,
      {
        headers: { Accept: "application/json", Authorization: `Bearer ${token}` },
        cache: "no-store",
        signal: AbortSignal.timeout(5_000),
      },
    );
    const data: unknown = await response.json().catch(() => undefined);
    if (!response.ok || !validEngineeringDemoResult(data))
      return NextResponse.json(
        { error: { code: "RESULT_UNAVAILABLE", message: "The synthetic preview is unavailable." } },
        { status: response.ok ? 502 : response.status, headers: { "Cache-Control": "no-store" } },
      );
    return NextResponse.json(data, { headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json(
      {
        error: { code: "DEPENDENCY_UNAVAILABLE", message: "The synthetic preview is unavailable." },
      },
      { status: 503, headers: { "Cache-Control": "no-store" } },
    );
  }
}
