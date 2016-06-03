#!/bin/bash

cd /var/lib/mongodb

chown -R mongodb .

exec gosu mongodb mongod --dbpath /var/lib/mongodb --bind_ip 127.0.0.1 --nounixsocket --noauth --wiredTigerDirectoryForIndexes --directoryperdb --syslog 

