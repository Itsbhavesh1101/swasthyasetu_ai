import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AnswerControl } from "../components/intake/answer-control";
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
});
