#!/bin/bash
# Kafka生成器测试运行脚本
# 支持多种测试模式和选项

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_DIR="$PROJECT_ROOT/test/kafka"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Kafka生成器测试套件${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -a, --all          运行所有测试（默认）"
    echo "  -c, --core         只运行核心功能测试"
    echo "  -p, --api          只运行API接口测试"
    echo "  -o, --old          运行原有测试脚本"
    echo "  -v, --verbose      显示详细输出"
    echo "  -q, --quiet        静默模式，只显示结果"
    echo "  --cov              生成覆盖率报告"
    echo "  --html             生成HTML格式的覆盖率报告"
    echo "  -h, --help         显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                  # 运行所有测试"
    echo "  $0 -c -v           # 详细模式运行核心测试"
    echo "  $0 --cov --html    # 生成HTML覆盖率报告"
    echo ""
}

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}检查依赖...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}错误: 未找到python3${NC}"
        exit 1
    fi
    
    if ! python3 -m pytest --version &> /dev/null; then
        echo -e "${YELLOW}安装pytest...${NC}"
        pip install pytest pytest-cov pytest-flask
    fi
    
    echo -e "${GREEN}✓ 依赖检查完成${NC}"
    echo ""
}

# 运行核心功能测试
run_core_tests() {
    local verbose_flag=$1
    local cov_flag=$2
    
    echo -e "${BLUE}========== 运行核心功能测试 ==========${NC}"
    
    local cmd="pytest $TEST_DIR/test_kafka_complete.py"
    
    if [ "$verbose_flag" = "true" ]; then
        cmd="$cmd -v --tb=long"
    else
        cmd="$cmd -v --tb=short"
    fi
    
    if [ "$cov_flag" = "true" ]; then
        cmd="$cmd --cov=routes.kafka.kafka_generator_routes --cov-report=term-missing"
    fi
    
    cmd="$cmd --disable-warnings"
    
    echo -e "${YELLOW}执行命令: $cmd${NC}"
    eval $cmd
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ 核心功能测试通过${NC}"
    else
        echo -e "${RED}✗ 核心功能测试失败${NC}"
        return $exit_code
    fi
    echo ""
}

# 运行API接口测试
run_api_tests() {
    local verbose_flag=$1
    local cov_flag=$2
    
    echo -e "${BLUE}========== 运行API接口测试 ==========${NC}"
    
    local cmd="pytest $TEST_DIR/test_kafka_api.py"
    
    if [ "$verbose_flag" = "true" ]; then
        cmd="$cmd -v --tb=long"
    else
        cmd="$cmd -v --tb=short"
    fi
    
    if [ "$cov_flag" = "true" ]; then
        cmd="$cmd --cov=routes.kafka.kafka_generator_routes --cov-report=term-missing"
    fi
    
    cmd="$cmd --disable-warnings"
    
    echo -e "${YELLOW}执行命令: $cmd${NC}"
    eval $cmd
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ API接口测试通过${NC}"
    else
        echo -e "${RED}✗ API接口测试失败${NC}"
        return $exit_code
    fi
    echo ""
}

# 运行原有测试脚本
run_old_tests() {
    echo -e "${BLUE}========== 运行原有测试脚本 ==========${NC}"
    
    cd "$PROJECT_ROOT"
    python3 test/kafka/test_kafka_generator.py
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ 原有测试通过${NC}"
    else
        echo -e "${RED}✗ 原有测试失败${NC}"
        return $exit_code
    fi
    echo ""
}

# 生成覆盖率报告
generate_coverage_report() {
    local html_flag=$1
    
    echo -e "${BLUE}========== 生成覆盖率报告 ==========${NC}"
    
    local cmd="pytest $TEST_DIR/ --cov=routes.kafka.kafka_generator_routes"
    
    if [ "$html_flag" = "true" ]; then
        cmd="$cmd --cov-report=html:htmlcov_kafka"
        echo -e "${YELLOW}生成HTML报告到 htmlcov_kafka/ 目录${NC}"
    else
        cmd="$cmd --cov-report=term-missing"
    fi
    
    cmd="$cmd --disable-warnings"
    
    eval $cmd
    
    echo -e "${GREEN}✓ 覆盖率报告生成完成${NC}"
    echo ""
}

# 主函数
main() {
    local run_all=true
    local run_core=false
    local run_api=false
    local run_old=false
    local verbose=false
    local quiet=false
    local coverage=false
    local html=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -a|--all)
                run_all=true
                shift
                ;;
            -c|--core)
                run_all=false
                run_core=true
                shift
                ;;
            -p|--api)
                run_all=false
                run_api=true
                shift
                ;;
            -o|--old)
                run_all=false
                run_old=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -q|--quiet)
                quiet=true
                shift
                ;;
            --cov)
                coverage=true
                shift
                ;;
            --html)
                html=true
                coverage=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}未知选项: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 检查依赖
    check_dependencies
    
    # 切换到项目根目录
    cd "$PROJECT_ROOT"
    
    local start_time=$(date +%s)
    local failed=0
    
    # 运行测试
    if [ "$run_all" = "true" ]; then
        run_core_tests "$verbose" "$coverage" || ((failed++))
        run_api_tests "$verbose" "$coverage" || ((failed++))
        
        if [ "$coverage" = "true" ]; then
            generate_coverage_report "$html"
        fi
    else
        if [ "$run_core" = "true" ]; then
            run_core_tests "$verbose" "$coverage" || ((failed++))
        fi
        
        if [ "$run_api" = "true" ]; then
            run_api_tests "$verbose" "$coverage" || ((failed++))
        fi
        
        if [ "$run_old" = "true" ]; then
            run_old_tests || ((failed++))
        fi
        
        if [ "$coverage" = "true" ] && ([ "$run_core" = "true" ] || [ "$run_api" = "true" ]); then
            generate_coverage_report "$html"
        fi
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # 显示总结
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  测试总结${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo -e "耗时: ${duration}秒"
    
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}✓ 所有测试通过！${NC}"
        exit 0
    else
        echo -e "${RED}✗ $failed 个测试套件失败${NC}"
        exit 1
    fi
}

# 执行主函数
main "$@"
