"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import type { PatientProfile, PatientProfileState } from "../lib/patient/contracts";
import {
  bloodGroupOptions,
  calculatedAge,
  calculatedBmi,
  formatProfileDate,
  maskedAadhaar,
  profileDraft,
  profileSubmission,
  type ProfileDraft,
} from "./profile-fields";

export type WizardStepKey =
  | "name"
  | "language"
  | "dob"
  | "sex"
  | "height"
  | "weight"
  | "mobile"
  | "bloodGroup"
  | "aadhaar"
  | "pregnancy"
  | "review";

const supportedSexValues = new Set(["female", "male", "intersex", "other"]);

function getWizardSteps(administrativeSex: string): WizardStepKey[] {
  const steps: WizardStepKey[] = [
    "name",
    "language",
    "dob",
    "sex",
    "height",
    "weight",
    "mobile",
    "bloodGroup",
    "aadhaar",
  ];
  if (administrativeSex === "female") {
    steps.push("pregnancy");
  }
  steps.push("review");
  return steps;
}

const stepTitles: Record<WizardStepKey, string> = {
  name: "What should we call you?",
  language: "Which language do you prefer?",
  dob: "When were you born?",
  sex: "What sex is recorded for healthcare?",
  height: "What is your height?",
  weight: "What is your weight?",
  mobile: "What is your mobile number?",
  bloodGroup: "What is your blood group?",
  aadhaar: "What is your Aadhaar number?",
  pregnancy: "Would you like to add pregnancy status?",
  review: "Review your details",
};

function validationMessage(stepKey: WizardStepKey, draft: ProfileDraft): string {
  if (stepKey === "name" && (!draft.displayName.trim() || draft.displayName.trim().length > 120))
    return "Enter your full name.";
  if (stepKey === "language" && !["en", "hi"].includes(draft.preferredLanguage))
    return "Choose your preferred language.";
  if (
    stepKey === "dob" &&
    (!/^\d{4}-\d{2}-\d{2}$/.test(draft.dateOfBirth) || calculatedAge(draft.dateOfBirth) === null)
  )
    return "Enter a valid date of birth.";
  if (stepKey === "sex" && !supportedSexValues.has(draft.administrativeSex))
    return "Choose the sex recorded for healthcare.";
  if (stepKey === "height" && !(Number(draft.heightCm) >= 30 && Number(draft.heightCm) <= 275))
    return "Enter a height between 30 and 275 cm.";
  if (stepKey === "weight" && !(Number(draft.weightKg) >= 1 && Number(draft.weightKg) <= 700))
    return "Enter a weight between 1 and 700 kg.";
  if (stepKey === "mobile" && !/^\+[1-9][0-9]{6,14}$/.test(draft.mobileNumber))
    return "Enter a mobile number in international format, such as +919876543210.";
  if (stepKey === "bloodGroup" && !bloodGroupOptions.some(({ value }) => value === draft.bloodGroup))
    return "Choose your blood group or Unknown.";
  if (stepKey === "aadhaar" && !/^[0-9]{12}$/.test(draft.aadhaarNumber))
    return "Enter a 12-digit Aadhaar number.";
  if (stepKey === "pregnancy" && draft.pregnancyStatus.trim().length > 256)
    return "Pregnancy status must be 256 characters or fewer.";
  return "";
}

function summaryValue(value: string, fallback = "Not provided") {
  return value.trim() || fallback;
}

export function ProfileSetupWizard({ profile }: Readonly<{ profile: PatientProfile }>) {
  const router = useRouter();
  const [draft, setDraft] = useState(() => profileDraft(profile));
  const [step, setStep] = useState(0);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const heading = useRef<HTMLHeadingElement>(null);
  const age = calculatedAge(draft.dateOfBirth);
  const bmi = calculatedBmi(draft.heightCm, draft.weightKg);

  const steps = getWizardSteps(draft.administrativeSex);
  const totalSteps = steps.length;
  const currentStepKey = steps[Math.min(step, totalSteps - 1)] ?? "name";

  useEffect(() => {
    document.body.classList.add("profile-setup-active");
    return () => document.body.classList.remove("profile-setup-active");
  }, []);

  useEffect(() => {
    heading.current?.focus();
  }, [step]);

  function update<K extends keyof ProfileDraft>(key: K, value: ProfileDraft[K]) {
    setDraft((current) => {
      const next = { ...current, [key]: value };
      if (key === "administrativeSex" && value !== "female") {
        next.pregnancyStatus = "";
      }
      return next;
    });
    setError("");
  }

  function advance() {
    const validation = validationMessage(currentStepKey, draft);
    if (validation) {
      setError(validation);
      return;
    }
    setError("");
    setStep((current) => Math.min(current + 1, totalSteps - 1));
  }

  function skip() {
    if (currentStepKey === "pregnancy") {
      update("pregnancyStatus", "");
    }
    setStep((current) => Math.min(current + 1, totalSteps - 1));
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (step < totalSteps - 1) {
      advance();
      return;
    }
    if (busy) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const result = await fetch("/api/patient/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profileSubmission(profile, draft)),
      });
      const response = (await result.json()) as PatientProfileState;
      if (!result.ok || response.state !== "AUTHENTICATED") {
        setError(
          result.status === 409
            ? "Your profile changed elsewhere. Reload the page before trying again."
            : "Your details could not be saved. Please try again.",
        );
        return;
      }
      setMessage("Your profile is ready. Opening your dashboard.");
      router.push("/dashboard");
    } catch {
      setError("Your details could not be saved. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  const title = stepTitles[currentStepKey];

  return (
    <section aria-label="First-time profile setup" className="profile-wizard-shell">
      <div aria-live="polite" className="wizard-progress">
        <span>
          Step {step + 1} of {totalSteps}
        </span>
        <span aria-hidden="true" className="wizard-progress-track">
          <span style={{ width: `${((step + 1) / totalSteps) * 100}%` }} />
        </span>
      </div>
      <form className="profile-wizard-card" noValidate onSubmit={submit}>
        <header className="wizard-heading">
          <p className="card-kicker">Create your private profile</p>
          <h2 ref={heading} tabIndex={-1}>
            {title}
          </h2>
        </header>
        <div className="wizard-field">
          {renderStep(currentStepKey, draft, update, age, bmi, (targetKey) => {
            const targetIndex = steps.indexOf(targetKey);
            if (targetIndex >= 0) setStep(targetIndex);
          })}
        </div>
        {error ? (
          <p className="form-summary" role="alert">
            {error}
          </p>
        ) : null}
        {message ? (
          <p aria-live="polite" className="form-message">
            {message}
          </p>
        ) : null}
        <div className="wizard-actions">
          {step > 0 ? (
            <button
              className="button button--secondary"
              onClick={() => {
                setError("");
                setStep((current) => Math.max(0, current - 1));
              }}
              type="button"
            >
              Back
            </button>
          ) : (
            <span />
          )}
          <div className="wizard-actions-next">
            {currentStepKey === "pregnancy" ? (
              <button className="button button--quiet" onClick={skip} type="button">
                Skip
              </button>
            ) : null}
            <button className="button button--primary" disabled={busy} type="submit">
              {step === totalSteps - 1 ? (busy ? "Saving…" : "Save and open dashboard") : "Next"}
            </button>
          </div>
        </div>
      </form>
      <p className="wizard-privacy-note">Nothing is saved until you confirm the review step.</p>
    </section>
  );
}

function renderStep(
  stepKey: WizardStepKey,
  draft: ProfileDraft,
  update: <K extends keyof ProfileDraft>(key: K, value: ProfileDraft[K]) => void,
  age: number | null,
  bmi: number | null,
  jumpToStep: (stepKey: WizardStepKey) => void,
) {
  if (stepKey === "name")
    return (
      <label>
        Full name
        <input
          autoComplete="name"
          maxLength={120}
          onChange={(event) => update("displayName", event.target.value)}
          value={draft.displayName}
        />
      </label>
    );
  if (stepKey === "language")
    return (
      <label>
        Preferred language
        <select
          onChange={(event) => update("preferredLanguage", event.target.value)}
          value={draft.preferredLanguage}
        >
          <option value="">Choose a language</option>
          <option value="en">English</option>
          <option value="hi">हिन्दी (Hindi)</option>
        </select>
      </label>
    );
  if (stepKey === "dob")
    return (
      <label>
        Date of birth
        <input
          max={new Date().toISOString().slice(0, 10)}
          onChange={(event) => update("dateOfBirth", event.target.value)}
          type="date"
          value={draft.dateOfBirth}
        />
        {age === null ? null : <small>{age} years old</small>}
      </label>
    );
  if (stepKey === "sex")
    return (
      <label>
        Sex recorded for healthcare
        <select
          onChange={(event) => update("administrativeSex", event.target.value)}
          value={draft.administrativeSex}
        >
          <option value="">Choose an option</option>
          <option value="female">Female</option>
          <option value="male">Male</option>
          <option value="intersex">Intersex</option>
          <option value="other">Other</option>
        </select>
      </label>
    );
  if (stepKey === "height")
    return (
      <label>
        Height (cm)
        <input
          inputMode="decimal"
          max={275}
          min={30}
          onChange={(event) => update("heightCm", event.target.value)}
          step="0.1"
          type="number"
          value={draft.heightCm}
        />
      </label>
    );
  if (stepKey === "weight")
    return (
      <label>
        Weight (kg)
        <input
          inputMode="decimal"
          max={700}
          min={1}
          onChange={(event) => update("weightKg", event.target.value)}
          step="0.1"
          type="number"
          value={draft.weightKg}
        />
        {bmi === null ? null : (
          <small>BMI {bmi.toFixed(1)} for profile context only—not a diagnosis.</small>
        )}
      </label>
    );
  if (stepKey === "mobile")
    return (
      <label>
        Mobile number
        <input
          autoComplete="tel"
          inputMode="tel"
          maxLength={16}
          onChange={(event) => update("mobileNumber", event.target.value)}
          placeholder="+919876543210"
          type="tel"
          value={draft.mobileNumber}
        />
        <small>Include the country code. This is not used for login or OTP.</small>
      </label>
    );
  if (stepKey === "bloodGroup")
    return (
      <label>
        Blood group
        <select
          onChange={(event) =>
            update("bloodGroup", event.target.value as ProfileDraft["bloodGroup"])
          }
          value={draft.bloodGroup}
        >
          <option value="">Choose a blood group</option>
          {bloodGroupOptions.map(({ label, value }) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
        <small>
          Self-reported only. Do not rely on this for transfusion or emergency decisions.
        </small>
      </label>
    );
  if (stepKey === "aadhaar")
    return (
      <label>
        Aadhaar number
        <input
          autoComplete="off"
          inputMode="numeric"
          maxLength={12}
          onChange={(event) => update("aadhaarNumber", event.target.value)}
          pattern="[0-9]{12}"
          placeholder="12-digit number"
          type="text"
          value={draft.aadhaarNumber}
        />
        <small>
          Enter your 12-digit Aadhaar number. Only the last four digits are stored to display a
          masked reference.
        </small>
      </label>
    );
  if (stepKey === "pregnancy")
    return (
      <label>
        Pregnancy status (optional)
        <input
          maxLength={256}
          onChange={(event) => update("pregnancyStatus", event.target.value)}
          placeholder="e.g. Second trimester, postpartum, or leave blank"
          value={draft.pregnancyStatus}
        />
      </label>
    );
  return (
    <dl className="wizard-review">
      <div>
        <dt>Full name</dt>
        <dd>{draft.displayName}</dd>
        <button onClick={() => jumpToStep("name")} type="button">
          Edit
        </button>
      </div>
      <div>
        <dt>Preferred language</dt>
        <dd>{draft.preferredLanguage === "hi" ? "Hindi" : "English"}</dd>
        <button onClick={() => jumpToStep("language")} type="button">
          Edit
        </button>
      </div>
      <div>
        <dt>Date of birth</dt>
        <dd>{formatProfileDate(draft.dateOfBirth)}</dd>
        <button onClick={() => jumpToStep("dob")} type="button">
          Edit
        </button>
      </div>
      <div>
        <dt>Sex recorded for healthcare</dt>
        <dd>
          {draft.administrativeSex
            ? draft.administrativeSex[0]?.toUpperCase() + draft.administrativeSex.slice(1)
            : "—"}
        </dd>
        <button onClick={() => jumpToStep("sex")} type="button">
          Edit
        </button>
      </div>
      <div>
        <dt>Height</dt>
        <dd>{draft.heightCm} cm</dd>
        <button onClick={() => jumpToStep("height")} type="button">
          Edit
        </button>
      </div>
      <div>
        <dt>Weight</dt>
        <dd>{draft.weightKg} kg</dd>
        <button onClick={() => jumpToStep("weight")} type="button">
          Edit
        </button>
      </div>
      <div>
        <dt>Mobile number</dt>
        <dd>{draft.mobileNumber}</dd>
        <button onClick={() => jumpToStep("mobile")} type="button">
          Edit
        </button>
      </div>
      <div>
        <dt>Blood group</dt>
        <dd>{draft.bloodGroup}</dd>
        <button onClick={() => jumpToStep("bloodGroup")} type="button">
          Edit
        </button>
      </div>
      <div>
        <dt>Aadhaar number</dt>
        <dd>{maskedAadhaar(draft.aadhaarNumber.slice(-4)) || "Not provided"}</dd>
        <button onClick={() => jumpToStep("aadhaar")} type="button">
          Edit
        </button>
      </div>
      {draft.administrativeSex === "female" ? (
        <div>
          <dt>Pregnancy status</dt>
          <dd>{summaryValue(draft.pregnancyStatus)}</dd>
          <button onClick={() => jumpToStep("pregnancy")} type="button">
            Edit
          </button>
        </div>
      ) : null}
    </dl>
  );
}
