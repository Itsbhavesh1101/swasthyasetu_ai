import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

describe("synthetic ABDM boundary presentation", () => {
  it("shows detached failures without identity, exchange, or action", async () => {
    let Component;
    try {
      const componentPath = "../components/abdm-synthetic-preview";
      Component = (await import(/* @vite-ignore */ componentPath)).ABDMSyntheticPreview;
    } catch {
      expect.fail("engineering ABDM preview component is not implemented");
    }

    const { container } = render(
      <Component
        result={{
          classification: "ENGINEERING_SYNTHETIC",
          authority: "ENGINEERING_ONLY",
          verification: "UNVERIFIED",
          mode: "SYNTHETIC_OFFLINE_MOCK",
          operation: "SYNTHETIC_OPERATION_ALPHA",
          scripted_state: "SYNTHETIC_REJECTED",
          scripted_issue: "SYNTHETIC_REJECTED",
          unknown_state: "SYNTHETIC_UNAVAILABLE",
          unknown_issue: "SYNTHETIC_UNAVAILABLE",
          zero_egress: true,
          official_protocol_adopted: false,
          abha_identity_processed: false,
          consent_evaluated: false,
          fhir_payload_present: false,
          sandbox_connected: false,
          patient_data_processed: false,
          local_intake_accessed: false,
          local_intake_mutated: false,
          external_transport: false,
          persistence_written: false,
          notice:
            "Synthetic offline engineering tokens only. No official ABDM protocol or ABHA identity is used, no consent or FHIR payload is processed, and no sandbox, patient data, local intake, network transport, or persistence is accessed.",
        }}
      />,
    );

    expect(
      screen.getByRole("heading", { level: 1, name: "Synthetic ABDM failure boundary" }),
    ).toBeVisible();
    expect(screen.getByText(/no abha identity or abdm exchange occurred/i)).toBeVisible();
    expect(screen.getByText(/unknown requests fail closed as unavailable/i)).toBeVisible();
    expect(screen.getByText(/local intake path is not accessed or mutated/i)).toBeVisible();
    expect(container.querySelector("button, form, input, textarea, select")).toBeNull();
    expect(container.querySelectorAll("a")).toHaveLength(1);
    expect(screen.getByRole("link", { name: /return home/i })).toHaveAttribute("href", "/");
  });
});
