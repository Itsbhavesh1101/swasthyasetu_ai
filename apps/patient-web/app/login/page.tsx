import Link from "next/link";
import { AccountForm } from "../../components/account-form";
import { PageHeader } from "../../components/ui-primitives";
export default function LoginPage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Welcome back"
        title="Sign in to your health record"
        description="Your password stays private and is never shown after submission."
      />
      <AccountForm mode="login" />
      <p>
        New here? <Link href="/register">Create an account</Link>.
      </p>
    </div>
  );
}
