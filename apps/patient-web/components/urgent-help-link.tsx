import Link from "next/link";

export function UrgentHelpLink() {
  return (
    <Link className="urgent-help-link" href="/urgent-help">
      <span aria-hidden="true" className="urgent-help-dot" />
      Urgent help
    </Link>
  );
}
