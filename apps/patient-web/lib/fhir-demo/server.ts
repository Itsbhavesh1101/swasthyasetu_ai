import { NextResponse } from "next/server";

import type { EngineeringFHIRPreview } from "./contracts";

const FIELDS = [
  "classification",
  "authority",
  "verification",
  "fhir_version",
  "mapping_direction",
  "mapping_state",
  "resource_type",
  "structural_validation",
  "profile_validation",
  "profile_issue",
  "fhir_payload_present",
  "patient_data_processed",
  "profile_conformance_claimed",
  "exchange_authorized",
  "external_transport",
  "abdm_invoked",
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

export function validEngineeringFHIRPreview(value: unknown): value is EngineeringFHIRPreview {
  if (!record(value) || !exactKeys(value)) return false;
  if (
    value.classification !== "ENGINEERING_SYNTHETIC" ||
    value.authority !== "ENGINEERING_ONLY" ||
    value.verification !== "UNVERIFIED" ||
    value.fhir_version !== "4.0.1" ||
    value.mapping_direction !== "EXPORT" ||
    value.mapping_state !== "SYNTHETIC_EXPORT_PROJECTION" ||
    value.resource_type !== "Observation" ||
    value.structural_validation !== "SYNTHETIC_STRUCTURAL_PASS" ||
    value.profile_validation !== "SYNTHETIC_UNAVAILABLE" ||
    value.profile_issue !== "PROFILE_PACKAGE_UNAVAILABLE" ||
    value.fhir_payload_present !== false ||
    value.patient_data_processed !== false ||
    value.profile_conformance_claimed !== false ||
    value.exchange_authorized !== false ||
    value.external_transport !== false ||
    value.abdm_invoked !== false ||
    value.persistence_written !== false ||
    typeof value.notice !== "string" ||
    value.notice.length === 0 ||
    value.notice.length > 384
  )
    return false;
  const notice = value.notice.toLowerCase();
  return [
    "synthetic engineering metadata only",
    "structural mechanics are not profile conformance",
    "no fhir payload or patient data is processed",
    "no exchange, external transport, abdm integration, or persistence occurs",
  ].every((token) => notice.includes(token));
}

export type EngineeringFHIROutcome =
  { ok: true; result: EngineeringFHIRPreview } | { ok: false; status: number; code: string };

export async function loadEngineeringFHIRPreview(): Promise<EngineeringFHIROutcome> {
  const base = backendUrl();
  if (!base) return { ok: false, status: 404, code: "FEATURE_DISABLED" };
  try {
    const response = await fetch(`${base}/api/v1/engineering-demo/fhir-preview`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(5_000),
    });
    const data: unknown = await response.json().catch(() => undefined);
    if (!response.ok || !validEngineeringFHIRPreview(data))
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

export async function readEngineeringFHIRPreview(): Promise<NextResponse> {
  const outcome = await loadEngineeringFHIRPreview();
  if (!outcome.ok)
    return NextResponse.json(
      { error: { code: outcome.code, message: "The engineering preview is unavailable." } },
      { status: outcome.status, headers: { "Cache-Control": "no-store" } },
    );
  return NextResponse.json(outcome.result, { headers: { "Cache-Control": "no-store" } });
}
