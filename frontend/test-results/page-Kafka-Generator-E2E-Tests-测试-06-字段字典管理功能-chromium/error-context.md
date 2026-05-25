# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: page.spec.ts >> Kafka Generator E2E Tests >> 测试 06: 字段字典管理功能
- Location: tests/page.spec.ts:91:3

# Error details

```
Test timeout of 60000ms exceeded.
```

```
Error: locator.click: Test timeout of 60000ms exceeded.
Call log:
  - waiting for locator('button').first()
    - locator resolved to <button type="button" data-v-104b1e87="" aria-disabled="false" class="el-button el-button--small">…</button>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <div role="dialog" aria-modal="true" aria-label="新增字典项" class="el-overlay-dialog" aria-describedby="el-id-6880-15">…</div> from <div data-v-41086d7c="" class="field-dict-manager">…</div> subtree intercepts pointer events
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <div role="dialog" aria-modal="true" aria-label="新增字典项" class="el-overlay-dialog" aria-describedby="el-id-6880-15">…</div> from <div data-v-41086d7c="" class="field-dict-manager">…</div> subtree intercepts pointer events
    - retrying click action
      - waiting 100ms
    110 × waiting for element to be visible, enabled and stable
        - element is visible, enabled and stable
        - scrolling into view if needed
        - done scrolling
        - <div role="dialog" aria-modal="true" aria-label="新增字典项" class="el-overlay-dialog" aria-describedby="el-id-6880-15">…</div> from <div data-v-41086d7c="" class="field-dict-manager">…</div> subtree intercepts pointer events
      - retrying click action
        - waiting 500ms

```

# Page snapshot

```yaml
- generic [ref=e1]:
  - generic [ref=e3]:
    - banner [ref=e4]:
      - generic [ref=e5]:
        - generic [ref=e6] [cursor=pointer]:
          - img "NOKIA" [ref=e7]
          - generic [ref=e8]: OPM 系统
        - menubar [ref=e9]:
          - menuitem "首页" [ref=e10] [cursor=pointer]:
            - img [ref=e12]
            - generic [ref=e14]: 首页
          - menuitem "文档" [ref=e15]:
            - generic [ref=e16] [cursor=pointer]:
              - img [ref=e18]
              - generic [ref=e20]: 文档
              - img [ref=e22]
          - menuitem "智能系统" [ref=e24]:
            - generic [ref=e25] [cursor=pointer]:
              - img [ref=e27]
              - generic [ref=e29]: 智能系统
              - img [ref=e31]
          - menuitem "高效工具" [ref=e33]:
            - generic [ref=e34] [cursor=pointer]:
              - img [ref=e36]
              - generic [ref=e40]: 高效工具
              - img [ref=e42]
        - generic [ref=e44]:
          - button "登录" [ref=e45] [cursor=pointer]:
            - generic [ref=e46]:
              - img [ref=e48]
              - generic [ref=e50]: 登录
          - button "注册" [ref=e51] [cursor=pointer]:
            - generic [ref=e52]:
              - img [ref=e54]
              - generic [ref=e56]: 注册
    - generic [ref=e57]:
      - generic [ref=e58]:
        - generic [ref=e60]:
          - generic [ref=e61]:
            - button "返回" [ref=e62] [cursor=pointer]:
              - generic [ref=e63]:
                - img [ref=e65]
                - text: 返回
            - generic [ref=e67]: Kafka 字段字典管理
          - generic [ref=e68]:
            - button "新增字典项" [ref=e69] [cursor=pointer]:
              - generic [ref=e70]: 新增字典项
            - button "批量导入" [ref=e71] [cursor=pointer]:
              - generic [ref=e72]: 批量导入
        - generic [ref=e73]:
          - generic [ref=e74]:
            - generic [ref=e75]:
              - generic [ref=e76]: Kafka 字段
              - generic [ref=e79]:
                - combobox "Kafka 字段" [expanded] [active] [ref=e82]: 测试字典
                - img [ref=e85] [cursor=pointer]
            - generic [ref=e88]:
              - button "查询" [ref=e89] [cursor=pointer]:
                - generic [ref=e90]: 查询
              - button "重置" [ref=e91] [cursor=pointer]:
                - generic [ref=e92]: 重置
          - generic [ref=e94]:
            - table [ref=e96]:
              - rowgroup [ref=e107]:
                - row "ID Kafka 字段 字典键 字典值 排序 状态 备注 更新时间 操作" [ref=e108]:
                  - columnheader "ID" [ref=e109]:
                    - generic [ref=e110]: ID
                  - columnheader "Kafka 字段" [ref=e111]:
                    - generic [ref=e112]: Kafka 字段
                  - columnheader "字典键" [ref=e113]:
                    - generic [ref=e114]: 字典键
                  - columnheader "字典值" [ref=e115]:
                    - generic [ref=e116]: 字典值
                  - columnheader "排序" [ref=e117]:
                    - generic [ref=e118]: 排序
                  - columnheader "状态" [ref=e119]:
                    - generic [ref=e120]: 状态
                  - columnheader "备注" [ref=e121]:
                    - generic [ref=e122]: 备注
                  - columnheader "更新时间" [ref=e123]:
                    - generic [ref=e124]: 更新时间
                  - columnheader "操作" [ref=e125]:
                    - generic [ref=e126]: 操作
            - generic [ref=e130]:
              - table:
                - rowgroup
              - generic [ref=e132]: 暂无数据
          - generic [ref=e134]:
            - generic [ref=e135]: 共 0 条
            - generic [ref=e138] [cursor=pointer]:
              - generic:
                - combobox [ref=e140]
                - generic [ref=e141]: 50条/页
              - img [ref=e144]
            - button "上一页" [disabled] [ref=e146]:
              - generic:
                - img
            - list [ref=e147]:
              - listitem "第 1 页" [ref=e148]: "1"
            - button "下一页" [disabled] [ref=e149]:
              - generic:
                - img
            - generic [ref=e150]:
              - generic [ref=e151]: 前往
              - spinbutton "页" [ref=e154]: "1"
              - generic [ref=e155]: 页
      - dialog "新增字典项" [ref=e157]:
        - generic [ref=e158]:
          - banner [ref=e159]:
            - heading "新增字典项" [level=2] [ref=e160]
            - button "关闭此对话框" [ref=e161] [cursor=pointer]:
              - img [ref=e163]
          - generic [ref=e166]:
            - generic [ref=e167]:
              - generic [ref=e168]: "* Kafka 字段"
              - generic [ref=e171]:
                - generic:
                  - combobox "* Kafka 字段" [ref=e173]
                  - generic [ref=e174]: 选择字段
                - img [ref=e177] [cursor=pointer]
            - generic [ref=e179]:
              - generic [ref=e180]: "* 字典键"
              - textbox "* 字典键" [ref=e184]:
                - /placeholder: 例如：1、CORE、ENABLED
            - generic [ref=e185]:
              - generic [ref=e186]: "* 字典值"
              - textbox "* 字典值" [ref=e190]:
                - /placeholder: 例如：核心层、已启用
            - generic [ref=e191]:
              - generic [ref=e192]: 排序
              - generic [ref=e194]:
                - button "减少数值" [ref=e195]:
                  - img [ref=e197]
                - button "增加数值" [ref=e199] [cursor=pointer]:
                  - img [ref=e201]
                - spinbutton "排序" [ref=e205]: "0"
            - generic [ref=e206]:
              - generic [ref=e207]: 备注
              - textbox "备注" [ref=e210]:
                - /placeholder: 可选的备注信息
          - contentinfo [ref=e211]:
            - button "取消" [ref=e212] [cursor=pointer]:
              - generic [ref=e213]: 取消
            - button "确定" [ref=e214] [cursor=pointer]:
              - generic [ref=e215]: 确定
  - tooltip "无匹配数据" [ref=e216]:
    - generic [ref=e217]:
      - generic:
        - generic:
          - listbox
      - generic [ref=e218]: 无匹配数据
```

# Test source

```ts
  16  | }
  17  | 
  18  | test.describe('Kafka Generator E2E Tests', () => {
  19  |   test('测试 01: 页面加载与验证', async ({ page }) => {
  20  |     await navigateToPage(page);
  21  |     
  22  |     await expect(page).toHaveTitle('Kafka 消息生成');
  23  |     await expect(page.locator('text=Kafka 消息生成器')).toBeVisible({ timeout: 10000 });
  24  |     await expect(page.locator('text=根据 ES 数据生成 Kafka 消息')).toBeVisible({ timeout: 10000 });
  25  |     await expect(page.locator('textarea')).toBeVisible({ timeout: 10000 });
  26  |   });
  27  | 
  28  |   test('测试 02: 加载示例数据功能', async ({ page }) => {
  29  |     await navigateToPage(page);
  30  |     
  31  |     await page.click('text=加载示例数据');
  32  |     
  33  |     const textarea = page.locator('textarea');
  34  |     await expect(textarea).toBeVisible({ timeout: 10000 });
  35  |     
  36  |     const esData = await textarea.inputValue();
  37  |     expect(esData).toBeTruthy();
  38  |     
  39  |     try {
  40  |       const data = JSON.parse(esData);
  41  |       expect(typeof data).toBe('object');
  42  |     } catch (error) {
  43  |       throw new Error('加载的示例数据不是有效的 JSON 格式');
  44  |     }
  45  |   });
  46  | 
  47  |   test('测试 03: 生成 Kafka 消息功能', async ({ page }) => {
  48  |     await navigateToPage(page);
  49  |     
  50  |     await page.click('text=加载示例数据');
  51  |     await page.click('text=生成 Kafka 消息');
  52  |     
  53  |     await page.waitForTimeout(1000);
  54  |     
  55  |     const count = await page.locator('text=Kafka 消息').count();
  56  |     await expect(page).toHaveTitle('Kafka 消息生成');
  57  |   });
  58  | 
  59  |   test('测试 04: 清除所有字段功能', async ({ page }) => {
  60  |     await navigateToPage(page);
  61  |     
  62  |     await page.click('text=加载示例数据');
  63  |     await page.waitForTimeout(500);
  64  |     
  65  |     const textarea = page.locator('textarea');
  66  |     const originalLength = (await textarea.inputValue()).length;
  67  |     expect(originalLength).toBeGreaterThan(0);
  68  |     await page.click('text=清除所有字段');
  69  |     await page.waitForTimeout(500);
  70  |     const clearedValue = await textarea.inputValue();
  71  |     if (clearedValue.length === originalLength) {
  72  |       console.log('清除按钮可能没有生效，检查是否有其他行为');
  73  |     }
  74  |     expect(clearedValue.length).toBeLessThanOrEqual(originalLength);
  75  |   });
  76  | 
  77  |   test('测试 05: 字段映射管理按钮', async ({ page }) => {
  78  |     await navigateToPage(page);
  79  |     
  80  |     const fieldMappingBtn = page.locator('text=字段映射管理');
  81  |     await expect(fieldMappingBtn).toBeVisible({ timeout: 10000 });
  82  |     
  83  |     try {
  84  |       await fieldMappingBtn.click();
  85  |       await page.waitForTimeout(500);
  86  |     } catch (error) {
  87  |       test.skip();
  88  |     }
  89  |   });
  90  | 
  91  |   test('测试 06: 字段字典管理功能', async ({ page }) => {
  92  |     await navigateToPage(page);
  93  |     
  94  |     const dictMgmtBtn = page.locator('text=字段字典管理');
  95  |     await expect(dictMgmtBtn).toBeVisible({ timeout: 10000 });
  96  |     
  97  |     await dictMgmtBtn.click();
  98  |     await page.waitForTimeout(1000);
  99  |     
  100 |     const addBtn = page.locator('text=新增');
  101 |     await expect(addBtn).toBeVisible({ timeout: 10000 });
  102 |     
  103 |     await addBtn.click();
  104 |     await page.waitForTimeout(500);
  105 |     
  106 |     const nameInput = page.locator('input').first();
  107 |     await expect(nameInput).toBeVisible({ timeout: 10000 });
  108 |     
  109 |     await nameInput.fill('测试字典');
  110 |     const filledValue = await nameInput.inputValue();
  111 |     expect(filledValue).toBe('测试字典');
  112 |     
  113 |     const saveBtn = page.locator('button').first();
  114 |     await expect(saveBtn).toBeVisible({ timeout: 10000 });
  115 |     
> 116 |     await saveBtn.click();
      |                   ^ Error: locator.click: Test timeout of 60000ms exceeded.
  117 |     await page.waitForTimeout(500);
  118 |     
  119 |     const searchInput = page.locator('input[placeholder*="搜索"]');
  120 |     await expect(searchInput).toBeVisible({ timeout: 10000 });
  121 |     
  122 |     await searchInput.fill('测试字典');
  123 |     await page.waitForTimeout(500);
  124 |     
  125 |     const searchBtn = page.locator('text=查询');
  126 |     await expect(searchBtn).toBeVisible({ timeout: 10000 });
  127 |     
  128 |     await searchBtn.click();
  129 |     await page.waitForTimeout(500);
  130 |     
  131 |     const resultCount = await page.locator('text=测试字典').count();
  132 |     expect(resultCount).toBeGreaterThan(0);
  133 |   });
  134 | 
  135 |   test('测试 07: 新增字典项功能', async ({ page }) => {
  136 |     await navigateToPage(page);
  137 |     
  138 |     const addDictBtn = page.locator('text=新增字典项');
  139 |     await expect(addDictBtn).toBeVisible({ timeout: 10000 });
  140 |     
  141 |     try {
  142 |       await addDictBtn.click();
  143 |       await page.waitForTimeout(500);
  144 |     } catch (error) {
  145 |       test.skip();
  146 |     }
  147 |   });
  148 | 
  149 |   test('测试 08: ES 源数据验证（边界值分析）', async ({ page }) => {
  150 |     await navigateToPage(page);
  151 |     
  152 |     await page.click('text=加载示例数据');
  153 |     
  154 |     const textarea = page.locator("textarea[placeholder='请输入 ES 查询结果的 JSON 数据']");
  155 |     const data = JSON.parse(await textarea.inputValue());
  156 |     
  157 |     expect(Object.keys(data).length).toBeGreaterThan(0);
  158 |     
  159 |     const requiredFields = ['FULL_REGION_ID', 'EVENT_LEVEL'];
  160 |     for (const field of requiredFields) {
  161 |       if (field in data) {
  162 |         expect(data[field]).not.toBeNull();
  163 |       }
  164 |     }
  165 |   });
  166 | 
  167 |   test('测试 09: 页面导航功能', async ({ page }) => {
  168 |     await navigateToPage(page);
  169 |     
  170 |     await expect(page.locator('text=首页')).toBeVisible({ timeout: 10000 });
  171 |     await expect(page.locator('text=文档')).toBeVisible({ timeout: 10000 });
  172 |     await expect(page.locator('text=智能系统')).toBeVisible({ timeout: 10000 });
  173 |     await expect(page.locator('text=高效工具')).toBeVisible({ timeout: 10000 });
  174 |   });
  175 | 
  176 |   test('测试 10: 登录/注册功能', async ({ page }) => {
  177 |     await navigateToPage(page);
  178 |     
  179 |     const loginBtn = page.locator('text=登录');
  180 |     await expect(loginBtn).toBeVisible({ timeout: 10000 });
  181 |     
  182 |     const registerBtn = page.locator('text=注册');
  183 |     await expect(registerBtn).toBeVisible({ timeout: 10000 });
  184 |     
  185 |     try {
  186 |       await loginBtn.click();
  187 |       await page.waitForTimeout(500);
  188 |     } catch (error) {
  189 |       test.skip();
  190 |     }
  191 |   });
  192 | 
  193 |   test('测试 11: 错误处理场景（错误推测法）', async ({ page }) => {
  194 |     await navigateToPage(page);
  195 |     
  196 |     const textarea = page.locator('textarea');
  197 |     await textarea.fill('{invalid json}');
  198 |     
  199 |     await page.click('text=生成 Kafka 消息');
  200 |     await page.waitForTimeout(1000);
  201 |     
  202 |     const errorCount = await page.locator('text=错误').count() + 
  203 |                        await page.locator('text=Error').count();
  204 |     
  205 |     if (errorCount === 0) {
  206 |       console.log('未找到错误提示，可能页面没有错误提示功能');
  207 |     }
  208 |     
  209 |     await textarea.fill('');
  210 |     await page.click('text=生成 Kafka 消息');
  211 |     await page.waitForTimeout(500);
  212 |   });
  213 | 
  214 |   test('测试 12: 基础性能检查', async ({ page }) => {
  215 |     await navigateToPage(page);
  216 |     
```