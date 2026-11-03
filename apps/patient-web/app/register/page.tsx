import Link from "next/link";
import { AccountForm } from "../../components/account-form";
import { PageHeader } from "../../components/ui-primitives";
export default function RegisterPage() {
  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Private patient record"
        title="Create your patient account"
        description="Use your name and email to create a private health record you can return to."
      />
      <AccountForm mode="register" />
      <p>
        Already registered? <Link href="/login">Sign in</Link>.
      </p>
    </div>
  );
}
