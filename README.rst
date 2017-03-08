************
Radical-Spam
************

**Serveur de filtrage SMTP - Anti-Virus et Anti-Spam intégré**

|Build Status| |Build Doc| |Gitter|

**Fonctionnalités:**

* Distribution Linux: Ubuntu 16.04 (Xenial)
* Serveur SMTP : Postfix 3.1.0
* Serveur de filtrage : Amavisd-new 2.11.0
* Anti-Spam : SpamAssassin 3.4.1
* Anti-Virus : Clamav 0.99
* Serveur NoSQL MongoDB 3.2.6
* Serveur de cache : Redis Server 2.3.0
* Razor
* Pyzor
* Web UI
* Serveur Syslog
* Enregistrement des logs dans MongoDB
* Mise à jour automatique des signatures virales et des règles anti-spam

======
Requis
======

* 10 Go minimum (selon la durée de stockage) 
* 4 Go RAM minimum (8 Go conseillé)
* Serveur Docker 1.10+ (testé avec docker 1.10.3 sur Ubuntu 14.04 OVH)
* Accès root

================
Démarrage rapide
================

*RadicalSpam sera installé dans /home/rs4 mais vous pouvez choisir un autre emplacement*

**Télécharger le projet à partir de Github:**

*Adaptez le chemin selon votre serveur*

.. code-block:: bash
    
    $ git clone https://github.com/srault95/radicalspam.git /home/rs4
    
    $ cd /home/rs4
    
**Editez le fichier ./docker_environ:**

*Personnalisez la configuration selon votre architecture et vos besoins*

.. code-block:: bash    

    $ vi docker_environ
    
**Générer l'image et lancez RadicalSpam**

.. code-block:: bash
    
    $ sh ./docker-run.sh

**Affichez les logs et vérifier les services:**

*Il faut quelques minutes pour le premier démarrage et il est normal d'y trouver quelques errors et warning*

.. code-block:: bash    

    $ docker logs radicalspam
    
    $ docker exec -it radicalspam bash -c "/usr/bin/sv status /etc/service/*"
    
    run: /etc/service/amavis: (pid 29363) 1368s
    run: /etc/service/clamd: (pid 29361) 1368s
    run: /etc/service/cron: (pid 29369) 1368s
    run: /etc/service/freshclam: (pid 29359) 1368s
    run: /etc/service/mongodb: (pid 29362) 1368s
    run: /etc/service/postfix: (pid 27537) 1s
    run: /etc/service/postgrey: (pid 29374) 1368s
    run: /etc/service/redis: (pid 29367) 1368s
    run: /etc/service/rs-admin: (pid 27566) 0s
    run: /etc/service/spamd: (pid 29375) 1368s
    down: /etc/service/sshd: 1368s
    run: /etc/service/syslog-forwarder: (pid 29372) 1368s
    run: /etc/service/syslog-ng: (pid 29364) 1368s
    
    
**Ouvrez l'interface d'administration:**

.. code-block:: 

    http://VOTRE_IP_PUBLIQUE:8080
    
    Le login et mot de passe se trouve dans le fichier ./docker_environ    
    
=====================
Tests de Radical-Spam
=====================

- Python et swaks sont requis
- Python peut être appellé directement à partir d'un contenair docker

Utilisation d'un faux serveur SMTP (mailhog)
--------------------------------------------

Pour éviter pendant les tests que des messages soient envoyés par erreur,
il est préférabe d'utiliser un faux serveur SMTP qui recevra toutes les 
sorties de messages.

Mailhog fournit en plus du service SMTP, une interface web pour vérifier les 
messages reçus.

Vous pouvez également visualisez les messages dans le répertoire /var/lib/mailhog 

**L'application sera accessible à l'adresse http://VOTRE_IP:8025** 

.. code-block:: bash

    $ docker build -t rs/mailhog https://github.com/srault95/docker-mailhog.git
    
    $ docker run -d --name mailhog \
       -e MAILHOG_USERNAME=admin -e MAILHOG_PASSWORD=admin \ 
       -p 127.0.0.1:2500:1025 -p 8025:8025 \
       -v /var/lib/mailhog:/var/lib/mail rs/mailhog

Les tests sont basés sur la configuration suivante
--------------------------------------------------

*Adaptez les valeurs à votre configuration !*

.. code-block:: bash

    # fichier docker_environ
    MY_NETWORK=127.0.0.1
    MY_HOSTNAME=mx-demo.radical-spam.com
    MY_DOMAIN=radical-spam.com
    MY_ROOT_EMAIL=root@radical-spam.com

Génération des faux mails
-------------------------

.. code-block:: bash

    $ echo 'Mail test normal' >/tmp/mail-normal.txt
    $ echo 'xxx' >/tmp/mail-banned.pif
    $ echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' >/tmp/mail-virus-eicar.txt
    $ echo 'XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X' >/tmp/mail-spam-gtube.txt

Préparation de Postfix et installation de swaks
-----------------------------------------------

.. code-block:: bash

    # ip:port du faux serveur smtp (mailhog)
    $ docker exec -it radicalspam bash -c "postconf -e 'relayhost=[127.0.0.1]:2500'"
    $ docker exec -it radicalspam bash -c "postconf -e 'smtpd_authorized_xclient_hosts=127.0.0.1'"
    $ docker exec -it radicalspam bash -c "sv hup /etc/service/postfix"
    $ apt-get install swaks

Tests de messages entrants (en provenance d'internet)
-----------------------------------------------------

:test: **Mail entrant - Normal**
:status: Mail envoyé à myuser@radical-spam.com
:notification: Aucune
:quarantaine: Aucune

.. code-block:: bash

    swaks --h-Subject "test mail entrant - NORMAL" \
       -s 127.0.0.1:25 --xclient 'ADDR=1.1.1.1' \ 
       --from sender@example.org --to myuser@radical-spam.com \
       --attach-type text/html --attach /tmp/mail-normal.txt

--------

:test: **Mail entrant - Contenant un virus**
:status: Mail non envoyé à myuser@radical-spam.com
:notification: Notifications à myuser@radical-spam.com et administrateur
:quarantaine: 1 fichier dans store/amavis/quarantine/virus/*

.. code-block:: bash
    
    $ swaks --h-Subject "test mail entrant - VIRUS" \
        -s 127.0.0.1:25 --xclient 'ADDR=1.1.1.1' \
        --from sender@example.org --to myuser@radical-spam.com \
        --attach-type text/plain --attach /tmp/mail-virus-eicar.txt

--------

:test: **Mail entrant - Contenant une pièce jointe interdite**
:status: Mail non envoyé à myuser@radical-spam.com
:notification: Notification administrateur
:quarantaine: 1 fichier dans store/amavis/quarantine/banned/*

.. code-block:: bash
    
    $ swaks --h-Subject "test mail entrant - BANNED PIF" \
        -s 127.0.0.1:25 --xclient 'ADDR=1.1.1.1' \
        --from sender@example.org --to myuser@radical-spam.com \
        --attach-type application/pif --attach /tmp/mail-banned.pif
   
--------

:test: **Mail entrant - Contenant un Spam**
:status: Mail envoyé à myuser@radical-spam.com (sujet modifié)
:notification: Notification administrateur
:quarantaine: 1 fichier dans store/amavis/quarantine/spam/*   

.. code-block:: bash
    
    $ swaks --h-Subject "test mail entrant - SPAM" \
        -s 127.0.0.1:25 --xclient 'ADDR=1.1.1.1' \
        --from sender@example.org --to myuser@radical-spam.com \
        --attach-type text/plain --attach /tmp/mail-spam-gtube.txt

.. |Build Status| image:: https://travis-ci.org/srault95/radicalspam.svg?branch=master
   :target: https://travis-ci.org/srault95/radicalspam
   :alt: Travis Build Status
   
.. |Build Doc| image:: https://readthedocs.org/projects/widukind-dlstats/badge/?version=latest
   :target: http://widukind-dlstats.readthedocs.org/en/latest/?badge=latest
   :alt: Documentation Status   
   
.. |Gitter| image:: https://badges.gitter.im/srault95/radicalspam.svg
   :alt: Join the chat at https://gitter.im/srault95/radicalspam
   :target: https://gitter.im/srault95/radicalspam?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge      

