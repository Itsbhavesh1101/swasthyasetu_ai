import { render, screen } from "@testing-library/react";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

import { projectSyntheticMentalHealthPresentation } from "../lib/mental-health/presentation";
import { SyntheticMentalHealthPreview } from "./support/synthetic-mental-health-preview";

const NOW = new Date("2026-10-31T18:00:30.000Z");
const HASH = "a".repeat(64);
function decision(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    decision_id: "syn_mh_policy_decision_alpha",
    evaluation_id: "syn_mh_policy_evaluation_alpha",
    evaluation_fingerprint: HASH,
    route: "SYNTHETIC_ROUTE_ALPHA",
    reason_codes: ["SYN_MH_POLICY_REASON_ALPHA"],
    policy_reference: {
      policy_id: "syn_mh_policy_fixture",
      policy_version: "engineering.v1",
      content_hash: HASH,
    },
    decided_at: "2026-10-31T18:00:00.000Z",
    authority: "ENGINEERING_ONLY",
    classification: "ENGINEERING_SYNTHETIC",
    verification: "UNVERIFIED",
    ...overrides,
  };
}
function project(value: unknown = decision(), environment: unknown = "TEST") {
  return projectSyntheticMentalHealthPresentation({
    decision: value,
    environment,
    observedAt: NOW,
  });
}

describe("P14-D isolated synthetic presentation", () => {
  it.each(["LOCAL", "TEST"])("accepts an exact toy decision in %s", (environment) => {
    expect(project(decision(), environment)).toMatchObject({
      kind: "ENGINEERING_SYNTHETIC_PREVIEW",
      route: "SYNTHETIC_ROUTE_ALPHA",
      reason_codes: ["SYN_MH_POLICY_REASON_ALPHA"],
    });
  });
  it.each([undefined, "STAGING", "PILOT", "PRODUCTION"])(
    "denies protected environment before reading data: %s",
    (environment) => {
      const hostile = Object.defineProperty({}, "route", {
        get() {
          throw new Error("private-canary");
        },
      });
      expect(
        projectSyntheticMentalHealthPresentation({
          decision: hostile,
          environment,
          observedAt: NOW,
        }),
      ).toEqual({
        contract_version: "synthetic-mental-health-presentation.v1",
        kind: "NOT_AVAILABLE",
        code: "POLICY_UNAPPROVED_OR_UNAVAILABLE",
      });
    },
  );
  it.each([
    null,
    [],
    decision({ patient_id: "private-canary" }),
    decision({ route: "ROUTE_C" }),
    decision({ reason_codes: ["SYN_MH_POLICY_REASON_ALPHA", "SYN_MH_POLICY_REASON_BETA"] }),
    decision({ decided_at: "2026-10-31T18:00:31.000Z" }),
    decision({ policy_reference: null }),
    decision({ decision_id: "private-canary" }),
    decision({ evaluation_id: "syn_mh_policy_evaluation_epsilon" }),
    decision({ decision_id: "syn_mh_policy_decision_beta" }),
    decision({ reason_codes: ["SYN_MH_POLICY_REASON_BETA"] }),
    decision({
      route: "SYNTHETIC_DEGRADED_SAFE_FALLBACK",
      reason_codes: ["SYN_MH_POLICY_REASON_ALPHA"],
    }),
  ])("degrades malformed/unauthorized input without echoing it", (value) => {
    const state = project(value);
    expect(state).toEqual({
      contract_version: "synthetic-mental-health-presentation.v1",
      kind: "DEGRADED",
      code: "INVALID_OR_INCOMPATIBLE_RESULT",
    });
    expect(JSON.stringify(state)).not.toContain("private-canary");
  });
  it("is immutable and has no production component or route", () => {
    const state = project();
    expect(Object.isFrozen(state)).toBe(true);
    const { container } = render(<SyntheticMentalHealthPreview state={state} />);
    expect(screen.getByText("Engineering test data only — not a medical assessment")).toBeVisible();
    expect(container.querySelector("a,button,input,form")).toBeNull();
    expect(screen.queryByText(/call|seek|diagnosis|treatment|crisis/i)).toBeNull();
    expect(
      existsSync(join(process.cwd(), "components", "mental-health", "synthetic-preview.tsx")),
    ).toBe(false);
    const appSource = readFileSync(join(process.cwd(), "app", "page.tsx"), "utf8");
    expect(appSource).not.toContain("SyntheticMentalHealthPreview");
  });
});
