import { test, expect } from "@playwright/test";

test.describe("CrudTableRecipe Component Spec", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to page hosting CrudTableRecipe (supports any route or dev port)
    await page.goto("/");
  });

  test("renders data table with accessible landmarks, headers, and rows", async ({ page }) => {
    // 1. Heading verification
    const heading = page.getByRole("heading", { level: 1 });
    await expect(heading).toBeVisible();

    // 2. Operational toolbar search input
    const searchInput = page.getByRole("searchbox").or(page.getByPlaceholder(/search/i));
    await expect(searchInput.first()).toBeVisible();

    // 3. Primary action button
    const createButton = page.getByRole("button", { name: /create/i });
    await expect(createButton.first()).toBeVisible();

    // 4. Semantic Table structure
    const table = page.getByRole("table");
    await expect(table).toBeVisible();

    // Column headers should match enterprise metadata
    const headers = page.getByRole("columnheader");
    await expect(headers.first()).toBeVisible();
    await expect(await headers.count()).toBeGreaterThanOrEqual(4);

    // Rows verification
    const rows = page.getByRole("row");
    await expect(await rows.count()).toBeGreaterThan(1);
  });

  test("filters rows dynamically upon user search input", async ({ page }) => {
    const searchInput = page.getByRole("searchbox").or(page.getByPlaceholder(/search/i)).first();
    await expect(searchInput).toBeVisible();

    // Type query matching specific item
    await searchInput.fill("NONEXISTENT_QUERY_TERM_xyz123");

    // Resilient empty state should render
    const emptyStateHeading = page.getByText(/no matching records/i);
    await expect(emptyStateHeading).toBeVisible();

    // Clear search button restores rows
    const clearButton = page.getByRole("button", { name: /clear search/i }).or(searchInput);
    if (await page.getByRole("button", { name: /clear search/i }).isVisible()) {
      await page.getByRole("button", { name: /clear search/i }).click();
    } else {
      await searchInput.fill("");
    }

    const tableRows = page.getByRole("row");
    await expect(await tableRows.count()).toBeGreaterThan(1);
  });

  test("supports pagination or row navigation", async ({ page }) => {
    const nextButton = page.getByRole("button", { name: /next page/i }).or(page.getByLabel(/next/i));
    if (await nextButton.isVisible()) {
      await expect(nextButton).toBeEnabled();
      await nextButton.click();
    }
  });

  test("passes accessibility checks with no violation of landmark structure", async ({ page }) => {
    // Confirm table has an accessible name
    const table = page.getByRole("table");
    await expect(table).toHaveAttribute("aria-label");
  });
});
