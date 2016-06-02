#!/bin/sh
exec 1>&2

mkdir -p /etc/postfix/local

postconf -e 'smtpd_banner=secure smtp'
postconf -e "myhostname=${MY_HOSTNAME}"

#TODO: 1,5 * message_size_limit
#postconf -e 'queue_minfree = 107374182400'

postconf -e "append_at_myorigin = no"
postconf -e "transport_maps = hash:/etc/postfix/local/transport"
postconf -e "relay_domains = \$mydestination, hash:/etc/postfix/local/relays"
postconf -e "relay_recipient_maps = hash:/etc/postfix/local/directory"
postconf -e "mynetworks=hash:/etc/postfix/local/mynetworks"

#postconf -e "disable_vrfy_command=yes"
#postconf -e "disable_verp_bounces = no"

if [ -n "${MESSAGE_SIZE_LIMIT}" ]; then
	postconf -e "message_size_limit = ${MESSAGE_SIZE_LIMIT}"
fi

if [ -n "${BIND_SMTP_TRANSPORT}" ]; then
	postconf -e "smtp_bind_address = ${BIND_SMTP_TRANSPORT}"
fi

if [ -n "${RELAYHOST}" ]; then
	postconf -e "relayhost = ${RELAYHOST}" 
fi

#postconf -e 'inet_interfaces = 127.0.0.1'
#mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128

#postconf -e "smtpd_client_restrictions = permit_mynetworks, check_client_access hash:$CONFIG/local-whitelist-clients, sleep 2, check_client_access hash:$CONFIG/local-blacklist-clients, reject_rbl_client zen.spamhaus.org"
#postconf -e "smtpd_helo_restrictions = check_helo_access hash:$CONFIG/local-exceptions-helo, check_helo_access hash:$CONFIG/local-blacklist-helo, check_helo_access hash:$CONFIG/local-spoofing"
#postconf -e "smtpd_sender_restrictions = permit_mynetworks, check_sender_access hash:$CONFIG/local-exceptions-senders, reject_non_fqdn_sender, check_sender_access hash:$CONFIG/local-spoofing, check_sender_access hash:$CONFIG/local-blacklist-senders"
#postconf -e "smtpd_recipient_restrictions = check_recipient_access hash:$CONFIG/local-blacklist-recipients, reject_non_fqdn_recipient, reject_unauth_destination, check_recipient_access hash:$CONFIG/local-verify-recipients, $ACTIVE_POSTGREY reject_unlisted_recipient, check_recipient_access hash:$CONFIG/local-filters"

#smtpd_client_restrictions =
#smtpd_etrn_restrictions =
#smtpd_helo_restrictions =
#smtpd_recipient_restrictions = 
#smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination
#smtpd_sender_restrictions =

grep 'smtp-amavis' /etc/postfix/master.cf || cat /etc/postfix/master-amavis.tmpl >> /etc/postfix/master.cf

if [ -e /etc/postfix/local/filters ]; then
	postconf -e "smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination check_recipient_access hash:/etc/postfix/local/filters"
	postconf -e "content_filter="
	postmap /etc/postfix/local/filters
else
	postconf -e "content_filter = smtp-amavis:[127.0.0.1]:10024"
fi

[ -e /etc/postfix/local/relays ] || touch /etc/postfix/local/relays
[ -e /etc/postfix/local/directory ] || touch /etc/postfix/local/directory
[ -e /etc/postfix/local/transport ] || touch /etc/postfix/local/transport
[ -e /etc/postfix/local/mynetworks ] || touch /etc/postfix/local/mynetworks

grep '127.0.0.1' /etc/postfix/local/mynetworks || echo -e "127.0.0.1\t#loopback" >> /etc/postfix/local/mynetworks 

postmap /etc/postfix/local/relays
postmap /etc/postfix/local/directory
postmap /etc/postfix/local/transport
postmap /etc/postfix/local/mynetworks

/usr/sbin/postfix check 1>&2 || exit 1

exec /usr/lib/postfix/sbin/master -c /etc/postfix -d

