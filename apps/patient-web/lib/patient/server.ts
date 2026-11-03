import { NextRequest, NextResponse } from "next/server";

import { SESSION_ID_COOKIE, SESSION_TOKEN_COOKIE } from "../onboarding/server";
import { validateMutationOrigin } from "../security/request-origin";
import type { PatientDemographics, PatientProfile, PatientProfileSubmission } from "./contracts";

const TIMEOUT_MS = 5_000;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const profileKeys = new Set([
  "expectedUpdatedAt",
  "preferredLanguage",
  "displayName",
  "demographics",
]);
const demographicKeys = new Set([
  "dateOfBirth",
  "administrativeSex",
  "genderIdentity",
  "pregnancyStatus",
  "locationContext",
  "heightCm",
  "weightKg",
]);
const backendDemographicKeys = new Set([
  "date_of_birth",
  "age_years",
  "administrative_sex",
  "gender_identity",
  "pregnancy_status",
  "location_context",
  "height_cm",
  "weight_kg",
  "bmi",
]);
type RecordValue = Record<string, unknown>;

function record(value: unknown): value is RecordValue {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function exactKeys(value: RecordValue, allowed: Set<string>) {
  return Object.keys(value).every((key) => allowed.has(key));
}

function response(body: unknown, status = 200) {
  const result = NextResponse.json(body, { status });
  result.headers.set("Cache-Control", "no-store");
  return result;
}

function failure(status: number, message: string) {
  return response({ error: { code: "PATIENT_PROFILE_FAILED", message } }, status);
}

function backendOrigin(): string | undefined {
  const configured = process.env.SWASTHYASETU_BACKEND_URL?.trim();
  if (!configured) return undefined;
  try {
    const url = new URL(configured);
    const loopback = ["localhost", "127.0.0.1", "::1"].includes(url.hostname);
    if (
      (url.protocol !== "https:" && !(url.protocol === "http:" && loopback)) ||
      url.pathname !== "/" ||
      url.search ||
      url.hash ||
      url.username ||
      url.password
    )
      return undefined;
    return url.origin;
  } catch {
    return undefined;
  }
}

function credentials(request: NextRequest) {
  const sessionId = request.cookies.get(SESSION_ID_COOKIE)?.value;
  const token = request.cookies.get(SESSION_TOKEN_COOKIE)?.value;
  return sessionId && UUID.test(sessionId) && token ? { token } : undefined;
}

async function backend(path: string, token: string, init: RequestInit) {
  const origin = backendOrigin();
  if (!origin) return undefined;
  try {
    return await fetch(`${origin}${path}`, {
      ...init,
      cache: "no-store",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
        ...init.headers,
      },
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

type CurrentAccount = { patientId: string; displayName: string | null; profileComplete: boolean };

async function currentAccount(token: string): Promise<CurrentAccount | undefined | null> {
  const result = await backend("/api/v1/accounts/me", token, { method: "GET" });
  if (!result) return undefined;
  const data = await json(result);
  if (result.status === 401) return null;
  return result.ok &&
    record(data) &&
    typeof data.patient_id === "string" &&
    UUID.test(data.patient_id) &&
    (data.display_name === null || typeof data.display_name === "string") &&
    typeof data.profile_complete === "boolean"
    ? {
        patientId: data.patient_id,
        displayName: data.display_name,
        profileComplete: data.profile_complete,
      }
    : undefined;
}

function nullableText(value: unknown, maximum: number): value is string | null {
  return (
    value === null ||
    (typeof value === "string" &&
      value.length > 0 &&
      value.length <= maximum &&
      value === value.trim())
  );
}

function validDemographics(value: unknown): value is PatientDemographics {
  return (
    record(value) &&
    exactKeys(value, demographicKeys) &&
    nullableText(value.dateOfBirth, 10) &&
    (value.dateOfBirth === null || /^\d{4}-\d{2}-\d{2}$/.test(value.dateOfBirth)) &&
    nullableText(value.administrativeSex, 256) &&
    nullableText(value.genderIdentity, 256) &&
    nullableText(value.pregnancyStatus, 256) &&
    nullableText(value.locationContext, 256) &&
    (value.heightCm === null ||
      (typeof value.heightCm === "number" && value.heightCm >= 30 && value.heightCm <= 275)) &&
    (value.weightKg === null ||
      (typeof value.weightKg === "number" && value.weightKg >= 1 && value.weightKg <= 700))
  );
}

function submission(value: unknown): value is PatientProfileSubmission {
  return (
    record(value) &&
    exactKeys(value, profileKeys) &&
    typeof value.expectedUpdatedAt === "string" &&
    !Number.isNaN(Date.parse(value.expectedUpdatedAt)) &&
    /(?:Z|[+-]\d{2}:\d{2})$/.test(value.expectedUpdatedAt) &&
    nullableText(value.preferredLanguage, 64) &&
    typeof value.displayName === "string" &&
    value.displayName === value.displayName.trim() &&
    value.displayName.length > 0 &&
    value.displayName.length <= 120 &&
    validDemographics(value.demographics)
  );
}

function profile(value: unknown, account: CurrentAccount): PatientProfile | undefined {
  if (
    !record(value) ||
    typeof value.patient_id !== "string" ||
    !UUID.test(value.patient_id) ||
    !["ACTIVE", "INACTIVE", "MERGED", "DELETED_PENDING"].includes(String(value.status)) ||
    !nullableText(value.preferred_language, 64) ||
    typeof value.updated_at !== "string" ||
    Number.isNaN(Date.parse(value.updated_at))
  )
    return undefined;
  const raw = value.demographics;
  if (raw !== null && !record(raw)) return undefined;
  if (
    raw !== null &&
    (!exactKeys(raw, backendDemographicKeys) ||
      !nullableText(raw.date_of_birth, 10) ||
      (raw.date_of_birth !== null && !/^\d{4}-\d{2}-\d{2}$/.test(raw.date_of_birth)) ||
      (raw.age_years !== null &&
        (typeof raw.age_years !== "number" ||
          !Number.isInteger(raw.age_years) ||
          raw.age_years < 0)) ||
      !nullableText(raw.administrative_sex, 256) ||
      !nullableText(raw.gender_identity, 256) ||
      !nullableText(raw.pregnancy_status, 256) ||
      !nullableText(raw.location_context, 256) ||
      (raw.height_cm !== null && typeof raw.height_cm !== "number") ||
      (raw.weight_kg !== null && typeof raw.weight_kg !== "number") ||
      (raw.bmi !== null && typeof raw.bmi !== "number"))
  )
    return undefined;
  const demographics =
    raw === null
      ? null
      : {
          dateOfBirth: raw.date_of_birth as string | null,
          administrativeSex: raw.administrative_sex as string | null,
          genderIdentity: raw.gender_identity as string | null,
          pregnancyStatus: raw.pregnancy_status as string | null,
          locationContext: raw.location_context as string | null,
          heightCm: raw.height_cm as number | null,
          weightKg: raw.weight_kg as number | null,
          bmi: raw.bmi as number | null,
        };
  return {
    patientId: value.patient_id,
    status: value.status as PatientProfile["status"],
    preferredLanguage: value.preferred_language,
    displayName: account.displayName,
    profileComplete: account.profileComplete,
    demographics,
    updatedAt: value.updated_at,
  };
}

export async function readPatientProfile(request: NextRequest) {
  const current = credentials(request);
  if (!current) return response({ state: "ANONYMOUS" }, 401);
  const account = await currentAccount(current.token);
  if (account === null) return response({ state: "ANONYMOUS" }, 401);
  if (!account) return failure(503, "Your profile is temporarily unavailable.");
  const result = await backend(`/api/v1/patients/${account.patientId}`, current.token, {
    method: "GET",
  });
  if (!result) return failure(503, "Your profile is temporarily unavailable.");
  const data = profile(await json(result), account);
  if (!result.ok || !data)
    return failure(result.status === 401 ? 401 : 502, "Your profile could not be loaded.");
  return response({ state: "AUTHENTICATED", profile: data });
}

export async function updatePatientProfile(request: NextRequest) {
  const originFailure = validateMutationOrigin(request);
  if (originFailure)
    return response(
      { error: { code: originFailure.code, message: originFailure.message } },
      originFailure.status,
    );
  const current = credentials(request);
  if (!current) return response({ state: "ANONYMOUS" }, 401);
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return failure(400, "Check your profile details and try again.");
  }
  if (!submission(body)) return failure(400, "Check your profile details and try again.");
  const account = await currentAccount(current.token);
  if (account === null) return response({ state: "ANONYMOUS" }, 401);
  if (!account) return failure(503, "Your profile is temporarily unavailable.");
  const result = await backend(`/api/v1/patients/${account.patientId}`, current.token, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      expected_updated_at: body.expectedUpdatedAt,
      preferred_language: body.preferredLanguage,
      demographics: {
        date_of_birth: body.demographics.dateOfBirth,
        age_years: null,
        administrative_sex: body.demographics.administrativeSex,
        gender_identity: body.demographics.genderIdentity,
        pregnancy_status: body.demographics.pregnancyStatus,
        location_context: body.demographics.locationContext,
        height_cm: body.demographics.heightCm,
        weight_kg: body.demographics.weightKg,
      },
    }),
  });
  if (!result) return failure(503, "Your profile is temporarily unavailable.");
  const patientPayload = await json(result);
  const data = profile(patientPayload, account);
  if (!result.ok || !data) {
    const status = result.status === 409 ? 409 : result.status === 401 ? 401 : 502;
    return failure(
      status,
      status === 409
        ? "Your profile changed in another window. Reload it and try again."
        : "Your profile could not be saved.",
    );
  }
  const accountResult = await backend("/api/v1/accounts/me", current.token, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ display_name: body.displayName }),
  });
  const updatedAccountPayload = accountResult ? await json(accountResult) : undefined;
  if (
    !accountResult?.ok ||
    !record(updatedAccountPayload) ||
    updatedAccountPayload.profile_complete !== true ||
    updatedAccountPayload.display_name !== body.displayName
  )
    return failure(502, "Your profile name could not be saved. Please try again.");
  return response({
    state: "AUTHENTICATED",
    profile: { ...data, displayName: body.displayName, profileComplete: true },
  });
}
