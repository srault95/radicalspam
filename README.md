# RadicalSpam 4

## Configuration

- La configuration pour tous les serveurs se trouve dans `group_vars/all.yml`

- Pour chaque serveur, vous devez créer un fichier dans `host_vars/MON_SERVER.yml`

- Le fichier /etc/ansible/hosts doit contenir la liste des serveurs à déployer

## Installation

### Directement par Ansible

	apt-get install ansible
	OU
	pip install ansible
	
	git clone https://github.com/srault95/radicalspam
	cd radicalspam
	ansible-playbook radicalspam.yml

### Ansible intégré dans une image Docker

	docker pull williamyeh/ansible:alpine3
	git clone https://github.com/srault95/radicalspam
	cd radicalspam
	docker run -it --rm -w /tmp \
		-v /etc/ansible:/etc/ansible -v $PWD:/tmp -v /root:/root \
		williamyeh/ansible:alpine3 \
		ansible-playbook /tmp/radicalspam.yml -l 'rs1' -vv

### Tout dans un container Docker


	chmod +x docker-run.sh
	./docker-run.sh
	
	# OU

	docker build -t radicalspam .
	docker run -d \
	   --name rs4 \
	   --net host --pid=host \
	   -v /etc/localtime:/etc/localtime \
	   -v $PWD/store/amavis/config:/var/lib/amavis/config \
	   -v $PWD/store/amavis/virusmails:/var/lib/amavis/virusmails \
	   -v $PWD/store/postfix/local:/etc/postfix/local \
	   -v $PWD/store/postfix/ssl:/etc/postfix/ssl \
	   -v $PWD/store/postfix/spool:/var/spool/postfix \
	   -v $PWD/store/etc/postgrey/etc:/etc/postgrey \
	   -v $PWD/store/etc/postgrey/data:/var/lib/postgrey \
	   -v $PWD/store/clamav:/var/lib/clamav \
	   -v $PWD/store/spamassassin/users:/var/lib/users/spamassassin \
	   radicalspam
		
### Par Vagrant

	git clone https://github.com/srault95/radicalspam
	cd radicalspam
	vagrant up
	
## Distributions Linux testés

- Ubuntu 16.04 (Xenial)	

## Fonctionnalités

- Serveur SMTP Postfix 3.1.0
- Anti-virus Clamav 0.99.2 avec des signatures supplémentaires 
- Anti-spam Spamassassin 3.4.1 + Razor/Pyzor
- Anti-spam Amavisd-new 2.10
- Serveur Syslog-ng
- Sécurité Fail2ban

## TODO

- Tests et adaptations Debian, Autres Ubuntu, Redhat, Alpine
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

