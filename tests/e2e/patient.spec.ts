import { expect, test } from "@playwright/test";

test("patient foundation is reachable", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("SwasthyaSetu Patient");
});
