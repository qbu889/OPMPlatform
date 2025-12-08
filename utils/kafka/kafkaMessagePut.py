import json
import time
import uuid
import random
from confluent_kafka import Producer, KafkaError

# -------------------------- 核心配置 --------------------------
# Kafka 集群地址（替换为你的实际地址）
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
# 要发送的 Kafka 主题
KAFKA_TOPIC = "test-reinstall"
# 批量发送的消息总数（可改为 1000/10000）
TOTAL_MSG_COUNT = 10000
# 基础 JSON 模板（基于你提供的结构，动态字段后续替换）
BASE_ALARM_JSON = {
    "ID": "",  # 动态生成 UUID
    "NETWORK_TYPE_TOP": "4",
    "ORG_SEVERITY": "3",
    "REGION_NAME": "三明市",
    "ACTIVE_STATUS": "1",
    "CITY_NAME": "大田县",
    "EQP_LABEL": "188-10527-三明大田湖美",
    "EQP_OBJECT_CLASS": "2009",
    "VENDOR_NAME": "烽火",
    "VENDOR_ID": "202",
    "ALARM_RESOURCE_STATUS": "1500",
    "LOCATE_INFO": "XSJ2[07]\\:XGE_1/VP-65",
    "NE_LABEL": "188-10527-三明大田湖美",
    "OBJECT_LEVEL": "305",
    "PROFESSIONAL_TYPE": "3",
    "NETWORK_TYPE": "404",
    "ORG_TYPE": "1",
    "VENDOR_TYPE": "1",
    "SEND_JT_FLAG": "0",
    "TITLE_TEXT": "VP_SSF",
    "STANDARD_ALARM_NAME": "MPLS-TP通路服务层信号失效",
    "STANDARD_ALARM_ID": "0404-024-034-10-006814",
    "STANDARD_FLAG": "2",
    "VENDOR_SEVERITY": "紧急告警",
    "PROBABLE_CAUSE": "2155",
    "NMS_ALARM_ID": "",  # 动态生成随机数
    "PROBABLE_CAUSE_TXT": "affectedSNCName:3500FHCS3TNL0000000PE28YI000",
    "PREPROCESS_MANNER": "",
    "EVENT_TIME": "22025-12-04 14:21:37",
    "TIME_STAMP": "",  # 动态生成时间戳
    "FP0_FP1_FP2_FP3": "",  # 需要唯一值
    "CFP0_CFP1_CFP2_CFP3": "",  # 需要唯一值
    "MACHINE_ROOM_INFO": "三明大田湖美（全业务）三楼303机房",
    "INT_ID": "8626017741975829480",
    "REDEFINE_SEVERITY": "4",
    "TYPE_KEYCODE": "",
    "NE_LOCATION": "188-10527-三明大田湖美",
    "ALARM_EXPLANATION": "一、告警解释：MPLS-TP通路服务层信号失效；二、告警原因：(1)该LSP所在线路存在LINK_LOS或收无光告警。\n(2)该LSP所在TUNNEL转发表配置错误。",
    "ALARM_EXPLANATION_ADDITION": "",
    "MAINTAIN_GROUP": "三明大田县城网格综合基站维护组1",
    "SITE_TYPE": "105",
    "SUB_ALARM_TYPE": "",
    "EVENT_CAT": "",
    "NMS_NAME": "直真传输综合网管",
    "CITY_ID": "-210966378",
    "REMOTE_EQP_LABEL": "",
    "REMOTE_RESOURCE_STATUS": "",
    "REMOTE_PROJ_SUB_STATUS": "",
    "REMOTE_INT_ID": "8626017741975829480",
    "PROJ_NAME": "【传输网】【福州】C类割接：福州核心层PTN7900、 7900E版本升级FJ-0001-20250714-076200",
    "PROJ_OA_FILE_CONTENT": "",
    "BUSINESS_REGION_IDS": "",
    "BUSINESS_REGIONS": "",
    "REMOTE_OBJECT_CLASS": "",
    "ALARM_REASON": "",
    "GCSS_CLIENT": "",
    "GCSS_CLIENT_NAME": "",
    "GCSS_CLIENT_NUM": "",
    "GCSS_CLIENT_LEVEL": "",
    "GCSS_SERVICE": "",
    "GCSS_SERVICE_NUM": "",
    "GCSS_SERVICE_LEVEL": "",
    "GCSS_SERVICE_TYPE": "",
    "BUSINESS_SYSTEM": "3500FHCS3",
    "NE_IP": "172.28.58.9",
    "LAYER_RATE": "22",
    "CIRCUIT_ID": "",
    "ALARM_ABNORMAL_TYPE": "40",
    "PROJ_OA_FILE_ID": "FJ-0001-20250714-076200",
    "GCSS_CLIENT_GRADE": "",
    "EFFECT_CIRCUIT_NUM": "",
    "PREHANDLE": "0",
    "OBJECT_CLASS_TEXT": "PTN",
    "BOARD_TYPE": "330",
    "OBJECT_CLASS": "2009",
    "LOGIC_ALARM_TYPE": "35",
    "LOGIC_SUB_ALARM_TYPE": "140195",
    "EFFECT_NE": "6",
    "EFFECT_SERVICE": "4",
    "SPECIAL_FIELD14": "DEVICEROOM-0598-00127",
    "SPECIAL_FIELD7": "5fb80080-6dfb-11e3-a2e9-0018fe2fb227",
    "SPECIAL_FIELD21": "",
    "ALARM_SOURCE": "3500FHCS3",
    "BUSINESS_LAYER": "1004",
    "ALARM_TEXT": "<ALARM-START>\nIntVersion:V1.2.0\nAlarmUniqueId:1991391827844644864\nNeId:UUID:5fb80080-6dfb-11e3-a2e9-0018fe2fb227\nNeName:188-10527-三明大田湖美\nTo_Mename:\nSystemName:直真传输综合网管\nEquipmentClass:PTN\nDevicemodel:Citrans 660\nVendor:烽火\nEmsID:3500FHCS3\nLocateNeName:188-10527-三明大田湖美\nLocateNeType:伪线\nLocateNeStatus:普通告警\nLocateInfo:XSJ2[07]\\:XGE_1/VP-65\nEventTime:22025-12-04 14:21:37\nCancelTime:\nDalTime:22025-12-04 14:23:04\nVendorAlarmType:qualityofServiceAlarm\nVendorSeverity:4\nALARMSEVERITY:4\nVendorAlarmId:2155\nNMSALARMID:224-120-00-901367\nAlarmStatus:1\nAckFlag:未确认\nAckTime:\nAckUser:设备厂家\nClrUser:设备厂家\nAlarmTitle:VP_SSF\nStandardAlarmName:VP_SSF\nProbableCauseTxt:affectedSNCName:3500FHCS3TNL0000000PE28YI000\nALARMTEXT:MPLS-TP通路服务层信号失效\nCircuit_no:\nSpecialty:传送网\nAlarmLogicClass:设备\nAlarmLogicSubClass:业务\nEffectOnEquipment:无影响\nEffectOnBusiness:可能业务受影响\nNmsAlarmType:设备告警\nSendGroupFlag:0\nRelatedFlag:4\nAlarmProvince:福建省\nAlarmRegion:三明\nAlarmCounty:大田县\nSite:\nAlarmActCount:1\nBusinessSystem:\nGroupCustomer:\nSheetSendStatus:0\nSheetStatus:未派单\nSheetNo:\nAlarmMemo:\nLayerSpeed:速率无关\nSignalSpeed:\nEmsAlarmTime:22025-12-04 14:21:37\nEmsAlarmClearTime:\nTaskID:\nNetworkType:本地汇聚\nImportance:\nMaintenanceunit:自维\nResponsibleperson:苏世征\nMaintOrga:三明大田县城网格综合基站维护组1\nMaintenancemode:自维\nTASKDETAIL:\nRoomCuid:DEVICEROOM-NMS-0598-00127\nToRoomCuid:\nCard_model:无\nCard_id:\nPtp_id:\nPtp_name:\nIPAddress:172.28.58.9\nNodeName:\nBMCUID:\nCI:\ncircuit_level:\nHomeClientNum:\nLinkOnuNum:\nCircuit_num:\nReService:\nOltlinkport_loadmade:\nOpticalcableName:\nImportantMe:0\nSoftwareVersion:VR2.0SP6\nVendorSeverityCH:紧急告警\nNSSIID:\nCard_name:\nOnu_sn:\nRingNet:\nAlarmId:1142377998\nMeRmuid:3500FHCS3NEL07UE100000000000\nMeName:188-10527-三明大田湖美\nObjectRmuid:\nObjectName:\nOppoMeRmuid:\nOppoMeName:\nOppoObjectRmuid:\nOppoObjectName:\nPosLosTopoInfo:\nPosLogicBreak:\nPosRealBreak:\nPosRealLongitude:\nPosRealLatitude:\nLosAlarm:\nBreakLength:\nPORTTYPE:\n<ALARM-END>",
    "CIRCUIT_NO": "",
    "PRODUCT_TYPE": "AlarmId:1142377998",
    "CIRCUIT_LEVEL": "-1",
    "BUSINESS_TYPE": "",
    "IRMS_GRID_NAME": "",
    "ADMIN_GRID_ID": "",
    "HOME_CLIENT_NUM": "",
    "SRC_ID": "GZEVENT0000000766100722",
    "SRC_IS_TEST": 0,
    "SRC_APP_ID": "1001",
    "SRC_ORG_ID": "2601772413_3879104831_1675769779_2776627502_2",
    "ORG_TEXT": "4_;3_;三明市_;1_;大田县_;188-10527-三明大田湖美_;2009_;烽火_;202_;1_;XSJ2[07]\\:XGE_1/VP-65_;188-10527-三明大田湖美_;305_;3_;404_;1_;1_;0_;VP_SSF_;MPLS-TP通路服务层信号失效_;0404-024-034-10-006814_;2_;紧急告警_;2155_;1142377998_;affectedSNCName:3500FHCS3TNL0000000PE28YI000_;_;22025-12-04 14:21:37_;1763619788_;_;2601772413_3879104831_1675769779_2776627502_;2691975489_3463756259_655419436_1383102850_;三明大田湖美（全业务）三楼303机房_;8626017741975829480_;4_;_;188-10527-三明大田湖美_;一、告警解释：MPLS-TP通路服务层信号失效；二、告警原因：(1)该LSP所在线路存在LINK_LOS或收无光告警。\n(2)该LSP所在TUNNEL转发表配置错误。_;_;三明大田县城网格综合基站维护组1_;105_;_;_;直真传输综合网管_;-210966378_;_;_;_;8626017741975829480_;_;_;_;_;_;_;_;_;_;_;_;_;_;_;_;3500FHCS3_;172.28.58.9_;22_;_;40_;_;_;_;0_;PTN_;330_;_;_;2009_;35_;140195_;6_;4_;DEVICEROOM-0598-00127_;5fb80080-6dfb-11e3-a2e9-0018fe2fb227_;_;3500FHCS3_;1004_;0_;<ALARM-START>\nIntVersion:V1.2.0\nAlarmUniqueId:1991391827844644864\nNeId:UUID:5fb80080-6dfb-11e3-a2e9-0018fe2fb227\nNeName:188-10527-三明大田湖美\nTo_Mename:\nSystemName:直真传输综合网管\nEquipmentClass:PTN\nDevicemodel:Citrans 660\nVendor:烽火\nEmsID:3500FHCS3\nLocateNeName:188-10527-三明大田湖美\nLocateNeType:伪线\nLocateNeStatus:普通告警\nLocateInfo:XSJ2[07]\\:XGE_1/VP-65\nEventTime:22025-12-04 14:21:37\nCancelTime:\nDalTime:22025-12-04 14:23:04\nVendorAlarmType:qualityofServiceAlarm\nVendorSeverity:4\nALARMSEVERITY:4\nVendorAlarmId:2155\nNMSALARMID:224-120-00-901367\nAlarmStatus:1\nAckFlag:未确认\nAckTime:\nAckUser:设备厂家\nClrUser:设备厂家\nAlarmTitle:VP_SSF\nStandardAlarmName:VP_SSF\nProbableCauseTxt:affectedSNCName:3500FHCS3TNL0000000PE28YI000\nALARMTEXT:MPLS-TP通路服务层信号失效\nCircuit_no:\nSpecialty:传送网\nAlarmLogicClass:设备\nAlarmLogicSubClass:业务\nEffectOnEquipment:无影响\nEffectOnBusiness:可能业务受影响\nNmsAlarmType:设备告警\nSendGroupFlag:0\nRelatedFlag:4\nAlarmProvince:福建省\nAlarmRegion:三明\nAlarmCounty:大田县\nSite:\nAlarmActCount:1\nBusinessSystem:\nGroupCustomer:\nSheetSendStatus:0\nSheetStatus:未派单\nSheetNo:\nAlarmMemo:\nLayerSpeed:速率无关\nSignalSpeed:\nEmsAlarmTime:22025-12-04 14:21:37\nEmsAlarmClearTime:\nTaskID:\nNetworkType:本地汇聚\nImportance:\nMaintenanceunit:自维\nResponsibleperson:苏世征\nMaintOrga:三明大田县城网格综合基站维护组1\nMaintenancemode:自维\nTASKDETAIL:\nRoomCuid:DEVICEROOM-NMS-0598-00127\nToRoomCuid:\nCard_model:无\nCard_id:\nPtp_id:\nPtp_name:\nIPAddress:172.28.58.9\nNodeName:\nBMCUID:\nCI:\ncircuit_level:\nHomeClientNum:\nLinkOnuNum:\nCircuit_num:\nReService:\nOltlinkport_loadmade:\nOpticalcableName:\nImportantMe:0\nSoftwareVersion:VR2.0SP6\nVendorSeverityCH:紧急告警\nNSSIID:\nCard_name:\nOnu_sn:\nRingNet:\nAlarmId:1142377998\nMeRmuid:3500FHCS3NEL07UE100000000000\nMeName:188-10527-三明大田湖美\nObjectRmuid:\nObjectName:\nOppoMeRmuid:\nOppoMeName:\nOppoObjectRmuid:\nOppoObjectName:\nPosLosTopoInfo:\nPosLogicBreak:\nPosRealBreak:\nPosRealLongitude:\nPosRealLatitude:\nLosAlarm:\nBreakLength:\nPORTTYPE:\n<ALARM-END>_;NULL_;_;AlarmId:1142377998_;-1_;_;_;_;_;1004_;_;300204_;_;_;330_;1004_;_;_;0_;【是否干扰告警】：否。_;_;_;_;_;188-10527-三明大田湖美_;\n",
    "TOPIC_PREFIX": "EVENT-GZ",
    "TOPIC_PARTITION": 81,
    "SPECIAL_FIELD17": "NULL",
    "EXTRA_ID2": "1004",
    "EXTRA_STRING1": "",
    "PORT_NUM": "300204",
    "NE_ADMIN_STATUS": "",
    "SPECIAL_FIELD18": "",
    "SPECIAL_FIELD20": "330",
    "TMSC_CAT": "1004",
    "ALARM_NE_STATUS": "",
    "ALARM_EQP_STATUS": "",
    "INTERFERENCE_FLAG": "0",
    "SPECIAL_FIELD2": "【是否干扰告警】：否。",
    "custGroupFeature": "",
    "industryCustType": "",
    "strategicCustTypeFL": "",
    "strategicCustTypeSL": "",
    "FAULT_LOCATION": "188-10527-三明大田湖美",
    "EVENT_SOURCE": 2,
    "ORIG_ALARM_CLEAR_FP": "",  # 需要唯一值
    "ORIG_ALARM_FP": "",  # 需要唯一值
    "EVENT_ARRIVAL_TIME": "22025-12-04 11:23:11"
}


# -------------------------- 工具函数 --------------------------
def generate_unique_alarm():
    """生成唯一的告警JSON（替换动态字段）"""
    alarm = BASE_ALARM_JSON.copy()
    # 1. 生成唯一UUID（ID字段）
    alarm["ID"] = str(uuid.uuid4())
    # 2. 生成随机NMS_ALARM_ID（10位随机数）
    alarm["NMS_ALARM_ID"] = str(random.randint(1000000000, 9999999999))
    # 3. 生成当前时间戳（秒级）
    alarm["TIME_STAMP"] = str(int(time.time()))
    # 3.1 生成名称
    alarm['PROJ_NAME'] = "【传输网】【福州】C类割接：福州核心层PTN7900、 7900E版本升级FJ-0001-20250714-5201314"
    # 4. 生成唯一标识符，用于所有FP字段
    unique_id = str(int(time.time() * 1000000) % 10000000000)  # 使用微秒时间戳的一部分
    fp_suffix = f"{unique_id}_{random.randint(1000000000, 9999999999)}_{random.randint(1000000000, 9999999999)}_{random.randint(1000000000, 9999999999)}_2"

    # 5. 所有FP字段使用相同值
    alarm["FP0_FP1_FP2_FP3"] = fp_suffix
    alarm["CFP0_CFP1_CFP2_CFP3"] = fp_suffix
    alarm["ORIG_ALARM_FP"] = fp_suffix
    alarm["ORIG_ALARM_CLEAR_FP"] = fp_suffix

    return alarm


def delivery_report(err, msg):
    """发送结果回调函数（可选，用于监控失败消息）"""
    if err is not None:
        print(f"消息发送失败: {err}")
    # 可选：打印成功发送的消息偏移量
    # else:
    #     print(f"消息发送成功: {msg.topic()} [{msg.partition()}] offset {msg.offset()}")


# -------------------------- 核心发送逻辑 --------------------------
def batch_send_kafka_messages():
    # 1. 配置Kafka Producer（批量优化参数）
    producer_conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'batch.size': 1048576,  # 1MB 批量大小
        'linger.ms': 5,
        'compression.type': 'lz4',
        'acks': 1,
        'retries': 3,
        'max.in.flight.requests.per.connection': 10,
        'queue.buffering.max.messages': 1000000,
        'queue.buffering.max.kbytes': 1048576,
        'message.timeout.ms': 30000,
    }

    # 2. 创建Producer实例
    producer = Producer(producer_conf)

    # 3. 时间控制参数
    target_rate = 1000  # 每秒1000条
    batch_size = 1000  # 每批次1000条
    interval = 1.0  # 1秒间隔

    # 4. 批量发送消息
    start_time = time.time()
    success_count = 0
    fail_count = 0

    # 计算总批次数
    total_batches = TOTAL_MSG_COUNT // batch_size

    print(f"开始发送消息，总共 {TOTAL_MSG_COUNT} 条，分 {total_batches} 批次发送")

    for batch_num in range(total_batches):
        batch_start_time = time.time()

        # 发送一批消息
        for i in range(batch_size):
            try:
                # 生成唯一告警消息
                alarm_msg = generate_unique_alarm()
                # 序列化为JSON字符串
                msg_value = json.dumps(alarm_msg, ensure_ascii=False).encode('utf-8')

                # 生成key值
                msg_key = alarm_msg["ID"].encode('utf-8')

                # 异步发送消息
                producer.produce(
                    topic=KAFKA_TOPIC,
                    key=msg_key,
                    value=msg_value,
                    on_delivery=delivery_report
                )

                success_count += 1

            except Exception as e:
                print(f"第 {batch_num * batch_size + i} 条消息发送异常: {e}")
                fail_count += 1

        # 定期报告进度（每10批次报告一次）
        if (batch_num + 1) % 10 == 0:
            elapsed = time.time() - start_time
            actual_rate = success_count / elapsed if elapsed > 0 else 0
            print(f"已发送 {success_count} 条消息，耗时: {elapsed:.2f}s，实际速率: {actual_rate:.2f} 条/秒")

            # 添加key和FP0_FP1_FP2_FP3值的打印示例
            if success_count > 0:
                # 获取最近一条消息的示例数据
                sample_alarm = generate_unique_alarm()
                sample_key = sample_alarm["ID"]
                sample_fp = sample_alarm["FP0_FP1_FP2_FP3"]
                print(f"示例消息 - Key: {sample_key}, FP0_FP1_FP2_FP3: {sample_fp}")

        # 控制发送速率
        batch_end_time = time.time()
        batch_duration = batch_end_time - batch_start_time

        # 如果发送太快，等待剩余时间
        if batch_duration < interval:
            sleep_time = interval - batch_duration
            time.sleep(sleep_time)

        # 定期触发消息发送（每秒触发一次）
        producer.poll(0)

    # 4. 刷出剩余所有消息
    flush_start = time.time()
    print("正在刷出剩余消息...")
    producer.flush(timeout=30)
    flush_duration = time.time() - flush_start
    print(f"刷出剩余消息耗时: {flush_duration:.2f}s")

    # 5. 打印统计信息
    total_time = time.time() - start_time
    print("=" * 50)
    print(f"发送完成！总计: {TOTAL_MSG_COUNT} 条")
    print(f"成功: {success_count} 条 | 失败: {fail_count} 条")
    print(f"总耗时: {total_time:.2f}s | 平均速率: {TOTAL_MSG_COUNT / total_time:.2f} 条/秒")
    print("=" * 50)


if __name__ == "__main__":
    batch_send_kafka_messages()
