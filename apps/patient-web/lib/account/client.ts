import type { AccountState, AccountSubmission } from "./contracts";

export type AccountResponse = AccountState & {
  errorMessage?: string;
};

export async function submitAccount(
  mode: "login" | "register",
  submission: AccountSubmission,
): Promise<AccountResponse | undefined> {
  try {
    const response = await fetch(`/api/account/${mode}`, {
      method: "POST",
      credentials: "same-origin",
      cache: "no-store",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(submission),
    });
    if (!response.ok) {
      try {
        const errorData = await response.json();
        const message = errorData?.error?.message;
        if (typeof message === "string") {
          return { state: "ANONYMOUS", errorMessage: message };
        }
      } catch {
        // Fall back to undefined if error response body cannot be parsed
      }
      return undefined;
    }
    return (await response.json()) as AccountResponse;
  } catch {
    return undefined;
  }
}
