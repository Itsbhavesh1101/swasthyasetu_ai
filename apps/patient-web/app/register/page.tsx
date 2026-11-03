import Link from "next/link";
import { AccountForm } from "../../components/account-form";
export default function RegisterPage() {
  return (
    <section aria-labelledby="register-title" className="auth-card">
      <header className="auth-card-header">
        <p className="page-eyebrow">Start your private record</p>
        <h1 id="register-title">Create your patient account</h1>
        <p>Use your email and a secure password. Your personal details are collected next.</p>
      </header>
      <AccountForm mode="register" />
      <p className="auth-switch">
        Already registered? <Link href="/login">Sign in</Link>
      </p>
    </section>
  );
}
