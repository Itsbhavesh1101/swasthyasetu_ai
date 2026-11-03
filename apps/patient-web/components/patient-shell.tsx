import Link from "next/link";
import type { ReactNode } from "react";

import { PatientNavigation } from "./patient-navigation";
import { AccountMenu } from "./account-menu";
import { UrgentHelpLink } from "./urgent-help-link";

export function PatientShell({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <div className="patient-shell">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <aside aria-label="Patient workspace" className="patient-sidebar">
        <div className="sidebar-primary">
          <Link aria-label="SwasthyaSetu patient home" className="brand" href="/">
            <span aria-hidden="true" className="brand-mark">
              <span>S</span>
            </span>
            <span>
              <strong>SwasthyaSetu</strong>
              <small>Patient care</small>
            </span>
          </Link>
          <p className="privacy-label">
            <span aria-hidden="true" className="privacy-dot" />
            Private health space
          </p>
          <PatientNavigation />
        </div>
        <div className="sidebar-support">
          <p>
            <strong>Your records, your control</strong>
            <span>Health information stays within your private account.</span>
          </p>
          <UrgentHelpLink />
        </div>
      </aside>
      <div className="patient-workspace">
        <header className="site-header">
          <div className="header-primary">
            <div className="workspace-title">
              <span aria-hidden="true" className="workspace-pulse" />
              <span>
                <small>SwasthyaSetu</small>
                <strong>Personal health workspace</strong>
              </span>
            </div>
            <div className="header-actions">
              <AccountMenu />
            </div>
          </div>
        </header>
        <main className="main-content" id="main-content" tabIndex={-1}>
          {children}
        </main>
        <footer className="site-footer">
          <div className="footer-content">
            <div>
              <strong>SwasthyaSetu Patient</strong>
              <p>Your private health history, documents, and guided intake in one place.</p>
            </div>
            <p>
              This college demonstration supports personal record keeping. It does not replace a
              doctor, diagnosis, treatment, or emergency care.
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
