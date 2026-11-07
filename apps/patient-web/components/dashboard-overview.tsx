"use client";

import { useEffect, useState } from "react";

import type { AccountState } from "../lib/account/contracts";
import { ActionLink, LoadingState, Panel } from "./ui-primitives";

const setupActions = [
  ["Review personal details", "/profile"],
  ["Add conditions", "/history"],
  ["Add medicines", "/history"],
  ["Add allergies", "/history"],
  ["Add procedures", "/history"],
  ["Add documents", "/documents"],
  ["Start guided intake", "/encounter"],
] as const;

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
  if (!account.profileComplete)
    return (
      <Panel>
        <p className="card-kicker">One step left</p>
        <h2>Create your base profile</h2>
        <p>Add your name and basic health details before opening your dashboard.</p>
        <ActionLink href="/profile?setup=1">Continue profile setup</ActionLink>
      </Panel>
    );

  return (
    <section aria-label="Your health record" className="page-stack">
      <p className="welcome-line">Welcome back, {account.displayName ?? "patient"}.</p>
      <section aria-labelledby="health-record-setup-heading" className="setup-checklist panel">
        <header>
          <p className="card-kicker">Optional next steps</p>
          <h2 id="health-record-setup-heading">Complete your health record</h2>
          <p>Add only the information you want to keep in your private patient record.</p>
        </header>
        <ul className="setup-action-list">
          {setupActions.map(([label, href]) => (
            <li key={label}>
              <ActionLink href={href}>{label}</ActionLink>
            </li>
          ))}
        </ul>
        <p className="setup-checklist-note">
          These are optional actions, not a medical assessment or measure of care quality.
        </p>
      </section>
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
          <p className="card-kicker">Over time</p>
          <h2>Medical timeline</h2>
          <p>See history entries and health journeys together in chronological order.</p>
          <ActionLink href="/timeline">Open timeline</ActionLink>
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
        <Panel>
          <p className="card-kicker">Structured intake</p>
          <h2>Health journey</h2>
          <p>Start or resume a guided intake draft linked to your private patient record.</p>
          <ActionLink href="/encounter">Open health journey</ActionLink>
        </Panel>
      </div>
    </section>
  );
}
