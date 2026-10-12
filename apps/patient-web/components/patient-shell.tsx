import Link from "next/link";
import type { ReactNode } from "react";

import { PatientNavigation } from "./patient-navigation";
import { UrgentHelpLink } from "./urgent-help-link";

export function PatientShell({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <div className="patient-shell">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <header className="site-header">
        <div className="shell-container header-primary">
          <Link aria-label="SwasthyaSetu patient home" className="brand" href="/">
            <span aria-hidden="true" className="brand-mark">
              S
            </span>
            <span>
              <strong>SwasthyaSetu</strong>
              <small>Patient</small>
            </span>
          </Link>
          <UrgentHelpLink />
        </div>
        <div className="shell-container">
          <PatientNavigation />
        </div>
      </header>
      <main className="shell-container main-content" id="main-content" tabIndex={-1}>
        {children}
      </main>
      <footer className="site-footer">
        <div className="shell-container footer-content">
          <div>
            <strong>SwasthyaSetu Patient</strong>
            <p>A respectful, privacy-conscious place to begin.</p>
          </div>
          <p>
            This early shell does not provide medical advice, diagnosis, or verified emergency
            contacts.
          </p>
        </div>
      </footer>
    </div>
  );
}
