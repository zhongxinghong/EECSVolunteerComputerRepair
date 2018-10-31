#!/bin/sh

SHELL_FOLDER=$(dirname $(readlink -f "$0"))

cd $SHELL_FOLDER

uwsgi --stop uwsgi.pid
uwsgi --ini *uwsgi.ini