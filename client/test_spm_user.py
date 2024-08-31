import unittest
from airiot_python_sdk.client.api.spm import SPMUserClient
from airiot_python_sdk.client.api.token import Token
from airiot_python_sdk.client.authentication import create_auth_from_etcd
from airiot_python_sdk.client.sync import SyncClients


class TestSPMUserClient(unittest.TestCase):
    client: SPMUserClient

    def setUp(self):
        # 创建平台认证(修改为自己的环境信息)
        # base_host: 平台的访问地址. 例如: http://127.0.0.1:3030/rest 或 http://127.0.0.1:31000
        # endpoint: 平台 etcd 服务访问地址. 例如: 127.0.0.1:2379
        # username: etcd 的用户名
        # password: etcd 的访问密码
        auth = create_auth_from_etcd(base_host="http://127.0.0.1:3030/rest", endpoint="127.0.0.1:2379",
                                     username="root", password="dell123")

        self.client = SyncClients("http://127.0.0.1:3030/rest", authentication=auth).get_spm_user_client()

    def test_login(self):
        resp = self.client.login("admin", "4k#eKh9WEw")
        self.assertTrue(resp.success)
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp.data)
        token = resp.data
        self.assertIsNotNone(token.token)
        print("token: {}, userId: {}".format(token.token, token.userId))

    def test_gettoken(self):
        resp = self.client.gettoken("138dd03b-d3ee-4230-d3d2-520feb580bfe", "138dd03b-d3ee-4230-d3d2-520feb580bfd")
        print(resp)
        self.assertTrue(resp.success)
        self.assertIsNotNone(resp)
        self.assertIsNotNone(resp.data)
        token: Token = resp.data
        self.assertIsNotNone(token.token)
        print("token: {}, userId: {}".format(token.token, token.userId))


if __name__ == '__main__':
    unittest.main()
