from airiot_python_sdk.flow_extension.startup import Startup
from flow_extension.my_flow_extension import MyFlowExtension

if __name__ == '__main__':
    startup = Startup()
    startup.run(MyFlowExtension())
