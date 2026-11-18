# 02. Processus de collecte des données

## 1. Source des données

Les données utilisées dans ce projet proviennent du fichier statistique de la DGESS intitulé `DONNEES_STATISTQUES_PRESCOLAIRE ET PRIMAIRE_2016_2025_DCB.xlsx`.

Ce classeur contient des informations statistiques sur l'enseignement préscolaire et primaire au Burkina Faso, réparties dans 14 feuilles.

Pour les besoins du projet, le fichier a été placé dans le dossier `data/01_raw_data/` sous le nom `donnees_education_bf.xlsx`.

## 2. Inventaire du fichier

La première étape a consisté à examiner la structure du classeur afin d'identifier les feuilles disponibles et les informations qu'elles contiennent.

Un script Python a été développé pour lire le fichier Excel et relever, pour chaque feuille, son nom ainsi que ses dimensions en lignes et en colonnes.

Les résultats de cette opération ont été enregistrés dans les fichiers `inventaire_donnees.csv` et `rapport_collecte.csv`.

## 3. Sélection des données

Après l'inventaire, les feuilles ont été examinées afin de déterminer leur intérêt pour le projet.

Sur les 14 feuilles disponibles, 13 ont été retenues. Onze sont destinées aux analyses principales et deux sont conservées comme sources complémentaires. La feuille consacrée au préscolaire a été exclue, car elle ne correspond pas au sujet de l'étude.

Les décisions prises ont été enregistrées dans `selection_donnees.csv` et `rapport_selection_donnees.csv`.

## 4. Organisation des données

Le fichier Excel original est conservé dans le dossier des données brutes. Les résultats de l'inventaire et de la sélection sont enregistrés séparément afin de préserver le fichier source et de faciliter le suivi des opérations.

Les scripts Python utilisés pour ces opérations sont conservés dans `src/01_data_collection/`.

Cette organisation permet de retrouver les étapes réalisées et de reprendre le processus si nécessaire.