"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import type { AccountState } from "../lib/account/contracts";

export function AccountMenu() {
  const router = useRouter();
  const [account, setAccount] = useState<AccountState>({ state: "ANONYMOUS" });
  useEffect(() => {
    void fetch("/api/account/me", { cache: "no-store" })
      .then(async (r) => setAccount((await r.json()) as AccountState))
      .catch(() => undefined);
  }, []);
  if (account.state !== "AUTHENTICATED") return null;
  return (
    <button
      className="button button--account"
      onClick={async () => {
        const response = await fetch("/api/account/logout", { method: "POST" });
        if (response.ok) router.push("/login");
      }}
      type="button"
    >
      Sign out{account.displayName ? `, ${account.displayName}` : ""}
    </button>
  );
}
