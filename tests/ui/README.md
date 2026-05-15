# UI 自动化测试用例 - diff_routes.py

## 目录结构

```
tests/ui/
├── test_diff_ui_automation.py   # UI 自动化测试用例
├── conftest.py                   # pytest 配置
├── pytest.ini                    # pytest 配置文件
└── README.md                     # 说明文档
```

## 测试覆盖范围

### JSON 对比界面测试 (TestDiffCompareUI)

#### 功能测试
- ✓ **基础对比功能** - 输入左右两侧 JSON，执行对比操作
- ✓ **带选项的对比** - 测试 ignore_case、strict_mode 等选项
- ✓ **复杂数据对比** - 嵌套对象、数组的对比

#### 异常处理
- ✓ **无效 JSON 错误提示** - 验证前端对格式错误的提示
- ✓ **空字段提示** - 未输入数据时的错误处理
- ✓ **特殊字符处理** - 中文、emoji 等特殊字符的 UI 展示

#### 边界测试
- ✓ **大数据量对比** - 100+ 键值对的 JSON 处理
- ✓ **深层嵌套 JSON** - 多层嵌套结构的 UI 展示

#### UI 交互测试
- ✓ **清空功能** - Clear 按钮操作验证
- ✓ **复制结果功能** - Copy Result 按钮操作验证
- ✓ **JSON 格式化功能** - Format JSON 按钮操作验证

### JSON 格式化界面测试 (TestDiffFormatUI)

- ✓ **JSON 格式化成功** - 未格式化 JSON 转换为格式化格式
- ✓ **无效 JSON 错误提示** - 验证前端对错误输入的提示

## 运行测试

### 安装依赖

```bash
cd /Users/linziwang/PycharmProjects/wordToWord/tests
pip install -r requirements.txt
```

### 运行所有 UI 测试

```bash
pytest tests/ui/test_diff_ui_automation.py -v
```

### 运行特定测试类

```bash
# 只运行对比界面测试
pytest tests/ui/test_diff_ui_automation.py::TestDiffCompareUI -v

# 只运行格式化界面测试
pytest tests/ui/test_diff_ui_automation.py::TestDiffFormatUI -v
```

### 运行特定测试方法

```bash
pytest tests/ui/test_diff_ui_automation.py::TestDiffCompareUI::test_compare_ui_success_basic -v
```

### 生成测试报告

```bash
# HTML 格式报告
pytest tests/ui/test_diff_ui_automation.py --html=report.html --self-contained-html

# 带覆盖率的报告
pytest tests/ui/test_diff_ui_automation.py --html=report.html --self-contained-html -v
```

### 不启用无头模式（可以看到浏览器操作）

```bash
# 修改 conftest.py 中的 options.add_argument('--headless') 注释
pytest tests/ui/test_diff_ui_automation.py -v
```

## 配置说明

### chrome_options fixture

```python
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
```

### 修改浏览器类型

编辑 `conftest.py`，将 Chrome 改为 Firefox：

```python
driver = webdriver.Firefox()
```

## 测试用例说明

### test_compare_ui_success_basic

**目的**: 验证基础对比功能正常工作

**步骤**:
1. 打开 diff 页面
2. 输入左侧 JSON: `{"a": 1, "b": 2}`
3. 输入右侧 JSON: `{"a": 1, "b": 3}`
4. 点击对比按钮
5. 验证结果区域已更新

**预期**: 结果显示区域包含对比结果

### test_compare_ui_invalid_json_error

**目的**: 验证无效 JSON 的错误提示

**步骤**:
1. 打开 diff 页面
2. 输入无效 JSON: `{invalid json}`
3. 点击对比按钮

**预期**: 显示错误提示信息

### test_compare_ui_large_data

**目的**: 验证大数据量对比的性能

**步骤**:
1. 生成 100+ 键值对的 JSON 数据
2. 输入左右两侧相同的 JSON
3. 点击对比按钮

**预期**: 响应时间 < 10 秒，正常显示结果

### test_ui_clear_functionality

**目的**: 验证清空功能正常工作

**步骤**:
1. 输入 JSON 数据
2. 点击清空按钮

**预期**: 输入框内容被清空

### test_ui_copy_result_functionality

**目的**: 验证复制结果功能正常工作

**步骤**:
1. 执行对比操作
2. 点击复制按钮

**预期**: 结果被复制到剪贴板，显示成功提示

## 浏览器配置

### Chrome (默认)

```bash
pip install selenium webdriver-manager
```

### Firefox

```bash
pip install selenium geckodriver
```

## 调试技巧

### 1. 查看浏览器操作

注释掉 `options.add_argument('--headless')`，可以看到浏览器实际操作。

### 2. 添加截图功能

在测试失败时自动截图：

```python
@pytest.fixture(autouse=True)
def take_screenshot_on_failure(request, browser):
    yield
    
    if request.node.rep_setup.failed or request.node.rep_call.failed:
        browser.save_screenshot(f"tests/ui/screenshots/{request.node.name}.png")
```

### 3. 增加等待时间

对于加载较慢的页面，可以增加显式等待：

```python
wait = WebDriverWait(browser, 20)  # 从 10 秒改为 20 秒
```

### 4. 使用隐式等待

```python
browser.implicitly_wait(10)  # 全局隐式等待 10 秒
```

## 常见问题

### Q: "SessionNotCreatedException: Could not start ChromeDriver"
A: 确保已安装 chromedriver，或使用 webdriver-manager：
```bash
pip install selenium webdriver-manager
```

### Q: "TimeoutException: timeout"
A: 增加等待时间或检查页面加载逻辑

### Q: "NoSuchElementException"
A: 检查元素选择器是否正确，或增加等待时间

### Q: UI 测试运行很慢
A: 
- 使用无头模式 (`--headless`)
- 减少截图操作
- 并行运行（但 UI 测试不建议并行）

### Q: 如何调试单个测试？
A: 使用 pytest 的 debug 模式：
```bash
pytest tests/ui/test_diff_ui_automation.py::TestDiffCompareUI::test_compare_ui_success_basic -v -s --headless=false
```

## 持续集成

### GitHub Actions UI 测试示例

```yaml
name: UI Tests

on: [push, pull_request]

jobs:
  ui-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r tests/requirements.txt
      
      - name: Install Chrome
        run: |
          sudo apt-get install -y google-chrome-stable
      
      - name: Run UI tests
        run: |
          pytest tests/ui/test_diff_ui_automation.py -v --headless=false
```

## 维护指南

1. **更新元素选择器**：前端页面结构变更时，更新 By.ID, By.CLASS_NAME 等选择器
2. **添加新测试场景**：在对应测试类中添加新的 `test_` 方法
3. **优化等待时间**：根据实际页面加载速度调整 timeout
4. **更新浏览器版本**：定期更新 selenium 和 chromedriver 版本

## 测试数据准备

如需测试特定场景，可以准备以下 JSON 数据：

```python
# 复杂嵌套结构
complex_data = {
    "users": [
        {"id": 1, "name": "Alice", "roles": ["admin"]},
        {"id": 2, "name": "Bob", "roles": ["user"]}
    ],
    "metadata": {
        "version": "1.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }
}

# 包含特殊字符
special_chars = {
    "text": "你好，世界！🎉",
    "emoji": "😀😁😂"
}

# 大数据量
large_data = {f"key_{i}": f"value_{i}" for i in range(100)}
```

## 联系方式

如有问题，请联系开发团队。
