#!/bin/bash

set -e

exec rs-mta-gevent -C /etc/rs-mta/config.yml
