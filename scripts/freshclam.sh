#!/bin/bash

set -e

[ -e /var/lib/clamav/main.cvd ] || freshclam -c 1

[ -e /var/lib/clamav/jurlbl.ndb ] || gosu clamav /usr/sbin/clamav-unofficial-sigs

exec freshclam -d --quiet -c 1 --enable-stats
