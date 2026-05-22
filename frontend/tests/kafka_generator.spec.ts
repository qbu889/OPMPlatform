import { test, expect } from '@playwright/test';

const mockEsData = JSON.stringify({
  "_source": {
    "CITY_ID": "350500",
    "BUSINESS_TAG": { "BUSINESS_TYPE": "传输" },
    "NETWORK_TYPE_ID": "1",
    "ALARM_LEVEL": "2",
    "EQUIPMENT_NAME": "泉州德化县传输外线",
    "NE_LABEL": "DEHUA-001",
    "EVENT_LOCATION": "泉州市德化县",
    "VENDOR_NAME": "华为",
    "ALARM_NAME": "光缆中断",
    "DELAY_TIME": 15
  }
});

test.describe('Kafka生成器 - 主流程测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5200/kafka-generator');
    await page.waitForLoadState('networkidle');
  });

  test('页面加载验证', async ({ page }) => {
    await expect(page).toHaveTitle(/Kafka/);
    const header = page.locator('h2', { hasText: 'Kafka 消息生成器' });
    await expect(header).toBeVisible();
  });

  test('输入ES数据并生成消息', async ({ page }) => {
    const esInput = page.locator('textarea');
    await esInput.fill(mockEsData);
    
    const generateBtn = page.locator('button', { hasText: '生成 Kafka 消息' });
    await generateBtn.click();
    
    await page.waitForResponse(
      (response) => response.url().includes('/kafka-generator/generate'),
      { timeout: 15000 }
    );
    
    await page.waitForTimeout(2000);
    const bodyText = await page.textContent('body');
    expect(bodyText).toContain('FP值:');
  });

  test('自定义字段覆盖', async ({ page }) => {
    await page.locator('textarea').fill(mockEsData);
    
    const titleInput = page.locator('input[placeholder*="告警标题"]');
    if (await titleInput.count() > 0) {
      await titleInput.first().fill('自定义告警标题');
    }
    
    await page.locator('button', { hasText: '生成 Kafka 消息' }).click();
    await page.waitForTimeout(2000);
    
    const bodyText = await page.textContent('body');
    expect(bodyText).toContain('自定义告警标题');
  });

  test('时间调整功能', async ({ page }) => {
    await page.locator('textarea').fill(mockEsData);
    
    const delayInput = page.locator('[type="number"]');
    if (await delayInput.isVisible()) {
      await delayInput.fill('30');
    }
    
    await page.locator('button', { hasText: '生成 Kafka 消息' }).click();
    await page.waitForTimeout(2000);
    
    const bodyText = await page.textContent('body');
    expect(bodyText).toContain('FP值:');
  });

  test('测试前缀功能', async ({ page }) => {
    await page.locator('textarea').fill(mockEsData);
    
    const testPrefixSwitch = page.locator('.el-switch').first();
    if (await testPrefixSwitch.isVisible()) {
      await testPrefixSwitch.click();
    }
    
    await page.locator('button', { hasText: '生成 Kafka 消息' }).click();
    await page.waitForTimeout(2000);
    
    const bodyText = await page.textContent('body');
    expect(bodyText).toContain('【测试】');
  });

  test('复制结果功能', async ({ page }) => {
    await page.locator('textarea').fill(mockEsData);
    await page.locator('button', { hasText: '生成 Kafka 消息' }).click();
    await page.waitForTimeout(2000);
    
    const copyBtn = page.locator('button', { hasText: '复制结果' });
    if (await copyBtn.isVisible()) {
      await copyBtn.click();
    }
  });

  test('生成推送消息', async ({ page }) => {
    await page.locator('textarea').fill(mockEsData);
    await page.locator('button', { hasText: '生成 Kafka 消息' }).click();
    await page.waitForTimeout(2000);
    
    const pushBtn = page.locator('button', { hasText: '生成推送消息' });
    if (await pushBtn.isVisible()) {
      await pushBtn.click();
    }
  });

  test('唯一值功能', async ({ page }) => {
    await page.locator('textarea').fill(mockEsData);
    
    const fieldCard = page.locator('.field-card');
    if (await fieldCard.first().isVisible()) {
      const uniqueSwitch = fieldCard.first().locator('[role="switch"]');
      if (await uniqueSwitch.isVisible()) {
        await uniqueSwitch.click();
      }
    }
    
    await page.locator('button', { hasText: '生成 Kafka 消息' }).click();
    await page.waitForTimeout(2000);
    
    const bodyText = await page.textContent('body');
    expect(bodyText).toContain('FP值:');
  });

  test('查看字段字典', async ({ page }) => {
    const fieldCard = page.locator('.field-card');
    if (await fieldCard.first().isVisible()) {
      const dictIcon = fieldCard.first().locator('[title*="字典"]');
      if (await dictIcon.isVisible()) {
        await dictIcon.click();
        await expect(page.locator('.el-dialog')).toBeVisible();
      }
    }
  });

  test('FP值复制功能', async ({ page }) => {
    await page.locator('textarea').fill(mockEsData);
    await page.locator('button', { hasText: '生成 Kafka 消息' }).click();
    await page.waitForTimeout(2000);
    
    const copyFpBtn = page.locator('button', { hasText: '复制FP值' });
    if (await copyFpBtn.isVisible()) {
      await copyFpBtn.click();
    }
  });

  test('添加备注', async ({ page }) => {
    const fieldCard = page.locator('.field-card');
    if (await fieldCard.first().isVisible()) {
      const remarkBtn = fieldCard.first().locator('[title*="备注"]');
      if (await remarkBtn.isVisible()) {
        await remarkBtn.click();
        await page.waitForTimeout(1000);
        const dialog = page.locator('.el-dialog');
        await expect(dialog).toBeVisible();
      }
    }
  });
});