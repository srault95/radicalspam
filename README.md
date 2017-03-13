# RadicalSpam 4

RadicalSpam est une passerelle anti-spam et anti-virus pour les moyennes et grandes entreprises.

Il doit être déclaré comme MX de vos domaines à protéger

RadicalSpam se place en frontal d'internet, dans une DMZ et devient le passage obligatoire de tous les messages échangés entre l'entreprise et internet.

Pour une protection efficace, vous devez définir au moins deux MX RadicalSpam mais si vous n'en déployez qu'un seul, ne définissez pas de MX secondaires non filtrés comme ceux fournis gratuitement par les fournisseurs d'accès internet.

## Configuration

RadicalSpam est pré-configuré pour la plupart des cas d'utilisations.

Les seuls éléments importants à personnaliser sont:

- Les noms de domaines
- L'adresse email du compte root 

### group_vars/all.yml

- Configurez dans ce fichier, ce qui est global à tous les serveurs déployés

### host_vars/localhost.yml

- Modifiez ou copiez ce fichier pour définir les variables spécifiques à vos serveurs.

### inventory.ini

- Placez vos groupes et serveurs de ce fichier (le même format que /etc/ansible/hosts)

### requirements.yml (optionnel)

- A utiliser si vous souhaitez charger des rôles Ansible (galaxy) supplémentaires 

### Variables d'environnements


Nom                 | Défaut | Description
------------------- | ------ | ------
AMAVIS_ENABLE       | true   | Activation/Désactivation de Amavisd-new
CLAMAV_ENABLE       | true   | Activation/Désactivation de Clamav
FAIL2BAN_ENABLE       | true   | Activation/Désactivation de Fail2ban
PDNS_ENABLE       | true   | Activation/Désactivation de PowerDNS
POSTFIX_ENABLE       | true   | Activation/Désactivation de Postfix
POSTFIX_FILTER_ENABLE       | true   | Activation/Désactivation du Filtre anti-spam/anti-virus pour Postfix
POSTGREY_ENABLE       | true   | Activation/Désactivation de Postgrey
SA_ENABLE       | true   | Activation/Désactivation de SpamAssassin
SUPERVISOR_ENABLE       | true   | Activation/Désactivation de Supervisor
SYSLOG_ENABLE       | true   | Activation/Désactivation de Syslog-ng

## Installation

### Ansible intégré dans une image Docker

A utiliser si vous souhaitez déployer RadicalSpam sur un ou plusieurs serveurs dédiés

	docker pull williamyeh/ansible:master-ubuntu16.04
	git clone https://github.com/srault95/radicalspam
	cd radicalspam
	docker run -it --rm -w /tmp \
		-v /etc/ansible:/etc/ansible -v $PWD:/tmp -v /root:/root \
		williamyeh/ansible:master-ubuntu16.04 \
		ansible-playbook /tmp/radicalspam.yml -vv
		
> Validé sur VPS SSD3 - https://www.ovh.com/fr/vps/vps-ssd.xml		

### Tout dans un container Docker

Cette version rassemble tous les éléments de RadicalSpam dans un seul container Docker.

> Tests réalisés avec Docker 1.12.5 sur Ubuntu 16.04 64bits

	git clone https://github.com/srault95/radicalspam
	cd radicalspam
	bash ./docker-run.sh full
	# OR
	chmod +x ./docker-run.sh
	./docker-run.sh full

### Directement par Ansible

> A utiliser par un expert ansible car la machine en cours sera entièrement reconfiguré.

> Attention à bien prendre Ansible en version 2.2 minimum

	apt-get install ansible
	OU
	pip install ansible
	
	git clone https://github.com/srault95/radicalspam
	cd radicalspam
	ansible-playbook radicalspam.yml
		
### Par Vagrant (non testé)

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

