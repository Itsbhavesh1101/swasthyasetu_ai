import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";

import LoginPage from "../app/login/page";
import RegisterPage from "../app/register/page";

const push = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));

beforeEach(() => {
  push.mockReset();
  vi.unstubAllGlobals();
});

it("registers with labeled fields and blocks password mismatch", async () => {
  const user = userEvent.setup();
  const fetchSpy = vi.fn();
  vi.stubGlobal("fetch", fetchSpy);
  render(<RegisterPage />);
  expect(
    screen.getByRole("heading", { level: 1, name: /create your patient account/i }),
  ).toBeVisible();
  await user.type(screen.getByLabelText(/^email/i), "patient@example.com");
  await user.type(screen.getByLabelText(/^password/i), "correct horse battery staple");
  await user.type(screen.getByLabelText(/confirm password/i), "different password here");
  await user.click(screen.getByRole("button", { name: /create account/i }));
  expect(screen.getByRole("alert")).toHaveTextContent(/passwords do not match/i);
  expect(fetchSpy).not.toHaveBeenCalled();
});

it("submits registration once, clears secrets, and navigates", async () => {
  const user = userEvent.setup();
  let resolve!: (value: Response) => void;
  const fetchSpy = vi.fn(() => new Promise<Response>((done) => (resolve = done)));
  vi.stubGlobal("fetch", fetchSpy);
  render(<RegisterPage />);
  await user.type(screen.getByLabelText(/^email/i), "patient@example.com");
  await user.type(screen.getByLabelText(/^password/i), "correct horse battery staple");
  await user.type(screen.getByLabelText(/confirm password/i), "correct horse battery staple");
  const submit = screen.getByRole("button", { name: /create account/i });
  await user.click(submit);
  expect(submit).toBeDisabled();
  expect(fetchSpy).toHaveBeenCalledTimes(1);
  resolve(Response.json({ state: "AUTHENTICATED", profileComplete: false }, { status: 201 }));
  expect(await screen.findByText(/account created/i)).toBeVisible();
  expect(push).toHaveBeenCalledWith("/profile?setup=1");
  expect(screen.getByLabelText(/^password/i)).toHaveValue("");
});

it("shows one generic login error and never repopulates password", async () => {
  const user = userEvent.setup();
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json({ error: {} }, { status: 401 })));
  render(<LoginPage />);
  await user.type(screen.getByLabelText(/^email/i), "patient@example.com");
  await user.type(screen.getByLabelText(/^password/i), "wrong password here");
  await user.click(screen.getByRole("button", { name: /sign in/i }));
  expect(await screen.findByRole("alert")).toHaveTextContent(/could not sign you in/i);
  expect(screen.getByLabelText(/^password/i)).toHaveValue("");
});
