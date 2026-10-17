"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ConsentState, onboardingRequest, SessionState } from "../lib/onboarding/client";
import { intakeRequest } from "../lib/intake/client";
import { LoadingState } from "./ui-primitives";

type Readiness = "LOADING" | "NO_SESSION" | "NO_CONSENT" | "READY" | "UNAVAILABLE";

async function resolveReadiness(): Promise<Readiness> {
  const session = await onboardingRequest<SessionState>("/api/onboarding/session");
  if (!session.ok || !session.value) return "UNAVAILABLE";
  if (session.value.state !== "ACTIVE") return "NO_SESSION";
  const consent = await onboardingRequest<ConsentState>("/api/onboarding/consent");
  if (!consent.ok || !consent.value) return "UNAVAILABLE";
  return consent.value.state === "GRANTED" ? "READY" : "NO_CONSENT";
}

export function OnboardingReadiness() {
  const router = useRouter();
  const [state, setState] = useState<Readiness>("LOADING");
  const [closing, setClosing] = useState(false);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    let active = true;
    void resolveReadiness().then((nextState) => {
      if (active) setState(nextState);
    });
    return () => {
      active = false;
    };
  }, []);

  async function load() {
    setState(await resolveReadiness());
  }

  async function close() {
    if (closing) return;
    setClosing(true);
    const result = await onboardingRequest<{ state: string }>("/api/onboarding/session/close", {
      method: "POST",
    });
    if (result.ok && (result.value?.state === "CLOSED" || result.value?.state === "NO_SESSION")) {
      router.push("/language");
      return;
    }
    setClosing(false);
    setState("UNAVAILABLE");
  }

  async function startIntake() {
    if (starting) return;
    setStarting(true);
    const result = await intakeRequest("/api/intake/start", { method: "POST" });
    if (result.ok) {
      router.push(`/intake/${result.value.intake_id}`);
      return;
    }
    setStarting(false);
    setState("UNAVAILABLE");
  }

  if (state === "LOADING") return <LoadingState label="Checking onboarding readiness" />;

  const content = {
    NO_SESSION: {
      title: "Start a private session",
      body: "No active private session is available. Clinical intake is not available in this phase.",
      href: "/language",
    },
    NO_CONSENT: {
      title: "Consent is still needed",
      body: "Review the project notice before continuing. Clinical intake is not available in this phase.",
      href: "/consent",
    },
    UNAVAILABLE: {
      title: "Onboarding status is temporarily unavailable",
      body: "We cannot confirm your session or consent right now. Clinical intake is not available.",
      href: null,
    },
  } as const;

  if (state !== "READY") {
    const current = content[state];
    return (
      <section
        className="state-panel"
        aria-labelledby="readiness-title"
        role={state === "UNAVAILABLE" ? "alert" : undefined}
      >
        <span aria-hidden="true" className="state-symbol">
          i
        </span>
        <div>
          <h2 id="readiness-title">{current.title}</h2>
          <p>{current.body}</p>
          {current.href ? (
            <div className="inline-actions">
              <Link className="action-link action-link--primary" href={current.href}>
                Continue
              </Link>
              {state === "NO_CONSENT" ? (
                <button
                  className="button button--secondary"
                  disabled={closing}
                  onClick={() => void close()}
                  type="button"
                >
                  {closing ? "Ending private session…" : "End private session"}
                </button>
              ) : null}
            </div>
          ) : (
            <button
              className="button button--primary"
              onClick={() => {
                setState("LOADING");
                void load();
              }}
              type="button"
            >
              Try again
            </button>
          )}
        </div>
      </section>
    );
  }

  return (
    <section className="state-panel" aria-labelledby="readiness-title">
      <span aria-hidden="true" className="state-symbol">
        ✓
      </span>
      <div>
        <h2 id="readiness-title">Your private session and consent are ready.</h2>
        <p>You can now start a structured, patient-provided intake draft.</p>
        <div className="inline-actions">
          <button
            className="button button--primary"
            disabled={starting || closing}
            onClick={() => void startIntake()}
            type="button"
          >
            {starting ? "Starting intake…" : "Start intake"}
          </button>
          <button
            className="button button--secondary"
            disabled={closing || starting}
            onClick={() => void close()}
            type="button"
          >
            {closing ? "Ending private session…" : "End private session"}
          </button>
        </div>
      </div>
    </section>
  );
}
