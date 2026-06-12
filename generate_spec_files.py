"""
将 Python 测试转换为 Playwright .spec.ts 文件
"""

import os
import re
from pathlib import Path


def python_to_typescript(python_code: str, test_name: str) -> str:
    """将 Python 测试代码转换为 TypeScript/Playwright Codegen 格式"""
    
    # 提取测试函数名
    func_match = re.search(r'def (\w+)\(self, page\):', python_code)
    if not func_match:
        return ""
    
    ts_test_name = func_match.group(1)
    
    # 转换 locator 选择器为 .spec.ts 格式
    ts_code = f"""// Auto-generated from Python test: {ts_test_name}
import {{ test, expect }} from '@playwright/test';

test('{ts_test_name}', async ({{ page }}) => {{
"""
    
    # 转换 locator("...") 为更简洁的格式
    lines = python_code.split('\n')
    in_function = False
    
    for line in lines:
        # 跳过 Python 函数定义和 docstring
        if 'def test_' in line and '(self, page):' in line:
            continue
        
        if '"""' in line and not in_function:
            continue
            
        # 提取测试函数内容
        if '"""' in line and in_function:
            continue
            
        # 转换 expect(page).to_have_url() -> page.goto() + expect(page).toHaveURL()
        if 'expect(page).to_have_url(' in line:
            url_match = re.search(r'"([^"]+)"', line)
            if url_match:
                ts_code += f"    await page.goto('{url_match.group(1)}');\n"
            continue
            
        # 转换 expect(page).to_have_title() -> expect(page).toHaveTitle()
        if 'expect(page).to_have_title(' in line:
            title_match = re.search(r'"([^"]+)"', line)
            if title_match:
                ts_code += f"    expect(page).toHaveTitle('{title_match.group(1)}');\n"
            continue
            
        # 转换 page.locator("...").to_be_visible() -> expect(...).toBeVisible()
        if 'expect(page.locator(' in line:
            selector_match = re.search(r'page\.locator\("([^"]+)"\)', line)
            if selector_match:
                selector = selector_match.group(1)
                ts_code += f"    expect(page.locator('{selector}')).toBeVisible();\n"
            continue
            
        # 转换 page.locator("...").count() > 0 -> page.locator(...).count() === 1
        if 'page.locator(' in line and '.count()' in line:
            selector_match = re.search(r'page\.locator\("([^"]+)"\)', line)
            if selector_match:
                selector = selector_match.group(1)
                ts_code += f"    const count = await page.locator('{selector}').count();\n"
            continue
            
        # 转换 expect(...).to_be_visible() -> expect(...).toBeVisible()
        if 'expect(' in line and '.to_be_visible()' in line:
            selector_match = re.search(r'expect\(([^)]+)\)', line)
            if selector_match:
                selector = selector_match.group(1).strip()
                ts_code += f"    expect({selector}).toBeVisible();\n"
            continue
            
        # 转换 page.click('button:has-text("...")') -> page.click('text=...')
        if 'page.click(' in line and ':has-text' in line:
            text_match = re.search(r':has-text\("([^"]+)"\)', line)
            if text_match:
                ts_code += f"    await page.click('text={text_match.group(1)}');\n"
            continue
            
        # 转换 page.click('text=...') -> page.click('text=...')
        if 'page.click("text=' in line:
            text_match = re.search(r'text=([^"]+)"', line)
            if text_match:
                ts_code += f"    await page.click('text={text_match.group(1)}');\n"
            continue
            
        # 转换 page.locator("textarea") -> page.locator('textarea')
        if 'page.locator("textarea")' in line:
            ts_code += f"    const textarea = page.locator('textarea');\n"
            continue
            
        # 转换 page.evaluate("el => el.value") -> textarea.inputValue()
        if 'page.evaluate("el => el.value")' in line:
            ts_code += f"    const value = await textarea.inputValue();\n"
            continue
            
        # 转换 json.loads() -> JSON.parse()
        if 'json.loads(' in line:
            ts_code += f"    const data = JSON.parse({line.split('json.loads(')[1].split(')')[0]});\n"
            continue
            
        # 转换 assert -> expect().toBe()
        if 'assert ' in line and not line.strip().startswith('#'):
            # 简单转换：保留 assert，但转换为 expect 格式
            if 'assert len(' in line:
                ts_code += f"    // {line.strip()}\n"
            elif 'assert es_data' in line:
                ts_code += f"    // {line.strip()}\n"
            elif 'assert original_data[key] == current_data[key]' in line:
                ts_code += f"    // {line.strip()}\n"
            else:
                ts_code += f"    // {line.strip()}\n"
            continue
            
        # 转换 page.wait_for_timeout(1000) -> await page.waitForTimeout(1000)
        if 'page.wait_for_timeout(' in line:
            timeout_match = re.search(r'(\d+)', line)
            if timeout_match:
                ts_code += f"    await page.waitForTimeout({timeout_match.group(1)});\n"
            continue
            
        # 转换 page.fill() -> page.fill()
        if 'textarea.fill(' in line:
            value_match = re.search(r'textarea\.fill\("([^"]+)"\)', line)
            if value_match:
                ts_code += f"    await textarea.fill('{value_match.group(1)}');\n"
            continue
            
        # 转换 expect(...).to_have_title() -> expect(...).toHaveTitle()
        if 'expect(page).to_have_title(' in line:
            title_match = re.search(r'"([^"]+)"', line)
            if title_match:
                ts_code += f"    expect(page).toHaveTitle('{title_match.group(1)}');\n"
            continue
            
        # 转换普通文本（跳过注释）
        if line.strip().startswith('#'):
            ts_code += f"    // {line.strip()[1:].strip()}\n"
        elif line.strip():
            # 跳过空行和纯装饰器
            if 'pytest' in line or 'yield' in line:
                continue
            ts_code += f"    {line.strip()}\n"
    
    ts_code += "  })\n"
    
    return ts_code


def generate_spec_files(source_dir: str, output_dir: str):
    """生成所有 .spec.ts 文件"""
    
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 查找所有 Python 测试文件
    test_files = list(source_path.glob("test_*.py"))
    
    for py_file in test_files:
        with open(py_file, 'r', encoding='utf-8') as f:
            python_code = f.read()
        
        # 提取测试函数
        test_functions = re.findall(r'def (\w+)\(self, page\):.*?(?=\n    def |\Z)', python_code, re.DOTALL)
        
        # 生成 TypeScript 文件内容
        ts_content = f"""// Auto-generated from {py_file.name}
import {{ test, expect }} from '@playwright/test';

"""
        
        for func_match in re.finditer(r'def (\w+)\(self, page\):', python_code):
            func_name = func_match.group(1)
            
        # 生成单个.spec.ts 文件（以第一个测试函数为例）
        if test_functions:
            first_func = re.search(r'def (\w+)\(self, page\):', python_code)
            if first_func:
                test_name = f"{first_func.group(1)}"
                
            # 转换整个文件为 TypeScript
            ts_code = python_to_typescript(python_code, test_name)
            
            # 保存到 tests/ui 目录
            spec_file = output_path / f"{first_func.group(1)}.spec.ts"
            with open(spec_file, 'w', encoding='utf-8') as f:
                f.write(ts_code)
            
            print(f"✓ 已生成：{spec_file}")


if __name__ == "__main__":
    generate_spec_files(
        source_dir="/Users/linziwang/PycharmProjects/wordToWord/test",
        output_dir="/Users/linziwang/PycharmProjects/wordToWord/tests/ui"
    )
