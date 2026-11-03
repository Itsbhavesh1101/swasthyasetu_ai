import { expect, test } from "@playwright/test";

import { registerPatient } from "./support/patient-account";

test("patient document vault validates, downloads, removes, and remains private", async ({
  page,
}) => {
  await registerPatient(page, "Synthetic Document Patient");
  await page.goto("/documents");

  const chooser = page.getByLabel("Choose document");
  await chooser.setInputFiles({
    name: "synthetic-report.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("%PDF-1.4\n1 0 obj\n<<>>\nendobj\n%%EOF\n"),
  });
  await page.getByRole("button", { name: "Upload document" }).click();
  await expect(page.getByText("Document uploaded securely.")).toBeVisible();
  await expect(page.getByText("synthetic-report.pdf")).toBeVisible();

  const download = page.waitForEvent("download");
  await page.getByRole("link", { name: "Download" }).click();
  expect((await download).suggestedFilename()).toBe("synthetic-report.pdf");

  await chooser.setInputFiles({
    name: "invalid.pdf",
    mimeType: "application/pdf",
    buffer: Buffer.from("not a pdf"),
  });
  await page.getByRole("button", { name: "Upload document" }).click();
  await expect(page.getByText(/choose a valid PDF/i)).toBeVisible();

  page.on("dialog", (dialog) => dialog.accept());
  await page.getByRole("button", { name: "Delete" }).click();
  await expect(page.getByText("Document deleted.")).toBeVisible();
  await expect(page.getByText("synthetic-report.pdf")).toHaveCount(0);

  await page.getByRole("button", { name: /sign out/i }).click();
  await expect(page).toHaveURL(/\/login$/);
  await page.goto("/documents");
  await expect(
    page.getByRole("heading", { name: /sign in to use your document vault/i }),
  ).toBeVisible();
  expect(await page.evaluate(() => document.cookie)).toBe("");
});

test("external-AI consent gates deterministic grounded guidance and degraded mode", async ({
  page,
}) => {
  await registerPatient(page, "Synthetic Guidance Patient");
  await page.goto("/guidance");
  await expect(page.getByText(/exact question.*sent to Google/i)).toBeVisible();
  await page.getByRole("button", { name: "I agree and continue" }).click();

  await page.getByLabel("Your question").fill("How can I support hydration?");
  await page.getByRole("button", { name: "Get grounded information" }).click();
  await expect(page.getByRole("heading", { name: "Grounded wellness information" })).toBeVisible();
  await expect(
    page.getByText("Gentle hydration habits may support general wellbeing."),
  ).toBeVisible();
  await expect(page.getByRole("link", { name: "World Health Organization" })).toHaveAttribute(
    "href",
    "https://who.int",
  );

  await page.getByLabel("Your question").fill("Synthetic unavailable general wellness question");
  await page.getByRole("button", { name: "Get grounded information" }).click();
  await expect(page.getByRole("heading", { name: /guidance is not available/i })).toBeVisible();

  await page.getByRole("button", { name: "Withdraw permission" }).click();
  await expect(page.getByRole("button", { name: "I agree and continue" })).toBeVisible();
  await expect(page.getByLabel("Your question")).toHaveCount(0);
});
