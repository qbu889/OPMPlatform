#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简易微信机器人 - itchat 版本
注意：微信网页版可能已受限，此版本仅供学习

安装：pip install itchat-uos
"""

import itchat
from itchat.content import TEXT
import logging
from datetime import datetime

# ==================== 配置区域 ====================

# 监控的群聊名称
MONITORED_GROUPS = [
    "测试群",
    # 添加你的群名
]

# 回复规则
REPLY_RULES = {
    "你好": "你好！欢迎！😊",
    "时间": lambda: f"当前时间：{datetime.now().strftime('%H:%M:%S')}",
    "日期": lambda: f"今天：{datetime.now().strftime('%Y年%m月%d日')}",
    "早上好": "早上好！☀️",
    "晚上好": "晚上好！🌙",
}

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_simple.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def check_reply(text):
    """检查并返回回复"""
    for keyword, reply in REPLY_RULES.items():
        if text.strip() == keyword:
            if callable(reply):
                return reply()
            return reply
        
        # 模糊匹配
        if keyword in text:
            if callable(reply):
                return reply()
            return reply
    
    return None


@itchat.msg_register(TEXT, isGroupChat=True)
def group_reply(msg):
    """处理群消息"""
    try:
        # 忽略自己
        if msg.fromUserName == itchat.originInstance.storageClass.userName:
            return
        
        text = msg.text
        room = itchat.search_chatrooms(name=msg.actualNickName)
        
        # 检查关键字
        reply = check_reply(text)
        
        if reply:
            logger.info(f"收到：{text} -> 回复：{reply}")
            itchat.send(reply, toUserName=msg.fromUserName)
        
    except Exception as e:
        logger.error(f"错误：{e}")


def main():
    """主程序"""
    print("=" * 50)
    print("简易微信机器人 - itchat 版本")
    print("=" * 50)
    print("\n提示:")
    print("- 首次运行需要扫码登录")
    print("- 如果无法登录，说明微信网页版已受限")
    print("- 建议使用 WeChatFerry (Windows)")
    print("\n按 Ctrl+C 停止\n")
    
    try:
        # 扫码登录
        itchat.auto_login(hotReload=True, enableCmdQR=2)
        
        logger.info("机器人启动成功!")
        logger.info(f"监控群聊：{', '.join(MONITORED_GROUPS)}")
        
        # 运行
        itchat.run()
        
    except Exception as e:
        logger.error(f"启动失败：{e}")
        print("\n登录失败，可能原因:")
        print("1. 微信网页版已被限制")
        print("2. 需要使用 Windows + WeChatFerry")
        print("3. 网络问题")


if __name__ == "__main__":
    main()
