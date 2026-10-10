import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  reporter: "html",
  use: {
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "patient-web",
      testMatch: /patient\.spec\.ts/,
      use: { ...devices["Desktop Chrome"], baseURL: "http://127.0.0.1:3100" },
    },
    {
      name: "clinician-web",
      testMatch: /clinician\.spec\.ts/,
      use: { ...devices["Desktop Chrome"], baseURL: "http://127.0.0.1:3101" },
    },
    {
      name: "admin-web",
      testMatch: /admin\.spec\.ts/,
      use: { ...devices["Desktop Chrome"], baseURL: "http://127.0.0.1:3102" },
    },
  ],
  webServer: [
    {
      command: "pnpm --filter @swasthyasetu/patient-web dev --port 3100",
      port: 3100,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: "pnpm --filter @swasthyasetu/clinician-web dev --port 3101",
      port: 3101,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: "pnpm --filter @swasthyasetu/admin-web dev --port 3102",
      port: 3102,
      reuseExistingServer: !process.env.CI,
    },
  ],
});
