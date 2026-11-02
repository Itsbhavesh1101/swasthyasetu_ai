import { defineConfig, devices } from "@playwright/test";

const patientPort = Number(process.env.SWASTHYASETU_E2E_PATIENT_PORT ?? "3100");
const clinicianPort = Number(process.env.SWASTHYASETU_E2E_CLINICIAN_PORT ?? "3101");
const adminPort = Number(process.env.SWASTHYASETU_E2E_ADMIN_PORT ?? "3102");

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
      use: { ...devices["Desktop Chrome"], baseURL: `http://127.0.0.1:${patientPort}` },
    },
    {
      name: "clinician-web",
      testMatch: /clinician\.spec\.ts/,
      use: { ...devices["Desktop Chrome"], baseURL: `http://127.0.0.1:${clinicianPort}` },
    },
    {
      name: "admin-web",
      testMatch: /admin\.spec\.ts/,
      use: { ...devices["Desktop Chrome"], baseURL: `http://127.0.0.1:${adminPort}` },
    },
  ],
  webServer: [
    {
      command: `pnpm --filter @swasthyasetu/patient-web dev --port ${patientPort}`,
      port: patientPort,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: `pnpm --filter @swasthyasetu/clinician-web dev --port ${clinicianPort}`,
      port: clinicianPort,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: `pnpm --filter @swasthyasetu/admin-web dev --port ${adminPort}`,
      port: adminPort,
      reuseExistingServer: !process.env.CI,
    },
  ],
});
