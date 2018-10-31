#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/libs/utils.py


import os

try:
    from .errors import CustomError
    from .compat import json
except ImportError:
    from errors import CustomError
    from compat import json


__all__ = [

    "singleton",
    "iter_flat",
    "error_json",
]


def singleton(cls):
    """ 单例模式 类修饰器
    """
    __instances = {}
    def __get_instance(*args, **kwargs):
        if cls not in __instances:
            __instances[cls] = cls(*args, **kwargs)
        return __instances[cls]
    return __get_instance


def iter_flat(origin):
    """ 嵌套序列打平
    """
    resultsList = []
    for item in origin:
        if isinstance(item, (list,tuple)):
            resultsList.extend(iter_flat(item))
        else:
            resultsList.append(item)
    return resultsList


def error_json(err=None):
    """ 统一格式化输出错误描述的 json 字段
    """
    if err is None: # 没有错误
        return {"errcode": 0, "errmsg": "success"}
    elif err.__class__.__name__ == CustomError.__name__:
        raise NotImplementedError
    elif not issubclass(err.__class__, CustomError): # 非自定义错误
        return {"errcode": -1, "errmsg": repr(err)}  # 输出原始错误描述
    else: # 自定义错误类
        return {"errcode": err.code, "errmsg": err.msg}