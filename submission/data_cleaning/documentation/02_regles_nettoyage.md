# 02. Règles de nettoyage des données

Le nettoyage a été adapté à la structure et au contenu de chaque feuille du fichier Excel. Les principales règles appliquées sont les suivantes.

1. Organisation des données

Les lignes et les colonnes ont été réorganisées pour faciliter l'exploitation des informations. Les en-têtes ont été identifiés et les données utiles ont été conservées.

2. Harmonisation des catégories

Les noms des régions et les catégories ont été uniformisés afin d'éviter les différences d'écriture. Les catégories relatives au sexe, au milieu de résidence et au statut des établissements ont également été normalisées.

3. Traitement des valeurs

Les valeurs numériques ont été converties dans un format exploitable par Python. Les valeurs manquantes et les valeurs négatives ont fait l'objet de contrôles.

4. Traitement des totaux

Les lignes nationales et les lignes de total ont été traitées selon leur utilité pour chaque fichier. Les données nationales ont été conservées lorsqu'elles étaient nécessaires aux contrôles, tandis que les données destinées aux analyses régionales ont été limitées aux 13 régions.

5. Organisation finale

Les données ont été enregistrées en fichiers CSV. Certaines feuilles ont été conservées sous forme de tableaux larges, tandis que d'autres ont été converties au format long pour faciliter les analyses par région, année et sexe.

Les mêmes règles n'ont pas été appliquées indistinctement à toutes les feuilles. Chaque traitement a tenu compte de la structure et de l'objectif des données concernées.