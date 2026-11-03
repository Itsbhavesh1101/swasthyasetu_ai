import Link from "next/link";
import { AccountForm } from "../../components/account-form";
import { PageHeader } from "../../components/ui-primitives";
export default function RegisterPage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Private patient record"
        title="Create your patient account"
        description="Use your email and a secure password first. You will create your personal profile next."
      />
      <AccountForm mode="register" />
      <p>
        Already registered? <Link href="/login">Sign in</Link>.
      </p>
    </div>
  );
}
