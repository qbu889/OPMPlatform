#!/usr/bin/env python3
"""
彩色抽奖转盘系统 - 后端路由模块
==========================================
提供转盘配置管理、随机抽奖接口。数据持久化于本地 JSON 文件。

路由列表:
  GET    /api/wheel-lottery/config          - 获取转盘配置
  POST   /api/wheel-lottery/config          - 保存/更新转盘配置
  POST   /api/wheel-lottery/draw            - 执行抽奖
  POST   /api/wheel-lottery/reset           - 重置配置

作者: Claude Code
日期: 2026-06-11
"""

import json
import logging
import os
import random

from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

wheel_lottery_bp = Blueprint("wheel_lottery", __name__, url_prefix="/api/wheel-lottery")

# 配置文件路径
CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "uploads", "wheel_lottery"
)
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# 默认分区配置
DEFAULT_ITEMS = [
    {"id": 1, "name": "一等奖", "color": "#FF4444", "weight": 1},
    {"id": 2, "name": "二等奖", "color": "#44BB44", "weight": 1},
    {"id": 3, "name": "三等奖", "color": "#4488FF", "weight": 1},
    {"id": 4, "name": "谢谢参与", "color": "#AAAAAA", "weight": 2},
]


def _ensure_config_dir():
    """确保配置文件目录存在"""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def _load_config():
    """
    从 JSON 文件加载转盘配置

    Returns:
        dict: 包含 items 列表的配置字典，若文件不存在则返回默认配置
    """
    _ensure_config_dir()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "items" in data and isinstance(data["items"], list):
                    return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"配置文件读取失败，使用默认配置: {e}")
    # 返回默认配置（确保 items 按 id 排序）
    config = {"items": sorted(DEFAULT_ITEMS, key=lambda x: x["id"])}
    _save_config(config)
    return config


def _save_config(config):
    """
    保存转盘配置到 JSON 文件

    Args:
        config (dict): 包含 items 列表的配置字典
    """
    _ensure_config_dir()
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except IOError as e:
        logger.error(f"配置文件保存失败: {e}")
        raise


def _get_next_id(items):
    """获取下一个可用的分区 ID"""
    if not items:
        return 1
    return max(item["id"] for item in items) + 1


def _weighted_random_choice(items):
    """
    加权随机选择算法

    根据分区的 weight 权重分配概率，权重越大被抽中的概率越高。

    Args:
        items (list): 分区列表，每个元素包含 weight 字段

    Returns:
        dict: 被选中的分区对象
    """
    total_weight = sum(item.get("weight", 1) for item in items)
    if total_weight <= 0:
        total_weight = len(items) or 1

    rand_value = random.uniform(0, total_weight)
    cumulative = 0
    for item in items:
        cumulative += item.get("weight", 1)
        if rand_value <= cumulative:
            return item
    # fallback：等概率随机
    return random.choice(items)


# ============================================================================
# API 路由
# ============================================================================


@wheel_lottery_bp.route("/config", methods=["GET"])
def get_wheel_config():
    """
    获取转盘配置

    Returns:
        jsonify: 包含 items 列表的配置字典，code=200 表示成功
    """
    try:
        config = _load_config()
        return jsonify(
            {
                "code": 200,
                "msg": "success",
                "data": config,
            }
        )
    except Exception as e:
        logger.error(f"获取转盘配置失败: {e}")
        return (
            jsonify(
                {
                    "code": 500,
                    "msg": f"服务器错误: {str(e)}",
                }
            ),
            500,
        )


@wheel_lottery_bp.route("/config", methods=["POST"])
def save_wheel_config():
    """
    保存/更新转盘配置

    JSON Body:
        dict: 包含 items 列表的配置字典

    Returns:
        jsonify: 操作结果，code=200 表示成功
    """
    try:
        data = request.get_json()
        if not data or "items" not in data:
            return (
                jsonify(
                    {
                        "code": 400,
                        "msg": "缺少 items 字段",
                    }
                ),
                400,
            )

        items = data["items"]
        if not isinstance(items, list):
            return (
                jsonify(
                    {
                        "code": 400,
                        "msg": "items 必须是数组",
                    }
                ),
                400,
            )

        # 验证每个分区的必要字段
        for i, item in enumerate(items):
            if not isinstance(item, dict):
                return (
                    jsonify(
                        {
                            "code": 400,
                            "msg": f"分区 {i + 1} 格式错误",
                        }
                    ),
                    400,
                )
            if "name" not in item or "color" not in item:
                return (
                    jsonify(
                        {
                            "code": 400,
                            "msg": f"分区 {i + 1} 缺少 name 或 color 字段",
                        }
                    ),
                    400,
                )

        config = {"items": items}
        _save_config(config)

        logger.info(f"转盘配置已保存，共 {len(items)} 个分区")
        return jsonify(
            {
                "code": 200,
                "msg": "配置保存成功",
            }
        )
    except Exception as e:
        logger.error(f"保存转盘配置失败: {e}")
        return (
            jsonify(
                {
                    "code": 500,
                    "msg": f"服务器错误: {str(e)}",
                }
            ),
            500,
        )


@wheel_lottery_bp.route("/draw", methods=["POST"])
def draw_wheel():
    """
    执行抽奖

    读取当前配置，根据权重随机算法返回中奖分区。

    Returns:
        jsonify: 包含中奖分区信息的响应，code=200 表示成功
    """
    try:
        config = _load_config()
        items = config.get("items", [])

        if not items:
            return (
                jsonify(
                    {
                        "code": 400,
                        "msg": "转盘分区为空，请先配置分区",
                    }
                ),
                400,
            )

        if len(items) < 2:
            return (
                jsonify(
                    {
                        "code": 400,
                        "msg": "至少需要 2 个分区才能抽奖",
                    }
                ),
                400,
            )

        # 执行加权随机抽奖
        winner = _weighted_random_choice(items)

        logger.info(f"抽奖结果: {winner['name']}")
        return jsonify(
            {
                "code": 200,
                "msg": "抽奖成功",
                "data": winner,
            }
        )
    except Exception as e:
        logger.error(f"抽奖失败: {e}")
        return (
            jsonify(
                {
                    "code": 500,
                    "msg": f"服务器错误: {str(e)}",
                }
            ),
            500,
        )


@wheel_lottery_bp.route("/reset", methods=["POST"])
def reset_wheel_config():
    """
    重置配置为默认分区

    Returns:
        jsonify: 操作结果，code=200 表示成功
    """
    try:
        config = {"items": sorted(DEFAULT_ITEMS, key=lambda x: x["id"])}
        _save_config(config)

        logger.info("转盘配置已重置为默认值")
        return jsonify(
            {
                "code": 200,
                "msg": "配置已重置",
                "data": config,
            }
        )
    except Exception as e:
        logger.error(f"重置配置失败: {e}")
        return (
            jsonify(
                {
                    "code": 500,
                    "msg": f"服务器错误: {str(e)}",
                }
            ),
            500,
        )


def init_wheel_config(app):
    """
    初始化转盘配置（首次使用时创建默认配置文件）

    Args:
        app (Flask): Flask 应用实例
    """
    with app.app_context():
        try:
            _ensure_config_dir()
            if not os.path.exists(CONFIG_FILE):
                default_config = {"items": sorted(DEFAULT_ITEMS, key=lambda x: x["id"])}
                _save_config(default_config)
            logger.info("✅ 转盘抽奖模块初始化完成")
        except Exception as e:
            logger.error(f"⚠️ 转盘抽奖模块初始化失败: {e}")
