import { NextRequest, NextResponse } from "next/server";

import { SESSION_ID_COOKIE, SESSION_TOKEN_COOKIE } from "../onboarding/server";
import { validateMutationOrigin } from "../security/request-origin";
import type { HistoryFactType, HistoryItem } from "./contracts";

const TIMEOUT_MS = 5_000;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const common = new Set(["fact_type", "effective_time"]);
const fields: Record<HistoryFactType, Set<string>> = {
  PROBLEM: new Set([...common, "label", "status", "onset", "resolution"]),
  MEDICATION: new Set([
    ...common,
    "name",
    "status",
    "dose",
    "dose_unit",
    "route",
    "frequency",
    "start_date",
    "end_date",
    "indication",
  ]),
  ALLERGY: new Set([...common, "substance", "status", "reaction", "severity"]),
  PROCEDURE: new Set([...common, "name", "performed_at", "facility", "notes"]),
  OBSERVATION: new Set([...common, "observation_type", "numeric_value", "text_value", "unit"]),
  INVESTIGATION: new Set([
    ...common,
    "investigation_type",
    "status",
    "performed_at",
    "result_summary",
  ]),
};
const required: Record<HistoryFactType, readonly string[]> = {
  PROBLEM: ["label", "status"],
  MEDICATION: ["name", "status"],
  ALLERGY: ["substance", "status"],
  PROCEDURE: ["name"],
  OBSERVATION: ["observation_type"],
  INVESTIGATION: ["investigation_type", "status"],
};
type RecordValue = Record<string, unknown>;

function record(value: unknown): value is RecordValue {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function response(body: unknown, status = 200) {
  const result = NextResponse.json(body, { status });
  result.headers.set("Cache-Control", "no-store");
  return result;
}

function failure(status: number, message: string) {
  return response({ error: { code: "PATIENT_HISTORY_FAILED", message } }, status);
}

function backendOrigin() {
  const configured = process.env.SWASTHYASETU_BACKEND_URL?.trim();
  if (!configured) return undefined;
  try {
    const url = new URL(configured);
    const loopback = ["localhost", "127.0.0.1", "::1"].includes(url.hostname);
    return (url.protocol === "https:" || (url.protocol === "http:" && loopback)) &&
      url.pathname === "/" &&
      !url.search &&
      !url.hash &&
      !url.username &&
      !url.password
      ? url.origin
      : undefined;
  } catch {
    return undefined;
  }
}

function credentials(request: NextRequest) {
  const sessionId = request.cookies.get(SESSION_ID_COOKIE)?.value;
  const token = request.cookies.get(SESSION_TOKEN_COOKIE)?.value;
  return sessionId && UUID.test(sessionId) && token ? token : undefined;
}

async function backend(path: string, token: string, init: RequestInit) {
  const origin = backendOrigin();
  if (!origin) return undefined;
  try {
    return await fetch(`${origin}${path}`, {
      ...init,
      cache: "no-store",
      headers: { Accept: "application/json", Authorization: `Bearer ${token}`, ...init.headers },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch {
    return undefined;
  }
}

async function json(value: Response): Promise<unknown> {
  try {
    return await value.json();
  } catch {
    return undefined;
  }
}

async function patientId(token: string): Promise<string | null | undefined> {
  const result = await backend("/api/v1/accounts/me", token, { method: "GET" });
  if (!result) return undefined;
  if (result.status === 401) return null;
  const value = await json(result);
  return result.ok &&
    record(value) &&
    typeof value.patient_id === "string" &&
    UUID.test(value.patient_id)
    ? value.patient_id
    : undefined;
}

function validPayload(value: unknown): value is RecordValue & { fact_type: HistoryFactType } {
  if (!record(value) || typeof value.fact_type !== "string" || !(value.fact_type in fields))
    return false;
  const type = value.fact_type as HistoryFactType;
  if (!Object.keys(value).every((key) => fields[type].has(key))) return false;
  if (!required[type].every((key) => typeof value[key] === "string" && value[key].length > 0))
    return false;
  if (
    type === "OBSERVATION" &&
    (value.numeric_value === undefined) === (value.text_value === undefined)
  )
    return false;
  return Object.entries(value).every(([key, item]) => {
    if (key === "fact_type") return true;
    if (item === null) return true;
    if (key === "dose" || key === "numeric_value")
      return typeof item === "string" && /^\d+(?:\.\d+)?$/.test(item);
    if (["onset", "resolution", "start_date", "end_date"].includes(key))
      return typeof item === "string" && /^\d{4}-\d{2}-\d{2}$/.test(item);
    if (["effective_time", "performed_at"].includes(key))
      return (
        typeof item === "string" &&
        !Number.isNaN(Date.parse(item)) &&
        /(?:Z|[+-]\d{2}:\d{2})$/.test(item)
      );
    return (
      typeof item === "string" && item.length > 0 && item.length <= 2000 && item === item.trim()
    );
  });
}

function historyItem(value: unknown): HistoryItem | undefined {
  if (
    !record(value) ||
    typeof value.fact_id !== "string" ||
    !UUID.test(value.fact_id) ||
    typeof value.fact_type !== "string" ||
    !(value.fact_type in fields) ||
    typeof value.canonical_label !== "string" ||
    value.canonical_label.length === 0 ||
    value.canonical_label.length > 256 ||
    value.canonical_label !== value.canonical_label.trim() ||
    (value.status !== null && (typeof value.status !== "string" || value.status.length > 64)) ||
    (value.effective_time !== null &&
      (typeof value.effective_time !== "string" ||
        Number.isNaN(Date.parse(value.effective_time)))) ||
    typeof value.recorded_at !== "string" ||
    Number.isNaN(Date.parse(value.recorded_at)) ||
    !["PATIENT_CONFIRMED", "CLINICIAN_CONFIRMED", "SUPERSEDED"].includes(
      String(value.verification_state),
    ) ||
    (value.superseded_by_fact_id !== null &&
      (typeof value.superseded_by_fact_id !== "string" || !UUID.test(value.superseded_by_fact_id)))
  )
    return undefined;
  return {
    factId: value.fact_id,
    factType: value.fact_type as HistoryFactType,
    label: value.canonical_label,
    status: value.status,
    effectiveTime: value.effective_time,
    recordedAt: value.recorded_at,
    verificationState: value.verification_state as HistoryItem["verificationState"],
    supersededByFactId: value.superseded_by_fact_id,
  };
}

async function context(request: NextRequest) {
  const token = credentials(request);
  if (!token) return { state: "ANONYMOUS" as const };
  const id = await patientId(token);
  if (id === null) return { state: "ANONYMOUS" as const };
  if (!id) return { state: "UNAVAILABLE" as const };
  return { state: "AUTHENTICATED" as const, token, patientId: id };
}

export async function readHistory(request: NextRequest) {
  const current = await context(request);
  if (current.state === "ANONYMOUS") return response({ state: "ANONYMOUS" }, 401);
  if (current.state !== "AUTHENTICATED") return failure(503, "Your history is unavailable.");
  const result = await backend(
    `/api/v1/patients/${current.patientId}/facts?limit=100`,
    current.token,
    { method: "GET" },
  );
  if (!result) return failure(503, "Your history is unavailable.");
  const data = await json(result);
  if (!result.ok || !record(data) || !Array.isArray(data.items))
    return failure(result.status === 401 ? 401 : 502, "Your history could not be loaded.");
  const items = data.items.map(historyItem);
  if (items.some((item) => item === undefined))
    return failure(502, "Your history could not be loaded.");
  return response({ state: "AUTHENTICATED", items });
}

async function mutate(request: NextRequest, factId?: string) {
  const originFailure = validateMutationOrigin(request);
  if (originFailure)
    return response(
      { error: { code: originFailure.code, message: originFailure.message } },
      originFailure.status,
    );
  if (factId !== undefined && !UUID.test(factId)) return failure(400, "The entry is invalid.");
  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return failure(400, "Check the history details and try again.");
  }
  if (!validPayload(payload)) return failure(400, "Check the history details and try again.");
  const current = await context(request);
  if (current.state === "ANONYMOUS") return response({ state: "ANONYMOUS" }, 401);
  if (current.state !== "AUTHENTICATED") return failure(503, "Your history is unavailable.");
  const path =
    factId === undefined
      ? `/api/v1/patients/${current.patientId}/facts`
      : `/api/v1/patients/${current.patientId}/facts/${factId}/supersede`;
  const result = await backend(path, current.token, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(
      factId === undefined ? payload : { expected_current_id: factId, replacement: payload },
    ),
  });
  if (!result) return failure(503, "Your history is unavailable.");
  if (!result.ok)
    return failure(
      result.status === 409 ? 409 : result.status === 401 ? 401 : 502,
      result.status === 409
        ? "This entry changed. Reload your history and try again."
        : "The history entry could not be saved.",
    );
  const data = await json(result);
  const item = historyItem(
    factId === undefined ? data : record(data) ? data.replacement : undefined,
  );
  return item
    ? response({ state: "AUTHENTICATED", item }, factId === undefined ? 201 : 200)
    : failure(502, "The history entry could not be saved.");
}

export const addHistory = (request: NextRequest) => mutate(request);
export const supersedeHistory = (request: NextRequest, factId: string) => mutate(request, factId);
