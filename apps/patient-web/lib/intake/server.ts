import { NextRequest, NextResponse } from "next/server";

import {
  SESSION_ID_COOKIE,
  SESSION_TOKEN_COOKIE,
  sessionCookieOptions,
} from "../onboarding/server";
import type { IntakeView } from "./contracts";

const REQUEST_TIMEOUT_MS = 5_000;
const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const ANSWER_TYPES = new Set([
  "TEXT",
  "SINGLE_CHOICE",
  "MULTI_CHOICE",
  "BOOLEAN",
  "NUMBER",
  "DATE",
  "DURATION",
  "SEVERITY_SCALE",
]);
const RESPONSE_DISPOSITIONS = new Set(["ANSWERED", "UNKNOWN", "PREFER_NOT_TO_ANSWER", "SKIPPED"]);
const ENGINE_STATES = new Set([
  "NEXT_QUESTION",
  "CLARIFICATION_REQUIRED",
  "INCOMPLETE",
  "COMPLETION_READY",
]);
const REQUIREDNESS = new Set(["REQUIRED", "OPTIONAL", "CONDITIONAL"]);
const SAFE_CODES = new Set([
  "AUTHENTICATION_REQUIRED",
  "AUTHORIZATION_DENIED",
  "CONSENT_REQUIRED",
  "DEPENDENCY_TIMEOUT",
  "DEPENDENCY_UNAVAILABLE",
  "FEATURE_DISABLED",
  "INSUFFICIENT_INFORMATION",
  "INVALID_STATE_TRANSITION",
  "POLICY_UNAVAILABLE",
  "PROCESSING_FAILED",
  "RESOURCE_CONFLICT",
  "RESOURCE_NOT_FOUND",
  "SESSION_EXPIRED",
  "VALIDATION_ERROR",
]);

type RecordValue = Record<string, unknown>;
type Credentials = { sessionId: string; token: string };
type BackendResult = { ok: boolean; status: number; data: unknown; errorCode?: string };

function record(value: unknown): value is RecordValue {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exactKeys(value: RecordValue, keys: readonly string[]): boolean {
  const actual = Object.keys(value).sort();
  const expected = [...keys].sort();
  return actual.length === expected.length && actual.every((key, index) => key === expected[index]);
}

function boundedString(value: unknown, maximum: number, allowEmpty = false): value is string {
  return typeof value === "string" && value.length <= maximum && (allowEmpty || value.length > 0);
}

function finiteNumeric(value: unknown): value is string | number {
  if (typeof value === "number") return Number.isFinite(value);
  return (
    typeof value === "string" &&
    value.length > 0 &&
    value.length <= 64 &&
    /^-?(?:\d+\.?\d*|\.\d+)$/.test(value) &&
    Number.isFinite(Number(value))
  );
}

function nullableFiniteNumeric(value: unknown): boolean {
  return value === null || finiteNumeric(value);
}

function isoDate(value: unknown): value is string {
  return (
    typeof value === "string" &&
    /^\d{4}-\d{2}-\d{2}$/.test(value) &&
    !Number.isNaN(Date.parse(`${value}T00:00:00Z`))
  );
}

function stringArray(value: unknown, maximum = 64): value is string[] {
  return (
    Array.isArray(value) &&
    value.length <= maximum &&
    value.every((item) => boundedString(item, 128)) &&
    new Set(value).size === value.length
  );
}

function validConstraints(value: RecordValue, answerType: string): boolean {
  switch (answerType) {
    case "TEXT":
      return (
        exactKeys(value, ["min_length", "max_length"]) &&
        Number.isInteger(value.min_length) &&
        Number(value.min_length) >= 0 &&
        Number.isInteger(value.max_length) &&
        Number(value.max_length) >= Number(value.min_length) &&
        Number(value.max_length) <= 4_000
      );
    case "SINGLE_CHOICE":
    case "MULTI_CHOICE":
      return (
        exactKeys(value, ["allowed_option_ids"]) &&
        stringArray(value.allowed_option_ids) &&
        value.allowed_option_ids.length > 0
      );
    case "BOOLEAN":
      return exactKeys(value, []);
    case "NUMBER":
      return (
        exactKeys(value, ["minimum", "maximum", "unit"]) &&
        nullableFiniteNumeric(value.minimum) &&
        nullableFiniteNumeric(value.maximum) &&
        (value.unit === null || boundedString(value.unit, 32)) &&
        (value.minimum === null ||
          value.maximum === null ||
          Number(value.minimum) <= Number(value.maximum))
      );
    case "DATE":
      return (
        exactKeys(value, ["earliest", "latest"]) &&
        (value.earliest === null || isoDate(value.earliest)) &&
        (value.latest === null || isoDate(value.latest)) &&
        (value.earliest === null || value.latest === null || value.earliest <= value.latest)
      );
    case "DURATION":
      return (
        exactKeys(value, ["allowed_units", "minimum", "maximum"]) &&
        stringArray(value.allowed_units) &&
        value.allowed_units.length > 0 &&
        finiteNumeric(value.minimum) &&
        Number(value.minimum) >= 0 &&
        nullableFiniteNumeric(value.maximum) &&
        (value.maximum === null || Number(value.minimum) <= Number(value.maximum))
      );
    case "SEVERITY_SCALE":
      return (
        exactKeys(value, ["scale_id", "scale_version", "allowed_values"]) &&
        boundedString(value.scale_id, 128) &&
        boundedString(value.scale_version, 64) &&
        Array.isArray(value.allowed_values) &&
        value.allowed_values.length > 0 &&
        value.allowed_values.length <= 64 &&
        value.allowed_values.every(finiteNumeric)
      );
    default:
      return false;
  }
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

function credentials(request: NextRequest): Credentials | undefined {
  const sessionId = request.cookies.get(SESSION_ID_COOKIE)?.value;
  const token = request.cookies.get(SESSION_TOKEN_COOKIE)?.value;
  return sessionId && token && UUID_PATTERN.test(sessionId) ? { sessionId, token } : undefined;
}

function json(value: unknown, status = 200): NextResponse {
  const response = NextResponse.json(value, { status });
  response.headers.set("Cache-Control", "no-store");
  return response;
}

function error(code: string, message: string, status: number): NextResponse {
  return json({ error: { code, message } }, status);
}

function rejectOrigin(request: NextRequest): NextResponse | undefined {
  const origin = request.headers.get("origin");
  const host = request.headers.get("host");
  const expected = host ? `${request.nextUrl.protocol}//${host}` : request.nextUrl.origin;
  return origin && origin !== expected
    ? error("ORIGIN_REJECTED", "This request origin is not allowed.", 403)
    : undefined;
}

async function body(request: NextRequest): Promise<unknown> {
  const length = Number(request.headers.get("content-length") ?? "0");
  if (length > 16_384) return undefined;
  try {
    return await request.json();
  } catch {
    return undefined;
  }
}

async function backend(
  path: string,
  token: string,
  method: "GET" | "POST",
  payload?: unknown,
): Promise<BackendResult | undefined> {
  const base = backendUrl();
  if (!base) return undefined;
  const headers: Record<string, string> = {
    Accept: "application/json",
    Authorization: `Bearer ${token}`,
  };
  if (payload !== undefined) headers["Content-Type"] = "application/json";
  try {
    const requestInit: RequestInit = {
      method,
      headers,
      cache: "no-store",
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
    };
    if (payload !== undefined) requestInit.body = JSON.stringify(payload);
    const response = await fetch(`${base}${path}`, requestInit);
    let data: unknown;
    try {
      data = await response.json();
    } catch {
      data = undefined;
    }
    const code =
      record(data) && record(data.error) && typeof data.error.code === "string"
        ? data.error.code
        : undefined;
    return {
      ok: response.ok,
      status: response.status,
      data,
      ...(code && SAFE_CODES.has(code) ? { errorCode: code } : {}),
    };
  } catch {
    return { ok: false, status: 503, data: undefined, errorCode: "DEPENDENCY_UNAVAILABLE" };
  }
}

function validQuestion(value: unknown): boolean {
  if (!record(value)) return false;
  const constraints = record(value.constraints) ? value.constraints : undefined;
  const allowedOptionIds = constraints?.allowed_option_ids;
  return (
    exactKeys(value, [
      "question_id",
      "question_version",
      "pack_id",
      "pack_version",
      "section",
      "prompt",
      "help_text",
      "answer_type",
      "requiredness",
      "allow_unknown",
      "allow_prefer_not_to_answer",
      "allow_skip",
      "constraints",
      "options",
    ]) &&
    boundedString(value.question_id, 128) &&
    boundedString(value.question_version, 128) &&
    boundedString(value.pack_id, 128) &&
    boundedString(value.pack_version, 128) &&
    boundedString(value.section, 64) &&
    boundedString(value.prompt, 2_000) &&
    (value.help_text === null || boundedString(value.help_text, 2_000)) &&
    typeof value.answer_type === "string" &&
    ANSWER_TYPES.has(value.answer_type) &&
    typeof value.requiredness === "string" &&
    REQUIREDNESS.has(value.requiredness) &&
    typeof value.allow_unknown === "boolean" &&
    typeof value.allow_prefer_not_to_answer === "boolean" &&
    typeof value.allow_skip === "boolean" &&
    constraints !== undefined &&
    validConstraints(constraints, value.answer_type) &&
    Array.isArray(value.options) &&
    value.options.every(
      (item) =>
        record(item) &&
        exactKeys(item, ["id", "label"]) &&
        boundedString(item.id, 128) &&
        boundedString(item.label, 512),
    ) &&
    (!["SINGLE_CHOICE", "MULTI_CHOICE"].includes(value.answer_type) ||
      (value.options.length > 0 &&
        stringArray(allowedOptionIds) &&
        value.options.length === allowedOptionIds.length &&
        value.options.every((item) => allowedOptionIds.includes(item.id))))
  );
}

function validAnswer(value: unknown): boolean {
  if (
    !record(value) ||
    !exactKeys(value, [
      "answer_id",
      "question_id",
      "question_version",
      "answer_type",
      "value",
      "selected_option_ids",
      "unit",
      "response_disposition",
      "source_label",
    ]) ||
    !boundedString(value.answer_id, 36) ||
    !UUID_PATTERN.test(value.answer_id) ||
    !boundedString(value.question_id, 128) ||
    !boundedString(value.question_version, 128) ||
    typeof value.answer_type !== "string" ||
    !ANSWER_TYPES.has(value.answer_type) ||
    typeof value.response_disposition !== "string" ||
    !RESPONSE_DISPOSITIONS.has(value.response_disposition) ||
    value.source_label !== "Patient provided"
  )
    return false;
  if (value.response_disposition !== "ANSWERED")
    return value.value === null && value.selected_option_ids === null && value.unit === null;
  switch (value.answer_type) {
    case "TEXT":
      return (
        boundedString(value.value, 4_000, true) &&
        value.selected_option_ids === null &&
        value.unit === null
      );
    case "SINGLE_CHOICE":
      return (
        value.value === null &&
        stringArray(value.selected_option_ids) &&
        value.selected_option_ids.length === 1 &&
        value.unit === null
      );
    case "MULTI_CHOICE":
      return (
        value.value === null &&
        stringArray(value.selected_option_ids) &&
        value.selected_option_ids.length > 0 &&
        value.unit === null
      );
    case "BOOLEAN":
      return (
        typeof value.value === "boolean" &&
        value.selected_option_ids === null &&
        value.unit === null
      );
    case "DATE":
      return isoDate(value.value) && value.selected_option_ids === null && value.unit === null;
    case "NUMBER":
      return (
        finiteNumeric(value.value) &&
        value.selected_option_ids === null &&
        (value.unit === null || boundedString(value.unit, 32))
      );
    case "DURATION":
      return (
        finiteNumeric(value.value) &&
        Number(value.value) >= 0 &&
        value.selected_option_ids === null &&
        boundedString(value.unit, 32)
      );
    case "SEVERITY_SCALE":
      return (
        finiteNumeric(value.value) && value.selected_option_ids === null && value.unit === null
      );
    default:
      return false;
  }
}

export function validIntake(value: unknown): value is IntakeView {
  return (
    record(value) &&
    exactKeys(value, [
      "intake_id",
      "encounter_id",
      "status",
      "version",
      "started_at",
      "completed_at",
      "pack_versions",
      "current_question",
      "engine_state",
      "completion_ready",
      "answers",
      "missing_information",
    ]) &&
    typeof value.intake_id === "string" &&
    UUID_PATTERN.test(value.intake_id) &&
    typeof value.encounter_id === "string" &&
    UUID_PATTERN.test(value.encounter_id) &&
    ["IN_PROGRESS", "COMPLETED", "ABANDONED"].includes(String(value.status)) &&
    Number.isInteger(value.version) &&
    Number(value.version) > 0 &&
    typeof value.started_at === "string" &&
    !Number.isNaN(Date.parse(value.started_at)) &&
    (value.completed_at === null ||
      (typeof value.completed_at === "string" && !Number.isNaN(Date.parse(value.completed_at)))) &&
    Array.isArray(value.pack_versions) &&
    value.pack_versions.every(
      (item) =>
        record(item) &&
        exactKeys(item, ["pack_id", "pack_version"]) &&
        boundedString(item.pack_id, 128) &&
        boundedString(item.pack_version, 128),
    ) &&
    (value.current_question === null || validQuestion(value.current_question)) &&
    typeof value.engine_state === "string" &&
    ENGINE_STATES.has(value.engine_state) &&
    typeof value.completion_ready === "boolean" &&
    value.completion_ready === (value.engine_state === "COMPLETION_READY") &&
    Array.isArray(value.answers) &&
    value.answers.every(validAnswer) &&
    Array.isArray(value.missing_information) &&
    value.missing_information.every(
      (item) =>
        record(item) &&
        exactKeys(item, ["field_or_question_key", "reason_code", "requiredness"]) &&
        boundedString(item.field_or_question_key, 128) &&
        [
          "REQUIRED_UNANSWERED",
          "CONDITIONAL_UNANSWERED",
          "RECONFIRMATION_REQUIRED",
          "CLARIFICATION_REQUIRED",
        ].includes(String(item.reason_code)) &&
        typeof item.requiredness === "string" &&
        REQUIREDNESS.has(item.requiredness),
    )
  );
}

function clearInvalidSession(request: NextRequest, response: NextResponse): NextResponse {
  const host = request.nextUrl.hostname;
  const options = sessionCookieOptions(host);
  response.cookies.set(SESSION_ID_COOKIE, "", { ...options, maxAge: 0 });
  response.cookies.set(SESSION_TOKEN_COOKIE, "", { ...options, maxAge: 0 });
  return response;
}

function backendError(request: NextRequest, result: BackendResult): NextResponse {
  const code = result.errorCode ?? "BACKEND_REQUEST_FAILED";
  const invalidSession =
    result.status === 401 || ["SESSION_EXPIRED", "AUTHENTICATION_REQUIRED"].includes(code);
  const response = error(
    code,
    code === "RESOURCE_CONFLICT"
      ? "This intake changed. Refresh and review the latest saved draft."
      : code === "CONSENT_REQUIRED"
        ? "Consent is required before continuing this intake."
        : code === "POLICY_UNAVAILABLE" || code === "FEATURE_DISABLED"
          ? "Intake content is not available for this session."
          : "The intake request could not be completed.",
    result.status >= 400 && result.status < 600 ? result.status : 502,
  );
  return invalidSession ? clearInvalidSession(request, response) : response;
}

async function relay(
  request: NextRequest,
  path: string,
  method: "GET" | "POST",
  payload?: unknown,
): Promise<NextResponse> {
  const current = credentials(request);
  if (!current) return error("SESSION_UNAVAILABLE", "Start a private session first.", 401);
  const result = await backend(path, current.token, method, payload);
  if (!result) return error("BACKEND_UNAVAILABLE", "The intake service is unavailable.", 503);
  if (!result.ok) return backendError(request, result);
  return validIntake(result.data)
    ? json(result.data, result.status)
    : error("INVALID_BACKEND_RESPONSE", "The intake response could not be verified.", 502);
}

export async function startEncounterIntake(
  request: NextRequest,
  encounterId: string,
): Promise<NextResponse> {
  const origin = rejectOrigin(request);
  if (origin) return origin;
  if (!UUID_PATTERN.test(encounterId))
    return error("VALIDATION_ERROR", "The encounter ID is invalid.", 400);
  return relay(request, `/api/v1/encounters/${encodeURIComponent(encounterId)}/intake`, "POST", {
    pack_ids: ["core.intake"],
  });
}

export async function createEncounterAndIntake(request: NextRequest): Promise<NextResponse> {
  const origin = rejectOrigin(request);
  if (origin) return origin;
  const current = credentials(request);
  if (!current) return error("SESSION_UNAVAILABLE", "Start a private session first.", 401);
  const created = await backend("/api/v1/encounters/general-intake", current.token, "POST", {
    session_id: current.sessionId,
  });
  if (!created) return error("BACKEND_UNAVAILABLE", "The intake service is unavailable.", 503);
  if (!created.ok || !record(created.data) || typeof created.data.encounter_id !== "string")
    return created.ok
      ? error("INVALID_BACKEND_RESPONSE", "The encounter response could not be verified.", 502)
      : backendError(request, created);
  return relay(
    request,
    `/api/v1/encounters/${encodeURIComponent(created.data.encounter_id)}/intake`,
    "POST",
    { pack_ids: ["core.intake"] },
  );
}

export async function readIntake(request: NextRequest, intakeId: string): Promise<NextResponse> {
  if (!UUID_PATTERN.test(intakeId))
    return error("VALIDATION_ERROR", "The intake ID is invalid.", 400);
  return relay(request, `/api/v1/intakes/${encodeURIComponent(intakeId)}`, "GET");
}

export async function answerIntake(request: NextRequest, intakeId: string): Promise<NextResponse> {
  const origin = rejectOrigin(request);
  if (origin) return origin;
  const payload = await body(request);
  if (!record(payload)) return error("VALIDATION_ERROR", "The answer request is invalid.", 400);
  return relay(request, `/api/v1/intakes/${encodeURIComponent(intakeId)}/answers`, "POST", payload);
}

export async function completeIntake(
  request: NextRequest,
  intakeId: string,
): Promise<NextResponse> {
  const origin = rejectOrigin(request);
  if (origin) return origin;
  const payload = await body(request);
  if (!record(payload) || !Number.isInteger(payload.expected_version))
    return error("VALIDATION_ERROR", "The completion request is invalid.", 400);
  return relay(
    request,
    `/api/v1/intakes/${encodeURIComponent(intakeId)}/complete`,
    "POST",
    payload,
  );
}
