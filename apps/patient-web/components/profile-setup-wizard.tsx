"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import type { PatientProfile, PatientProfileState } from "../lib/patient/contracts";
import {
  bloodGroupOptions,
  calculatedAge,
  calculatedBmi,
  profileDraft,
  profileSubmission,
  type ProfileDraft,
} from "./profile-fields";

const totalSteps = 13;
const optionalSteps = new Set([9, 10, 11]);
const supportedSexValues = new Set(["female", "male", "intersex", "other"]);

function validationMessage(step: number, draft: ProfileDraft): string {
  if (step === 0 && (!draft.displayName.trim() || draft.displayName.trim().length > 120))
    return "Enter your full name.";
  if (step === 1 && !["en", "hi"].includes(draft.preferredLanguage))
    return "Choose your preferred language.";
  if (
    step === 2 &&
    (!/^\d{4}-\d{2}-\d{2}$/.test(draft.dateOfBirth) || calculatedAge(draft.dateOfBirth) === null)
  )
    return "Enter a valid date of birth.";
  if (step === 3 && !supportedSexValues.has(draft.administrativeSex))
    return "Choose the sex recorded for healthcare.";
  if (step === 4 && !(Number(draft.heightCm) >= 30 && Number(draft.heightCm) <= 275))
    return "Enter a height between 30 and 275 cm.";
  if (step === 5 && !(Number(draft.weightKg) >= 1 && Number(draft.weightKg) <= 700))
    return "Enter a weight between 1 and 700 kg.";
  if (step === 6 && !/^\+[1-9][0-9]{6,14}$/.test(draft.mobileNumber))
    return "Enter a mobile number in international format, such as +919876543210.";
  if (step === 7 && !bloodGroupOptions.some(({ value }) => value === draft.bloodGroup))
    return "Choose your blood group or Unknown.";
  if (step === 8 && !/^DEMO-AADHAAR-[0-9]{4}$/.test(draft.demoAadhaarReference))
    return "Do not enter a real Aadhaar number. Use the synthetic format DEMO-AADHAAR-1234.";
  if (step === 9 && draft.genderIdentity.trim().length > 256)
    return "Gender identity must be 256 characters or fewer.";
  if (step === 10 && draft.pregnancyStatus.trim().length > 256)
    return "Pregnancy status must be 256 characters or fewer.";
  if (step === 11 && draft.locationContext.trim().length > 256)
    return "Location must be 256 characters or fewer.";
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

  useEffect(() => {
    document.body.classList.add("profile-setup-active");
    return () => document.body.classList.remove("profile-setup-active");
  }, []);

  useEffect(() => {
    heading.current?.focus();
  }, [step]);

  function update<K extends keyof ProfileDraft>(key: K, value: ProfileDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }));
    setError("");
  }

  function advance() {
    const validation = validationMessage(step, draft);
    if (validation) {
      setError(validation);
      return;
    }
    setError("");
    setStep((current) => Math.min(current + 1, totalSteps - 1));
  }

  function skip() {
    const optionalKey = (["genderIdentity", "pregnancyStatus", "locationContext"] as const)[
      step - 9
    ];
    if (optionalKey) update(optionalKey, "");
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

  const title = [
    "What should we call you?",
    "Which language do you prefer?",
    "When were you born?",
    "What sex is recorded for healthcare?",
    "What is your height?",
    "What is your weight?",
    "What is your mobile number?",
    "What is your blood group?",
    "Add a synthetic Aadhaar demonstration reference",
    "How do you describe your gender identity?",
    "Would you like to add pregnancy status?",
    "Where are you based?",
    "Review your details",
  ][step];

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
        <div className="wizard-field">{renderStep(step, draft, update, age, bmi, setStep)}</div>
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
                setStep((current) => current - 1);
              }}
              type="button"
            >
              Back
            </button>
          ) : (
            <span />
          )}
          <div className="wizard-actions-next">
            {optionalSteps.has(step) ? (
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
  step: number,
  draft: ProfileDraft,
  update: <K extends keyof ProfileDraft>(key: K, value: ProfileDraft[K]) => void,
  age: number | null,
  bmi: number | null,
  setStep: (step: number) => void,
) {
  if (step === 0)
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
  if (step === 1)
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
  if (step === 2)
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
  if (step === 3)
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
  if (step === 4)
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
  if (step === 5)
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
  if (step === 6)
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
  if (step === 7)
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
  if (step === 8)
    return (
      <label>
        Aadhaar demonstration reference
        <input
          autoCapitalize="characters"
          maxLength={17}
          onChange={(event) => update("demoAadhaarReference", event.target.value.toUpperCase())}
          placeholder="DEMO-AADHAAR-1234"
          value={draft.demoAadhaarReference}
        />
        <small>Synthetic college-demo value only. Never enter a real Aadhaar number.</small>
      </label>
    );
  if (step === 9)
    return (
      <label>
        Gender identity (optional)
        <input
          maxLength={256}
          onChange={(event) => update("genderIdentity", event.target.value)}
          value={draft.genderIdentity}
        />
      </label>
    );
  if (step === 10)
    return (
      <label>
        Pregnancy status (optional)
        <input
          maxLength={256}
          onChange={(event) => update("pregnancyStatus", event.target.value)}
          value={draft.pregnancyStatus}
        />
      </label>
    );
  if (step === 11)
    return (
      <label>
        City or location (optional)
        <input
          autoComplete="address-level2"
          maxLength={256}
          onChange={(event) => update("locationContext", event.target.value)}
          value={draft.locationContext}
        />
      </label>
    );
  return (
    <dl className="wizard-review">
      <div>
        <dt>Full name</dt>
        <dd>{draft.displayName}</dd>
        <button onClick={() => setStep(0)} type="button">
          Edit
        </button>
      </div>
      <div>
        <dt>Mobile number</dt>
        <dd>{draft.mobileNumber}</dd>
        <button onClick={() => setStep(6)} type="button">
          Edit
        </button>
      </div>
      <div>
        <dt>Blood group</dt>
        <dd>{draft.bloodGroup}</dd>
        <button onClick={() => setStep(7)} type="button">
          Edit
        </button>
      </div>
      <div>
        <dt>Aadhaar demo reference</dt>
        <dd>{draft.demoAadhaarReference}</dd>
        <button onClick={() => setStep(8)} type="button">
          Edit
        </button>
      </div>
      <div>
        <dt>Location</dt>
        <dd>{summaryValue(draft.locationContext)}</dd>
        <button onClick={() => setStep(11)} type="button">
          Edit
        </button>
      </div>
    </dl>
  );
}
