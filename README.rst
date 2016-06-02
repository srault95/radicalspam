************
Radical-Spam
************

**Serveur de filtrage SMTP - Anti-Virus et Anti-Spam intégré**

**Fonctionnalités:**

* Distribution Linux: Ubuntu 16.04 (Xenial)
* Serveur SMTP : Postfix 3.1.0
* Serveur de filtrage : Amavisd-new 2.11.0
* Anti-Spam : SpamAssassin 3.4.1
* Anti-Virus : Clamav 0.99
* Serveur de cache : Redis Server 2.3.0
* Razor
* Pyzor
* Syslog intégré, redirigé pour docker
* Mise à jour automatique des signatures virales et des règles anti-spam

======
Requis
======

* 10 Go minimum (selon durée de stockage) 
* 4 Go RAM minimum (8 Go conseillé)
* Serveur Docker 1.10+ (testé avec docker 1.10.3 sur Ubuntu 14.04 OVH)
* Accès root

===============================
Démarrage rapide en 6 commandes
===============================

**1. Créez un répertoire d'installation:**

*Adaptez le chemin selon votre serveur*

.. code-block:: bash
    
    $ mkdir /home/rs4 && cd /home/rs4
    
**2. Générez l'image docker de base:**

.. code-block:: bash    

    $ docker build -t rs/base-image:xenial https://github.com/srault95/baseimage-docker.git#base-ubuntu-xenial:image

**3. Générez l'image de RadicalSpam**

.. code-block:: bash    
    
    $ docker build -t rs/radicalspam:4.0.0 https://github.com/srault95/radicalspam.git

**4. Editez le fichier ./docker_environ:**

*Personnalisez la configuration selon votre architecture*

.. code-block:: bash    

    $ curl -L -O https://raw.githubusercontent.com/srault95/radicalspam/master/docker_environ    
    $ vi docker_environ
    
**5. Démarrez RadicalSpam:**

.. code-block:: bash    
    
    $ docker run -d --net host --pid=host --name rs4 \
       --env-file=./docker_environ \
       rs/radicalspam:4.0.0

**6. Affichez les logs:**

*Il faut quelques minutes pour le premier démarrage*

.. code-block:: bash    

    $ docker logs rs4
    
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

=====================================
Astuce - Stockage externe des données
=====================================

Vous pouvez externaliser les répertoires de données à l'aide des volumes docker.

.. code-block:: bash

    $ mkdir /home/rs4 && cd /home/rs4
    docker run -d \
       --net host --name rs4 \
       --env-file=./docker_environ \
       -v $PWD/store/amavis:/var/lib/amavis \
       -v $PWD/store/clamav:/var/lib/clamav \
       -v $PWD/store/spamassassin/users:/var/lib/users/spamassassin \
       -v $PWD/store/postfix/config:/etc/postfix/local \
       rs/radicalspam:4.0.0
       
Si vous devez réinstaller Radical-Spam, il suffira de copier le répertoire store/ 
et de lancer à nouveau `docker run`.       

=====================================
Astuce - Synchronisation de l'horloge
=====================================

Pour synchroniser la timezone avec celle de l'hôte:

.. code-block:: bash

    # Executer le docker run en ajoutant le volume suivant:
    -v /etc/localtime:/etc/localtime

