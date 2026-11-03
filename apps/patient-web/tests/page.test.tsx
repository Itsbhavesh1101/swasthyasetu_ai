import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import PatientHomePage from "../app/page";

describe("patient landing page", () => {
  it("presents one clear heading and honest product language", () => {
    render(<PatientHomePage />);

    expect(
      screen.getByRole("heading", { level: 1, name: "Your health history, kept together" }),
    ).toBeVisible();
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByText(/does not provide a diagnosis/i)).toBeVisible();
  });

  it("links to account and urgent-help routes", () => {
    render(<PatientHomePage />);

    expect(screen.getByRole("link", { name: /create account/i })).toHaveAttribute(
      "href",
      "/register",
    );
    expect(screen.getByRole("link", { name: /sign in/i })).toHaveAttribute("href", "/login");
    expect(screen.getByRole("link", { name: /urgent help/i })).toHaveAttribute(
      "href",
      "/urgent-help",
    );
  });
});
