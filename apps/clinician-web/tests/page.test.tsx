import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import ClinicianFoundationPage from "../app/page";

describe("clinician foundation page", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("identifies the clinician engineering surface with accessible headings", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(null, { status: 404 })));
    render(await ClinicianFoundationPage());

    expect(screen.getByRole("heading", { level: 1, name: "SwasthyaSetu Clinician" })).toBeVisible();
    expect(
      screen.getByRole("heading", { level: 2, name: "Clinician engineering workspace" }),
    ).toBeVisible();
    expect(screen.getByRole("main")).toBeInTheDocument();
  });
});
