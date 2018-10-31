#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/libs/safety.py


import base64
import hashlib
import hmac
from Crypto import Random
from Crypto.Cipher import AES
from functools import partial

try:
    from .config import SecretConfig
    from .compat import json
    from .utils import singleton
except ImportError:
    from config import SecretConfig
    from compat import json
    from utils import singleton


secretCfg = SecretConfig()


__all__ = [

    "MD5", "SHA1", "SHA256",
    "HMAC_MD5", "HMAC_SHA1", "HMAC_SHA256",

    "OrderSign",
    "RegisterToken",
    "SerialNumSign",
    "AdminToken",

    "OrderCookiesAESCipher",
    "OrderRedirectAESCipher",
]


def to_bytes(data):
    if isinstance(data, bytes):
        return data
    elif isinstance(data, (str, int, float)):
        return str(data).encode('utf-8')
    else:
        raise TypeError('unsupported type %s' % type(data))

def to_utf8(data):
    if isinstance(data, (str, int, float)):
        return str(data)
    elif isinstance(data, bytes):
        return data.decode('utf-8')
    else:
        raise TypeError('unsupported type %s' % type(data))

def base64_encode(data):
    return to_utf8(base64.b64encode(to_bytes(data)))

def base64_decode(data):
    return base64.b64decode(data)

def urlsafe_base64_encode(data):
    return to_utf8(base64.urlsafe_b64encode(to_bytes(data)))

def urlsafe_base64_decode(data):
    return base64.urlsafe_b64decode(data)


def MD5(data):
    return hashlib.md5(to_bytes(data)).hexdigest()

def SHA1(data):
    return hashlib.sha1(to_bytes(data)).hexdigest()

def SHA256(data):
    return hashlib.sha256(to_bytes(data)).hexdigest()

def HMAC_MD5(key, data):
    return hmac.new(to_bytes(key), to_bytes(data), hashlib.md5).hexdigest()

def HMAC_SHA1(key, data):
    return hmac.new(to_bytes(key), to_bytes(data), hashlib.sha1).hexdigest()

def HMAC_SHA256(key, data):
    return hmac.new(to_bytes(key), to_bytes(data), hashlib.sha256).hexdigest()



class SignatureBuilder(object):
    """ 签名摘要的抽象基类

        Attributes:
            Alg     hashfunc    使用的摘要算法
            Key     str         签名秘钥
    """
    Alg = None
    Key = None

    def __init__(self):

        if self.Alg is None:
            raise NotImplementedError

        if self.Key is None:
            self._builder = self.__class__.Alg
        else:
            self._builder = partial(self.__class__.Alg, self.Key)

    @staticmethod
    def _serialize(data):
        """ 统一的序列化接口

            注： 暂时不可处理嵌套结构
        """
        if isinstance(data, (str,int,float)):
            return str(data)
        elif isinstance(data, dict): # 字典 --> {k1},{v1}.{k2},{v2}...
            return ".".join(",".join([k, str(v)]) for k, v in sorted(data.items()))
        elif isinstance(data, (list,tuple)): # 列表、元祖 --> {ele1}:{ele2}:{ele3}:...
            return ":".join(str(data))
        else:
            raise TypeError('unsupported type %s' % type(data))

    def create(self, raw):
        """ 生成摘要
        """
        return self._builder(self._serialize(raw))

    def verify(self, raw, digest):
        """ 校验摘要
        """
        return self.create(raw) == digest


@singleton
class OrderSign(SignatureBuilder):
    """ 订单信息校验码
    """
    Alg = HMAC_MD5
    Key = secretCfg.get('keys', 'Order_CheckSum')


@singleton
class RegisterToken(SignatureBuilder):
    """ 注册功能的鉴权 token
    """
    Alg = HMAC_MD5
    Key = secretCfg.get('keys', 'Register_Token')


@singleton
class SerialNumSign(SignatureBuilder):
    """ 流水号页面鉴权签名
    """
    Alg = HMAC_MD5
    Key = secretCfg.get('keys', 'SerialNum_Sign')


@singleton
class AdminToken(SignatureBuilder):
    """ 管理员 token
    """
    Alg = HMAC_SHA1
    Key = secretCfg.get('keys', 'Admin_Token')


class AESCipher(object):
    """ AES 密文编码的抽象基类

        Attributes:
            Key           str    秘钥
            Block_Size    int    块大小
            Mode          int    AES 加密模式
    """
    Key = ""

    Block_Size = 32
    Mode = AES.MODE_CBC

    def __init__(self):
        if self.Key == "":
            raise NotImplementedError
        self._key = hashlib.sha256(to_bytes(self.Key)).digest() # 32 bytes

    """
        AES 内部算法
        不应被修改
    """
    @classmethod
    def _pad(cls, s):
        bs = cls.Block_Size
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

    def _encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self._key, self.Mode, iv)
        return urlsafe_base64_encode(iv + cipher.encrypt(raw))

    def _decrypt(self, enc):
        enc = urlsafe_base64_decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self._key, self.Mode, iv)
        return to_utf8(self._unpad(cipher.decrypt(enc[AES.block_size:])))

    """
        外部接口
        可多态 methods
    """
    @staticmethod
    def _serialize(data):
        """ 序列化方法
            默认为 json.dumps
        """
        return json.dumps(data, sort_keys=True, separators=(",",":"))

    @staticmethod
    def _unserialize(data):
        """ 反序列化方法
            默认为 json.loads
        """
        return json.loads(data)

    def encrypt(self, raw):
        """ 加密接口
        """
        return self._encrypt(self._serialize(raw))

    def decrypt(self, enc):
        """ 解密接口
        """
        return self._unserialize(self._decrypt(enc))


@singleton
class OrderCookiesAESCipher(AESCipher):
    """ 用于 cookies 中 order 字段的加密解密
    """
    Key = secretCfg.get("keys", "Order_CookiesAES")

    def encrypt(self, orderInfo):
        raw = {k:v for k,v in orderInfo.items() if k in ("orderID",)}
        return self._encrypt(self._serialize(raw))


@singleton
class OrderRedirectAESCipher(AESCipher):
    """ 用于重定向过程中 order 字段的加密解密
    """
    Key = secretCfg.get("keys", "Order_Redirect")