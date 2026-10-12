import { expect, test, type Locator, type Page } from "@playwright/test";

const sessionIdCookie = "swasthyasetu_session_id";
const sessionTokenCookie = "swasthyasetu_session_token";
const backendUrl = process.env.SWASTHYASETU_BACKEND_URL ?? "http://127.0.0.1:8000";

async function expectHydrated(locator: Locator) {
  await expect
    .poll(() =>
      locator.evaluate((element) =>
        Object.keys(element).some((key) => key.startsWith("__reactProps")),
      ),
    )
    .toBe(true);
}

async function completeOnboarding(page: Page) {
  await page.goto("/start");
  await page.getByRole("link", { name: "Continue", exact: true }).press("Enter");
  await expect(page).toHaveURL(/\/language$/);
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
  const agreement = page.getByRole("checkbox", {
    name: /I understand and agree to this use for this session/i,
  });
  await expectHydrated(agreement);
  await agreement.focus();
  await page.keyboard.press("Space");
  await expect(agreement).toBeChecked();
  await page.getByRole("button", { name: /agree and continue/i }).press("Enter");
  await expect(page).toHaveURL(/\/encounter$/);
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
  expect(idCookie?.value).toBeTruthy();
  expect(tokenCookie?.value).toBeTruthy();

  const browserStorage = await page.evaluate(async () => ({
    local: localStorage.length,
    session: sessionStorage.length,
    indexedDatabases: (await indexedDB.databases()).length,
    cacheEntries: ("caches" in window ? await caches.keys() : []).length,
    visibleCookies: document.cookie,
  }));
  expect(browserStorage).toEqual({
    local: 0,
    session: 0,
    indexedDatabases: 0,
    cacheEntries: 0,
    visibleCookies: "",
  });

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

  await page.getByRole("button", { name: /end private session/i }).click();
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
