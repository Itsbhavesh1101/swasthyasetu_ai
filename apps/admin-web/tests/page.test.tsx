import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import AdminFoundationPage from "../app/page";

describe("administration foundation page", () => {
  it("identifies the administration surface with accessible headings", () => {
    render(<AdminFoundationPage />);

    expect(screen.getByRole("heading", { level: 1, name: "SwasthyaSetu Admin" })).toBeVisible();
    expect(screen.getByRole("heading", { level: 2, name: "Foundation ready" })).toBeVisible();
    expect(screen.getByRole("main")).toBeInTheDocument();
  });
});
