import { test, expect } from '@playwright/test';
test('验证 Playwright 安装', async ({ page }) => { await page.goto('https://playwright.dev'); await expect(page).toHaveTitle(/Playwright/); });
