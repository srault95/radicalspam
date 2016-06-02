#!/bin/bash

exec spamd -u debian-spamd -g debian-spamd --create-prefs --max-children 5 --helper-home-dir=/var/lib/amavis/.spamassassin -i 127.0.0.1:783 --virtual-config-dir=/var/lib/users/spamassassin/%d

