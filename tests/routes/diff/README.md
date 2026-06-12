# diff_routes.py 接口测试用例

## 目录结构

```
tests/routes/diff/
├── test_diff_routes.py      # 接口测试用例
├── conftest.py             # pytest 配置
├── pytest.ini              # pytest 配置文件
└── README.md               # 说明文档
```

## 测试覆盖范围

### API 接口测试 (test_diff_routes.py)

#### 1. JSON 对比接口 (/api/diff/compare)

**正常场景：**
- ✓ 基础 JSON 对比成功
- ✓ 带选项的 JSON 对比（strict_mode, ignore_case, ignore_whitespace）
- ✓ 复杂嵌套结构对比
- ✓ 空对象对比
- ✓ 相同 JSON 对比

**异常场景：**
- ✓ 请求体为空
- ✓ 缺少左侧/右侧 JSON
- ✓ 左侧/右侧 JSON 格式错误
- ✓ 非 JSON 格式数据
- ✓ 特殊字符处理

**边界条件：**
- ✓ 超大 JSON 数据（1000+ 键值对）
- ✓ 深层嵌套 JSON
- ✓ 数组对比
- ✓ 混合数据类型

**性能测试：**
- ✓ 响应时间监控（<5s）

#### 2. JSON 格式化接口 (/api/diff/format)

**正常场景：**
- ✓ 基础 JSON 格式化
- ✓ 中文内容格式化
- ✓ 嵌套 JSON 格式化

**异常场景：**
- ✓ 缺少 JSON 数据
- ✓ 无效 JSON
- ✓ 空字符串

### UI 自动化测试 (test_diff_ui_automation.py)

#### 1. JSON 对比界面

**功能测试：**
- ✓ 基础对比功能
- ✓ 带选项的对比（ignore_case 等）
- ✓ 复杂数据对比

**异常处理：**
- ✓ 无效 JSON 错误提示
- ✓ 空字段提示
- ✓ 特殊字符处理

**边界测试：**
- ✓ 大数据量对比（100+ 键值对）
- ✓ 深层嵌套 JSON

**UI 交互：**
- ✓ 清空功能
- ✓ 复制结果功能
- ✓ JSON 格式化功能

#### 2. JSON 格式化界面

**功能测试：**
- ✓ JSON 格式化成功
- ✓ 无效 JSON 错误提示

## 运行测试

### 安装依赖

```bash
cd /Users/linziwang/PycharmProjects/wordToWord/tests
pip install -r requirements.txt
```

### 运行接口测试

```bash
# 运行所有测试
pytest tests/routes/diff/test_diff_routes.py -v

# 运行特定测试类
pytest tests/routes/diff/test_diff_routes.py::TestDiffCompareAPI -v

# 运行特定测试方法
pytest tests/routes/diff/test_diff_routes.py::TestDiffCompareAPI::test_compare_success_basic -v

# 生成测试报告
pytest tests/routes/diff/test_diff_routes.py --html=report.html --self-contained-html

# 生成覆盖率报告
pytest tests/routes/diff/test_diff_routes.py --cov=. --cov-report=html
```

### 运行 UI 自动化测试

**前提条件：**
- 确保 Chrome 浏览器已安装
- 确保 chromedriver 已配置（或使用 webdriver-manager 自动管理）

```bash
# 运行所有 UI 测试
pytest tests/ui/test_diff_ui_automation.py -v

# 运行特定测试类
pytest tests/ui/test_diff_ui_automation.py::TestDiffCompareUI -v

# 不启用无头模式（可以看到浏览器操作）
pytest tests/ui/test_diff_ui_automation.py -v --headless=false

# 生成测试报告
pytest tests/ui/test_diff_ui_automation.py --html=report.html --self-contained-html
```

### 并行测试

```bash
# 使用 pytest-xdist 并行运行（4 个进程）
pytest tests/routes/diff/test_diff_routes.py -n 4 -v

# UI 测试并行（注意：UI 测试通常不建议并行）
pytest tests/ui/test_diff_ui_automation.py -n 2 -v
```

## 测试用例说明

### 正常场景 (test_compare_success_*)

- **目的**：验证接口在正常输入下的正确行为
- **预期结果**：返回 200 状态码，success=true

### 异常场景 (test_compare_invalid_*, test_compare_empty_*)

- **目的**：验证接口对错误输入的处理能力
- **预期结果**：返回 400 状态码，success=false

### 边界条件 (test_compare_*, test_compare_ui_large_data, test_compare_ui_deeply_nested)

- **目的**：验证接口在极端情况下的稳定性
- **预期结果**：正常处理，不崩溃

### 性能测试 (test_compare_performance)

- **目的**：监控接口响应时间
- **预期结果**：响应时间 < 5 秒

## 配置说明

### conftest.py

- `client`: Flask 测试客户端
- `valid_json_data`: 生成有效的测试 JSON 数据

### pytest.ini

```ini
[pytest]
testpaths = tests/routes/diff
python_files = test_*.py
timeout = 30
```

## 常见问题

### Q: 测试失败，提示"连接被拒绝"？
A: 确保后端服务已启动：`python start_all_prod.sh`

### Q: UI 测试找不到浏览器？
A: 安装 chromedriver：`pip install webdriver-manager`

### Q: 如何添加新的测试用例？
A: 在对应的测试类中添加 `test_` 开头的方法

### Q: 如何跳过某些测试？
A: 使用 `@pytest.mark.skip` 装饰器

```python
@pytest.mark.skip("暂时跳过")
def test_something():
    pass
```

## 持续集成

### GitHub Actions 示例

```yaml
name: API Tests

on: [push, pull_request]

jobs:
  test:
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
      
      - name: Run API tests
        run: |
          pytest tests/routes/diff/test_diff_routes.py -v
      
      - name: Run UI tests
        run: |
          pytest tests/ui/test_diff_ui_automation.py -v
```

## 维护指南

1. **更新测试数据**：根据接口变更更新 `valid_json_data` fixture
2. **添加新测试场景**：在对应测试类中添加新的 `test_` 方法
3. **优化性能**：定期运行性能测试，监控响应时间变化
4. **更新文档**：接口变更时同步更新 README.md

## 联系方式

如有问题，请联系开发团队。
