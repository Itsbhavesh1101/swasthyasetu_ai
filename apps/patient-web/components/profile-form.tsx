"use client";

import Link from "next/link";
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

  async function load() {
    try {
      const { result, data } = await requestProfile();
      if (result.status === 401 || data.state === "ANONYMOUS") {
        setAnonymous(true);
        return;
      }
      if (!result.ok || data.state !== "AUTHENTICATED") throw new Error("profile unavailable");
      setProfile(data.profile);
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
      demographics: {
        dateOfBirth: optional(data, "dateOfBirth"),
        administrativeSex: optional(data, "administrativeSex"),
        genderIdentity: optional(data, "genderIdentity"),
        pregnancyStatus: optional(data, "pregnancyStatus"),
        locationContext: optional(data, "locationContext"),
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
        return;
      }
      setProfile(response.profile);
      setMessage("Your details have been saved.");
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

  return (
    <form className="profile-form panel" onSubmit={submit}>
      <div className="form-grid">
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
          <input defaultValue={demographics.dateOfBirth ?? ""} name="dateOfBirth" type="date" />
        </label>
        <label>
          Sex recorded for healthcare
          <select defaultValue={demographics.administrativeSex ?? ""} name="administrativeSex">
            <option value="">Prefer not to say</option>
            <option value="female">Female</option>
            <option value="male">Male</option>
            <option value="intersex">Intersex</option>
            <option value="other">Other</option>
          </select>
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
        {busy ? "Saving…" : "Save details"}
      </button>
    </form>
  );
}
