import dataclasses
import unittest

from airiot_python_sdk.client import WorkTableDataClient
from airiot_python_sdk.client.api.query import Query
from airiot_python_sdk.client.authentication import AuthorizationType, Authentication, create_auth_from_etcd
from airiot_python_sdk.client.sync import SyncClients


@dataclasses.dataclass
class Student:
    id: str
    name: str
    age: int
    sex: str

    def __init__(self, id: str = None, name: str = None, age: int = None, sex: str = None):
        self.id = id
        self.name = name
        self.age = age
        self.sex = sex

    @staticmethod
    def __fields__():
        return ["id", "name", "age", "sex"]


class TestWorktableDataClient(unittest.TestCase):
    client: WorkTableDataClient

    def setUp(self):
        # 创建平台认证(修改为自己的环境信息)
        # base_host: 平台的访问地址. 例如: http://127.0.0.1:3030/rest 或 http://127.0.0.1:31000
        # endpoint: 平台 etcd 服务访问地址. 例如: 127.0.0.1:2379
        # username: etcd 的用户名
        # password: etcd 的访问密码
        self.project_id = "default"
        auth = create_auth_from_etcd(base_host="http://127.0.0.1:3030/rest", endpoint="127.0.0.1:2379",
                                     username="root", password="dell123")

        self.client = SyncClients("http://127.0.0.1:3030/rest", authentication=auth).get_worktable_client()

    def test_create(self):
        s1 = {'name': '小红', 'age': 18, 'sex': "female"}
        response = self.client.create(self.project_id, "student", s1)
        self.assertTrue(response.success, f"新增记录失败, {response.full_message}")
        print(response)

    def test_create_batch(self):
        # ss = [Student(name="张三", age=15, sex="male"), Student(name="李四", age=18, sex="female"),
        #       Student(name="王五", age=23, sex="male")]

        ss = [
            {'name': '张三', 'age': 15, 'sex': "male"},
            {'name': '李四', 'age': 18, 'sex': "female"},
            {'name': '王五', 'age': 23, 'sex': "male"},
        ]
        response = self.client.create_batch(self.project_id, "student", ss)
        self.assertTrue(response.success, f"新增记录失败, {response.full_message}")
        self.assertIsNotNone(response.data, f"新增记录失败, {response.full_message}")
        self.assertEqual(len(response.data.InsertedIDs), 3, "新增记录返回ID数量不正确")
        print(response)

    def test_query_by_id(self):
        response = self.client.query_by_id(self.project_id, "student", "64edca489666e6d6007da49b")
        self.assertTrue(response.success, response.full_message)
        self.assertIsNotNone(response.data, "未查询到记录")
        self.assertEqual(response.data["name"], "小明", "查询结果不匹配")
        print(response.data)

    def test_query(self):
        query = (Query.new_builder().select(*Student.__fields__())
                 .filter()
                 .eq("name", "小红")
                 .end()
                 .build())
        response = self.client.query(self.project_id, "student", query)
        self.assertTrue(response.success, response.full_message)
        self.assertIsNotNone(response.data, "未查询到记录")
        self.assertEqual(response.data[0]["name"], "小红", "查询结果不匹配")
        print(response.data)

    def test_query_many(self):
        query = (Query.new_builder().select(*Student.__fields__())
                 .filter()
                 .between("age", 16, 20)
                 .end()
                 .build())
        response = self.client.query(self.project_id, "student", query)
        self.assertTrue(response.success, response.full_message)
        self.assertIsNotNone(response.data, "未查询到记录")
        print(response.data)

    def test_update(self):
        response = self.client.update(self.project_id, "student", "64eea53596483dd032f78945",
                                      {"name": "又更新了名称了", "age": 33})
        self.assertTrue(response.success, f"更新工作表记录失败, {response.full_message}")

        response = self.client.query_by_id(self.project_id, 'student', '64eea53596483dd032f78945')
        self.assertTrue(response.success, response.full_message)
        self.assertIsNotNone(response.data, "未查询到记录")
        self.assertEqual(response.data["name"], "又更新了名称了", "未查询到记录")
        self.assertEqual(response.data["age"], 33, "未查询到记录")
        print(response)

    def test_update_batch(self):
        query_filter = Query.new_builder().filter().between("age", 16, 20).end().build()
        response = self.client.update_many(self.project_id, "student", query_filter,
                                           {"name": "又更新了名称了", "age": 44})
        self.assertTrue(response.success, f"更新工作表记录失败, {response.full_message}")

    def test_delete_by_id(self):
        response = self.client.delete_by_id(self.project_id, "student", "64f998465ec4fed5bfe1608b")
        self.assertTrue(response.success, f"删除工作表记录失败, {response.full_message}")

        response = self.client.query_by_id(self.project_id, "student", "64f998465ec4fed5bfe1608b")
        self.assertTrue(response.success, response.full_message)
        self.assertIsNotNone(response.data, "删除失败")
        print(response.data)

    def test_delete(self):
        query = Query.new_builder().filter().gt("age", 30).end().build()
        response = self.client.delete(self.project_id, "student", query)
        self.assertTrue(response.success, f"删除工作表记录失败, {response.full_message}")

        query = (Query.new_builder().select(*Student.__fields__())
                 .filter()
                 .gt("age", 30)
                 .end()
                 .build())
        response = self.client.query(self.project_id, "student", query)
        self.assertTrue(response.success, response.full_message)
        self.assertEqual(len(response.data), 0, "工作表记录未删除")
        print(response.data)


if __name__ == '__main__':
    unittest.main()
