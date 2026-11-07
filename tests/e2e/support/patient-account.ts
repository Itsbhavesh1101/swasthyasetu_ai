import { expect, type Page } from "@playwright/test";

export const patientPassword = "Synthetic-demo-passphrase-42";

export async function registerPatient(page: Page, label: string) {
  const email = `${label.toLowerCase().replaceAll(/[^a-z0-9]+/g, "-")}-${crypto.randomUUID()}@example.test`;
  await page.goto("/register");
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
  await expect(page).toHaveURL(/\/profile\?setup=1$/);
  await page.getByLabel("Full name").fill(label);
  await page.getByRole("button", { name: "Next", exact: true }).click();
  await page.getByLabel("Preferred language").selectOption("en");
  await page.getByRole("button", { name: "Next", exact: true }).click();
  await page.getByLabel("Date of birth").fill("1998-04-12");
  await page.getByRole("button", { name: "Next", exact: true }).click();
  await page.getByLabel("Sex recorded for healthcare").selectOption("female");
  await page.getByRole("button", { name: "Next", exact: true }).click();
  await page.getByLabel("Height (cm)").fill("165");
  await page.getByRole("button", { name: "Next", exact: true }).click();
  await page.getByLabel("Weight (kg)").fill("60");
  await page.getByRole("button", { name: "Next", exact: true }).click();
  await page.getByLabel("Mobile number").fill("+919876543210");
  await page.getByRole("button", { name: "Next", exact: true }).click();
  await page.getByLabel("Blood group").selectOption("UNKNOWN");
  await page.getByRole("button", { name: "Next", exact: true }).click();
  await page.getByLabel("Aadhaar demonstration reference").fill("DEMO-AADHAAR-2301");
  await page.getByRole("button", { name: "Next", exact: true }).click();
  await page.getByRole("button", { name: "Skip" }).click();
  await page.getByRole("button", { name: "Skip" }).click();
  await page.getByRole("button", { name: "Skip" }).click();
  await page.getByRole("button", { name: "Save and open dashboard" }).click();
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
