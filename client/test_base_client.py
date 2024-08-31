import unittest
from airiot_python_sdk.client.sync._base_client import BaseClient


class TestBaseClient(unittest.TestCase):
    client: BaseClient

    def setUp(self):
        self.client = BaseClient("http://127.0.0.1:3030/rest")

    def test_perform_get(self):
        print("test_perform_get")
        setting = self.client.perform_get("/core/setting")
        print(setting)


if __name__ == '__main__':
    print("test_base_client.py")
    unittest.main()
