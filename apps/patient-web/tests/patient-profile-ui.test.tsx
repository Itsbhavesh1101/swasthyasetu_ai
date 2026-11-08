import { fireEvent, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

import DashboardPage from "../app/dashboard/page";
import ProfilePage from "../app/profile/page";

const patientId = "2f0bb868-b00b-41c6-9335-f9c8b96ce7b2";
const push = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));

beforeEach(() => {
  vi.unstubAllGlobals();
  push.mockReset();
});

it("shows the signed-in patient dashboard and core health-record actions", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      Response.json({
        state: "AUTHENTICATED",
        displayName: "Patient Demo",
        patientId,
        profileComplete: true,
      }),
    ),
  );
  render(<DashboardPage />);
  expect(await screen.findByText(/welcome back, patient demo/i)).toBeVisible();
  expect(screen.getByRole("link", { name: /open profile/i })).toHaveAttribute("href", "/profile");
  expect(screen.getByRole("link", { name: /open history/i })).toHaveAttribute("href", "/history");
  expect(screen.getByRole("link", { name: /open documents/i })).toBeVisible();
  const setup = screen.getByRole("region", { name: /complete your health record/i });
  expect(within(setup).getByRole("link", { name: /review personal details/i })).toHaveAttribute(
    "href",
    "/profile",
  );
  for (const label of ["Add conditions", "Add medicines", "Add allergies", "Add procedures"]) {
    expect(within(setup).getByRole("link", { name: label })).toHaveAttribute("href", "/history");
  }
  expect(within(setup).getByRole("link", { name: /add documents/i })).toHaveAttribute(
    "href",
    "/documents",
  );
  expect(within(setup).getByRole("link", { name: /start guided intake/i })).toHaveAttribute(
    "href",
    "/encounter",
  );
  expect(setup).toHaveTextContent(/optional/i);
  expect(setup).not.toHaveTextContent(/✓|completed|\d+%/i);
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
          displayName: "Patient Demo",
          profileComplete: true,
          demographics: {
            dateOfBirth: "2000-01-02",
            administrativeSex: "female",
            genderIdentity: null,
            pregnancyStatus: null,
            locationContext: "Delhi",
            heightCm: 165,
            weightKg: 60,
            bmi: 22,
            mobileNumber: "+919876543210",
            bloodGroup: "B+",
            demoAadhaarReference: "DEMO-AADHAAR-2301",
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
          displayName: "Patient Demo",
          profileComplete: true,
          demographics: null,
          updatedAt: "2026-11-03T10:01:00Z",
        },
      }),
    );
  vi.stubGlobal("fetch", fetchSpy);
  render(<ProfilePage />);
  expect(await screen.findByDisplayValue("Delhi")).toBeVisible();
  await user.selectOptions(screen.getByLabelText(/preferred language/i), "hi");
  expect(screen.getByLabelText(/bmi \(calculated\)/i)).toHaveTextContent("22.0");
  expect(screen.getByLabelText(/mobile number/i)).toHaveValue("+919876543210");
  expect(screen.getByLabelText(/blood group/i)).toHaveValue("B+");
  expect(screen.getByLabelText(/aadhaar demonstration reference/i)).toHaveValue(
    "DEMO-AADHAAR-2301",
  );
  await user.click(screen.getByRole("button", { name: /save details/i }));
  expect(await screen.findByText(/profile is ready/i)).toBeVisible();
  expect(push).toHaveBeenCalledWith("/dashboard");
  const submitted = JSON.parse(String(fetchSpy.mock.calls[1]?.[1]?.body)) as Record<
    string,
    unknown
  >;
  expect(submitted).toMatchObject({
    expectedUpdatedAt: "2026-11-03T10:00:00Z",
    preferredLanguage: "hi",
    demographics: {
      mobileNumber: "+919876543210",
      bloodGroup: "B+",
      demoAadhaarReference: "DEMO-AADHAAR-2301",
    },
  });
  expect(submitted).not.toHaveProperty("patientId");
});

it("collects first-login details one tile at a time and submits only after review", async () => {
  const user = userEvent.setup();
  const initialProfile = {
    patientId,
    status: "ACTIVE",
    preferredLanguage: null,
    displayName: null,
    profileComplete: false,
    demographics: null,
    updatedAt: "2026-11-03T10:00:00Z",
  };
  const fetchSpy = vi
    .fn()
    .mockResolvedValueOnce(Response.json({ state: "AUTHENTICATED", profile: initialProfile }))
    .mockResolvedValueOnce(
      Response.json({
        state: "AUTHENTICATED",
        profile: { ...initialProfile, displayName: "Asha Demo", profileComplete: true },
      }),
    );
  vi.stubGlobal("fetch", fetchSpy);
  render(<ProfilePage />);

  expect(await screen.findByText("Step 1 of 13")).toBeVisible();
  expect(screen.getByRole("heading", { name: /what should we call you/i })).toBeVisible();
  expect(screen.queryByLabelText(/mobile number/i)).not.toBeInTheDocument();
  await user.type(screen.getByLabelText(/full name/i), "Asha Demo");
  await user.click(screen.getByRole("button", { name: /next/i }));

  await user.selectOptions(screen.getByLabelText(/preferred language/i), "en");
  await user.click(screen.getByRole("button", { name: /next/i }));
  fireEvent.change(screen.getByLabelText(/date of birth/i), { target: { value: "2000-01-02" } });
  expect(screen.getByText(/years old/i)).toBeVisible();
  await user.click(screen.getByRole("button", { name: /next/i }));
  await user.selectOptions(screen.getByLabelText(/sex recorded for healthcare/i), "female");
  await user.click(screen.getByRole("button", { name: /next/i }));
  await user.type(screen.getByLabelText(/height/i), "165");
  await user.click(screen.getByRole("button", { name: /next/i }));
  await user.type(screen.getByLabelText(/weight/i), "60");
  expect(screen.getByText(/bmi.*22\.0/i)).toBeVisible();
  await user.click(screen.getByRole("button", { name: /next/i }));

  await user.type(screen.getByLabelText(/mobile number/i), "+919876543210");
  await user.click(screen.getByRole("button", { name: /next/i }));
  await user.selectOptions(screen.getByLabelText(/blood group/i), "B+");
  await user.click(screen.getByRole("button", { name: /next/i }));
  await user.type(screen.getByLabelText(/aadhaar demonstration reference/i), "123456789012");
  await user.click(screen.getByRole("button", { name: /next/i }));
  expect(screen.getByRole("alert")).toHaveTextContent(/do not enter a real aadhaar/i);
  await user.clear(screen.getByLabelText(/aadhaar demonstration reference/i));
  await user.type(screen.getByLabelText(/aadhaar demonstration reference/i), "DEMO-AADHAAR-2301");
  await user.click(screen.getByRole("button", { name: /next/i }));

  await user.click(screen.getByRole("button", { name: /skip/i }));
  await user.click(screen.getByRole("button", { name: /skip/i }));
  await user.click(screen.getByRole("button", { name: /back/i }));
  expect(screen.getByRole("heading", { name: /pregnancy status/i })).toBeVisible();
  await user.click(screen.getByRole("button", { name: /skip/i }));
  await user.click(screen.getByRole("button", { name: /skip/i }));

  expect(screen.getByText("Step 13 of 13")).toBeVisible();
  const reviewHeading = screen.getByRole("heading", { name: /review your details/i });
  expect(reviewHeading).toBeVisible();
  const review = reviewHeading.closest("form");
  expect(review).not.toBeNull();
  expect(review).toHaveTextContent("Asha Demo");
  expect(review).toHaveTextContent("English");
  expect(review).toHaveTextContent("2 January 2000");
  expect(review).toHaveTextContent("Female");
  expect(review).toHaveTextContent("165 cm");
  expect(review).toHaveTextContent("60 kg");
  expect(review).toHaveTextContent("+919876543210");
  expect(review).toHaveTextContent("B+");
  expect(review).toHaveTextContent("DEMO-AADHAAR-2301");
  expect(review).toHaveTextContent("Gender identityNot provided");
  expect(review).toHaveTextContent("Pregnancy statusNot provided");
  expect(review).toHaveTextContent("LocationNot provided");
  expect(fetchSpy).toHaveBeenCalledTimes(1);
  expect(localStorage).toHaveLength(0);
  expect(sessionStorage).toHaveLength(0);
  await user.click(screen.getByRole("button", { name: /save and open dashboard/i }));

  expect(await screen.findByText(/profile is ready/i)).toBeVisible();
  expect(fetchSpy).toHaveBeenCalledTimes(2);
  expect(push).toHaveBeenCalledWith("/dashboard");
  const submitted = JSON.parse(String(fetchSpy.mock.calls[1]?.[1]?.body));
  expect(submitted).toMatchObject({
    displayName: "Asha Demo",
    preferredLanguage: "en",
    demographics: {
      mobileNumber: "+919876543210",
      bloodGroup: "B+",
      demoAadhaarReference: "DEMO-AADHAAR-2301",
    },
  });
});

it("keeps the first-login wizard on review when the profile changed elsewhere", async () => {
  const user = userEvent.setup();
  const profile = {
    patientId,
    status: "ACTIVE",
    preferredLanguage: "en",
    displayName: "Asha Demo",
    profileComplete: false,
    demographics: {
      dateOfBirth: "2000-01-02",
      administrativeSex: "female",
      genderIdentity: null,
      pregnancyStatus: null,
      locationContext: null,
      heightCm: 165,
      weightKg: 60,
      bmi: 22,
      mobileNumber: "+919876543210",
      bloodGroup: "B+",
      demoAadhaarReference: "DEMO-AADHAAR-2301",
    },
    updatedAt: "2026-11-03T10:00:00Z",
  };
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValueOnce(Response.json({ state: "AUTHENTICATED", profile }))
      .mockResolvedValueOnce(
        Response.json({ error: { code: "PATIENT_PROFILE_FAILED" } }, { status: 409 }),
      ),
  );
  render(<ProfilePage />);
  await screen.findByText("Step 1 of 13");
  for (let step = 1; step < 13; step += 1) {
    const next = screen.queryByRole("button", { name: "Next" });
    await user.click(next ?? screen.getByRole("button", { name: "Skip" }));
  }
  await user.click(screen.getByRole("button", { name: /save and open dashboard/i }));
  expect(await screen.findByText(/changed elsewhere/i)).toBeVisible();
  expect(screen.getByRole("heading", { name: /review your details/i })).toBeVisible();
  expect(push).not.toHaveBeenCalled();
});

it("does not render profile data for an anonymous visitor", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(Response.json({ state: "ANONYMOUS" }, { status: 401 })),
  );
  render(<ProfilePage />);
  expect(await screen.findByRole("link", { name: /sign in/i })).toHaveAttribute("href", "/login");
});
