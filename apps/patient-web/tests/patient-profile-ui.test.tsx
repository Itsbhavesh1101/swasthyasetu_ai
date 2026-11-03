import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

import DashboardPage from "../app/dashboard/page";
import ProfilePage from "../app/profile/page";

const patientId = "2f0bb868-b00b-41c6-9335-f9c8b96ce7b2";

beforeEach(() => {
  vi.unstubAllGlobals();
});

it("shows the signed-in patient dashboard and core health-record actions", async () => {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValue(
        Response.json({ state: "AUTHENTICATED", displayName: "Patient Demo", patientId }),
      ),
  );
  render(<DashboardPage />);
  expect(await screen.findByText(/welcome back, patient demo/i)).toBeVisible();
  expect(screen.getByRole("link", { name: /open profile/i })).toHaveAttribute("href", "/profile");
  expect(screen.getByRole("link", { name: /open history/i })).toHaveAttribute("href", "/history");
  expect(screen.getByRole("link", { name: /open documents/i })).toBeVisible();
});

it("loads and saves the editable patient profile with an optimistic version", async () => {
  const user = userEvent.setup();
  const fetchSpy = vi
    .fn()
    .mockResolvedValueOnce(
      Response.json({
        state: "AUTHENTICATED",
        profile: {
          patientId,
          status: "ACTIVE",
          preferredLanguage: "en",
          demographics: {
            dateOfBirth: "2000-01-02",
            administrativeSex: "female",
            genderIdentity: null,
            pregnancyStatus: null,
            locationContext: "Delhi",
          },
          updatedAt: "2026-11-03T10:00:00Z",
        },
      }),
    )
    .mockResolvedValueOnce(
      Response.json({
        state: "AUTHENTICATED",
        profile: {
          patientId,
          status: "ACTIVE",
          preferredLanguage: "hi",
          demographics: null,
          updatedAt: "2026-11-03T10:01:00Z",
        },
      }),
    );
  vi.stubGlobal("fetch", fetchSpy);
  render(<ProfilePage />);
  expect(await screen.findByDisplayValue("Delhi")).toBeVisible();
  await user.selectOptions(screen.getByLabelText(/preferred language/i), "hi");
  await user.click(screen.getByRole("button", { name: /save details/i }));
  expect(await screen.findByText(/details have been saved/i)).toBeVisible();
  const submitted = JSON.parse(String(fetchSpy.mock.calls[1]?.[1]?.body)) as Record<
    string,
    unknown
  >;
  expect(submitted).toMatchObject({
    expectedUpdatedAt: "2026-11-03T10:00:00Z",
    preferredLanguage: "hi",
  });
  expect(submitted).not.toHaveProperty("patientId");
});

it("does not render profile data for an anonymous visitor", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(Response.json({ state: "ANONYMOUS" }, { status: 401 })),
  );
  render(<ProfilePage />);
  expect(await screen.findByRole("link", { name: /sign in/i })).toHaveAttribute("href", "/login");
});
