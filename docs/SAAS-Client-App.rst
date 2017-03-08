Client App SAAS
===============

*      | DEFAULT              | admin@localhost.net                      | superadmin
*      | abakus               | admin@abakus.fr                          | admin
*      | gcr                  | admin@gcrfrance.com                      | admin
*      | brasseurs            | admin@brasseurs-de-france.com            | admin
*      | cias                 | admin@ciasdublaisois.fr                  | admin
*      | srault               | admin@radical-spam.org                   | admin
*      | ma                   | admin@mail-analytics.io                  | admin
*      | rs                   | admin@radical-spam.fr                    | admin
*      | blois                | admin@ville-blois.fr                     | admin
*      | geometre             | admin@dupouy-flamencourt.geometre-expert.fr | admin

Que doit t'on trouver dans l'espace client
------------------------------------------

- Formulaire simplifier pour ajout domain/mynetwork qui permettent de déterminer IN/OUT/RELAY !!!
    - Utiliser api falcon + angular ?

- Settings !
    - Timezone global et pour chaque serveur envoyant des données (ou gérer au départ) non, pytz utc !
    - Langue
    - thème (plus tard)
    - Auth ?

- Lien dashboard grafana vers DB influxDB pour ce groupe

- Lien dashboard kibana vers DB ES pour ce groupe

- Lien dashboard facette ? graphite ?

- Accès aux logs ?    

- Un dashboard light ?
    - Nombre d'entrée policy total
    - Autres stats de cumul par années/mois/jour et voir par host
    - aggrégation pour générer des tops
    
- API REST ?    

- Options export/save dropbox/s3/...

Que mettre derrière l'espace client
-----------------------------------

- CT nginx pour le client si j'arrive à proxy !!!

- MongoDB Mutualisé/Clusterisé avec une DB par client
    - Donner accès en priorité aux SLAVE en lectures pour le client

- InfluxDB Mutualisé/Clusterisé avec une DB par client

- ES Mutualisé/Clusterisé avec un index par client

- Pour grafana/kibana: plus compliqué !
    - Problème CORS
    - DB par client = config.js ?
    - OU générer l'interface à la demande ? et utiliser un nginx mutualisé ?
    - Le client peut modifier son dashboard ?


SAAS - SITE - CLIENT APP - Dashboard et dashlets
------------------------------------------------
   
- Idées widget pour dashboard ou autre: 
    - https://github.com/dpgaspar/Flask-AppBuilder/blob/master/flask_appbuilder/widgets.py
    - Authentication support for OpenID, Database, LDAP and REMOTE_USER environ 
    - SQLAlchemy, multiple database support: sqlite, MySQL, ORACLE, MSSQL, DB2 
    - Bootstrap 3.1.1 CSS and js, with Select2 and DatePicker
    - http://flask-appbuilder.readthedocs.org/en/latest/
    - Mongo: https://github.com/dpgaspar/Flask-AppBuilder/blob/645005f34fb559744655a269462d115e5931db58/flask_appbuilder/models/mongoengine/interface.py


SAAS - CLIENTS
--------------

- Si possible, livrable en 1 binaire unique

- Packages virtualenv/deb/rpm/... ? 

- Server TCP policy local
    - Par postfix ou partagé par plusieurs
    - Implémentation gevent, threading
    - Backup local pour ne pas perdre de données
    
- Clients intégrés au serveur policy (zmq/tcp/udp/rest)

- Version docker avec un server tcp + config intégré

- Version vagrant ?

Version/Espace Client Gratuit
-----------------------------

- Limitations:
    - 1 domain
    - 1 mynetworks (un serveur interne d'envoi de mail)
    - 1 seul client policy autorisé (ip fixe)
    - Rétention
    - Options search ?
    - Pas de support

Version/Espace Client Payant
----------------------------

- POUR ne pas transformer l'app en site de commerce:
    - Limiter les infos clients stockés au minimum
    - Les clients sous contrats seront gérer par le CRM client / David
    
- Besoins Minimum:
    - Auth client: combien de compte par groupe ????

    - Mini formulaire / dashboard pour gérer/visualiser ses options:
        - Onglet pour tableaux : domain/mynetwork/apikey    

- Structure model Customer
    - Infos DB nécessaire pour pymongo (mais db = nom du group)
        - Pour stocker les stats d'un client dans sa propre DB
    - Infos de contact (dans User et profil social plus profil étendu ?)
    
Enregistrement d'un nouveau client (group)
------------------------------------------

1. form register: saisie et post (informations minimum)
    - Pas de login social ici
    - Saisie des domaines/mynetworks ?

2. Confirmation par email

3. Création de l'espace client: (auto ?) : 

    - Création DB au nom du group: Elle qui reçoit les Policy ?
    
    - Copie des mynetworks/domains dans cette DB
    
    - Création Web App avec config vers DB du client ?
        - Implique ip/par public par client ?????
        - NON: accès par site ma/app

3. Création de l'espace client: Version 1 DB mutualisé + 1 DB / client

    - Création group déjà faite
    
    - mynetworks/domains déjà rattaché au group

    - Création d'une DB pour recevoir les stats par ZMQ/TCP/....
        - Enregistrement de cette DB dans les données du client
        
    - Espace de travail du client = ?
        - Client App Flask rattaché à l'app principal (site MA)
        - MongoDB ?: sessions web
        - Redis ?
        - InfluxDB mutualisé et redondé
        - ES dédié mutualisé et redondé
        - Dashboard grafana relié à un influxdb dédié ?
            - Template de config CT/config.js pour utiliser base au nom du client ou dédié
        - Dashboard kibana relié à un ES dédié ?


