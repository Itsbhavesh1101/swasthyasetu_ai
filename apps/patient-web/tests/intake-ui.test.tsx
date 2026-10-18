import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AnswerControl } from "../components/intake/answer-control";
import { answerBody } from "../components/intake/intake-journey";
import type { AnswerType, IntakeQuestion } from "../lib/intake/contracts";

function question(answerType: AnswerType): IntakeQuestion {
  const constraints: Record<string, unknown> = {
    TEXT: { min_length: 1, max_length: 20 },
    SINGLE_CHOICE: { allowed_option_ids: ["one", "two"] },
    MULTI_CHOICE: { allowed_option_ids: ["one", "two"] },
    BOOLEAN: {},
    NUMBER: { minimum: "0", maximum: "10", unit: "unit" },
    DATE: { earliest: "2020-01-01", latest: "2030-01-01" },
    DURATION: { allowed_units: ["day", "week"] },
    SEVERITY_SCALE: { allowed_values: ["0", "1", "2"] },
  }[answerType] as Record<string, unknown>;
  return {
    question_id: `synthetic.${answerType.toLowerCase()}`,
    question_version: "1",
    pack_id: "synthetic.pack",
    pack_version: "1",
    section: "EXTENSION",
    prompt: `Synthetic ${answerType} question`,
    help_text: "Synthetic representation-only help",
    answer_type: answerType,
    requiredness: "REQUIRED",
    allow_unknown: false,
    allow_prefer_not_to_answer: false,
    allow_skip: false,
    constraints,
    options: [
      { id: "one", label: "Option one" },
      { id: "two", label: "Option two" },
    ],
  };
}

describe("P7-C answer controls", () => {
  it.each<AnswerType>([
    "TEXT",
    "SINGLE_CHOICE",
    "MULTI_CHOICE",
    "BOOLEAN",
    "NUMBER",
    "DATE",
    "DURATION",
    "SEVERITY_SCALE",
  ])("renders an accessible %s control from server metadata", (answerType) => {
    render(<AnswerControl disabled={false} question={question(answerType)} />);
    expect(document.querySelector("input, textarea, select")).not.toBeNull();
  });

  it("submits the configured NUMBER unit as server-derived hidden metadata", () => {
    const { container } = render(
      <form>
        <AnswerControl disabled={false} question={question("NUMBER")} />
      </form>,
    );
    const form = container.querySelector("form");
    const value = container.querySelector<HTMLInputElement>('input[name="value"]');
    expect(form).not.toBeNull();
    expect(value).not.toBeNull();
    if (!form || !value) throw new Error("synthetic NUMBER form did not render");
    value.value = "2.5";
    const payload = answerBody(question("NUMBER"), new FormData(form), 7);
    expect(payload).toMatchObject({
      question_id: "synthetic.number",
      expected_version: 7,
      answer: { answer_type: "NUMBER", value: 2.5, unit: "unit" },
    });
    expect(container.querySelector('input[type="hidden"][name="unit"]')).toHaveValue("unit");
  });

  it.each([
    [
      "TEXT",
      { value: "synthetic text" },
      { value: "synthetic text", original_text: "synthetic text" },
    ],
    [
      "SINGLE_CHOICE",
      { selected_option_ids: ["one"] },
      { value: null, selected_option_ids: ["one"] },
    ],
    [
      "MULTI_CHOICE",
      { selected_option_ids: ["one", "two"] },
      { value: null, selected_option_ids: ["one", "two"] },
    ],
    ["BOOLEAN", { value: "false" }, { value: false }],
    ["NUMBER", { value: "4.5", unit: "unit" }, { value: 4.5, unit: "unit" }],
    ["DATE", { value: "2026-10-18" }, { value: "2026-10-18" }],
    ["DURATION", { value: "3", unit: "day" }, { value: 3, unit: "day" }],
    ["SEVERITY_SCALE", { value: "2" }, { value: 2, unit: null }],
  ] as const)("builds the canonical %s request shape", (answerType, entries, expected) => {
    const form = new FormData();
    for (const [key, raw] of Object.entries(entries)) {
      for (const value of Array.isArray(raw) ? raw : [raw]) form.append(key, value);
    }
    const payload = answerBody(question(answerType), form, 3);
    expect(payload.answer).toMatchObject({
      answer_type: answerType,
      response_disposition: "ANSWERED",
      ...expected,
    });
  });

  it.each([
    ["UNKNOWN", "allow_unknown"],
    ["PREFER_NOT_TO_ANSWER", "allow_prefer_not_to_answer"],
    ["SKIPPED", "allow_skip"],
  ] as const)("emits an allowed %s disposition without stale values", (disposition, flag) => {
    const configured = { ...question("TEXT"), [flag]: true };
    const form = new FormData();
    form.set("value", "must not be submitted");
    form.set("response_disposition", disposition);
    expect(answerBody(configured, form, 2).answer).toMatchObject({
      value: null,
      selected_option_ids: null,
      unit: null,
      original_text: null,
      response_disposition: disposition,
    });
  });
});
