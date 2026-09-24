import { test, expect } from "@playwright/test";

test.describe("SettingsTabsRecipe Component Spec", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("renders portal governance settings with tabbed categories", async ({ page }) => {
    // 1. Heading verification
    const heading = page.getByRole("heading", { level: 1 }).first();
    await expect(heading).toBeVisible();

    // 2. Settings tablist verification
    const tabList = page.getByRole("tablist", { name: /settings/i }).or(page.getByRole("tablist"));
    await expect(tabList.first()).toBeVisible();

    // Tab buttons
    const generalTab = page.getByRole("tab", { name: /general/i });
    const securityTab = page.getByRole("tab", { name: /security/i });
    const apiTab = page.getByRole("tab", { name: /api/i });
    const notifTab = page.getByRole("tab", { name: /notifications/i });

    await expect(generalTab).toBeVisible();
    await expect(securityTab).toBeVisible();
    await expect(apiTab).toBeVisible();
    await expect(notifTab).toBeVisible();
  });

  test("edits inputs and saves preferences successfully", async ({ page }) => {
    // Fill application name
    const appNameInput = page.getByLabel(/application name/i).or(page.locator("#app-name"));
    await expect(appNameInput.first()).toBeVisible();
    await appNameInput.fill("Updated Global Operations Hub");

    // Click Save Preferences
    const saveButton = page.getByRole("button", { name: /save preferences/i });
    await expect(saveButton).toBeVisible();
    await saveButton.click();

    // Feedback alert appears
    const successAlert = page.getByText(/settings saved successfully/i);
    await expect(successAlert).toBeVisible();
  });

  test("switches between security and API key tabs to toggle secret visibility", async ({ page }) => {
    // Click API & Credentials tab
    const apiTab = page.getByRole("tab", { name: /api/i });
    await apiTab.click();

    const apiKeyInput = page.locator("#api-key");
    await expect(apiKeyInput).toBeVisible();
    await expect(apiKeyInput).toHaveAttribute("type", "password");

    // Click Reveal
    const revealBtn = page.getByRole("button", { name: /reveal/i });
    await revealBtn.click();
    await expect(apiKeyInput).toHaveAttribute("type", "text");
  });
});
