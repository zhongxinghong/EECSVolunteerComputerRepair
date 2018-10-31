#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/__init__.py


from flask import Flask
from setting.config import Config_Map


def create_app(key="default"):

    app = Flask(__name__)

    app.config.from_object(Config_Map[key])
    Config_Map[key].init_app(app)


    from .views import base, order, admin

    app.register_blueprint(base)
    app.register_blueprint(order, url_prefix="/order")
    app.register_blueprint(admin, url_prefix="/admin")

    return app