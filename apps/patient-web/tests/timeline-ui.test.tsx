import { render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";

import TimelinePage from "../app/timeline/page";

it("renders categorized timeline entries in the server-provided deterministic order", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      Response.json({
        state: "AUTHENTICATED",
        items: [
          {
            entryId: "1f0bb868-b00b-41c6-9335-f9c8b96ce7b1",
            entryType: "CLINICAL_FACT",
            occurredAt: "2026-11-03T12:00:00Z",
            category: "PROBLEM",
            label: "Synthetic concern",
            detail: "PATIENT CONFIRMED",
          },
          {
            entryId: "2f0bb868-b00b-41c6-9335-f9c8b96ce7b2",
            entryType: "ENCOUNTER",
            occurredAt: "2026-11-02T12:00:00Z",
            category: "Health journey",
            label: "GENERAL INTAKE",
            detail: "COMPLETED",
          },
        ],
      }),
    ),
  );
  render(<TimelinePage />);

  const entries = await screen.findAllByRole("listitem");
  expect(entries).toHaveLength(2);
  expect(entries[0]).toHaveTextContent("Synthetic concern");
  expect(entries[1]).toHaveTextContent("GENERAL INTAKE");
  expect(screen.getByRole("heading", { name: "Medical timeline" })).toBeVisible();
  vi.unstubAllGlobals();
});
