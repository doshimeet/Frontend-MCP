import { test, expect } from "@playwright/test";

test.describe("AuditTimelineRecipe Component Spec", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("renders audit stream heading, filter tags, and export button", async ({ page }) => {
    // 1. Heading verification
    const heading = page.getByRole("heading", { level: 1 }).first();
    await expect(heading).toBeVisible();

    // 2. Export button
    const exportBtn = page.getByRole("button", { name: /export/i });
    await expect(exportBtn).toBeVisible();

    // 3. Category filters
    const allFilter = page.getByRole("button", { name: /^all$/i });
    const approvalFilter = page.getByRole("button", { name: /^approval$/i });
    await expect(allFilter).toBeVisible();
    await expect(approvalFilter).toBeVisible();

    // 4. Search input
    const searchInput = page.getByRole("searchbox").or(page.getByPlaceholder(/search/i));
    await expect(searchInput.first()).toBeVisible();
  });

  test("filters timeline events by category pill", async ({ page }) => {
    const approvalFilter = page.getByRole("button", { name: /^approval$/i });
    await approvalFilter.click();

    // Approval events should be visible
    const approvalTag = page.getByText(/approved tranche/i);
    await expect(approvalTag.first()).toBeVisible();
  });

  test("expands telemetry and JSON diff details on click", async ({ page }) => {
    // Locate the first telemetry toggle button
    const toggleBtn = page.getByRole("button", { name: /view telemetry/i }).first();
    await expect(toggleBtn).toBeVisible();
    await toggleBtn.click();

    // Verify expanded telemetry code/pre element with integrity_hash
    const telemetryBlock = page.locator("pre").first();
    await expect(telemetryBlock).toBeVisible();
    await expect(telemetryBlock).toContainText("integrity_hash");

    // Toggle closed
    const hideBtn = page.getByRole("button", { name: /hide telemetry/i }).first();
    await hideBtn.click();
    await expect(telemetryBlock).not.toBeVisible();
  });
});
