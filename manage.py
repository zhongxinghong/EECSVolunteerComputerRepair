#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# filename: manage.py


from app import create_app
from flask_script import Manager, Shell


if __name__ == '__main__':
    app = create_app()
    manage = Manager(app)
    manage.add_command("shell", Shell(make_context=lambda: dict(app=app)))
    manage.run()
else:
    app = create_app("release")