// SQL Formatter 页面 E2E 测试用例
// 高级测试工程师技能应用：
// - 等价类划分：测试正常/异常 SQL 输入场景
// - 边界值分析：测试 SQL 语句长度边界
// - 场景法/用户故事：基于业务流程设计端到端测试
// - UI 自动化：使用 Playwright 进行浏览器自动化测试

import { test, expect } from '@playwright/test';

const BASE_URL = "http://localhost:5004/sql-formatter";

async function navigateToPage(page: any) {
  await page.goto(BASE_URL, { timeout: 30000 });
  await page.waitForLoadState('networkidle', { timeout: 30000 });
}

test.describe('SQL Formatter E2E Tests', () => {
  test('测试 01: 页面加载与基本元素验证', async ({ page }) => {
    await navigateToPage(page);
    
    await expect(page).toHaveTitle('SQL ID 格式化工具');
    await expect(page.locator('textarea').first()).toBeVisible({ timeout: 10000 });
    const buttonCount = await page.locator('button').count();
    expect(buttonCount).toBeGreaterThan(0);
  });

  test('测试 02: SQL 格式化功能（正常输入）', async ({ page }) => {
    await navigateToPage(page);
    
    const inputTextarea = page.locator('textarea').first();
    const idsInput = `ID001\nID002`;
    
    await inputTextarea.fill(idsInput);
    await page.waitForTimeout(500);
    
    const formatBtn = page.getByRole('button', { name: /格式化/ }).first();
    await formatBtn.click();
    await page.waitForTimeout(1000);
    
    const outputTextarea = page.locator('textarea').last();
    const formattedSql = await outputTextarea.inputValue();
    
    expect(formattedSql).toBeTruthy();
    expect(formattedSql).toContain("'ID001'");
    expect(formattedSql).toContain("'ID002'");
  });

  test('测试 03: SQL 格式化功能（多行输入）', async ({ page }) => {
    await navigateToPage(page);
    
    const inputTextarea = page.locator('textarea').first();
    const idsInput = `ID001\nID002\nID003`;
    
    await inputTextarea.fill(idsInput);
    await page.waitForTimeout(500);
    
    const formatBtn = page.getByRole('button', { name: /格式化/ }).first();
    await formatBtn.click();
    await page.waitForTimeout(1000);
    
    const outputTextarea = page.locator('textarea').last();
    const formattedSql = await outputTextarea.inputValue();
    
    expect(formattedSql).toContain('\n');
    expect(formattedSql).toContain("'ID001'");
    expect(formattedSql).toContain("'ID002'");
    expect(formattedSql).toContain("'ID003'");
  });

  test('测试 04: 空输入处理', async ({ page }) => {
    await navigateToPage(page);
    
    const formatBtn = page.getByRole('button', { name: /格式化/ }).first();
    await formatBtn.click();
    await page.waitForTimeout(500);
    
    const outputTextarea = page.locator('textarea').last();
    const formattedSql = await outputTextarea.inputValue();
    
    expect(formattedSql).toBe('');
  });

  test('测试 05: 复制功能', async ({ page }) => {
    await navigateToPage(page);
    
    const inputTextarea = page.locator('textarea').first();
    await inputTextarea.fill('SELECT 1');
    
    const formatBtn = page.getByRole('button', { name: /格式化/ }).first();
    await formatBtn.click();
    await page.waitForTimeout(500);
    
    const copyBtn = page.getByRole('button', { name: /复制/ }).first();
    await expect(copyBtn).toBeVisible({ timeout: 10000 });
    
    await copyBtn.click();
    await page.waitForTimeout(500);
  });

  test('测试 06: 清除功能', async ({ page }) => {
    await navigateToPage(page);
    
    const inputTextarea = page.locator('textarea').first();
    await inputTextarea.fill('SELECT * FROM test');
    
    const clearBtn = page.getByRole('button', { name: /清除/ }).first();
    await expect(clearBtn).toBeVisible({ timeout: 10000 });
    
    await clearBtn.click();
    await page.waitForTimeout(500);
    
    const inputValue = await inputTextarea.inputValue();
    expect(inputValue).toBe('');
  });

  test('测试 07: 错误 SQL 处理（错误推测法）', async ({ page }) => {
    await navigateToPage(page);
    
    const inputTextarea = page.locator('textarea').first();
    await inputTextarea.fill('SELECT FROM users');
    
    const formatBtn = page.getByRole('button', { name: /格式化/ }).first();
    await formatBtn.click();
    await page.waitForTimeout(500);
    
    const outputTextarea = page.locator('textarea').last();
    const result = await outputTextarea.inputValue();
    
    expect(result).toBeTruthy();
  });

  test('测试 09: 大 SQL 语句处理（性能测试）', async ({ page }) => {
    await navigateToPage(page);
    
    const largeSql = 'SELECT ' + Array.from({ length: 50 }, (_, i) => `col${i}`).join(', ') + ' FROM large_table';
    
    const inputTextarea = page.locator('textarea').first();
    await inputTextarea.fill(largeSql);
    
    const startTime = await page.evaluate(() => performance.now());
    
    const formatBtn = page.getByRole('button', { name: /格式化/ }).first();
    await formatBtn.click();
    await page.waitForTimeout(1000);
    
    const endTime = await page.evaluate(() => performance.now());
    
    expect((endTime - startTime) / 1000).toBeLessThan(5);
    
    const outputTextarea = page.locator('textarea').last();
    const result = await outputTextarea.inputValue();
    expect(result).toBeTruthy();
  });

  test('测试 10: 页面导航验证', async ({ page }) => {
    await navigateToPage(page);
    
    const navLinks = ['首页', '文档', '工具', '关于'];
    for (const link of navLinks) {
      const element = page.locator(`text=${link}`);
      if (await element.count() > 0) {
        await expect(element.first()).toBeVisible({ timeout: 5000 });
      }
    }
  });
});