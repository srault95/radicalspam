#!/bin/bash

set -e

[ -e /var/run/clamav ] || mkdir -vp /var/run/clamav
chown clamav.clamav -R /var/run/clamav
chown clamav.clamav -R /var/lib/clamav

exec clamd
