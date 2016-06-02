============
Radical-Spam
============

**Serveur de filtrage SMTP - Anti-Virus et Anti-Spam intégré**

**Fonctionnalités:**

- Distribution Linux: Ubuntu 16.04 (Xenial)
- Serveur SMTP : Postfix 3.1.0
- Serveur de filtrage : Amavisd-new 2.11.0
- Anti-Spam : SpamAssassin 3.4.1
- Anti-Virus : Clamav 0.99
- Serveur de cache : Redis Server 2.3.0
- Razor
- Pyzor
- Syslog intégré, redirigé pour docker
- Mise à jour automatique des signatures virales et des règles anti-spam

Requis
------

- 10 Go minimum (selon durée de stockage) 
- 4 Go RAM minimum (8 Go conseillé)
- Serveur Docker 1.10+ (testé avec docker 1.10.3 sur Ubuntu 14.04 OVH)
- Accès root

Démarrage rapide en 6 commandes
-------------------------------

**1. Créez un répertoire d'installation:**

*Adaptez le chemin selon votre serveur*

::
    
    $ mkdir /home/rs4 && cd /home/rs4
    
**2. Générez l'image docker de base:**

::    

    $ docker build -t rs/base-image:xenial https://github.com/srault95/baseimage-docker.git#base-ubuntu-xenial:image

**3. Générez l'image de RadicalSpam**

::    
    
    $ docker build -t rs/radicalspam:4.0.0 https://github.com/srault95/radicalspam.git

**4. Editez le fichier ./docker_environ:**

*Personnalisez la configuration selon votre architecture*

::    
    
    $ vi docker_environ
    
**5. Démarrez RadicalSpam:**

::    
    
    $ docker run -d --net host --name rs4 \
       --env-file=./docker_environ \
       rs/radicalspam:4.0.0

**6. Affichez les logs:**

*Il faut quelques minutes pour le premier démarrage*

::    

    $ docker logs rs4
    
Astuce - Stockage externe des données
-------------------------------------

Vous pouvez externaliser les répertoires de données à l'aide des volumes docker.

::

    $ mkdir /home/rs4 && cd /home/rs4
    docker run -d \
       --net host --name rs4 \
       --env-file=./docker_environ \
       -v $PWD/store/amavis:/var/lib/amavis \
       -v $PWD/store/clamav:/var/lib/clamav \
       -v $PWD/store/spamassassin/users:/var/lib/users/spamassassin \
       -v $PWD/store/postfix/config:/etc/postfix/local \
       rs/radicalspam

Astuce - Synchronisation de l'horloge
-------------------------------------

Pour synchroniser la timezone avec celle de l'hôte:

::

    # Executer le docker run en ajoutant le volume suivant:
    -v /etc/localtime:/etc/localtime

Test de Radical-Spam
--------------------

- Python et swaks sont requis
- Python peut être appellé directement à partir d'un contenair docker

Les tests suivants sont basés sur la configuration d'un domaine local example.org.

Adaptez les valeurs à votre configuration. 

::


    $ apt-get install swaks
    
    # Simulation d'un mail entrant
    swaks -s 127.0.0.1:25 --from sender@example.com --to root@example.org
    
    # Simulation d'un mail sortant
    swaks -s 127.0.0.1:25 --from root@example.org --to sender@example.com
    
    # Générez un fichier avec un faux virus de test
    echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > /tmp/eicar
    
    # Virus dans un mail entrant
    swaks -s 127.0.0.1:25 --from sender@example.com --to root@example.org --attach - --suppress-data </tmp/eicar
    
    # Virus dans un mail sortant
    swaks -s 127.0.0.1:25 --from root@example.org --to sender@example.com --attach - --suppress-data </tmp/eicar

TODO
----

