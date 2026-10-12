import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import ErrorPage from "../app/error";
import DocumentsPage from "../app/documents/page";
import LoadingPage from "../app/loading";
import OfflinePage from "../app/offline/page";
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
    render(<DocumentsPage />);

    expect(screen.getByText("Not available yet")).toBeVisible();
    expect(screen.getByText(/document upload and review are not enabled/i)).toBeVisible();
    expect(screen.getByRole("button", { name: "Continue unavailable" })).toBeDisabled();
  });

  it("announces loading state", () => {
    render(<LoadingPage />);

    expect(screen.getByRole("status")).toHaveAttribute("aria-busy", "true");
    expect(screen.getByText("Loading patient page")).toBeVisible();
  });

  it("renders an honest generic offline fallback with accessible recovery actions", () => {
    render(<OfflinePage />);

    expect(
      screen.getByRole("heading", { level: 1, name: "You appear to be offline" }),
    ).toBeVisible();
    expect(screen.getByText(/session and consent status cannot be confirmed/i)).toBeVisible();
    expect(screen.getByText(/clinical workflows are unavailable offline/i)).toBeVisible();
    expect(screen.getByRole("button", { name: "Try again" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Return home" })).toHaveAttribute("href", "/");
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
