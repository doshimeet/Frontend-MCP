import { test, expect } from "@playwright/test";

test.describe("FormWizardRecipe Component Spec", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("renders step progress tracker and initial step fields", async ({ page }) => {
    // 1. Wizard heading
    const heading = page.getByRole("heading", { level: 1 }).first();
    await expect(heading).toBeVisible();

    // 2. Step 0 fields
    const orgNameInput = page.getByLabel(/organization name/i).or(page.locator("#orgName"));
    await expect(orgNameInput.first()).toBeVisible();

    const adminEmailInput = page.getByLabel(/admin.*email/i).or(page.locator("#adminEmail"));
    await expect(adminEmailInput.first()).toBeVisible();

    // 3. Navigation controls
    const nextButton = page.getByRole("button", { name: /next step/i });
    await expect(nextButton).toBeVisible();
  });

  test("prevents step progression when required fields are missing", async ({ page }) => {
    const orgNameInput = page.getByLabel(/organization name/i).or(page.locator("#orgName")).first();
    await orgNameInput.clear();

    const nextButton = page.getByRole("button", { name: /next step/i });
    await nextButton.click();

    // Validation error text or invalid attribute should appear
    const errorText = page.getByText(/required|valid/i);
    await expect(errorText.first()).toBeVisible();
  });

  test("progresses through multi-step intake flow to final confirmation", async ({ page }) => {
    // Step 0: Fill General Information
    const orgNameInput = page.getByLabel(/organization name/i).or(page.locator("#orgName")).first();
    await orgNameInput.fill("Acme Global Operations");

    const emailInput = page.getByLabel(/admin.*email/i).or(page.locator("#adminEmail")).first();
    await emailInput.fill("admin@acme-global.org");

    const nextBtn1 = page.getByRole("button", { name: /next step/i });
    await nextBtn1.click();

    // Step 1: Infrastructure
    const infraHeading = page.getByRole("heading", { name: /infrastructure/i });
    await expect(infraHeading).toBeVisible();

    const nextBtn2 = page.getByRole("button", { name: /next step/i });
    await nextBtn2.click();

    // Step 2: Governance & Security
    const secHeading = page.getByRole("heading", { name: /security|governance/i });
    await expect(secHeading).toBeVisible();

    const nextBtn3 = page.getByRole("button", { name: /next step/i });
    await nextBtn3.click();

    // Step 3: Review & Summary
    const summaryHeading = page.getByRole("heading", { name: /summary|review/i });
    await expect(summaryHeading).toBeVisible();

    // Confirm button should be ready
    const confirmBtn = page.getByRole("button", { name: /confirm|provision/i });
    await expect(confirmBtn).toBeVisible();
  });
});
