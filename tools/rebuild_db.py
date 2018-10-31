#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/tools/rebuild_db.py


import time
import datetime
import string

import sys
sys.path.append("../")

from app.libs.compat import random
from app.libs.db import OrderDB
from app.libs.config import GeneralConfig


def _get_appointment_options(start, end, span):
    """ 生成预约时段选项 """
    pClock = lambda clockStr: datetime.datetime.strptime(clockStr, "%H:%M")
    fClock = lambda clockObj: datetime.datetime.strftime(clockObj, "%H:%M")

    start, end = map(pClock, (start, end))
    span = datetime.timedelta(minutes=span)

    options = []
    now = start
    while True:
        if now + span < end:
            options.append("{}-{}".format(fClock(now), fClock(now + span)))
            now += span
        else:
            options.append("{}-{}".format(fClock(now), fClock(end)))
            break

    return options


generalCfg = GeneralConfig()
Date = generalCfg.get('activity', 'date')
Site = generalCfg.get('activity', 'site')
Start = generalCfg.get('activity', 'start')
End = generalCfg.get('activity', 'end')
Span = generalCfg.getint('activity', 'span')

Options = _get_appointment_options(Start, End, Span)

TypeMap = {
        "dust": "清灰",
        "hardware": "硬件",
        "software": "软件",
        "other": "其他",
    }


def rebuild_table_orders():
    with OrderDB() as db:
        db.create_table("orders", rebuild=True)


def rebuild_table_queue():
    with OrderDB() as db:
        db.create_table("queue", rebuild=True)


def random_insert_to_orders(count):
    with OrderDB() as db:
        db.insert_many("orders", [{
                "status": random.choice([0,1]),
                "email": "1300012{}@pku.edu.cn".format(str(i).zfill(3)),
                "wechat": "".join(random.sample(string.ascii_letters, random.randint(9,13))),
                "type": TypeMap[random.choice(["dust","software","hardware","other"])],
                "model": "ThinkPad X2{}0".format(random.randint(2,6)),
                "description": "".join(random.sample(string.ascii_letters, random.randint(0,50))),
                "day": Date,
                "site": Site,
                "appointment": random.choices(Options, list(range(len(Options), 0, -1)))[0],
                "create_time": int(time.time()) + i*2,
            } for i in range(count)])


def random_insert_to_queue(count):
    with OrderDB() as db:
        orders = db.single_cur.execute("SELECT orderID FROM orders WHERE status == 0").fetchall()
        db.insert_many("queue", [{
                "orderID": orderID,
                "status": random.choice([0,1,2]),
                "create_time": int(time.time()) + i*2,
            } for (i, orderID) in enumerate(random.sample(orders, count)) ])


if __name__ == '__main__':
    rebuild_table_orders()
    # random_insert_to_orders(200)
    rebuild_table_queue()
    # random_insert_to_queue(50)