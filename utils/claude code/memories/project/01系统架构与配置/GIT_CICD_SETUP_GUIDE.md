# Git CI/CD 自动化测试配置说明

## 📋 目录
- [概述](#概述)
- [快速开始](#快速开始)
- [本地运行测试](#本地运行测试)
- [GitHub Actions 配置](#github-actions-配置)
- [测试覆盖率](#测试覆盖率)
- [常见问题](#常见问题)

---

## 概述

本项目已配置完整的 Git CI/CD 自动化测试流程，使用 **GitHub Actions** 作为持续集成工具。

### 主要功能
✅ 代码提交时自动触发测试  
✅ 多 Python 版本兼容性测试 (3.9, 3.10, 3.11)  
✅ 自动生成测试覆盖率报告  
✅ MySQL 数据库集成测试支持  
✅ 测试报告上传和存档  

---

## 快速开始

### 1. 本地环境准备

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-linux.txt

# 安装测试工具
pip install pytest pytest-cov pytest-flask
```

### 2. 运行自动化测试

#### 方法一：使用运行脚本（推荐）
```bash
python run_tests.py
```

#### 方法二：直接使用 pytest
```bash
pytest test/ -v --cov=. --cov-report=html
```

---

## 本地运行测试

### 完整测试套件
```bash
python run_tests.py
```

这个脚本会：
1. 自动升级 pip
2. 安装所有依赖
3. 运行所有测试用例
4. 生成 HTML 格式的覆盖率报告

### 选择性运行测试

#### 运行特定测试文件
```bash
pytest test/kafka/test_kafka_api.py -v
```

#### 运行特定类型的测试
```bash
# 只运行单元测试
pytest test/ -v -m unit

# 只运行集成测试
pytest test/ -v -m integration

# 跳过慢速测试
pytest test/ -v -m "not slow"
```

#### 运行特定目录的测试
```bash
# Kafka 相关测试
pytest test/kafka/ -v

# FPA 相关测试
pytest test/fpa/ -v

# 登录认证测试
pytest test/login_test/ -v
```

### 查看测试覆盖率
```bash
# 终端显示覆盖率
pytest test/ --cov=. --cov-report=term

# 生成 HTML 报告
pytest test/ --cov=. --cov-report=html

# 打开覆盖率报告（Mac/Linux）
open htmlcov/index.html

# Windows
start htmlcov\index.html
```

---

## GitHub Actions 配置

### 触发条件

CI/CD 流程会在以下情况自动触发：

1. **Push 到主分支**
   - `main`
   - `master`
   - `develop`

2. **Pull Request**
   - 针对上述分支的 PR

### 工作流程

`.github/workflows/python-tests.yml` 定义了完整的 CI/CD 流程：

```yaml
on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master, develop ]
```

### CI/CD 执行步骤

1. **Checkout Code** - 检出代码
2. **Setup Python** - 设置 Python 环境（多版本）
3. **Cache Dependencies** - 缓存 pip 包
4. **Install Dependencies** - 安装依赖
5. **Create Test Config** - 创建测试配置文件
6. **Run Tests** - 执行 pytest 测试
7. **Upload Coverage** - 上传覆盖率到 Codecov
8. **Archive Results** - 存档测试结果

### MySQL 数据库支持

CI/CD 环境会自动启动 MySQL 8.0 容器：

```yaml
services:
  mysql:
    image: mysql:8.0
    env:
      MYSQL_ROOT_PASSWORD: 12345678
      MYSQL_DATABASE: test_db
    ports:
      - 3306:3306
```

测试中的数据库连接配置：
- Host: `localhost`
- Port: `3306`
- User: `root`
- Password: `12345678`
- Database: `test_db`

---

## 测试覆盖率

### 覆盖率配置

项目使用 `.coveragerc` 配置覆盖率统计：

- **目标覆盖率**: 30%（最低要求）
- **排除目录**: 
  - 虚拟环境 (.venv/)
  - 测试文件 (test/)
  - 构建文件 (build/, dist/)
  - 第三方库 (omlx/)
  - 脚本文件 (scripts/)

### 查看覆盖率报告

运行测试后，HTML 报告会生成在 `htmlcov/` 目录：

```bash
# 在浏览器中打开
open htmlcov/index.html  # Mac
start htmlcov\index.html # Windows
```

报告包含：
- 每个文件的覆盖率
- 未覆盖的代码行
- 代码执行统计

---

## 常见问题

### Q1: 测试失败怎么办？

**检查步骤：**
1. 确认所有依赖已安装
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-linux.txt
   ```

2. 检查数据库连接
   ```bash
   # 本地需要有 MySQL 服务
   mysql -u root -p
   ```

3. 查看详细错误信息
   ```bash
   pytest test/ -v --tb=long
   ```

### Q2: 如何跳过某些测试？

使用 pytest 标记：

```python
import pytest

@pytest.mark.slow
def test_something_slow():
    # 这个测试可以用 -m "not slow" 跳过
    pass

@pytest.mark.integration
def test_integration():
    # 集成测试，可以选择性运行
    pass
```

### Q3: 如何在本地模拟 CI 环境？

```bash
# 创建测试环境
cp .env.example .env

# 编辑 .env 文件，设置测试配置
cat > .env << EOF
FLASK_ENV=testing
SECRET_KEY=test-secret-key
USE_MYSQL=true
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=12345678
LOG_LEVEL=ERROR
EOF

# 运行测试
python run_tests.py
```

### Q4: 如何优化测试速度？

1. **跳过慢速测试**
   ```bash
   pytest test/ -v -m "not slow"
   ```

2. **并行执行测试**
   ```bash
   pip install pytest-xdist
   pytest test/ -n auto
   ```

3. **使用缓存**
   ```bash
   pytest test/ --cache-show
   pytest test/ --cache-clear  # 清除缓存
   ```

### Q5: GitHub Actions 失败如何调试？

1. **查看 GitHub Actions 日志**
   - 进入 GitHub 仓库
   - Actions 标签
   - 点击失败的 workflow
   - 查看详细日志

2. **本地复现问题**
   ```bash
   # 使用与 CI 相同的 Python 版本
   python3.9 -m venv .venv
   source .venv/bin/activate
   
   # 安装相同依赖
   pip install pytest pytest-cov pytest-flask
   
   # 运行测试
   pytest test/ -v
   ```

---

## 最佳实践

### 1. 编写测试用例

```python
import pytest
from app import create_app

def test_example():
    """简单的测试示例"""
    assert 1 + 1 == 2

@pytest.mark.unit
def test_unit_example():
    """单元测试"""
    result = some_function()
    assert result is not None

@pytest.mark.integration
def test_integration_example():
    """集成测试"""
    response = client.get('/api/data')
    assert response.status_code == 200
```

### 2. 使用 Fixtures

```python
import pytest

@pytest.fixture
def sample_data():
    """测试数据夹具"""
    return {"key": "value"}

def test_with_fixture(sample_data):
    """使用夹具的测试"""
    assert sample_data["key"] == "value"
```

### 3. 参数化测试

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_multiplication(input, expected):
    """参数化测试"""
    assert input * 2 == expected
```

---

## 相关文件

- `.github/workflows/python-tests.yml` - GitHub Actions 工作流配置
- `pytest.ini` - Pytest 配置文件
- `.coveragerc` - 覆盖率配置文件
- `run_tests.py` - 本地测试运行脚本
- `.gitignore` - Git 忽略文件配置

---

## 支持

如有问题，请：
1. 查看本文档
2. 检查 GitHub Actions 日志
3. 联系开发团队

🎉 Happy Testing!
