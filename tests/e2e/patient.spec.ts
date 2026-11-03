import { expect, test, type Page } from "@playwright/test";

const approvedCachedPaths = new Set([
  "/offline",
  "/manifest.webmanifest",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
  "/icons/icon-maskable-512.png",
]);

async function activateServiceWorker(page: Page) {
  await page.goto("/");
  await page.evaluate(async () => navigator.serviceWorker.ready);
  if (!(await page.evaluate(() => Boolean(navigator.serviceWorker.controller))))
    await page.reload();
  await expect
    .poll(() => page.evaluate(() => Boolean(navigator.serviceWorker.controller)))
    .toBe(true);
}

test("patient landing focuses on account access before exposing the product shell", async ({
  page,
}) => {
  const response = await page.goto("/");
  expect(response?.headers()).toMatchObject({
    "referrer-policy": "no-referrer",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
  });
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(/welcome back/i);
  await expect(page.getByRole("button", { name: "Sign in" })).toBeVisible();
  await expect(page.getByRole("link", { name: /create account/i })).toHaveAttribute(
    "href",
    "/register",
  );
  await expect(page.getByRole("navigation", { name: "Patient navigation" })).toHaveCount(0);
  await expect(page.getByRole("link", { name: "Urgent help" }).first()).toBeVisible();
});

test("private routes require an account and remain usable on a narrow screen", async ({ page }) => {
  await page.setViewportSize({ width: 320, height: 800 });
  for (const route of [
    "/dashboard",
    "/profile",
    "/history",
    "/timeline",
    "/documents",
    "/guidance",
  ]) {
    await page.goto(route);
    await expect(page.getByRole("heading", { level: 1 })).toHaveCount(1);
    await expect(page.getByRole("link", { name: /sign in/i }).last()).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(
      false,
    );
  }
});

test("service worker persists only approved public shell resources", async ({ page }) => {
  await activateServiceWorker(page);
  const paths = await page.evaluate(async () => {
    const values: string[] = [];
    for (const name of await caches.keys())
      for (const request of await (await caches.open(name)).keys())
        values.push(new URL(request.url).pathname);
    return values;
  });
  expect(paths.length).toBeGreaterThan(0);
  expect(paths.every((path) => approvedCachedPaths.has(path))).toBe(true);
  expect(
    await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length })),
  ).toEqual({
    local: 0,
    session: 0,
  });
});

test("public navigation uses the generic offline fallback without exposing private state", async ({
  context,
  page,
}) => {
  await activateServiceWorker(page);
  await context.setOffline(true);
  try {
    await page.goto("/public-offline-check");
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(/appear to be offline/i);
    await expect(page.getByText(/clinical workflows are unavailable offline/i)).toBeVisible();
  } finally {
    await context.setOffline(false);
  }
});
