import { expect, test } from "@playwright/test";

test("clinician foundation is reachable", async ({ page }) => {
  const response = await page.goto("/");
  expect(response?.headers()).toMatchObject({
    "content-security-policy": expect.stringContaining("frame-ancestors 'none'"),
    "permissions-policy": expect.stringContaining("camera=()"),
    "referrer-policy": "no-referrer",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
  });
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("SwasthyaSetu Clinician");
});
