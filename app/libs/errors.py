#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/libs/errors.py


__all__ = [

    "CustomError",

    "FormKeysError",
    "FormNullValueError",
    "FormIllegalValueError",
    "QueryMissingError",

    "OrderChksnVerifyError",
    "InvalidOrderInfoError",
    "RegisterTokenVerifyError",
    "SerialNumSignVerifyError",
    "AdminTokenVerifyError",

    "OrderRepeatError",
    "OrderNotFoundError",
]


class CustomError(Exception):
    """ 自定义错误的抽象基类

        Attributes:
            code    int    错误码
                               0 --- 无错误
                              -1 --- 未知错误
                             1xx --- 不应该出现的错误
                             2xx --- 鉴权类错误
            msg     str    错误描述
    """
    code = 0
    msg  = ""

    @classmethod
    def err_info(cls):
        return {"errcode": cls.code, "errmsg": cls.msg}


class FormKeysError(CustomError):
    code = 101
    msg  = "表单键错误"


class FormNullValueError(CustomError):
    code = 102
    msg  = "表单存在空值"


class FormIllegalValueError(CustomError):
    code = 103
    msg  = "表单值非法"


class QueryMissingError(CustomError):
    code = 104
    msg  = "URL 参数缺失"


class OrderChksnVerifyError(CustomError):
    code = 201
    msg  = "校验码验证失败"


class InvalidOrderInfoError(CustomError):
    code = 202
    msg  = "发送的订单字段非法"


class RegisterTokenVerifyError(CustomError):
    code = 203
    msg  = "挂号 token 校验失败"


class SerialNumSignVerifyError(CustomError):
    code = 204
    msg  = "流水号签名校验失败"


class AdminTokenVerifyError(CustomError):
    code = 205
    msg  = "管理员 token 校验失败"


class OrderRepeatError(CustomError):
    code = 301
    msg  = "订单重复创建"


class OrderNotFoundError(CustomError):
    code = 302
    msg  = "订单未找到"
