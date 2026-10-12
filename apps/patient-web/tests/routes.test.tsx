import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import ErrorPage from "../app/error";
import LanguagePage from "../app/language/page";
import LoadingPage from "../app/loading";
import UrgentHelpPage from "../app/urgent-help/page";

describe("patient route states", () => {
  it("uses safe urgent-help wording without invented contact data", () => {
    const { container } = render(<UrgentHelpPage />);

    expect(
      screen.getByRole("heading", { level: 1, name: "Get help now if you feel unsafe" }),
    ).toBeVisible();
    expect(screen.getByText(/verified resources are not configured/i)).toBeVisible();
    expect(screen.getByText(/will not guess/i)).toBeVisible();
    expect(container).not.toHaveTextContent(/\+?\d[\d\s()-]{6,}/);
  });

  it("renders future routes as unavailable with a natively disabled control", () => {
    render(<LanguagePage />);

    expect(screen.getByText("Not available yet")).toBeVisible();
    expect(screen.getByText(/no preference is stored/i)).toBeVisible();
    expect(screen.getByRole("button", { name: "Continue unavailable" })).toBeDisabled();
  });

  it("announces loading state", () => {
    render(<LoadingPage />);

    expect(screen.getByRole("status")).toHaveAttribute("aria-busy", "true");
    expect(screen.getByText("Loading patient page")).toBeVisible();
  });

  it("keeps errors content-free and provides a meaningful retry", async () => {
    const reset = vi.fn();
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => undefined);
    const user = userEvent.setup();
    render(<ErrorPage error={new Error("sensitive raw detail")} reset={reset} />);

    expect(screen.queryByText("sensitive raw detail")).not.toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Try this page again" }));
    expect(reset).toHaveBeenCalledOnce();
    expect(consoleError).toHaveBeenCalledWith("Patient page failed to render.");
    consoleError.mockRestore();
  });
});
