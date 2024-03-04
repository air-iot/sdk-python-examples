from airiot_python_sdk.flow_plugin.startup import Startup

from flow_plugin.python_script_plugin import PythonScriptPlugin
from flow_plugin.script_cache import create_cache

if __name__ == '__main__':
    cache = create_cache()
    plugin = PythonScriptPlugin(cache)

    startup = Startup()
    startup.run(plugin)
