# RadicalSpam

## BUGS

## TODO

- Testabilité:

	example.net
	root@example.net

- utiliser inventaire pour définir ressources nécessaires    	

   - Il faut pouvoir mettre à jour la PIL complète et lancer des tests pertinents
      - Mails entrants/sortants / accept/reject : vérification dans DB
      - Recherche DNS
      - Filter SA/CLAMD
      - Livraison finale / Turing / Quarantaine / Notification (besoin serveur test pop/imap)


- utiliser psutil pour surveiller process
- placer tout dans supervisor pour console + xmlrpc ?
- dns
- scripts nagios ?
- iso fonctionnalités sauf lan/wan ?
- récupération config existante
	- role migrate
- script de gestion RS construit à la demande selon config ?	
- gestion 2 interface: lan/wan ?
- ufw
- fail2ban config
- ln -sf /usr/local/etc/radicalspam.cron /etc/cron.d/radicalspam
- migration bayes
- ssl postfix

- voir:

	Mar  8 12:00:23 rs1 postfix[12101]: To disable backwards compatibility use "postconf compatibility_level=2" and "postfix reload"

	Mar  8 13:58:43 rs1 amavis[18108]: OS_Fingerprint code  NOT loaded
	Mar  8 12:00:16 rs1 amavis[11751]: DKIM code            loaded
	Mar  8 12:00:16 rs1 amavis[11751]: Tools code           NOT loaded
	Mar  8 12:00:16 rs1 amavis[11751]: No $altermime,         not using it
	Mar  8 12:00:16 rs1 amavis[11751]: No decoder for       .7z


## Installation with Ansible

	docker run -it --rm -v /etc/ansible:/etc/ansible -w /tmp -v $PWD:/tmp -v /root:/root williamyeh/ansible:alpine3 ansible-playbook /tmp/site.yml --syntax-check
	
	docker run -it --rm -v /etc/ansible:/etc/ansible -w /tmp -v $PWD:/tmp -v /root:/root williamyeh/ansible:alpine3 ansible-playbook /tmp/site.yml -l 'rs1' -vv
	
	
	

## Installation with Docker

	docker build -t radicalspam .
	
	docker run -d --name radicalspam -p 25:25 -p 465:465 radicalspam 
	
	docker run -d \
	   --net host --name ${CT_NAME} \
	   --pid=host \
	   --env-file=./docker_environ \
	   -v /etc/localtime:/etc/localtime \
	   -v $PWD/store/amavis:/var/lib/amavis \
	   -v $PWD/store/clamav:/var/lib/clamav \
	   -v $PWD/store/spamassassin/users:/var/lib/users/spamassassin \
	   -v $PWD/store/postfix/config:/etc/postfix/local \
	   -v $PWD/store/postfix/spool:/var/spool/postfix \
	   -v $PWD/store/redis/data:/var/lib/redis \
	   -v $PWD/store/postgrey/db:/var/lib/postgrey \
	   -v $PWD/store/mongodb/data:/var/lib/mongodb \
	   ${DOCKER_IMAGE}
		

## Installation with Vagrant

	vagrant up
	
## Tested Linux distributions

- Ubuntu 16.04 (Xenial)	

## Features

- SMTP Server Postfix 3.1.0
- Clamav 0.99.2 and clamav-unofficial-sigs 
- Amavisd-new 2.10
- Spamassassin 3.4.1
- Razor
- Pyzor
- Python 3.5.2
- Syslog-ng
- Fail2ban

## Features Added

- MongoDB Server 3.2.6
- Record and search logs in MongoDB
- Redis Server 2.3.0

- mongrey ?
- SSL letsencrypt
- ufw
- altermime
- sa bayes redis
- amavis redis ?
- collectd
- rbl server
- opendkim
- opendmarc
- elk
- nagios

## Ubuntu 16.04

	cd /home/tmp
	mkdir xenial && cd xenial
	docker run -it --rm -v $PWD:/datas ubuntu:xenial
	
	#?opendkim
	#?
	
		
	
      
## Alpine

## Debian 8      

## Fedora ?

