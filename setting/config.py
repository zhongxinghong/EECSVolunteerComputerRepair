#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: setting/config.py


import os
import time
from app.libs.config import SecretConfig

Root_Dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
secretCfg = SecretConfig()


__all__ = ["Config_Map",]


class Config(object):
    """ 基础配置 """

    DEBUG = True
    APPLICATION_ROOT = Root_Dir
    TRAP_BAD_REQUEST_ERRORS = False
    JSON_AS_ASCII = False

    SESSION_COOKIE_PATH = '/'
    SECRET_KEY = secretCfg.get('keys', 'Session_Key')

    @staticmethod
    def init_app(app):
        app.jinja_env.filters["strftime"] = lambda timestamp: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


class DevelopmentConfig(Config):
    """ 开发配置 """
    DEBUG = True


class ReleaseConfig(Config):
    """ 上线配置 """
    DEBUG = False


Config_Map = { # 注册 config
    'default': DevelopmentConfig,
    'develop': DevelopmentConfig,
    'release': ReleaseConfig,
}