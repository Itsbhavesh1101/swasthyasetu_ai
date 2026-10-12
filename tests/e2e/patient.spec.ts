import { expect, test } from "@playwright/test";

test("patient shell exposes clear primary and urgent actions", async ({ page }) => {
  await page.goto("/");

  await expect(
    page.getByRole("heading", { level: 1, name: "Your health journey, one step at a time" }),
  ).toBeVisible();
  await expect(page.getByRole("link", { name: /get started/i })).toHaveAttribute("href", "/start");
  await expect(page.getByRole("link", { name: "Urgent help" }).first()).toBeVisible();

  await page.getByRole("link", { name: "Urgent help" }).first().click();
  await expect(
    page.getByRole("heading", { level: 1, name: "Get help now if you feel unsafe" }),
  ).toBeVisible();
  await expect(page.getByText(/verified resources are not configured/i)).toBeVisible();
});

test("keyboard navigation reaches skip link and primary actions without a trap", async ({
  page,
}) => {
  await page.goto("/");

  await page.keyboard.press("Tab");
  const skipLink = page.getByRole("link", { name: "Skip to main content" });
  await expect(skipLink).toBeFocused();
  await expect(skipLink).toHaveCSS("outline-style", "solid");
  await skipLink.press("Enter");
  await expect(page.getByRole("main")).toBeFocused();

  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: /get started/i })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: /urgent help/i }).last()).toBeFocused();
});

test("mobile patient shell remains usable without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await expect(page.getByRole("link", { name: "Urgent help" }).first()).toBeVisible();
  const hasHorizontalOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  );
  expect(hasHorizontalOverflow).toBe(false);
});
