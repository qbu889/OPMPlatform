#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化测试运行脚本
用于本地运行所有测试，模拟 CI/CD 环境
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80 + "\n")


def run_command(command, description=""):
    """运行命令并返回结果"""
    if description:
        print_header(description)
    
    print(f"执行命令：{' '.join(command)}")
    
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )
    
    # 输出标准输出
    if result.stdout:
        print(result.stdout)
    
    # 输出错误信息
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0


def main():
    """主函数"""
    print_header("Python 自动化测试套件")
    
    # 获取项目根目录
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # 检查 Python 解释器路径
    python_executable = sys.executable
    print(f"当前 Python 解释器：{python_executable}")
    
    # 警告：如果不在项目虚拟环境中
    venv_path = project_root / ".venv"
    if venv_path.exists():
        expected_python = venv_path / "bin" / "python"
        if not Path(python_executable).samefile(expected_python) and \
           str(python_executable) != str(expected_python):
            print(f"\n⚠️  警告：未使用项目虚拟环境!")
            print(f"   当前环境：{python_executable}")
            print(f"   预期环境：{expected_python}")
            print(f"\n💡 建议运行方式:")
            print(f"   cd {project_root}")
            print(f"   source .venv/bin/activate")
            print(f"   python run_tests.py\n")
            # 不退出，继续执行，因为用户可能就是想用其他环境
    
    # 1. 安装依赖
    if not run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        "步骤 1: 升级 pip"
    ):
        print("❌ pip 升级失败")
        return False
    
    # 2. 安装测试依赖
    requirements_files = ["requirements.txt", "requirements-linux.txt"]
    for req_file in requirements_files:
        if (project_root / req_file).exists():
            print(f"\n尝试安装 {req_file}...")
            # 使用 --only-binary 避免编译问题（特别是 numpy）
            success = run_command(
                [sys.executable, "-m", "pip", "install", "-r", req_file, "--only-binary", ":all:"],
                f"步骤 2: 安装 {req_file}"
            )
            if not success:
                print(f"⚠️  警告：{req_file} 安装失败，继续执行...")
                print("💡 某些包可能需要从源码编译，这不影响测试运行")
    
    # 安装测试工具
    if not run_command(
        [sys.executable, "-m", "pip", "install", "pytest", "pytest-cov", "pytest-flask"],
        "步骤 3: 安装测试工具"
    ):
        print("❌ 测试工具安装失败")
        return False
    
    # 3. 运行测试
    print_header("步骤 4: 运行自动化测试")
    
    print("\n💡 提示：跳过需要特定文件、数据库或外部服务的测试")
    print("   只运行基础的单元测试\n")
    
    # 构建 pytest 命令 - 只运行稳定的单元测试
    pytest_cmd = [
        sys.executable, "-m", "pytest",
        # 指定要运行的测试目录和文件
        "test/login_test/test_admin_init.py",
        "test/login_test/test_hash_fix.py",
        "test/login_test/test_login_improvements.py",
        "test/Index_test/",
        "test/kafka/TestKafkaRoutes.py",
        "test/test_main_flow.py",  # 新增：主流程测试
        "test/test_core_logic.py",  # 新增：核心逻辑测试
        "-v",  # 详细输出
        "--tb=short",  # 简短的错误追踪
        "--maxfail=5",  # 最多 5 个失败后停止
        "--disable-warnings",  # 禁用警告
        "-m", "not slow",  # 跳过慢速测试
    ]
    
    # 添加覆盖率选项 - 只生成报告，不设置失败阈值
    pytest_cmd.extend([
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term-missing",
    ])
    
    success = run_command(pytest_cmd, "运行 pytest 测试")
    
    # 4. 显示结果
    print_header("测试执行完成")
    
    if success:
        print("✅ 所有测试通过！")
        print("\n📊 覆盖率报告已生成:")
        print(f"   📁 {project_root}/htmlcov/index.html")
        print("\n💡 提示：在浏览器中打开上面的文件查看详细覆盖率报告")
    else:
        print("❌ 部分测试失败，请查看上面的错误信息")
        print("\n💡 调试建议:")
        print("   1. 检查数据库连接配置")
        print("   2. 确认所有依赖已正确安装")
        print("   3. 查看具体的测试失败原因")
    
    return success


if __name__ == "__main__":
    """
    运行命令一：/Users/linziwang/PycharmProjects/wordToWord/run_tests_quick.sh
    运行命令二：
        cd /Users/linziwang/PycharmProjects/wordToWord
        source .venv/bin/activate
        python run_tests.py
    """
    success = main()
    sys.exit(0 if success else 1)
