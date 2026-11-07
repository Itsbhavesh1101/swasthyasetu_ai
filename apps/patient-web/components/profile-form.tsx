"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import type {
  PatientDemographics,
  PatientProfile,
  PatientProfileState,
  PatientProfileSubmission,
} from "../lib/patient/contracts";
import { ErrorState, LoadingState } from "./ui-primitives";

const emptyDemographics: PatientDemographics = {
  dateOfBirth: null,
  administrativeSex: null,
  genderIdentity: null,
  pregnancyStatus: null,
  locationContext: null,
  heightCm: null,
  weightKg: null,
  bmi: null,
  mobileNumber: null,
  bloodGroup: null,
  demoAadhaarReference: null,
};

function optional(data: FormData, name: string) {
  const value = String(data.get(name) ?? "").trim();
  return value || null;
}

async function requestProfile() {
  const result = await fetch("/api/patient/profile", { cache: "no-store" });
  return { result, data: (await result.json()) as PatientProfileState };
}

export function ProfileForm() {
  const router = useRouter();
  const [profile, setProfile] = useState<PatientProfile>();
  const [anonymous, setAnonymous] = useState(false);
  const [failed, setFailed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [heightCm, setHeightCm] = useState("");
  const [weightKg, setWeightKg] = useState("");

  async function load() {
    try {
      const { result, data } = await requestProfile();
      if (result.status === 401 || data.state === "ANONYMOUS") {
        setAnonymous(true);
        return;
      }
      if (!result.ok || data.state !== "AUTHENTICATED") throw new Error("profile unavailable");
      setProfile(data.profile);
      setDateOfBirth(data.profile.demographics?.dateOfBirth ?? "");
      setHeightCm(String(data.profile.demographics?.heightCm ?? ""));
      setWeightKg(String(data.profile.demographics?.weightKg ?? ""));
    } catch {
      setFailed(true);
    }
  }

  useEffect(() => {
    let active = true;
    void requestProfile()
      .then(({ result, data }) => {
        if (!active) return;
        if (result.status === 401 || data.state === "ANONYMOUS") {
          setAnonymous(true);
        } else if (!result.ok || data.state !== "AUTHENTICATED") {
          setFailed(true);
        } else {
          setProfile(data.profile);
          setDateOfBirth(data.profile.demographics?.dateOfBirth ?? "");
          setHeightCm(String(data.profile.demographics?.heightCm ?? ""));
          setWeightKg(String(data.profile.demographics?.weightKg ?? ""));
        }
      })
      .catch(() => {
        if (active) setFailed(true);
      });
    return () => {
      active = false;
    };
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!profile || busy) return;
    const data = new FormData(event.currentTarget);
    const payload: PatientProfileSubmission = {
      expectedUpdatedAt: profile.updatedAt,
      preferredLanguage: optional(data, "preferredLanguage"),
      displayName: String(data.get("displayName") ?? "").trim(),
      demographics: {
        dateOfBirth: optional(data, "dateOfBirth"),
        administrativeSex: optional(data, "administrativeSex"),
        genderIdentity: optional(data, "genderIdentity"),
        pregnancyStatus: optional(data, "pregnancyStatus"),
        locationContext: optional(data, "locationContext"),
        heightCm: Number(data.get("heightCm")),
        weightKg: Number(data.get("weightKg")),
        mobileNumber: demographics.mobileNumber,
        bloodGroup: demographics.bloodGroup,
        demoAadhaarReference: demographics.demoAadhaarReference,
      },
    };
    setBusy(true);
    setMessage("");
    try {
      const result = await fetch("/api/patient/profile", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const response = (await result.json()) as PatientProfileState;
      if (!result.ok || response.state !== "AUTHENTICATED") {
        setMessage(
          result.status === 409
            ? "Your profile changed elsewhere. Reload the page before trying again."
            : "Your details could not be saved. Please try again.",
        );
        if (result.status !== 409) void load();
        return;
      }
      setProfile(response.profile);
      setMessage("Your profile is ready. Opening your dashboard.");
      router.push("/dashboard");
    } catch {
      setMessage("Your details could not be saved. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  if (anonymous)
    return (
      <section className="panel">
        <h2>Sign in to edit your profile</h2>
        <p>Your personal details are protected by your patient account.</p>
        <Link className="action-link action-link--primary" href="/login">
          Sign in <span aria-hidden="true">→</span>
        </Link>
      </section>
    );
  if (failed)
    return (
      <ErrorState
        onRetry={() => {
          setFailed(false);
          void load();
        }}
      />
    );
  if (!profile) return <LoadingState label="Loading your personal details." />;
  const demographics = profile.demographics ?? emptyDemographics;
  const parsedHeight = Number(heightCm);
  const parsedWeight = Number(weightKg);
  const bmi =
    parsedHeight >= 30 && parsedWeight >= 1 ? parsedWeight / (parsedHeight / 100) ** 2 : null;
  const birthDate = /^\d{4}-\d{2}-\d{2}$/.test(dateOfBirth)
    ? new Date(`${dateOfBirth}T00:00:00Z`)
    : null;
  const today = new Date();
  const age = birthDate
    ? today.getUTCFullYear() -
      birthDate.getUTCFullYear() -
      (today.getUTCMonth() < birthDate.getUTCMonth() ||
      (today.getUTCMonth() === birthDate.getUTCMonth() &&
        today.getUTCDate() < birthDate.getUTCDate())
        ? 1
        : 0)
    : null;

  return (
    <form className="profile-form panel" onSubmit={submit}>
      <header className="form-heading">
        <p className="card-kicker">Step 2 of 2</p>
        <h2>{profile.profileComplete ? "Edit your base profile" : "Create your base profile"}</h2>
        <p>These details personalize your health record. You can update them later.</p>
      </header>
      <div className="form-grid">
        <label>
          Full name
          <input
            autoComplete="name"
            defaultValue={profile.displayName ?? ""}
            maxLength={120}
            name="displayName"
            required
          />
        </label>
        <label>
          Preferred language
          <select defaultValue={profile.preferredLanguage ?? ""} name="preferredLanguage">
            <option value="">No preference</option>
            <option value="en">English</option>
            <option value="hi">हिन्दी (Hindi)</option>
          </select>
        </label>
        <label>
          Date of birth
          <input
            max={new Date().toISOString().slice(0, 10)}
            name="dateOfBirth"
            onChange={(event) => setDateOfBirth(event.target.value)}
            required
            type="date"
            value={dateOfBirth}
          />
        </label>
        <label>
          Age (calculated)
          <output className="calculated-field">
            {age === null || age < 0 ? "—" : `${age} years`}
          </output>
        </label>
        <label>
          Sex recorded for healthcare
          <select
            defaultValue={demographics.administrativeSex ?? ""}
            name="administrativeSex"
            required
          >
            <option disabled value="">
              Select an option
            </option>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="intersex">Intersex</option>
            <option value="other">Other</option>
          </select>
        </label>
        <label>
          Height (cm)
          <input
            inputMode="decimal"
            max={275}
            min={30}
            name="heightCm"
            onChange={(event) => setHeightCm(event.target.value)}
            required
            step="0.1"
            type="number"
            value={heightCm}
          />
        </label>
        <label>
          Weight (kg)
          <input
            inputMode="decimal"
            max={700}
            min={1}
            name="weightKg"
            onChange={(event) => setWeightKg(event.target.value)}
            required
            step="0.1"
            type="number"
            value={weightKg}
          />
        </label>
        <label>
          BMI (calculated)
          <output className="calculated-field">{bmi === null ? "—" : bmi.toFixed(1)}</output>
          <small>For profile context only; this is not a diagnosis.</small>
        </label>
        <label>
          Gender identity (optional)
          <input
            defaultValue={demographics.genderIdentity ?? ""}
            maxLength={256}
            name="genderIdentity"
          />
        </label>
        <label>
          Pregnancy status (optional)
          <input
            defaultValue={demographics.pregnancyStatus ?? ""}
            maxLength={256}
            name="pregnancyStatus"
          />
        </label>
        <label>
          City or location (optional)
          <input
            autoComplete="address-level2"
            defaultValue={demographics.locationContext ?? ""}
            maxLength={256}
            name="locationContext"
          />
        </label>
      </div>
      {message ? (
        <p aria-live="polite" className="form-message">
          {message}
        </p>
      ) : null}
      <button className="button button--primary" disabled={busy} type="submit">
        {busy ? "Saving…" : profile.profileComplete ? "Save details" : "Create profile"}
      </button>
    </form>
  );
}
