#!/bin/bash

set -e

exec supervisord --nodaemon -c /etc/supervisor/supervisord.conf
