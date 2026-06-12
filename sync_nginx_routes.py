#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_nginx_routes.py - 自动检测 Flask 路由并同步到 Nginx 配置
用法:
  python sync_nginx_routes.py              # 检测并提示确认
  python sync_nginx_routes.py --auto       # 自动应用（不确认）
  python sync_nginx_routes.py --check      # 仅检查，不同步
"""

import os
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

# 配置
PROJECT_ROOT = Path(__file__).parent
ROUTES_DIR = PROJECT_ROOT / "routes"
NGINX_CONF_FILE = PROJECT_ROOT / "nginx_5173_complete.conf"
DEPLOY_PY_FILE = PROJECT_ROOT / "deploy.py"

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def extract_routes_from_file(file_path):
    """从 Python 文件中提取 Flask 路由"""
    routes = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配 @blueprint.route('/path', methods=[...]) 模式
        pattern = r"@(\w+_bp)\.route\(['\"]([^'\"]+)['\"](?:,\s*methods=\[([^\]]+)\])?\)"
        matches = re.finditer(pattern, content)
        
        for match in matches:
            blueprint_name = match.group(1)
            path = match.group(2)
            methods = match.group(3)
            
            # 解析 HTTP 方法
            method_list = ['GET']  # 默认 GET
            if methods:
                method_list = [m.strip().strip("'\"") for m in methods.split(',')]
            
            # 清理路径（移除尾部的 /）
            clean_path = path.rstrip('/')
            if not clean_path:
                clean_path = '/'
            
            routes.append({
                'blueprint': blueprint_name,
                'path': clean_path,
                'methods': method_list,
                'file': str(file_path.relative_to(PROJECT_ROOT))
            })
    
    except Exception as e:
        print_error(f"读取文件失败 {file_path}: {e}")
    
    return routes

def scan_all_routes():
    """扫描所有路由文件"""
    print_header("步骤 1: 扫描 Flask 路由")
    
    all_routes = []
    
    # 遍历 routes 目录
    for py_file in ROUTES_DIR.rglob("*.py"):
        if py_file.name.startswith('_'):
            continue
        
        routes = extract_routes_from_file(py_file)
        all_routes.extend(routes)
    
    print_success(f"共检测到 {len(all_routes)} 个路由")
    
    # 按蓝图分组
    routes_by_bp = defaultdict(list)
    for route in all_routes:
        bp_name = route['blueprint'].replace('_bp', '').replace('_', '-')
        routes_by_bp[bp_name].append(route)
    
    return routes_by_bp

def extract_nginx_locations(nginx_conf_path):
    """从 Nginx 配置中提取现有的 location 规则"""
    locations = []
    
    try:
        with open(nginx_conf_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配 location 规则
        # 支持两种格式：
        # 1. location = /path { proxy_pass ... }
        # 2. location /path/ { proxy_pass ... }
        pattern = r"location\s+(=)?\s+(/[^\s{]+)\s*\{"
        matches = re.finditer(pattern, content)
        
        for match in matches:
            is_exact = bool(match.group(1))  # 是否有 = 精确匹配
            path = match.group(2)
            locations.append({
                'path': path,
                'exact': is_exact
            })
    
    except Exception as e:
        print_error(f"读取 Nginx 配置失败: {e}")
    
    return locations

def detect_missing_routes(routes_by_bp, nginx_locations):
    """检测缺失的路由"""
    print_header("步骤 2: 对比现有 Nginx 配置")
    
    # 提取 Nginx 已有的路径
    nginx_paths = set(loc['path'] for loc in nginx_locations)
    
    missing_routes = []
    
    for bp_name, routes in routes_by_bp.items():
        for route in routes:
            path = route['path']
            
            # 跳过静态资源、根路径等
            if path in ['/', '/login', '/register', '/forgot-password']:
                continue
            
            # 检查是否已存在于 Nginx 配置中
            # 需要同时检查精确匹配和前缀匹配
            has_exact = path in nginx_paths
            has_prefix = any(path.startswith(np) or np.startswith(path) 
                           for np in nginx_paths if np != '/')
            
            if not has_exact and not has_prefix:
                missing_routes.append(route)
    
    return missing_routes

def generate_nginx_location(route):
    """生成 Nginx location 配置"""
    path = route['path']
    methods = route['methods']
    
    # 判断是否需要精确匹配
    # 如果路径不包含参数占位符且不是前缀路径，使用精确匹配
    needs_exact = '<' not in path and not path.endswith('/')
    
    if needs_exact:
        return f"    location = {path} {{ proxy_pass http://127.0.0.1:5004; }}"
    else:
        return f"    location {path} {{ proxy_pass http://127.0.0.1:5004; }}"

def generate_deploy_check_code(route):
    """生成 deploy.py 中的测试代码片段"""
    path = route['path']
    methods = route['methods']
    
    # 根据 HTTP 方法生成不同的测试代码
    if 'POST' in methods:
        return f"""    # TODO: 添加 {path} 的 POST 测试
    # test_data = {{"key": "value"}}
    # response = requests.post(f"http://{{REMOTE_HOST}}:{{NGINX_PORT}}{path}", json=test_data)"""
    elif 'PUT' in methods:
        return f"""    # TODO: 添加 {path} 的 PUT 测试
    # response = requests.put(f"http://{{REMOTE_HOST}}:{{NGINX_PORT}}{path}", json={{"id": 1}})"""
    elif 'DELETE' in methods:
        return f"""    # TODO: 添加 {path} 的 DELETE 测试
    # response = requests.delete(f"http://{{REMOTE_HOST}}:{{NGINX_PORT}}{path}")"""
    else:
        return f"""    # TODO: 添加 {path} 的 GET 测试
    # response = requests.get(f"http://{{REMOTE_HOST}}:{{NGINX_PORT}}{path}")"""

def display_missing_routes(missing_routes):
    """显示缺失的路由"""
    if not missing_routes:
        print_success("✅ 所有路由都已在 Nginx 配置中！")
        return
    
    print_warning(f"发现 {len(missing_routes)} 个缺失的路由:\n")
    
    # 按蓝图分组显示
    by_bp = defaultdict(list)
    for route in missing_routes:
        bp_name = route['blueprint'].replace('_bp', '')
        by_bp[bp_name].append(route)
    
    for bp_name, routes in sorted(by_bp.items()):
        print(f"{Colors.CYAN}📦 {bp_name}:{Colors.END}")
        for route in routes:
            methods_str = ', '.join(route['methods'])
            print(f"   {Colors.YELLOW}[{methods_str}]{Colors.END} {route['path']}")
            print(f"      文件: {route['file']}")
        print()

def confirm_and_apply(missing_routes, auto=False):
    """确认并应用更改"""
    if not missing_routes:
        return True
    
    print_header("步骤 3: 生成配置更新")
    
    # 生成 Nginx 配置片段
    print_info("需要添加到 nginx_5173_complete.conf 的配置:")
    print(f"{Colors.YELLOW}{'─' * 60}{Colors.END}")
    
    nginx_additions = []
    for route in missing_routes:
        location_line = generate_nginx_location(route)
        print(location_line)
        nginx_additions.append((route, location_line))
    
    print(f"{Colors.YELLOW}{'─' * 60}{Colors.END}\n")
    
    # 生成 deploy.py 测试代码
    print_info("建议在 deploy.py 的 test_api() 函数中添加的测试代码:")
    print(f"{Colors.YELLOW}{'─' * 60}{Colors.END}")
    
    deploy_additions = []
    for route in missing_routes[:5]:  # 只显示前5个
        test_code = generate_deploy_check_code(route)
        print(test_code)
        deploy_additions.append((route, test_code))
    
    print(f"{Colors.YELLOW}{'─' * 60}{Colors.END}\n")
    
    if auto:
        print_info("自动模式：直接应用更改...")
        apply_changes(nginx_additions, deploy_additions)
        return True
    
    # 询问用户
    print(f"{Colors.BOLD}是否应用这些更改？(y/n): {Colors.END}", end="", flush=True)
    try:
        choice = input().strip().lower()
        if choice == 'y':
            apply_changes(nginx_additions, deploy_additions)
            return True
        else:
            print_info("已取消")
            return False
    except:
        print_info("\n已取消")
        return False

def apply_changes(nginx_additions, deploy_additions):
    """应用更改到配置文件"""
    print_header("步骤 4: 应用更改")
    
    # 1. 更新 Nginx 配置
    if nginx_additions:
        print_info("更新 nginx_5173_complete.conf...")
        
        with open(NGINX_CONF_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 找到最后一个 location 块的位置（在 SPA 路由之前）
        insert_index = -1
        for i, line in enumerate(lines):
            if '# SPA 路由' in line:
                insert_index = i
                break
        
        if insert_index == -1:
            # 如果没找到注释，找 location / {
            for i, line in enumerate(lines):
                if 'location / {' in line or 'location /' in line:
                    insert_index = i
                    break
        
        if insert_index > 0:
            # 插入新的 location 规则
            new_lines = []
            for route, location_line in nginx_additions:
                new_lines.append(f"\n    # {route['blueprint'].replace('_bp', '')} API\n")
                new_lines.append(f"    {location_line}\n")
            
            # 在插入位置前添加空行
            lines.insert(insert_index, '\n')
            for i, new_line in enumerate(new_lines):
                lines.insert(insert_index + 1 + i, new_line)
            
            # 写回文件
            with open(NGINX_CONF_FILE, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print_success(f"已添加 {len(nginx_additions)} 个 location 规则")
        else:
            print_error("无法找到插入位置，请手动添加")
    
    # 2. 更新 deploy.py（可选）
    if deploy_additions:
        print_warning("deploy.py 的测试代码需要手动添加（避免破坏现有逻辑）")
        print_info("建议位置: test_api() 函数末尾")
    
    print_success("配置更新完成！")
    print_info("下一步:")
    print("   1. 运行 python deploy.py 重新部署")
    print("   2. 或在服务器上执行: nginx -t && nginx -s reload")

def print_header(title):
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}  {title}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")

def main():
    parser = argparse.ArgumentParser(description='自动同步 Flask 路由到 Nginx 配置')
    parser.add_argument('--auto', action='store_true', help='自动应用，无需确认')
    parser.add_argument('--check', action='store_true', help='仅检查，不修改文件')
    args = parser.parse_args()
    
    print_header("🔍 Flask 路由自动检测与 Nginx 配置同步工具")
    
    try:
        # 1. 扫描所有路由
        routes_by_bp = scan_all_routes()
        
        # 2. 提取现有 Nginx 配置
        nginx_locations = extract_nginx_locations(NGINX_CONF_FILE)
        print_info(f"Nginx 配置中已有 {len(nginx_locations)} 个 location 规则")
        
        # 3. 检测缺失的路由
        missing_routes = detect_missing_routes(routes_by_bp, nginx_locations)
        
        # 4. 显示结果
        display_missing_routes(missing_routes)
        
        # 5. 应用更改
        if not args.check:
            confirm_and_apply(missing_routes, auto=args.auto)
        else:
            print_info("检查模式：未应用任何更改")
    
    except KeyboardInterrupt:
        print_warning("\n用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
