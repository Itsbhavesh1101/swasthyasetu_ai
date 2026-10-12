import type { Metadata } from "next";
import type { ReactNode } from "react";

import { PatientShell } from "../components/patient-shell";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "SwasthyaSetu Patient",
    template: "%s | SwasthyaSetu",
  },
  description: "A clear, privacy-conscious starting point for the SwasthyaSetu patient journey.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <PatientShell>{children}</PatientShell>
      </body>
    </html>
  );
}
