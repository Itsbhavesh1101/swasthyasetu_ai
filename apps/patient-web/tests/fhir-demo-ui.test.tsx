import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { FHIRSyntheticPreview } from "../components/fhir-synthetic-preview";

describe("synthetic FHIR presentation", () => {
  it("shows mapping boundaries without payload, conformance, or exchange action", () => {
    const { container } = render(
      <FHIRSyntheticPreview
        result={{
          classification: "ENGINEERING_SYNTHETIC",
          authority: "ENGINEERING_ONLY",
          verification: "UNVERIFIED",
          fhir_version: "4.0.1",
          mapping_direction: "EXPORT",
          mapping_state: "SYNTHETIC_EXPORT_PROJECTION",
          resource_type: "Observation",
          structural_validation: "SYNTHETIC_STRUCTURAL_PASS",
          profile_validation: "SYNTHETIC_UNAVAILABLE",
          profile_issue: "PROFILE_PACKAGE_UNAVAILABLE",
          fhir_payload_present: false,
          patient_data_processed: false,
          profile_conformance_claimed: false,
          exchange_authorized: false,
          external_transport: false,
          abdm_invoked: false,
          persistence_written: false,
          notice:
            "Synthetic engineering metadata only. Structural mechanics are not profile conformance, no FHIR payload or patient data is processed, and no exchange, external transport, ABDM integration, or persistence occurs.",
        }}
      />,
    );

    expect(
      screen.getByRole("heading", { level: 1, name: "Synthetic FHIR boundary preview" }),
    ).toBeVisible();
    expect(screen.getByText(/no fhir exchange or conformance claim occurred/i)).toBeVisible();
    expect(screen.getByText(/profile validation fails closed/i)).toBeVisible();
    expect(screen.getByText(/no upload, input, export, import/i)).toBeVisible();
    expect(container.querySelector("button, form, input, textarea, select")).toBeNull();
    expect(container.querySelectorAll("a")).toHaveLength(1);
    expect(screen.getByRole("link", { name: /return home/i })).toHaveAttribute("href", "/");
  });
});
