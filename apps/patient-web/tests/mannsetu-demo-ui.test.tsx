import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MannSetuSyntheticPreview } from "../components/mannsetu-synthetic-preview";

describe("synthetic MannSetu presentation", () => {
  it("shows symbolic precedence with no assessment or clinical action", () => {
    const { container } = render(
      <MannSetuSyntheticPreview
        result={{
          classification: "ENGINEERING_SYNTHETIC",
          authority: "ENGINEERING_ONLY",
          verification: "UNVERIFIED",
          extraction_status: "SYNTHETIC_PARSED",
          extractor_signal: "SYN_MH_SIGNAL_ALPHA",
          backstop_outcome: "SYNTHETIC_MATCHED",
          backstop_signal: "SYN_MH_SIGNAL_DELTA",
          precedence: "SYNTHETIC_OVERRIDE",
          route: "SYNTHETIC_ROUTE_GAMMA",
          reason_code: "SYN_MH_POLICY_REASON_DELTA",
          policy_state: "TEST_ONLY_ENABLED",
          clinical_meaning_assigned: false,
          mental_health_assessment_performed: false,
          patient_data_processed: false,
          resource_contacts_available: false,
          referral_created: false,
          external_delivery: false,
          notice:
            "Synthetic engineering symbols only. No mental-health assessment is performed, no clinical meaning is assigned, and no resource, referral, or external delivery is available.",
        }}
      />,
    );

    expect(
      screen.getByRole("heading", { level: 1, name: "MannSetu synthetic policy preview" }),
    ).toBeVisible();
    expect(screen.getByText(/no mental-health assessment was performed/i)).toBeVisible();
    expect(screen.getByText(/toy override wins mechanically/i)).toBeVisible();
    expect(screen.getByText(/no assessment, messaging, resource, referral/i)).toBeVisible();
    expect(container.querySelector("button, form, input, textarea, select")).toBeNull();
    expect(container.querySelectorAll("a")).toHaveLength(1);
    expect(screen.getByRole("link", { name: /return home/i })).toHaveAttribute("href", "/");
  });
});
