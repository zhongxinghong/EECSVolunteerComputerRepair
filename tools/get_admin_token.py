#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/tools/get_register_token.py


import sys
sys.path.append("../")

from app.libs.config import SecretConfig
from app.libs.safety import AdminToken


secretCfg = SecretConfig()
adminToken = AdminToken()

Admin_Account = secretCfg.get('admin', 'account')


if __name__ == '__main__':
    token = adminToken.create(Admin_Account)
    print(token)
    path = "/admin/page/queue?token=%s" % token
    print(path)