import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ClinicianFoundationPage from "../app/page";

describe("clinician foundation page", () => {
  it("identifies the clinician surface with accessible headings", () => {
    render(<ClinicianFoundationPage />);

    expect(screen.getByRole("heading", { level: 1, name: "SwasthyaSetu Clinician" })).toBeVisible();
    expect(screen.getByRole("heading", { level: 2, name: "Foundation ready" })).toBeVisible();
    expect(screen.getByRole("main")).toBeInTheDocument();
  });
});
