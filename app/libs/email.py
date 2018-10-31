#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/libs/email.py


import os
import time
import jinja2
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from email.header import Header

try:
    from .config import SecretConfig
except ImportError:
    from config import SecretConfig


secretCfg = SecretConfig()

Root_Dir = os.path.join(os.path.dirname(__file__), "../")
Templates_Dir = os.path.join(Root_Dir, "templates/email/")

jinja_env = jinja2.Environment()
jinja_env.filters["strftime"] = lambda timestamp: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


__all__ = ["OrderMailer",]


class OrderMailer(object):

    SMTP_Domain = secretCfg.get('email', 'domain')
    SMTP_Port = secretCfg.getint('email', 'port')

    SMTP_Account = secretCfg.get('email', 'account')
    Authorization_Code = secretCfg.get('email', 'authcode')

    From_User = "EECS-Volunteer"
    From_Email = "eecsvolunteer@163.com"

    with open(os.path.join(Templates_Dir, "order.html"), "r", encoding="utf-8-sig") as fp:
        Order_Template = jinja_env.from_string(fp.read())


    @classmethod
    def _send(cls, from_user, to_user, subject, message):
        try:
            with smtplib.SMTP_SSL(cls.SMTP_Domain, cls.SMTP_Port) as server:
                server.login(cls.SMTP_Account, cls.Authorization_Code)
                server.sendmail(cls.SMTP_Account, [to_user,], message.as_string())
        except smtplib.SMTPException as err:
            raise err

    def send(self, order, subject="[电脑小队] 维修订单"):
        to_user = order["email"]
        message = MIMEText(self.Order_Template.render(order=order), 'html', 'utf-8')
        message['From'] = formataddr([self.From_User, self.From_Email])
        message['To'] = formataddr([to_user.split("@", 1)[0], to_user])
        message['Subject'] = Header(subject, "utf-8")
        self._send(self.From_User, to_user, subject, message)
