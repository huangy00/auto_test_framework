# -*- coding: utf-8 -*-
"""
配置读取工具模块
负责读取 config/config.ini 配置文件，提供统一的配置访问接口
"""
import os
import configparser


# 获取项目根目录（config文件的上级目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.ini")
CONFIG_EXAMPLE_PATH = os.path.join(BASE_DIR, "config", "config.ini.example")


class ConfigReader:
    """配置文件读取器，封装 configparser 提供便捷访问方法"""

    def __init__(self, config_path: str = None):
        """
        初始化配置读取器
        :param config_path: 配置文件路径，默认为 config/config.ini；
                            config.ini 不存在时回退到 config/config.ini.example（如 CI 环境）
        """
        path = config_path or CONFIG_PATH
        if not os.path.exists(path) and os.path.exists(CONFIG_EXAMPLE_PATH):
            path = CONFIG_EXAMPLE_PATH
        self.config = configparser.ConfigParser()
        self.config.read(path, encoding="utf-8")

    def get(self, section: str, key: str) -> str:
        """
        获取字符串配置值
        优先级：环境变量（如 DB_PASSWORD、UI_BASE_URL）> config/config.ini
        这样数据库密码等敏感信息可通过环境变量注入，无需提交到仓库
        :param section: 配置节名称（如 [ui], [db]）
        :param key: 配置键名
        :return: 配置值字符串
        """
        env_key = f"{section}_{key}".upper()
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value
        return self.config.get(section, key)

    def getint(self, section: str, key: str) -> int:
        """
        获取整数配置值
        :param section: 配置节名称
        :param key: 配置键名
        :return: 配置值整数
        """
        return int(self.get(section, key))


# 全局单例，方便其他模块直接导入使用
config = ConfigReader()
