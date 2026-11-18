# 01 — Processus de transformation des données

## 1. Objectif

La phase de transformation a pour objectif de préparer les données nettoyées afin de les rendre exploitables pour les analyses statistiques et l'étude des disparités dans l'enseignement primaire au Burkina Faso.

Elle comprend la préparation des données, l'harmonisation des variables, la construction des indicateurs et le regroupement des informations provenant de différentes feuilles du fichier source.

## 2. Données d'entrée

Les données utilisées proviennent de la phase précédente de nettoyage.

Elles couvrent les années scolaires 2015-2016 à 2024-2025 et les 13 régions du Burkina Faso.

Onze fichiers nettoyés sont utilisés comme données d'entrée pour cette phase.

## 3. Étapes de transformation

### 3.1. Préparation des données

Cette étape consiste à inspecter la structure des fichiers, vérifier les variables disponibles, examiner les catégories et appliquer les transformations nécessaires à leur exploitation.

Les données sont ensuite préparées dans un format cohérent pour les traitements ultérieurs.

### 3.2. Fusion des données

Les données préparées sont regroupées pour construire cinq tables analytiques :

-Indicateurs régionaux par sexe : regroupement des effectifs, des nouveaux inscrits au CP1 et des indicateurs TBA, TBS et TAP.
-Indices de parité :préparation des indices de parité régionaux.
-Comparaison urbain-rural : regroupement des effectifs des milieux urbain et rural.
-Résultats du CEP : préparation des résultats par région et par sexe.
-Répartition des écoles : regroupement des effectifs des établissements publics et privés par région.

### 3.3. Contrôle de la transformation

Les fichiers produits font l'objet de contrôles portant notamment sur leur structure, la cohérence des données, la fidélité numérique par rapport aux données nettoyées et la validité des indicateurs.

## 4. Résultats

La phase de transformation produit :

-11 fichiers de données transformées correspondant aux feuilles traitées ;
-5 tables analytiques regroupées ;
-Des rapports de contrôle permettant de documenter la qualité des résultats.

Les fichiers transformés sont conservés dans `results/transformed_sheets/` et les tables regroupées dans `results/merged_data/`.

Les rapports de contrôle retenus sont conservés dans `results/quality_reports/`.

## 5. Utilisation des données

Les données obtenues constituent la base des analyses statistiques et comparatives de la phase suivante du projet EduEquity BF.