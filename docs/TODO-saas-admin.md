TODO
====

- Manque owner_group pour Message:
    - A faire par tasks de consolidation/parsing

- Pour chaque collection:
    - lib/0d_collections.js
    - lib/0e_hooks.js: ajout entrée collection à ModelsByGroup
    - lib/0f_contollers.js ???
    - client/config/0b_tables_settings.js: définit de la reactivetable
    - client/views/COLL/COLL.html: template COLLForm et COLLList
    - client/views/COLL/COLL.js:
        - Template.DomainForm.helpers(MongreyClient.fn.CollectionFormHelpers(MongreyClient.Collections.Domain));
    - client/routes.js
    - server/security.js
    - server/publish.js

- Faire une collection null pour gérer les alertes

- Revenir sur tableau/formulaires traditionnel et voir plus tard pour modal ou form à coté du tableau

- Bien définir les droits de chaque roles et groupes:
    - Ne pas afficher liste domain pour user ?

- Droits:
    - Domaine
    - Mynetwork

- Outils avec validation et autres regexp/outils:
    -  https://github.com/copleykj/meteor-shower

- Politiques de filtrages entrantes/sortantes pour policy et filter
    -  Gérer politiques et form/process pour affecter à : Ip, sender, ....
    -  Filtre ou mongre, cherche éléments comme ip, domain, ... et demande politique de filtrage

- Désactiver validation par autoform pour prendre la main sur le submit

- Opérations obligatoires à partir d'un mx déclaré:
    - Envoi de mail externe (notification, turing, smtp verify)
        - Implique un agent sur chaque MX pour executer les tâches

- Prévoir de désactiver multi-groupe quand app dédié à gros client avec ses propres db mongo

- Utiliser plutot des méthodes pour update/insert/remove que les autoform actions ?
    - pour insert, plus facile pour insérer data et passer autre userId que celui en cours

- Utiliser une ReativeVar pour que admin ou manager selectionne le groupe en cours
    - Tous les subscribe doivent passer ce current groupe en paramètre

- Notion de manager dans un group et/ou de owner default ?

- limiter les stats et graphiques dans app et envoyer data pour use dashboard en service externe

- Structure le dashboard en widgets et charger la collection avec les paramètres du user

- api rest
    - collection apikey ou champs dans mta et user ?

- options globales ou settings utilisateurs pour:
    - choix edition/creation modal, full, ou à coté du tableau


## API

- List

```
//https://188.165.254.60:444/api/domain
{
    status: "success",
    data: [
        {
        _id: "S5iDzifk7u8PxGPh6",
        name: "mathilde.org",
        active: true,
        owner: "zGSktuXbzWnbjJiSg",
        owner_group: "group2"
        }
    ]
}
```

- Pour un id non trouvé:

```
//https://188.165.254.60:444/api/domain/S5iDzifk7u8PxGPh6
{
status: "fail",
message: "Item not found"
}
```

curl -X POST http://localhost:$PORT/api/domain/ -d "name=domain1.com" -d "active=true"

curl -X DELETE http://localhost:3000/api/posts/LrcEYNojn5N7NPRdo


## Login

```
curl http://localhost:$PORT/api/login/ -d "password=password&user=admin@example.com"
{
  "status": "success",
  "data": {
    "authToken": "8HskGGPr7cfAW4n2VcijinN42XSHJPFQJnsfHk-0QcK",
    "userId": "EjEkNJgo2LaffnDsj"
  }
}
```

curl http://localhost:3000/api/logout -H "X-Auth-Token: f2KpRW7KeN9aPmjSZ" -H "X-User-Id: fbdpsNf4oHiX79vMJ"

 http://localhost:3000/api/posts/

"data": {
    "authToken": "",
    "userId": ""
  }
}(mkdocs)(docker)root@292f90f092c7:~$

curl -H "X-Auth-Token: 8HskGGPr7cfAW4n2VcijinN42XSHJPFQJnsfHk-0QcK" -H "X-User-Id: EjEkNJgo2LaffnDsj" -X POST http://localhost:$PORT/api/domain/ -d "name=domain1.com" -d "active=True"
