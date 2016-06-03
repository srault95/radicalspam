#!/bin/bash

# Delete all tmp files/directory - current day + 2
find /var/lib/amavis/tmp -mindepth 1 -maxdepth 1 -type d -mtime +2 -exec rm -rf {} \;
