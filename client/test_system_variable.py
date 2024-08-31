import unittest

from airiot_python_sdk.client.api.system_variable import SystemVariableClient, SystemVariable, SystemVariableType
from airiot_python_sdk.client.authentication import AuthorizationType, create_auth_from_etcd
from airiot_python_sdk.client.sync import SyncClients


def to_dict(variables: list[SystemVariable]) -> dict:
    data = {}
    for variable in variables:
        data[variable.uid] = variable.value
    return data


class TestSystemVariableClient(unittest.TestCase):
    client: SystemVariableClient

    def setUp(self):
        # 创建平台认证(修改为自己的环境信息)
        # base_host: 平台的访问地址. 例如: http://127.0.0.1:3030/rest 或 http://127.0.0.1:31000
        # endpoint: 平台 etcd 服务访问地址. 例如: 127.0.0.1:2379
        # username: etcd 的用户名
        # password: etcd 的访问密码
        auth = create_auth_from_etcd(base_host="http://127.0.0.1:3030/rest", endpoint="127.0.0.1:2379",
                                     username="root", password="dell123")

        self.client = SyncClients("http://127.0.0.1:3030/rest", authentication=auth).get_system_variable_client()

    def test_create(self):
        variable = SystemVariable()
        variable.uid = "test_number"
        variable.type = SystemVariableType.Number
        variable.name = "数值变量"
        variable.value = 123.456

        print("创建系统变量:", variable)

        response = self.client.create(self.project_id, variable)
        self.assertTrue(response.success, f"创建系统变量失败, {response.message}")

    def test_get_by_uid(self):
        response = self.client.get_by_uid(self.project_id, "test_number")
        self.assertTrue(response.success, f"查询系统变量失败, {response.message}")
        self.assertEqual(len(response.data), 1, "查询系统变量失败, 未找到指定的系统变量")
        self.assertEqual(response.data[0].uid, "test_number", "查询系统变量失败, 未找到指定的系统变量")
        self.assertEqual(response.data[0].name, "数值变量", "查询系统变量失败, 未找到指定的系统变量")
        self.assertEqual(response.data[0].value, 123.456, "查询系统变量失败, 未找到指定的系统变量")
        print(response.data[0])

    def test_get_by_uids(self):
        variable1 = SystemVariable()
        variable1.uid = "test_array"
        variable1.type = SystemVariableType.Array
        variable1.name = "数组变量"
        variable1.value = [123, 456, 78.9]

        variable2 = SystemVariable()
        variable2.uid = "test_string"
        variable2.type = SystemVariableType.String
        variable2.name = "字符串变量"
        variable2.value = "hello 世界"

        response = self.client.create(self.project_id, variable1)
        self.assertTrue(response.success, f"创建系统变量1失败, {response.message}")

        response = self.client.create(self.project_id, variable2)
        self.assertTrue(response.success, f"创建系统变量2失败, {response.message}")

        response = self.client.get_by_uids(self.project_id, ["test_string", "test_array"])
        self.assertTrue(response.success, f"查询系统变量失败, {response.message}")
        self.assertEqual(len(response.data), 2, "查询系统变量失败, 未找到指定的系统变量")

        print(response.data)

        query_data = to_dict(response.data)
        self.assertEqual(query_data, {"test_string": "hello 世界", "test_array": [123, 456, 78.9]})

    def test_get_by_name(self):
        response = self.client.get_by_name(self.project_id, "数值变量")
        self.assertTrue(response.success, f"查询系统变量失败, {response.message}")
        self.assertEqual(len(response.data), 1, "查询系统变量失败, 未找到指定的系统变量")
        self.assertEqual(response.data[0].uid, "test_number", "查询系统变量失败, 未找到指定的系统变量")
        self.assertEqual(response.data[0].name, "数值变量", "查询系统变量失败, 未找到指定的系统变量")
        self.assertEqual(response.data[0].value, 123.456, "查询系统变量失败, 未找到指定的系统变量")
        print(response.data[0])

    def test_get_by_names(self):
        variable1 = SystemVariable()
        variable1.uid = "test_bool"
        variable1.type = SystemVariableType.Boolean
        variable1.name = "布尔变量"
        variable1.value = True

        variable2 = SystemVariable()
        variable2.uid = "test_object"
        variable2.type = SystemVariableType.Object
        variable2.name = "对象变量"
        variable2.value = {"name": "小明", "age": 23, "male": True}

        response = self.client.create(self.project_id, variable1)
        self.assertTrue(response.success, f"创建系统变量1失败, {response.message}")

        response = self.client.create(self.project_id, variable2)
        self.assertTrue(response.success, f"创建系统变量2失败, {response.message}")

        response = self.client.get_by_names(self.project_id, ["布尔变量", "对象变量"])
        self.assertTrue(response.success, f"查询系统变量失败, {response.message}")
        self.assertEqual(len(response.data), 2, "查询系统变量失败, 未找到指定的系统变量")

        print(response.data)

        query_data = to_dict(response.data)
        self.assertEqual(query_data, {"test_bool": True, "test_object": {"name": "小明", "age": 23, "male": True}})

    def test_update_value(self):
        response = self.client.update_value(self.project_id, "64f85798a089cbcffb3c02f1", 456.123)
        self.assertTrue(response.success, f"修改系统变量的值失败, {response.message}")

        response = self.client.get_by_id(self.project_id, "64f85798a089cbcffb3c02f1")
        self.assertTrue(response.success, f"查询系统变量失败, {response.message}")
        self.assertIsNotNone(response.data, "查询系统变量失败, 未找到指定的系统变量")
        self.assertEqual(response.data.value, 456.123, "查询系统变量失败, 未找到指定的系统变量")
        print(response.data)

    def test_update(self):
        variable = SystemVariable()
        variable.id = "64f85798a089cbcffb3c02f1"
        variable.name = "数值变量(修改后)"
        variable.value = 12.34

        response = self.client.update(self.project_id, variable)
        self.assertTrue(response.success, f"修改系统变量失败, {response.message}")

        response = self.client.get_by_id(self.project_id, "64f85798a089cbcffb3c02f1")
        self.assertTrue(response.success, f"查询系统变量失败, {response.message}")
        self.assertIsNotNone(response.data, "查询系统变量失败, 未找到指定的系统变量")
        self.assertEqual(response.data.name, "数值变量(修改后)", "查询系统变量失败, 未找到指定的系统变量")
        self.assertEqual(response.data.value, 12.34, "查询系统变量失败, 未找到指定的系统变量")
        print(response.data)

    def test_delete(self):
        response = self.client.delete(self.project_id, "64f85798a089cbcffb3c02f1")
        self.assertTrue(response.success, f"删除系统变量失败, {response.message}")

        response = self.client.get_by_id(self.project_id, "64f85798a089cbcffb3c02f1")
        self.assertTrue(response.success, f"查询系统变量失败, {response.message}")
        self.assertIsNotNone(response.data, "查询系统变量失败, 未找到指定的系统变量")


if __name__ == '__main__':
    unittest.main()
