# utils/kafka/converter.py
import uuid
from datetime import datetime, timedelta

# 配置项
UNIQUE_FIELDS = [
    "CFP0_CFP1_CFP2_CFP3",
    "ORIG_ALARM_FP",
    "ORIG_ALARM_CLEAR_FP",
    "FP0_FP1_FP2_FP3"
]

TIME_FIELDS = [
    "EVENT_TIME",
    "CREATION_EVENT_TIME",
    "EVENT_ARRIVAL_TIME"
]

def generate_unique_value() -> str:
    """
    生成基于当前时间的唯一值（匹配样例格式）
    :return: 唯一标识符字符串
    """
    time_part = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]  # 精确到毫秒
    uuid_part = str(uuid.uuid4())[:8]
    return f"FP_{time_part}_{uuid_part}"

def generate_time_str(time_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    生成当日减15分钟的时间字符串，支持自定义格式
    :param time_format: 时间格式，默认为 "%Y-%m-%d %H:%M:%S"
    :return: 格式化后的时间字符串
    """
    target_time = datetime.now() - timedelta(minutes=15)
    return target_time.strftime(time_format)

def es_to_kafka(es_source_data: dict, front_params: dict = None, time_format: str = "%Y-%m-%d %H:%M:%S") -> dict:
    """
    抽象的公用方法：将ES的_source数据转换为Kafka消息体
    :param es_source_data: ES中_source层的JSON数据（必传）
    :param front_params: 前端传入的覆盖参数（可选）
    :param time_format: 时间字段格式（匹配样例，默认"%Y-%m-%d %H:%M:%S"）
    :return: 符合规则的Kafka消息体（JSON格式）
    :raises ValueError: 当 es_source_data 为空时抛出异常
    """
    if not es_source_data:
        raise ValueError("ES的_source数据不能为空")

    # 初始化Kafka消息体：默认使用ES数据
    kafka_msg = es_source_data.copy()
    front_params = front_params or {}

    # 1. 前端参数覆盖（填写的字段替换默认值）
    for key, value in front_params.items():
        if isinstance(value, str) and value.strip():  # 非空字符串才覆盖
            kafka_msg[key] = value.strip()

    # 2. 生成唯一值字段（强制覆盖）
    for field in UNIQUE_FIELDS:
        kafka_msg[field] = generate_unique_value()

    # 3. 生成时间字段（强制覆盖）
    time_str = generate_time_str(time_format)
    for field in TIME_FIELDS:
        kafka_msg[field] = time_str

    return kafka_msg
