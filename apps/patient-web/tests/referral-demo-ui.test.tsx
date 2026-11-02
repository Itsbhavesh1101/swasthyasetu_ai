import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ReferralDiscoveryPreview } from "../components/referral-discovery-preview";

describe("synthetic referral discovery presentation", () => {
  it("shows unverified detached fixtures with no referral action", () => {
    const { container } = render(
      <ReferralDiscoveryPreview
        result={{
          classification: "ENGINEERING_SYNTHETIC",
          authority: "ENGINEERING_ONLY",
          route_disposition: "SYMBOLIC_MATCH",
          route_reason: "EXACT_SYMBOLIC_MATCH",
          service_code: "syn_service_college_demo",
          provider_display_name: "Synthetic College Demo Provider",
          provider_service_code: "syn_service_college_demo",
          provider_verification: "UNVERIFIED",
          resource_display_name: "Synthetic College Demo Resource",
          resource_code: "syn_resource_type_college_demo",
          resource_verification: "UNVERIFIED",
          source_verification: "UNVERIFIED",
          contacts_available: false,
          provider_selected: false,
          referral_state_model: "OFFERED",
          referral_created: false,
          sharing_consent: "NOT_REQUESTED",
          external_delivery: false,
          notification_delivery: false,
          notice:
            "Synthetic engineering preview only. Directory records are unverified, no provider is selected, no referral is created, and no data is shared or delivered.",
        }}
      />,
    );

    expect(
      screen.getByRole("heading", { level: 1, name: "Synthetic referral discovery" }),
    ).toBeVisible();
    expect(screen.getByText(/no referral or sharing occurred/i)).toBeVisible();
    expect(screen.getAllByText(/unverified/i).length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText(/no provider-selection.*controls are enabled/i)).toBeVisible();
    expect(container.querySelector("button, form, input")).toBeNull();
    expect(container.querySelectorAll("a")).toHaveLength(1);
    expect(screen.getByRole("link", { name: /return home/i })).toHaveAttribute("href", "/");
  });
});
