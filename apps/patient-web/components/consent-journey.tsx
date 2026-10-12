"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ConsentState, onboardingRequest } from "../lib/onboarding/client";
import { LoadingState } from "./ui-primitives";

type ViewState = "LOADING" | "ERROR" | ConsentState["state"];
type ErrorContext = "STATUS" | "GRANT" | "WITHDRAW";

async function resolveConsentState(): Promise<ViewState> {
  const result = await onboardingRequest<ConsentState>("/api/onboarding/consent");
  return result.ok && result.value ? result.value.state : "ERROR";
}

export function ConsentJourney() {
  const router = useRouter();
  const [state, setState] = useState<ViewState>("LOADING");
  const [agreed, setAgreed] = useState(false);
  const [pending, setPending] = useState(false);
  const [errorContext, setErrorContext] = useState<ErrorContext>("STATUS");

  useEffect(() => {
    let active = true;
    void resolveConsentState().then((nextState) => {
      if (active) setState(nextState);
    });
    return () => {
      active = false;
    };
  }, []);

  async function refresh() {
    setErrorContext("STATUS");
    setState(await resolveConsentState());
  }

  async function grant() {
    if (!agreed || pending) return;
    setPending(true);
    const result = await onboardingRequest<ConsentState>("/api/onboarding/consent", {
      method: "POST",
    });
    if (result.ok && result.value?.state === "GRANTED") {
      setState("GRANTED");
      router.push("/encounter");
      return;
    }
    setPending(false);
    setErrorContext("GRANT");
    setState("ERROR");
  }

  async function withdraw() {
    if (pending) return;
    setPending(true);
    const result = await onboardingRequest<ConsentState>("/api/onboarding/consent/revoke", {
      method: "POST",
    });
    setPending(false);
    if (result.ok && result.value?.state === "REVOKED") {
      setState("REVOKED");
    } else {
      setErrorContext("WITHDRAW");
      setState("ERROR");
    }
  }

  if (state === "LOADING") return <LoadingState label="Checking your session consent" />;

  if (state === "SESSION_UNAVAILABLE") {
    return (
      <section className="state-panel" aria-labelledby="consent-session-title">
        <span aria-hidden="true" className="state-symbol">
          i
        </span>
        <div>
          <h2 id="consent-session-title">Start a private session first</h2>
          <p>Your temporary session is not available. Choose a language to begin again.</p>
          <Link className="action-link action-link--primary" href="/language">
            Choose language
          </Link>
        </div>
      </section>
    );
  }

  if (state === "ERROR") {
    return (
      <section className="state-panel" aria-labelledby="consent-error-title" role="alert">
        <span aria-hidden="true" className="state-symbol">
          !
        </span>
        <div>
          <h2 id="consent-error-title">Consent status is temporarily unavailable</h2>
          <p>
            {errorContext === "WITHDRAW"
              ? "We could not confirm that all active grants were withdrawn. Some consent records may have changed. Please check again."
              : "We could not confirm the requested consent state. Please try again."}
          </p>
          <button
            className="button button--primary"
            onClick={() => {
              setState("LOADING");
              void refresh();
            }}
            type="button"
          >
            Try again
          </button>
        </div>
      </section>
    );
  }

  if (state === "GRANTED") {
    return (
      <section className="state-panel" aria-labelledby="consent-active-title">
        <span aria-hidden="true" className="state-symbol">
          ✓
        </span>
        <div>
          <h2 id="consent-active-title">Consent is active for this session</h2>
          <p>You may continue. Clinical intake is not available in this phase.</p>
          <div className="inline-actions">
            <Link className="action-link action-link--primary" href="/encounter">
              Continue
            </Link>
            <button
              className="button button--secondary"
              disabled={pending}
              onClick={() => void withdraw()}
              type="button"
            >
              {pending ? "Withdrawing…" : "Withdraw this consent"}
            </button>
          </div>
        </div>
      </section>
    );
  }

  if (state === "REVOKED" || state === "EXPIRED") {
    return (
      <section className="state-panel" aria-labelledby="consent-inactive-title">
        <span aria-hidden="true" className="state-symbol">
          i
        </span>
        <div>
          <h2 id="consent-inactive-title">
            {state === "REVOKED" ? "Consent has been withdrawn" : "Consent is no longer active"}
          </h2>
          <p>You can review the notice and choose again for this session.</p>
          <button
            className="button button--secondary"
            onClick={() => setState("NOT_GRANTED")}
            type="button"
          >
            Review consent
          </button>
        </div>
      </section>
    );
  }

  return (
    <div className="consent-stack">
      <section aria-labelledby="consent-notice-title" className="panel notice-panel">
        <p className="card-kicker">Project notice · privacy-v1</p>
        <h2 id="consent-notice-title">Use of this temporary session</h2>
        <p>
          This temporary pseudonymous session requests consent for general product use and future
          clinical-intake processing. No name is required.
        </p>
        <p>
          <strong>SwasthyaSetu is not an emergency service.</strong>
        </p>
        <p>
          This consent does not include referral sharing, research use, ABDM exchange, caregiver
          access, or separate external-AI processing.
        </p>
        <p className="governance-note">
          A final jurisdiction-specific privacy notice remains subject to governance approval.
        </p>
      </section>
      <label className="agreement-control">
        <input
          checked={agreed}
          onChange={(event) => setAgreed(event.target.checked)}
          type="checkbox"
        />
        <span>I understand and agree to this use for this session.</span>
      </label>
      <button
        className="button button--primary"
        disabled={!agreed || pending}
        onClick={() => void grant()}
        type="button"
      >
        {pending ? "Recording consent…" : "Agree and continue"}
      </button>
    </div>
  );
}
