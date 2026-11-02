import { NextResponse } from "next/server";

import type { EngineeringSelfCarePreview } from "./contracts";

const FIELDS = [
  "classification",
  "authority",
  "verification",
  "knowledge_pack_state",
  "knowledge_item_review_state",
  "source_verification",
  "placeholder_token",
  "candidate_outcome",
  "candidate_reason",
  "candidate_count",
  "blocked_outcome",
  "blocked_reason",
  "blocked_candidate_count",
  "safety_block_preserved",
  "clinical_eligibility_established",
  "guidance_text_available",
  "guidance_display_authorized",
  "rag_invoked",
  "patient_data_processed",
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

export function validEngineeringSelfCarePreview(
  value: unknown,
): value is EngineeringSelfCarePreview {
  if (!record(value) || !exactKeys(value)) return false;
  if (
    value.classification !== "ENGINEERING_SYNTHETIC" ||
    value.authority !== "ENGINEERING_ONLY" ||
    value.verification !== "UNVERIFIED" ||
    value.knowledge_pack_state !== "TEST_ONLY_UNAPPROVED" ||
    value.knowledge_item_review_state !== "TEST_ONLY_UNAPPROVED" ||
    value.source_verification !== "UNVERIFIED" ||
    value.placeholder_token !== "SYNTHETIC_PLACEHOLDER_ALPHA" ||
    value.candidate_outcome !== "SYNTHETIC_ENGINEERING_CANDIDATE" ||
    value.candidate_reason !== "SYNTHETIC_RULE_MATCH" ||
    value.candidate_count !== 1 ||
    value.blocked_outcome !== "SYNTHETIC_BLOCKED" ||
    value.blocked_reason !== "SYNTHETIC_SAFETY_BLOCK" ||
    value.blocked_candidate_count !== 0 ||
    value.safety_block_preserved !== true ||
    value.clinical_eligibility_established !== false ||
    value.guidance_text_available !== false ||
    value.guidance_display_authorized !== false ||
    value.rag_invoked !== false ||
    value.patient_data_processed !== false ||
    value.external_delivery !== false ||
    typeof value.notice !== "string" ||
    value.notice.length === 0 ||
    value.notice.length > 384
  )
    return false;
  const notice = value.notice.toLowerCase();
  return [
    "synthetic engineering placeholders only",
    "no clinical eligibility is established",
    "no guidance text is available or authorized for display",
    "no rag, patient-data processing, or external delivery occurs",
  ].every((token) => notice.includes(token));
}

export type EngineeringSelfCareOutcome =
  { ok: true; result: EngineeringSelfCarePreview } | { ok: false; status: number; code: string };

export async function loadEngineeringSelfCarePreview(): Promise<EngineeringSelfCareOutcome> {
  const base = backendUrl();
  if (!base) return { ok: false, status: 404, code: "FEATURE_DISABLED" };
  try {
    const response = await fetch(`${base}/api/v1/engineering-demo/self-care-preview`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(5_000),
    });
    const data: unknown = await response.json().catch(() => undefined);
    if (!response.ok || !validEngineeringSelfCarePreview(data))
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

export async function readEngineeringSelfCarePreview(): Promise<NextResponse> {
  const outcome = await loadEngineeringSelfCarePreview();
  if (!outcome.ok)
    return NextResponse.json(
      { error: { code: outcome.code, message: "The engineering preview is unavailable." } },
      { status: outcome.status, headers: { "Cache-Control": "no-store" } },
    );
  return NextResponse.json(outcome.result, { headers: { "Cache-Control": "no-store" } });
}
