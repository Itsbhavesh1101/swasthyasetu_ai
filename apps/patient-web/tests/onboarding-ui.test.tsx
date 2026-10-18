import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import ConsentPage from "../app/consent/page";
import EncounterPage from "../app/encounter/page";
import LanguagePage from "../app/language/page";
import StartPage from "../app/start/page";

const push = vi.fn();

vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

beforeEach(() => push.mockReset());

describe("P6-B onboarding UI", () => {
  it("explains the private start without making a backend call", () => {
    const fetchSpy = vi.fn();
    vi.stubGlobal("fetch", fetchSpy);
    render(<StartPage />);

    expect(screen.getByRole("heading", { level: 1, name: /begin privately/i })).toBeVisible();
    expect(screen.getByText(/no name is required/i)).toBeVisible();
    expect(screen.getByText(/temporary pseudonymous session/i)).toBeVisible();
    expect(screen.getByText(/review consent/i)).toBeVisible();
    expect(screen.getByRole("link", { name: "Continue" })).toHaveAttribute("href", "/language");
    expect(screen.getByRole("link", { name: /urgent help/i })).toHaveAttribute(
      "href",
      "/urgent-help",
    );
    expect(fetchSpy).not.toHaveBeenCalled();
  });

  it("offers keyboard-operable English and Hindi choices and creates the session", async () => {
    const user = userEvent.setup();
    const fetchSpy = vi.fn().mockResolvedValue(
      Response.json({
        state: "ACTIVE",
        session_id: "safe-id",
        language_preference: "en",
        expires_at: "2026-10-12T11:00:00Z",
      }),
    );
    vi.stubGlobal("fetch", fetchSpy);
    render(<LanguagePage />);

    expect(screen.getByRole("radio", { name: /English/i })).not.toBeChecked();
    expect(screen.getByRole("radio", { name: /हिन्दी/i })).not.toBeChecked();
    expect(screen.getByRole("button", { name: /continue to consent/i })).toBeDisabled();

    await user.tab();
    expect(screen.getByRole("radio", { name: /English/i })).toHaveFocus();
    await user.keyboard(" ");
    expect(screen.getByRole("radio", { name: /English/i })).toBeChecked();
    await user.click(screen.getByRole("button", { name: /continue to consent/i }));

    expect(fetchSpy).toHaveBeenCalledWith(
      "/api/onboarding/session",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ language_preference: "en" }),
      }),
    );
    expect(push).toHaveBeenCalledWith("/consent");
  });

  it("shows an honest language-service error", async () => {
    const user = userEvent.setup();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json({}, { status: 503 })));
    render(<LanguagePage />);

    await user.click(screen.getByRole("radio", { name: /हिन्दी/i }));
    await user.click(screen.getByRole("button", { name: /continue to consent/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/temporarily unavailable/i);
    expect(push).not.toHaveBeenCalled();
  });

  it("requires unchecked explicit agreement before granting consent", async () => {
    const user = userEvent.setup();
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce(Response.json({ state: "NOT_GRANTED" }))
      .mockResolvedValueOnce(
        Response.json({
          state: "GRANTED",
          notice_version: "privacy-v1",
          granted_at: "2026-10-12T10:00:00Z",
        }),
      );
    vi.stubGlobal("fetch", fetchSpy);
    render(<ConsentPage />);

    const agreement = await screen.findByRole("checkbox", {
      name: /I understand and agree to this use for this session/i,
    });
    const grant = screen.getByRole("button", { name: /agree and continue/i });
    expect(agreement).not.toBeChecked();
    expect(grant).toBeDisabled();
    expect(screen.getByText(/not an emergency service/i)).toBeVisible();
    expect(screen.getByText(/does not include referral sharing/i)).toBeVisible();

    await user.click(agreement);
    await user.click(grant);

    expect(fetchSpy).toHaveBeenLastCalledWith(
      "/api/onboarding/consent",
      expect.objectContaining({ method: "POST" }),
    );
    expect(push).toHaveBeenCalledWith("/encounter");
  });

  it("renders loading then an existing granted state with withdrawal", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        Response.json({
          state: "GRANTED",
          notice_version: "privacy-v1",
          granted_at: "2026-10-12T10:00:00Z",
        }),
      ),
    );
    render(<ConsentPage />);

    expect(screen.getByRole("status")).toHaveTextContent(/checking your session consent/i);
    expect(await screen.findByText(/consent is active for this session/i)).toBeVisible();
    expect(screen.getByRole("button", { name: /withdraw this consent/i })).toBeVisible();
  });

  it("withdraws consent without closing the session", async () => {
    const user = userEvent.setup();
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce(Response.json({ state: "GRANTED" }))
      .mockResolvedValueOnce(Response.json({ state: "REVOKED" }));
    vi.stubGlobal("fetch", fetchSpy);
    render(<ConsentPage />);

    await user.click(await screen.findByRole("button", { name: /withdraw this consent/i }));
    expect(await screen.findByText(/consent has been withdrawn/i)).toBeVisible();
    expect(fetchSpy).toHaveBeenLastCalledWith(
      "/api/onboarding/consent/revoke",
      expect.objectContaining({ method: "POST" }),
    );
    expect(fetchSpy).not.toHaveBeenCalledWith("/api/onboarding/session/close", expect.anything());
  });

  it.each([
    [{ state: "NO_SESSION" }, null, /start a private session/i, "/language"],
    [{ state: "ACTIVE" }, { state: "NOT_GRANTED" }, /consent is still needed/i, "/consent"],
    [{ state: "ACTIVE" }, { state: "GRANTED" }, /private session and consent are ready/i, null],
  ])(
    "shows the governed encounter readiness state",
    async (session, consent, message, expectedHref) => {
      const fetchSpy = vi.fn().mockResolvedValueOnce(Response.json(session));
      if (consent) fetchSpy.mockResolvedValueOnce(Response.json(consent));
      vi.stubGlobal("fetch", fetchSpy);
      render(<EncounterPage />);

      expect(await screen.findByText(message)).toBeVisible();
      if (expectedHref === null) {
        expect(screen.getByRole("button", { name: /start intake/i })).toBeVisible();
      } else {
        expect(screen.getByText(/clinical intake is not available/i)).toBeVisible();
      }
      if (expectedHref) {
        expect(screen.getByRole("link", { name: /continue/i })).toHaveAttribute(
          "href",
          expectedHref,
        );
        if (expectedHref === "/consent") {
          expect(screen.getByRole("button", { name: /end private session/i })).toBeVisible();
        }
      } else {
        expect(screen.getByRole("button", { name: /end private session/i })).toBeVisible();
      }
    },
  );

  it("shows degraded readiness and lets an active session be ended", async () => {
    const user = userEvent.setup();
    const fetchSpy = vi
      .fn()
      .mockResolvedValueOnce(Response.json({ state: "ACTIVE" }))
      .mockResolvedValueOnce(Response.json({ state: "GRANTED" }))
      .mockResolvedValueOnce(Response.json({ state: "CLOSED" }));
    vi.stubGlobal("fetch", fetchSpy);
    render(<EncounterPage />);

    await user.click(await screen.findByRole("button", { name: /end private session/i }));
    await waitFor(() => expect(push).toHaveBeenCalledWith("/language"));
    expect(fetchSpy).toHaveBeenLastCalledWith(
      "/api/onboarding/session/close",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
