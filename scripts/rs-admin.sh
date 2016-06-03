#!/bin/bash

exec gunicorn -c /usr/local/etc/gunicorn_conf "rs_admin.wsgi:create_app()"
