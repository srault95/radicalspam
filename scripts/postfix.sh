#!/bin/bash
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

grep 'smtp-amavis' /etc/postfix/master.cf || cat /etc/postfix/master-amavis.tmpl >> /etc/postfix/master.cf

if [ -z "${GREYLIST_HOST}" ]; then
	sv down /etc/service/postgrey
	ACTIVE_POSTGREY=""
else
	ACTIVE_POSTGREY="check_policy_service inet:${GREYLIST_HOST},"
fi

if [ -e /etc/postfix/local/filters ]; then
	postconf -e "smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, ${ACTIVE_POSTGREY} defer_unauth_destination check_recipient_access hash:/etc/postfix/local/filters"
	postconf -e "content_filter="
	postmap /etc/postfix/local/filters
else
	postconf -e "content_filter = smtp-amavis:[127.0.0.1]:10024"
	postconf -e "smtpd_relay_restrictions = permit_mynetworks, permit_sasl_authenticated, ${ACTIVE_POSTGREY} defer_unauth_destination"
fi

[ -e /etc/postfix/local/relays ] || touch /etc/postfix/local/relays
[ -e /etc/postfix/local/directory ] || touch /etc/postfix/local/directory
[ -e /etc/postfix/local/transport ] || touch /etc/postfix/local/transport
[ -e /etc/postfix/local/mynetworks ] || touch /etc/postfix/local/mynetworks

grep ${MY_NETWORK} /etc/postfix/local/mynetworks 2>/dev/null 1>&2 || echo -e "${MY_NETWORK}\t#loopback" >> /etc/postfix/local/mynetworks
grep ${MY_DOMAIN} /etc/postfix/local/relays 2>/dev/null 1>&2 || echo -e "${MY_DOMAIN}\tOK" >> /etc/postfix/local/relays  
grep ${MY_DOMAIN} /etc/postfix/local/directory 2>/dev/null 1>&2 || echo -e "@${MY_DOMAIN}\tOK" >> /etc/postfix/local/directory

#if [ -n "${MY_TRANSPORT}" ]; then
#	grep ${MY_TRANSPORT} /etc/postfix/local/transport 2>/dev/null 1>&2 || echo -e "${MY_DOMAIN}\t${MY_TRANSPORT}" >> /etc/postfix/local/transport
#fi

grep ${MY_ROOT_EMAIL} /etc/aliases 2>/dev/null 1>&2
RET=$?
if [ "$RET" != "0" ]; then
	echo "postmaster: root"> /etc/aliases 
	echo "root: ${MY_ROOT_EMAIL}" >> /etc/aliases 
	newaliases
fi 

postmap /etc/postfix/local/relays
postmap /etc/postfix/local/directory
postmap /etc/postfix/local/transport
postmap /etc/postfix/local/mynetworks

cd /etc/postfix

/usr/sbin/postfix check 1>&2 || exit 1

exec /usr/lib/postfix/sbin/master -c /etc/postfix -d

