#!/bin/bash

mkdir /var/run/redis

chown redis /var/run/redis

cd /var/lib/redis

chown -R redis .

exec gosu redis redis-server /etc/redis/redis.conf

