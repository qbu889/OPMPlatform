# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: page.spec.ts >> Kafka Generator E2E Tests >> 测试 06: 字段字典管理功能
- Location: frontend/tests/page.spec.ts:91:3

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for locator('button').first()
    - locator resolved to <button type="button" data-v-104b1e87="" aria-disabled="false" class="el-button el-button--small">…</button>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <div role="dialog" aria-modal="true" aria-label="新增字典项" class="el-overlay-dialog" aria-describedby="el-id-5344-15">…</div> from <div data-v-41086d7c="" class="field-dict-manager">…</div> subtree intercepts pointer events
    - retrying click action
    - waiting 20ms
    2 × waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <div role="dialog" aria-modal="true" aria-label="新增字典项" class="el-overlay-dialog" aria-describedby="el-id-5344-15">…</div> from <div data-v-41086d7c="" class="field-dict-manager">…</div> subtree intercepts pointer events
    - retrying click action
      - waiting 100ms
    51 × waiting for element to be visible, enabled and stable
       - element is visible, enabled and stable
       - scrolling into view if needed
       - done scrolling
       - <div role="dialog" aria-modal="true" aria-label="新增字典项" class="el-overlay-dialog" aria-describedby="el-id-5344-15">…</div> from <div data-v-41086d7c="" class="field-dict-manager">…</div> subtree intercepts pointer events
     - retrying click action
       - waiting 500ms

```

# Page snapshot

```yaml
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
              - generic:
                - combobox "Kafka 字段" [ref=e81]
                - generic [ref=e82]: 选择字段
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
          - table [ref=e131]:
            - rowgroup [ref=e142]:
              - row "4 EFFECT_NE 1 影响网元 1 启用 直接影响 Wed, 20 May 2026 14:05:45 GMT 编辑 删除" [ref=e143]:
                - cell "4" [ref=e144]:
                  - generic [ref=e145]: "4"
                - cell "EFFECT_NE" [ref=e146]:
                  - generic [ref=e147]: EFFECT_NE
                - cell "1" [ref=e148]:
                  - generic [ref=e149]: "1"
                - cell "影响网元" [ref=e150]:
                  - generic [ref=e151]: 影响网元
                - cell "1" [ref=e152]:
                  - generic [ref=e153]: "1"
                - cell "启用" [ref=e154]:
                  - generic [ref=e157]: 启用
                - cell "直接影响" [ref=e158]:
                  - generic [ref=e159]: 直接影响
                - cell "Wed, 20 May 2026 14:05:45 GMT" [ref=e160]:
                  - generic [ref=e161]: Wed, 20 May 2026 14:05:45 GMT
                - cell "编辑 删除" [ref=e162]:
                  - generic [ref=e163]:
                    - button "编辑" [ref=e164] [cursor=pointer]:
                      - generic [ref=e165]: 编辑
                    - button "删除" [ref=e166] [cursor=pointer]:
                      - generic [ref=e167]: 删除
              - row "5 EFFECT_NE 2 不影响网元 2 启用 间接影响 Wed, 20 May 2026 14:05:45 GMT 编辑 删除" [ref=e168]:
                - cell "5" [ref=e169]:
                  - generic [ref=e170]: "5"
                - cell "EFFECT_NE" [ref=e171]:
                  - generic [ref=e172]: EFFECT_NE
                - cell "2" [ref=e173]:
                  - generic [ref=e174]: "2"
                - cell "不影响网元" [ref=e175]:
                  - generic [ref=e176]: 不影响网元
                - cell "2" [ref=e177]:
                  - generic [ref=e178]: "2"
                - cell "启用" [ref=e179]:
                  - generic [ref=e182]: 启用
                - cell "间接影响" [ref=e183]:
                  - generic [ref=e184]: 间接影响
                - cell "Wed, 20 May 2026 14:05:45 GMT" [ref=e185]:
                  - generic [ref=e186]: Wed, 20 May 2026 14:05:45 GMT
                - cell "编辑 删除" [ref=e187]:
                  - generic [ref=e188]:
                    - button "编辑" [ref=e189] [cursor=pointer]:
                      - generic [ref=e190]: 编辑
                    - button "删除" [ref=e191] [cursor=pointer]:
                      - generic [ref=e192]: 删除
              - row "6 EFFECT_SERVICE 1 影响业务 1 启用 业务中断 Wed, 20 May 2026 14:05:45 GMT 编辑 删除" [ref=e193]:
                - cell "6" [ref=e194]:
                  - generic [ref=e195]: "6"
                - cell "EFFECT_SERVICE" [ref=e196]:
                  - generic [ref=e197]: EFFECT_SERVICE
                - cell "1" [ref=e198]:
                  - generic [ref=e199]: "1"
                - cell "影响业务" [ref=e200]:
                  - generic [ref=e201]: 影响业务
                - cell "1" [ref=e202]:
                  - generic [ref=e203]: "1"
                - cell "启用" [ref=e204]:
                  - generic [ref=e207]: 启用
                - cell "业务中断" [ref=e208]:
                  - generic [ref=e209]: 业务中断
                - cell "Wed, 20 May 2026 14:05:45 GMT" [ref=e210]:
                  - generic [ref=e211]: Wed, 20 May 2026 14:05:45 GMT
                - cell "编辑 删除" [ref=e212]:
                  - generic [ref=e213]:
                    - button "编辑" [ref=e214] [cursor=pointer]:
                      - generic [ref=e215]: 编辑
                    - button "删除" [ref=e216] [cursor=pointer]:
                      - generic [ref=e217]: 删除
              - row "7 EFFECT_SERVICE 2 不影响业务 2 启用 业务正常 Wed, 20 May 2026 14:05:45 GMT 编辑 删除" [ref=e218]:
                - cell "7" [ref=e219]:
                  - generic [ref=e220]: "7"
                - cell "EFFECT_SERVICE" [ref=e221]:
                  - generic [ref=e222]: EFFECT_SERVICE
                - cell "2" [ref=e223]:
                  - generic [ref=e224]: "2"
                - cell "不影响业务" [ref=e225]:
                  - generic [ref=e226]: 不影响业务
                - cell "2" [ref=e227]:
                  - generic [ref=e228]: "2"
                - cell "启用" [ref=e229]:
                  - generic [ref=e232]: 启用
                - cell "业务正常" [ref=e233]:
                  - generic [ref=e234]: 业务正常
                - cell "Wed, 20 May 2026 14:05:45 GMT" [ref=e235]:
                  - generic [ref=e236]: Wed, 20 May 2026 14:05:45 GMT
                - cell "编辑 删除" [ref=e237]:
                  - generic [ref=e238]:
                    - button "编辑" [ref=e239] [cursor=pointer]:
                      - generic [ref=e240]: 编辑
                    - button "删除" [ref=e241] [cursor=pointer]:
                      - generic [ref=e242]: 删除
              - row "1 NETWORK_TYPE_TOP 1 核心层 1 启用 骨干网络 Wed, 20 May 2026 14:05:45 GMT 编辑 删除" [ref=e243]:
                - cell "1" [ref=e244]:
                  - generic [ref=e245]: "1"
                - cell "NETWORK_TYPE_TOP" [ref=e246]:
                  - generic [ref=e247]: NETWORK_TYPE_TOP
                - cell "1" [ref=e248]:
                  - generic [ref=e249]: "1"
                - cell "核心层" [ref=e250]:
                  - generic [ref=e251]: 核心层
                - cell "1" [ref=e252]:
                  - generic [ref=e253]: "1"
                - cell "启用" [ref=e254]:
                  - generic [ref=e257]: 启用
                - cell "骨干网络" [ref=e258]:
                  - generic [ref=e259]: 骨干网络
                - cell "Wed, 20 May 2026 14:05:45 GMT" [ref=e260]:
                  - generic [ref=e261]: Wed, 20 May 2026 14:05:45 GMT
                - cell "编辑 删除" [ref=e262]:
                  - generic [ref=e263]:
                    - button "编辑" [ref=e264] [cursor=pointer]:
                      - generic [ref=e265]: 编辑
                    - button "删除" [ref=e266] [cursor=pointer]:
                      - generic [ref=e267]: 删除
              - row "2 NETWORK_TYPE_TOP 2 汇聚层 2 启用 区域汇聚 Wed, 20 May 2026 14:05:45 GMT 编辑 删除" [ref=e268]:
                - cell "2" [ref=e269]:
                  - generic [ref=e270]: "2"
                - cell "NETWORK_TYPE_TOP" [ref=e271]:
                  - generic [ref=e272]: NETWORK_TYPE_TOP
                - cell "2" [ref=e273]:
                  - generic [ref=e274]: "2"
                - cell "汇聚层" [ref=e275]:
                  - generic [ref=e276]: 汇聚层
                - cell "2" [ref=e277]:
                  - generic [ref=e278]: "2"
                - cell "启用" [ref=e279]:
                  - generic [ref=e282]: 启用
                - cell "区域汇聚" [ref=e283]:
                  - generic [ref=e284]: 区域汇聚
                - cell "Wed, 20 May 2026 14:05:45 GMT" [ref=e285]:
                  - generic [ref=e286]: Wed, 20 May 2026 14:05:45 GMT
                - cell "编辑 删除" [ref=e287]:
                  - generic [ref=e288]:
                    - button "编辑" [ref=e289] [cursor=pointer]:
                      - generic [ref=e290]: 编辑
                    - button "删除" [ref=e291] [cursor=pointer]:
                      - generic [ref=e292]: 删除
              - row "3 NETWORK_TYPE_TOP 3 接入层 3 启用 用户接入 Wed, 20 May 2026 14:05:45 GMT 编辑 删除" [ref=e293]:
                - cell "3" [ref=e294]:
                  - generic [ref=e295]: "3"
                - cell "NETWORK_TYPE_TOP" [ref=e296]:
                  - generic [ref=e297]: NETWORK_TYPE_TOP
                - cell "3" [ref=e298]:
                  - generic [ref=e299]: "3"
                - cell "接入层" [ref=e300]:
                  - generic [ref=e301]: 接入层
                - cell "3" [ref=e302]:
                  - generic [ref=e303]: "3"
                - cell "启用" [ref=e304]:
                  - generic [ref=e307]: 启用
                - cell "用户接入" [ref=e308]:
                  - generic [ref=e309]: 用户接入
                - cell "Wed, 20 May 2026 14:05:45 GMT" [ref=e310]:
                  - generic [ref=e311]: Wed, 20 May 2026 14:05:45 GMT
                - cell "编辑 删除" [ref=e312]:
                  - generic [ref=e313]:
                    - button "编辑" [ref=e314] [cursor=pointer]:
                      - generic [ref=e315]: 编辑
                    - button "删除" [ref=e316] [cursor=pointer]:
                      - generic [ref=e317]: 删除
        - generic [ref=e319]:
          - generic [ref=e320]: 共 7 条
          - generic [ref=e323] [cursor=pointer]:
            - generic:
              - combobox [ref=e325]
              - generic [ref=e326]: 50条/页
            - img [ref=e329]
          - button "上一页" [disabled] [ref=e331]:
            - generic:
              - img
          - list [ref=e332]:
            - listitem "第 1 页" [ref=e333]: "1"
          - button "下一页" [disabled] [ref=e334]:
            - generic:
              - img
          - generic [ref=e335]:
            - generic [ref=e336]: 前往
            - spinbutton "页" [ref=e339]: "1"
            - generic [ref=e340]: 页
    - dialog "新增字典项" [ref=e342]:
      - generic [active] [ref=e343]:
        - banner [ref=e344]:
          - heading "新增字典项" [level=2] [ref=e345]
          - button "关闭此对话框" [ref=e346] [cursor=pointer]:
            - img [ref=e348]
        - generic [ref=e351]:
          - generic [ref=e352]:
            - generic [ref=e353]: "* Kafka 字段"
            - generic [ref=e356]:
              - generic:
                - combobox "* Kafka 字段" [ref=e358]
                - generic [ref=e359]: 选择字段
              - img [ref=e362] [cursor=pointer]
          - generic [ref=e364]:
            - generic [ref=e365]: "* 字典键"
            - textbox "* 字典键" [ref=e369]:
              - /placeholder: 例如：1、CORE、ENABLED
          - generic [ref=e370]:
            - generic [ref=e371]: "* 字典值"
            - textbox "* 字典值" [ref=e375]:
              - /placeholder: 例如：核心层、已启用
          - generic [ref=e376]:
            - generic [ref=e377]: 排序
            - generic [ref=e379]:
              - button "减少数值" [ref=e380]:
                - img [ref=e382]
              - button "增加数值" [ref=e384] [cursor=pointer]:
                - img [ref=e386]
              - spinbutton "排序" [ref=e390]: "0"
          - generic [ref=e391]:
            - generic [ref=e392]: 备注
            - textbox "备注" [ref=e395]:
              - /placeholder: 可选的备注信息
        - contentinfo [ref=e396]:
          - button "取消" [ref=e397] [cursor=pointer]:
            - generic [ref=e398]: 取消
          - button "确定" [ref=e399] [cursor=pointer]:
            - generic [ref=e400]: 确定
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
      |                   ^ Error: locator.click: Test timeout of 30000ms exceeded.
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