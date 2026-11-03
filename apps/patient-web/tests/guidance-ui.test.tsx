import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, expect, it, vi } from "vitest";

import GuidancePage from "../app/guidance/page";

afterEach(() => vi.unstubAllGlobals());

it("discloses external processing, previews the question, and renders cited safety copy", async () => {
  const user = userEvent.setup();
  const fetchSpy = vi
    .fn()
    .mockResolvedValueOnce(
      Response.json({
        state: "AUTHENTICATED",
        active: false,
        noticeVersion: "external-ai-v1",
        scope: ["ayurvedic_guidance"],
      }),
    )
    .mockResolvedValueOnce(Response.json({ state: "AUTHENTICATED", active: true }))
    .mockResolvedValueOnce(
      Response.json({
        outcome: "ANSWERED",
        answer: "Gentle hydration habits may support general wellbeing.",
        citations: [{ title: "WHO", url: "https://who.int/advice" }],
        retrievedAt: "2026-11-03T12:00:00Z",
      }),
    )
    .mockResolvedValueOnce(Response.json({ state: "AUTHENTICATED", active: false }));
  vi.stubGlobal("fetch", fetchSpy);
  render(<GuidancePage />);

  expect(await screen.findByText(/exact question you type will be sent/i)).toBeVisible();
  expect(screen.getByText(/name, email, history, and documents are not sent/i)).toBeVisible();
  await user.click(screen.getByRole("button", { name: "I agree and continue" }));

  const question = "How can I support hydration?";
  await user.type(await screen.findByLabelText("Your question"), question);
  expect(screen.getAllByText(question)).toHaveLength(2);
  await user.click(screen.getByRole("button", { name: "Get grounded information" }));

  expect(await screen.findByText(/gentle hydration habits/i)).toBeVisible();
  expect(screen.getByText(/not a diagnosis or prescription/i)).toBeVisible();
  expect(screen.getByRole("link", { name: "WHO" })).toHaveAttribute(
    "href",
    "https://who.int/advice",
  );
  expect(screen.getByText(/can interact with health conditions or medicines/i)).toBeVisible();
  await user.click(screen.getByRole("button", { name: "Withdraw permission" }));
  expect(await screen.findByRole("button", { name: "I agree and continue" })).toBeVisible();
  await waitFor(() => expect(fetchSpy).toHaveBeenCalledTimes(4));
});

it("never displays model text for a rejected result", async () => {
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValueOnce(
        Response.json({
          state: "AUTHENTICATED",
          active: true,
          noticeVersion: "external-ai-v1",
          scope: ["ayurvedic_guidance"],
        }),
      )
      .mockResolvedValueOnce(Response.json({ outcome: "REJECTED", citations: [] })),
  );
  const user = userEvent.setup();
  render(<GuidancePage />);
  await user.type(await screen.findByLabelText("Your question"), "A general wellness question");
  await user.click(screen.getByRole("button", { name: "Get grounded information" }));
  expect(await screen.findByText(/no remedy or model text has been displayed/i)).toBeVisible();
  expect(screen.queryByText(/raw model output/i)).toBeNull();
});
