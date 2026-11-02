import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SelfCareSyntheticPreview } from "../components/self-care-synthetic-preview";

describe("synthetic self-care presentation", () => {
  it("shows safety-first mechanics without guidance or action", () => {
    const { container } = render(
      <SelfCareSyntheticPreview
        result={{
          classification: "ENGINEERING_SYNTHETIC",
          authority: "ENGINEERING_ONLY",
          verification: "UNVERIFIED",
          knowledge_pack_state: "TEST_ONLY_UNAPPROVED",
          knowledge_item_review_state: "TEST_ONLY_UNAPPROVED",
          source_verification: "UNVERIFIED",
          placeholder_token: "SYNTHETIC_PLACEHOLDER_ALPHA",
          candidate_outcome: "SYNTHETIC_ENGINEERING_CANDIDATE",
          candidate_reason: "SYNTHETIC_RULE_MATCH",
          candidate_count: 1,
          blocked_outcome: "SYNTHETIC_BLOCKED",
          blocked_reason: "SYNTHETIC_SAFETY_BLOCK",
          blocked_candidate_count: 0,
          safety_block_preserved: true,
          clinical_eligibility_established: false,
          guidance_text_available: false,
          guidance_display_authorized: false,
          rag_invoked: false,
          patient_data_processed: false,
          external_delivery: false,
          notice:
            "Synthetic engineering placeholders only. No clinical eligibility is established, no guidance text is available or authorized for display, and no RAG, patient-data processing, or external delivery occurs.",
        }}
      />,
    );

    expect(
      screen.getByRole("heading", { level: 1, name: "Synthetic self-care safety preview" }),
    ).toBeVisible();
    expect(screen.getByText(/no self-care guidance is displayed/i)).toBeVisible();
    expect(screen.getByText(/upstream synthetic safety override removes/i)).toBeVisible();
    expect(screen.getByText(/no input, advice, retrieval, recommendation/i)).toBeVisible();
    expect(container.querySelector("button, form, input, textarea, select")).toBeNull();
    expect(container.querySelectorAll("a")).toHaveLength(1);
    expect(screen.getByRole("link", { name: /return home/i })).toHaveAttribute("href", "/");
  });
});
