#!/bin/bash

[ -e /var/lib/clamav/main.cvd ] || freshclam -c 1

[ -e /var/lib/clamav/jurlbl.ndb ] || /usr/sbin/clamav-unofficial-sigs

exec freshclam -d --quiet -c 1 --enable-stats
