import datetime
import logging

from airiot_python_sdk.algorithm import AlgorithmApp, algorithm_function

logger = logging.getLogger("algorithm-example")


class MyAlgorithmApp(AlgorithmApp):

    def id(self) -> str:
        return "PythonAlgorithmSDKExample"

    def name(self) -> str:
        return "Python算法SDK示例程序"

    def start(self):
        logger.info("Python算法示例程序已启动")

    def stop(self):
        logger.info("Python算法示例程序已停止")

    async def schema(self) -> str:
        with open('schema.js', 'r', encoding="utf-8") as f:
            return f.read()

    async def run(self, project_id: str, function: str, params: dict[str, any]) -> [dict[str, any] | object]:
        logger.info("执行算法: project_id = %s, function = %s, params = %s", project_id, function, params)
        return {}

    @algorithm_function(name="add")
    async def add(self, project_id: str, params: dict[str, any]) -> [dict[str, any] | object]:
        num1 = params["num1"]
        num2 = params["num2"]
        return {"num1": num1 + num2}

    @algorithm_function(name="abs")
    async def abs(self, project_id: str, params: dict[str, any]) -> [dict[str, any] | object]:
        num = params["num1"]
        return {"num": abs(num)}

    @algorithm_function(name="now")
    async def now(self, project_id: str, params: dict[str, any]) -> [dict[str, any] | object]:
        return {"sysdate": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
