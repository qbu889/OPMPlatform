# 快速运行测试指南

## 🚀 最简单的方法

### Mac/Linux
```bash
# 1. 激活项目虚拟环境
source .venv/bin/activate

# 2. 安装测试依赖
pip install pytest pytest-cov pytest-flask

# 3. 运行测试
python run_tests.py
```

### Windows
```cmd
REM 1. 激活项目虚拟环境
.venv\Scripts\activate

REM 2. 安装测试依赖
pip install pytest pytest-cov pytest-flask

REM 3. 运行测试
python run_tests.py
```

---

## ⚠️ 注意事项

### 1. 使用正确的虚拟环境

**错误示例：**
```bash
# ❌ 不要使用其他项目的虚拟环境
/Users/linziwang/PycharmProjects/Api_Auto_Test_Excel/.venv1/bin/python
```

**正确示例：**
```bash
# ✅ 使用本项目的虚拟环境
cd /Users/linziwang/PycharmProjects/wordToWord
source .venv/bin/activate
```

### 2. 如果还没有虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 安装测试工具
pip install pytest pytest-cov pytest-flask
```

---

## 📝 运行测试的几种方式

### 方式一：使用运行脚本（推荐）
```bash
python run_tests.py
```

### 方式二：直接使用 pytest
```bash
pytest test/ -v --cov=. --cov-report=html
```

### 方式三：运行特定测试
```bash
# 只运行 Kafka 测试
pytest test/kafka/ -v

# 只运行 FPA 测试
pytest test/fpa/ -v

# 只运行登录测试
pytest test/login_test/ -v
```

---

## 📊 查看测试覆盖率报告

```bash
# 生成 HTML 报告后，在浏览器中打开
open htmlcov/index.html  # Mac
start htmlcov\index.html # Windows
```

---

## 🔧 常见问题

### Q: 依赖安装失败怎么办？

**A:** 某些包（如 numpy）可能需要编译，确保已安装 Xcode Command Line Tools（Mac）或 Visual C++ Build Tools（Windows）。

```bash
# Mac: 安装 Xcode Command Line Tools
xcode-select --install

# 或者使用预编译的 wheel 包
pip install numpy --only-binary :all:
```

### Q: 提示找不到模块怎么办？

**A:** 确保已激活正确的虚拟环境并安装了所有依赖。

```bash
# 检查当前 Python 路径
which python  # Mac/Linux
where python  # Windows

# 重新安装依赖
pip install -r requirements.txt
```

### Q: 如何跳过某些测试？

**A:** 使用 pytest 标记。

```bash
# 跳过慢速测试
pytest test/ -v -m "not slow"

# 只运行单元测试
pytest test/ -v -m unit
```

---

## 🎯 成功标志

当你看到以下输出时，表示测试配置成功：

```
================================================================================
 测试执行完成
================================================================================

✅ 所有测试通过！

📊 覆盖率报告已生成:
   📁 /path/to/project/htmlcov/index.html
```

---

## 📚 更多文档

详细文档请查看：`docs/GIT_CICD_SETUP_GUIDE.md`
