import Link from "next/link";
import type { ReactNode } from "react";

type ActionVariant = "primary" | "secondary" | "critical";

export function ActionLink({
  children,
  href,
  variant = "primary",
}: Readonly<{ children: ReactNode; href: string; variant?: ActionVariant }>) {
  return (
    <Link className={`action-link action-link--${variant}`} href={href}>
      {children}
      <span aria-hidden="true">→</span>
    </Link>
  );
}

export function PageHeader({
  description,
  eyebrow,
  title,
}: Readonly<{ description?: string; eyebrow?: string; title: string }>) {
  return (
    <header className="page-header">
      {eyebrow ? <p className="page-eyebrow">{eyebrow}</p> : null}
      <h1>{title}</h1>
      {description ? <p className="page-description">{description}</p> : null}
    </header>
  );
}

export function Panel({ children }: Readonly<{ children: ReactNode }>) {
  return <article className="panel">{children}</article>;
}

export function StatusBanner({
  children,
  title,
  tone = "info",
}: Readonly<{ children: ReactNode; title: string; tone?: "info" | "critical" }>) {
  return (
    <section
      aria-labelledby={`status-${tone}-title`}
      className={`status-banner status-banner--${tone}`}
    >
      <span aria-hidden="true" className="status-symbol">
        {tone === "critical" ? "!" : "i"}
      </span>
      <div>
        <h2 id={`status-${tone}-title`}>{title}</h2>
        <div>{children}</div>
      </div>
    </section>
  );
}

export function LoadingState({ label }: Readonly<{ label: string }>) {
  return (
    <section aria-busy="true" aria-live="polite" className="state-panel" role="status">
      <span aria-hidden="true" className="loading-indicator" />
      <div>
        <h2>One moment</h2>
        <p>{label}</p>
      </div>
    </section>
  );
}

export function ErrorState({ onRetry }: Readonly<{ onRetry: () => void }>) {
  return (
    <section aria-labelledby="patient-error-title" className="state-panel" role="alert">
      <span aria-hidden="true" className="state-symbol">
        !
      </span>
      <div>
        <h2 id="patient-error-title">Something interrupted this page</h2>
        <p>No information was submitted. You can safely try to open the page again.</p>
        <button className="button button--primary" onClick={onRetry} type="button">
          Try this page again
        </button>
      </div>
    </section>
  );
}

export function UnavailableState({
  availableIn,
  description,
  title,
}: Readonly<{ availableIn: string; description: string; title: string }>) {
  return (
    <section aria-labelledby="unavailable-title" className="state-panel state-panel--unavailable">
      <span aria-hidden="true" className="state-symbol">
        …
      </span>
      <div>
        <p className="state-label">Not available yet</p>
        <h2 id="unavailable-title">{title}</h2>
        <p>{description}</p>
        <p className="availability-note">Planned for {availableIn}.</p>
        <button className="button button--disabled" disabled type="button">
          Continue unavailable
        </button>
      </div>
    </section>
  );
}
