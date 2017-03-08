SAAS - Mail Analytics
=====================

GIT Temporaire
--------------

::

    git init --bare /home/persist/git/repos/saas-site.git
    git remote add origin ssh://root@dev2:/home/persist/git/repos/saas-site.git
    git push origin master

Ce qu'il manque au minimum pour déployer
----------------------------------------

- Besoin maitrise ufw/iptables pour éviter d'implémenter trop de sécurité !

- Sécuriser policyng-servers avec SSH/SSL (ou cryptage datas) et fail2ban
    - Comment récupérer IP d'un client ZMQ ! 

- Site SAAS pour récupérer apikey + register ?
    - utiliser apikey sur disque dans un fichier mis à jour par python ?

- !!! domains/mynetwork pour distinguer in/out/relay
- !!! consolidation multi-recipient

- App mongo pour lire stats:
    - tableaux HTML + REST pour l'instant
    - ensuite websocket + graphiques

- Déploiement d'un cluser mongodb
    
- Selon avancement:
    - Migration netcall
    - Traitement à l'arrivé comme:
        - country
        - vérification RBL
    - Génération binaire par pyinstaller pour policyng-proxy

Déploiement
-----------

1. Déployer 
    - policyng-servers sur policy.mail-analytics.io (5.196.195.66)
    - db mongo associé
    - site sur www.mail-analytics.io  (5.196.195.65)
        - Séparer client app et site ?

- srault95/policy-ng-servers configuré avec mongodb pour recevoir entrées

- srault95/policy-ng-proxy pour mutualisé et blois

- App pour lire les entrées mongo

- Process pour affectation client ou déjà fait par apikey
    - mongodb avec db public_policy et coll apikey_by_group rempli


URGENT - IMPORTANT
------------------

- Le plus important:
    - Avoir toujours du SSL entre navigateur et app
    - Avoir une auth unique géré par Nginx
    - Ne pas exposer les apps sur des ip public
    - Haute dispo pour certains apps distribués
    - Gérer les pb CORS
        - Pouvoir extraire et adapter les apps web pure

- Besoins reverse proxy avec auth et SSL pour accès aux apps comme 
    - docker-ui 
    - docker-registry
    - pypi-server
    - docker api en mode secure sans SSH
    - les ui ES, influxDB, ...
    
- Il faut d'abord régler le pb dns car routes basés sur SERVER_NAME:
    - docker-ui.mondomain.com
    - registry...
    OU il faut essayer avec des location /... et des proxy pass
    OU un seul point d'entrée mais avec des ports différents:
        proxy.mondomain.com
            :80 et :443 > pointe vers site mail-analytic
            :81 et :444 > ???

- Mapper les ports de chaque app sur le docker0    

- Config nginx avec certs mutualisé ?
    https://docker1-ui.mail-analytics.net

::

    # cumuler des cert ssl:
    cat www.example.com.crt bundle.crt > www.example.com.chained.crt
    ssl_certificate     www.example.com.chained.crt;
    openssl s_client -connect www.godaddy.com:443
    
- Idée VIRTUAL_HOST=foo.bar.com à exploiter:
    - Process qui surveille docker events
    - Pour start/stop vérifie env du CT
    - Si VIRTUAL_HOST, vérifier dans proxy-nginx si existe
        - VIRTUAL_HOST doit permettre d'ajouter une entrée reverse proxy nginx pointant vers le service dans le CT
        - il faut plus d'info: type (http/smtp/...), auth ?
    - Nginx peut t'il utiliser une DB type redis ?
    - Ou voir la config dynamique nginx
    
    - IL FAUT éviter de devoir relancer nginx

TIPS - Gestion de version git tag et setup.py
---------------------------------------------

https://pypi.python.org/packages/source/g/gitversion/gitversion-2.1.3.tar.gz

::

    le numéro de version MAJEUR quand il y a des changements rétro-incompatibles,
    le numéro de version MINEUR quand il y a des changements rétro-compatibles,
    le numéro de version de CORRECTIF quand il y a des corrections d’anomalies rétro-compatibles
   
    # tag sur le dernier commit (récupérer avec git log)
    git tag 0.0.7 c8600797dc8870554b642df9131bc33615db4259
    
    git tag
    0.0.7
    
    git describe --tags --match *.*
    0.0.7
    
    #rs_smtpd_server\version.py
    from gitversion import rewritable_git_version
    __VERSION__ = rewritable_git_version(__file__)
    
    $ python setup.py -V
    
    from rs_smtpd_server.version import get_version
    
    setup(
        name='rs-smtpd-server',
        version=get_version(),
        ...
    )


TODO - TESTS
------------

Tests unitaires
:::::::::::::::

- Mise au points config et requis: flake, coverage, ....

- https://github.com/pybuilder/pybuilder
    - A etudier, sino, jenkins
    

Tests de performances
:::::::::::::::::::::

- Locust ?

- stress:
    - outil de stress cpu/ram/...
    FROM ubuntu
    RUN apt-get update -y && apt-get install -y stress && apt-get clean -y
    ENTRYPOINT ["stress"]    
        

Tests continues
:::::::::::::::

- Drone

- http://wercker.com/

- https://travis-ci.org/getting_started
    - Projets public
    - tests unitaires et qualité
    
TODO - Apprentissage
--------------------

- Variables env pour perf CPU/Autres des apps Go

- ZMQ:
    - ZMQ_RCVMORE ?
    - LINGER
    - encodage utf ?
    - Utilisation de queue et/ou Pool pour execution des remote méthodes
    - Trouver si zmq.recv est bloquant pour 1 connection à la fois ?
    - Options context et socket
    - Use DEALER/ROUTER/POLL/MONITOR/...
    - http://zeroless.readthedocs.org/en/latest/
        - Mettre au point comme lui, des raccourcis pour des patterns zmq
- Introspection:
    - Pouvoir modifier les nom de méthodes et les décorer 
    - VOIR: package decorator, ma doc introspection et mon ancien rs tools Proxy

- os/python: rlimit, ulimit, renice, profiling, map/reduce, generator

- iptables

- MongoDB
    - Mieux exploiter les outils livrés avec mongodb: mongostat, mongotop, mongoperf
    - Mongo en sharding et replicaset
    - Indexes: http://docs.mongodb.org/manual/reference/method/db.collection.ensureIndex/#db.collection.ensureIndex
    - /mestests/src/eval_pymongo
    - Outils de test de réplique: http://mongolab.org/flip-flop/            
    
TODO - Correction docker-proxy-api
----------------------------------

- corriger syntax markdown ou refaire sphinx pour docker-proxy-api !!!

- !!! ATTENTION, registry docker utiliser le readme !!!

- token registry: a72adddc-835a-11e4-ab02-0242ac11000a 
    https://registry.hub.docker.com/u/srault95/docker-proxy-api/trigger/a72adddc-835a-11e4-ab02-0242ac11000a/
    > ex:
    $ curl --data "build=true" -X POST https://registry.hub.docker.com/u/srault95/docker-proxy-api/trigger/a72adddc-835a-11e4-ab02-0242ac11000a/
    - j'ai désactiver le build auto
    

Memento - Architecture
----------------------

::

    smtp.mail-analytics.net (5.196.195.64)
        $ dig mail-analytics.net mx
        mail-analytics.net.     10800   IN      MX      10 smtp.mail-analytics.net.
        $ host smtp.mail-analytics.net
        smtp.mail-analytics.net has address 5.196.195.64
        
    www.mail-analytics.io  (5.196.195.65)

    policy.mail-analytics.io (5.196.195.66)
        port 443    : arrivés HTTPS (A binder sur une seule interface)
        
Zone DNS::
    # mx google
    
    @ 10800 IN A 5.196.195.65
    policy 10800 IN A 5.196.195.66
    www 10800 IN A 5.196.195.65
    @ 3600 IN MX 3 ALT1.ASPMX.L.GOOGLE.COM.
    @ 3600 IN MX 3 ALT2.ASPMX.L.GOOGLE.COM.
    @ 3600 IN MX 1 ASPMX.L.GOOGLE.COM.
    @ 3600 IN MX 5 ASPMX2.GOOGLEMAIL.COM.
    @ 3600 IN MX 5 ASPMX3.GOOGLEMAIL.COM.
    @ 3600 IN MX 5 ASPMX4.GOOGLEMAIL.COM.
    @ 3600 IN MX 5 ASPMX5.GOOGLEMAIL.COM.
    @ 10800 IN TXT "google-site-verification=QzsrGVVwYYMbKN5fGQvpgTcx1VRmF32mNJCBCG7LWIg"
    @ 10800 IN TXT "v=spf1 include:aspmx.googlemail.com ~all"        
    
Memento - Commandes
-------------------

Démarrage d'un serveur ZMQ MUTUALISE pour record Mongo::

    python -m policyng.servers.saas_zmq_server -c start --debug
    
    Options:
        -A ADDRESS, --server-address ADDRESS : ZMQ Server bind address : tcp://*:4000
        -L LOCAL_ADDRESS, --server-local-address LOCAL_ADDRESS : ZMQ Local Server bind address : tcp://127.0.0.1:4001
        -U MONGO_URI, --mongo-uri MONGO_URI : MongoDB URI : mongodb://localhost:27017/public_policy           
        --log-level {CRITICAL,DEBUG,ERROR,INFO,WARNING,critical,debug,error,info,warning}
        --log-output LOGOUTPUT
        -D, --debug
        -c {start,stop,reload}, --command {start,stop,reload}
        
Proxy TCP policy/Client ZMQ::

    # Pour postfix, warn_if_reject, check_policy... inet:127.0.0.1:9998
    docker run -it --rm -p 127.0.0.1:9998:9998 srault95/policy-ng-relay /usr/local/bin/policy-client -c start -D -H 0.0.0.0
    
SAAS - Déploiement
------------------

- déployer:
    - Master et/ou site saas ?
         
    - policy-ng-relay sur dev1 et dev2 -> dev2:policy-ng-server
    
    - pour chaque groupe:
        - créer ct influxdb/grafana

- Déployer sur dev2: site, mongodb, server policy stats, influxdb, grafana..

    - Utiliser plumbum pour executer commandes distantes comme ?

    - Outil app docker pour créer/gérer ces ct
        - ouvrir un tunnel ssh quand nécessaire: clé public déjà déployé pour fabric, li faut stocker la clé privé

    - Besoin d'un register central ou en cluster
    
    - grafana/kibana/nginx proxy vers grafana/kibana + ES et influxdb dans même machine:
        - Au lieu /xxx utiliser un host diff en interne du proxy ?
        - Voir plutot les virtuel name pour garder même port dans tous les proxy
  

SAAS - MASTER
-------------

- Doit être capable par programmation ou api de lancer des CT d'après images dispo

- 1 master par server
    - Election entre master(d'un datacenter) pour savoir qui est le maitre
    - Les slave routent les demandes vers le maitre
    - Le maitre transfère l'execution de tâche à server tasks, record pickle mongo ?
        - Permet si le maitre est indisponible de faire executer les tâches par le prochain maitre
    - Le maitre peut déléguer execution d'une tâche à un slave !
        - Le mieux en async, placer tâche dans DB tasks et affecter à N slave
                
- utiliser libcloud pour remote storage (mail backup au format original/...), archive légal

- Master pour créer/lancer/maintenir CT et Services dans les ct
    - Features a Ajouter à master:
        - zmq PUB avec event normaliser pour propager event
        - event doit aussi être récupérable par websocket et long polling (vue api rest)
        - Comment avertir CT postfix1 que policy relay change IP ?
            - Mauvais cas, car use dns round robin
            - MAIS event déclenche mise à jour DNS
        - Cas entre grafana et influxdb:
            - même chose si use dns, pas de pb pour change ip
    - master -> mongodb / master -> agents
    - master -> dockers hosts par api (event et autres)

- Images prête à être connecté à master
    - mongodb/influxdb/redis
    - postfix -> policy relay
    - policy-relay -> policy server zmq
    - policy-server zmq -> mongodb
  
- Au début: juste un cluster mongo et une app master
    - Liste d'image référencés
    - Outils et template pour créer à la demande des CT d'après les images référencés
    - MANQUE ce qu'il se passe ensuite dans le CT

- Déploiement/Démarrage:
    - Création d'instances policy server + record dns
        - run.py: download config et run l'app par subprocess ?
    - Création d'instances postfix + record dns
    - Création d'instances policy relay + record dns

- Après run saas:
    - Connaissance de l'ip public saas, des urls mongodb, des groupes
    - Lancer policy-ng-server
    - Lancer pour chaque group: influxdb/grafana/es/kibana ?

SAAS - SITE - Séparation
------------------------

- Site
- Admin site
- API Master        
- API public
- API interne
- Espace Client
- API Client

SAAS - SITE - ALL WEB
---------------------

- Récupérer ancien rs-admin: JS, graphiques, websocket, zmq

- Intégration x-editable dans les vues comme le push request de flask-admin ?

- besoin maitrise assets ou par nodejs/bower/grunt ?

- Récupérer le meilleur de flaskbuilder et l'appliquer dans flask-Admin 
    - la bonne idée: mettre au point des éléments visuel et les transformer en macro + widget

- A chaque fois que je vois un exemple/morceau de page ok, le transformer en macro flask + widget        

- Editeur WYSIWYG/bootstrap:
    http://summernote.org/
    - ref: https://github.com/nathancahill/Flask-Edits
    
- Templates que j'ai acheté: http://www.bootbundle.com/tool

- A maitriser pour tous besoins:
    - Tansformations du menu left en barre d'icon/texte selon replié ou déplié
    - Structure générale selon page
    - Tables !!!: filter/search/pagination
        - Choix par ajax ou en live

- Flask-Admin autonome non rattaché au template mais un peu custom

- flask preferences:
    - Afficher un select avec choix de format d'affichage pour court/medium/long datetime/date
    - tableau: liste des colonnes à afficher/masquer    

- En implémentation light, angular permet:
    - de remplacer des morceaux de pages sans recharger
    - facilite Ajax
        
    

SAAS - SITE - Site Public
-------------------------

- gunicorn embarqué: (au lieu de mes serveurs WSGI custom)
    - Ou voir si chaussette mieux car prêt pour cirus
    - http://docs.gunicorn.org/en/latest/custom.html
    - gunicorn à un envoi statsd et une protection par ip + ha proxy ?
        gunicorn --statsd-host=localhost:8125 ...
    - config nginx + ssl

- templates payant à revoir:
    https://wrapbootstrap.com/theme/artificial-reason-responsive-full-pack-WB0307B17
        http://razonartificial.com/themes/reason/v1.2.1/header-light-dark/
    https://wrapbootstrap.com/theme/idea-responsive-website-template-WB0DN19X0
        http://htmlcoder.me/preview/idea/v.1.1/html/
    
- il faut en page d'index, un carousel des images de dashboard possibles
    - Voir aussi onglets pour en mettre plus dès le haut de la page
    - Semble courant maintenant de tous mettre sur première page ?
        http://www.blacktie.co/demo/pratt/#contact

- CONTENU: Ne pas oublier de charger un moyen de saisir contenu par un editeur de type markdown

- version mobile importante avec résumé principal des stats
    https://www.geckoboard.com/product/
    
- pricing:
    https://pusher.com/pricing
    http://www.iron.io/pricing
    - prices avec thèmes bootswatch:
        http://bootsnipp.com/snippets/featured/bootstrap-30-responsive-pricing-tables
        
- Setting form + db pour chaque vue (pages, nom display, options) + setting par défaut
    - interêt pour http://wtforms-json.readthedocs.org/en/latest/ ?

- menu barre vertical d'icon au lieu de menus texte quand reply: 
    http://bootsnipp.com/snippets/featured/hover-blue-button-bar

- https://github.com/abilian/abilian-core/blob/master/abilian/web/assets/__init__.py
        
- validations models/data:
    http://validators.readthedocs.org/en/latest/
    https://github.com/23andMe/Yamale

Rôles:
::::::

- A définir

Public
::::::

- Générer les SSL gratuits chez Gandi

- Version française uniquement pour l'instant

- Auth social pour version démo/free

- Register plus complet pour version payante
    - Confirmation par mail
    - Option ip fixe des clients relais

- Page de status des services

Version/Espace Revendeur
::::::::::::::::::::::::

- Faire module reseller

- Module de Facturation à l'usage:
    - Remonter les infos permettant au revendeur de générer une facturation à l'usage    

- Doit pouvoir gérer des comptes clients (groupes/users/...) ?

- Selon le niveau d'engagement:
    - Ne fait que l'interface avec le client
    - Fournit un point d'entrée à ses couleurs pour les mêmes fonctions

Domaines mail-analytics
:::::::::::::::::::::::

- Domaines achetés:
    mail-analytics.fr
    mail-analytics.net
    mail-analytics.com
    mail-analytics.org
    mail-analytics.io   : principal ou .fr 

        
SAAS - SITE - Flask-Admin
-------------------------

- Utiliser vues admin pour afficher des block complet au lieu de tableaux
    - ex User: micro fiche horizontal

- custom admin et structure / = frontend, /api = api, /backend = admin
    - Pour admin reférencer les block pour custom emplacement
    - Voir jinja custom pour placer plus facilement les blocs par des imports/include ?
        - comme les shortcode = macros ?
        - injecter des fonctions et instances dans jinja pour utiliser dans les macros comme:
            - get_articles([1,2])

- Extension flask admin et flask-security: (tous ce dont j'ai besoin pour dev rapide d'une app web)
    - oublie quokka comme exemple
    - Comme flask-admin-openerp, faire vues métier
    - Version peewee et mongoengine + admin redis/mongo
    - api rest à partir des vues d'admin
    - surtout, forms custom par onglets et choix par type de champs
    - un jolie template ou plusieurs avec change style
    - structure auth mongoengine
    - menus d'admin
    - dashboard en page d'accueil (index)
    - En plusieurs extensions pour éviter trop gros et de faire peur
    - http://bootbundle.herokuapp.com/


SAAS - SITE - ALL WEB - WebSocket - Ajax
----------------------------------------

- socket.io vs websocket
    > socket.io: voir code ajenti, circus, gunicorn, chaussette
    - http://openclassrooms.com/courses/des-applications-ultra-rapides-avec-node-js/socket-io-passez-au-temps-reel
    - voir si x-editable peut utiliser websocket ou comment mettre à jour des forms sans ajax !!!!!
    - Aide sur l'api client: http://socket.io/docs/client-api/#
    - concurrent socket.io/websocket: https://github.com/sockjs
    
    - Transports de secours pour socketio:
        WebSocket
        Flash Socket
        AJAX long-polling
        AJAX multipart streaming
        IFrame
        JSONP polling
    
    
- Utiliser websocket ou zmq pour concurrence d'accès. ex: 2 admin connecté avec le même login

- Ajax:
    - Refresh par setInterval
    - Charge coté client et server
    - Pas de maitrise si surcharge car demande refresh constante
    - Le client peut arrêter le refresh ou allongé la durée !
    
- Socket:
    - Refresh par cron ou timer
    - Charge surtout coté server ?
    - Permet de changer dynamiquement règles de push selon charge ?
    - Ouvre de multiple connections !!!

SAAS - SITE - API - Choix outils
--------------------------------

http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask

http://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
- revoir https://github.com/flask-restful/flask-restful
    https://pypi.python.org/pypi/Flask-Restdoc/0.0.2
        - Met à jour un fichier api.md ?
    https://github.com/anjianshi/flask-restful-extend
    https://github.com/rantav/flask-restful-swagger
    https://github.com/janLo/restful-fieldsets

- https://github.com/fatiherikli/kule

> idée: faire api rest en frontal pour lire/écrire dans DB
    - implémentation backend mongodb/cache/etc...
    - Utiliser dans besoins générique policy ?

- Faire un datastore json générique ?
    - lecture/écriture json ?
        
Auth REST API
:::::::::::::

- https://github.com/mozilla/PyHawk
    - https://github.com/marselester/flask-api-utils
    
::

    jq : outil json en ligne de commande
    $ apt-get install jq
    $ docker inspect redis1 |jq '.[0].Config.Env'
    $ docker inspect redis1 |jq '.[0].NetworkSettings.IPAddress'
    "172.17.0.4"
    
Schéma validation
:::::::::::::::::

- https://github.com/keleshev/schema

Docs
::::

- Voir doc api si suffit:
    ex: http://readme.drone.io/api/overview/
    http://highlightjs.readthedocs.org/en/latest/reference.html
            
SAAS - DOCS
-----------

- Récap rst format:
    https://github.com/ralsina/rst-cheatsheet/blob/master/rst-cheatsheet.rst

- https://github.com/PharkMillups/beautiful-docs#generating-docs
    - recommandé pour github: http://documentup.com/
- https://github.com/ansible/ansible/blob/devel/docsite/build-site.py
- python-guide
- Contribuer aussi à python guide ou étudier en tous cas structure
- Référencer les liens inter-sphinx pour éviter redondances (voir ceux de readthedocs)
- https://github.com/vinta/awesome-python#testing
- https://github.com/yoloseem/awesome-sphinxdoc
- voir https://pypi.python.org/pypi/alabaster/0.6.2

- A mettre en avant:
    - Server policy local ou remote répond toujours DUNNO rapidement et met en queue l'envoi du protocol
    - IL faut bien conseiller et documenter sur la partie postfix !!!
    - IMPORTANT de s'ouvrir au format graphite mais quelle partie ?
    
SAAS - Serveurs de Stats
------------------------

- Bien mettre au point l'utilisation d'un reverse proxy efficace pour les apps angulars !

::
    
    Proxy python intégré ?
        - expose interface http
        - réinterprète chaque requette ?
    

- Prévoir aggrégation pour générer des tops

- Mini Dashboard pour les parties non faisable par grafana/kibana

- Accès protocol (graphite/...) interne seulement ?

- Accès WEB/REST selon backend et frontend (grafana/...)

- Accès WEB socket à part (socketio, websocket, long polling, flash)

- Accès par profil utilisateur pour le même client
    - Voir auth ldap avec le ldap du client ?

SAAS - Serveur de recherche ES
------------------------------

ARCH - Décisions (pour rappel)
------------------------------

- Eviter de mapper ports externes quand CT accessible par son ip privé

- Eviter les link car ne fonctionne que sur la même machine

- Utiliser quand c'est possible, des CT data utiliser par des volume-from

- Chaque server Docker doit être configuré pour --dns sur DOCKER0
    - il faut sur chaque machine, un serveur dns udp/53 qui écoute sur DOCKER0
    
ARCH - Global
-------------

- Prévoir répartition géographique chez autres que OVH

- Clusters/Shard MongoDB en images Docker ou voir services externes payants (plus tard)
    - Faire un LAN virtuel pour l'accès à ces serveurs
    - COMMENCER avec un cluster de 3 serveurs simple

- Site WEB unique pour l'instant mais sur contenair/ip public dédié pour déplacement

- Serveurs de réception policy (leur trouver un nom)
    - Déployable et redondable facilement sauf les zmq qui accèdent à MongoDB
    
- Serveurs TASK car si gros volume et ordonnancement nécessaire !

- Serveurs REDIS si utilisé pour les tâches

- Prévoir purge des données servant à générer des stats

    
ARCH - Besoins Minimum: (Sur Dev2)
----------------------------------

- Contenair pour MA Site avec :
    - weaver si seul moyen de communiquer entre 2 serveurs car ip internes !

- Relais TCP policy -> ZMQ:
    - srault95/policy-ng-relay

    - blois mx1/mx2
    - mutualisé: par conteneur
    - dev2::
    
    $ docker run -it --rm -p 127.0.0.1:9998:9998 srault95/policy-ng-relay
    # postfix:
    smtpd_recipient_restrictions = warn_if_reject, check_policy_service inet:127.0.0.1:9998, check_recipient_access hash:/addons/postfix/etc/local-blacklist-recipients, reject_non_fqdn_recipient, reject_unauth_destination, check_recipient_access hash:/addons/postfix/etc/local-verify-recipients, check_policy_service inet:127.0.0.1:10023, reject_unlisted_recipient, check_recipient_access hash:/addons/postfix/etc/local-filters

- DB mongo du site avec données pour auth apikey et infos sur DB du client
    - 1 DB par client
    - 1 DB global pour le site et la gestion des clients/groupes  

- Serveur ZMQ SUB/BIND ou PULL/PUSH (voir aussi dealer/router)
    - Sécurisé par tunnel SSH avec les clients ZMQ

- Server policy local + client zmq intégré à déployer sur chaque server postfix ?

- Site web mini pour auth / register et point d'entrée du client (www.mail-analytics.io)
    - Générateur d'apikey
    - Formulaire pour ajout domain/mynetwork
    - Mini Dashboard
    - Liens vers ses différents services


ARCH - Orchestration
--------------------

A TRIER / A VOIR
::::::::::::::::

- https://github.com/andreasjansson/head-in-the-clouds
    - fabric/docker

Besoins IP/Port
:::::::::::::::

- Référentiel:
    - machines physiques
    - interface/ip physiques de chaque machine
    - liste de ports réservés non utilisable pour les CT
    - images (ip/port mappables)
    - CT (ip/port utilisé)

Besoins DNS
:::::::::::

- Server DNS relié à une DB en cluster pour utiliser les mêmes données
    - Idéalement MongoDB car déjà déployé
    - Il faut pouvoir transformer les données mongo en réponse DNS

Hors de contenair
!!!!!!!!!!!!!!!!!

- Besoins publics comme les mx, etc...
- Besoins internes pour retrouver les machines avec un dns interne

Dans les contenair
!!!!!!!!!!!!!!!!!!

Besoins - Volumes
:::::::::::::::::

- Stockage des images/backup ct par git dans un repo privé !

- Volumes non répliqués !
    - Voir CT volume from pour backup de volume/ct

- Faire des packs avec l'image + sites/app à déployer en archives

Besoins - Propagation d'évènement: start/stop/change ip
:::::::::::::::::::::::::::::::::::::::::::::::::::::::

- le restart d'une instance dockerfile/mongodb doit être visible pour qui s'y abonne

- Si archi avec master, c'est les master qui écoute et propage events

- Qui/Comment gérer les répercutions:
    - modif dns
    - restart de services dépendants
- Si master lance un influxdb1:
    - le master connait id, name, ...
- Si master lance une grafana1 dépendant de influxdb1
    - le master fournit info sur influxdb1
    - en cas de changement, le master fait : ?

- LE PLUS SOUVENT:
    - lancement de grafana1 qui dit dépendre d'une image influxdb

Besoins - Comment identifier un contenair
:::::::::::::::::::::::::::::::::::::::::

- std: récupérable par api event: (attention, valable par machine !!!)
    - name manuel au run/create ou affecté par docker
    - HOSTNAME=5c835c2645b4 qui contient pas défaut le début de l'id
    - l'id affecté par docker
    - nom de l'image
- fichier .key ou env inséré au démarrage pour toute la durée de vie du CT

Besoins - Auto-Conf
:::::::::::::::::::

- POUR choisir:
    - capacité à créer/run par api docker
        - créer une image avec un socket docker et un client docker 
            - volume externe pour executer un script utilisant le client docker ?                       
        - ligne de commande
        - Par master
            - 1 master par machine ?
    - capacité à controler ct distant à partir d'un master
        - start/stop services à l'intérieur
    - besoins annexes comme syslog partagé      

- Un ct ne doit pas être créé hors du control d'un master
- Le ct se lance et attend instruction/config du master ?
OU
- Le ct est créé/lancé par master qui fournit la conf ?
    - Le master sera à l'extérieur du CT, il faut une phase supp pour reste config ?
    - Ou, le master à l'init, donne un lien REST pour que ct récupère sa config
        - Il faut alors créer le CT avec un ID unique ?


Outils - MongoDB
::::::::::::::::

- Optimisations mongodb server: 
    https://github.com/square/cube/wiki/Scaling

- Pour ui de gestion mongo: ?
    - https://github.com/jwilder/mongodb-tools
    

Outils - PAAS
:::::::::::::

- voir le mini heroku ?

Outils - Fig ou Mastreo
:::::::::::::::::::::::

- Créer des bundles json pour fig ou mon outil de création ?
    - un par machine et/ou un par app ?

Outils - Scripts python
:::::::::::::::::::::::

- Comme rs-postfix, boucle avec config-from et reload/restart services
    - Piloté par le CT lui même sans contrôle du MASTER
    - Ne concerne que besoins à l'intérieur du CT
    
Outils - Consul
:::::::::::::::

- il faut scripts qui surveille event comme modif KV et reload config/app d'une app docker ?
    - comme script de rs-postfix, il faut un prog python principal qui surveille conf et génère config par tmpl puis start/reload services

- SE PREPARER comme si j'allais utiliser CONSUL avec 3 servers physiques
    - config json pour chaque services
    - install agent dans les ct
    
ARCH - Environnement de démo
----------------------------

- Mode test dans le client pour vérifier connection et auth
    - Tester les plusieurs modes selon dispo libs et firewall 

- Utilisation d'un serveur unique avec jeux de test unique ? ou un par démo ?

- Besoins démo:
    - Réception tcp policy par relais client ou direct
    - Accès dashboards stats


ARCH - Circus
-------------

Cirus sur l'hôte
::::::::::::::::

Cirus dans les contenaires
::::::::::::::::::::::::::

Cirus UI
::::::::

ARCH - Proxy - Reverse Proxy
----------------------------

- reverse proxy, plutot: http://blog.adminrezo.fr/2014/05/hipache-un-reverse-proxy-web/
    - créer pour dotcloud
    http://mitmproxy.org/doc/index.html
    
- https://github.com/bitly/google_auth_proxy
    - reverse proxy en Go avec auth google


ARCH - DNS
----------

- Testabilité solution python et mise au point requette
    - Voir surtout les doctest dans le code de dnslib
    - Utiliser un resolver python qui pointe vers le serveur DNS en cours de test
    - Tests des round robin, ...
    - Simuler les events Docker

- Bien distingué HOSTS et SERVICES:
    - hosts = une instance de CT
    - services = les services rendus par cette instance (mta, cache, ...)
        - Mettre au point nomenclature basé sur src _redis.tcp.... ou _cache.tcp...

- dns bind - haute dispo par DNS:
    http://www.zytrax.com/books/dns/ch9/rr.html
    
- Choix produits:
    - dnsmasq
    - bind
    - nsd ?
    - python dns server avec cache redis
    - powerdns

- https://github.com/johnae/docker-dnsmasq
    FROM: https://github.com/sequenceiq/docker-serf/blob/serf-only/Dockerfile
        FROM: https://github.com/sequenceiq/docker-pam/blob/master/ubuntu-14.04/Dockerfile
- https://github.com/mbentley/dockerfiles/tree/master/ubuntu/bind9
- https://github.com/majoux/docker-serveur/tree/master/bind
- https://github.com/jprjr/docker-ubuntu-stack/tree/master/dnsmasq
- https://github.com/mail-in-a-box/mailinabox/blob/master/setup/dns.sh

Services SRV
::::::::::::

- mta 
- mta_reply: retour smtpd du filtre
- filter: entrée amavis ou smtpd filter
- admin: app web
- mongodb: serveur mongo
- clamd: serveur clamav 

ARCH - Séparation par client
----------------------------

- Maitrise création db/users/role mongodb

- gérer db centralisé des clients et apikey,...

- création redis ? ajout d'une DB par client ? et d'un espace RAM ? ou un CT    
    

ARCH - Volumes externes
-----------------------

- VOIR plutot un volume data par client

- Droits sur les répertoires ?
- volume from ???
- Cluster entre plusieurs machines ?
- DB mongodb par client
- DB redis par client ?
- sous zone dns client1.radicalspam.local

::

    client1/
        postfix/
            etc/
            var/
        amavis/
            etc/        -> /opt/radicalspam/amavis/etc
            var/        -> /opt/radicalspam/amavis/var
        sa/
            etc/
            var/
        clamav/
            etc/
            var/

ARCH - Sécurité
---------------

- https://github.com/juancho088/SecureMongoEngine

- Besoins SSH
    - https://github.com/mbentley/dockerfiles/tree/master/ubuntu/openssh-server

ARCH - Sécurité - stunnel
:::::::::::::::::::::::::


ARCH - Sécurité - Serveurs de Réception REQUEST (zmq/tcp/udp/rest)
::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

- Inclure apikey dans le message pour simplifier implémentation de protocol d'auth !

- Bypass quand tunnel SSH ? et/ou identifié par ip fixe du client

ARCH - Sécurité - Site Web
::::::::::::::::::::::::::

- Banned IP
- Auth multiple ?
- SSL
- Fail2ban
    
ARCH - Sécurité - Firewall
::::::::::::::::::::::::::

- Besoin maitrise UFW !!! et ou shorewall ?
    - docs/products/ufw.rst
    - http://docs.ansible.com/ufw_module.html    

- iptables: 
    http://www.alsacreations.com/tuto/lire/622-Securite-firewall-iptables.html
    https://github.com/TheDutchSelection/captain/blob/master/docker/captain_iptables_discoverer/latest/files/scripts/run.sh

- fail2ban ?
    https://github.com/oussemos/fail2ban-dashboard/blob/master/home.py
    
ARCH - Sécurité - SSL
:::::::::::::::::::::

- https://help.ubuntu.com/14.04/serverguide/certificates-and-security.html#creating-a-self-signed-certificate

- Besoin d'un outil simple et/ou webservice pour générer des certs SSL

- Certificats SSL / pki ?
    - https://www.startssl.com/?app=1
    

ARCH - Sécurité - Tunnels SSH
:::::::::::::::::::::::::::::

- Gestion d'un magasin de key/cert SSH et test en ligne

- SSH plumbum ?

- Génération/Ouverture d'un tunnel SSH dans un contenair Docker
    https://github.com/andreasjansson/head-in-the-clouds/blob/f773a991a5bcbb9d7bcab253ed7497bf054e522e/headintheclouds/docker.py

- https://pypi.python.org/pypi/bgtunnel

- https://github.com/pahaz/sshtunnel

- Implémentation SSH tunnel de zmq

- Voir la même chose avec paramiko (client/server) sans ssh ?

- Si tunnel ssh inversé ouvert, pourquoi passer par ZMQ: le master peut utiliser fabric ou ansible ?

- Si le tunnel sert à ouvrir une connection vers un service SSH:
    - Install server ssh des 2 cotés

- Si le tunnel sert à ouvrir une connection vers un autre service comme HTTP ou Mongo:
    - Install server ssh que du coté MASTER: celui qui utilisera connection VERS MONGO par tunnel inversé
    
- pour inversé, il faut que client se connecte par http à serveur !::

    python -m SimpleHTTPServer 8000
    ssh -C -N -R 8000:127.0.0.1:8000 root@172.17.1.120
    > dans server qui dispose de l'accès inversé
    curl http://127.0.0.1:8000/index.html
    
Résumé des TESTS SSH docker - OK - (tunnel inversé)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

- Build d'un server SSH dans une image ubuntu et lancement auto (pas de mapping externe)::

    vi Dockerfile
    FROM ubuntu:14.04
    MAINTAINER Sven Dowideit <SvenDowideit@docker.com>
    RUN apt-get update && apt-get install -y openssh-server curl
    RUN mkdir /var/run/sshd
    RUN echo 'root:screencast' | chpasswd
    RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config
    # SSH login fix. Otherwise user is kicked off after login
    RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
    ENV NOTVISIBLE "in users profile"
    RUN echo "export VISIBLE=now" >> /etc/profile
    EXPOSE 22
    CMD ["/usr/sbin/sshd", "-D"]
    
    $ sudo docker build -t eg_sshd .
    
    # Voir version sans le -P - ne sert qu'à exposer vers un port aléatoire (trouver par sudo docker port test_sshd 22)
    $ sudo docker run -d --name test_sshd eg_sshd
    
    # Création d'un client:
    $ docker run -it --rm ubuntu:14.04 bash
    $ apt-get install --no-install-recommends ssh
    
    # Dans le client, lancement d'un server python sur port 8000
    $ python -m SimpleHTTPServer 8000
    
    # Dans le client, ouverture d'un tunnel inversé vers un server python sur le port 8000
    # Par une autre session
    ssh -C -N -R 8000:127.0.0.1:8000 root@172.17.1.120
    
    # Dans le server, utilisation du tunnel inversé
    $ curl http://127.0.0.1:8000
    
    

ARCH - Logs centralisé
----------------------

- http://www.fluentd.org/guides/recipes/syslog-influxdb
- Hekad / logstash / logcabin
- python udp (logcabin ou autre) -> logstash ? ou direct elasticsearch ?
- rsyslog dans chaque contenair avec UDP -> logstash ?
    - copie local des logs ?
- rsyslog dans chaque contenair avec UDP -> Rsyslog centralisé -> logstash
    - copie local des logs ?
- socket /dev/log ajouté dans chaque contenair ?
    - perte hostname ?
- volume-from ?
    - perte hostname ?
- IMPORTANT: pouvoir identifier chaque hostname

http://jasonwilder.com/blog/2014/03/17/docker-log-management-using-fluentd/
- Utiliser directement les fichier ID*-json.log dans les contenairs sur l'hote
- Ne fonctionne qu'avec les sortie stdout/stderr que peut afficher "docker logs CID"
    - Il faut que les applis envoi sur stdout ou alors syslog ?
- Une solution:
    RUN ln -sf /dev/stdout /var/log/nginx/access.log
    RUN ln -sf /dev/stderr /var/log/nginx/error.log

VM RS 3.5.4::
 
    $ vi /etc/rsyslog.d/50-default.conf
    *.*                             -/var/log/messages
    # commenter les mail*
    
    $ vi /etc/rsyslog.d/radicalspam.conf
    $AddUnixListenSocket /var/rs/dev/log
    $template MailLogFile,"/var/log/maillog-%$DAY%%$MONTH%%$YEAR%.log"
    mail.* -?MailLogFile


ARCH - Instances / IP / Ports
-----------------------------

- Simple RadicalSpam - Pas de cluster - 1 instance de chaque produit

- 1 domaine local par client

::

    MongoDB
        LISTEN:             ?:27017

    Redis
        LISTEN:             ?:6379

    rs-postfix (rs-postfix-deb)
        LISTEN:             ?:25
        > rs-policy-server  ?:13001
        > rs-smtpd-server   ?:14001
        > postgrey ?        ?:?
        > rs-admin ?        ?:12001 (auto config) ?
        > rs-agent-sent     : livraison de tous mail en direct par python smtp
        
    rs-agent-sent (lancé dans rs-postfix)

    rs-smtpd-server
        LISTEN:             ?:14001
        > MongoDB           ?:27017

    rs-policy-server
        LISTEN:             ?:13001
        > rs-admin          ?:12001
        
    rs-admin
        LISTEN:             ?:12001
        > MongoDB           ?:27017
        > Docker            /socket        
        > All               By docker

    rs-clamav (Partager volume clamav-data pour les signatures ?)
        LISTEN:             ?:3310

    rs-spamassassin (razor/pyzor/dcc)
        LISTEN:             ?:783
        > Redis             ?:6379 (bayes)
        
    rs-amavis ?
        LISTEN:             ?:10024, ... ? (all ports)
        > clamav            /socket ?
        > Redis             ?:6379
        > SpamAssassin      : NON, inclus
        > Quarantaine SMTP  : ?        

    rs-filter-agent
        > clamav            /socket ?
        > Redis             ?:6379
        > SpamAssassin      ?:783
        > rs-admin          ?:12001

        
ARCH - Supervision
------------------

- shinken car python et zmq

- Surveillance d'evènements ct/host

- Surveillance charge des instances

- Surveillance des changements de config
    - Ou inutile si process après modif config par UI web


ETUDE - Outils divers
---------------------

- Transformer des options non défini d'argparse en VAR YML
    - Paramètres positionnels non static comme ip=xxx devient une var yml var: xxx
    - retrouver le projet qui le faisait 

- commandes local et remote: 
    http://plumbum.readthedocs.org/en/latest/    

- http://amoffat.github.io/sh/

- https://github.com/kennethreitz/env
    - Permet de transformer en dict une série d'env avec un prefix comme REMOTERPC_xxx : {'xxx':'', ...}

- https://github.com/pypa/twine
    - Utilitaires pour pypi 

- http://sametmax.com/les-time-zones-en-python/ 

- essayer wheel:
    https://pip.pypa.io/en/latest/user_guide.html#create-an-installation-bundle-with-compiled-dependencies

- A utiliser dans mes setup.py:
    #https://github.com/pypa/warehouse/blob/master/warehouse/__about__.py

- APT Custom FR (mirroir FR pour les source APT)    
- SPF
- Dkim
- p0f
- clamav-unofficial-sigs
- Disclaimer
- ntp/timezone des contenairs
- upgrade distribution
- update d'un contenair
- Purge /tmp et autres dans les contenairs ?
- Environnement de dev/prod pour tests avant mise en production de mise à jour

ETUDE - Docker
--------------

- gestion de volumes docker (go): https://github.com/cpuguy83/docker-volumes

- ambassador with serf: http://www.centurylinklabs.com/linking-docker-containers-with-a-serf-ambassador/

- Vérifier conséquences des modifs sur images hérité docker
    - hérité toujours d'un tag et non de latest !!!
    
- forego: lanceur golang d'app docker
    https://github.com/ddollar/forego
    https://godist.herokuapp.com/projects/ddollar/forego/releases/current/linux-amd64/forego    
    
- allouer 1Go de RAM, 1 CPU et le port 9200::

    docker run -d -P -m 1g -c 1 -p 9200:9200 dockerfile/elasticsearch
    
- IMPORTANT: fermeture propre des tâches à l'arrêt du contenair
    - Cirus !
    - Trap 
        - https://github.com/urelx/dockerfiles/blob/master/centos6-postfix/start.sh 
        - http://www.christopher.compagnon.name/techno/shell-trap.html
        - http://guidespratiques.traduc.org/guides/lecture/Bash-Beginners-Guide/Bash-Beginners-Guide.html#sect_12_01
        - http://www.quennec.fr/gnulinux/programmation-shell-sous-gnulinux
    - Python atexit/signaux
    - python dans phusion

- voir:
    RUN echo "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc) main universe" > /etc/apt/sources.list
    $ lsb_release -sc
    trusty

- Utiliser depth: git clone --depth=1 https://github.com/angular/angular-seed.git <your-project-name>


- Gestion des tags::

    $ docker images
    radicalspam/orion-smtp          latest              82f5b3025823        About an hour ago   579.7 MB
    
    $ docker tag 82f5b3025823 radicalspam/orion-smtp:1.0

    $ docker images
    radicalspam/orion-smtp          latest              82f5b3025823        About an hour ago   579.7 MB
    radicalspam/orion-smtp          1.0                 82f5b3025823        About an hour ago   579.7 MB

- Capabilities (add/drop)

- restart auto::

    docker run --restart=on-failure:10 redis
    docker run --restart=always redis

- Démarrage auto des instances Docker

- Limitations de ressources RAM/CPU/DISK
    -m="": Memory limit (format: <number><optional unit>, where unit = b, k, m or g)
    -c=0 : CPU shares (relative weight)

- Quel ip source est vu dans un contenair quand ip externe ?
    - l'eth0 de l'HOTE !!! 37.187.249.195 pour rs mutualisé
    
- voir: docker --ip-masq=false (/etc/default/docker)

- Publication registry    
    
ETUDE - STATS - (influxdb/graphite/statds/grafana/kibana/collectd)
------------------------------------------------------------------

A Trier
:::::::

::

    oubli interface pour graphite: https://github.com/urbanairship/tessera
    https://github.com/dotcloud/collectd-graphite         
    https://github.com/tutumcloud/tutum-docker-grafana
    https://github.com/dockerana/dockerana/blob/master/components/grafana/Dockerfile
    https://github.com/bbinet/docker-grafana
    https://github.com/tutumcloud/tutum-docker-influxdb
    https://github.com/kamon-io/docker-grafana-influxdb
    https://gist.github.com/otoolep/3d5741e680bf76021f77
    https://github.com/ChristianKniep/docker-monster
        - stack complète (yum/supervisor/etcd): grafana, kibana, ES, statsd, logstash, nginx, graphite, diamond
        - des dashboard, ...
    https://github.com/vimeo/graphite-api-influxdb-docker
    https://github.com/kamon-io/docker-grafana-graphite
    https://github.com/mingfang/docker-grafana
    https://github.com/lincolnloop/docker-kibana    
    https://github.com/mozilla/metrics-graphics

    - Revoir shinken pour client graphite !
    - Idée pour envoi stats vers redis:
        https://github.com/seatgeek/circus-logstash/blob/master/circus_logstash/circus_logstash.py
    - graph rickshaw: https://github.com/circus-tent/circus-web/blob/master/circusweb/media/circus.js

    - idée psutil pour surveiller process et envoi stats:   
        https://github.com/crosbymichael/sysmonitor/blob/master/monitor.py

        https://developer.rackspace.com/blog/using-logstash-to-push-metrics-to-graphite/
        http://blog.geeksgonemad.com/2013/12/logstash-metrics-filter-and-graphite.html
        
    - statsd en nodejs à beaucoup de backend dont mongodb
        # Envoi de l'incrémentation d'une metric: (:1|c
        echo "production.login_service:1|c" | nc -w 1 -u statsd.example.com 8125

    - Voir facette avant grafana car ouvert à plusieurs sources: grafana aussi ?
    https://github.com/dockerana/dockerana
        https://github.com/dockerana/dockerana/blob/master/components/grafana/Dockerfile
    
- metric sur mongodb par nodejs: https://github.com/square/cube/wiki/Metrics

- Pourquoi "strip-components": tar xzvf /tmp/grafana-1.8.1.tar.gz --directory /grafana --strip-components 1

- Comment utiliser une instance ou select par client ?
    - db influxdb / elasticsearch diff par client
    - utiliser domain/ip pour router dans logstash ?

    
Stockage brut en dur: MongoDB
:::::::::::::::::::::::::::::

    Handler: policyng.handlers.async_me_record_handler.MongoEngineRecordHandler
        - Reçoit protocol
    Workers: policyng.workers.wsgi_app.worker

    - Mettre en prod un minimum pour record DB le mutualisé et peut être blois mx2 (par tunnel) (mx1 par tunnel inversé)
        - il faudra un jeu de donné pour la consolidation _identity
    
    - Voir comment récupérer data de la db ci dessus au fur et à mesure sans rien perdre ni modifier
        - Export json/rest/...          
    
    - Maitriser la génération des timestamp en trichant pour fixtures
        https://github.com/influxdb/influxdb-python/blob/master/examples/tutorial_server_data.py
            - Parfait pour envoyer des datas avec dates maitrisés
        Diamond/Diamond-master/src/diamond/handler/zmq_pubsub.py    
        https://github.com/studio-ousia/gevent-statsd-mock
        http://metrics20.org/implementations/
            https://github.com/vimeo/graph-explorer/tree/master/graph_explorer/structured_metrics
        http://agiliq.com/demo/graphos/tutorial/
            
    - Travailler sur l'exploitation interne des stats pour l'instant avec socketio/rickshaw/flot/chartjs
                
    - Faire un worker ou un convert stats au format influxDB
    
    - Faire un format de sortie pour ES pour utiliser kibana qui est plus complet

facette
:::::::
    
ElasticSearch / Kibana / Logstash
:::::::::::::::::::::::::::::::::

TODO::


    https://github.com/elasticsearch/kibana/blob/v3.1.2/sample/nginx.conf
    https://github.com/elasticsearch/kibana/blob/v3.1.2/sample/filtered-alias-example/nginx.conf

    - Maitrise kibana:
        - ou logstash avec pattern simple sur ligne amavis Passed seulement ?
        - index manuellement des données dans elastic
        - requette manuel sur kibana
    
    OU
    - meilleur maitrise par logcabin ou bucky ou rs-logsd ?

    - Utiliser git pour install/update ?
        - le git server est sur soyoustart
    - Rebuild all avec les corrections
        - run avec limite RAM pour elasticsearch et logstash
    - Sortie debug ruby vers fichier pour logstash
    - Requettes py et/ou curl sur elastic pour comprendre
    - Templates elasticsearch
    - Config dashboard kibana
        https://github.com/vspiewak/mag-programmez-2014/blob/master/dashboard.json
        https://github.com/vspiewak/elk-monitoring/blob/master/system/dashboard.collectd.json
    - Sécuriser accès à elasticsearch/logstash/kibana
    
    - Metric graphite pendant l'analyse logstash:
        https://blog.bearstech.com/2013/12/logstash.html
    
    - Page avec les liens vers les apps et plugins elastic
        http://37.187.249.195:9200/_plugin/kopf/
        http://37.187.249.195:9200/_plugin/HQ/
        http://37.187.249.195:9200/_plugin/head/
        http://37.187.249.195:9200/_plugin/marvel/
        http://37.187.249.195:9200/_template/
        http://37.187.249.195/index.html#/dashboard/file/logstash.json
                                        #/dashboard/script/logstash.js
    
    docker start elasticsearch
    docker start logstash
    docker start kibana

    docker stop kibana
    docker stop logstash
    docker stop elasticsearch

- https://www.digitalocean.com/community/tutorials/how-to-use-logstash-and-kibana-to-centralize-and-visualize-logs-on-ubuntu-14-04
    - nginx, ssl, ...
    echo 'deb http://packages.elasticsearch.org/logstash/1.4/debian stable main' | sudo tee /etc/apt/sources.list.d/logstash.list
    echo 'deb http://packages.elasticsearch.org/logstashforwarder/debian stable main' | sudo tee /etc/apt/sources.list.d/logstashforwarder.list

- https://github.com/ChristianKniep/docker-elk
    - ATTENTION: fedora !
    - sshd, diamond, StatsD, logstash, elasticsearch, kibana, nginx
    - zeromq

- Input logstash: 
    - collectd: http://logstash.net/docs/1.4.2/inputs/collectd
           - http://logstash.net/docs/1.4.2/codecs/collectd
           - Via Plugin network de collectd : port 25826
    - elasticsearch: http://logstash.net/docs/1.4.2/inputs/elasticsearch
    - file: http://logstash.net/docs/1.4.2/inputs/file
    - graphite: http://logstash.net/docs/1.4.2/inputs/graphite
        - http://logstash.net/docs/1.4.2/codecs/graphite
    - imap: http://logstash.net/docs/1.4.2/inputs/imap
    - redis: http://logstash.net/docs/1.4.2/inputs/redis
    - syslog: http://logstash.net/docs/1.4.2/inputs/syslog
    - tcp/udp
    - websocket: http://logstash.net/docs/1.4.2/inputs/websocket
    - zeromq: http://logstash.net/docs/1.4.2/inputs/zeromq
    
- Output logstash:
    - influxdb: https://github.com/elasticsearch/logstash-contrib/blob/master/lib/logstash/outputs/influxdb.rb
        - port 8086
        - Non documenté    
    - graphite: http://logstash.net/docs/1.4.2/outputs/graphite
        - carbon 2003 (tcp ou udp) ?
        - Possible influxdb !!!    
    - mongodb: http://logstash.net/docs/1.4.2/outputs/mongodb
    - redis: http://logstash.net/docs/1.4.2/outputs/redis
    - statds: http://logstash.net/docs/1.4.2/outputs/statsd
    - websocket
    - zeromq
    
Config collectd
:::::::::::::::

- Voir par collectd -> REDIS et REDIS -> logstash
    - https://beingasysadmin.wordpress.com/category/logstash/

- https://gist.github.com/untergeek/ab85cb86a9bf39f1fc6d    

::

    export LOGSTASH_ADDR=127.0.0.1
    export LOGSTASH_PORT_COLLECTD=25826
    
    cat > /etc/collectd/collectd.conf.d/logstash.conf << EOF
    <Plugin network>
        <Server "${LOGSTASH_ADDR}" "${LOGSTASH_PORT_COLLECTD}">
        </Server>
    </Plugin>
    EOF
    
    vi /etc/collectd/collectd.conf.d/logstash.conf
    LoadPlugin network
    <Plugin network>
        <Server "127.0.0.1" "25826">
        </Server>
    </Plugin>
    
    {
                   "host" => "ns339295.ip-37-187-249.eu",
             "@timestamp" => "2014-11-22T11:07:39.634Z",
                 "plugin" => "disk",
        "plugin_instance" => "sdb2",
          "collectd_type" => "disk_octets",
                   "read" => 53167104,
                  "write" => 7871987712,
               "@version" => "1",
                   "type" => "collectd"
    }
    
InfluxDB / Grafana
::::::::::::::::::

- influxdb: 
    - fournir -h HOSTNAME pour le cluster future
    - pour la création de db à l'avance!!! pb car influxdb doit être lancé
    - ssl
    - Changer le compte root par défaut ou au moins le pass !!!

- https://github.com/grafana/grafana-plugins

- http://vincent.composieux.fr/article/grafana-monitor-metrics-collected-by-collectd-into-influxdb
    - collecd -> grafana par plugin network
    - Non, par un proxy nodejs: https://github.com/hoonmin/influxdb-collectd-proxy.git

- Stats collectd et/ou diamond
    - https://github.com/nacyot/docker-logs/tree/master/diamond

- Reception de stats graphite

Graphite API
::::::::::::

- https://registry.hub.docker.com/u/qnib/monster/
    - https://github.com/ChristianKniep/docker-monster
    - yum !!!
    - carbon,statsd,grafana & elk

- https://github.com/ChristianKniep/docker-graphite-api
    - Remplace l'api web pour extraction de graphite
    
- https://registry.hub.docker.com/u/brutasse/graphite-api/dockerfile/
    - Cyanite = backend cassandra pour graphite    

- https://github.com/graphite-ng/carbon-relay-ng
    - Pour avoir un server carbon en Go avec interface web intégré

Facette
:::::::


Statsd
::::::

- http://www.symantec.com/connect/blogs/metrics-cocktail-statsdinfluxdbgrafana

::

    # A tester
    sudo apt-get install nodejs
    cd /opt
    sudo git clone https://github.com/etsy/statsd.git
    cd statsd
    apt-get install npm
    npm install statsd-influxdb-backend -d    

fnordmetric (ruby)
::::::::::::::::::

http://fnordmetric.io/documentation/classic_running_fm/

::

    Installation
        apt-get install ruby1.9.1   
        gem install fnordmetric
    
            Building native extensions.  This could take a while...
            ERROR:  Error installing fnordmetric:
            ERROR: Failed to build gem native extension.
            /usr/bin/ruby1.9.1 extconf.rb
            /usr/lib/ruby/1.9.1/rubygems/custom_require.rb:36:in `require': cannot load such file -- mkmf (LoadError)
            from /usr/lib/ruby/1.9.1/rubygems/custom_require.rb:36:in `require'
            from extconf.rb:2:in `<main>'
            Gem files will remain installed in /var/lib/gems/1.9.1/gems/eventmachine-1.0.3 for inspection.
            Results logged to /var/lib/gems/1.9.1/gems/eventmachine-1.0.3/ext/gem_make.out
        
    
        #my_fnordmetric.rb
        require "fnordmetric"
    
        FnordMetric.namespace :myapp do
          # your configuration here...
        end
    
        #start a web server on port 4242, a tcp acceptor on port 1337 and a worker
        FnordMetric.standalone
        
        FnordMetric.options = {
          :redis_url => "redis://my_redis_server.domain.com:6379"
        }   
        
        #FnordMetric::Web.new(:port => 4242)
        #FnordMetric::Acceptor.new(:protocol => :tcp, :port => 2323)
        #FnordMetric::Worker.new
    
    $ ruby my_fnordmetric.rb
    
        
ETUDE - OUTILS - Redis
----------------------

- Travailler sur Redis car utilisable pour beaucoup de choses !!!
    - 1. Cache pour postgrey et autres besoins
    - 2. Stats avec outils se basants sur redis
    - 3. Tasks queue !
    - 4. Session
    - 5. Limitation basé sur durée comme nombre de mail/spam par heures
    - 6. DNS cache

    - Client redis py direct pour cache et voir si api ok ex: werkzeurg ou flask
    - Install redis static par fabric

- Persistence
- DB par client ?

ETUDE - OUTILS - Docker Registry
--------------------------------

- Register de contenair docker privés
    - https://github.com/Deliverous/docker-standalone-registry/blob/master/Dockerfile

IDEE - rs-postqueue-mongo
-------------------------

- Queue pour postfix
- Stocké en before filter SMTP
- Commandes en lignes pour remplacer postqueue/mailq/...

PRODUIT - POLICY / POSTFIX
--------------------------

- IMPORTANT postfix/policy:
    - Dans config policy postfix, par sécurité, mettre un warn_if_reject devant 
    - Utiliser un local_settings qui appel default_settings et surcharge ce qu'il veut
    - Pour ceux qui ne veulent pas utiliser policy en frontal
        - Un postfix light ou un proxy smtp comme ci-dessous qui se branche après réception du SMTP frontal
            - Attention perte ip/helo d'origine si pas postfix ou si postfix < 2.1 (xforward)
    - Pour ceux qui n'ont pas postfix:
        - Proxy SMTP qui analyse les données essentiel du mail et envoi par policy-relay

- policy-ng et zmq:

    - country: ne suffira pas pour geo localisation : il faut identifier avec geoip les coordonnées
    
    - en plus des stats, envoyer infos vers ES pour search 
    
    - Faire des aggrégations de GenericStats ? mais dure de découper le name ? regexp ?

    - il faut valider la version postfix géré par la structure db car champs en plus !!!
        - ou champs supp dans un dict
        - ou supp values dans protocol
    
    - Déploiement docker pour test avec mails mutualisé

    - !! fixtures: charger un fichier json au démarrage ou à la demande : important pour policy (group/domain/...)
    - Ajout petite api rest pour ajout/list domain/mynetwork: agnostic ?
    - données mini pour qualifier in/out/relay et affectation group ou mini plugin dédié
        - ou rester version simple pour mode stats: prendre dans la config externe + options et partagé avec workers/plugins
    
    - EVITER PolicySession Mongo, direct Policy ?
        
    - sortie au format logstash, influxdb, graphite pour être large

    - Faire un push systématique à la réception d'une entrée ? ou utiliser signal 
    - Permettre à des plugins de s'abonner par sub
    - ou utiliser zmq pour écrire dans REDIS

- En filter pure où postfix attend réponse:
    - Par handler REST -> app web -> record DB / use manager > return actions
    - Par local handler -> use manager (load/save/search) -> use filter -> return actions

- Pense que au lieu de cherche à utiliser policy pour le filtrage ou l'envoi de stats:
    - certains peuvent préférer simplement se brancher à une api (rest/zmq/db/...) pour récupérer les données bruts
    - idéal: signals récupère stats et envoi à queue zmq interne pour record ou distribution

- Les filters, ajoutent des tags et augmente le score 
    - Utiliser plutot verrou que queue ?
    - score à synchroniser ! ? par une class qui implémente __add__ et un lock pour faire un ++ ?
    - La stratégie analyse les tags et score et décide
        - il faut charger la stratégie
        - l'appliquer à chaque filter ?
        
- oublie ajout ip address postfix et identity policy server (hostname ?)

- Ajout param dans Plugin pour définir si accès externe par le plugin (db, dns, ...)
        
- Faire des tâches/plugins d'arrière plan:
    - faire un add_task pour ajouter à la liste des tâches par timer
        - scheduler pour avoir une durée diff d'execution
    - Recherches whois/dns qui vont en même temps alimenter le cache DNS pour le filter 
    - Alimenter cache DDOS pour mesures

- commencer à rassembler filters nécessaire: nofqdn, spf, ...
    postmaster, abuse, SPOOFING
    sasl / ssl sender ?
    Relocated - Rejet 5xx relocated avec nouvel email du destinataire - seulement si externe
    check (DB/LDAP/RADIUS) - not_listed_recipient
    check BL ip/country/domain/email/helo < selon enable_bl_xxx
    filter liste de réputation pour modérer le score ?
    check DOS - nombre de messages rejetés (SMTP 5xx)
    >>> DDOS nombre de destinataires pour même message
    check DOS - nombre de mail dans la dernière heure (jour/...) : session simultané ?
    check DOS - pourcentage de SPAM/VIRUS/... dans quel délai ? cumuler TOUT ?
        - Info, pas encore là mais gérable
        - Faire aussi sur nombre de reject pour ip/sender/recipient

- fournir aux plugins un resolver dns

- Pour régler pb pyinstaller, installer peut être policy par setup avant transformation

- peewee: psycopg2 (voir version gevent), mysql? (voir doc django et peewee)

    


PRODUIT - REMOTE-RPC
--------------------

- DOC:
    > Les vues suivantes fonctionnent en REST et en HTML
    http://127.0.0.1:8080/remote/status
    http://127.0.0.1:8080/remote/status/79b16e6f96651f5478bc4c94c8f4e3e828f4b592a23851a7c0248a466a05ff08
    http://127.0.0.1:8080/remote/services/79b16e6f96651f5478bc4c94c8f4e3e828f4b592a23851a7c0248a466a05ff08/get_sysinfo
    
- TODO:

    - Considérer le worker WSGI et/ou server Socketio comme des workers à ajouter dynamiquement !!!!

    - NE pas oublier les besoins de reporting (tableaux/valeurs/export pdf)
    
    - Chaque worker (consomateur) doit pouvoir être lancé en ligne de commande, hors remote-rpc
        - Attention inproc: voir ipc ?
    
    - EN PREMIER:
        - Comme je ne connais pas à l'avance les services générateur de stats:
            - Il faut un phase de transformation variable
            - Le producteur de stats doit devenir plus intelligent: avec son propre setup(app)
            - Mapping/Filter/Transformation/Aggrégation ???: beaucoup de travail ?
        - Bien gérer transformation stats par Worker stats qui est le producteur !!!
            - Doit pouvoir renvoyer un dict pour chaque stats ? ou envoi brut et reste à la charge du consomatteur ?
        - Prévoir stats par app en plus de par agent (apps.postfix....) / apps.postfix.[SERVER]...
        - Prévoir les tops par aggrégation
    
    - Mettre en oeuvre une mini architecture sur les serveurs pour avoir des données complètes:
        - C LA qu'il faudrait le control master de création CT docker !
            - Surveiller les events !!!!
        - Lancer plusieurs vm agent
        - Lancer 1 ou 2 master
        - 1 influxdb + 1 grafana
        - Voir collect ou diamond ? ou tous ce qui peut faire remonter des stats
        - Voir aussi le carbon relay ng ou un autre intermédiaire qui sécurisé
        - LAISSER peut être graphite pour écrire directement en influxdb qui est plus complet ?
            - En profiter pour générer/ajouter des tags dans une liste pour réutiliser dans les where= de grafana
    - Carbon ou autre: penser à un serveur relais de consolidation/aggrégation
    - Voir comment sécuriser les flux et détecter les manques/retard
        - Revoir le produit qui détectait les écarts ?
    - Apports statsd ?

    - Utiliser setup aussi pour des actions before start comme le load/save des agents
        - Le save basé plutot sur signal
        - En before, oui, le load / purge / ...
    
    - Utiliser setup coté agent pour le chargement de services ?
    
    - setup aussi pour chargement de blueprint ou autres modification app flask ?

    - Pouvoir facilement paramétrer les interval - voir scheduler ou mettre en task queue ?
    - Pouvoir changer la destination des stats
    
    - modifier socketio pour utiliser un seul namespace au lieu de /stats et /agent, use emit(agent.stats) ou emit(agent.state)
    
    - Revoir ma façon d'assembler un prog dans un runner: beaucoup plus clair chez dnsrest
    
    - Fournir la configuration aux applications distantes
    - record dns des agents enregistrés 
    - Gérer des contenair docker:
        - Permettrait aussi de créer dynamiquement une instance d'agent ?
    
    - STATS: comment déléguer pour choix futures:
        - Ne pas perdre de stats
        - Multi-Master: qui fait quoi ?
        - Record MongoDB et ou Redis
            - Faire ensuite worker pour gérer datas et send stats
        - Voir si envoi direct graphite d'influxDB, risque de perte ?
        - Voir carbon-relay ng Go
    - Rendre optionnel la phase de register si création agent gérer par master ?
    - Fournir un beau dashboard et des vues d'affichage/gestion des services distants
        - role de socketio ou websocket ?
        - utiliser mini graph dans les pavés de chaque agent
    - Fournir une api pour être utilisable hors web
    - msgpack
    - Gérer des serveurs/services distants par RPC: Il faudrait qu'un agent ne réponde qu'au master en cours ?
    - bouton update du status + last update date affiché
    - Comme sentry, faire une page d'état et config de l'app:
        http://5.196.195.66/manage/status/
            
    - Fournir des services prêt à l'usage comme psutil, ...
        - Voir espace de nom pour chaque classe de services ajoutés
        - il faut maitriser __getattr__ ou autre pour mapper les demandes
        - Revoir idée du ProxyResult pour intercepter et normaliser les données renvoyés
        - Services: ansible ?, test connect, envoi de mail, ... nagios ?
    - Features:
        - Intégrer un beau dashboard simple et alimenter par websocket: Stats des agents, doivent venir de psutil
        - Stats ou compteur pour l'état des connections websocket en cours
    
    - Bien référencer ce qui doit être fait à la fermeture de l'application
    - Profiter aussi d'un worker/task externe type redis qui limite l'utilisation RAM du MASTER !!!
        - Implémentation autonome: tasks gérer par un worker zmq
        - Implémentation redis, record tasks dans redis et traitement par rq ou mrq ?
    - Utiliser setup(app) pour charger des workers ?                
    - Régler pb flask sur l'encodage des templates !!!
    - Revoir les lib d'outil JS pour faciliter manipulation datas
    - Ne pas cherche l'auto doc des api rest, utiliser template
    
- Sérialisation:
    - http://www.blosc.org/ (python https://github.com/Blosc/python-blosc)
    - compression https://github.com/Blosc/bloscpack 
    - bson

- Packaging:
    Utiliser tous mes développement tools rslib pour créer des services
    Englobé dans une app WEB Flask (blueprint) pour réutilisation
    Runner pour version autonome avec app Flask() et server WSGI
    Implémentation/Extension de zmqrpc-ng-api pour les particularités de remote-rpc

    RPC inversé: le master (client) contact les agents (server)
        - Les agents (server) sont lancé avec des services consommés par les clients (masters)
        - L'enregistrement de l'agent peut se faire par pré-requette REST OU par api ou par config
    
    RPC normal: les agents (client) contacte un ou plusieurs server master
        - Veut dire qu'il faut lancer un master avec des services qui seront consommés par les agents
        - Utilise cycle si les agents peuvent se connecter à n'importe quel master
    SSH:
        - Nécessite échange de clé ou implémenter un serveur SSH dans le MASTER
        - L'agent -> register http -> récupère clé ssh et infos -> lance un tunnel inversé -> averti par http le master que prêt pour tunnel
            - Ou un yield dans la vue http qui renvoi les infos selon les étapes

- Version psdash:
    - Faire d'abord un fork et pull request de psdash pour proposer une réorganisation du code ?
    - Récupérer toute la partie web de psdash et ajouter des graphiques
    - Le faire comme un addons optionnel à remote-rpc:
        - partie web de psdash dans un blueprint/app à intégrer
        - partie service psutil / service logs / ...

- rs-admin OU autre master:         
    - rs-admin lance un server WSGI et lance des clients RPC vers les agents enregistrés !!! ?
    - rs-admin doit pouvoir prendre le controle par RPC et l'api docker des CT qui se sont enregistrés
        https://github.com/phensley/docker-dns-rest/tree/master/dnsrest
    - rs-admin fournit une interface web pour visualiser l'état des machines/services
    - Toutes les commandes concernant les services sont lancés à partir de rs-admin
    - rs-admin doit être clusterisé
    - rs-admin doit pouvoir créer par l'api docker un CT d'après une image qui contient l'agent remote
    - rs-admin centralise les stats récoltés par docker/rpc/services et les utilisent ou les retransmets
    - Tester la disponibilité des services annoncés par les agents ? (smtp 25, ...)
    - API: 
        - register agent / agent list / ...
    - Auth à définir !!!
                    
- Process pour enlever une machine ?


PRODUIT - FLASK-AUTH
--------------------

- utiliser models Group/... de policy ?

- Auth interne et voir LDAP
        
- Terminer module flask-auth-me/peewee autonome
    - basé sur flask-security+social+ldap en mongoengine ET peewee
    - Peut être le même setup(app) que policy pour ajout de fonctionnalités

- auth social:
    - boutons super: http://theaqua.github.io/BrandButtons/             
    - python social trop gros pour mes besoins ?
    - ok: auth sur 1 app, ok pour les autres mais pas très propre
    - view flask admin pour visualiser/gérer user et infos socials
    - testabilité: python-social (httpretty)
    - form/model pour gérer activation + settings de chaque auth ?
    - settings pour vérifier ceux disponibles (avec leur clé/secret dans setting) des autres
    - template doit dérouler que ceux dispo et ACTIF
    - apport libsaas pour python-auth-social ?
    - diff flask-security-social/python-auth-social ?
    
    
IDEES
-----

- Idée pour améliorer le filtrage:
    - Ouvrir des comptes pièges sur gmail/yahoo/... et les diffuser
    - Batch imap/pop pour récupérer ces mails, les analyser et extraires des infos, en particulier CEUX déjà qualifiés comme SPAM
    
A VOIR PLUS TARD - Produits RS
------------------------------

rs-filter
:::::::::

- app web mini pour gérer mails mise en DB mongo par rs-smtpd-server
    - Tableau pour parcourir les mails
    - Gestion de queue (status par mail)
    - Interface REST
    - fonction d'envoi smtp
    - flag pour signalement spam/ham
    - extraction received/sender/... pour W/B List
    - Interprétation:
        - lib email std python
        - flanker
        - ripmime et ensuite lib email ou flanker
    - Agent qui selon flag lance actiob: (envoi smtp/scan virus/scan spam/add list/...)


rs-admin
::::::::

- Idéalement, 1 instance par client (groupe de domaine) DONC relié à une DB Mongodb par client ?

rs-postfix
::::::::::

- IL FAUT peut être que postfix soit dans un contenair lancé avec --net host ???
- Utilisation memcached pour postfix ?

- Comment éviter ou faut t'il 2 ip (lan/wan)::

    content_filter=

    smtpd_recipient_restrictions = ..., check_recipient_access hash:/addons/postfix/etc/local-filters
        domain.com  FILTER smtp-amavis:[127.0.0.1]:10031 #IN

    smtpd_sender_restrictions = ..., check_sender_access hash:/addons/postfix/etc/local-filters
        domain.com  FILTER smtp-amavis:[127.0.0.1]:10032 #OUT - Pas de filtrage spam     


- postscreen ?

- https://github.com/cpuguy83/docker-mail/blob/master/Dockerfile
- https://github.com/nirnanaaa/docker-postfix-dovecot
- https://github.com/catatnight/docker-postfix/blob/master/assets/install.sh
    - postconf -M submission/inet : edition master.cf
- SSL: 
    - https://github.com/lukas-hetzenecker/docker-postfix/blob/master/assets/install.sh
    - https://github.com/jprjr/docker-ubuntu-stack/blob/master/postfix/postfix.setup
    - https://github.com/mail-in-a-box/mailinabox/blob/master/setup/mail-postfix.sh
    - apt-get install ca-certificates
    - https://github.com/mail-in-a-box/mailinabox/blob/master/setup/ssl.sh

- test smtp postfix command smtp-sink: http://www.postfix.org/smtp-sink.1.html

- http://www.starbridge.org/spip/spip.php?article12
- http://www.placenet.fr/2012/08/19/configuration-de-postfix-smtp-smtpd-sasl-dovecot-pop3-imap-postfixadmin-roundcube-sous-debian-wheezy-utilisant-postgresql/
- http://www.placenet.fr/2010/10/17/deux-instances-pour-postfix/
- http://blog.jotheroot.fr/?p=26
- http://blog.valouille.fr/2014/04/commandes-utiles-pour-postfix/
- http://blog.valouille.fr/2013/02/voir-quelles-ip-generent-ou-ont-genere-le-plus-de-connexions/
- http://www.opendoc.net/solutions/comment-installer-configurer-serveur-log-syslog-ng

rs-filter-agent
:::::::::::::::

- Partagé un volume avec rs-clamav et rs-spamassassin pour éviter de décompresser 2 fois le mail à analysé ?
    - Peut être pas valable avec Spamd/Clamd par TCP ?
    
- lance analyse mail, livraison(non), envoi mail turing    
    
rs-amavis
:::::::::

    
Amavis vs RS-Filter
!!!!!!!!!!!!!!!!!!!

- Peu de valeur ajouté avec amavis mais plus d'expérience et pb encodage réglé
- RS Filter, Innovation d'un stockage Mongodb + réplication
- RS Filter, monté en charge: N instances clamav/SA/... selon besoin
        
    
rs-spamassassin
:::::::::::::::

- Compilation rules
- Updates

- https://github.com/mail-in-a-box/mailinabox/blob/master/setup/spamassassin.sh
- https://github.com/jprjr/docker-ubuntu-stack/tree/master/spamassassin

::

    docker run -it --rm --link redis1:redis -p 793:793 -v /root/docker/r-compil/postfix:/DATA radicalspam/addons-postfix:1.1
    
rs-clamav
:::::::::

- Configuration spécifique par groupe de domaines (client)
- Gestion freshclam par daemon ou cron ?
    - Si signatures partagé, il faut un script capable de prévenir TOUTES les instances clamav     
    
- https://registry.hub.docker.com/u/y0ug/irma-probe-clamav/dockerfile/


ETUDE - OUTILS - Backup / Maintenance
-------------------------------------

- Contenair data

- Backup : produit un backup.tar.gz à l'endroit où la commande est lancé::

    docker run --rm --volumes-from postfix1:ro -v $(pwd):/backup ubuntu tar -czf /backup/backup.tar.gz /var/spool/postfix


SMTPD - Voir si ces techniques permettrait d'analyser et garder une trace des hash des fichiers dans les mails
--------------------------------------------------------------------------------------------------------------

::

    NSRL: https://github.com/blacktop/docker-nsrl
        pybloomfilter
    https://pypi.python.org/pypi/shadow-server-api/1.0.4
    https://pypi.python.org/pypi/shadowdns/0.1.3
        ShadowDNS creates a DNS server at localhost.
        https://github.com/clowwindy/shadowdns
        A DNS forwarder using Shadowsocks as the server: requis shadowsocks

    https://github.com/blacktop/shadow-server-api
    https://www.shadowserver.org/wiki/
    http://bin-test.shadowserver.org/
    http://www.nsrl.nist.gov/
    http://ssdeep.sourceforge.net/usage.html
    
        

ESSAI - Proxy shadowsocks
-------------------------

.. note::

    C'est un proxy sock, pas nativement un proxy http

- https://github.com/clowwindy/shadowsocks
- A fast tunnel proxy that helps you bypass firewalls

    
::

    pip install shadowsocks
    ssserver -p 8000 -k password -m rc4-md5
    
    # background:
    ssserver -p 8000 -k password -m rc4-md5 -d start
    ssserver -p 8000 -k password -m rc4-md5 -d stop 
    
    # optimisations:
    https://github.com/shadowsocks/shadowsocks/wiki/Optimizing-Shadowsocks
    
    # config:
    # /etc/shadowsocks.json
    {
        "server":"my_server_ip",
        "server_port":8388,
        "local_address": "127.0.0.1",
        "local_port":1080,
        "password":"mypassword",
        "timeout":300,
        "method":"aes-256-cfb",
        "fast_open": false
    }
    
    # plusieurs user:
    {
        "server": "0.0.0.0",
        "server_port":80,
        "local_address": "127.0.0.1",
        "local_port":8080,
        "port_password": {
            "8381": "foobar1",
            "8382": "foobar2",
            "8383": "foobar3",
            "8384": "foobar4"
        },
        "timeout": 300,
        "method": "aes-256-cfb"
    }        
               
    

TODO -  Contenair de test pour envoi de mail
--------------------------------------------

- parcourir les mails d'un répertoire
- envoi postfix pour filter et policy
- envoi direct filter


TODO - Essayer ce new pypi privé
--------------------------------

::

        pip install papaye
        wget https://raw.githubusercontent.com/rcommande/papaye/master/production.ini
        papaye_init production.ini
        pserve production.ini
        
        #pip install -i http://localhost:6543/simple numpy
        
         ~/pip.conf
        [install]
        index-url = http://localhost:6543/simple         
        
        [distutils]
        index-servers =
            papaye

        [papaye]
        username: <admin>
        password: <password>
        repository: http://localhost:6543/simple        
        
        # upload
        cd /chemin/vers/votre/module
        python setup.py sdist upload -v -r papaye
    
Domaines A acheter
==================

policy-ng
---------

::

    postfix policy new generation = postfix politique nouvelle génération = ppng
    
    postfix-policy-ng    : ok (prendre le .io) : ok rien dans github
    policy-ng: ok  : ok rien dans github
    
    politique de filtrage postfix nouvelle génération = filtering policy postfix new generation = fpp-ng

    open policy filter for postfix smtp = filtre de stratégie ouverte de postfix smtp = opfps
    filtre de stratégie ouvert de postfix smtp = open policy filter postfix smtp = opfps

    postfix filter policy = politique de filtrage postfix = pfp (73 repos github)
    politique de filtrage postfix = filtering policy postfix = fpp (180 repos github)
    open postfix policy filtering = filtrage de la politique de postfix ouverte = oppf (opp = 978 repo/ oppf = 3)
    
    politique de filtrage postfix ouverte = filtering policy open postfix = fpop (8 repos 0 avec le même nom)
    
        libres: .io
        pris: .fr (musique redirect), .com (chine redirect)
              .org (religion), .net (chine)
              
    open policy of filtering postfix = politique ouverte de filtrage postfix = opfp
        libres: .fr, .io
        pris: .com, .net, .org 
        
    politique de filtrage smtp postfix = Postfix SMTP filtering policy = psfp
    Postfix SMTP filtering policy = La politique de filtrage SMTP de Postfix
    
    SMTP Postfix filtering policy = Politique de filtrage SMTP Postfix = spfp
    
    Postfix SMTP Access Policy Delegation = Délégation politique d'accès SMTP Postfix = psapd
              
    open filtering postfix policy = politique de postfix de filtrage ouverte    
    politique ouverte de filtrage postfix = open policy filtering postfix = opfp
    open policy filtering postfix = politique ouverte filtrage postfix = opfp
    open policy of filtering postfix = politique ouverte de filtrage postfix = opofp
    open policy of postfix filtering = politique d'ouverture du filtrage de postfix 
    politique d'ouverture du filtrage par postfix = by postfix filtering policy of opening (bpfpo)


    