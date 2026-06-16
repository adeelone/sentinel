import { expect, test } from "@playwright/test";

test("dashboard loads", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Fraud operations dashboard")).toBeVisible();
  await expect(page.getByText("Score a transaction")).toBeVisible();
});
