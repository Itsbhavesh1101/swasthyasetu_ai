import { render, screen } from "@testing-library/react";
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

import { SyntheticSafetyPreview } from "./support/synthetic-safety-preview";
import {
  projectSyntheticSafetyPresentation,
  type SafetyPresentationState,
} from "../lib/safety/presentation";

const OBSERVED_AT = new Date("2026-10-19T12:00:30.000Z");

function syntheticDecision(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    route: "EMERGENCY",
    reason_codes: ["SYNTHETIC_OVERRIDE_A"],
    policy_id: "synthetic-physical-safety-metadata",
    policy_version: "engineering.1",
    requires_clarification: false,
    blocks_self_care: true,
    created_at: "2026-10-19T12:00:00.000Z",
    ...overrides,
  };
}

function project(
  decision: unknown = syntheticDecision(),
  environment?: unknown,
): SafetyPresentationState {
  const resolvedEnvironment = arguments.length < 2 ? "TEST" : environment;
  return projectSyntheticSafetyPresentation({
    decision,
    environment: resolvedEnvironment,
    observedAt: OBSERVED_AT,
  });
}

describe("P9-C synthetic safety presentation contract", () => {
  it.each(["LOCAL", "TEST"])(
    "projects the exact engineering fixture in %s while keeping presentation self-care blocked",
    (environment) => {
      expect(project(syntheticDecision(), environment)).toEqual({
        contract_version: "safety-presentation.v1",
        kind: "ENGINEERING_SYNTHETIC_PREVIEW",
        blocks_self_care: true,
        classification: "ENGINEERING_ONLY",
        synthetic_decision: {
          route: "EMERGENCY",
          reason_codes: ["SYNTHETIC_OVERRIDE_A"],
          policy_id: "synthetic-physical-safety-metadata",
          policy_version: "engineering.1",
          requires_clarification: false,
          blocks_self_care: true,
          created_at: "2026-10-19T12:00:00.000Z",
        },
      });
    },
  );

  it.each([undefined, null, "", "UNKNOWN", "STAGING", "PILOT", "PRODUCTION"])(
    "fails closed before reading a decision in environment %s",
    (environment) => {
      const decision = Object.defineProperty({}, "route", {
        get() {
          throw new Error("decision must not be read");
        },
      });
      expect(project(decision, environment)).toEqual({
        contract_version: "safety-presentation.v1",
        kind: "NOT_AVAILABLE",
        blocks_self_care: true,
        code: "POLICY_UNAPPROVED_OR_UNAVAILABLE",
      });
    },
  );

  it.each([
    ["wrong root", null],
    ["array root", []],
    ["unknown top-level key", syntheticDecision({ approved: true })],
    ["patient identifier", syntheticDecision({ patient_id: "privacy-canary" })],
    ["source evidence", syntheticDecision({ source_evidence: "privacy-canary" })],
    ["unknown route", syntheticDecision({ route: "CLEARED" })],
    ["forged policy identity", syntheticDecision({ policy_id: "physical-safety" })],
    ["forged policy version", syntheticDecision({ policy_version: "approved.1" })],
    ["wrong reason namespace", syntheticDecision({ reason_codes: ["PATIENT_DANGER"] })],
    ["unordered reasons", syntheticDecision({ reason_codes: ["SYNTHETIC_Z", "SYNTHETIC_A"] })],
    ["duplicate reasons", syntheticDecision({ reason_codes: ["SYNTHETIC_A", "SYNTHETIC_A"] })],
    ["overlong reasons", syntheticDecision({ reason_codes: Array(17).fill("SYNTHETIC_A") })],
    ["nested reason object", syntheticDecision({ reason_codes: [{ code: "SYNTHETIC_A" }] })],
    ["wrong clarification flag type", syntheticDecision({ requires_clarification: 0 })],
    ["wrong self-care flag type", syntheticDecision({ blocks_self_care: "true" })],
    [
      "inconsistent clarification route",
      syntheticDecision({ route: "CLARIFICATION_REQUIRED", requires_clarification: false }),
    ],
    [
      "clarification that does not block fixture self-care",
      syntheticDecision({
        route: "CLARIFICATION_REQUIRED",
        requires_clarification: true,
        blocks_self_care: false,
      }),
    ],
    ["non-UTC timestamp", syntheticDecision({ created_at: "2026-10-19T17:30:00+05:30" })],
    ["future timestamp", syntheticDecision({ created_at: "2026-10-19T12:00:31.000Z" })],
    ["stale timestamp", syntheticDecision({ created_at: "2026-10-19T11:59:29.999Z" })],
  ])("degrades safely for %s", (_label, decision) => {
    expect(project(decision)).toEqual({
      contract_version: "safety-presentation.v1",
      kind: "DEGRADED",
      blocks_self_care: true,
      code: "INVALID_OR_INCOMPATIBLE_RESULT",
    });
  });

  it.each([
    ["single hole", Array(1)],
    ["leading hole", [, "SYNTHETIC_B"]],
    ["trailing hole", ["SYNTHETIC_A", ,]],
    ["undefined element", [undefined]],
    ["null element", [null]],
    ["invalid element", ["privacy-canary"]],
    ["too many elements", Array.from({ length: 17 }, (_, index) => `SYNTHETIC_${index}`)],
    ["duplicate elements", ["SYNTHETIC_A", "SYNTHETIC_A"]],
    ["unsorted elements", ["SYNTHETIC_B", "SYNTHETIC_A"]],
  ])("rejects adversarial reason arrays with a %s", (_label, reason_codes) => {
    const state = project(syntheticDecision({ reason_codes }));
    expect(state).toEqual({
      contract_version: "safety-presentation.v1",
      kind: "DEGRADED",
      blocks_self_care: true,
      code: "INVALID_OR_INCOMPATIBLE_RESULT",
    });
    expect(JSON.stringify(state)).not.toContain("privacy-canary");
    expect(JSON.stringify(state)).not.toContain("undefined");
  });

  it("rejects non-enumerable and symbol extra own keys without reading or echoing them", () => {
    const hidden = syntheticDecision();
    Object.defineProperty(hidden, "patient_id", {
      enumerable: false,
      value: "hidden-privacy-canary",
    });
    const symbol = syntheticDecision();
    Object.defineProperty(symbol, Symbol("source_evidence"), {
      enumerable: false,
      get() {
        throw new Error("symbol-privacy-canary");
      },
    });

    for (const decision of [hidden, symbol]) {
      const state = project(decision);
      expect(state.kind).toBe("DEGRADED");
      expect(JSON.stringify(state)).not.toContain("privacy-canary");
    }
  });

  it("contains hostile own-key and array-index traps without echoing their canaries", () => {
    const ownKeyCanary = "own-key-privacy-canary";
    const hostileDecision = new Proxy(syntheticDecision(), {
      ownKeys() {
        throw new Error(ownKeyCanary);
      },
    });
    const reasonCanary = "reason-index-privacy-canary";
    const hostileReasons = ["SYNTHETIC_A"];
    Object.defineProperty(hostileReasons, 0, {
      enumerable: true,
      get() {
        throw new Error(reasonCanary);
      },
    });

    for (const decision of [hostileDecision, syntheticDecision({ reason_codes: hostileReasons })]) {
      const state = project(decision);
      expect(state.kind).toBe("DEGRADED");
      expect(JSON.stringify(state)).not.toContain("privacy-canary");
    }
  });

  it.each([
    ["second precision", "2026-10-19T12:00:00Z"],
    ["millisecond precision", "2026-10-19T12:00:00.000Z"],
  ])("accepts canonical UTC %s", (_label, created_at) => {
    expect(project(syntheticDecision({ created_at })).kind).toBe("ENGINEERING_SYNTHETIC_PREVIEW");
  });

  it.each([
    ["February 30", "2026-02-30T12:00:00Z", "2026-03-02T12:00:30Z"],
    ["non-leap February 29", "2025-02-29T12:00:00Z", "2025-03-01T12:00:30Z"],
    ["hour 24", "2026-10-19T24:00:00Z", "2026-10-20T00:00:30Z"],
  ])(
    "rejects calendar-invalid UTC %s even when normalization looks fresh",
    (_label, created_at, observedAt) => {
      expect(
        projectSyntheticSafetyPresentation({
          decision: syntheticDecision({ created_at }),
          environment: "TEST",
          observedAt: new Date(observedAt),
        }),
      ).toEqual({
        contract_version: "safety-presentation.v1",
        kind: "DEGRADED",
        blocks_self_care: true,
        code: "INVALID_OR_INCOMPATIBLE_RESULT",
      });
    },
  );

  it.each([
    ["EMERGENCY", false, true],
    ["PRIORITY_REVIEW", false, true],
    ["ROUTINE_CARE", false, true],
    ["SUPPORTED_SELF_CARE", false, false],
    ["CLARIFICATION_REQUIRED", true, true],
  ])("accepts the bounded toy %s flag shape", (route, clarification, blocksSelfCare) => {
    const state = project(
      syntheticDecision({
        route,
        reason_codes: [`SYNTHETIC_${route}`],
        requires_clarification: clarification,
        blocks_self_care: blocksSelfCare,
      }),
    );
    expect(state.kind).toBe("ENGINEERING_SYNTHETIC_PREVIEW");
    expect(state.blocks_self_care).toBe(true);
  });

  it("returns immutable bounded values and never echoes rejected content", () => {
    const state = project(syntheticDecision({ patient_id: "private-patient-canary" }));
    expect(Object.isFrozen(state)).toBe(true);
    expect(JSON.stringify(state)).not.toContain("private-patient-canary");

    const preview = project();
    expect(Object.isFrozen(preview)).toBe(true);
    if (preview.kind !== "ENGINEERING_SYNTHETIC_PREVIEW") {
      throw new Error("expected a synthetic engineering preview");
    }
    expect(Object.isFrozen(preview.synthetic_decision)).toBe(true);
    expect(Object.isFrozen(preview.synthetic_decision.reason_codes)).toBe(true);
  });

  it("contains invalid clocks and throwing decision access as a content-free degraded state", () => {
    expect(
      projectSyntheticSafetyPresentation({
        decision: syntheticDecision(),
        environment: "TEST",
        observedAt: new Date(Number.NaN),
      }),
    ).toEqual({
      contract_version: "safety-presentation.v1",
      kind: "DEGRADED",
      blocks_self_care: true,
      code: "INVALID_OR_INCOMPATIBLE_RESULT",
    });

    const canary = "private-patient-canary";
    const throwingDecision = Object.defineProperty({}, "route", {
      get() {
        throw new Error(canary);
      },
      enumerable: true,
    });
    const state = project(throwingDecision);
    expect(state.kind).toBe("DEGRADED");
    expect(JSON.stringify(state)).not.toContain(canary);
  });
});

describe("P9-C isolated synthetic preview component", () => {
  it("exists only in test support and has no production import path", () => {
    const patientRoot = process.cwd();
    const productionPreview = join(
      patientRoot,
      "components",
      "safety",
      "synthetic-safety-preview.tsx",
    );
    const productionRoots = [join(patientRoot, "app"), join(patientRoot, "components")];
    function walk(path: string): string[] {
      if (!existsSync(path)) return [];
      return readdirSync(path).flatMap((entry) => {
        const candidate = join(path, entry);
        return statSync(candidate).isDirectory() ? walk(candidate) : [candidate];
      });
    }
    const sourceFiles = productionRoots.flatMap((root) => walk(root));

    expect(existsSync(productionPreview)).toBe(false);
    expect(
      sourceFiles
        .filter((path) => /\.(?:ts|tsx)$/.test(path))
        .map((path) => readFileSync(path, "utf8"))
        .join("\n"),
    ).not.toContain("SyntheticSafetyPreview");
  });

  it("labels toy data prominently and exposes only harmless machine literals", () => {
    const { container } = render(<SyntheticSafetyPreview state={project()} />);

    expect(screen.getByText("Engineering test data only — not a medical assessment")).toBeVisible();
    expect(
      screen.getByRole("heading", { level: 2, name: "Synthetic safety preview" }),
    ).toBeVisible();
    expect(screen.getByText("EMERGENCY")).toBeVisible();
    expect(screen.getByText("SYNTHETIC_OVERRIDE_A")).toBeVisible();
    expect(screen.getByRole("status")).toBeVisible();
    expect(container).not.toHaveTextContent(/seek|call|clinician|treatment|diagnosis|cleared/i);
    expect(container.querySelector("a, button, input, form")).toBeNull();
  });

  it.each([
    ["NOT_AVAILABLE", "No safety assessment has been performed."],
    ["DEGRADED", "No safety assessment has been performed."],
  ] as const)("renders the %s state without an optimistic result", (kind, message) => {
    const state: SafetyPresentationState =
      kind === "NOT_AVAILABLE"
        ? {
            contract_version: "safety-presentation.v1",
            kind,
            blocks_self_care: true,
            code: "POLICY_UNAPPROVED_OR_UNAVAILABLE",
          }
        : {
            contract_version: "safety-presentation.v1",
            kind,
            blocks_self_care: true,
            code: "INVALID_OR_INCOMPATIBLE_RESULT",
          };
    render(<SyntheticSafetyPreview state={state} />);

    expect(screen.getByRole("status")).toHaveTextContent(message);
    expect(screen.queryByText(/assessment completed|routine care|supported self-care/i)).toBeNull();
  });
});
