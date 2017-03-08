Migration Abakus/Cias/Blois vers un même server
===============================================

TODO - FIXME
------------

- DEFAULT de l'architecture:
    - Pas redondable
    - Pas distribuable à cause de l'usage intensif des loopback
- ARCHITECTURE souhaités:
    - Utilisation de docker et swarm
    - Répartition des CT sur plusieurs serveurs ou lancement à la demande mais config ?
        - il faudrait pouvoir lancer n'importe quelle images avec une config dynamique    

- Suivre consommation CPU/RAM/.. par collect ou autre avec envoi InfluxDB ou Graphite !
- Ecrire un test pour le problème outgoing_bypass dans mongrey
- Test de l'import des fixtures pour voir le pb des warning: je crois parce que pas de purge
- Purger les données de chaque instance mongo
- Activer les autres instances (cias/blois)

- Réactiver la rbl coté postfix et la désactiver coté mongrey ?

- Tous activer dans les filter/policy pour lancer toutes les VM
- Voir centralisation des logs par TCP ou par logcabin ?
    - voir aussi driver syslog de docker

- Chercher un autre proxy smtp pour simuler les filters avec API REST pour vérifier réception    

- Créer une vrai image de filtrage amavis ou autre pour remplacer les faux filtres
    - VOIR ce que fait amavis en sortie si il n'arrive pas à joindre le reply ou si il est rejeté
        - Toujours dans la session initiale ou background ?
    - Si mongo-mail-server:
        - Appels clamav/sa par commande sys plutot que protocol
        - Manque gestion décision selon virus ou spam score
        - Manque gestion livraison ou mise en quarantaine + notifications
        - Manque filtrage pièces jointes
        - Manque scorings sur BL/WL

Docker Alpine
-------------

- http://alpinelinux.org/
- http://wiki.alpinelinux.org/wiki/Main_Page
- http://gliderlabs.viewdocs.io/docker-alpine/usage

- La base alpine la plus utilisé:
    https://registry.hub.docker.com/u/gliderlabs/alpine/
    https://github.com/gliderlabs/docker-alpine
- En second    
    - https://registry.hub.docker.com/_/alpine/

- Entre un mysql-client dans un docker ubuntu 14 et la même chose avec alpine:
    - ubuntu: 164 Mo
    - alpine: 16 Mo

- Alpine Linux est une distribution communautaire dédiées aux routeurs x86, pare-feux, VPN, 
boîtes VoIP et systèmes embarqués. Elle fait de la sécurité proactive grâce à PaX et SSP. 
La bibliothèque C utilisée est uClibc et les outils de base sont dans BusyBox. 

- http://pkgs.alpinelinux.org/contents?pkgname=postfix&arch=x86
    - postfix 3.0.1-r2
- cython

::

    docker run gliderlabs/alpine apk --update add postfix

    docker pull frolvlad/alpine-python2
    docker pull frolvlad/alpine-python3
    
    FROM alpine:3.2
    RUN apk add --update python && \
        apk add wget ca-certificates && \
        wget "https://bootstrap.pypa.io/get-pip.py" -O /dev/stdout | python && \
        apk del wget ca-certificates && \
        rm /var/cache/apk/*        

Retour à RS3:
-------------

- Etre au moins iso-fonctionnel coté postfix avant d'intégrer des modifications fonctionnelles
    - Juste reporté certains paramètres qui étaient dans le main.cf, dans le master.cf quand c possible sinon dans des policy class
    - OU généraliser l'usage de policy class
    - cumuler tout dans relay restrictions

- Copier le rs abakus
- vider la queue
- ajout myhostname dans l'ip wan abakus
- ajout entrée ip wan/lan/ smtp out bind pour cias
- ajout des domaines et autres infos cias
- config amavis: ajout port + policie cias
- Pour cias, ajouter une ip public pour son future mx ou ne gérer que remplacement ip dans dns
    - ancien et nouvelle ip avec même myhostname
- Prévoir ip à part pour gcr

- Avec new postfix et new amavis et mongrey:
    - 1. mettre en oeuvre et lancer les instances mongrey
    - 2. même chose pour amavis
        - config du minimum dans amavisd.conf
        - ensuite, 1 template filter-in et un filter-out
    - 3. lancer la config auto postfix
        - adapter filters et policies
        - 1 mynetwork wan par ip lan
        - 1 mynetwork lan par ip lan
        - déplacer dans policy access, les règles par domaines
            - pour chaque client, une policy in et une policy out

Essai migration iso sur les restrictions
----------------------------------------

::

    WAN AVANT:

        smtpd_client_restrictions = permit_mynetworks, check_client_access hash:/addons/postfix/etc/local-whitelist-clients, sleep 2, check_client_access hash:/addons/postfix/etc/local-blacklist-clients, reject_rbl_client zen.spamhaus.org
        smtpd_helo_restrictions = check_helo_access hash:/addons/postfix/etc/local-exceptions-helo, check_helo_access hash:/addons/postfix/etc/local-blacklist-helo, check_helo_access hash:/addons/postfix/etc/local-spoofing
        smtpd_sender_restrictions = permit_mynetworks, check_sender_access hash:/addons/postfix/etc/local-exceptions-senders, reject_non_fqdn_sender, check_sender_access hash:/addons/postfix/etc/local-spoofing, check_sender_access hash:/addons/postfix/etc/local-blacklist-senders
        smtpd_recipient_restrictions = check_recipient_access hash:/addons/postfix/etc/local-blacklist-recipients, reject_non_fqdn_recipient, reject_unauth_destination, check_recipient_access hash:/addons/postfix/etc/local-verify-recipients, check_policy_service inet:127.0.0.1:10023, reject_unlisted_recipient, check_recipient_access hash:/addons/postfix/etc/local-filters

    WAN APRES:

        # global
        smtpd_relay_restrictions = defer_if_reject, check_recipient_access hash:${config_directory}/policies-recipients, check_recipient_access hash:${config_directory}/verify-recipients, defer_unauth_destination
        smtpd_restriction_classes=policy_abakus_in,policy_abakus_out

        -o smtpd_client_restrictions=
        -o smtpd_helo_restrictions=
        -o smtpd_sender_restrictions=
        -o smtpd_recipient_restrictions=

        policy_abakus_in =
            check_client_access hash:${config_directory}/policies-ip, 
            reject_non_fqdn_sender
            reject_non_fqdn_recipient 
            check_client_access hash:/addons/postfix/etc/local-whitelist-clients, sleep 2, check_client_access hash:/addons/postfix/etc/local-blacklist-clients, reject_rbl_client zen.spamhaus.org
            check_sender_access hash:/addons/postfix/etc/local-spoofing, check_sender_access hash:/addons/postfix/etc/local-blacklist-senders
            check_recipient_access hash:/addons/postfix/etc/local-blacklist-recipients, reject_non_fqdn_recipient, reject_unauth_destination, check_recipient_access hash:/addons/postfix/etc/local-verify-recipients, check_policy_service inet:127.0.0.1:10023, reject_unlisted_recipient, check_recipient_access hash:/addons/postfix/etc/local-filters 


Retour à un RS unique partagé MAIS avec variante
------------------------------------------------

- POURQUOI: ?
    - il faut ip lan et wan dans la même instance car ce qui vient de l'ip lan doit être livré par l'ip wan
    > ou dans l'instance ip lan, utiliser un smtp_bind de l'ip wan ? NON va aussi livrer au LAN avec l'ip wan, pas mieux !
    
    - Pose le problème des limites de config du master.cf pour l'ip LAN
    
    - OU: garder 2 instances (lan/wan) mais sur WAN ouvrir un canal local sur un port précis et configurer le relayhost 
    de l'instance LAN pour sortir toujours par l'ip WAN ?

- 1 seul postfix

- Chaque mx à son entrée IP:25 + son myhostname + ses règles dans master.cf

- 1 seul fichier mynetwork ?

- un check policy par domains pour utiliser une instance mongrey diff selon domaine
    - Que par policy access je crois::
    
    #smtpd_relay_restrictions = defer_if_reject, check_policy_service inet:127.0.0.1:11002, check_recipient_access hash:${config_directory}/verify-recipients, defer_unauth_destination

    #pour out - policy par ip
    smtpd_client_restrictions = check_client_access hash:${config_directory}/policies-ip
    smtpd_relay_restrictions = defer_if_reject, check_recipient_access hash:${config_directory}/policies-recipients, check_recipient_access hash:${config_directory}/verify-recipients, defer_unauth_destination
    smtpd_restriction_classes = policy_abakus, policy_gcr
    
    policy_abakus = check_policy_service inet:127.0.0.1:11002
    policy_gcr = check_policy_service inet:127.0.0.1:11003
    
    #filters-recipients
    abakus.fr        FILTER smtp-filter:[127.0.0.1]:10031
    globallp.com     FILTER smtp-filter:[127.0.0.1]:10032

    #filters-ip:
    193.240.22.65    FILTER smtp-filter:[127.0.0.1]:10131
    86.65.251.111    FILTER smtp-filter:[127.0.0.1]:10132
     
    #policies-recipients
    abakus.fr        policy_abakus
    globallp.com     policy_gcr
    
    #policies-ip:
    #91.121.40.27     policy_abakus : nagios check !!!: pas de policy
    193.240.22.65    policy_abakus
    86.65.251.111    policy_gcr
    217.119.135.21   policy_gcr
    
    swaks
    swaks --local-interface 127.0.0.1 --server 149.202.17.32 --quit-after RCPT --timeout 2 --protocol ESMTP --xclient 'NAME=mx.mcglynn.net ADDR=53.13.140.122 PROTO=ESMTP HELO=mx.mcglynn.net' --to rcpt@abakus.fr --from sender@example.org
    swaks --local-interface 127.0.0.1 --server 149.202.17.32 --quit-after RCPT --timeout 2 --protocol ESMTP --xclient 'NAME=mx.abakus.fr ADDR=193.240.22.65 PROTO=ESMTP HELO=mx.abakus.fr' --to rcpt@example.org --from sender@abakus.fr
    
    swaks --local-interface 127.0.0.1 --server 149.202.17.32 --quit-after RCPT --timeout 2 --protocol ESMTP --xclient 'NAME=mx.mcglynn.net ADDR=53.13.140.122 PROTO=ESMTP HELO=mx.mcglynn.net' --to rcpt@globallp.com --from sender@example.org
    
TODO
----

::

    Erreur: l'instance postfix out ne peut livrer elle même les mails vers les destinataire externes:
    - car sont ip n'est pas celle du mx
    
    > SI MONGREY, retour à architecture à 1 IP MAIS en attendant supp de la seconde:
        - même conf sur ip mx que ip lan: juste un double bind ?
    
    ip mx:
        - entrant/sortant officiel des mails d'un domaine
        - règles in:
            - policy/filter in/mynetwork wan quand nécessaire
        
    ip lan:
        - entrant/sortant du lan client
        - policy light/filter out facultatif/mynetwork lan !!!
        - 1 fois le mail arrivé, il doit être livré à l'extérieur par l'ip MX !
    
    

- tests dans docker:
    https://github.com/gryphius/fuglu/blob/master/fuglu/tests/docker/ubuntu/checkout-and-run-fuglu-tests.sh
    et intégration centos

- manque gestion in/out amavis
    - LE plus simple:
        - ajout entrée amavis retour dans master.cf pour chaque instance
            - attention au cleanup
        - chaque amavis à une ip looback / port diff qui pointe vers sont postfix master
        - chaque amavis à un nombre de processus limité: 1 pour out, 2 pour in et ram  en proportion
        !!! SI diff in/out coté amavis, il y aura 2 bayes distinct !!!
        
    abakus-in:
        smtpd in:
            87.98.174.172:25
        amavis in:
            127.0.0.1:10035
        amavis out:
            127.0.0.1:10036
        content filter in:
            domaines recipients abakus: 127.0.0.1:10025
            domaines recipients gcr:    127.0.0.1:10027
        content filter out:
            domaines sender abakus: 127.0.0.1:10026
            domaines sender gcr:    127.0.0.1:10028
        
    amavis-abakus:
        policy-abakus-in:
            127.0.0.1:10025 -> 127.0.0.1:10035
        policy-abakus-out:
            127.0.0.1:10026 -> 127.0.0.1:10036
        policy-gcr-in:
            127.0.0.1:10027 -> 127.0.0.1:10035
        policy-gcr-out:
            127.0.0.1:10028 -> 127.0.0.1:10036
        

    - Créer des ip locales virtuelles ?: non, il faut un bridge dédié à docker
    - ajouter dans le master du in qui possède les transport
    - ajout bind ip loopback ?: pas possible sur chaque !
    - si loopback, diff de 10025/10026 pour multi postfix
    OU
    - création instance dédié avec mynetwork + reject dans clients restriction ou relay

- Télécharger les premieres signatures::
    RUN wget -O /var/lib/clamav/main.cvd http://database.clamav.net/main.cvd && \
        wget -O /var/lib/clamav/daily.cvd http://database.clamav.net/daily.cvd && \
        wget -O /var/lib/clamav/bytecode.cvd http://database.clamav.net/bytecode.cvd && \
        chown clamav:clamav /var/lib/clamav/*.cvd
        
- spamd: https://registry.hub.docker.com/u/dinkel/spamassassin/dockerfile/
- https://github.com/erocarrera/pefile
    https://github.com/blacktop/malice/blob/master/modules/file/pe.py
    
- Shadow Server - Binary Whitelist and MD5/SHA1 AV Service API
    https://pypi.python.org/pypi/shadow-server-api/1.0.4
    https://www.shadowserver.org/wiki/
    
- https://github.com/blacktop/malice/blob/master/modules/intel/virustotal.py                

- amavis:
    - ou remplacer amavis par:
        https://wiki.apache.org/spamassassin/IntegratedSpamdInPostfix
        https://wiki.apache.org/spamassassin/IntegratePostfixViaSpampd
        https://wiki.archlinux.org/index.php/ClamSMTP:_An_SMTP_Virus_Filter
        https://www.debian-administration.org/article/259/Virus_filtering_with_Postfix_and_ClamAV_in_4_steps_

    - séparer clamav et voir amavis tcp ou use volume from pour use socket

        - ATTENTION au fait que le message est envoyé par tcp au lieu d'une analyse unique sur disque !!!!!

        - attention aux droits amavis/clamav        
        
        - add user clamav to the amavis group and AllowSupplementaryGroups to clamd.conf
        
        - comment utiliser tcp au lieu de socket dans::
        
            # ['ClamAV-clamd',
            #   \&ask_daemon, ["CONTSCAN {}\n", "/var/run/clamav/clamd.sock"],
            #   qr/\bOK$/m, qr/\bFOUND$/m,
            #   qr/^.*?: (?!Infected Archive)(.*) FOUND$/m ],
            
            Existe dans les av de secours: MAIS il faut le client clamdscan :
            
            # ### http://www.clamav.net/ - using remote clamd scanner as a backup
            # ['ClamAV-clamdscan', 'clamdscan',
            #   "--stdout --no-summary --config-file=/etc/clamd-client.conf {}",
            #   [0], qr/:.*\sFOUND$/m, qr/^.*?: (?!Infected Archive)(.*) FOUND$/m ],
            
            Sinon:
            http://packages.ubuntu.com/trusty/libclamav-client-perl

    - utiliser un startamavis.sh pour gérer les var d'env dans la commande            

    - config postfix pour les retour in/ou amavis
        - voir si amavis peut utiliser des noms d'hotes
    - Préparation de l'image amavis: (pas le temps pour terminer mms)
    
    - penser aux templates de notifications
    
    - !!! utiliser lmtp entre postfix et amavis ?

- Comment tester correctement config:
    - envoi direct requettes sur mongrey mais reste pb des règles postfix
        - servira pour tests des binaires
    - scénarios postfix et policy avec réponse attendu

- Import datas postgrey

- voir trap dans https://github.com/onesysadmin/ubuntu-postfix/blob/master/deploy/run-app.sh

- si tests mongrey, ok, il faut désactiver postfix: 
    - directory
    - relays-domains ?

- Consolidation bayes des 3 serveurs::
    - export bayes de chacun
    - import bayes -> redis de chacun des exports

- apport gosu dans les images ?

- ce qui m'empêche de placer postfix multi-instance dans docker:
    - run auto des instances postfix au démarrage
    - mises à jour des données
    - besoins ssh
    
- fixtures mongrey pour ajout par défaut des mx gmail et autres connus ? 

- voir question du::
    syslog_name = postfix-out
    Attention, une entrée postfix/ devient postfix-abakus-out/
    Adapter nagios ?

- Voir autre process pour mongrey car génère une image par instance web et server
    - publier images sur registry ?
    - utiliser ma registry ?
    
- ELK ou logcabin -> mongodb et/ou influxdb

Process complet
---------------

- local - A partir de rs3-migration::

    fab mongrey_fixtures
    
    fab git_update
    
    fab mongrey_compose:hosts=rs3
        
    # Build + run + init multi + conf complète des instances postfix
    fab postfix_build:hosts=rs3
    fab postfix_run:hosts=rs3
    fab postfix_config:hosts=rs3_postfix_dev
    
    # pour juste raffraichir une modif dans fabfile
    fab postfix_refresh:hosts=rs3_postfix_dev
    
    # pour lancer les tests
    fab swaks_tests:hosts=rs3_postfix_dev,instance_name=postfix-abakus-in
    fab swaks_tests:hosts=rs3_postfix_dev,instance_name=postfix-abakus-out

Méthode
-------

Base
::::

- Sur mx abakus::

    cd /home
    radicalspam stop
    tar --numeric-owner --exclude=rs/proc -cf rs-abakus.tar rs
    scp rs-abakus.tar 37.187.147.163:/home
    # radicalspam start : NON

    PHASE2: au moment de la migration

        - down les ip sur l'ancien mx
            ifdown eth0:2
            ifdown eth0:1
            ifdown eth0:0
                
        tar --numeric-owner -cf rs-abakus-complement.tar rs/addons/postfix/var/spool rs/addons/amavis/var/amavis/virusmails
        scp rs-abakus-complement.tar 37.187.147.163:/home
    
- Sur new dedie::

    cd /home
    tar --numeric-owner -xf rs-abakus.tar
    ln -vsf /home/rs /var/rs
    mkdir -p /var/rs/proc
    rm -f rs-abakus.tar
        
    # sur queue et quarantaine
        rm -rf /var/rs/addons/postfix/var/spool/*
        find /var/rs/addons/amavis/var/amavis/virusmails -type f -exec rm -f {} \;
    
    - restart rsyslog
        service rsyslog restart

    - path scripts postfix:
        vi /root/.bashrc
        export PATH=/var/rs/etc/scripts:/var/rs/addons/postfix/scripts:$PATH
        . /root/.bashrc
        
        mailq

    - modif master.cf pour myhostname dans master au lieu de main
        -o myhostname=smtp.radicalspam.org
    
    - Désactiver bind si use dnsmasq de l'os
        radicalspam status_change BIND
        
    > revoir interfaces car semble dire que suffise les entrée post-up et post-down
        > non: http://docs.ovh.ca/fr/guides-network-ipaliasing.html
        
    - Transférer les ip de ns339295 vers ns397840: NOK
        87.98.174.172
        91.121.33.51
        
        ns339295
            contact admin/fact: HP3756-OVH
            contact tech: RS134081-OVH
            Datacentre :    rbx6
            Datacentre :    gra1
        ns397840
            contact admin/fact: PD29915-OVH / mongodb2015*
            contact tech: RS134081-OVH
            
    - Transférer les ip de 0-ns332247-soyoustart vers ns397840: NOK
        37.187.189.48
        37.187.189.50
        
        avec login: PD29915-OVH
        block: 37.187.189.48/30
        code: tuuwLKjqGnfXS3ykaDNr
        
        Une erreur est survenue lors de la récupération des serveurs disponibles (Under the conditions of RIPE/ARIN, we are required to check how you use your IPs. Please get in touch with our Client Service.)        
            
    - modif master.cf pour ip et myhostname
    
    - relancer network
    
    - install services init
        $ ln -sf /var/rs/etc/scripts/radicalspam /etc/init.d/radicalspam
        $ cd /etc/rc2.d/
        $ ln -sf ../init.d/radicalspam S99radicalspam
        $ ln -sf ../init.d/radicalspam K01radicalspam
    
    - install cron
        ln -sf /var/rs/etc/radicalspam.cron /etc/cron.d/radicalspam
        
    - backup mail
       cd /root
       wget http://download.radicalspam.org/3-others/backup-rs.cron
       wget http://download.radicalspam.org/3-others/backup-rs.sh
       chmod +x backup-rs.sh
       ln -sf /root/backup-rs.cron /etc/cron.d/backup-rs
    
    - voir:
        apt-get install bsd-mailx
        vi /etc/mail.rc
        set smtp=127.0.0.1

        vi /root/.mailrc
        set smtp=127.0.0.1
        #set sendmail=/usr/bin/msmtp
    
    
    - modif local-xxx pour ajout cias/blois
    - modif amavis pour ajout cias/blois
        - ajout conf + policy
    - modif nagios pour liens cias/blois
    - modif whitelist postgrey: ok même list
    
    - AJOUT CIAS:
        # fermer rs
        
        ifdown eth0:0
        ifdown eth0:2
        
        # backup virusmail et spool:
        cd /home
        tar --numeric-owner -cf rs-cias-complement.tar rs/addons/postfix/var/spool rs/addons/amavis/var/amavis/virusmails
        scp rs-cias-complement.tar 37.187.147.163:/home
    
        #amavisd.conf: OK
            
            %banned_rules = (
              'cias' => new_RE(
                qr'.\.(ade|adp|app|bas|bat|chm|cmd|com|cpl|crt|fxp|hlp|hta|inf|ins|isp|js|jse|lnk|mdt|mdw|msc|msp|mst|ops|pif|prg|reg|scr|sct|shb|shs|vbs|wsc|wsf|wsh)$'i,
              ),

            );
            
            $interface_policy{'10039'} = 'cias';
            include_config_files('/addons/amavis/etc/amavisd.d/cias.conf');
        
        #amavisd.d/cias.conf:
        
        #/var/rs/addons/amavis/var/amavis/inet_socket_port
        10039
        
        local-relays: OK
            ciasdublaisois.fr   OK
        
        local-canonical-recipient: OK
            abuse@ciasdublaisois.fr abuse@mx3.radical-spam.fr
            postmaster@ciasdublaisois.fr    postmaster@mx3.radical-spam.fr
        
        local-blacklist-*   : A FAIRE
        
        local-spoofing
            robot@ciasdublaisois.fr                         OK
            no-reply@ciasdublaisois.fr          OK
            ciasdublaisois.fr                               REJECT ANTI-SPOOFING
        
        local-transport: OK
            ciasdublaisois.fr                               smtp-customers-cias:[92.103.220.106]:25
        
        local-transport-opt...: OK
            hotmail.com         smtp-hotmail:
            hotmail.fr          smtp-hotmail:
            live.fr             smtp-hotmail:
        
        local-mynetworks-lan:
            81.252.10.245           # in/out CIAS
            92.103.220.106          # neq
        
        local-directory : OK
            @ciasdublaisois.fr      OK
        
        local-filters: (vérifier port): OK
            ciasdublaisois.fr               FILTER smtp-amavis:[127.0.0.1]:10039
            
        master.cf:
            # WAN - CIAS - mx3.radical-spam.fr
            37.187.189.48:smtp      inet  n       -       n       -       -      smtpd
               -o myhostname=mx3.radical-spam.fr
               -o mynetworks=hash:/addons/postfix/etc/local-mynetworks-wan
               -o cleanup_service_name=cleanup-wan
               -o receive_override_options=no_address_mappings
            
            # LAN - CIAS
            37.187.189.50:smtp      inet  n       -       n       -       -      smtpd
                -o myhostname=mx-out2.radical-spam.fr
               -o content_filter=smtp-amavis:[127.0.0.1]:10029
               -o mynetworks=hash:/addons/postfix/etc/local-mynetworks-lan
               -o smtpd_client_restrictions=permit_mynetworks,reject
               -o smtpd_helo_restrictions=
               -o smtpd_sender_restrictions=reject_non_fqdn_sender,hash:/addons/postfix/etc/local-blacklist-senders,hash:/addons/postfix/etc/local-relays,hash:/addons/postfix/etc/local-exceptions-senders
               -o smtpd_recipient_restrictions=reject_non_fqdn_recipient,hash:/addons/postfix/etc/local-blacklist-recipients,permit_mynetworks,reject
               -o smtpd_end_of_data_restrictions=
               -o smtpd_reject_unlisted_sender=yes
               -o smtpd_reject_unlisted_recipient=no
               -o receive_override_options=no_address_mappings
        
            smtp-customers-cias unix        -       -       n       -       10  smtp
               -o smtp_bind_address=37.187.189.50
               
            smtp-hotmail unix        -       -       n       -       1  smtp
               -o smtp_destination_concurrency_limit=3
               
    

CIAS
::::

- Vérifier queue et supp si necessaire

Abakus
::::::

- Vérifier queue et supp si necessaire - SI pas relancer apres backup

Blois
:::::

- Vérifier queue et supp si necessaire

new dédié - Interfaces
----------------------

::

    # déjà prix: eth0:0 -> eth0:7

    # abakus - smtp.radicalspam.org
    auto eth0:8
    iface eth0:8 inet static
            address 87.98.174.172
            netmask 255.255.255.255
            broadcast 87.98.174.172
    
    # abakus - smtp-out.radicalspam.org
    auto eth0:9
    iface eth0:9 inet static
            address 91.121.33.51
            netmask 255.255.255.255
            broadcast 91.121.33.51

    # cias - mx3.radical-spam.fr
    #auto eth0:10
    #iface eth0:10 inet static
    #        address 37.187.189.48
    #        netmask 255.255.255.255
    #        broadcast 37.187.189.48

    # cias - mx-out2.radical-spam.fr
    #auto eth0:11
    #iface eth0:11 inet static
    #        address 37.187.189.50
    #        netmask 255.255.255.255
    #        broadcast 37.187.189.50
            
    # blois - mx2.ville-blois.fr / 87.98.146.126            
    #auto eth0:12
    #iface eth0:12 inet static
    #        address 87.98.146.126
    #        netmask 255.255.255.255
    #        broadcast 87.98.146.126
            
    # blois - smtp out            
    #auto eth0:13
    #iface eth0:13 inet static
    #        address 87.98.146.127
    #        netmask 255.255.255.255
    #        broadcast 87.98.146.127

    post-up /sbin/ifconfig eth0:8 87.98.174.172 netmask 255.255.255.255 broadcast 87.98.174.172
    post-down /sbin/ifconfig eth0:8 down

    post-up /sbin/ifconfig eth0:9 91.121.33.51 netmask 255.255.255.255 broadcast 91.121.33.51
    post-down /sbin/ifconfig eth0:9 down

    #post-up /sbin/ifconfig eth0:10 37.187.189.48 netmask 255.255.255.255 broadcast 37.187.189.48
    #post-down /sbin/ifconfig eth0:10 down

    #post-up /sbin/ifconfig eth0:11 37.187.189.50 netmask 255.255.255.255 broadcast 37.187.189.50
    #post-down /sbin/ifconfig eth0:11 down
    
    #post-up /sbin/ifconfig eth0:12 87.98.146.126 netmask 255.255.255.255 broadcast 87.98.146.126
    #post-down /sbin/ifconfig eth0:12 down

    #post-up /sbin/ifconfig eth0:13 87.98.146.127 netmask 255.255.255.255 broadcast 87.98.146.127
    #post-down /sbin/ifconfig eth0:13 down

new dédié - amavis - ports
--------------------------

::

    10024   : Pas utilisé
    9998    : port de service
    
    10029   : port output abakus
        - renvoi ensuite vers postfix 10026
    
    10031   : abakus
    10033   : brasseurs
    10037   : gcr
    10038   : dupouy
    
    10040   : CIAS 
    10050   : Blois 
    

new dédié - master.cf
---------------------

::

    - voir smtp_helo_name pour les entrée customer


    # WAN - eth0:8 - abakus - smtp.radicalspam.org
    87.98.174.172:smtp      inet  n       -       n       -       -      smtpd
       -o mynetworks=hash:/addons/postfix/etc/local-mynetworks-wan
       -o receive_override_options=no_address_mappings
       -o myhostname=smtp.radicalspam.org
    
    # LAN - eth0:9 - abakus - smtp-out.radicalspam.org
    91.121.33.51:smtp      inet  n       -       n       -       -      smtpd
       -o content_filter=smtp-amavis:[127.0.0.1]:10029
       -o mynetworks=hash:/addons/postfix/etc/local-mynetworks-lan
       -o smtpd_client_restrictions=permit_mynetworks,reject
       -o smtpd_helo_restrictions=
       -o smtpd_sender_restrictions=reject_non_fqdn_sender,hash:/addons/postfix/etc/local-blacklist-senders,hash:/addons/postfix/etc/local-relays,hash:/addons/postfix/etc/local-exceptions-senders
       -o smtpd_recipient_restrictions=reject_non_fqdn_recipient,hash:/addons/postfix/etc/local-blacklist-recipients,permit_mynetworks,reject
       -o smtpd_end_of_data_restrictions=
       -o smtpd_reject_unlisted_sender=yes
       -o smtpd_reject_unlisted_recipient=no
       -o receive_override_options=no_address_mappings
       -o myhostname=smtp-out.radicalspam.org

    
Abakus IP/mx/lan
----------------

mx: smtp.radicalspam.org / 87.98.174.172

ip wan: 87.98.174.172
ip lan: 91.121.33.51

smtp-customers unix        -       -       n       -       10  smtp
   -o smtp_bind_address=91.121.33.51
   
smtp-limit-connect      unix  -       -       n       -       -       smtp
   -o smtp_destination_concurrency_limit=5

smtp-orange      unix  -       -       n       -       1       smtp
   -o smtp_destination_concurrency_limit=3
   

CIAS IP/mx/lan
--------------

mx: mx3.radical-spam.fr / 37.187.189.48

ip wan: 37.187.189.48
ip lan: 37.187.189.50

smtp-customers unix        -       -       n       -       10  smtp
   -o smtp_bind_address=37.187.189.50

smtp-customers-cias unix        -       -       n       -       10  smtp
   -o smtp_bind_address=37.187.189.50

smtp-hotmail unix        -       -       n       -       1  smtp
   -o smtp_bind_address=188.165.212.81
   -o smtp_destination_concurrency_limit=3

smtp-limit-connect      unix  -       -       n       -       -       smtp
   -o smtp_destination_concurrency_limit=5

smtp-orange      unix  -       -       n       -       1       smtp
   -o smtp_destination_concurrency_limit=3


Blois - mx2 - IP/mx/lan
-----------------------

mx: mx2.ville-blois.fr / 87.98.146.126

ip wan: 87.98.146.126
ip lan: 87.98.146.127

smtp-customers unix        -       -       n       -       10  smtp
   -o smtp_bind_address=87.98.146.127

smtp-orange      unix  -       -       n       -       1       smtp
   -o smtp_destination_concurrency_limit=3

smtp-gmail      unix  -       -       n       -       -       smtp
   -o smtp_destination_concurrency_limit=2
   -o smtp_destination_recipient_limit=5

Postfix Multi Instance
----------------------

- Essai avec un Dockerfile::
    
    # Si net host, pas besoin du mapping
    $ docker run -it --rm -e AUTHORIZED_KEYS="`cat ~/.ssh/authorized_keys2`" --net host --privileged=true --cap-add=ALL -v /dev/log:/dev/log -v /dev/log:/var/spool/postfix/dev/log postfix/dev
    
    # Sans net host:
    $ docker run -it --rm -e AUTHORIZED_KEYS="`cat ~/.ssh/authorized_keys2`" -p 37.187.147.163:2222:2222 --privileged=true --cap-add=ALL -v /dev/log:/dev/log -v /dev/log:/var/spool/postfix/dev/log postfix/dev
    
    $ echo "${AUTHORIZED_KEYS}" > /root/.ssh/authorized_keys
    $ /usr/sbin/sshd
    
    $ fab hostname:hosts=rs3_postfix_dev

    # reload:
    postmulti -i <instance_name> -p reload
    
    # flush:
    postmulti -i <instance_name> -p flush
    
    # postconf sur instance: 
    postconf -c /etc/postfix-in -n
    

