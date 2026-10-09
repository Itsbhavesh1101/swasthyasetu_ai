import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import PatientFoundationPage from "../app/page";

describe("patient foundation page", () => {
  it("identifies the patient surface with accessible headings", () => {
    render(<PatientFoundationPage />);

    expect(screen.getByRole("heading", { level: 1, name: "SwasthyaSetu Patient" })).toBeVisible();
    expect(screen.getByRole("heading", { level: 2, name: "Foundation ready" })).toBeVisible();
    expect(screen.getByRole("main")).toBeInTheDocument();
  });
});
