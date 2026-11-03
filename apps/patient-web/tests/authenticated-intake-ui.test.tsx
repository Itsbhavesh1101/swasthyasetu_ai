import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";

import EncounterPage from "../app/encounter/page";

const push = vi.fn();
const intakeRequest = vi.hoisted(() => vi.fn());
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
vi.mock("../lib/intake/client", () => ({ intakeRequest }));

afterEach(() => {
  vi.unstubAllGlobals();
  push.mockReset();
});

it("requires explicit intake consent then starts the account-bound resumable intake", async () => {
  const user = userEvent.setup();
  const fetchSpy = vi
    .fn()
    .mockResolvedValueOnce(Response.json({ state: "AUTHENTICATED", displayName: "Patient" }))
    .mockResolvedValueOnce(Response.json({ state: "NOT_GRANTED" }))
    .mockResolvedValueOnce(Response.json({ state: "GRANTED" }, { status: 201 }));
  intakeRequest.mockResolvedValue({
    ok: true,
    value: { intake_id: "2f0bb868-b00b-41c6-9335-f9c8b96ce7b2" },
  });
  vi.stubGlobal("fetch", fetchSpy);
  render(<EncounterPage />);

  expect(await screen.findByText(/allow this private account session/i)).toBeVisible();
  await user.click(screen.getByRole("button", { name: "Allow structured intake" }));
  await user.click(await screen.findByRole("button", { name: "Start or resume intake" }));
  expect(push).toHaveBeenCalledWith("/intake/2f0bb868-b00b-41c6-9335-f9c8b96ce7b2");
  expect(fetchSpy).toHaveBeenCalledTimes(3);
  expect(intakeRequest).toHaveBeenCalledWith("/api/intake/start", { method: "POST" });
});
