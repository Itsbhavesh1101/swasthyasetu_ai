import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import PatientHomePage from "../app/page";

vi.mock("next/navigation", () => ({ useRouter: () => ({ push: vi.fn() }) }));

describe("patient landing page", () => {
  it("presents one focused login heading", () => {
    render(<PatientHomePage />);

    expect(screen.getByRole("heading", { level: 1, name: "Welcome back" })).toBeVisible();
    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);
  });

  it("shows one sign-in form and links to registration", () => {
    render(<PatientHomePage />);

    expect(screen.getByRole("button", { name: /sign in/i })).toBeVisible();
    expect(screen.queryByRole("button", { name: /create account/i })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: /create account/i })).toHaveAttribute(
      "href",
      "/register",
    );
  });
});
