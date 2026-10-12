import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { PatientShell } from "../components/patient-shell";

vi.mock("next/navigation", () => ({ usePathname: () => "/" }));

describe("patient shell", () => {
  it("provides landmarks, navigation, skip target, and persistent urgent help", () => {
    render(
      <PatientShell>
        <h1>Test page</h1>
      </PatientShell>,
    );

    expect(screen.getByRole("banner")).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Patient navigation" })).toBeInTheDocument();
    expect(screen.getByRole("main")).toHaveAttribute("id", "main-content");
    expect(screen.getByRole("contentinfo")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Skip to main content" })).toHaveAttribute(
      "href",
      "#main-content",
    );
    expect(screen.getByRole("link", { name: "Urgent help" })).toHaveAttribute(
      "href",
      "/urgent-help",
    );
  });

  it("keeps planned features out of active primary navigation", () => {
    render(
      <PatientShell>
        <h1>Test page</h1>
      </PatientShell>,
    );

    const navigation = screen.getByRole("navigation", { name: "Patient navigation" });
    expect(navigation).toHaveTextContent("Home");
    expect(navigation).toHaveTextContent("Start");
    expect(navigation).not.toHaveTextContent("Documents");
    expect(navigation).not.toHaveTextContent("Results");
  });
});
