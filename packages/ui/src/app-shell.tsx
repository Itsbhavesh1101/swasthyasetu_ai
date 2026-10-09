import type { ReactNode } from "react";

export interface AppShellProps {
  readonly children: ReactNode;
  readonly title: string;
}

export function AppShell({ children, title }: AppShellProps) {
  return (
    <div className="min-h-screen bg-[var(--color-canvas)] text-[var(--color-text)]">
      <a className="skip-link" href="#main-content">
        Skip to main content
      </a>
      <header className="border-b border-[var(--color-border)] bg-[var(--color-surface)]">
        <div className="mx-auto max-w-5xl px-6 py-8">
          <p className="mb-2 text-sm font-semibold tracking-wide text-[var(--color-accent)] uppercase">
            SwasthyaSetu AI
          </p>
          <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-12" id="main-content">
        {children}
      </main>
      <footer className="mx-auto max-w-5xl px-6 py-8 text-sm text-[var(--color-muted)]">
        Foundation workspace
      </footer>
    </div>
  );
}
