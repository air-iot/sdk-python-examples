import asyncio
import datetime
import logging
import traceback
from asyncio import AbstractEventLoop
from typing import List, Optional, Callable

import js2py
import jsons
import urllib3.util
from paho.mqtt import client as mqtt_client
from paho.mqtt.reasoncodes import ReasonCodes

from airiot_python_sdk.driver import DriverApp, DataSender, DriverAppFactory
from airiot_python_sdk.driver.model.point import Field, Point
from model import MQTTDriverConfig, ModelConfig, MQTTTag

logger = logging.getLogger("mqtt_driver")


class MqttSubscription:
    """
    工作表消息订阅处理
    """

    data_sender: DataSender
    client: mqtt_client.Client
    table: ModelConfig

    # 工作表中各设备的数据点信息
    device_tags: dict[str, dict[str, MQTTTag]] = {}

    parse_script: Callable
    command_script: Callable

    def __init__(self, loop: AbstractEventLoop, client: mqtt_client.Client, data_sender: DataSender,
                 table: ModelConfig):
        self.data_sender = data_sender
        self.client = client
        self.table = table
        self.parse_script = js2py.eval_js(table.device.settings.parseScript)
        self.command_script = js2py.eval_js(table.device.settings.commandScript)
        self.loop = loop

        config = table.device
        for device in table.devices:
            # 合并工作表和设备的配置
            if device.device is None:
                device.device = config
            else:
                device.device.merge(config)

            device_settings = device.device.settings

            # 如果设备配置中没有自定义设备 ID，则使用资产编号作为自定义设备 ID
            if device_settings.customDeviceId is None:
                device_settings.customDeviceId = device.id

            device_tags = {}
            if device.device.tags is None or len(device.device.tags) == 0:
                continue

            for tag in device.device.tags:
                device_tags[tag.key] = tag

            self.device_tags[device.id] = device_tags

    def subscribe(self):
        settings = self.table.device.settings
        self.client.message_callback_add(settings.topic, self.on_message)
        self.client.subscribe(settings.topic)

    def on_message(self, mosq, obj, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8")

        points = []

        try:
            print("topic:", topic)
            print("payload:", payload)

            result = self.parse_script(topic, payload)
            print("result:", result)

            if result is None or len(result) == 0:
                logger.warning("数据处理脚本返回结果为空, 工作表: %s, topic: %s, payload: %s",
                               self.table.id, topic, payload)
                return

            for dev in result:
                dev_id = dev.get("id")
                if dev_id is None:
                    logger.warning("未找到资产, 工作表: %s, 资产编号: %s", self.table.id, dev.id)
                    continue

                fields = dev.get("fields")
                if fields is None or len(fields) == 0:
                    logger.warning("数据处理脚本返回结果中 fields 为空, 工作表: %s, topic: %s, payload: %s, result: %s",
                                   self.table.id, topic, payload, dev)
                    return

                if dev_id not in self.device_tags:
                    logger.warning("数据处理脚本返回结果: 未找到设备 '%s', data=%s", dev_id, dev)
                    continue

                dev_tags = self.device_tags[dev_id]
                send_fields = []

                for field in fields:
                    if field not in dev_tags:
                        logger.warning("未在设备中找到数据点, 工作表: %s, 资产编号: %s, 数据点: %s", self.table.id,
                                       dev_id, field)
                        continue
                    send_fields.append(Field(dev_tags[field], fields[field]))

                if len(send_fields) == 0:
                    logger.warning("未找到可发送的数据点, 工作表: %s, 资产编号: %s, fields: %s", self.table.id, dev_id,
                                   fields)
                    continue

                point = Point()
                point.table = self.table.id
                point.id = dev_id
                point.fields = send_fields
                point.time = int(datetime.datetime.now().timestamp()) * 1000

                points.append(point)
        except Exception as e:
            traceback.print_exception(e)
            logger.error("解析数据处理脚本返回值异常: %s", e)
        
        for point in points:
            try:
                self.loop.run_until_complete(self.data_sender.write_point(point))
            except Exception as e:
                traceback.print_exception(e)
                logger.error("发送数据点异常: %s", e)


class MqttDriverApp(DriverApp):
    service_id: str
    data_sender: DataSender
    client: Optional[mqtt_client.Client] = None

    # 工作表与订阅. key 为工作表 ID, value 为订阅对象
    subscriptions: dict[str, MqttSubscription] = {}

    def __init__(self, service_id: str, data_sender: DataSender):
        self.service_id = service_id
        self.data_sender = data_sender
        self.loop = asyncio.new_event_loop()

    def __create_mqtt_client__(self, config: MQTTDriverConfig):
        """
        根据驱动实例配置创建 mqtt 客户端
        :param config: 驱动实例配置
        :return:
        """
        settings = config.device.settings
        broker_url = urllib3.util.parse_url(settings.server)

        logger.info("connect to mqtt: %s", settings.server)

        self.client = mqtt_client.Client(client_id="mqtt_driver_{}".format(self.service_id),
                                         clean_session=True, protocol=mqtt_client.MQTTv311)
        self.client.username_pw_set(settings.username, settings.password)
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        # self.client.on_disconnect = lambda: (logger.error("mqtt client disconnected"))
        # self.client.on_connect = lambda x1, x2, x3, x4: logger.info("mqtt client connected")
        self.client.connect(host=broker_url.host, port=broker_url.port, keepalive=60)

    def handle_table(self, table: ModelConfig):
        """
        根据工作表的设备配置订阅 mqtt 主题
        :param table:
        :return:
        """

        table_id = table.id
        config = table.device

        logger.info("handle table: {}".format(table_id))

        if config is None:
            logger.warning("工作表 '%s' 的设备配置为空", table_id)
            return

        settings = config.settings
        devices = table.devices

        if len(devices) == 0:
            logger.warning("工作表 '%s' 的设备列表为空", table_id)
            return

        if settings is None or settings.topic is None or len(settings.topic) == 0:
            logger.warning("工作表 '%s' 的设备配置中 topic 为空", table_id)
            return

        logger.info("工作表 '%s', 订阅主题: %s", table_id, settings.topic)
        subscription = MqttSubscription(self.loop, self.client, self.data_sender, table)
        subscription.subscribe()
        self.subscriptions[table_id] = subscription

    async def start(self, config: str):
        logger.info("driver start: {}".format(config))
        driver_config: MQTTDriverConfig = jsons.loads(config, MQTTDriverConfig)
        logger.info("driver start, config: {}".format(driver_config))

        await self.stop()

        tables = driver_config.tables
        if tables is None or len(tables) == 0:
            logger.warning("没有任何工作表使用该驱动")
            return

        # 创建 mqtt 客户端
        self.__create_mqtt_client__(driver_config)

        # 处理每个使用该驱动实例的工作表
        for table in tables:
            try:
                self.handle_table(table)
            except Exception as e:
                traceback.print_stack()
                logger.error("处理工作表 '{}' 时出错: {}".format(table.id, e))

        logger.info("mqtt driver started")

        self.data_sender.send_warning()

        self.client.loop_start()

    async def stop(self):
        logger.info("stopping mqtt driver")

        if self.client is not None:
            self.client.loop_stop()
            self.client.disconnect(reasoncode=ReasonCodes)

        self.subscriptions = {}

        logger.info("mqtt driver stopped")

    def get_version(self) -> str:
        return "v4.0.0"

    def http_proxy_enabled(self) -> bool:
        return False

    async def http_proxy(self, request_type: str, headers: dict[str, List[str]], data: str) -> any:
        return data

    async def run(self, serial_no: str, table_id: str, device_id: str, command: str) -> any:
        pass

    async def batch_run(self, serial_no: str, table_id: str, device_ids: List[str], command: str) -> any:
        pass

    async def write_tag(self, serial_no: str, table_id: str, device_id: str, tag: str) -> any:
        pass

    async def debug(self, debug: str) -> str:
        pass

    async def schema(self) -> str:
        with open('schema.js', 'r', encoding="utf-8") as f:
            return f.read()


class MqttDriverFactory(DriverAppFactory):

    def create(self, service_id: str, data_sender: DataSender) -> DriverApp:
        return MqttDriverApp(service_id, data_sender)
