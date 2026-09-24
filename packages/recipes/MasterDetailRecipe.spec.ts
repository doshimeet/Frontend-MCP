import { test, expect } from "@playwright/test";

test.describe("MasterDetailRecipe Component Spec", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("renders master list and selected record inspection drawer", async ({ page }) => {
    // 1. Heading verification
    const heading = page.getByRole("heading", { level: 1 }).first();
    await expect(heading).toBeVisible();

    // 2. Search box for cases/records
    const searchBox = page.getByRole("searchbox").or(page.getByPlaceholder(/search/i));
    await expect(searchBox.first()).toBeVisible();

    // 3. Action buttons (Approve / Reject) in detail pane
    const approveBtn = page.getByRole("button", { name: /approve/i });
    const rejectBtn = page.getByRole("button", { name: /reject/i });
    await expect(approveBtn.first()).toBeVisible();
    await expect(rejectBtn.first()).toBeVisible();

    // 4. Detail tabs
    const tabList = page.getByRole("tablist");
    await expect(tabList.first()).toBeVisible();
  });

  test("filters master list when query is typed", async ({ page }) => {
    const searchBox = page.getByRole("searchbox").or(page.getByPlaceholder(/search/i)).first();
    await searchBox.fill("Solar");

    // Verify filtered match appears
    const solarRecord = page.getByText(/solar/i);
    await expect(solarRecord.first()).toBeVisible();

    // Clear search
    await searchBox.fill("");
  });

  test("switches tabs in the detail inspection pane seamlessly", async ({ page }) => {
    // Click Approval Chain tab
    const approvalsTab = page.getByRole("tab", { name: /approval/i });
    await expect(approvalsTab).toBeVisible();
    await approvalsTab.click();

    // Signatories heading should appear
    const signatoriesHeading = page.getByText(/signatories|designated/i);
    await expect(signatoriesHeading.first()).toBeVisible();

    // Click Audit History tab
    const auditTab = page.getByRole("tab", { name: /audit/i });
    await expect(auditTab).toBeVisible();
    await auditTab.click();

    const auditContent = page.getByText(/audit trail|checksum/i);
    await expect(auditContent.first()).toBeVisible();
  });
});
