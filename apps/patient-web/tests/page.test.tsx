import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import PatientHomePage from "../app/page";

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }) }));

describe("patient landing page", () => {
  it("presents one clear heading and honest product language", () => {
    render(<PatientHomePage />);

    expect(
      screen.getByRole("heading", { level: 1, name: "Your health history, kept together" }),
    ).toBeVisible();
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
    expect(screen.getByText(/does not provide a diagnosis/i)).toBeVisible();
  });

  it("puts sign-in and registration forms first and keeps urgent help visible", () => {
    render(<PatientHomePage />);

    expect(screen.getByRole("button", { name: /create account/i })).toBeVisible();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeVisible();
    expect(screen.getByRole("link", { name: /urgent help/i })).toHaveAttribute(
      "href",
      "/urgent-help",
    );
  });
});
