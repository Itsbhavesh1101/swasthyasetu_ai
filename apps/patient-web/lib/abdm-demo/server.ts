import { NextResponse } from "next/server";

import type { EngineeringABDMPreview } from "./contracts";

const FIELDS = [
  "classification",
  "authority",
  "verification",
  "mode",
  "operation",
  "scripted_state",
  "scripted_issue",
  "unknown_state",
  "unknown_issue",
  "zero_egress",
  "official_protocol_adopted",
  "abha_identity_processed",
  "consent_evaluated",
  "fhir_payload_present",
  "sandbox_connected",
  "patient_data_processed",
  "local_intake_accessed",
  "local_intake_mutated",
  "external_transport",
  "persistence_written",
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

export function validEngineeringABDMPreview(value: unknown): value is EngineeringABDMPreview {
  if (!record(value) || !exactKeys(value)) return false;
  if (
    value.classification !== "ENGINEERING_SYNTHETIC" ||
    value.authority !== "ENGINEERING_ONLY" ||
    value.verification !== "UNVERIFIED" ||
    value.mode !== "SYNTHETIC_OFFLINE_MOCK" ||
    value.operation !== "SYNTHETIC_OPERATION_ALPHA" ||
    value.scripted_state !== "SYNTHETIC_REJECTED" ||
    value.scripted_issue !== "SYNTHETIC_REJECTED" ||
    value.unknown_state !== "SYNTHETIC_UNAVAILABLE" ||
    value.unknown_issue !== "SYNTHETIC_UNAVAILABLE" ||
    value.zero_egress !== true ||
    value.official_protocol_adopted !== false ||
    value.abha_identity_processed !== false ||
    value.consent_evaluated !== false ||
    value.fhir_payload_present !== false ||
    value.sandbox_connected !== false ||
    value.patient_data_processed !== false ||
    value.local_intake_accessed !== false ||
    value.local_intake_mutated !== false ||
    value.external_transport !== false ||
    value.persistence_written !== false ||
    typeof value.notice !== "string" ||
    value.notice.length === 0 ||
    value.notice.length > 384
  )
    return false;
  const notice = value.notice.toLowerCase();
  return [
    "synthetic offline engineering tokens only",
    "no official abdm protocol or abha identity is used",
    "no consent or fhir payload is processed",
    "no sandbox, patient data, local intake, network transport, or persistence is accessed",
  ].every((token) => notice.includes(token));
}

export type EngineeringABDMOutcome =
  { ok: true; result: EngineeringABDMPreview } | { ok: false; status: number; code: string };

export async function loadEngineeringABDMPreview(): Promise<EngineeringABDMOutcome> {
  const base = backendUrl();
  if (!base) return { ok: false, status: 404, code: "FEATURE_DISABLED" };
  try {
    const response = await fetch(`${base}/api/v1/engineering-demo/abdm-preview`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(5_000),
    });
    const data: unknown = await response.json().catch(() => undefined);
    if (!response.ok || !validEngineeringABDMPreview(data))
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

export async function readEngineeringABDMPreview(): Promise<NextResponse> {
  const outcome = await loadEngineeringABDMPreview();
  if (!outcome.ok)
    return NextResponse.json(
      { error: { code: outcome.code, message: "The engineering preview is unavailable." } },
      { status: outcome.status, headers: { "Cache-Control": "no-store" } },
    );
  return NextResponse.json(outcome.result, { headers: { "Cache-Control": "no-store" } });
}
