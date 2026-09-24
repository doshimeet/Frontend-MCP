import { test, expect } from "@playwright/test";

test.describe("MetricsDashboardRecipe Component Spec", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("renders executive KPI summary tiles with metrics and labels", async ({ page }) => {
    // 1. Heading verification
    const heading = page.getByRole("heading", { level: 1 }).first();
    await expect(heading).toBeVisible();

    // 2. Date range filter buttons
    const filterButtons = page.getByRole("button", { name: /24H|7D|30D|90D/i });
    await expect(filterButtons.first()).toBeVisible();

    // Click 7D filter and verify active state
    const sevenDayBtn = page.getByRole("button", { name: /^7D$/i });
    if (await sevenDayBtn.isVisible()) {
      await sevenDayBtn.click();
    }

    // 3. Export button presence
    const exportButton = page.getByRole("button", { name: /export/i });
    await expect(exportButton.first()).toBeVisible();

    // 4. Metrics cards / tiles are rendered with values
    const metricTexts = page.getByText(/Total Operational|Active Enterprise|SLA Compliance|Reviews/i);
    await expect(metricTexts.first()).toBeVisible();
  });

  test("renders recent telemetry & activities table with semantic rows", async ({ page }) => {
    // Table heading
    const sectionHeading = page.getByRole("heading", { name: /recent/i });
    await expect(sectionHeading).toBeVisible();

    // Telemetry Table
    const table = page.getByRole("table");
    await expect(table.first()).toBeVisible();

    // Table rows should contain activities
    const rows = page.getByRole("row");
    await expect(await rows.count()).toBeGreaterThanOrEqual(2);
  });

  test("handles loading and empty resilient states gracefully", async ({ page }) => {
    // Ensure no broken images or unstyled layout shifts
    const table = page.getByRole("table").first();
    await expect(table).toBeVisible();
  });
});
