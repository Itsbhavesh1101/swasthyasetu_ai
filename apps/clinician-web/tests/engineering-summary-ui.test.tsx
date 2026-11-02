import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EngineeringSummaryReview } from "../components/engineering-summary-review";

const sections = [
  "CHIEF_COMPLAINT",
  "HPI",
  "PAST_MEDICAL_HISTORY",
  "PAST_SURGICAL_HISTORY",
  "MEDICATIONS",
  "ALLERGIES",
  "FAMILY_HISTORY",
  "PERSONAL_HISTORY",
  "REVIEW_OF_SYSTEMS",
  "PRIOR_INVESTIGATIONS",
] as const;

describe("synthetic summary review presentation", () => {
  it("shows draft, provenance, missing-data, and drift states without controls", () => {
    render(
      <EngineeringSummaryReview
        result={{
          status: "DRAFT",
          classification: "ENGINEERING_ONLY",
          review_state: "REVIEW_REQUIRED",
          freshness: "STALE",
          affected_sections: ["HPI"],
          drift_reasons: ["NEW_SOURCE"],
          source_count: 1,
          sections: sections.map((section, index) => ({
            section,
            readiness: index === 0 ? "UNVERIFIED" : "UNKNOWN",
            assertions: index === 0 ? ["SYNTHETIC_REPORTED_COMPLAINT"] : [],
            source_kinds: index === 0 ? ["P7_PATIENT_REPORTED"] : [],
            conflict_review_required: false,
          })),
          source_access: "NOT_AUTHORIZED",
          can_edit: false,
          can_confirm: false,
          can_reject: false,
          external_egress: false,
          notice:
            "Synthetic engineering draft only. Missing sections are unknown, source drift requires review, and no clinical action is authorized.",
        }}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Synthetic source-backed summary draft" }),
    ).toBeVisible();
    expect(screen.getByText(/not signed clinical documentation/i)).toBeVisible();
    expect(screen.getByText("STALE", { exact: true })).toBeVisible();
    expect(screen.getByText("NOT AUTHORIZED", { exact: true })).toBeVisible();
    expect(screen.getAllByText(/absence is not a clinical finding/i)).toHaveLength(9);
    expect(screen.getByText(/controls remain unavailable/i)).toBeVisible();
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("fails closed when the engineering endpoint is unavailable", () => {
    render(<EngineeringSummaryReview result={null} />);

    expect(screen.getByRole("heading", { name: "Summary preview unavailable" })).toBeVisible();
    expect(screen.getByText(/no source-backed summary or clinician action/i)).toBeVisible();
  });
});
