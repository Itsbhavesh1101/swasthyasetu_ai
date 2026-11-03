import { NextRequest, NextResponse } from "next/server";

import { SESSION_ID_COOKIE, SESSION_TOKEN_COOKIE } from "../onboarding/server";
import { validateMutationOrigin } from "../security/request-origin";
import type { DocumentItem } from "./contracts";

const TIMEOUT_MS = 10_000;
const MAX_BYTES = 10 * 1024 * 1024;
const MAX_MULTIPART_OVERHEAD = 64 * 1024;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
type RecordValue = Record<string, unknown>;

const record = (value: unknown): value is RecordValue =>
  typeof value === "object" && value !== null && !Array.isArray(value);

function json(body: unknown, status = 200) {
  const result = NextResponse.json(body, { status });
  result.headers.set("Cache-Control", "no-store");
  return result;
}

const failure = (status: number, message: string) =>
  json({ error: { code: "PATIENT_DOCUMENT_FAILED", message } }, status);

function origin() {
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

function token(request: NextRequest) {
  const session = request.cookies.get(SESSION_ID_COOKIE)?.value;
  const bearer = request.cookies.get(SESSION_TOKEN_COOKIE)?.value;
  return session && UUID.test(session) && bearer ? bearer : undefined;
}

async function backend(path: string, bearer: string, init: RequestInit) {
  const base = origin();
  if (!base) return undefined;
  try {
    return await fetch(`${base}${path}`, {
      ...init,
      cache: "no-store",
      headers: { Authorization: `Bearer ${bearer}`, ...init.headers },
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch {
    return undefined;
  }
}

async function value(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

class UploadTooLarge extends Error {}

async function boundedFormData(request: NextRequest) {
  const declared = Number(request.headers.get("content-length"));
  const limit = MAX_BYTES + MAX_MULTIPART_OVERHEAD;
  if (Number.isFinite(declared) && declared > limit) throw new UploadTooLarge();
  if (!request.body) throw new TypeError("missing upload body");
  const reader = request.body.getReader();
  const chunks: ArrayBuffer[] = [];
  let received = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      received += value.byteLength;
      if (received > limit) {
        await reader.cancel();
        throw new UploadTooLarge();
      }
      const copy = new Uint8Array(value.byteLength);
      copy.set(value);
      chunks.push(copy.buffer);
    }
  } finally {
    reader.releaseLock();
  }
  return new Response(new Blob(chunks), {
    headers: { "Content-Type": request.headers.get("content-type") ?? "" },
  }).formData();
}

async function context(request: NextRequest) {
  const bearer = token(request);
  if (!bearer) return undefined;
  const response = await backend("/api/v1/accounts/me", bearer, { method: "GET" });
  if (!response) return false;
  const body = await value(response);
  if (response.status === 401) return undefined;
  return response.ok &&
    record(body) &&
    typeof body.patient_id === "string" &&
    UUID.test(body.patient_id)
    ? { bearer, patientId: body.patient_id }
    : false;
}

function item(value: unknown): DocumentItem | undefined {
  if (
    !record(value) ||
    typeof value.document_id !== "string" ||
    !UUID.test(value.document_id) ||
    typeof value.display_name !== "string" ||
    !value.display_name ||
    value.display_name.length > 255 ||
    !["application/pdf", "image/jpeg", "image/png"].includes(String(value.mime_type)) ||
    typeof value.byte_size !== "number" ||
    value.byte_size <= 0 ||
    value.byte_size > MAX_BYTES ||
    typeof value.created_at !== "string" ||
    Number.isNaN(Date.parse(value.created_at))
  )
    return undefined;
  return {
    documentId: value.document_id,
    displayName: value.display_name,
    mimeType: String(value.mime_type),
    byteSize: value.byte_size,
    createdAt: value.created_at,
  };
}

export async function listDocuments(request: NextRequest) {
  const current = await context(request);
  if (current === undefined) return json({ state: "ANONYMOUS" }, 401);
  if (!current) return failure(503, "Your documents are unavailable.");
  const response = await backend(
    `/api/v1/patients/${current.patientId}/documents`,
    current.bearer,
    { method: "GET" },
  );
  if (!response) return failure(503, "Your documents are unavailable.");
  const body = await value(response);
  if (!response.ok || !record(body) || !Array.isArray(body.items))
    return failure(response.status === 401 ? 401 : 502, "Your documents could not be loaded.");
  const items = body.items.map(item);
  return items.some((entry) => entry === undefined)
    ? failure(502, "Your documents could not be loaded.")
    : json({ state: "AUTHENTICATED", items });
}

export async function uploadDocument(request: NextRequest) {
  const originFailure = validateMutationOrigin(request);
  if (originFailure)
    return json(
      { error: { code: originFailure.code, message: originFailure.message } },
      originFailure.status,
    );
  const current = await context(request);
  if (current === undefined) return json({ state: "ANONYMOUS" }, 401);
  if (!current) return failure(503, "Your documents are unavailable.");
  try {
    const form = await boundedFormData(request);
    const file = form.get("file");
    if (!(file instanceof File) || file.size <= 0 || file.size > MAX_BYTES)
      return failure(
        file instanceof File && file.size > MAX_BYTES ? 413 : 400,
        "Choose a valid PDF, JPEG, or PNG file.",
      );
    const forward = new FormData();
    forward.set("file", file, file.name);
    const response = await backend(
      `/api/v1/patients/${current.patientId}/documents`,
      current.bearer,
      { method: "POST", body: forward },
    );
    if (!response) return failure(503, "Your document could not be uploaded.");
    const document = item(await value(response));
    return response.ok && document
      ? json({ state: "AUTHENTICATED", item: document }, 201)
      : failure(
          response.status === 413 || response.status === 415 ? response.status : 502,
          "Your document could not be uploaded.",
        );
  } catch (error) {
    if (error instanceof UploadTooLarge) return failure(413, "That file is larger than 10 MB.");
    return failure(400, "Choose a valid PDF, JPEG, or PNG file.");
  }
}

export async function downloadDocument(request: NextRequest, documentId: string) {
  if (!UUID.test(documentId)) return failure(400, "The document is invalid.");
  const current = await context(request);
  if (current === undefined) return json({ state: "ANONYMOUS" }, 401);
  if (!current) return failure(503, "Your document is unavailable.");
  const response = await backend(
    `/api/v1/patients/${current.patientId}/documents/${documentId}/content`,
    current.bearer,
    { method: "GET" },
  );
  if (!response?.ok)
    return failure(response?.status === 404 ? 404 : 502, "Your document could not be downloaded.");
  const content = await response.arrayBuffer();
  if (content.byteLength > MAX_BYTES) return failure(502, "Your document could not be downloaded.");
  const result = new NextResponse(content, { status: 200 });
  result.headers.set("Cache-Control", "no-store");
  result.headers.set(
    "Content-Type",
    response.headers.get("content-type") ?? "application/octet-stream",
  );
  result.headers.set(
    "Content-Disposition",
    response.headers.get("content-disposition") ?? 'attachment; filename="document"',
  );
  result.headers.set("X-Content-Type-Options", "nosniff");
  return result;
}

export async function deleteDocument(request: NextRequest, documentId: string) {
  const originFailure = validateMutationOrigin(request);
  if (originFailure)
    return json(
      { error: { code: originFailure.code, message: originFailure.message } },
      originFailure.status,
    );
  if (!UUID.test(documentId)) return failure(400, "The document is invalid.");
  const current = await context(request);
  if (current === undefined) return json({ state: "ANONYMOUS" }, 401);
  if (!current) return failure(503, "Your document is unavailable.");
  const response = await backend(
    `/api/v1/patients/${current.patientId}/documents/${documentId}`,
    current.bearer,
    { method: "DELETE" },
  );
  return response?.ok
    ? new NextResponse(null, { status: 204, headers: { "Cache-Control": "no-store" } })
    : failure(response?.status === 404 ? 404 : 502, "Your document could not be deleted.");
}
