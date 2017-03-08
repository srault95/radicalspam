RadicalSpam Agent
=================

Choix Stream ou disk
--------------------

- Pour utiliser plusieurs instance clamd/spamd à partir de rs-agent, il ne faut passer que par Stream !!!
    - Sauf si un rs-agent appel seulement un clamd/spamd sur la même machine ?

- Si nécessaire, optimiser en utilisant zmq ou gevent/tcp comme intermédiaire

- rs-agent doit accèder à :
    - mongodb
    - redis/queue
    - clamd/spamd/autre
    - postfix pour envoyer le mail à partir de la bonne ip public
        - postfix est lancé en --net host
        
     

Scénarios
---------

::

    1. Arrivé d'un mail dans mongodb par rs-smtpd-server
    
    2. Process dans rs-agent, génère une tâche MQ d'analyse (selon config DB/client)
        - il faut détecter new doc à traiter ou timer avec vérification
        - queue = incoming
    
    Tâche:
        - extrait le mail sur disque: 1 fois si possible
        
        - demande analyse virale si enable
            - met à jour les résultat dans DB
        - demande analyse spam si enable
            - met à jour les résultat dans DB
        - demande autres (modification sender/geoip/supp header/signature dkim/disclaimer/...)
            - met à jour MAIL dans DB
        - supprimer le mail sur disque
        - Générer tâches suivante ou flag dans DB ?
        
        DFAULT: les tâches ne sont pas parallèles !
            - Si, la tâche peut les lancer en parallèle ?
                - Sauf modification du mail


Build/Run
---------

::

    docker build -t radicalspam/rs-agent .
    
    CLAMD_ID=$(docker run -d --name clamd1 -p 3310:3310 radicalspam/rs-clamav)
    CLAMD_IP=$(docker inspect -f '{{.NetworkSettings.IPAddress}}' ${CLAMD_ID})

    docker run -it --rm --volumes-from ${CLAMD_ID} radicalspam/rs-agent clamav-cli --help 
    
    docker run -it --rm --volumes-from ${CLAMD_ID} -v `pwd`/scan:/scan radicalspam/rs-agent clamav-cli --help
    
    docker run -it --rm --volumes-from ${CLAMD_ID} -v `pwd`/scan:/scan radicalspam/rs-agent clamav-cli --host ${CLAMD_IP} ping
    docker run -it --rm --volumes-from ${CLAMD_ID} -v `pwd`/scan:/scan radicalspam/rs-agent clamav-cli --host ${CLAMD_IP} version
    
    #/var/tmp: volume partagé avec clamd
    docker run -it --rm --volumes-from ${CLAMD_ID} radicalspam/rs-agent ls -l /var/tmp
    
    docker run -it --rm --volumes-from ${CLAMD_ID} radicalspam/rs-agent ls -l /var/lib/clamav
    docker run -it --rm --volumes-from ${CLAMD_ID} radicalspam/rs-agent ls -l /etc/clamav
    
        