import datetime
import unittest

from airiot_python_sdk.client import TimingDataClient
from airiot_python_sdk.client.api.timing_data import TimingDataQueries
from airiot_python_sdk.client.authentication import AuthorizationType, create_auth_from_etcd
from airiot_python_sdk.client.sync import SyncClients


class TestTimingDataClient(unittest.TestCase):
    client: TimingDataClient

    def setUp(self):
        # 创建平台认证(修改为自己的环境信息)
        # base_host: 平台的访问地址. 例如: http://127.0.0.1:3030/rest 或 http://127.0.0.1:31000
        # endpoint: 平台 etcd 服务访问地址. 例如: 127.0.0.1:2379
        # username: etcd 的用户名
        # password: etcd 的访问密码
        auth = create_auth_from_etcd(base_host="http://127.0.0.1:3030/rest", endpoint="127.0.0.1:2379",
                                     username="root", password="dell123")

        self.client = SyncClients("http://127.0.0.1:3030/rest", authentication=auth).get_timing_data_client()

    def test_query1(self):
        query = (TimingDataQueries.new_builder().table("java_mqtt_driver_demo")
                 .select("id", "key1", "key2", "key3").since("7d").finish().build())
        response = self.client.query(self.project_id, query)
        self.assertTrue(response.success, f"查询时序数据失败, {response.full_message}")
        print("timing_data:", response.data)

    def test_query2(self):
        query = (TimingDataQueries.new_builder()
                 .table("java_mqtt_driver_demo")
                 .select("id", "key1", "key2", "key3")
                 .since("7d")
                 .group_by_device()
                 .finish()
                 .build())
        response = self.client.query(self.project_id, query)
        self.assertTrue(response.success, f"查询时序数据失败, {response.full_message}")
        print("timing_data:", response.data)

    def test_query3(self):
        """
        查询指定设备的时序数据
        :return:
        """
        query = (TimingDataQueries.new_builder().table("java_mqtt_driver_demo")
                 .select("id", "key1", "key2", "key3").since("7d")
                 .device("javasdk001")
                 .finish().build())
        response = self.client.query(self.project_id, query)
        self.assertTrue(response.success, f"查询时序数据失败, {response.full_message}")
        print("timing_data:", response.data)

    def test_query4(self):
        query = (TimingDataQueries.new_builder().table("java_mqtt_driver_demo")
                 .select("id", "key1", "key2", "key3")
                 .end_time(datetime.datetime.today())
                 .device("javasdk001")
                 .finish().build())
        response = self.client.query(self.project_id, query)
        self.assertTrue(response.success, f"查询时序数据失败, {response.full_message}")
        print("timing_data:", response.data)

    def test_query5(self):
        query = (TimingDataQueries.new_builder().table("java_mqtt_driver_demo")
                 .select("id", "key1", "key2", "key3")
                 .end_time(datetime.datetime.today())
                 .gt("key1", 6666)
                 .device("javasdk001")
                 .finish().build())
        response = self.client.query(self.project_id, query)
        self.assertTrue(response.success, f"查询时序数据失败, {response.full_message}")
        print("timing_data:", response.data)


if __name__ == '__main__':
    unittest.main()
