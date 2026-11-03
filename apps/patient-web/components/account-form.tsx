"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { submitAccount } from "../lib/account/client";

export function AccountForm({ mode }: Readonly<{ mode: "login" | "register" }>) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const form = event.currentTarget;
    const data = new FormData(form);
    const password = String(data.get("password") ?? "");
    const confirmation = String(data.get("confirmation") ?? "");
    setError("");
    if (mode === "register" && password !== confirmation) {
      setError("Passwords do not match. Please enter them again.");
      return;
    }
    setBusy(true);
    const result = await submitAccount(mode, {
      email: String(data.get("email") ?? ""),
      password,
    });
    const passwordInput = form.elements.namedItem("password") as HTMLInputElement;
    passwordInput.value = "";
    const confirmationInput = form.elements.namedItem("confirmation") as HTMLInputElement | null;
    if (confirmationInput) confirmationInput.value = "";
    if (result?.state === "AUTHENTICATED") {
      setSuccess(
        mode === "register" ? "Account created. Let’s create your profile." : "Signed in.",
      );
      router.push(result.profileComplete ? "/dashboard" : "/profile?setup=1");
    } else {
      setError(
        mode === "login"
          ? "We could not sign you in with those details."
          : "We could not create your account. Check the details and try again.",
      );
      setBusy(false);
    }
  }

  return (
    <form className="account-form panel" noValidate onSubmit={submit}>
      {error ? (
        <div className="form-summary" role="alert">
          {error}
        </div>
      ) : null}
      {success ? <div aria-live="polite">{success}</div> : null}
      <label>
        Email address
        <input autoComplete="email" maxLength={320} name="email" required type="email" />
      </label>
      <label>
        Password
        <input
          autoComplete={mode === "login" ? "current-password" : "new-password"}
          minLength={12}
          maxLength={128}
          name="password"
          required
          type="password"
        />
      </label>
      {mode === "register" ? (
        <label>
          Confirm password
          <input
            autoComplete="new-password"
            minLength={12}
            maxLength={128}
            name="confirmation"
            required
            type="password"
          />
        </label>
      ) : null}
      <button className="button button--primary" disabled={busy} type="submit">
        {busy ? "Please wait…" : mode === "register" ? "Create account" : "Sign in"}
      </button>
    </form>
  );
}
