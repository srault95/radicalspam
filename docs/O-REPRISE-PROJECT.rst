==========
RS Project
==========


1. Sortie un RS4 pure docker avec des plus:
    - Commencer par mise au point des images individuels

    - Au départ, juste un radicalspam/install
      
      - Démarre avec lien socket docker et app web
        - Choix création de contenair ou utilisation de CT existant avec des noms fixes
      
      - Liste des options disponibles: lit la liste des images RS (postfix, clamav, ...)
        - récupère options et liste d'image du site public 
      
      - A la fin, l'installer devient quoi ?
    
    - Gestion par supervisor ou séparer les images et les gérer par app web + docker-py ?
        - Voir capacité à télécharger projet docker pour build local
        - utiliser des build publiés chez Docker
    
    - Toujours 2 ip ?
        - Ou 2 instance postfix avec des ports diff
        - Afficher options et laisser choisir
    
    - mini app web
    
    - centralisateur de log et search logs
    
    - Reste pb de la config auto et la mise à jour
      - wizard install: a la fin créé et lance les CT
    
    - Version vagrant par provisionning Docker ?

2. Travailler sur mail analytic phase1:
    - stats sur policy postfix
    - options pour reject relay, ....
    - auth client par ip
    - option client local + push rest

3. Turing SAAS:
    - service turing
    - record db mongo local ou sql
    - interraction avec saas par rest pour config et ordre
    - envoi de mail turing à partir du saas

4. Filtrage anti-spam / anti-virus ?

OU retour à l'idée de mail analytic qui demandait moins d'investissement !
- pure python
- optimisation par rest à partir d'un policy local

Problèmes actuels
=================

- MMS:
    - Manque de découplage entre mms (server smtp) et policy
    - Testabilité, surtout monté en charge

- POLICY:
    - Trop de code au même endroits
    - Testabilité
    - Extension
    - Maitrise d'une solution DNS interne avec cache durable (mongo ?)

- APRES MMS:
    - agents sa/clamd/ et livraison
    - Turing
    - Autres anti-virus en chaine
    - Tasks server
    - Instances par client (sa/clamd) pour config diff

Etudier
=======

- Outil de gestion mongo pour déployer un cluster et gérer les backups

Choix
=====

- OS pour les dockers:
    - Attention à Debian et aux versions en retard comme clamav

- Py2 ou Py3 ?

- MMS smtp direct ou comme Proxy de Postfix ou les 2 au choix:
    - SAAS: direct
    - Client: au choix MAIS attention config postfix !!!

RS-Saas
=======

- Publier ou non une version publique ? ou que du saas
    - Séparer policy comme une api utilisé par MMS
        - Faire implémentation REST rapide
        - Extraire le greylisting ?

RS-Dédié
========

- Idée:
    - Install d'une app web python à l'extérieur ou à l'intérieur de docker
    - cet app pilote la création, le setting d'images/ct docker
    - contruit et démarre les ct RS Postfix, Clamav, ...
        - Gère les dépendances internes et externes

- Version Vagrant

- Sans interface

- Postfix/Amavis/Clamav/SpamAssassin/Postgrey/Graylog ou ELK ?
    - Sans mongrey pas de stats !
- Conf par template + un gros YML
- Versions docker, ansible, virtualbox

OU

- Idéal: séparer pour réutiliser dans plusieurs modes:
    - rs-grey
        - lib + app autonome pour le greylisting de postfix
    - rs-policy
        - Peux utiliser rs-grey comme plugin
    - rs-policy-contrib
    - rs-smtpd
        - 1. serveur smtpd autonome mais qui peut servir comme smtp proxy de postfix
        - 2. interroge rs-grey et/ou rs-policy pour tous les RCPT à la fin avant DATA
        - 3. record mongodb optionnel ou autre ?
        - MANQUE traitement en sortie pour filter et/ou livrer !
    - rs-agent ou rs-filter:
        - Complément à rs-smtpd pour le traitement après record mongodb

MMS Server
==========

- Serveur SMTP autonome avec filtrage amont et storage MongoDB
- Intégre l'ancien mongrey pour le filtrage POLICY mais sans postfix

Web UI
======


Provisoire pour avancer
-----------------------

- Minimum de fonctionnalités pour commencer, quelques soit les choix finaux
    - Pas de wtform ?
    - Use form html direct
        - Les select par ajax
    - formvalidation coté client
    - schéma voluptous ou cerberus coté server: en attendant mongo 3.2 et validation coté server ?
        - Renvoi la liste des champs et erreur en json pour formvalidation ?

- App web intégrable en tant qu'addons ou bp à un site web saas
- CRUD sur Domain/Mynetwork/WBL/Transport
- Model Directory ou User ou config check smtp/ldap ?
- Bypass et whitelist greylisting: ip/net/domain/email

- Stats: ???
    - Intercepter les appels policy pour capture et redirection vers postgrey
        - il faudrait ajouter un id et une entrée policy pour l'ajout du champs ?
    - Intercepter les appels filter amavis pour capture et redirection vers amavis ?
        - il faudrait utiliser l'id policy pour consolider
        - manque résultat du traitement amavis

- Manque config amavis: banned, notifications quarantaine, ...
- Manque exploitation des données saisie:
    - RS 3.5.4: templates + rest
    - RS 4.x / Saas: exploitation direct

Config APPs
-----------

- Doit permettre de gérer la config des app RS

TAGS
----

- Reprendre l'idée du serveur de tags pour les recherches dans les mails et logs

UI Client
---------

- Plutôt que de recommencer avec des crud par objet: Domain, Network, ...
    - 1 seul document par client ?: attention limite de champs: 16 megabytes par doc
    - difficile pour comptes users ? et droits du user
        - si profil user, modification du même doc !!!

    - OU séparer les données mais utiliser un seul form avec onglets
    onglet settings: config du groupe/client
    onglet domain: tableau des domaines
        - Par forcément un tableau normal

    onglet mynetwork: ...
    onglet filter
    onglet wl/bl
    onglet users

    - Ensuite, présentation à part pour les données mails, logs, ...


- Gestion basique par manager:
    - CRUD: domain, wb/L
    - Règles de filtrage: voir formvalidation.io pour ajout dynamique de champs

- Gestion des messages et autres données par groupe de client
- Gestion indépendante du SAAS
- Dans le SAAS espace de travail par client (manager/user)

Task server
===========

- Portage sur APSheduler en PY3
- Manque tâches clamd/SA/... et contenair Docker liés

Manque
======

- Supervision
- Sentry ou Graylog ou logcabin ?
- ELK ? / InfluxDB

Demo
====


Architecture
============

- Faire un docker-compose

- Un des ct reliés à docker docker pour écouter les events des autres CT
    - Les ct emetteur doivent avoir une variable d'env pour les démarquer
    - use var env pour définir type app: mongodb, smtp, ...
    - mini app web ou rest dans ce CT pour maintenir les services ?
        - mise en pause / restart d'un ct, ...
    - Revient à un outil d'orchestration RS

- Répartition des produits:
    - CT data shared
    - mongodb
    - redis
    - graylog ?
    - radicalspam/clamav
        - 1 instance par client selon options, sinon 1 instance partagé ?
    - radicalspam/spamassassin
        - Comprend spamd, razor, pyzor, dcc
        - Lié à CT Redis
        - 1 instance par client selon options, sinon 1 instance partagé ?
    - radicalspam/rs-mms
        - 1 instance par MX ou choix de routage DB à l'intérieur ?
    - radicalspam/rs-mmw
    - radicalspam/rs-tasks

RS 3.5.4 mutualisé - TROP de travail et pas assez de capacité d'interception mail pour action et stats
------------------------------------------------------------------------------------------------------

- Commencer par une interface utilisable pour la config du RS mutualisé actuel ?

- Saisie domaines
- ip autorisés ?
- WB/L ip/domain/email
- Filtrage SA
- Logs ?
