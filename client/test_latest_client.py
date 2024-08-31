import unittest

from airiot_python_sdk.client import LatestClient
from airiot_python_sdk.client.authentication import AuthorizationType, create_auth_from_etcd
from airiot_python_sdk.client.sync import SyncClients


class TestSystemVariableClient(unittest.TestCase):
    client: LatestClient

    def setUp(self):
        # 创建平台认证(修改为自己的环境信息)
        # base_host: 平台的访问地址. 例如: http://127.0.0.1:3030/rest 或 http://127.0.0.1:31000
        # endpoint: 平台 etcd 服务访问地址. 例如: 127.0.0.1:2379
        # username: etcd 的用户名
        # password: etcd 的访问密码
        self.project_id = "default"
        auth = create_auth_from_etcd(base_host="http://127.0.0.1:3030/rest", endpoint="127.0.0.1:2379",
                                     username="root", password="dell123")

        self.client = SyncClients("http://127.0.0.1:3030/rest", authentication=auth).get_latest_client()

    def test_get_device_all_tags(self):
        response = self.client.get_by_device_id(self.project_id, "java_mqtt_driver_demo", "javasdk001")
        self.assertTrue(response.success, f"查询设备所有数据点最新数据失败, {response.message}")
        print(response.data)

    def test_get_specified_tag(self):
        response = self.client.get_device_tag(self.project_id, "java_mqtt_driver_demo", "javasdk001", "key3")
        self.assertTrue(response.success, f"查询设备所有数据点最新数据失败, {response.message}")
        self.assertEqual(response.data[0].tableId, "java_mqtt_driver_demo")
        self.assertEqual(response.data[0].id, "javasdk001")
        self.assertEqual(response.data[0].tagId, "key3")
        self.assertIsNotNone(response.data[0].value)
        print(response.data)

    def test_get_devices_tag(self):
        response = self.client.get_every_device(self.project_id, "java_mqtt_driver_demo", ["javasdk001", "javasdk002"],
                                                "key3")
        self.assertTrue(response.success, f"查询设备所有数据点最新数据失败, {response.message}")
        self.assertEqual(response.data[0].tableId, "java_mqtt_driver_demo")
        self.assertEqual(response.data[0].id, "javasdk001")
        self.assertEqual(response.data[0].tagId, "key3")
        self.assertIsNotNone(response.data[0].value)
        print(response.data)

    def test_get_device_tags(self):
        response = self.client.get_device_tags(self.project_id, "java_mqtt_driver_demo", "javasdk001",
                                               ["key1", "key3"])
        self.assertTrue(response.success, f"查询设备所有数据点最新数据失败, {response.message}")
        self.assertEqual(response.data[0].tableId, "java_mqtt_driver_demo")
        self.assertEqual(response.data[0].id, "javasdk001")
        self.assertIsNotNone(response.data[0].value)
        print(response.data)


if __name__ == '__main__':
    unittest.main()
