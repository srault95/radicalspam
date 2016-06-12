#!/bin/bash

set -e

echo "Start mongodb..."
supervisorctl start mongodb

echo "Start redis..."
supervisorctl start redis

echo "Start rs-admin..."
supervisorctl start rs-admin