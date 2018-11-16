#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/views/admin.py


import os
import time
from functools import wraps
from flask import Blueprint, render_template, url_for, redirect, request,\
    make_response, jsonify, abort

from ..libs.utils import error_json
from ..libs.log import Logger
from ..libs.config import GeneralConfig, SecretConfig
from ..libs.db import OrderDB
from ..libs.safety import AdminToken
from ..libs.errors import QueryMissingError, AdminTokenVerifyError


admin = Blueprint('admin', __name__)

logger = Logger('views.admin')
generalCfg = GeneralConfig()
secretCfg = SecretConfig()
adminToken = AdminToken()

Active = generalCfg.getboolean('route', 'active')
Date = generalCfg.get('activity', 'date')

Admin_Account = secretCfg.get('admin', 'account')


def verify_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            token = request.args.get("token") or request.form.get("token") or None
            if token is None or adminToken.verify(Admin_Account, token) == False:
                raise AdminTokenVerifyError
        except Exception as err:
            # logger.exception(err)
            return jsonify(error_json(err))
        else:
            return func(*args, **kwargs)
    return wrapper



@admin.route('/', methods=["GET"])
def root():
    return redirect(url_for("admin.page_home"))


@admin.route('/page', methods=["GET"])
def page():
    return redirect(url_for("admin.page_home"))


@admin.route('/api', methods=["GET","POST"])
def api():
    return abort(403)


@admin.route('/page/home', methods=["GET"])
def page_home():
    return render_template("admin/home.html")


@admin.route('/page/queue', methods=["GET"])
def page_queue():
    try:
        with OrderDB() as orderDB:
            queue = orderDB.execute("""
                        SELECT q.queueID, q.status, o.type, o.model, o.description
                        FROM queue AS q
                        INNER JOIN orders AS o ON q.orderID == o.orderID
                        WHERE o.status == 0 AND o.day == ?
                        -- ORDER BY q.status, q.queueID
                    """, (Date,)).fetchall()

        status_map = lambda status: 0 if status in (0,1) else 1
        queue.sort(key=lambda item: (status_map(item["status"]), item["queueID"]))

        token = request.args.get("token")
        isAdmin = token is not None and adminToken.verify(Admin_Account, token) == True

        count_status = lambda queue, status: len([qInfo for qInfo in queue if qInfo["status"] == status])
        counts = [count_status(queue, status) for status in (0,1,2)]

        return render_template("admin/queue.html", queue=queue, counts=counts, isAdmin=isAdmin)

    except Exception as err:
        # logger.exception(err)
        return jsonify(error_json(err))


@admin.route('/api/change_status', methods=["POST"])
@verify_token
def api_change_status():
    try:
        try:
            queueID, status = map(request.form.__getitem__, ("queueID","status"))
            status = int(status)
        except KeyError:
            raise QueryMissingError

        orderDB = OrderDB()

        orderDB.execute("""
                    UPDATE queue
                    SET status = ?
                    WHERE queueID == ?
                """, (status, queueID))

        orderDB.commit()

    except Exception as err:
        # logger.exception(err)
        resp = jsonify(error_json(err))
    else:
        resp = jsonify(error_json())
    finally:
        if orderDB:
            orderDB.close()
        return resp