"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useCallback, useEffect, useRef, useState } from "react";

import { intakeRequest } from "../../lib/intake/client";
import type { IntakeQuestion, IntakeView } from "../../lib/intake/contracts";
import { onboardingRequest } from "../../lib/onboarding/client";
import { LoadingState } from "../ui-primitives";
import { UrgentHelpLink } from "../urgent-help-link";
import { AnswerControl } from "./answer-control";

function answerBody(question: IntakeQuestion, form: FormData, version: number) {
  const selected = form.getAll("selected_option_ids").map(String);
  const raw = form.get("value");
  let value: string | boolean | number | null = raw === null ? null : String(raw);
  if (question.answer_type === "BOOLEAN") value = raw === "true";
  if (["NUMBER", "DURATION", "SEVERITY_SCALE"].includes(question.answer_type))
    value = raw === null ? null : Number(raw);
  return {
    question_id: question.question_id,
    question_version: question.question_version,
    answer: {
      schema_version: "intake-answer.v1",
      answer_type: question.answer_type,
      value: ["SINGLE_CHOICE", "MULTI_CHOICE"].includes(question.answer_type) ? null : value,
      selected_option_ids: selected.length ? selected : null,
      unit: form.get("unit") ? String(form.get("unit")) : null,
      response_disposition: "ANSWERED",
      language_code: "en",
      original_text: question.answer_type === "TEXT" ? String(raw ?? "") : null,
    },
    source_type: question.answer_type === "TEXT" ? "PATIENT_TEXT" : "PATIENT_TOUCH",
    expected_version: version,
  };
}

export function IntakeJourney({
  intakeId,
  review = false,
}: {
  intakeId: string;
  review?: boolean;
}) {
  const router = useRouter();
  const heading = useRef<HTMLHeadingElement>(null);
  const [intake, setIntake] = useState<IntakeView | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    const result = await intakeRequest(`/api/intake/${encodeURIComponent(intakeId)}`);
    if (result.ok) {
      setIntake(result.value);
      setError(null);
    } else {
      setError(result.error.message);
    }
  }, [intakeId]);

  useEffect(() => {
    let active = true;
    void intakeRequest(`/api/intake/${encodeURIComponent(intakeId)}`).then((result) => {
      if (!active) return;
      if (result.ok) {
        setIntake(result.value);
        setError(null);
      } else {
        setError(result.error.message);
      }
    });
    return () => {
      active = false;
    };
  }, [intakeId]);

  useEffect(() => {
    if (intake || error) heading.current?.focus();
  }, [intake, error]);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!intake?.current_question || busy) return;
    setBusy(true);
    const result = await intakeRequest(`/api/intake/${encodeURIComponent(intakeId)}/answers`, {
      method: "POST",
      body: answerBody(intake.current_question, new FormData(event.currentTarget), intake.version),
    });
    setBusy(false);
    if (!result.ok) {
      setError(result.error.message);
      await load();
      return;
    }
    setIntake(result.value);
    setError(null);
    if (result.value.completion_ready) router.push(`/intake/${intakeId}/review`);
  }

  async function complete() {
    if (!intake || busy) return;
    setBusy(true);
    const result = await intakeRequest(`/api/intake/${encodeURIComponent(intakeId)}/complete`, {
      method: "POST",
      body: { expected_version: intake.version },
    });
    setBusy(false);
    if (result.ok) {
      setIntake(result.value);
      setError(null);
    } else {
      setError(result.error.message);
      await load();
    }
  }

  async function closeSession() {
    if (busy) return;
    setBusy(true);
    const result = await onboardingRequest<{ state: string }>("/api/onboarding/session/close", {
      method: "POST",
    });
    if (result.ok) router.push("/language");
    else {
      setBusy(false);
      setError("The private session could not be ended. Please try again.");
    }
  }

  if (!intake && !error) return <LoadingState label="Loading your saved intake draft" />;
  if (!intake)
    return (
      <section className="state-panel" role="alert">
        <div>
          <h1 ref={heading} tabIndex={-1}>
            Intake unavailable
          </h1>
          <p>{error}</p>
          <div className="inline-actions">
            <button className="button button--primary" onClick={() => void load()} type="button">
              Try again
            </button>
            <UrgentHelpLink />
          </div>
        </div>
      </section>
    );

  if (review || intake.status === "COMPLETED") {
    return (
      <div className="page-stack page-stack--narrow">
        <header className="page-header">
          <p className="eyebrow">Structured intake</p>
          <h1 ref={heading} tabIndex={-1}>
            {intake.status === "COMPLETED"
              ? "Your intake draft has been saved"
              : "Review your intake draft"}
          </h1>
          <p>
            This is a patient-provided draft. It is not a diagnosis, treatment plan, urgency
            assessment, or clinician confirmation.
          </p>
        </header>
        {error ? (
          <p className="form-error" role="alert">
            {error}
          </p>
        ) : null}
        <section className="content-card" aria-labelledby="patient-information">
          <h2 id="patient-information">Patient-provided information</h2>
          {intake.answers.length ? (
            <dl className="review-list">
              {intake.answers.map((answer) => (
                <div key={answer.question_id}>
                  <dt>{answer.question_id.replaceAll(".", " ")}</dt>
                  <dd>
                    {answer.selected_option_ids?.join(", ") ??
                      String(answer.value ?? answer.response_disposition)}{" "}
                    <span>— {answer.source_label}</span>
                  </dd>
                </div>
              ))}
            </dl>
          ) : (
            <p>No answers have been saved.</p>
          )}
        </section>
        <div className="inline-actions">
          {intake.status === "IN_PROGRESS" ? (
            <>
              <Link className="action-link action-link--secondary" href={`/intake/${intakeId}`}>
                Review or change
              </Link>
              <button
                className="button button--primary"
                disabled={!intake.completion_ready || busy}
                onClick={() => void complete()}
                type="button"
              >
                {busy ? "Saving draft…" : "Complete draft"}
              </button>
            </>
          ) : null}
          <button
            className="button button--secondary"
            disabled={busy}
            onClick={() => void closeSession()}
            type="button"
          >
            End private session
          </button>
          <UrgentHelpLink />
        </div>
      </div>
    );
  }

  const question = intake.current_question;
  return (
    <div className="page-stack page-stack--narrow">
      <header className="page-header">
        <p className="eyebrow">
          Structured intake · {question?.section.replaceAll("_", " ").toLowerCase()}
        </p>
        <h1 ref={heading} tabIndex={-1}>
          {question?.prompt ?? "More information is needed"}
        </h1>
        <p>
          Questions are selected by the saved questionnaire. No percentage or medical conclusion is
          calculated.
        </p>
      </header>
      {error ? (
        <p className="form-error" id="answer-error" role="alert">
          {error}
        </p>
      ) : null}
      {question ? (
        <form className="content-card intake-form" onSubmit={(event) => void submit(event)}>
          {question.help_text ? <p id="question-help">{question.help_text}</p> : null}
          <label className="visually-hidden" htmlFor="answer-value">
            {question.prompt}
          </label>
          <AnswerControl disabled={busy} question={question} />
          <div className="inline-actions">
            <button className="button button--primary" disabled={busy} type="submit">
              {busy ? "Saving…" : "Save and continue"}
            </button>
            <Link
              className="action-link action-link--secondary"
              href={`/intake/${intakeId}/review`}
            >
              Review draft
            </Link>
          </div>
        </form>
      ) : (
        <section className="state-panel">
          <div>
            <h2>Review is needed</h2>
            <p>The server has not selected another question.</p>
            <Link className="action-link action-link--primary" href={`/intake/${intakeId}/review`}>
              Review draft
            </Link>
          </div>
        </section>
      )}
      <div className="inline-actions">
        <button
          className="button button--secondary"
          disabled={busy}
          onClick={() => void closeSession()}
          type="button"
        >
          End private session
        </button>
        <UrgentHelpLink />
      </div>
    </div>
  );
}
