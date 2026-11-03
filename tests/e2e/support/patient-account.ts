import { expect, type Page } from "@playwright/test";

export const patientPassword = "Synthetic-demo-passphrase-42";

export async function registerPatient(page: Page, label: string) {
  const email = `${label.toLowerCase().replaceAll(/[^a-z0-9]+/g, "-")}-${crypto.randomUUID()}@example.test`;
  await page.goto("/register");
  await page.getByLabel("Full name").fill(label);
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password", { exact: true }).fill(patientPassword);
  await page.getByLabel("Confirm password").fill(patientPassword);
  const registration = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/account/register") && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Create account" }).click();
  const response = await registration;
  expect(response.status()).toBe(201);
  await expect(page).toHaveURL(/\/dashboard$/);
  await expect(page.getByText(`Welcome back, ${label}.`)).toBeVisible();
  return { email, password: patientPassword };
}

export async function signInPatient(page: Page, email: string, password: string) {
  await page.goto("/login");
  await page.getByLabel("Email address").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}
