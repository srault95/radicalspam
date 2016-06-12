#!/bin/bash

set -e

echo "Start mongodb..."
supervisorctl start mongodb

echo "Start redis..."
supervisorctl start redis

echo "Start freshclam..."
supervisorctl start freshclam

echo "Start clamd..."
supervisorctl start clamd

echo "Start amavis..."
supervisorctl start amavis

echo "Start postgrey..."
supervisorctl start postgrey

echo "Start postfix..."
supervisorctl start postfix

echo "Start rs-admin..."
supervisorctl start rs-admin