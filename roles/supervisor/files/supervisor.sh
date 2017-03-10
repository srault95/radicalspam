#!/bin/bash

set -e

/usr/local/bin/radicalspam-start

[-e /var/log/supervisor ] || mkdir -vp /var/log/supervisor

exec supervisord --nodaemon -c /etc/supervisor/supervisord.conf
