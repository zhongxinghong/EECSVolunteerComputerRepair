#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/libs/config.py


import os
from configparser import RawConfigParser

try:
    from .utils import singleton
except ImportError:
    from utils import singleton


Root_Dir = os.path.join(os.path.dirname(__file__), "../")
Setting_Dir = os.path.join(Root_Dir, "../setting")


__all__ = [
    "GeneralConfig",
    "SecretConfig",
]


class Config(object):
    """ 配置文件类的抽象基类
    """
    FileName = ""

    def __init__(self):
        if self.FileName == "":
            raise NotImplementedError
        path = os.path.join(Setting_Dir, self.FileName)
        if not os.path.exists(path):
            raise FileNotFoundError("config file %s is missing !" % path)
        self._config = RawConfigParser(allow_no_value=True)
        self._config.read(path, encoding="utf-8-sig") # 必须显示指明 encoding

    def __getitem__(self, idx):
        """ config[] 操作运算的封装
        """
        return self._config[idx]

    def sections(self):
        """ config.sections 函数的封装
        """
        return self._config.sections()

    @staticmethod
    def __get(get_fn, section, key, **kwargs):
        """ 配置文件 get 函数模板

            Args:
                get_fn     function    原始的 config.get 函数
                section    str         section 名称
                key        str         section 下的 option 名称
                **kwargs               传入 get_fn
            Returns:
                value      str/int/float/bool   返回相应 section 下相应 key 的 value 值
        """
        value = get_fn(section, key, **kwargs)
        if value is None:
            raise ValueError("key '%s' in section [%s] is missing !" % (key, section))
        else:
            return value

    """
        以下对四个 config.get 函数进行封装

        Args:
            section    str    section 名称
            key        str    section 下的 option 名称
        Returns:
            value             以特定类型返回相应 section 下相应 key 的 value 值
    """
    def get(self, section, key):
        return self.__get(self._config.get, section, key)

    def getint(self, section, key):
        return self.__get(self._config.getint, section, key)

    def getfloat(self, section, key):
        return self.__get(self._config.getfloat, section, key)

    def getboolean(self, section, key):
        return self.__get(self._config.getboolean, section, key)


@singleton
class GeneralConfig(Config):
    """ 通用配置
    """
    FileName = "setting.ini"


@singleton
class SecretConfig(Config):
    """ 隐私配置
    """
    FileName = "secret.ini"


