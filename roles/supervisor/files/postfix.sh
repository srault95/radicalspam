#!/bin/bash

cd /etc/postfix

/usr/sbin/postfix -c /etc/postfix check 1>&2

exec /usr/lib/postfix/sbin/master -c /etc/postfix -d
