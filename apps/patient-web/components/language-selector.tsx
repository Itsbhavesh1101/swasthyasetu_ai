"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { onboardingRequest, SessionState } from "../lib/onboarding/client";

type Language = "en" | "hi";

export function LanguageSelector() {
  const router = useRouter();
  const [language, setLanguage] = useState<Language | undefined>();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!language || pending) return;
    setPending(true);
    setError(false);
    const result = await onboardingRequest<SessionState>("/api/onboarding/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ language_preference: language }),
    });
    if (result.ok && result.value?.state === "ACTIVE") {
      router.push("/consent");
      return;
    }
    setPending(false);
    setError(true);
  }

  return (
    <form className="onboarding-form" onSubmit={submit}>
      <fieldset className="choice-group">
        <legend>Preferred language for this private session</legend>
        <p>Broader multilingual content will be added in a later phase.</p>
        <label className="choice-card">
          <input
            checked={language === "en"}
            name="session-language"
            onChange={() => setLanguage("en")}
            type="radio"
            value="en"
          />
          <span>
            <strong>English</strong>
            <small>Use English for this session</small>
          </span>
        </label>
        <label className="choice-card">
          <input
            checked={language === "hi"}
            name="session-language"
            onChange={() => setLanguage("hi")}
            type="radio"
            value="hi"
          />
          <span lang="hi">
            <strong>हिन्दी</strong>
            <small>इस सत्र के लिए हिन्दी चुनें</small>
          </span>
        </label>
      </fieldset>
      {error ? (
        <p className="form-error" role="alert">
          The private-session service is temporarily unavailable. No session was started. Please try
          again.
        </p>
      ) : null}
      <button className="button button--primary" disabled={!language || pending} type="submit">
        {pending ? "Starting private session…" : "Continue to consent"}
      </button>
    </form>
  );
}
