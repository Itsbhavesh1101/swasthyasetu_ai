"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import type { GuidanceResult, GuidanceState } from "../lib/guidance/contracts";
import { ErrorState, LoadingState, Panel } from "./ui-primitives";

export function GuidanceForm() {
  const [consent, setConsent] = useState<GuidanceState>();
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<GuidanceResult>();
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    void fetch("/api/guidance/consent", { cache: "no-store" })
      .then(async (response) => {
        if (!response.ok && response.status !== 401) throw new Error();
        setConsent((await response.json()) as GuidanceState);
      })
      .catch(() => setFailed(true));
  }, []);

  async function updateConsent(method: "POST" | "DELETE") {
    if (busy) return;
    setBusy(true);
    try {
      const response = await fetch("/api/guidance/consent", { method });
      if (!response.ok) throw new Error();
      setConsent({
        state: "AUTHENTICATED",
        active: method === "POST",
        noticeVersion: "external-ai-v1",
        scope: ["ayurvedic_guidance"],
      });
      setResult(undefined);
    } catch {
      setFailed(true);
    } finally {
      setBusy(false);
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy || !question.trim()) return;
    setBusy(true);
    setResult(undefined);
    try {
      const response = await fetch("/api/guidance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!response.ok) throw new Error();
      setResult((await response.json()) as GuidanceResult);
    } catch {
      setResult({ outcome: "UNAVAILABLE", citations: [] });
    } finally {
      setBusy(false);
    }
  }

  if (failed) return <ErrorState onRetry={() => window.location.reload()} />;
  if (!consent) return <LoadingState label="Checking your guidance preference." />;
  if (consent.state === "ANONYMOUS")
    return (
      <Panel>
        <h2>Sign in to ask a wellness question</h2>
        <p>This feature is available only inside your private patient account.</p>
        <Link className="action-link action-link--primary" href="/login">
          Sign in <span aria-hidden="true">→</span>
        </Link>
      </Panel>
    );
  if (!consent.active)
    return (
      <Panel>
        <h2>Choose whether to use Google Gemini</h2>
        <p>
          If you continue, the exact question you type will be sent to Google&apos;s Gemini service
          for Google Search grounding. Your name, email, history, and documents are not sent.
        </p>
        <p>You can withdraw this permission at any time without affecting your health record.</p>
        <button
          className="button button--primary"
          disabled={busy}
          onClick={() => void updateConsent("POST")}
          type="button"
        >
          {busy ? "Saving…" : "I agree and continue"}
        </button>
      </Panel>
    );

  return (
    <div className="page-stack">
      <form className="panel guidance-form" onSubmit={submit}>
        <h2>Ask a general wellness question</h2>
        <label>
          Your question
          <textarea
            maxLength={1000}
            onChange={(event) => setQuestion(event.currentTarget.value)}
            required
            rows={5}
            value={question}
          />
        </label>
        {question.trim() ? (
          <div className="question-preview">
            <strong>Text that will be sent</strong>
            <p>{question}</p>
          </div>
        ) : null}
        <button className="button button--primary" disabled={busy} type="submit">
          {busy ? "Searching official sources…" : "Get grounded information"}
        </button>
      </form>

      {result?.outcome === "ANSWERED" ? (
        <section aria-live="polite" className="panel guidance-result">
          <h2>Grounded wellness information</h2>
          <p className="safety-note">Educational information, not a diagnosis or prescription.</p>
          <p>{result.answer}</p>
          <h3>Sources</h3>
          <ul>
            {result.citations.map((citation) => (
              <li key={citation.url}>
                <a href={citation.url} rel="noreferrer" target="_blank">
                  {citation.title}
                </a>
              </li>
            ))}
          </ul>
          <small>Retrieved {new Date(result.retrievedAt!).toLocaleString()}</small>
          <p>
            Herbs and household products can interact with health conditions or medicines. Seek
            qualified care for persistent, worsening, severe, pregnancy-related, paediatric, or
            medication-related concerns.
          </p>
        </section>
      ) : result ? (
        <Panel>
          <h2>Guidance is not available for this question</h2>
          <p>
            No remedy or model text has been displayed. Try a low-risk general wellness question.
          </p>
        </Panel>
      ) : null}

      <Panel>
        <h2>External AI permission</h2>
        <p>Permission is active only for this grounded guidance feature.</p>
        <button
          className="button button--secondary"
          disabled={busy}
          onClick={() => void updateConsent("DELETE")}
          type="button"
        >
          Withdraw permission
        </button>
      </Panel>
    </div>
  );
}
