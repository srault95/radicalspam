#!/bin/bash

[ -e /scripts ] || exit 1

declare -a SERVICES
SERVICES[0]="redis"
SERVICES[1]="mongodb"
SERVICES[2]="freshclam"
SERVICES[3]="clamd"
SERVICES[4]="amavis"
SERVICES[5]="postgrey"
SERVICES[6]="postfix"
SERVICES[7]="rs-admin"
SERVICES[8]="spamd"

chmod +x /scripts/*

for service in ${SERVICES[@]}; do
  mkdir -p /etc/service/${service}
  touch /etc/service/${service}/down
  cp -a /scripts/${service}.sh /etc/service/${service}/run
done

