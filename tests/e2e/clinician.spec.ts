import { expect, test } from "@playwright/test";

test("clinician foundation is reachable", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("SwasthyaSetu Clinician");
});
