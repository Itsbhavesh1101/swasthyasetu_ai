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
  const response = await page.goto("/");
  expect(response?.headers()).toMatchObject({
    "content-security-policy": expect.stringContaining("frame-ancestors 'none'"),
    "permissions-policy": expect.stringContaining("camera=()"),
    "referrer-policy": "no-referrer",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
  });

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

  await expect(page.getByRole("button", { name: /start intake/i })).toBeVisible();
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

test("keyboard-only structured intake saves, reviews, completes, and exits privately", async ({
  page,
}) => {
  test.slow();
  await completeOnboarding(page);
  const start = page.getByRole("button", { name: /start intake/i });
  await start.focus();
  await expect(start).toBeFocused();
  await start.press("Enter");
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+$/);
  await expect(page).toHaveTitle("Structured intake | SwasthyaSetu");
  const questionHeading = page.getByRole("heading", { level: 1 });
  await expect(questionHeading).toContainText(/what would you like to share/i);
  await expect(questionHeading).toBeFocused();

  await page.keyboard.press("Tab");
  const answer = page.getByLabel(/what would you like to share/i);
  await expect(answer).toBeFocused();
  await page.keyboard.type("Synthetic browser journey concern");
  await page.keyboard.press("Tab");
  const save = page.getByRole("button", { name: /save and continue/i });
  await expect(save).toBeFocused();
  await save.press("Enter");

  await expect(page).toHaveURL(/\/review$/, { timeout: 15_000 });
  await expect(page).toHaveTitle("Review intake draft | SwasthyaSetu");
  const reviewHeading = page.getByRole("heading", { level: 1 });
  await expect(reviewHeading).toBeFocused();
  await expect(page.getByText("Synthetic browser journey concern")).toBeVisible();
  await expect(
    page.getByText(/not a diagnosis, treatment plan, urgency assessment/i),
  ).toBeVisible();

  await page.reload();
  await expect(reviewHeading).toBeFocused();
  await expect(page.getByText("Synthetic browser journey concern")).toBeVisible();
  await page.keyboard.press("Tab");
  const reviewOrChange = page.getByRole("link", { name: /review or change/i });
  await expect(reviewOrChange).toBeFocused();
  await reviewOrChange.press("Enter");
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+$/);
  await expect(page).toHaveTitle("Structured intake | SwasthyaSetu");
  await expect(page.getByRole("heading", { level: 1 })).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(answer).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(save).toBeFocused();
  await page.keyboard.press("Tab");
  const returnToReview = page.getByRole("link", { name: /review draft/i });
  await expect(returnToReview).toBeFocused();
  await returnToReview.press("Enter");
  await expect(page).toHaveURL(/\/review$/);
  await expect(reviewHeading).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(reviewOrChange).toBeFocused();
  await page.keyboard.press("Tab");
  const complete = page.getByRole("button", { name: /complete draft/i });
  await expect(complete).toBeFocused();
  await complete.press("Enter");
  const completedHeading = page.getByRole("heading", {
    level: 1,
    name: /your intake draft has been saved/i,
  });
  await expect(completedHeading).toBeFocused();
  await expect(page.getByText(/not a diagnosis/i)).toBeVisible();

  await page.keyboard.press("Tab");
  const syntheticPreview = page.getByRole("link", { name: /open offline synthetic preview/i });
  await expect(syntheticPreview).toBeFocused();
  await page.keyboard.press("Tab");
  const endSession = page.getByRole("button", { name: /end private session/i });
  await expect(endSession).toBeFocused();
  await endSession.press("Enter");
  await expect(page).toHaveURL(/\/language$/);
  await expect(page.getByRole("main")).toBeFocused();
});

test("completed exact fixture runs the offline synthetic P8-P10 preview", async ({ page }) => {
  test.slow();
  await completeOnboarding(page);
  await page.getByRole("button", { name: /start intake/i }).click();
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+$/);

  const answer = page.getByLabel(/what would you like to share/i);
  await answer.fill("I report synthetic pain");
  await page.getByRole("button", { name: /save and continue/i }).click();
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+\/review$/, { timeout: 15_000 });
  await page.getByRole("button", { name: /complete draft/i }).click();
  await expect(
    page.getByRole("heading", { name: /your intake draft has been saved/i }),
  ).toBeVisible();

  await page.getByRole("link", { name: /open offline synthetic preview/i }).click();
  await expect(page).toHaveURL(/\/results\/[0-9a-f-]+$/);
  await expect(page.getByRole("heading", { name: "Synthetic result preview" })).toBeVisible();
  await expect(page.getByText(/engineering test data only/i)).toBeVisible();
  await expect(page.getByText("Synthetic pain", { exact: true })).toBeVisible();
  await expect(page.getByText("AI extracted, unconfirmed", { exact: true })).toBeVisible();
  await expect(page.getByText("ROUTINE_CARE", { exact: true })).toBeVisible();
  await expect(page.getByText(/clinician review required/i)).toBeVisible();

  expect(
    await page.evaluate(() => ({
      local: localStorage.length,
      session: sessionStorage.length,
      visibleCookies: document.cookie,
    })),
  ).toEqual({ local: 0, session: 0, visibleCookies: "" });
});

test("a failed intake save keeps unsent input and succeeds only after an explicit retry", async ({
  page,
}) => {
  test.slow();
  const unsentAnswer = "Synthetic retryable save concern";
  const answerRoute = "**/api/intake/*/answers";
  await page.setViewportSize({ width: 320, height: 800 });
  await completeOnboarding(page);
  const startIntake = page.getByRole("button", { name: /start intake/i });
  await startIntake.focus();
  await startIntake.press("Enter");
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+$/);
  const intakePath = new URL(page.url()).pathname;
  const answer = page.getByLabel(/what would you like to share/i);
  await answer.focus();
  await page.keyboard.type(unsentAnswer);

  let attemptedSaves = 0;
  await page.route(answerRoute, async (route) => {
    attemptedSaves += 1;
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      headers: { "Cache-Control": "no-store" },
      body: JSON.stringify({
        error: {
          code: "BACKEND_UNAVAILABLE",
          message: "The intake request could not be completed.",
        },
      }),
    });
  });
  const save = page.getByRole("button", { name: /save and continue/i });
  await save.focus();
  await save.press("Enter");

  const answerError = page.locator("#answer-error");
  await expect(answerError).toHaveAttribute("role", "alert");
  await expect(answerError).toHaveText("The intake request could not be completed.");
  await expect(page.getByRole("heading", { level: 1 })).toBeFocused();
  await expect(answer).toHaveAttribute("aria-invalid", "true");
  await expect(answer).toHaveAttribute("aria-describedby", "question-help answer-error");
  await expect(answer).toHaveValue(unsentAnswer);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
    ),
  ).toBe(false);
  expect(attemptedSaves).toBe(1);
  const unchanged = await page.request.get(`/api${intakePath}`);
  expect(unchanged.ok(), await unchanged.text()).toBe(true);
  expect((await unchanged.json()).answers).toHaveLength(0);

  await page.unroute(answerRoute);
  await save.focus();
  await save.press("Enter");
  await expect(page).toHaveURL(/\/review$/, { timeout: 15_000 });
  await expect(page.getByText(unsentAnswer)).toBeVisible();
  const saved = await page.request.get(`/api${intakePath}`);
  expect(saved.ok(), await saved.text()).toBe(true);
  const savedState = await saved.json();
  expect(savedState.answers).toHaveLength(1);
  expect(savedState.answers[0].value).toBe(unsentAnswer);
});

test("an offline answer stays memory-only and is never replayed after reconnection", async ({
  context,
  page,
}) => {
  test.slow();
  const unsentAnswer = "Synthetic offline answer that must not be queued";
  await activateServiceWorker(page);
  await completeOnboarding(page);
  await page.getByRole("button", { name: /start intake/i }).click();
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+$/);
  const intakePath = new URL(page.url()).pathname;
  await page.getByLabel(/what would you like to share/i).fill(unsentAnswer);
  let answerRequests = 0;
  page.on("request", (request) => {
    if (request.url().endsWith("/answers") && request.method() === "POST") answerRequests += 1;
  });

  await context.setOffline(true);
  try {
    await page.getByRole("button", { name: /save and continue/i }).click();
    await expect(page.locator("#answer-error")).toHaveText(
      "The request could not be confirmed. Refresh before trying again.",
    );
    await expect(page.getByLabel(/what would you like to share/i)).toHaveValue(unsentAnswer);
    expect(answerRequests).toBe(1);
    await expectPrivateCache(page);
    expect(
      await page.evaluate(async () => ({
        local: localStorage.length,
        session: sessionStorage.length,
        indexedDatabases: (await indexedDB.databases()).length,
      })),
    ).toEqual({ local: 0, session: 0, indexedDatabases: 0 });
  } finally {
    await context.setOffline(false);
  }

  const unchanged = await page.request.get(`/api${intakePath}`);
  expect(unchanged.ok(), await unchanged.text()).toBe(true);
  expect((await unchanged.json()).answers).toHaveLength(0);
  expect(answerRequests).toBe(1);
  expect(
    await page.evaluate(async () => {
      const registration = await navigator.serviceWorker.ready;
      const sync = Reflect.get(registration, "sync") as
        { getTags(): Promise<string[]> } | undefined;
      if (!sync) return { state: "UNAVAILABLE", tags: [] };
      try {
        return { state: "AVAILABLE", tags: await sync.getTags() };
      } catch {
        return { state: "DISABLED", tags: [] };
      }
    }),
  ).toMatchObject({ tags: [] });
  await expect(page.getByLabel(/what would you like to share/i)).toHaveValue(unsentAnswer);

  await page.getByRole("button", { name: /save and continue/i }).click();
  await expect(page).toHaveURL(/\/review$/, { timeout: 15_000 });
  const saved = await page.request.get(`/api${intakePath}`);
  expect(saved.ok(), await saved.text()).toBe(true);
  const savedState = await saved.json();
  expect(savedState.answers).toHaveLength(1);
  expect(savedState.answers[0].value).toBe(unsentAnswer);
  expect(answerRequests).toBe(2);
});

test("an ambiguous intake response refetches saved state without replaying the mutation", async ({
  page,
}) => {
  test.slow();
  const savedAnswer = "Synthetic ambiguous-response concern";
  const answerRoute = "**/api/intake/*/answers";
  await completeOnboarding(page);
  await page.getByRole("button", { name: /start intake/i }).click();
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+$/);
  const intakePath = new URL(page.url()).pathname;
  await page.getByLabel(/what would you like to share/i).fill(savedAnswer);

  let attemptedSaves = 0;
  await page.route(answerRoute, async (route) => {
    attemptedSaves += 1;
    const backendResponse = await route.fetch();
    expect(backendResponse.ok(), await backendResponse.text()).toBe(true);
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      headers: { "Cache-Control": "no-store" },
      body: JSON.stringify({
        error: {
          code: "REQUEST_FAILED",
          message: "The request could not be confirmed. Refresh before trying again.",
        },
      }),
    });
  });
  await page.getByRole("button", { name: /save and continue/i }).click();

  await expect(page.locator("#answer-error")).toHaveText(
    "The request could not be confirmed. Refresh before trying again.",
  );
  expect(attemptedSaves).toBe(1);
  const saved = await page.request.get(`/api${intakePath}`);
  expect(saved.ok(), await saved.text()).toBe(true);
  const savedState = await saved.json();
  expect(savedState.answers).toHaveLength(1);
  expect(savedState.answers[0].value).toBe(savedAnswer);

  await page.unroute(answerRoute);
  await page.getByRole("link", { name: /review draft/i }).click();
  await expect(page).toHaveURL(/\/review$/);
  await expect(page.getByText(savedAnswer)).toBeVisible();
  expect(attemptedSaves).toBe(1);
});

test("a stale intake version refetches authoritative state and requires review", async ({
  page,
}) => {
  test.slow();
  const acceptedAnswer = "Synthetic concurrently accepted concern";
  const staleAnswer = "Synthetic stale concern that must not be replayed";
  await completeOnboarding(page);
  await page.getByRole("button", { name: /start intake/i }).click();
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+$/);
  const intakePath = new URL(page.url()).pathname;
  const stalePage = await page.context().newPage();

  try {
    await stalePage.goto(intakePath);
    await stalePage.getByLabel(/what would you like to share/i).fill(staleAnswer);

    await page.getByLabel(/what would you like to share/i).fill(acceptedAnswer);
    await page.getByRole("button", { name: /save and continue/i }).click();
    await expect(page).toHaveURL(/\/review$/, { timeout: 15_000 });
    await expect(page.getByText(acceptedAnswer)).toBeVisible();

    const conflictPromise = stalePage.waitForResponse(
      (response) => response.url().endsWith("/answers") && response.request().method() === "POST",
    );
    await stalePage.getByRole("button", { name: /save and continue/i }).click();
    const conflict = await conflictPromise;
    const conflictBody = await conflict.text();
    expect(conflict.status()).toBe(409);
    expect(conflict.headers()["cache-control"]).toContain("no-store");
    expect(JSON.parse(conflictBody)).toMatchObject({ error: { code: "RESOURCE_CONFLICT" } });
    expect(conflictBody).not.toContain(acceptedAnswer);
    expect(conflictBody).not.toContain(staleAnswer);

    await expect(stalePage.locator("#answer-error")).toHaveText(
      "This intake changed. Refresh and review the latest saved draft.",
    );
    await expect(
      stalePage.getByRole("heading", { level: 2, name: "Review the latest saved draft" }),
    ).toBeVisible();
    await expect(stalePage.locator("textarea")).toHaveCount(0);
    await expect(stalePage.getByRole("button", { name: /save and continue/i })).toHaveCount(0);

    const authoritative = await stalePage.request.get(`/api${intakePath}`);
    expect(authoritative.ok(), await authoritative.text()).toBe(true);
    const authoritativeState = await authoritative.json();
    expect(authoritativeState.version).toBe(2);
    expect(authoritativeState.answers).toHaveLength(1);
    expect(authoritativeState.answers[0].value).toBe(acceptedAnswer);
    expect(JSON.stringify(authoritativeState)).not.toContain(staleAnswer);

    await stalePage.getByRole("link", { name: "Review latest draft" }).click();
    await expect(stalePage).toHaveURL(/\/review$/);
    await expect(stalePage.getByText(acceptedAnswer)).toBeVisible();
    await expect(stalePage.getByText(staleAnswer)).toHaveCount(0);
  } finally {
    await stalePage.close();
  }
});

test("concurrent session closure removes loaded intake state and browser credentials", async ({
  context,
  page,
  request,
}) => {
  test.slow();
  const unsentAnswer = "Synthetic unsent value removed after session closure";
  await completeOnboarding(page);
  await page.getByRole("button", { name: /start intake/i }).click();
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+$/);
  const intakePath = new URL(page.url()).pathname;
  const intakeId = intakePath.split("/").at(-1);
  await page.getByLabel(/what would you like to share/i).fill(unsentAnswer);

  const cookies = await context.cookies();
  const sessionId = cookies.find(({ name }) => name === sessionIdCookie)?.value;
  const sessionToken = cookies.find(({ name }) => name === sessionTokenCookie)?.value;
  expect(sessionId).toBeTruthy();
  expect(sessionToken).toBeTruthy();
  const closed = await request.post(`${backendUrl}/api/v1/sessions/${sessionId}/close`, {
    headers: { Authorization: `Bearer ${sessionToken}` },
  });
  expect(closed.status(), await closed.text()).toBe(200);

  const deniedPromise = page.waitForResponse(
    (response) => response.url().endsWith("/answers") && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: /save and continue/i }).click();
  const denied = await deniedPromise;
  const deniedBody = await denied.text();
  expect(denied.status()).toBe(401);
  expect(denied.headers()["cache-control"]).toContain("no-store");
  expect(JSON.parse(deniedBody)).toEqual({
    error: { code: "SESSION_UNAVAILABLE", message: "Start a private session first." },
  });
  expect(deniedBody).not.toContain(unsentAnswer);

  await expect(page).toHaveURL(/\/language$/);
  await expect(page.getByText(unsentAnswer)).toHaveCount(0);
  const remainingCookies = await context.cookies();
  expect(remainingCookies.some(({ name }) => name === sessionIdCookie)).toBe(false);
  expect(remainingCookies.some(({ name }) => name === sessionTokenCookie)).toBe(false);
  expect(
    await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length })),
  ).toEqual({ local: 0, session: 0 });

  const backendDenied = await request.get(`${backendUrl}/api/v1/intakes/${intakeId}`, {
    headers: { Authorization: `Bearer ${sessionToken}` },
  });
  const backendDeniedBody = await backendDenied.text();
  expect(backendDenied.status()).toBe(409);
  expect(JSON.parse(backendDeniedBody)).toMatchObject({
    error: { code: "INVALID_STATE_TRANSITION" },
  });
  expect(backendDeniedBody).not.toContain(unsentAnswer);
});

test("concurrent consent withdrawal removes loaded intake state but preserves the session", async ({
  context,
  page,
  request,
}) => {
  test.slow();
  const unsentAnswer = "Synthetic unsent value removed after consent withdrawal";
  await completeOnboarding(page);
  await page.getByRole("button", { name: /start intake/i }).click();
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+$/);
  const intakePath = new URL(page.url()).pathname;
  const intakeId = intakePath.split("/").at(-1);
  await page.getByLabel(/what would you like to share/i).fill(unsentAnswer);

  const cookies = await context.cookies();
  const sessionId = cookies.find(({ name }) => name === sessionIdCookie)?.value;
  const sessionToken = cookies.find(({ name }) => name === sessionTokenCookie)?.value;
  expect(sessionId).toBeTruthy();
  expect(sessionToken).toBeTruthy();

  const consentPage = await context.newPage();
  await consentPage.goto("/consent");
  await consentPage.getByRole("button", { name: /withdraw this consent/i }).click();
  await expect(consentPage.getByText(/consent has been withdrawn/i)).toBeVisible();
  await consentPage.close();

  const deniedPromise = page.waitForResponse(
    (response) => response.url().endsWith("/answers") && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: /save and continue/i }).click();
  const denied = await deniedPromise;
  const deniedBody = await denied.text();
  expect(denied.status()).toBe(403);
  expect(denied.headers()["cache-control"]).toContain("no-store");
  expect(JSON.parse(deniedBody)).toEqual({
    error: {
      code: "CONSENT_REQUIRED",
      message: "Consent is required before continuing this intake.",
    },
  });
  expect(deniedBody).not.toContain(unsentAnswer);

  await expect(page).toHaveURL(/\/consent$/);
  await expect(page.getByText(unsentAnswer)).toHaveCount(0);
  await expect(page.getByText(/consent has been withdrawn/i)).toBeVisible();
  const remainingCookies = await context.cookies();
  expect(remainingCookies.some(({ name }) => name === sessionIdCookie)).toBe(true);
  expect(remainingCookies.some(({ name }) => name === sessionTokenCookie)).toBe(true);
  expect(
    await page.evaluate(() => ({ local: localStorage.length, session: sessionStorage.length })),
  ).toEqual({ local: 0, session: 0 });

  const sessionResponse = await request.get(`${backendUrl}/api/v1/sessions/${sessionId}`, {
    headers: { Authorization: `Bearer ${sessionToken}` },
  });
  expect(sessionResponse.ok(), await sessionResponse.text()).toBe(true);
  expect((await sessionResponse.json()).status).toBe("ACTIVE");

  const backendDenied = await request.get(`${backendUrl}/api/v1/intakes/${intakeId}`, {
    headers: { Authorization: `Bearer ${sessionToken}` },
  });
  const backendDeniedBody = await backendDenied.text();
  expect(backendDenied.status()).toBe(403);
  expect(JSON.parse(backendDeniedBody)).toMatchObject({ error: { code: "CONSENT_REQUIRED" } });
  expect(backendDeniedBody).not.toContain(unsentAnswer);
});

test("withdrawing consent blocks an active intake without ending the session", async ({ page }) => {
  test.slow();
  const protectedDraft = "Synthetic consent-withdrawal draft";
  await completeOnboarding(page);
  await page.getByRole("button", { name: /start intake/i }).click();
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+$/);
  const intakePath = new URL(page.url()).pathname;
  await page.getByLabel(/what would you like to share/i).fill(protectedDraft);
  await page.getByRole("button", { name: /save and continue/i }).click();
  await expect(page).toHaveURL(/\/review$/, { timeout: 15_000 });
  await expect(page.getByText(protectedDraft)).toBeVisible();

  await page.goto("/consent");
  await page.getByRole("button", { name: /withdraw this consent/i }).click();
  await expect(page.getByText(/consent has been withdrawn/i)).toBeVisible();

  const denied = await page.request.get(`/api${intakePath}`);
  const deniedBody = await denied.text();
  expect(denied.status()).toBe(403);
  expect(JSON.parse(deniedBody)).toMatchObject({ error: { code: "CONSENT_REQUIRED" } });
  expect(deniedBody).not.toContain(protectedDraft);

  await page.goto(intakePath);
  await expect(page).toHaveURL(/\/consent$/);
  await expect(page.getByRole("heading", { level: 1, name: "Review consent" })).toBeVisible();
  await expect(page.getByText(/consent has been withdrawn/i)).toBeVisible();
  await expect(page.getByText(protectedDraft)).toHaveCount(0);

  await page.goto("/encounter");
  await expect(page.getByText(/consent is still needed/i)).toBeVisible();
  await expect(page.getByRole("link", { name: /continue/i })).toHaveAttribute("href", "/consent");
});

test("a second private session cannot discover or read another session intake", async ({
  browser,
  page,
}) => {
  test.slow();
  const protectedDraft = "Synthetic owner-only draft";
  await completeOnboarding(page);
  await page.getByRole("button", { name: /start intake/i }).click();
  await expect(page).toHaveURL(/\/intake\/[0-9a-f-]+$/);
  const intakePath = new URL(page.url()).pathname;
  const intakeId = intakePath.split("/").at(-1);
  expect(intakeId).toBeTruthy();
  await page.getByLabel(/what would you like to share/i).fill(protectedDraft);
  await page.getByRole("button", { name: /save and continue/i }).click();
  await expect(page).toHaveURL(/\/review$/, { timeout: 15_000 });
  await expect(page.getByText(protectedDraft)).toBeVisible();

  const secondContext = await browser.newContext({ baseURL: new URL(page.url()).origin });
  try {
    const secondPage = await secondContext.newPage();
    await completeOnboarding(secondPage);

    const attackerCookies = await secondContext.cookies();
    const attackerToken = attackerCookies.find(({ name }) => name === sessionTokenCookie)?.value;
    expect(attackerToken).toBeTruthy();
    const attackerHeaders = { Authorization: `Bearer ${attackerToken}` };
    const unknownIntakeId = "11111111-1111-4111-8111-111111111111";
    const existingDirect = await secondPage.request.get(
      `${backendUrl}/api/v1/intakes/${intakeId}`,
      { headers: attackerHeaders },
    );
    const unknownDirect = await secondPage.request.get(
      `${backendUrl}/api/v1/intakes/${unknownIntakeId}`,
      { headers: attackerHeaders },
    );
    for (const response of [existingDirect, unknownDirect]) {
      const body = await response.text();
      expect(response.status()).toBe(401);
      expect(JSON.parse(body)).toMatchObject({ error: { code: "AUTHENTICATION_REQUIRED" } });
      expect(body).not.toContain(protectedDraft);
      expect(body).not.toContain(intakeId ?? "unreachable");
    }

    const existingDemo = await secondPage.request.get(
      `/api/engineering-demo/intakes/${intakeId}/result`,
    );
    const unknownDemo = await secondPage.request.get(
      `/api/engineering-demo/intakes/${unknownIntakeId}/result`,
    );
    for (const response of [existingDemo, unknownDemo]) {
      const body = await response.text();
      expect(response.status()).toBe(401);
      expect(JSON.parse(body)).toEqual({
        error: { code: "RESULT_UNAVAILABLE", message: "The synthetic preview is unavailable." },
      });
      expect(body).not.toContain(protectedDraft);
      expect(body).not.toContain(intakeId ?? "unreachable");
    }

    const denied = await secondPage.request.get(`/api${intakePath}`);
    const deniedBody = await denied.text();
    expect(denied.status()).toBe(401);
    expect(JSON.parse(deniedBody)).toMatchObject({
      error: { code: "AUTHENTICATION_REQUIRED" },
    });
    expect(deniedBody).not.toContain(protectedDraft);

    await secondPage.goto(intakePath);
    await expect(
      secondPage.getByRole("heading", { level: 1, name: "Intake unavailable" }),
    ).toBeVisible();
    await expect(secondPage.getByText(/start a private session first/i)).toBeVisible();
    await expect(secondPage.getByText(protectedDraft)).toHaveCount(0);

    await page.reload();
    await expect(page.getByText(protectedDraft)).toBeVisible();
  } finally {
    await secondContext.close();
  }
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
