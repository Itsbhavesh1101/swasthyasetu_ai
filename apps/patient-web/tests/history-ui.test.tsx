import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

import HistoryPage from "../app/history/page";

const factId = "3f0bb868-b00b-41c6-9335-f9c8b96ce7b3";

beforeEach(() => vi.unstubAllGlobals());

it("shows every supported history category and an actionable empty state", async () => {
  const user = userEvent.setup();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(Response.json({ state: "AUTHENTICATED", items: [] })),
  );
  render(<HistoryPage />);
  expect(await screen.findByText(/no history entries yet/i)).toBeVisible();
  const category = screen.getByLabelText(/category/i);
  for (const [value, field] of [
    ["PROBLEM", /condition name/i],
    ["MEDICATION", /medicine name/i],
    ["ALLERGY", /allergy name/i],
    ["PROCEDURE", /procedure name/i],
    ["OBSERVATION", /observation name/i],
    ["INVESTIGATION", /investigation or test name/i],
  ] as const) {
    await user.selectOptions(category, value);
    expect(screen.getByLabelText(field)).toBeVisible();
  }
});

it("submits a patient entry and reloads the authoritative list", async () => {
  const user = userEvent.setup();
  const fetchSpy = vi
    .fn()
    .mockResolvedValueOnce(Response.json({ state: "AUTHENTICATED", items: [] }))
    .mockResolvedValueOnce(Response.json({ state: "AUTHENTICATED", item: {} }, { status: 201 }))
    .mockResolvedValueOnce(Response.json({ state: "AUTHENTICATED", items: [] }));
  vi.stubGlobal("fetch", fetchSpy);
  render(<HistoryPage />);
  await screen.findByText(/no history entries yet/i);
  await user.type(screen.getByLabelText(/condition name/i), "Synthetic migraine");
  await user.click(screen.getByRole("button", { name: /add entry/i }));
  expect(await screen.findByText(/entry has been added/i)).toBeVisible();
  expect(JSON.parse(String(fetchSpy.mock.calls[1]?.[1]?.body))).toEqual({
    fact_type: "PROBLEM",
    label: "Synthetic migraine",
    status: "ACTIVE",
  });
});

it("starts a correction for the current entry and never offers correction on old versions", async () => {
  const user = userEvent.setup();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      Response.json({
        state: "AUTHENTICATED",
        items: [
          {
            factId,
            factType: "PROBLEM",
            label: "Synthetic current",
            status: "ACTIVE",
            effectiveTime: null,
            recordedAt: "2026-11-03T13:00:00Z",
            verificationState: "PATIENT_CONFIRMED",
            supersededByFactId: null,
          },
          {
            factId: "4f0bb868-b00b-41c6-9335-f9c8b96ce7b4",
            factType: "PROBLEM",
            label: "Synthetic previous",
            status: "ACTIVE",
            effectiveTime: null,
            recordedAt: "2026-11-02T13:00:00Z",
            verificationState: "SUPERSEDED",
            supersededByFactId: factId,
          },
        ],
      }),
    ),
  );
  render(<HistoryPage />);
  expect(await screen.findByText("Synthetic current")).toBeVisible();
  expect(screen.getAllByRole("button", { name: /correct entry/i })).toHaveLength(1);
  await user.selectOptions(screen.getByLabelText(/category/i), "INVESTIGATION");
  expect(screen.getByLabelText(/investigation or test name/i)).toBeVisible();
  await user.click(screen.getByRole("button", { name: /correct entry/i }));
  expect(screen.getByRole("heading", { name: /replace “synthetic current”/i })).toBeVisible();
  expect(screen.getByLabelText(/condition name/i)).toHaveValue("Synthetic current");
  expect(screen.getByRole("button", { name: /save correction/i })).toBeVisible();
});

it("filters entries by category tabs and search input", async () => {
  const user = userEvent.setup();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      Response.json({
        state: "AUTHENTICATED",
        items: [
          {
            factId: "11111111-1111-4111-8111-111111111111",
            factType: "PROBLEM",
            label: "Asthma condition",
            status: "ACTIVE",
            effectiveTime: null,
            recordedAt: "2026-11-03T13:00:00Z",
            verificationState: "PATIENT_CONFIRMED",
            supersededByFactId: null,
          },
          {
            factId: "22222222-2222-4222-8222-222222222222",
            factType: "MEDICATION",
            label: "Albuterol inhaler",
            status: "ACTIVE",
            effectiveTime: null,
            recordedAt: "2026-11-03T13:00:00Z",
            verificationState: "PATIENT_CONFIRMED",
            supersededByFactId: null,
          },
          {
            factId: "33333333-3333-4333-8333-333333333333",
            factType: "ALLERGY",
            label: "Dust mite allergy",
            status: "ACTIVE",
            effectiveTime: null,
            recordedAt: "2026-11-03T13:00:00Z",
            verificationState: "PATIENT_CONFIRMED",
            supersededByFactId: null,
          },
        ],
      }),
    ),
  );
  render(<HistoryPage />);

  expect(await screen.findByText("Asthma condition")).toBeVisible();
  expect(screen.getByText("Albuterol inhaler")).toBeVisible();
  expect(screen.getByText("Dust mite allergy")).toBeVisible();

  // Click Medicines category tab
  const tabs = screen.getByRole("toolbar", { name: /filter entries by type/i });
  await user.click(within(tabs).getByRole("button", { name: /medicines/i }));
  expect(screen.getByText("Albuterol inhaler")).toBeVisible();
  expect(screen.queryByText("Asthma condition")).toBeNull();
  expect(screen.queryByText("Dust mite allergy")).toBeNull();

  // Switch back to All
  await user.click(within(tabs).getByRole("button", { name: /^all /i }));
  expect(screen.getByText("Asthma condition")).toBeVisible();

  // Search filter
  await user.type(screen.getByLabelText(/search entries/i), "dust");
  expect(screen.getByText("Dust mite allergy")).toBeVisible();
  expect(screen.queryByText("Asthma condition")).toBeNull();
  expect(screen.queryByText("Albuterol inhaler")).toBeNull();
});

it("navigates quick-add category actions", async () => {
  const user = userEvent.setup();
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      Response.json({
        state: "AUTHENTICATED",
        items: [
          {
            factId: "11111111-1111-4111-8111-111111111111",
            factType: "PROBLEM",
            label: "Existing problem",
            status: "ACTIVE",
            effectiveTime: null,
            recordedAt: "2026-11-03T13:00:00Z",
            verificationState: "PATIENT_CONFIRMED",
            supersededByFactId: null,
          },
        ],
      }),
    ),
  );
  render(<HistoryPage />);
  expect(await screen.findByText("Existing problem")).toBeVisible();

  await user.click(screen.getByRole("button", { name: "+ Medicine" }));
  expect(screen.getByLabelText(/medicine name/i)).toBeVisible();

  await user.click(screen.getByRole("button", { name: "+ Allergy" }));
  expect(screen.getByLabelText(/allergy name/i)).toBeVisible();
});
