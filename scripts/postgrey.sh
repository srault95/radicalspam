#!/bin/bash

set -e

mkdir -p /var/lib/postgrey

chown postgrey.postgrey /var/lib/postgrey

exec /usr/sbin/postgrey -v --inet=${GREYLIST_HOST} --delay=60 --hostname=${MY_HOSTNAME} --retry-window=5 --auto-whitelist-clients=2
