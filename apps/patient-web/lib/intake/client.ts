import type { IntakeError, IntakeView } from "./contracts";

export async function intakeRequest(
  path: string,
  init?: { method?: "GET" | "POST"; body?: unknown },
): Promise<{ ok: true; value: IntakeView } | { ok: false; error: IntakeError["error"] }> {
  try {
    const requestInit: RequestInit = {
      method: init?.method ?? "GET",
      credentials: "same-origin",
      cache: "no-store",
    };
    if (init?.body !== undefined) {
      requestInit.headers = { "Content-Type": "application/json" };
      requestInit.body = JSON.stringify(init.body);
    }
    const response = await fetch(path, requestInit);
    const value: unknown = await response.json();
    if (response.ok) return { ok: true, value: value as IntakeView };
    if (
      typeof value === "object" &&
      value !== null &&
      "error" in value &&
      typeof value.error === "object" &&
      value.error !== null &&
      "code" in value.error &&
      "message" in value.error &&
      typeof value.error.code === "string" &&
      typeof value.error.message === "string"
    )
      return { ok: false, error: { code: value.error.code, message: value.error.message } };
  } catch {
    // A mutation is never replayed here after an ambiguous network failure.
  }
  return {
    ok: false,
    error: {
      code: "REQUEST_FAILED",
      message: "The request could not be confirmed. Refresh before trying again.",
    },
  };
}
