#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/views/order.py


import time
import datetime
from functools import wraps
from flask import Blueprint, render_template, url_for, redirect, request,\
    make_response, jsonify, abort

from ..libs.compat import json, JSONDecodeError
from ..libs.log import Logger
from ..libs.config import GeneralConfig
from ..libs.db import OrderDB
from ..libs.email import OrderMailer
from ..libs.safety import OrderSign, RegisterToken, SerialNumSign,\
    OrderCookiesAESCipher, OrderRedirectAESCipher
from ..libs.utils import error_json
from ..libs.errors import FormKeysError, FormNullValueError, FormIllegalValueError,\
        QueryMissingError,\
    OrderChksnVerifyError, InvalidOrderInfoError, RegisterTokenVerifyError,\
        SerialNumSignVerifyError,\
    OrderRepeatError, OrderNotFoundError


order = Blueprint('order', __name__)

logger = Logger('views.order')
generalCfg = GeneralConfig()
orderSign = OrderSign()
registerToken = RegisterToken()
serialNumSign = SerialNumSign()
orderCookiesAESCipher = OrderCookiesAESCipher()
orderRedirectAESCipher = OrderRedirectAESCipher()
orderMailer = OrderMailer()

TypeMap = {
        "dust": "清灰",
        "hardware": "硬件",
        "software": "软件",
        "other": "其他",
    }


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


Active = generalCfg.getboolean('route', 'active')
Allow_Register = generalCfg.getboolean('route', 'allow_register')

Date = generalCfg.get('activity', 'date')
Site = generalCfg.get('activity', 'site')
Start = generalCfg.get('activity', 'start')
End = generalCfg.get('activity', 'end')
Span = generalCfg.getint('activity', 'span')
Next = generalCfg.get('activity', 'next')

Options = _get_appointment_options(Start, End, Span)


def verify_register_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            token = request.args.get("token") or request.form.get("token") or None
            if token is None or registerToken.verify(Date, token) == False:
                raise RegisterTokenVerifyError
        except Exception as err:
            # logger.exception(err)
            return jsonify(error_json(err))
        else:
            return func(*args, **kwargs)
    return wrapper


@order.route('/', methods=["GET"])
def root():
    return redirect(url_for("order.page_home"))


@order.route('/page', methods=["GET"])
def page():
    return redirect(url_for("order.page_home"))


@order.route('/api', methods=["GET","POST"])
def api():
    return abort(403)


@order.route('/page/inactive', methods=["GET"])
def page_inactive():
    if Active:
        if request.args.get("no_register") == "True":
            return render_template("order/inactive.html", no_register=True, date=Date, start=Start, end=End)
        else:
            abort(404) # 正常活动期间不能访问
    else:
        return render_template("order/inactive.html", next=Next)


@order.route('/page/home', methods=["GET"])
def page_home():
    if Active:
        # return render_template("order/home.html")
        return redirect(url_for('order.page_guide'))
    else:
        return redirect(url_for('order.page_inactive'))


@order.route("/page/guide", methods=["GET"])
def page_guide():
    if Active:
        return render_template("order/guide.html")
    else:
        return redirect(url_for('order.page_inactive'))


@order.route('/page/new', methods=["GET"])
def page_new():
    if Active:
        orderDB = OrderDB()

        appointments = dict.fromkeys(Options, 0)
        for name, count in orderDB.origin_cur.execute("""
                    SELECT appointment, count(appointment) FROM orders
                    WHERE day == ? AND status == 0
                    GROUP BY appointment
                """, (Date,)).fetchall():
            appointments[name] = count
        appointments = [dict(zip(["appointment", "sum"], item)) for item in sorted(appointments.items())]

        orderDB.close()
        return render_template("order/new.html", date=Date, site=Site, start=Start, end=End,\
                                     options=Options, appointments=appointments)
    else:
        return redirect(url_for('order.page_inactive'))


@order.route('/page/check', methods=["GET"])
def page_check():
    if Active:
        try:
            orderDB = OrderDB()
            orderCache = request.cookies.get("order")
            orderInfo = {}
            if orderCache is not None:
                try:
                    cookie = orderCookiesAESCipher.decrypt(orderCache)
                    orderInfo = orderDB.execute("""
                                SELECT * FROM orders
                                WHERE orderID == ? and status == 0
                            """, (cookie["orderID"],)).fetchone()
                except Exception as err:
                    # logger.exception(err)
                    #raise err
                    pass
        except Exception as err:
            # logger.exception(err)
            resp = jsonify(error_json(err))
        else:
            resp = make_response(render_template("order/check.html", order=orderInfo))
        finally:
            orderDB.close()
            return resp
    else:
        return redirect(url_for('order.page_inactive'))


@order.route("/page/register", methods=["GET"])
@verify_register_token
def page_register():
    if not Active:
        return redirect(url_for('order.page_inactive'))
    elif not Allow_Register:
        return redirect(url_for('order.page_inactive', no_register=True))
    else:
        return render_template("order/register.html")


@order.route("/page/result", methods=["GET"])
@verify_register_token
def page_result():
    if not Active:
        return redirect(url_for('order.page_inactive'))
    elif not Allow_Register:
        return redirect(url_for('order.page_inactive', no_register=True))
    else:
        try:
            try:
                queueID, sign = map(request.args.__getitem__, ("serial_num","sign"))
                queueID = int(queueID)
            except KeyError:
                raise QueryMissingError

            if serialNumSign.verify({"queueID": queueID, "date": Date}, sign) == False:
                raise SerialNumSignVerifyError

            orderDB = OrderDB()

            orderID = orderDB.single_cur.execute("""
                        SELECT orderID FROM queue
                        WHERE queueID == ?
                    """, (queueID,)).fetchone()

            orderInfo = orderDB.execute("""
                        SELECT * FROM orders
                        WHERE orderID == ?
                    """, (orderID,)).fetchone()

            interval = orderDB.single_cur.execute("""
                        SELECT count(*)
                        FROM queue AS q
                        INNER JOIN orders AS o ON q.orderID == o.orderID
                        WHERE q.status IN (0,1)
                        AND o.day == ?
                        AND q.queueID != ? -- 去掉自己
                    """, (Date, queueID)).fetchone()

            orderDB.close()

            return render_template("order/result.html", queueID=queueID, interval=interval, order=orderInfo)

        except Exception as err:
            return jsonify(error_json(err))


@order.route("/page/order", methods=["GET"])
def page_order():
    if Active:
        try:
            try:
                action, orderInfo = map(request.args.__getitem__, ("action","order"))
            except KeyError:
                raise QueryMissingError
            try:
                orderInfo = orderRedirectAESCipher.decrypt(orderInfo)
            except Exception as err:
                # logger.exception(err)
                raise InvalidOrderInfoError
        except Exception as err:
            return jsonify(error_json(err))
        else:
            return render_template("order/order.html", action=action, order=orderInfo)
    else:
        return redirect(url_for('order.page_inactive'))


@order.route('/api/create', methods=["POST"])
def api_create():
    try:
        orderInfo = dict(request.form.items())

        if orderInfo.keys() != {"email","wechat","model","type","description","appointment"}:
            raise FormKeysError

        for k, v in orderInfo.items():
            orderInfo[k] = v = v.strip() # strip
            if k in ("email","wechat","type","appointment") and v == "": # 必填项为空
                raise FormNullValueError
            if k == "type":
                if v not in TypeMap:
                    raise FormIllegalValueError
                else:
                    orderInfo[k] = TypeMap[v]
            if k == "appointment" and v not in Options:
                raise FormIllegalValueError

        orderDB = OrderDB()

        if orderDB.execute("""
                    SELECT * FROM orders
                    WHERE email == ? AND day == ? AND status == 0
                """, (orderInfo["email"], Date)).fetchone():
            raise OrderRepeatError # 单个邮箱单次活动只能创建一个订单

        orderInfo.update(day=Date, site=Site, status=0, create_time=int(time.time()))
        cur = orderDB.insert_one("orders", orderInfo)
        orderID = cur.lastrowid

        orderInfo.update(orderID=orderID)
        orderInfo.update(chksn=orderSign.create(orderInfo))

        orderMailer.send(orderInfo)

        respJson = {"redirect": url_for("order.page_order", action="create", order=orderRedirectAESCipher.encrypt(orderInfo))}
        respJson.update(error_json())
        resp = jsonify(respJson)

        resp.set_cookie("order", orderCookiesAESCipher.encrypt(orderInfo), expires=int(time.time() + 14*24*60*60)) # 两周过期

    except Exception as err:
        # logger.exception(err)
        resp = jsonify(error_json(err))
    finally:
        orderDB.close()
        return resp


@order.route('/api/check', methods=["POST"])
def api_check():
    try:
        email = request.form.get("email")
        if email is None:
            raise FormKeysError
        elif email == "":
            raise FormNullValueError

        orderDB = OrderDB()

        orderInfos = orderDB.execute("""
                        SELECT * FROM orders
                        WHERE email == ? AND day == ? AND status == 0
                    """, (email, Date)).fetchall()

        if orderInfos == []:
            raise OrderNotFoundError
        else:
            orderInfos.sort(key=lambda item: (item["orderID"], -item["status"]), reverse=True) # id 降序 status 升顺序
            orderAES = orderRedirectAESCipher.encrypt(orderInfos[0])
            if request.args.get("action") == "register":
                token = request.args.get("token","")
                respJson = {"redirect": url_for('order.page_order', action="register", token=token, order=orderAES)}
            else:
                respJson = {"redirect": url_for('order.page_order', action="check", order=orderAES)}


    except Exception as err:
        # logger.exception(err)
        resp = jsonify(error_json(err))
    else:
        respJson.update(error_json())
        resp = jsonify(respJson)
    finally:
        orderDB.close()
        return resp


@order.route('/api/withdraw', methods=["POST"])
def api_withdraw():
    try:
        email, chksn = map(request.form.get, ("email", "chksn"))

        if email is None or chksn is None:
            raise FormKeysError

        email, chksn = email.strip(), chksn.strip()

        orderDB = OrderDB()

        orderInfo = orderDB.execute("""
                    SELECT * FROM orders
                    WHERE email == ? AND day == ? AND status == 0
                """, (email, Date)).fetchone()

        if not orderInfo:
            raise OrderNotFoundError
        elif not orderSign.verify(orderInfo, chksn):
            raise OrderChksnVerifyError
        else:
            orderDB.execute(""" UPDATE orders
                                SET status = 1
                                WHERE orderID == ?
                        """, (orderInfo["orderID"],))
            orderDB.commit()
            orderInfo.update(status = 1)

            respJson = {"redirect": url_for('order.page_order', action="withdraw", order=orderRedirectAESCipher.encrypt(orderInfo))}

    except Exception as err:
        # logger.exception(err)
        resp = jsonify(error_json(err))
    else:
        respJson.update(error_json())
        resp = jsonify(respJson)
    finally:
        orderDB.close()
        return resp


@order.route("/api/register", methods=["POST"])
@verify_register_token
def api_register():
    try:
        try:
            orderInfo = request.form.get("order")
            orderInfo = orderRedirectAESCipher.decrypt(orderInfo)
            orderID = orderInfo.get("orderID")
        except Exception as err:
            # logger.exception(err)
            raise InvalidOrderInfoError

        orderDB = OrderDB()

        queueID = orderDB.single_cur.execute("""
                    SELECT q.queueID
                    FROM queue AS q
                    INNER JOIN orders AS o ON q.orderID == o.orderID
                    WHERE q.orderID == ?
                """, (orderID,)).fetchone()

        if queueID is None:
            queueInfo = {k:v for k,v in orderInfo.items() if k in ("orderID",)}
            queueInfo.update(status=0, create_time=int(time.time()))

            cur = orderDB.insert_one("queue", queueInfo)
            queueID = cur.lastrowid

        respJson = {"redirect": url_for("order.page_result", serial_num=queueID, token=request.args.get("token"),\
                                            sign=serialNumSign.create({"queueID": queueID, "date": Date}))}

    except Exception as err:
        # logger.exception(err)
        resp = jsonify(error_json(err))
    else:
        respJson.update(error_json())
        resp = jsonify(respJson)
    finally:
        orderDB.close()
        return resp
