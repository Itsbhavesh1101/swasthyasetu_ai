"use client";

import { useEffect, useState } from "react";

import type { AccountState } from "../lib/account/contracts";
import { ActionLink, LoadingState, Panel } from "./ui-primitives";

export function DashboardOverview() {
  const [account, setAccount] = useState<AccountState | undefined>();

  useEffect(() => {
    void fetch("/api/account/me", { cache: "no-store" })
      .then(async (result) => setAccount((await result.json()) as AccountState))
      .catch(() => setAccount({ state: "ANONYMOUS" }));
  }, []);

  if (!account) return <LoadingState label="Opening your private health record." />;
  if (account.state !== "AUTHENTICATED")
    return (
      <Panel>
        <h2>Sign in to view your private record</h2>
        <p>Your health information is available only after you sign in.</p>
        <ActionLink href="/login">Sign in</ActionLink>
      </Panel>
    );

  return (
    <section aria-label="Your health record" className="page-stack">
      <p className="welcome-line">Welcome back, {account.displayName ?? "patient"}.</p>
      <div className="feature-grid">
        <Panel>
          <p className="card-kicker">Your details</p>
          <h2>Personal profile</h2>
          <p>Keep your language, date of birth, and other personal details current.</p>
          <ActionLink href="/profile">Open profile</ActionLink>
        </Panel>
        <Panel>
          <p className="card-kicker">Your record</p>
          <h2>Medical history</h2>
          <p>Record conditions, medicines, allergies, procedures, and observations.</p>
          <ActionLink href="/history">Open history</ActionLink>
        </Panel>
        <Panel>
          <p className="card-kicker">Private vault</p>
          <h2>Documents</h2>
          <p>Keep reports and prescriptions with the rest of your health record.</p>
          <ActionLink href="/documents">Open documents</ActionLink>
        </Panel>
        <Panel>
          <p className="card-kicker">Grounded education</p>
          <h2>Ayurvedic home-care guidance</h2>
          <p>Ask a general wellness question and review source-backed educational information.</p>
          <ActionLink href="/guidance">Open guidance</ActionLink>
        </Panel>
      </div>
    </section>
  );
}
