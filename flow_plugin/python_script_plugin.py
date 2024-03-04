import hashlib
import json
import logging
import traceback
from threading import Lock

from airiot_python_sdk.flow_plugin import FlowPlugin, FlowTask, FlowResult, FlowPluginType, DebugTask, DebugResult
from cacheout import Cache

logger = logging.getLogger("python-script-plugin")
entrypoint = "execute"
globalParameters = {}


class Runner:
    def __init__(self, ctx: dict):
        self.ctx = ctx
        if entrypoint not in ctx:
            raise Exception("未找到入口函数 execute")
        self.execute = ctx[entrypoint]

    def execute(self, inputs: dict) -> dict:
        return self.execute(inputs)


class PythonScriptPlugin(FlowPlugin):
    compile_lock = Lock()
    health_lock = Lock()
    jsonDecoder = json.JSONDecoder()
    jsonEncoder = json.JSONEncoder()
    cache: Cache

    def __init__(self, cache: Cache):
        self.cache = cache

    def get_name(self) -> str:
        return "pythonScript"

    def get_type(self) -> FlowPluginType:
        return FlowPluginType.ServiceTask

    def on_connection_state_changed(self, state: bool):
        if state:
            logger.info("connection state change: connected")
        else:
            logger.info("connection state change: disconnected")

    def start(self):
        logger.info("start python script plugin")

    def stop(self):
        logger.info("stop python script plugin")

    async def execute(self, request: FlowTask) -> FlowResult:
        config = self.jsonDecoder.decode(request.config.decode("utf-8"))
        inputs = config["input"]
        content = config["content"]

        # 执行脚本
        try:
            result = self._execute(request.projectId, inputs, content)
            logger.debug("run: success, args = %s, result = %s, script: \r\n%s", inputs, result, content)
            return FlowResult(message="OK", details="", data=result)
        except Exception as e:
            logger.error("run: failed, reason = %s, args = %s, script: \r\n%s", e, inputs, content)
            traceback.print_exc()
            raise Exception("执行脚本异常, {}".format(traceback.format_exc()))

    async def debug(self, task: DebugTask) -> DebugResult:
        config = self.jsonDecoder.decode(task.config.decode("utf-8"))
        inputs = config["input"]
        content = config["content"]
        # 执行脚本
        try:
            result = self._execute(task.projectId, inputs, content)
            logger.debug("debug: success, args = %s, result = %s, script: \r\n%s", inputs, result, content)
            return DebugResult(success=True, reason="", detail="", value=result, logs=[])
        except Exception as e:
            logger.error("debug: failed, reason = %s, args = %s, script: \r\n%s", e, inputs, content)
            traceback.print_exc()
            raise Exception("执行调试脚本异常, {}".format(traceback.format_exc()))

    def _execute(self, project_id: str, inputs: dict, script: str) -> dict:

        # 编译脚本
        try:
            logger.debug("compile: script\r\n%s", script)
            runner = self.compile(project_id, script)
        except Exception as e:
            logger.error("compile: failed, error = %s, script: \r\n%s", e, script)
            traceback.print_exc()
            raise Exception("编译脚本异常, {}".format(traceback.format_exc()))

        logger.debug("parse args: args = %s", inputs)

        # 解析输入参数
        logger.debug("args: %s", inputs)
        logger.debug("run: args = %s, script: \r\n%s", inputs, script)

        # 执行脚本
        try:
            result = runner.execute(inputs)
            logger.debug("run: success, args = %s, result = %s, script: \r\n%s", inputs, result, script)
            return result
        except Exception as e:
            logger.error("run: failed, reason = %s, args = %s, script: \r\n%s", e, inputs, script)
            traceback.print_exc()
            raise Exception("执行脚本异常, {}".format(traceback.format_exc()))

    def compile(self, project_id: str, script: str) -> Runner:
        # 获取脚本的 md5 值
        signature = hashlib.md5(script.encode("utf-8")).hexdigest()
        with self.compile_lock:
            # 如果脚本已经编译过, 则直接返回
            if self.cache.has(signature):
                logger.debug("compile: compiled. signature = %s, script: \r\n%s", signature, script)
                return self.cache.get(signature)

            # 如果没有编译过则重新编译并缓存编译结果
            logger.debug("compile: signature = %s, script: \r\n%s", signature, script)

            ctx = {}
            bytecode = compile(script, "<{}>".format(signature), "exec")
            exec(bytecode, ctx)

            logger.debug("compile: signature = %s, script: \r\n%s \r\nctx = %s", signature, script, ctx)

            runner = Runner(ctx)
            self.cache.add(signature, runner)
            return runner
