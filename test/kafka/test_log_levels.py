#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试日志等级配置功能
====================

用于验证不同日志级别配置的效果

使用方法：
    python test_log_levels.py
"""

import os
import logging
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

def test_logging_with_level(log_level):
    """测试指定日志级别的输出效果"""
    print(f"\n{'='*60}")
    print(f"测试日志级别：{log_level}")
    print('='*60)
    
    # 设置环境变量
    os.environ['LOG_LEVEL'] = log_level
    os.environ['LOG_TO_CONSOLE'] = 'True'
    os.environ['LOG_TO_FILE'] = 'False'  # 测试时不写入文件
    
    # 重新配置日志
    logger = logging.getLogger()
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    
    # 导入并调用 setup_logging 函数
    from app import setup_logging
    app_logger = setup_logging()
    
    # 测试各种级别的日志
    logger.debug("这是一条 DEBUG 日志（调试信息）")
    logger.info("这是一条 INFO 日志（普通信息）")
    logger.warning("这是一条 WARNING 日志（警告信息）")
    logger.error("这是一条 ERROR 日志（错误信息）")
    
    print(f"\n预期输出：")
    if log_level == 'DEBUG':
        print("  ✓ 输出 DEBUG, INFO, WARNING, ERROR")
    elif log_level == 'INFO':
        print("  ✓ 输出 INFO, WARNING, ERROR（不输出 DEBUG）")
    elif log_level == 'WARNING':
        print("  ✓ 输出 WARNING, ERROR（不输出 DEBUG, INFO）")
    elif log_level == 'ERROR':
        print("  ✓ 只输出 ERROR（不输出 DEBUG, INFO, WARNING）")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("日志等级配置功能测试")
    print("="*60)
    print("\n本项目支持通过 LOG_LEVEL 环境变量控制日志输出级别")
    print("可在 .env 文件中配置，或在启动前设置系统环境变量")
    print("\n支持的日志级别：")
    print("  - ERROR:   只输出错误日志")
    print("  - WARNING: 输出错误和警告日志")
    print("  - INFO:    输出错误、警告和信息日志（默认）")
    print("  - DEBUG:   输出所有级别日志")
    
    # 测试各个级别
    test_levels = ['ERROR', 'WARNING', 'INFO', 'DEBUG']
    
    for level in test_levels:
        test_logging_with_level(level)
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)
    print("\n使用说明：")
    print("1. 修改 .env 文件中的 LOG_LEVEL 配置")
    print("2. 重启应用即可生效")
    print("3. 示例：LOG_LEVEL=ERROR （只输出错误日志）")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
