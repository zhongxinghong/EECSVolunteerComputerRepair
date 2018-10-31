#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/tools/get_register_token.py


import sys
sys.path.append("../")

from app.libs.config import GeneralConfig
from app.libs.safety import RegisterToken


generalCfg = GeneralConfig()
registerToken = RegisterToken()

Date = generalCfg.get('activity', 'date')


if __name__ == '__main__':
    token = registerToken.create(Date)
    print(token)
    path = "/order/page/register?token=%s" % token
    print(path)