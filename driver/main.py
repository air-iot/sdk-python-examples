from airiot_python_sdk.driver.startup import Startup
from driver.mqtt_driver import MqttDriverFactory

if __name__ == "__main__":
    command_line = Startup()
    command_line.run(MqttDriverFactory())
