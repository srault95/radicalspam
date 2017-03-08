=====================
Projet Mail Analytics
=====================

Cahier des charges
==================

Utilisation de postfix pour extraire des données statistiques (voir aussi exim)

Doit avoir le moins d'impact possible sur les architectures existantes

En sortie policy direct:
    - Réception sur un agent policy local ou remote
    - Envoi REST vers https://policy.mail-analytics.io
    - Les plus possible:
        - Ajout header id unique sur les mails sortants
    - version after data ?

En sortie postfix proxy smtp:
    - Réception sur un agent smtpd local qui rend la main de suite avec un code 2xx
    
    - 2 modes:
        - celui de type policy qui s'arrête avant data
        - celui après data
    
    - Analyse partiel local: surtout 
        - la taille du mail
        - la liste des pièces jointes
    
    - Envoi REST vers https://smtpd.mail-analytics.io
        - Seulement le résultat d'analyse et les entêtes cryptés/compressés
    
Prévoir les cas où:
    - Pas de postfix en frontal
    - Solutions fermé type firewall/proxy smtp
    
Les analyses possibles après réception (par tasks async)
    - Géolocalisation
    - Vérifications RBL des ips et domaines

Reporting:
    - En ligne
        - Des Top N
        - Des tableaux comparatif avec la période précédente
    - Export REST
    - Moteur de recherche
    - Envoi de rapport PDF    
        
Informations disponibles selon le mode choisi
=============================================

Informations nécessaires à fournir / gérer par le client
========================================================

- Liste de ses domaines
- Liste de ses ip/net qui permet de déterminer mails sortants 



Code existant
=============

- /rs-admin/src/radicalspam/0-mail-analytics/postfix-policyng-proxy/policyng_proxy.py
    - Recoit demande policy et stockage local db sqlite
    - Queue de traitement pour envoi async en push rest        
        