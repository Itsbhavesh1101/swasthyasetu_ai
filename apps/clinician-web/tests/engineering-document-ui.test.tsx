import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EngineeringDocumentReview } from "../components/engineering-document-review";

describe("synthetic document review presentation", () => {
  it("shows explicit engineering, unconfirmed, and inaccessible-source states", () => {
    render(
      <EngineeringDocumentReview
        result={{
          status: "NEEDS_REVIEW",
          classification: "ENGINEERING_ONLY",
          ingestion_disposition: "SYNTHETIC_COMPATIBLE",
          lifecycle: ["UPLOADED", "VALIDATING", "ACCEPTED", "QUEUED", "PROCESSING", "NEEDS_REVIEW"],
          processing_status: "SUCCEEDED",
          processed_pages: 1,
          provider: "engineering.fixture",
          external_egress: false,
          document_type: "LAB_REPORT",
          classification_disposition: "SELECTED",
          classification_reason: "EXACT_SYNTHETIC_LABEL",
          processor_id: "LabReportProcessor",
          processor_version: "v1",
          processor_disposition: "NOOP_ABSTAIN",
          candidate_disposition: "UNCONFIRMED",
          evidence_references: 1,
          structural_match: "STRUCTURALLY_MATCHED_UNCONFIRMED",
          source_access: "NOT_VERIFIED",
          confidence: "UNKNOWN",
          notice:
            "Synthetic engineering metadata only. No file was uploaded, no medical value was extracted, and no clinical decision was made.",
        }}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Synthetic document review receipt" }),
    ).toBeVisible();
    expect(screen.getByText(/not patient data/i)).toBeVisible();
    expect(screen.getByText("UNCONFIRMED", { exact: true })).toBeVisible();
    expect(screen.getByText("NOT VERIFIED", { exact: true })).toBeVisible();
    expect(screen.getByText(/review controls remain disabled/i)).toBeVisible();
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("fails closed when the engineering endpoint is unavailable", () => {
    render(<EngineeringDocumentReview result={null} />);

    expect(screen.getByRole("heading", { name: "Engineering preview unavailable" })).toBeVisible();
    expect(screen.getByText(/no clinician workflow or document source access/i)).toBeVisible();
  });
});
