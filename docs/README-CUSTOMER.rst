
Présentation idéal::

    Tableau étendu:
        Pour chaque domain:
            - Image
            - Groupe selon droits 
            - Nom
            - Date de création
            - Nombre de mails (entrant/sortant/....)
            - Lien edit/disable/... selon droits

    Form d'ajout domain/multi-domaine
        - Selection manuel ou auto du groupe de rattachement
        - Ajout dans un textaera
        - Import fichier plat
        - Champs dynamique
            - Le plus simple sera une gestion par render template + ajax:
                - 1. affiche form de base avec minimal fields
                - 2. bouton add:
                    - requette ajax pour demander le code html un champs numéroté pour ce form
                    bouton del:
                    - del jquery du champs
                - 3. submit:
                    - vue pour récupérer tous les champs, valider chaque entrée ?
                    - populate obj ?


Si structure suivante:

::

    class Client:
        group_name ?
        networks = []       String ou embed ?
        domains = []
        transport = []
        whitelist
        blacklist
        settings
        
        - clean pour chaque type et champs
        - méthodes pour render client -> json, html show, html edit
        
        getform ou model form partial ?
        
    Form dédié, crud domains:
        - Tableau avec x-editable
        - Form light car un seul champs, le nom de domain, peut se faire en modal ?
            - Placer id client en champs caché pour trouver ensuite le Client à mettre à jour
            - Validation coté form et coté class Client
        - Sortie du form:
            - Charger client
            - Modifier selon opération crud
            
            
            