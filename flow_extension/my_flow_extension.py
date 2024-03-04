from airiot_python_sdk.flow_extension import FlowExtension


class MyFlowExtension(FlowExtension):

    def id(self) -> str:
        return "python_flow_extension_example"

    def name(self) -> str:
        return "Python流程扩展节点示例"

    def start(self):
        print("python flow extension node started")
    
    def stop(self):
        print("python flow extension node stopped")

    async def schema(self) -> str:
        with open("schema.json", "r", encoding="utf-8") as f:
            return f.read()

    async def run(self, params: dict) -> dict:
        num1 = params["num1"]
        num2 = params["num2"]
        return {"result": num1 + num2}
