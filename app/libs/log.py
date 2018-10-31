#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/libs/log.py


import logging


__all__ = ["Logger",]


class Logger(object):
    """ [日志类，logging 模块的封装]

        Attributes:
            class:
                Default_Name     str                    缺省的日志名
            instance:
                logger           logging.Logger         logging 的 Logger 对象
                level            int                    logging.level 级别
                console_headler  logging.StreamHandler  控制台日志 handler
    """
    Default_Name = __name__

    def __init__(self, name=None):
        self.logger = logging.getLogger(name or self.Default_Name)
        self.level = logging.DEBUG
        self.logger.setLevel(self.level)
        self.logger.addHandler(self.console_headler)

    @property
    def console_headler(self):
        console_headler = logging.StreamHandler()
        console_headler.setLevel(self.level)
        console_headler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s, %(asctime)s, %(message)s", "%Y-%m-%d %H:%M:%S"))
        return console_headler

    """
        以下是对 logging 的六种 level 输出函数的封装
        并定义 __call__ = logging.info
    """
    def debug(self, *args, **kwargs):
        return self.logger.debug(*args, **kwargs)

    def info(self, *args, **kwargs):
        return self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        return self.logger.warning(*args, **kwargs)

    def exception(self, *args, **kwargs):
        return self.logger.exception(*args, **kwargs)

    def error(self, *args, **kwargs):
        return self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        return self.logger.critical(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.info(*args, **kwargs)