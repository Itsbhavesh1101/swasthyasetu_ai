import type { Metadata } from "next";
import Link from "next/link";

import { AccountForm } from "../components/account-form";

export const metadata: Metadata = { title: "Sign in" };

export default function PatientHomePage() {
  return (
    <section aria-labelledby="login-title" className="auth-card">
      <header className="auth-card-header">
        <p className="page-eyebrow">Your private health record</p>
        <h1 id="login-title">Welcome back</h1>
        <p>Sign in to continue to your medical history, documents, and personal health profile.</p>
      </header>
      <AccountForm mode="login" />
      <p className="auth-switch">
        New to SwasthyaSetu? <Link href="/register">Create account</Link>
      </p>
    </section>
  );
}
