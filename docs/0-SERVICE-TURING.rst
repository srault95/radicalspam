======================
Service Turing Hybryde
======================

- Le client reçoit les mails sur son frontal smtp dans son architecture

- Le mail est livré en local par smtp à un agent intermédiaire du service turing
    - l'agent interroge le service externe turing pour savoir si il faut livrer le mail en interne
    - Si le mail n'est pas encore stocké, le mail est enregistré par API REST au service externe
        - Ou stocké localement ou dans db (option) et record dans service externe : infos minimum
    - Un mail avec captcha est envoyé à l'expéditeur
    - L'agent boucle en attente de mail à débloquer

Agent local
-----------

- Serveur SMTP basic sans besoin SSL si local
- Queue async ?
- Module record: sqlite, file, mongodb, cassandra, ...
- Client rest pour interroger api externe (boucle + sleep)
    - voir plus tard, websocket client/server

Service web (falcon/tornado ?)
------------------------------

- Derrière un haproxy + proxy web
- Répond aux demandes du client rest de l'agent
- API public pour gérer config, list, ...
- Captch

Valeur ajouté
-------------

- Réputation des ips du service d'envoi des mails d'auth
    - Payer service réputation
- Partage de listes W/B
- Interface de gestion des mails en attentes
- Gestion de règles spécifique pour les VIP
- Envoi de rapport quotidien pour état des mails en attente de validation
- Service web auth dispo pour les captcha

Optimisations
-------------

- Générer liste bypass pour postfix et autre, contenant les ip/domain/email déjà authentifiés et ceux en BL
- Importer des listes ip/domain/email en BL/WL
- Gestion de règles spécifiques selon les heures/jours      

Services Inclus
---------------

- Stats / reporting
- Search
- API Rest

MailServer Mailhog
------------------

Dans mongodb
::::::::::::

::

    > db.messages.findOne()
    {
            "_id" : ObjectId("5736c6e816add8d40a918314"),
            "id" : "N4Pqm6lL7GLCvui2_TAh8vGbesDK7XOjDrErknF1AM8=@mailhog.example",
            "from" : {
                    "relays" : [ ],
                    "mailbox" : "user1",
                    "domain" : "domain1.com",
                    "params" : ""
            },
            "to" : [
                    {
                            "relays" : [ ],
                            "mailbox" : "rcpt1",
                            "domain" : "domain1.com",
                            "params" : ""
                    }
            ],
            "content" : {
                    "headers" : {
                            "MIME-Version" : [
                                    "1.0"
                            ],
                            "Subject" : [
                                    "The contents of test1"
                            ],
                            "To" : [
                                    "rcpt1@domain1.com"
                            ],
                            "Message-ID" : [
                                    "N4Pqm6lL7GLCvui2_TAh8vGbesDK7XOjDrErknF1AM8=@mailhog.example"
                            ],
                            "Received" : [
                                    "from [169.254.18.107] by mailhog.example (Go-MailHog)\r\n          id N4Pqm6lL7GLCvui2_TAh8vGbesDK7XOjDrErknF1AM8=@mailhog.example; Sat, 14 May 201
    6 08:34:16 +0200"
                            ],
                            "Content-Type" : [
                                    "text/plain; charset=\"us-ascii\""
                            ],
                            "Content-Transfer-Encoding" : [
                                    "7bit"
                            ],
                            "From" : [
                                    "sender1@domain1.com"
                            ],
                            "Return-Path" : [
                                    "<user1@domain1.com>"
                            ]
                    },
                    "body" : "test1...",
                    "size" : 215,
                    "mime" : null
            },
            "created" : ISODate("2016-05-14T06:34:16.188Z"),
            "mime" : null,
            "raw" : {
                    "from" : "user1@domain1.com",
                    "to" : [
                            "rcpt1@domain1.com"
                    ],
                    "data" : "Content-Type: text/plain; charset=\"us-ascii\"\r\nMIME-Version: 1.0\r\nContent-Transfer-Encoding: 7bit\r\nSubject: The contents of test1\r\nFrom: user1@do
    main1.com\r\nTo: rcpt1@domain1.com\r\nFrom: sender1@domain1.com\r\n\r\ntest1...",
                    "helo" : "[169.254.18.107]"
            }
    }