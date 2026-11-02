import { NextResponse } from "next/server";

import type { EngineeringDocumentResult } from "./contracts";

const LIFECYCLE = ["UPLOADED", "VALIDATING", "ACCEPTED", "QUEUED", "PROCESSING", "NEEDS_REVIEW"];
const FIELDS = [
  "status",
  "classification",
  "ingestion_disposition",
  "lifecycle",
  "processing_status",
  "processed_pages",
  "provider",
  "external_egress",
  "document_type",
  "classification_disposition",
  "classification_reason",
  "processor_id",
  "processor_version",
  "processor_disposition",
  "candidate_disposition",
  "evidence_references",
  "structural_match",
  "source_access",
  "confidence",
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

export function validEngineeringDocumentResult(value: unknown): value is EngineeringDocumentResult {
  if (!record(value) || !exactKeys(value)) return false;
  if (
    value.status !== "NEEDS_REVIEW" ||
    value.classification !== "ENGINEERING_ONLY" ||
    value.ingestion_disposition !== "SYNTHETIC_COMPATIBLE" ||
    !Array.isArray(value.lifecycle) ||
    value.lifecycle.length !== LIFECYCLE.length ||
    !value.lifecycle.every((item, index) => item === LIFECYCLE[index]) ||
    value.processing_status !== "SUCCEEDED" ||
    value.processed_pages !== 1 ||
    value.provider !== "engineering.fixture" ||
    value.external_egress !== false ||
    value.document_type !== "LAB_REPORT" ||
    value.classification_disposition !== "SELECTED" ||
    value.classification_reason !== "EXACT_SYNTHETIC_LABEL" ||
    value.processor_id !== "LabReportProcessor" ||
    value.processor_version !== "v1" ||
    value.processor_disposition !== "NOOP_ABSTAIN" ||
    value.candidate_disposition !== "UNCONFIRMED" ||
    value.evidence_references !== 1 ||
    value.structural_match !== "STRUCTURALLY_MATCHED_UNCONFIRMED" ||
    value.source_access !== "NOT_VERIFIED" ||
    value.confidence !== "UNKNOWN" ||
    typeof value.notice !== "string" ||
    value.notice.length === 0 ||
    value.notice.length > 256
  )
    return false;
  const notice = value.notice.toLowerCase();
  return ["synthetic", "no file", "no medical value", "no clinical decision"].every((token) =>
    notice.includes(token),
  );
}

type EngineeringDocumentOutcome =
  { ok: true; result: EngineeringDocumentResult } | { ok: false; status: number; code: string };

export async function loadEngineeringDocumentResult(): Promise<EngineeringDocumentOutcome> {
  const base = backendUrl();
  if (!base) return { ok: false, status: 404, code: "FEATURE_DISABLED" };
  try {
    const response = await fetch(`${base}/api/v1/engineering-demo/document-review`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(5_000),
    });
    const data: unknown = await response.json().catch(() => undefined);
    if (!response.ok || !validEngineeringDocumentResult(data))
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

export async function readEngineeringDocumentResult(): Promise<NextResponse> {
  const outcome = await loadEngineeringDocumentResult();
  if (!outcome.ok)
    return NextResponse.json(
      {
        error: {
          code: outcome.code,
          message: "The engineering preview is unavailable.",
        },
      },
      { status: outcome.status, headers: { "Cache-Control": "no-store" } },
    );
  return NextResponse.json(outcome.result, { headers: { "Cache-Control": "no-store" } });
}
