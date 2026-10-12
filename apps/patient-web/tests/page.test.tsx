import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import PatientHomePage from "../app/page";

describe("patient landing page", () => {
  it("presents one clear heading and honest product language", () => {
    render(<PatientHomePage />);

    expect(
      screen.getByRole("heading", { level: 1, name: "Your health journey, one step at a time" }),
    ).toBeVisible();
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByText(/does not provide a diagnosis/i)).toBeVisible();
  });

  it("links to start and urgent-help routes", () => {
    render(<PatientHomePage />);

    expect(screen.getByRole("link", { name: /get started/i })).toHaveAttribute("href", "/start");
    expect(screen.getByRole("link", { name: /urgent help/i })).toHaveAttribute(
      "href",
      "/urgent-help",
    );
  });
});
