#!/bin/bash

set -e

mkdir -vp /var/lib/amavis/{tmp,db,var,quarantine,policies}
mkdir -vp /var/lib/amavis/quarantine/{virus,banned,spam,archives,clean}
touch /var/lib/amavis/local_domains
touch /var/lib/amavis/mynetworks
touch /var/lib/amavis/whitelist_sender
touch /var/lib/amavis/blacklist_sender
touch /var/lib/amavis/virus_lovers
touch /var/lib/amavis/spam_lovers
touch /var/lib/amavis/banned_lovers
touch /var/lib/amavis/debug_senders
touch /var/lib/amavis/inet_socket_port
grep 10024 /var/lib/amavis/inet_socket_port || echo "10024" >> /var/lib/amavis/inet_socket_port

grep ${MY_DOMAIN} /var/lib/amavis/local_domains 2>/dev/null 1>&2 || echo "${MY_DOMAIN}" >> /var/lib/amavis/local_domains

if [ ! -e /var/lib/amavis/.razor/identity ]; then
	gosu amavis bash -c "razor-admin -create"
fi	

COUNT=$(find /var/lib/spamassassin -type f -name "*.cf" | wc -l)
if [ $COUNT -lt 1 ]; then
	gosu debian-spamd bash -c "sa-update --channelfile /etc/spamassassin/channels.txt --nogpg --allowplugins"
fi

[ -e /var/lib/users/spamassassin ] || mkdir -p /var/lib/users/spamassassin
chown -R debian-spamd.debian-spamd /var/lib/users/spamassassin 

chown -R amavis:amavis /var/lib/amavis

exec /usr/local/bin/amavisd-new -c /etc/amavis/amavisd.conf -p 127.0.0.1:10024 -m ${AMAVIS_MAX_SERVERS} foreground
 