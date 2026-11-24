"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import type {
  BloodGroup,
  PatientDemographics,
  PatientProfile,
  PatientProfileState,
  PatientProfileSubmission,
} from "../lib/patient/contracts";
import {
  bloodGroupOptions,
  calculatedAge,
  calculatedBmi,
  formatProfileDate,
  maskedAadhaar,
} from "./profile-fields";
import { ProfileSetupWizard } from "./profile-setup-wizard";
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
  aadhaarLastFour: null,
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
  const [profile, setProfile] = useState<PatientProfile>();
  const [anonymous, setAnonymous] = useState(false);
  const [failed, setFailed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [isEditing, setIsEditing] = useState(false);

  const [dateOfBirth, setDateOfBirth] = useState("");
  const [heightCm, setHeightCm] = useState("");
  const [weightKg, setWeightKg] = useState("");
  const [selectedSex, setSelectedSex] = useState("");

  function syncProfileState(loadedProfile: PatientProfile) {
    setProfile(loadedProfile);
    setDateOfBirth(loadedProfile.demographics?.dateOfBirth ?? "");
    setHeightCm(String(loadedProfile.demographics?.heightCm ?? ""));
    setWeightKg(String(loadedProfile.demographics?.weightKg ?? ""));
    setSelectedSex(loadedProfile.demographics?.administrativeSex ?? "");
  }

  async function load() {
    try {
      const { result, data } = await requestProfile();
      if (result.status === 401 || data.state === "ANONYMOUS") {
        setAnonymous(true);
        return;
      }
      if (!result.ok || data.state !== "AUTHENTICATED") throw new Error("profile unavailable");
      syncProfileState(data.profile);
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
          syncProfileState(data.profile);
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
    const administrativeSex = optional(data, "administrativeSex");
    const payload: PatientProfileSubmission = {
      expectedUpdatedAt: profile.updatedAt,
      preferredLanguage: optional(data, "preferredLanguage"),
      displayName: String(data.get("displayName") ?? "").trim(),
      demographics: {
        dateOfBirth: optional(data, "dateOfBirth"),
        administrativeSex,
        genderIdentity: null,
        pregnancyStatus:
          administrativeSex === "female" ? optional(data, "pregnancyStatus") : null,
        locationContext: null,
        heightCm: Number(data.get("heightCm")),
        weightKg: Number(data.get("weightKg")),
        mobileNumber: optional(data, "mobileNumber"),
        bloodGroup: optional(data, "bloodGroup") as BloodGroup | null,
        aadhaarNumber: optional(data, "aadhaarNumber"),
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
      syncProfileState(response.profile);
      setIsEditing(false);
      setMessage("Your profile details have been updated.");
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
  if (!profile.profileComplete) return <ProfileSetupWizard profile={profile} />;

  const demographics = profile.demographics ?? emptyDemographics;
  const parsedHeight = Number(heightCm);
  const parsedWeight = Number(weightKg);
  const bmi = calculatedBmi(heightCm, weightKg);
  const age = calculatedAge(dateOfBirth);

  if (!isEditing) {
    const lockedAge = calculatedAge(demographics.dateOfBirth ?? "");
    const lockedBmi =
      demographics.bmi !== null && demographics.bmi !== undefined
        ? Number(demographics.bmi).toFixed(1)
        : demographics.heightCm && demographics.weightKg
          ? (
              demographics.weightKg /
              ((demographics.heightCm / 100) * (demographics.heightCm / 100))
            ).toFixed(1)
          : null;

    return (
      <article className="panel profile-view">
        <div className="profile-view-header">
          <div>
            <p className="card-kicker">Patient profile</p>
            <h2>{profile.displayName || "Personal details"}</h2>
            <p className="profile-subtitle">
              Your basic health profile details are saved and locked.
            </p>
          </div>
          <button
            className="button button--secondary edit-profile-button"
            onClick={() => {
              setIsEditing(true);
              setMessage("");
              setDateOfBirth(demographics.dateOfBirth ?? "");
              setHeightCm(String(demographics.heightCm ?? ""));
              setWeightKg(String(demographics.weightKg ?? ""));
              setSelectedSex(demographics.administrativeSex ?? "");
            }}
            type="button"
          >
            Edit details
          </button>
        </div>

        <div className="profile-detail-grid">
          <div className="profile-detail-item">
            <span className="profile-detail-label">Full name</span>
            <span className="profile-detail-value">{profile.displayName || "—"}</span>
          </div>

          <div className="profile-detail-item">
            <span className="profile-detail-label">Preferred language</span>
            <span className="profile-detail-value">
              {profile.preferredLanguage === "hi"
                ? "हिन्दी (Hindi)"
                : profile.preferredLanguage === "en"
                  ? "English"
                  : "No preference"}
            </span>
          </div>

          <div className="profile-detail-item">
            <span className="profile-detail-label">Date of birth</span>
            <span className="profile-detail-value">
              {formatProfileDate(demographics.dateOfBirth)}
              {lockedAge !== null ? ` (${lockedAge} years old)` : ""}
            </span>
          </div>

          <div className="profile-detail-item">
            <span className="profile-detail-label">Sex recorded for healthcare</span>
            <span className="profile-detail-value">
              {demographics.administrativeSex
                ? demographics.administrativeSex.charAt(0).toUpperCase() +
                  demographics.administrativeSex.slice(1)
                : "—"}
            </span>
          </div>

          <div className="profile-detail-item">
            <span className="profile-detail-label">Height</span>
            <span className="profile-detail-value">
              {demographics.heightCm ? `${demographics.heightCm} cm` : "—"}
            </span>
          </div>

          <div className="profile-detail-item">
            <span className="profile-detail-label">Weight</span>
            <span className="profile-detail-value">
              {demographics.weightKg ? `${demographics.weightKg} kg` : "—"}
            </span>
          </div>

          <div className="profile-detail-item">
            <span className="profile-detail-label">BMI (calculated)</span>
            <span className="profile-detail-value">{lockedBmi ?? "—"}</span>
          </div>

          <div className="profile-detail-item">
            <span className="profile-detail-label">Mobile number</span>
            <span className="profile-detail-value">{demographics.mobileNumber || "—"}</span>
          </div>

          <div className="profile-detail-item">
            <span className="profile-detail-label">Blood group</span>
            <span className="profile-detail-value">{demographics.bloodGroup || "—"}</span>
          </div>

          <div className="profile-detail-item">
            <span className="profile-detail-label">Aadhaar number</span>
            <span className="profile-detail-value">
              {maskedAadhaar(demographics.aadhaarLastFour) || "Not provided"}
            </span>
          </div>

          {demographics.administrativeSex === "female" && demographics.pregnancyStatus ? (
            <div className="profile-detail-item">
              <span className="profile-detail-label">Pregnancy status</span>
              <span className="profile-detail-value">{demographics.pregnancyStatus}</span>
            </div>
          ) : null}
        </div>

        {message ? (
          <p aria-live="polite" className="form-message">
            {message}
          </p>
        ) : null}
      </article>
    );
  }

  return (
    <form className="profile-form panel" onSubmit={submit}>
      <header className="form-heading profile-edit-header">
        <div>
          <p className="card-kicker">Edit profile</p>
          <h2>Edit your personal details</h2>
          <p>Update the personal details supporting your health record.</p>
        </div>
        <button
          className="button button--secondary"
          onClick={() => {
            setIsEditing(false);
            setMessage("");
          }}
          type="button"
        >
          Cancel
        </button>
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
            name="administrativeSex"
            onChange={(event) => setSelectedSex(event.target.value)}
            required
            value={selectedSex}
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
          Mobile number
          <input
            autoComplete="tel"
            defaultValue={demographics.mobileNumber ?? ""}
            inputMode="tel"
            maxLength={16}
            name="mobileNumber"
            pattern="\+[1-9][0-9]{6,14}"
            placeholder="+919876543210"
            required
            type="tel"
          />
          <small>Include the country code. This is not used for login or OTP.</small>
        </label>
        <label>
          Blood group
          <select defaultValue={demographics.bloodGroup ?? ""} name="bloodGroup" required>
            <option disabled value="">
              Choose a blood group
            </option>
            {bloodGroupOptions.map(({ label, value }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <small>Self-reported only. Do not rely on this for emergency decisions.</small>
        </label>
        <label>
          Replace Aadhaar number (optional)
          {demographics.aadhaarLastFour ? (
            <small>Current: {maskedAadhaar(demographics.aadhaarLastFour)}</small>
          ) : null}
          <input
            autoComplete="off"
            inputMode="numeric"
            maxLength={12}
            name="aadhaarNumber"
            pattern="[0-9]{12}"
            placeholder="Enter 12 digits to update"
            type="text"
          />
        </label>
        {selectedSex === "female" ? (
          <label>
            Pregnancy status (optional)
            <input
              defaultValue={demographics.pregnancyStatus ?? ""}
              maxLength={256}
              name="pregnancyStatus"
            />
          </label>
        ) : null}
      </div>
      {message ? (
        <p aria-live="polite" className="form-message">
          {message}
        </p>
      ) : null}
      <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
        <button className="button button--primary" disabled={busy} type="submit">
          {busy ? "Saving…" : "Save details"}
        </button>
        <button
          className="button button--secondary"
          onClick={() => {
            setIsEditing(false);
            setMessage("");
          }}
          type="button"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
