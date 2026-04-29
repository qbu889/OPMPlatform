# Kafka生成器测试指南

## 测试文件说明

### 1. test_kafka_complete.py - 核心功能测试
**覆盖范围**：
- ✅ FP字段生成（格式、唯一性、一致性）
- ✅ 时间字段计算（DELAY_TIME提取、默认值、用户覆盖）
- ✅ 字段映射逻辑（基本映射、嵌套字段、缺失字段处理）
- ✅ 特殊字段处理（忽略数据库配置、ORG_TEXT生成）
- ✅ 自定义字段覆盖
- ✅ 边界情况（空数据、无效JSON、None值、超大延迟时间）
- ✅ 集成测试（真实数据、性能测试）

**运行方式**：
```bash
pytest test/kafka/test_kafka_complete.py -v
```

### 2. test_kafka_api.py - API接口测试
**覆盖范围**：
- ✅ 生成接口（有效数据、自定义字段、无效数据）
- ✅ 字段元数据接口
- ✅ 字段顺序接口
- ✅ 历史记录接口
- ✅ 字段缓存接口
- ✅ 字段历史接口
- ✅ 字典数据接口
- ✅ 测试前缀功能
- ✅ NETWORK_TYPE_TOP=20特殊处理
- ✅ 并发请求处理
- ✅ 错误处理（数据库失败、格式错误、空请求）

**运行方式**：
```bash
pytest test/kafka/test_kafka_api.py -v
```

### 3. test_kafka_generator.py - 原有测试脚本
**用途**：快速手动测试，使用真实ES数据验证生成结果

**运行方式**：
```bash
python test/kafka/test_kafka_generator.py
```

## CI/CD自动化测试

### 触发条件
- 推送到 `q/*` 分支时自动运行
- 推送到 `main/master/develop` 分支时自动运行
- 创建Pull Request到主分支时自动运行

### 测试流程
1. **环境准备**
   - 启动MySQL 8.0服务容器
   - 安装Python 3.13
   - 安装项目依赖和测试依赖

2. **Kafka专项测试**
   ```bash
   # 运行核心功能测试
   pytest test/kafka/test_kafka_complete.py
   
   # 运行API接口测试
   pytest test/kafka/test_kafka_api.py
   ```

3. **全量测试**
   ```bash
   pytest test/ --cov=. --cov-report=xml
   ```

4. **覆盖率报告**
   - 生成XML格式的覆盖率报告
   - 上传到Codecov
   - 生成HTML报告作为artifact保存

### 查看测试结果
1. **GitHub Actions页面**
   - 访问: https://github.com/your-repo/actions
   - 查看最近的工作流运行状态

2. **覆盖率报告**
   - HTML报告会在workflow完成后作为artifact下载
   - Codecov提供在线覆盖率可视化

3. **本地查看详细日志**
   ```bash
   # 运行测试并显示详细输出
   pytest test/kafka/ -v --tb=long
   
   # 只显示失败的测试
   pytest test/kafka/ -v --tb=short --maxfail=5
   ```

## 本地运行测试

### 前置条件
```bash
# 安装测试依赖
pip install pytest pytest-cov pytest-flask

# 确保MySQL服务运行（用于API测试）
# 或设置环境变量跳过数据库测试
export USE_MYSQL=false
```

### 运行所有Kafka测试
```bash
# 方式1：运行整个kafka测试目录
pytest test/kafka/ -v

# 方式2：分别运行两个测试文件
pytest test/kafka/test_kafka_complete.py -v
pytest test/kafka/test_kafka_api.py -v

# 方式3：运行并生成覆盖率报告
pytest test/kafka/ -v --cov=routes.kafka --cov-report=html
```

### 运行特定测试类
```bash
# 只测试FP生成
pytest test/kafka/test_kafka_complete.py::TestFPGeneration -v

# 只测试时间字段
pytest test/kafka/test_kafka_complete.py::TestTimeFields -v

# 只测试API接口
pytest test/kafka/test_kafka_api.py::TestKafkaGeneratorAPI -v
```

### 运行单个测试方法
```bash
pytest test/kafka/test_kafka_complete.py::TestFPGeneration::test_fp_format -v
```

## 测试覆盖的功能点

### 核心算法测试 (test_kafka_complete.py)
| 测试类别 | 测试点数量 | 说明 |
|---------|----------|------|
| FP字段生成 | 3 | 格式验证、唯一性、一致性 |
| 时间字段 | 5 | DELAY_TIME提取、默认值、用户覆盖、一致性、格式 |
| 字段映射 | 4 | 基本映射、嵌套字段、缺失字段、顺序保持 |
| 特殊字段 | 2 | 忽略DB配置、ORG_TEXT生成 |
| 自定义字段 | 1 | 覆盖自动生成值 |
| 边界情况 | 5 | 空数据、无效JSON、None值、超大延迟、零延迟 |
| 集成测试 | 2 | 真实数据、性能测试 |
| **总计** | **22** | **核心功能全覆盖** |

### API接口测试 (test_kafka_api.py)
| 测试类别 | 测试点数量 | 说明 |
|---------|----------|------|
| 生成接口 | 6 | 有效数据、自定义字段、无效JSON、缺少字段、测试前缀、特殊专业 |
| 元数据接口 | 2 | 字段元数据、字段顺序 |
| 历史相关 | 3 | 历史记录、字段缓存、字段历史 |
| 字典接口 | 1 | 字典数据查询 |
| 并发测试 | 1 | 10个并发请求 |
| 错误处理 | 3 | DB失败、格式错误、空请求 |
| **总计** | **16** | **API接口全覆盖** |

### 总体覆盖率目标
- **代码行覆盖率**: ≥ 80%
- **分支覆盖率**: ≥ 75%
- **函数覆盖率**: ≥ 90%

## 常见问题

### Q1: 测试失败提示数据库连接错误
**解决方案**：
```bash
# 方案1：启动MySQL服务
docker run -d --name mysql-test -e MYSQL_ROOT_PASSWORD=12345678 -p 3306:3306 mysql:8.0

# 方案2：设置环境变量跳过DB测试
export USE_MYSQL=false
```

### Q2: 某些测试在CI中通过，本地失败
**原因**：可能是时区差异或随机数种子不同
**解决方案**：
```bash
# 设置统一的时区
export TZ=Asia/Shanghai

# 使用固定的随机种子（在测试代码中）
import random
random.seed(42)
```

### Q3: 如何添加新的测试用例
**步骤**：
1. 确定测试类型（核心功能 or API接口）
2. 在对应的测试文件中添加测试类和方法
3. 使用描述性的方法名（test_开头）
4. 添加清晰的docstring说明测试目的
5. 运行测试验证通过
6. 提交代码时CI会自动运行

### Q4: 如何提高测试覆盖率
**建议**：
1. 使用 `--cov-report=term-missing` 查看未覆盖的行
2. 针对未覆盖的分支添加测试用例
3. 特别关注异常处理和边界情况
4. 使用mock模拟外部依赖（数据库、API调用）

## 持续改进

### 待补充的测试
- [ ] 前端Vue组件的单元测试
- [ ] 字段字典数据的完整性测试
- [ ] 大数据量性能测试（>10MB ES数据）
- [ ] 内存泄漏检测
- [ ] 安全测试（SQL注入、XSS等）

### 测试优化建议
1. **并行执行**：使用 `pytest-xdist` 插件并行运行测试
2. **测试数据管理**：建立统一的测试数据集
3. **Mock优化**：减少对外部服务的依赖
4. **快照测试**：对生成的JSON结构进行快照比对

## 联系与支持

如有测试相关问题，请：
1. 查看测试代码中的注释和docstring
2. 检查GitHub Actions的运行日志
3. 联系项目维护者
