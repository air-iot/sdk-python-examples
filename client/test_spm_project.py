import unittest

from airiot_python_sdk.client.api.spm import SPMProjectClient
from airiot_python_sdk.client.authentication import AuthorizationType, create_auth_from_etcd
from airiot_python_sdk.client.sync import SyncClients


class TestSPMProjectClient(unittest.TestCase):
    client: SPMProjectClient

    def setUp(self):
        # 创建平台认证(修改为自己的环境信息)
        # base_host: 平台的访问地址. 例如: http://127.0.0.1:3030/rest 或 http://127.0.0.1:31000
        # endpoint: 平台 etcd 服务访问地址. 例如: 127.0.0.1:2379
        # username: etcd 的用户名
        # password: etcd 的访问密码
        auth = create_auth_from_etcd(base_host="http://127.0.0.1:3030/rest", endpoint="127.0.0.1:2379",
                                     username="root", password="dell123")

        self.client = SyncClients("http://127.0.0.1:3030/rest", authentication=auth).get_spm_project_client()

    def test_query_by_id(self):
        resp = self.client.query_by_id("647d3f6db395ea47865d4b9e")
        print(resp)


if __name__ == '__main__':
    unittest.main()
