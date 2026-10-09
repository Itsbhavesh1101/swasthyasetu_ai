import { expect, test } from "@playwright/test";

test("admin foundation is reachable", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("SwasthyaSetu Admin");
});
