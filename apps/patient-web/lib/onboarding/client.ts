export type SessionState =
  | {
      state: "ACTIVE";
      session_id?: string;
      language_preference?: string | null;
      expires_at?: string;
    }
  | { state: "NO_SESSION" };

export type ConsentState =
  | { state: "GRANTED"; notice_version?: string; granted_at?: string }
  | { state: "NOT_GRANTED" | "REVOKED" | "EXPIRED" | "SESSION_UNAVAILABLE" };

export async function safeJson<T>(response: Response): Promise<T | undefined> {
  try {
    return (await response.json()) as T;
  } catch {
    return undefined;
  }
}

export async function onboardingRequest<T>(
  path: string,
  init?: RequestInit,
): Promise<{ ok: boolean; value?: T }> {
  try {
    const response = await fetch(path, {
      ...init,
      cache: "no-store",
      credentials: "same-origin",
      headers: { Accept: "application/json", ...init?.headers },
    });
    const value = await safeJson<T>(response);
    return value === undefined ? { ok: response.ok } : { ok: response.ok, value };
  } catch {
    return { ok: false };
  }
}
