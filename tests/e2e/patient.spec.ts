import { expect, test, type Locator, type Page } from "@playwright/test";

const sessionIdCookie = "swasthyasetu_session_id";
const sessionTokenCookie = "swasthyasetu_session_token";
const backendUrl = process.env.SWASTHYASETU_BACKEND_URL ?? "http://127.0.0.1:8000";
const approvedCachedPaths = new Set([
  "/offline",
  "/manifest.webmanifest",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
  "/icons/icon-maskable-512.png",
]);

async function expectHydrated(locator: Locator) {
  await expect
    .poll(() =>
      locator.evaluate((element) =>
        Object.keys(element).some((key) => key.startsWith("__reactProps")),
      ),
    )
    .toBe(true);
}

async function expectTouchTarget(locator: Locator) {
  const box = await locator.boundingBox();
  expect(Boolean(box && box.width >= 44 && box.height >= 44)).toBe(true);
}

async function activateServiceWorker(page: Page) {
  await page.goto("/");
  await page.evaluate(async () => navigator.serviceWorker.ready);
  if (!(await page.evaluate(() => Boolean(navigator.serviceWorker.controller)))) {
    await page.reload();
  }
  await expect
    .poll(() => page.evaluate(() => Boolean(navigator.serviceWorker.controller)))
    .toBe(true);
  const scope = await page.evaluate(async () => (await navigator.serviceWorker.ready).scope);
  expect(new URL(scope).pathname).toBe("/");
}

async function cachedPaths(page: Page): Promise<string[]> {
  return page.evaluate(async () => {
    const paths: string[] = [];
    for (const name of await caches.keys()) {
      const cache = await caches.open(name);
      for (const request of await cache.keys()) paths.push(new URL(request.url).pathname);
    }
    return paths.sort();
  });
}

async function expectPrivateCache(page: Page) {
  await page.evaluate(async () => navigator.serviceWorker.ready);
  const paths = await cachedPaths(page);
  expect(paths.length).toBeGreaterThan(0);
  expect(paths.every((path) => approvedCachedPaths.has(path))).toBe(true);
  expect(paths.some((path) => path.startsWith("/api/"))).toBe(false);
  expect(paths).not.toContain("/consent");
  expect(paths).not.toContain("/encounter");
}

async function completeOnboarding(page: Page) {
  await page.goto("/start");
  await page.getByRole("link", { name: "Continue", exact: true }).press("Enter");
  await expect(page).toHaveURL(/\/language$/);
  await expect(page.getByRole("main")).toBeFocused();
  const english = page.getByRole("radio", { name: /English/i });
  await expectHydrated(english);
  await english.focus();
  await page.keyboard.press("Space");
  await expect(english).toBeChecked();
  const continueToConsent = page.getByRole("button", { name: /continue to consent/i });
  await expect(continueToConsent).toBeEnabled();
  const sessionResponsePromise = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/onboarding/session") && response.request().method() === "POST",
  );
  await continueToConsent.press("Enter");
  const sessionResponse = await sessionResponsePromise;
  expect(sessionResponse.status(), await sessionResponse.text()).toBe(201);
  await expect(page).toHaveURL(/\/consent$/);
  await expect(page.getByRole("main")).toBeFocused();
  const agreement = page.getByRole("checkbox", {
    name: /I understand and agree to this use for this session/i,
  });
  await expectHydrated(agreement);
  await agreement.focus();
  await page.keyboard.press("Space");
  await expect(agreement).toBeChecked();
  await page.getByRole("button", { name: /agree and continue/i }).press("Enter");
  await expect(page).toHaveURL(/\/encounter$/);
  await expect(page.getByRole("main")).toBeFocused();
  await expect(page.getByText(/private session and consent are ready/i)).toBeVisible();
}

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

test("all patient routes preserve landmarks, one h1, urgent help, and narrow reflow", async ({
  page,
}) => {
  const routes = [
    "/",
    "/start",
    "/language",
    "/consent",
    "/encounter",
    "/documents",
    "/results",
    "/urgent-help",
    "/referrals",
    "/offline",
  ];

  for (const width of [320, 390]) {
    await page.setViewportSize({ width, height: width === 320 ? 800 : 844 });
    for (const route of routes) {
      await page.goto(route);
      await expect(page.getByRole("main")).toBeVisible();
      await expect(page.getByRole("heading", { level: 1 })).toHaveCount(1);
      await expect(page.getByRole("link", { name: "Urgent help" }).first()).toBeVisible();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
        ),
      ).toBe(false);
    }
  }
});

test("representative controls keep touch targets and high-contrast identity", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expectTouchTarget(page.getByRole("link", { name: "Urgent help" }).first());
  await expectTouchTarget(page.getByRole("link", { name: /get started/i }));
  await page.getByRole("link", { name: /get started/i }).click();
  await expectTouchTarget(page.getByRole("link", { name: "Continue", exact: true }));

  await page.getByRole("link", { name: "Continue", exact: true }).click();
  const english = page.getByRole("radio", { name: /English/i });
  await expectTouchTarget(english.locator(".."));
  await expectTouchTarget(page.getByRole("button", { name: /continue to consent/i }));
  await english.check();
  await page.getByRole("button", { name: /continue to consent/i }).click();
  const agreement = page.getByRole("checkbox", { name: /I understand and agree/i });
  await expectTouchTarget(agreement.locator(".."));
  await expectTouchTarget(page.getByRole("button", { name: /agree and continue/i }));
  await agreement.check();
  await page.getByRole("button", { name: /agree and continue/i }).click();
  await expectTouchTarget(page.getByRole("button", { name: /end private session/i }));
  await page.goto("/consent");
  await expectTouchTarget(page.getByRole("button", { name: /withdraw this consent/i }));

  await page.emulateMedia({ forcedColors: "active", reducedMotion: "reduce" });
  await page.goto("/");
  const urgent = page.getByRole("link", { name: "Urgent help" }).first();
  await urgent.focus();
  await expect(urgent).toHaveCSS("border-top-style", "solid");
  await expect(urgent).toHaveCSS("outline-style", "solid");
  await expect(page.locator("html")).toHaveCSS("scroll-behavior", "auto");
});

test("manifest and service worker expose only the privacy-safe shell cache", async ({ page }) => {
  const manifestResponse = await page.request.get("/manifest.webmanifest");
  expect(manifestResponse.ok()).toBe(true);
  expect(await manifestResponse.json()).toMatchObject({
    name: "SwasthyaSetu Patient",
    start_url: "/",
    scope: "/",
    display: "standalone",
  });
  const workerResponse = await page.request.get("/sw.js");
  expect(workerResponse.ok()).toBe(true);
  expect(workerResponse.headers()["cache-control"]).toContain("no-cache");
  expect(workerResponse.headers()["service-worker-allowed"]).toBe("/");

  await activateServiceWorker(page);
  await expectPrivateCache(page);
});

test("network-failed navigation shows the generic offline fallback", async ({ context, page }) => {
  await activateServiceWorker(page);
  await context.setOffline(true);
  try {
    await page.goto("/documents?offline-fallback-check=1");
    await expect(
      page.getByRole("heading", { level: 1, name: "You appear to be offline" }),
    ).toBeVisible();
    await expect(page.getByText(/session and consent status cannot be confirmed/i)).toBeVisible();
    await expect(page.getByText(/clinical workflows are unavailable offline/i)).toBeVisible();
  } finally {
    await context.setOffline(false);
  }
});

test("keyboard onboarding uses real session and consent services without browser storage", async ({
  context,
  page,
  request,
}) => {
  await completeOnboarding(page);

  await expect(page.getByText(/clinical intake is not available in this phase/i)).toBeVisible();
  await expect(page.getByRole("link", { name: "Urgent help" }).first()).toBeVisible();

  const cookies = await context.cookies();
  const idCookie = cookies.find(({ name }) => name === sessionIdCookie);
  const tokenCookie = cookies.find(({ name }) => name === sessionTokenCookie);
  expect({
    present: Boolean(idCookie),
    httpOnly: idCookie?.httpOnly,
    sameSite: idCookie?.sameSite,
    expires: idCookie?.expires,
  }).toEqual({ present: true, httpOnly: true, sameSite: "Strict", expires: -1 });
  expect({
    present: Boolean(tokenCookie),
    httpOnly: tokenCookie?.httpOnly,
    sameSite: tokenCookie?.sameSite,
    expires: tokenCookie?.expires,
  }).toEqual({ present: true, httpOnly: true, sameSite: "Strict", expires: -1 });
  expect(Boolean(idCookie?.value)).toBe(true);
  expect(Boolean(tokenCookie?.value)).toBe(true);

  const browserStorage = await page.evaluate(async () => ({
    local: localStorage.length,
    session: sessionStorage.length,
    indexedDatabases: (await indexedDB.databases()).length,
    visibleCookies: document.cookie,
  }));
  expect(browserStorage).toEqual({
    local: 0,
    session: 0,
    indexedDatabases: 0,
    visibleCookies: "",
  });
  await expectPrivateCache(page);

  const sessionResponse = await request.get(
    `${backendUrl}/api/v1/sessions/${idCookie?.value ?? "missing"}`,
    { headers: { Authorization: `Bearer ${tokenCookie?.value ?? "missing"}` } },
  );
  expect(sessionResponse.ok()).toBe(true);
  expect((await sessionResponse.json()).status).toBe("ACTIVE");

  const consentResponse = await request.get(
    `${backendUrl}/api/v1/consents?subject_type=SESSION&subject_id=${idCookie?.value ?? "missing"}&purpose=GENERAL_PRODUCT_USE`,
    { headers: { Authorization: `Bearer ${tokenCookie?.value ?? "missing"}` } },
  );
  expect(consentResponse.ok()).toBe(true);
  const consentRecords = (await consentResponse.json()) as Array<Record<string, unknown>>;
  expect(consentRecords).toHaveLength(1);
  expect(consentRecords[0]).toMatchObject({
    status: "GRANTED",
    purpose: "GENERAL_PRODUCT_USE",
    scope: ["clinical_intake"],
    notice_version: "privacy-v1",
  });
});

test("withdrawing consent removes onboarding readiness without closing the session", async ({
  context,
  page,
  request,
}) => {
  await completeOnboarding(page);
  const cookies = await context.cookies();
  const idCookie = cookies.find(({ name }) => name === sessionIdCookie);
  const tokenCookie = cookies.find(({ name }) => name === sessionTokenCookie);
  await page.goto("/consent");
  await page.getByRole("button", { name: /withdraw this consent/i }).click();
  await expect(page.getByText(/consent has been withdrawn/i)).toBeVisible();

  await page.goto("/encounter");
  await expect(page.getByText(/consent is still needed/i)).toBeVisible();
  await expect(page.getByRole("link", { name: /continue/i })).toHaveAttribute("href", "/consent");

  const sessionResponse = await request.get(
    `${backendUrl}/api/v1/sessions/${idCookie?.value ?? "missing"}`,
    { headers: { Authorization: `Bearer ${tokenCookie?.value ?? "missing"}` } },
  );
  expect(sessionResponse.ok()).toBe(true);
  expect((await sessionResponse.json()).status).toBe("ACTIVE");

  const consentResponse = await request.get(
    `${backendUrl}/api/v1/consents?subject_type=SESSION&subject_id=${idCookie?.value ?? "missing"}&purpose=GENERAL_PRODUCT_USE`,
    { headers: { Authorization: `Bearer ${tokenCookie?.value ?? "missing"}` } },
  );
  expect(consentResponse.ok()).toBe(true);
  const consentRecords = (await consentResponse.json()) as Array<Record<string, unknown>>;
  expect(consentRecords).not.toHaveLength(0);
  expect(consentRecords.every(({ status }) => status !== "GRANTED")).toBe(true);
  expect(consentRecords.some(({ status }) => status === "REVOKED")).toBe(true);
});

test("ending a private session closes the backend session and clears cookies", async ({
  context,
  page,
  request,
}) => {
  await completeOnboarding(page);
  const cookies = await context.cookies();
  const idCookie = cookies.find(({ name }) => name === sessionIdCookie);
  const tokenCookie = cookies.find(({ name }) => name === sessionTokenCookie);

  const endSession = page.getByRole("button", { name: /end private session/i });
  await endSession.focus();
  await expect(endSession).toHaveCSS("outline-style", "solid");
  await endSession.press("Enter");
  await expect(page).toHaveURL(/\/language$/);
  const remainingCookies = await context.cookies();
  expect(remainingCookies.some(({ name }) => name === sessionIdCookie)).toBe(false);
  expect(remainingCookies.some(({ name }) => name === sessionTokenCookie)).toBe(false);

  const sessionResponse = await request.get(
    `${backendUrl}/api/v1/sessions/${idCookie?.value ?? "missing"}`,
    { headers: { Authorization: `Bearer ${tokenCookie?.value ?? "missing"}` } },
  );
  expect(sessionResponse.status()).toBe(409);
  expect((await sessionResponse.json()).error.code).toBe("INVALID_STATE_TRANSITION");

  const frontendStatus = await page.request.get("/api/onboarding/session");
  expect(await frontendStatus.json()).toEqual({ state: "NO_SESSION" });
});
