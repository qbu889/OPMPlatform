#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kafka生成器API测试报告生成器
生成美观的HTML测试报告
"""
import sys
import os
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

def print_header(text):
    """打印漂亮的标题"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)

def generate_report(test_path=None, output_dir=None):
    """生成测试报告"""
    print_header("Kafka生成器API测试报告生成器")
    
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    venv_path = project_root / ".venv"
    if venv_path.exists():
        python_executable = venv_path / "bin" / "python"
        print(f"使用虚拟环境: {python_executable}")
    else:
        python_executable = sys.executable
        print(f"使用系统Python: {python_executable}")
    
    if test_path is None:
        test_path = "test/kafka/test_kafka_api_complete.py"
    
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"test_reports/report_{timestamp}"
    
    output_path = project_root / output_dir
    output_path.mkdir(parents=True, exist_ok=True)
    
    report_file = output_path / "report.html"
    junit_file = output_path / "results.xml"
    
    print(f"\n测试文件: {test_path}")
    print(f"输出目录: {output_path}")
    print(f"报告文件: {report_file}")
    
    pytest_cmd = [
        str(python_executable), "-m", "pytest",
        test_path,
        "-v",
        "--tb=short",
        "--maxfail=10",
        "--html=" + str(report_file),
        "--self-contained-html",
        "--junitxml=" + str(junit_file),
        "-p", "no:warnings",
        "--override-ini=addopts=",
    ]
    
    print("\n开始执行测试...")
    print("-" * 80)
    
    result = subprocess.run(
        pytest_cmd,
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    print(result.stdout)
    if result.stderr:
        print("stderr:", result.stderr[:500])
    
    print("-" * 80)
    
    if result.returncode == 0:
        print("测试全部通过!")
    else:
        print(f"部分测试失败 (退出码: {result.returncode})")
    
    customize_report(report_file)
    
    print(f"\n测试报告已生成: {report_file}")
    print(f"JUnit结果文件: {junit_file}")
    
    show_report_summary(report_file)
    
    return report_file

def customize_report(report_path):
    """自定义报告样式"""
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        custom_css = """
        <style>
            :root {
                --primary-color: #4f46e5;
                --success-color: #10b981;
                --warning-color: #f59e0b;
                --danger-color: #ef4444;
                --bg-color: #0f172a;
                --card-bg: #1e293b;
                --text-color: #f1f5f9;
                --border-color: #334155;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
                min-height: 100vh;
                color: var(--text-color);
            }
            
            .results-table {
                border-collapse: separate;
                border-spacing: 0;
                width: 100%;
                background: var(--card-bg);
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            }
            
            .results-table th {
                background: linear-gradient(135deg, var(--primary-color) 0%, #6366f1 100%);
                color: white;
                font-weight: 600;
                padding: 14px 16px;
                text-align: left;
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .results-table td {
                padding: 12px 16px;
                border-bottom: 1px solid var(--border-color);
                font-size: 14px;
            }
            
            .results-table tr:last-child td {
                border-bottom: none;
            }
            
            .results-table tr:hover td {
                background: rgba(79, 70, 229, 0.1);
            }
            
            .passed {
                background: rgba(16, 185, 129, 0.15);
                color: var(--success-color);
                padding: 4px 12px;
                border-radius: 20px;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 12px;
            }
            
            .failed {
                background: rgba(239, 68, 68, 0.15);
                color: var(--danger-color);
                padding: 4px 12px;
                border-radius: 20px;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 12px;
            }
            
            .error {
                background: rgba(245, 158, 11, 0.15);
                color: var(--warning-color);
                padding: 4px 12px;
                border-radius: 20px;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 12px;
            }
            
            .summary {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .summary-card {
                background: var(--card-bg);
                border-radius: 12px;
                padding: 24px;
                text-align: center;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
                border: 1px solid var(--border-color);
            }
            
            .summary-card h3 {
                font-size: 14px;
                color: #94a3b8;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .summary-card .value {
                font-size: 36px;
                font-weight: 700;
            }
            
            .summary-card.passed-card .value { color: var(--success-color); }
            .summary-card.failed-card .value { color: var(--danger-color); }
            .summary-card.total-card .value { color: var(--primary-color); }
            .summary-card.time-card .value { color: var(--warning-color); }
            
            .test-name {
                font-family: 'JetBrains Mono', monospace;
                font-size: 13px;
                color: #cbd5e1;
            }
            
            .test-class {
                color: #94a3b8;
                font-size: 12px;
            }
            
            .header {
                background: var(--card-bg);
                padding: 24px 32px;
                border-radius: 12px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            }
            
            .header h1 {
                font-size: 28px;
                margin: 0 0 8px 0;
                background: linear-gradient(135deg, var(--primary-color) 0%, #818cf8 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .header p {
                color: #94a3b8;
                margin: 0;
                font-size: 14px;
            }
            
            .footer {
                text-align: center;
                padding: 20px;
                color: #64748b;
                font-size: 12px;
            }
        </style>
        """
        
        content = content.replace('</head>', custom_css + '</head>')
        content = content.replace(
            '<h1>Test Report</h1>',
            '<div class="header"><h1>Kafka生成器API测试报告</h1><p>自动化接口测试结果</p></div>'
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("报告样式已美化")
        
    except Exception as e:
        print(f"美化报告失败: {e}")

def show_report_summary(report_file):
    """显示报告摘要"""
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        
        total_match = re.search(r'Total: (\d+)', content)
        passed_match = re.search(r'Passed: (\d+)', content)
        failed_match = re.search(r'Failed: (\d+)', content)
        time_match = re.search(r'Time: ([\d.]+)s', content)
        
        print("\n测试报告摘要:")
        print("-" * 40)
        if total_match:
            print(f"总测试数: {total_match.group(1)}")
        if passed_match:
            print(f"通过: {passed_match.group(1)}")
        if failed_match:
            print(f"失败: {failed_match.group(1)}")
        if time_match:
            print(f"耗时: {time_match.group(1)}秒")
        print("-" * 40)
        
    except Exception as e:
        print(f"读取报告摘要失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Kafka生成器API测试报告生成器',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '-t', '--test',
        default='test/kafka/test_kafka_api_complete.py',
        help='测试文件路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='输出目录'
    )
    
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='列出可用的测试文件'
    )
    
    args = parser.parse_args()
    
    if args.list:
        print_header("可用测试文件")
        test_files = sorted(Path('test').rglob('*.py'))
        for f in test_files:
            print(f"  {f}")
        return
    
    report_file = generate_report(args.test, args.output)
    
    try:
        import webbrowser
        webbrowser.open('file://' + str(report_file))
        print("报告已在浏览器中打开")
    except Exception as e:
        print(f"无法自动打开浏览器，请手动打开: {report_file}")

if __name__ == "__main__":
    main()
