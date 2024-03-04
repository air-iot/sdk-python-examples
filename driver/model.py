import dataclasses
from typing import Optional

from airiot_python_sdk.driver.model.tag import Tag


@dataclasses.dataclass
class Settings:
    """
    驱动配置

    Attributes:
        server: MQTT 服务器地址
        username: MQTT 用户名
        password: MQTT 密码
        topic: MQTT 主题
        parseScript: 解析脚本
        commandScript: 命令脚本
        customDeviceId: 自定义设备 ID
    """
    server: Optional[str]
    username: Optional[str]
    password: Optional[str]
    topic: Optional[str]
    parseScript: Optional[str]
    commandScript: Optional[str]
    customDeviceId: Optional[str]

    def merge(self, other):
        """
        合并配置
        :param other:
        :return:
        """
        if other is None:
            return

        self.server = self.server if self.server is not None else other.server
        self.username = self.username if self.username is not None else other.username
        self.password = self.password if self.password is not None else other.password
        self.topic = self.topic if self.topic is not None else other.topic
        self.parseScript = self.parseScript if self.parseScript is not None else other.parseScript
        self.commandScript = self.commandScript if self.commandScript is not None else other.commandScript
        self.customDeviceId = self.customDeviceId if self.customDeviceId is not None else other.customDeviceId


@dataclasses.dataclass
class MQTTTag(Tag):
    """
    MQTT 自定义数据点信息

    Attributes:
        key: 数据点在 MQTT 消息中的键名
    """
    key: str


@dataclasses.dataclass
class DriverConfig:
    """
    设备配置

    Attributes:
        settings: 驱动配置
        tags: 数据点列表
    """
    settings: Optional[Settings]
    tags: Optional[list[MQTTTag]]

    def merge(self, other):
        """
        合并配置
        :param other:
        :return:
        """

        if other is None:
            return

        if self.settings is None and other.settings is not None:
            self.settings = other.settings
        elif self.settings is not None and other.settings is not None:
            self.settings.merge(other.settings)

        if self.tags is None:
            self.tags = [] if other.tags is None else other.tags
        elif len(self.tags) == 0 and len(other.tags) > 0:
            self.tags = other.tags
        elif len(self.tags) > 0 and len(other.tags) > 0:
            exists_tags = {}
            for tag in self.tags:
                exists_tags[tag.id] = True

            for tag in other.tags:
                if tag.id not in exists_tags:
                    self.tags.append(tag)


@dataclasses.dataclass
class Device:
    """
    设备配置

    Attributes:
        id: 设备ID
        device: 驱动配置
    """
    id: str
    device: DriverConfig


@dataclasses.dataclass
class ModelConfig:
    """
    模型配置

    Attributes:
        id: 工作表标识
        device: 驱动配置
        devices: 设备列表
    """
    id: str
    device: DriverConfig
    devices: list[Device]


@dataclasses.dataclass
class MQTTDriverConfig:
    """
    驱动实例配置

    Attributes:
        id: 驱动实例 ID
        name: 驱动名称
        driverType: 驱动ID
        device: 设备配置
    """

    id: str
    name: str
    driverType: str
    device: DriverConfig
    tables: list[ModelConfig]
