import { test, expect } from "@playwright/test";

test.describe("Enterprise Operations Portal - Core Suite", () => {
  test("1. Renders official classification banner and application title", async ({ page }) => {
    await page.goto("/");
    // Verify top classification banner
    const banner = page.getByText("OFFICIAL USE ONLY");
    await expect(banner).toBeVisible();

    // Verify main page heading
    await expect(page.locator("h1")).toBeVisible();
  });

  test("2. MSAL Verification Route loads session controls", async ({ page }) => {
    await page.goto("/verify-msal");
    await expect(page.getByText("MSAL Verification Dashboard")).toBeVisible();
    await expect(page.getByText("Session Details")).toBeVisible();
  });

  test("3. Telemetry Verification Route dispatches events", async ({ page }) => {
    await page.goto("/verify-adobe-app-insight");
    await expect(page.getByText("Telemetry & Analytics Verification")).toBeVisible();
    await page.getByRole("button", { name: "Trigger Adobe Event" }).click();
    await expect(page.getByText("Adobe Omniture Event Fired")).toBeVisible();
  });

  test("4. About page renders architecture specifications", async ({ page }) => {
    await page.goto("/about");
    await expect(page.getByText("About the Enterprise Operations Portal")).toBeVisible();
    await expect(page.getByText("@wbg/design-system")).toBeVisible();
  });
});
