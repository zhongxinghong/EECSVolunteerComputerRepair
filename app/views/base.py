#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: app/views/base.py


from flask import Blueprint, redirect, url_for

base = Blueprint('base', __name__)


@base.route('/', methods=["GET"])
def root():
    return "Hello World !"

@base.route('/favicon.ico', methods=["GET"])
def favicon():
    return redirect(url_for('static', filename="assets/favicon.ico"))

@base.route('/robots.txt')
def robots():
    return redirect(url_for('static', filename="robots.txt"))