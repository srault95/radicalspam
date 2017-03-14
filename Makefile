NAME=rs/radicalspam:testing
VERSION=4.0.0
MAILHOG_IP=

all: build-no-cache fake run fixtures tests clean

build-no-cache:	
	docker build --pull --force-rm --no-cache -t $(NAME) .
	
build:
	docker build -t $(NAME) \
		--build-arg POSTFIX_FILTER_ENABLE=false \
		--build-arg POSTGREY_ENABLE=false \
		--build-arg AMAVIS_ENABLE=false \
		--build-arg CLAMAV_ENABLE=false \
		--build-arg SA_ENABLE=false .

fake:
	mkdir -vp /mailhog
	docker run -d --name mailhog-testing \
		-p 1025:1025 \
		-p 8025:8025 \
		-v /mailhog/mail:/var/lib/mail \
		srault95/docker-mailhog
	MAILHOG_IP=$(docker inspect --format='{{.NetworkSettings.IPAddress}}' mailhog-testing)
	
	#TODO: creer un client smtp et utiliser son ip dans mynetworks
	
run:
	docker run -d --name mail \
	   --dns 127.0.0.1 \
	   -h mail.my-domain.com \
	   -t \
	   --cap-add NET_ADMIN \
	   -v "`pwd`/test":/tmp/docker-mailserver-test \
	   -v /etc/localtime:/etc/localtime \
	   $(NAME)
	
	sleep 15
	
pre_test:
	docker exec mail postconf -e 'transport_maps='	
	docker exec mail postconf -e 'smtpd_client_restrictions=permit_mynetworks,check_client_access hash:/etc/postfix/local/whitelist-clients, check_client_access hash:/etc/postfix/local/blacklist-clients'	
	docker exec mail postconf -e 'smtpd_relay_restrictions=check_recipient_access hash:/etc/postfix/local/blacklist-recipients, reject_non_fqdn_recipient, reject_unauth_destination'	
	docker exec mail postconf -e 'transport_maps='	
	
fixtures:
	docker exec mail /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/amavis-spam.txt"
	
	docker exec mail /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/amavis-virus.txt"
	
	#docker exec mail /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/existing-alias-external.txt"
	#docker exec mail /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/existing-alias-local.txt"
	#docker exec mail /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/existing-alias-recipient-delimiter.txt"
	#docker exec mail /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/existing-user.txt"
	#docker exec mail /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/existing-user-and-cc-local-alias.txt"
	#docker exec mail /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/existing-regexp-alias-external.txt"
	#docker exec mail /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/existing-regexp-alias-local.txt"
	
	#docker exec mail /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/existing-catchall-local.txt"
	
	#docker exec mail /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/sieve-spam-folder.txt"
	
	#docker exec mail /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/non-existing-user.txt"
	
	#docker exec mail_disabled_clamav_spamassassin /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/existing-user.txt"
	
	# postfix virtual transport lmtp
	#docker exec mail_lmtp_ip /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/existing-user.txt"

	#docker exec mail_override_hostname /bin/sh -c "nc 0.0.0.0 25 < /tmp/docker-mailserver-test/email-templates/existing-user.txt"
	# Wait for mails to be analyzed
	sleep 20
		

tests:
	./test/bats/bin/bats test/tests.bats
	
clean:
	-docker rm -f \
		mailhog-testing \
		mail
		
		