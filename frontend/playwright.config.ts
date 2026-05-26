import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  // 配置截图策略
  screenshot: {
    mode: 'only-on-failure',
    fullPage: true,
  },
  // 配置测试报告
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['line'],
  ],
});
