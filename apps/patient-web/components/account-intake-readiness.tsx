"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import type { AccountState } from "../lib/account/contracts";
import { intakeRequest } from "../lib/intake/client";
import { ConsentState, onboardingRequest } from "../lib/onboarding/client";
import { LoadingState, Panel } from "./ui-primitives";

type State = "LOADING" | "ANONYMOUS" | "CONSENT_REQUIRED" | "READY" | "UNAVAILABLE";

async function resolveState(): Promise<State> {
  try {
    const accountResponse = await fetch("/api/account/me", { cache: "no-store" });
    const account = (await accountResponse.json()) as AccountState;
    if (account.state !== "AUTHENTICATED") return "ANONYMOUS";
    const consent = await onboardingRequest<ConsentState>("/api/onboarding/consent");
    if (!consent.ok || !consent.value) return "UNAVAILABLE";
    return consent.value.state === "GRANTED" ? "READY" : "CONSENT_REQUIRED";
  } catch {
    return "UNAVAILABLE";
  }
}

export function AccountIntakeReadiness() {
  const router = useRouter();
  const [state, setState] = useState<State>("LOADING");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    void resolveState().then((next) => {
      if (active) setState(next);
    });
    return () => {
      active = false;
    };
  }, []);

  if (state === "LOADING") return <LoadingState label="Checking your intake readiness." />;
  if (state === "ANONYMOUS")
    return (
      <Panel>
        <h2>Sign in to start your health journey</h2>
        <Link className="action-link action-link--primary" href="/login">
          Sign in <span aria-hidden="true">→</span>
        </Link>
      </Panel>
    );
  if (state === "CONSENT_REQUIRED")
    return (
      <Panel>
        <h2>Review intake permission</h2>
        <p>
          Allow this private account session to save the answers you choose to provide as a
          structured intake draft. This does not confirm a diagnosis.
        </p>
        <button
          className="button button--primary"
          disabled={busy}
          onClick={async () => {
            setBusy(true);
            const response = await onboardingRequest<ConsentState>("/api/onboarding/consent", {
              method: "POST",
            });
            setBusy(false);
            setState(response.ok && response.value?.state === "GRANTED" ? "READY" : "UNAVAILABLE");
          }}
          type="button"
        >
          {busy ? "Saving…" : "Allow structured intake"}
        </button>
      </Panel>
    );
  if (state === "UNAVAILABLE")
    return (
      <Panel>
        <h2>Intake is temporarily unavailable</h2>
        <button
          className="button button--primary"
          onClick={() => void resolveState().then(setState)}
          type="button"
        >
          Try again
        </button>
      </Panel>
    );
  return (
    <Panel>
      <h2>Your account is ready</h2>
      <p>Start or resume your structured, patient-provided intake draft.</p>
      <button
        className="button button--primary"
        disabled={busy}
        onClick={async () => {
          setBusy(true);
          const result = await intakeRequest("/api/intake/start", { method: "POST" });
          if (result.ok) return router.push(`/intake/${result.value.intake_id}`);
          setBusy(false);
          if (
            ["AUTHENTICATION_REQUIRED", "SESSION_EXPIRED", "SESSION_UNAVAILABLE"].includes(
              result.error.code,
            )
          )
            return router.push("/login");
          setState("UNAVAILABLE");
        }}
        type="button"
      >
        {busy ? "Starting intake…" : "Start or resume intake"}
      </button>
    </Panel>
  );
}
