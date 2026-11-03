import { expect, test } from "@playwright/test";

import { registerPatient, signInPatient } from "./support/patient-account";

test("patient account preserves profile, all history categories, correction, timeline, and intake", async ({
  page,
}) => {
  test.slow();
  const credentials = await registerPatient(page, "Synthetic History Patient");

  await page.goto("/profile");
  await page.getByLabel("Preferred language").selectOption("en");
  await page.getByLabel("Date of birth").fill("1998-04-12");
  await page.getByLabel("City or location (optional)").fill("Synthetic City");
  await page.getByRole("button", { name: "Save details" }).click();
  await expect(page.getByText("Your details have been saved.")).toBeVisible();

  await page.goto("/history");
  const form = page.locator("form.history-form").last();
  const entries = [
    ["PROBLEM", "Synthetic seasonal discomfort"],
    ["MEDICATION", "Synthetic medicine record"],
    ["ALLERGY", "Synthetic allergy record"],
    ["PROCEDURE", "Synthetic procedure record"],
    ["OBSERVATION", "Synthetic observation record"],
    ["INVESTIGATION", "Synthetic investigation record"],
  ] as const;
  for (const [category, label] of entries) {
    await form.getByLabel("Category").selectOption(category);
    await form.getByLabel(/name$/).fill(label);
    if (category === "OBSERVATION") await form.getByLabel("Value").fill("Synthetic normal value");
    await form.getByRole("button", { name: "Add entry" }).click();
    await expect(page.getByRole("heading", { name: label })).toBeVisible();
  }

  const original = page.getByRole("listitem").filter({ hasText: "Synthetic seasonal discomfort" });
  await original.getByRole("button", { name: "Correct entry" }).click();
  const correction = page.locator("form.history-form").last();
  await correction.getByLabel(/Condition name/).fill("Synthetic seasonal discomfort corrected");
  await correction.getByRole("button", { name: "Save correction" }).click();
  await expect(page.getByText("Previous version retained for history.")).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Synthetic seasonal discomfort corrected" }),
  ).toBeVisible();

  await page.goto("/timeline");
  await expect(page.getByText("Synthetic seasonal discomfort corrected")).toBeVisible();

  await page.goto("/encounter");
  await page.getByRole("button", { name: "Allow structured intake" }).click();
  await page.getByRole("button", { name: "Start or resume intake" }).click();
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+$/);
  await page.getByLabel(/what would you like to share/i).fill("Synthetic intake information");
  await page.getByRole("button", { name: /save and continue/i }).click();
  await expect(page).toHaveURL(/\/review$/);
  await page.getByRole("button", { name: /complete draft/i }).click();
  await expect(
    page.getByRole("heading", { name: "Your intake draft has been saved" }),
  ).toBeVisible();

  await page.getByRole("button", { name: /sign out/i }).click();
  await expect(page).toHaveURL(/\/login$/);
  await signInPatient(page, credentials.email, credentials.password);
  await page.goto("/history");
  await expect(
    page.getByRole("heading", { name: "Synthetic seasonal discomfort corrected" }),
  ).toBeVisible();
  await page.goto("/profile");
  await expect(page.getByLabel("City or location (optional)")).toHaveValue("Synthetic City");
});

test("backend rejects cross-account patient access", async ({ request }) => {
  const backend = process.env.SWASTHYASETU_BACKEND_URL ?? "http://127.0.0.1:8000";
  const register = async (number: number) => {
    const response = await request.post(`${backend}/api/v1/accounts/register`, {
      data: {
        email: `idor-${number}-${crypto.randomUUID()}@example.test`,
        display_name: `Synthetic IDOR ${number}`,
        password: "Synthetic-demo-passphrase-42",
      },
    });
    expect(response.status()).toBe(201);
    return response.json() as Promise<{ session_token: string }>;
  };
  const owner = await register(1);
  const attacker = await register(2);
  const current = await request.get(`${backend}/api/v1/accounts/me`, {
    headers: { Authorization: `Bearer ${owner.session_token}` },
  });
  expect(current.status()).toBe(200);
  const patientId = ((await current.json()) as { patient_id: string }).patient_id;
  const denied = await request.get(`${backend}/api/v1/patients/${patientId}`, {
    headers: { Authorization: `Bearer ${attacker.session_token}` },
  });
  expect(denied.status()).toBe(403);
});
