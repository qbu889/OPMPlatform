import unittest
from flask import Flask
from routes.kafka_routes import kafka_bp, generate_unique_fp, get_formatted_time, get_time_minus_minutes, load_es_data, generate_kafka_from_es

class TestKafkaRoutes(unittest.TestCase):

    def setUp(self):
        # 创建一个测试客户端
        self.app = Flask(__name__)
        self.app.register_blueprint(kafka_bp)
        self.client = self.app.test_client()

    def test_generate_unique_fp(self):
        # 测试生成唯一FP值的函数
        fp = generate_unique_fp()
        self.assertIsInstance(fp, str)
        self.assertIn('_', fp)  # 确保FP值包含下划线

    def test_get_formatted_time(self):
        # 测试获取格式化时间的函数
        formatted_time = get_formatted_time()
        self.assertIsInstance(formatted_time, str)
        self.assertIn(':', formatted_time)  # 确保时间格式包含冒号

    def test_get_time_minus_minutes(self):
        # 测试获取减去指定分钟数的时间函数
        time_minus_10 = get_time_minus_minutes(10)
        self.assertIsInstance(time_minus_10, str)
        self.assertIn(':', time_minus_10)  # 确保时间格式包含冒号

    def test_load_es_data_wireless(self):
        # 测试加载无线类型的ES数据
        es_data = load_es_data('wireless')
        self.assertEqual(es_data['NETWORK_TYPE_TOP'], '1')
        self.assertEqual(es_data['VENDOR_NAME'], '诺基亚')

    def test_load_es_data_enterprise(self):
        # 测试加载企业类型的ES数据
        es_data = load_es_data('enterprise')
        self.assertEqual(es_data['NETWORK_TYPE_TOP'], '11')
        self.assertEqual(es_data['VENDOR_ID'], '323')

    def test_load_es_data_home_broadband(self):
        # 测试加载家宽类型的ES数据
        es_data = load_es_data('home_broadband')
        self.assertEqual(es_data['NETWORK_TYPE_TOP'], '12')
        self.assertEqual(es_data['VENDOR_NAME'], '中兴')

    def test_load_es_data_power_equipment(self):
        # 测试加载电源设备类型的ES数据
        es_data = load_es_data('power_equipment')
        self.assertEqual(es_data['NETWORK_TYPE_TOP'], '5')
        self.assertEqual(es_data['VENDOR_NAME'], '高新兴')

    def test_generate_kafka_from_es(self):
        # 测试根据ES数据生成Kafka消息的函数
        es_data = load_es_data('wireless')
        room_id = 'TEST-ROOM-ID'
        machine_room_info = '测试机房信息'
        kafka_msg = generate_kafka_from_es(es_data, room_id, machine_room_info)

        self.assertEqual(kafka_msg['SPECIAL_FIELD14'], room_id)
        self.assertEqual(kafka_msg['MACHINE_ROOM_INFO'], machine_room_info)
        self.assertIn('FP0_FP1_FP2_FP3', kafka_msg)
        self.assertIn('EVENT_TIME', kafka_msg)

if __name__ == '__main__':
    unittest.main()
''