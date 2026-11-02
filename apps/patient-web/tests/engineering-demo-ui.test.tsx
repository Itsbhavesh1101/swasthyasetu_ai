import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { EngineeringResult } from "../components/demo/engineering-result";

const intakeId = "3f0bb868-b00b-41c6-9335-f9c8b96ce7b3";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("engineering result presentation", () => {
  it("labels every result as synthetic and unconfirmed", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json({
          intake_id: intakeId,
          encounter_id: "2f0bb868-b00b-41c6-9335-f9c8b96ce7b2",
          status: "SYNTHETIC_PREVIEW",
          classification: "ENGINEERING_ONLY",
          extracted_label: "SYNTHETIC_PAIN",
          verification_state: "AI_EXTRACTED_UNCONFIRMED",
          safety_decision: { route: "ROUTINE_CARE", blocks_self_care: true },
          summary_sections: [
            {
              section_id: "CHIEF_COMPLAINT",
              readiness: "UNVERIFIED",
              labels: ["SYNTHETIC_PAIN"],
              review_required: false,
            },
          ],
          notice: "Engineering test data only. This is not a diagnosis or medical assessment.",
        }),
      ),
    );

    render(<EngineeringResult intakeId={intakeId} />);

    expect(await screen.findByRole("heading", { name: "Synthetic result preview" })).toBeVisible();
    expect(screen.getByText(/not a diagnosis or medical assessment/i)).toBeVisible();
    expect(screen.getByText(/AI extracted, unconfirmed/i)).toBeVisible();
    expect(screen.getByText(/not a medical assessment/i)).toBeVisible();
    expect(screen.getByText(/clinician review required/i)).toBeVisible();
  });

  it("renders abstention without fabricating a result", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          Response.json({ status: "ABSTAINED", notice: "No clinical assessment was performed." }),
        ),
    );

    render(<EngineeringResult intakeId={intakeId} />);

    expect(await screen.findByRole("heading", { name: "No fixture matched" })).toBeVisible();
    expect(screen.getByText(/no clinical assessment was performed/i)).toBeVisible();
    await waitFor(() => expect(screen.queryByText(/routine care/i)).toBeNull());
  });
});
