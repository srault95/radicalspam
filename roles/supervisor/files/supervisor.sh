#!/bin/bash

set -e

/usr/bin/radicalspam-start

exec supervisord --nodaemon -c /etc/supervisor/supervisord.conf
