import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { AnswerControl } from "../components/intake/answer-control";
import { answerBody, IntakeJourney } from "../components/intake/intake-journey";
import { intakeRequest } from "../lib/intake/client";
import type { AnswerType, IntakeQuestion, IntakeView } from "../lib/intake/contracts";

const push = vi.fn();
const replace = vi.fn();
const router = { push, replace };

vi.mock("next/navigation", () => ({ useRouter: () => router }));
vi.mock("../lib/intake/client", () => ({ intakeRequest: vi.fn() }));

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

function intakeView(): IntakeView {
  return {
    intake_id: "11111111-1111-4111-8111-111111111111",
    encounter_id: "22222222-2222-4222-8222-222222222222",
    status: "IN_PROGRESS",
    version: 1,
    started_at: "2026-11-02T00:00:00Z",
    completed_at: null,
    pack_versions: [{ pack_id: "synthetic.pack", pack_version: "1" }],
    completion_ready: false,
    current_question: question("TEXT"),
    engine_state: "NEXT_QUESTION",
    answers: [],
    missing_information: [],
  };
}

describe("P7-C answer controls", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

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

  it("keeps a failed-save message and unsent input after authoritative state refetch", async () => {
    const request = vi.mocked(intakeRequest);
    const current = intakeView();
    request
      .mockResolvedValueOnce({ ok: true, value: current })
      .mockResolvedValueOnce({
        ok: false,
        error: {
          code: "BACKEND_UNAVAILABLE",
          message: "The intake request could not be completed.",
        },
      })
      .mockResolvedValueOnce({ ok: true, value: current });

    const user = userEvent.setup();
    render(<IntakeJourney intakeId={current.intake_id} />);
    const answer = await screen.findByLabelText(/synthetic text question/i);
    await user.type(answer, "Synthetic unsent");
    await user.click(screen.getByRole("button", { name: /save and continue/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "The intake request could not be completed.",
    );
    expect(answer).toHaveValue("Synthetic unsent");
    await waitFor(() => expect(request).toHaveBeenCalledTimes(3));
    expect(request.mock.calls.filter(([, init]) => init?.method === "POST")).toHaveLength(1);
    expect(push).not.toHaveBeenCalled();
  });

  it("renders refetched saved state without replaying an ambiguously acknowledged mutation", async () => {
    const request = vi.mocked(intakeRequest);
    const current = intakeView();
    const saved: IntakeView = {
      ...current,
      version: 2,
      completion_ready: true,
      current_question: null,
      engine_state: "COMPLETION_READY",
      answers: [
        {
          answer_id: "33333333-3333-4333-8333-333333333333",
          question_id: current.current_question?.question_id ?? "synthetic.text",
          question_version: "1",
          answer_type: "TEXT",
          value: "Synthetic saved",
          selected_option_ids: null,
          unit: null,
          response_disposition: "ANSWERED",
          source_label: "Patient-provided text",
        },
      ],
    };
    request
      .mockResolvedValueOnce({ ok: true, value: current })
      .mockResolvedValueOnce({
        ok: false,
        error: {
          code: "REQUEST_FAILED",
          message: "The request could not be confirmed. Refresh before trying again.",
        },
      })
      .mockResolvedValueOnce({ ok: true, value: saved });

    const user = userEvent.setup();
    render(<IntakeJourney intakeId={current.intake_id} />);
    await user.type(await screen.findByLabelText(/synthetic text question/i), "Synthetic saved");
    await user.click(screen.getByRole("button", { name: /save and continue/i }));

    expect(
      await screen.findByRole("heading", { level: 2, name: "Review is needed" }),
    ).toBeVisible();
    expect(screen.getByRole("alert")).toHaveTextContent(
      "The request could not be confirmed. Refresh before trying again.",
    );
    expect(request.mock.calls.filter(([, init]) => init?.method === "POST")).toHaveLength(1);
    expect(push).not.toHaveBeenCalled();
  });

  it("discards stale input and requires review after an authoritative version conflict", async () => {
    const request = vi.mocked(intakeRequest);
    const current = intakeView();
    const authoritative: IntakeView = {
      ...current,
      version: 2,
      completion_ready: true,
      current_question: null,
      engine_state: "COMPLETION_READY",
      answers: [
        {
          answer_id: "44444444-4444-4444-8444-444444444444",
          question_id: current.current_question?.question_id ?? "synthetic.text",
          question_version: "1",
          answer_type: "TEXT",
          value: "Synthetic authoritative answer",
          selected_option_ids: null,
          unit: null,
          response_disposition: "ANSWERED",
          source_label: "Patient-provided text",
        },
      ],
    };
    request
      .mockResolvedValueOnce({ ok: true, value: current })
      .mockResolvedValueOnce({
        ok: false,
        error: {
          code: "RESOURCE_CONFLICT",
          message: "This intake changed. Refresh and review the latest saved draft.",
        },
      })
      .mockResolvedValueOnce({ ok: true, value: authoritative });

    const user = userEvent.setup();
    render(<IntakeJourney intakeId={current.intake_id} />);
    await user.type(
      await screen.findByLabelText(/synthetic text question/i),
      "Synthetic stale answer",
    );
    await user.click(screen.getByRole("button", { name: /save and continue/i }));

    expect(
      await screen.findByRole("heading", { level: 2, name: "Review the latest saved draft" }),
    ).toBeVisible();
    expect(screen.getByRole("alert")).toHaveTextContent(
      "This intake changed. Refresh and review the latest saved draft.",
    );
    expect(screen.queryByDisplayValue("Synthetic stale answer")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /save and continue/i })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Review latest draft" })).toHaveAttribute(
      "href",
      `/intake/${current.intake_id}/review`,
    );
    expect(request.mock.calls.filter(([, init]) => init?.method === "POST")).toHaveLength(1);
    expect(push).not.toHaveBeenCalled();
  });

  it("removes loaded intake state and returns to session start when the session is invalid", async () => {
    const request = vi.mocked(intakeRequest);
    const current = intakeView();
    request.mockResolvedValueOnce({ ok: true, value: current }).mockResolvedValueOnce({
      ok: false,
      error: { code: "SESSION_UNAVAILABLE", message: "Start a private session first." },
    });

    const user = userEvent.setup();
    render(<IntakeJourney intakeId={current.intake_id} />);
    const answer = await screen.findByLabelText(/synthetic text question/i);
    await user.type(answer, "Synthetic value removed on session loss");
    await user.click(screen.getByRole("button", { name: /save and continue/i }));

    await waitFor(() => expect(replace).toHaveBeenCalledWith("/language"));
    expect(
      screen.queryByDisplayValue("Synthetic value removed on session loss"),
    ).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /save and continue/i })).not.toBeInTheDocument();
    expect(request).toHaveBeenCalledTimes(2);
    expect(push).not.toHaveBeenCalled();
  });
});
