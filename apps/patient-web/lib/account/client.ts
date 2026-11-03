import type { AccountState, AccountSubmission } from "./contracts";

export async function submitAccount(
  mode: "login" | "register",
  submission: AccountSubmission,
): Promise<AccountState | undefined> {
  try {
    const response = await fetch(`/api/account/${mode}`, {
      method: "POST",
      credentials: "same-origin",
      cache: "no-store",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(submission),
    });
    if (!response.ok) return undefined;
    return (await response.json()) as AccountState;
  } catch {
    return undefined;
  }
}
