# 01. Sources des données

## 1. Source principale

Les données de cette étude proviennent de la Direction générale des études et des statistiques sectorielles (DGESS) du Burkina Faso.

Le fichier utilisé est intitulé `DONNEES_STATISTQUES_PRESCOLAIRE ET PRIMAIRE_2016_2025_DCB.xlsx`. Il regroupe des statistiques relatives à l'enseignement préscolaire et primaire.

## 2. Source complémentaire

Une source complémentaire provient de l'Institut national de la statistique et de la démographie (INSD), à travers le rapport intitulé *Cinquième Recensement Général de la Population et de l’Habitation du Burkina Faso*.

Les données exploitées sont issues des tableaux 37 et 38, présentés aux pages 77 à 85 du rapport, publié en juin 2022.

Le tableau 37 présente la répartition de la population âgée de 6 à 16 ans selon le statut scolaire, le milieu de résidence et le sexe.

Le tableau 38 présente la répartition de la population selon le statut scolaire et la région, avec une ventilation par groupe d'âge. Pour cette étude, les données du groupe des 6 à 11 ans sont retenues.

Ces informations complètent les statistiques de la DGESS en apportant un éclairage sur les disparités de scolarisation observées en 2019.

## 3. Contenu des données

Le classeur principal comprend 14 feuilles présentant différentes informations sur le système éducatif. Elles portent notamment sur les effectifs scolaires, les taux d'admission et de scolarisation, les taux d'achèvement, les résultats au CEP, les indices de parité et les établissements scolaires.

Les données permettent d'étudier les différences entre filles et garçons ainsi que les disparités entre les régions et les milieux urbains et ruraux.

Les données complémentaires de l'INSD permettent d'enrichir cette analyse avec des informations sur le statut scolaire de la population selon le sexe, le milieu de résidence, la région et le groupe d'âge, dans la limite des ventilations disponibles.

## 4. Période couverte

Les données principales de la DGESS couvrent la période allant de 2015-2016 à 2024-2025 pour les indicateurs présentés par année scolaire. Les statistiques du CEP sont présentées selon les années civiles 2016 à 2025.

Les données complémentaires de l'INSD correspondent au Recensement général de la population et de l'habitation de 2019. Elles constituent une référence ponctuelle et non une série annuelle.

## 5. Format et stockage

Le fichier principal est au format Excel (`.xlsx`). Il est conservé dans le dossier `data/01_raw_data/` sous le nom `donnees_education_bf.xlsx`.

Le fichier complémentaire de l'INSD est au format CSV (`.csv`). Il est conservé dans le dossier `data/02_donnees_complementaires/insd_rgph_2019/` sous le nom `donnees_scolarisation_insd_rgph_2019.csv`.

Les données originales sont conservées séparément des fichiers issus des opérations d'exploration, de nettoyage et de transformation.