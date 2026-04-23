# 钉钉推送系统测试

## 测试文件结构

```
test/dingtalk_push/
├── __init__.py                          # 模块初始化
├── test_dingtalk_push_config.py         # 配置管理API测试
├── test_dingtalk_push_integration.py    # 集成测试（完整流程）
└── run_tests.py                         # 测试运行脚本
```

## 测试覆盖范围

### 1. 配置管理测试 (test_dingtalk_push_config.py)

- ✅ 创建推送配置
- ✅ 获取配置列表（分页、筛选）
- ✅ 获取配置详情
- ✅ 更新配置
- ✅ 启用/禁用配置
- ✅ 按分类和状态筛选
- ✅ 删除配置

### 2. 集成测试 (test_dingtalk_push_integration.py)

- ✅ 创建配置 -> 预览模板 -> 手动推送 -> 查看历史 -> 统计分析
- ✅ 完整的业务流程验证
- ✅ 数据一致性检查

## 运行测试

### 方式一：运行所有测试

```bash
cd /Users/linziwang/PycharmProjects/wordToWord
python test/dingtalk_push/run_tests.py
```

### 方式二：运行单个测试文件

```bash
# 配置管理测试
python -m pytest test/dingtalk_push/test_dingtalk_push_config.py -v

# 集成测试
python -m pytest test/dingtalk_push/test_dingtalk_push_integration.py -v
```

### 方式三：使用 unittest

```bash
python -m unittest test.dingtalk_push.test_dingtalk_push_config -v
python -m unittest test.dingtalk_push.test_dingtalk_push_integration -v
```

## 测试前置条件

1. **数据库表已创建**
   ```bash
   mysql -u root -p your_database < sql/create_dingtalk_push_tables.sql
   ```

2. **环境变量已配置**（在 `.env` 文件中）
   ```env
   WEBHOOK_ENCRYPTION_KEY=dGVzdF9rZXlfZm9yX2Rldl9vbmx5XzEyMzQ1Njc4OTA=
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=your_database
   ```

3. **后端服务已启动**
   ```bash
   python app.py
   ```

## 测试输出示例

```
================================================================================
钉钉推送系统 - 自动化测试
================================================================================

test_01_create_config (test_dingtalk_push_config.TestDingTalkPushConfig)
测试创建配置 ... 
📝 测试: 创建推送配置
✅ 配置创建成功，ID: 1
ok

test_02_get_config_list (test_dingtalk_push_config.TestDingTalkPushConfig)
测试获取配置列表 ... 
📋 测试: 获取配置列表
✅ 获取到 1 条配置
ok

...

================================================================================
测试总结
================================================================================
总测试数: 12
成功: 12
失败: 0
错误: 0
================================================================================
```

## 注意事项

1. **测试数据隔离**：每个测试类会在结束时自动清理创建的测试数据
2. **Webhook 测试**：由于测试使用的是无效的 Webhook URL，推送执行会失败，但 API 调用本身应该成功
3. **定时任务**：测试环境不会实际触发定时任务，只验证配置是否正确保存
4. **数据库依赖**：测试需要真实的 MySQL 数据库连接

## 常见问题

### Q: 测试失败提示 "Connection refused"
A: 确保后端服务已启动，并且数据库连接配置正确

### Q: 测试失败提示 "Table doesn't exist"
A: 先执行 SQL 脚本创建数据库表

### Q: 如何跳过某些测试？
A: 使用 `@unittest.skip("原因")` 装饰器

## 持续集成

可以将测试添加到 CI/CD 流程中：

```yaml
# .github/workflows/python-tests.yml
name: DingTalk Push Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python test/dingtalk_push/run_tests.py
```
