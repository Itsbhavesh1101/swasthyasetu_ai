import { expect, test } from "@playwright/test";

test("clinician synthetic document receipt is reachable and non-authoritative", async ({
  page,
}) => {
  const response = await page.goto("/");
  expect(response?.headers()).toMatchObject({
    "content-security-policy": expect.stringContaining("frame-ancestors 'none'"),
    "permissions-policy": expect.stringContaining("camera=()"),
    "referrer-policy": "no-referrer",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
  });
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("SwasthyaSetu Clinician");
  await expect(
    page.getByRole("heading", { name: "Synthetic document review receipt" }),
  ).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText(/not patient data/i)).toBeVisible();
  await expect(page.getByText("UNCONFIRMED", { exact: true })).toBeVisible();
  await expect(page.getByText("NOT VERIFIED", { exact: true })).toBeVisible();
  await expect(page.getByText(/review controls remain disabled/i)).toBeVisible();
  await expect(page.getByRole("button")).toHaveCount(0);

  expect(
    await page.evaluate(() => ({
      local: localStorage.length,
      session: sessionStorage.length,
      visibleCookies: document.cookie,
    })),
  ).toEqual({ local: 0, session: 0, visibleCookies: "" });
});
