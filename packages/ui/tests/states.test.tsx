import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ErrorState, LoadingState } from "../src";

describe("shared application states", () => {
  it("announces loading without requiring visual cues", () => {
    render(<LoadingState label="Loading workspace" />);

    expect(screen.getByRole("status")).toHaveAttribute("aria-busy", "true");
    expect(screen.getByText("Loading workspace")).toBeInTheDocument();
  });

  it("provides a semantic retry button", async () => {
    const onRetry = vi.fn();
    const user = userEvent.setup();
    render(<ErrorState onRetry={onRetry} />);

    await user.click(screen.getByRole("button", { name: "Try again" }));

    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(onRetry).toHaveBeenCalledOnce();
  });
});
