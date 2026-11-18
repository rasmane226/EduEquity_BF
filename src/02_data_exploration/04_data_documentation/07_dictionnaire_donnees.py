
from pathlib import Path

import pandas as pd


# Chemins du projet
BASE_DIR = Path(__file__).resolve().parents[3]

FICHIER_SOURCE = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

DOSSIER_SORTIE = BASE_DIR / "outputs" / "tables"
FICHIER_SORTIE = DOSSIER_SORTIE / "dictionnaire_donnees.csv"


# Description des feuilles du classeur
descriptions = [
    {
        "feuille": "PRESCOLAIRE",
        "theme": "Effectifs du préscolaire",
        "variables_principales": "Sexe, région, statut",
        "periode": "2015/2016 à 2024/2025 (à confirmer)",
        "unite": "Nombre d'élèves",
        "utilite": "Analyse contextuelle de la situation du préscolaire",
        "limites": "Ne pas mélanger avec les indicateurs du primaire. Vérifier la correspondance entre les années affichées et les années scolaires."
    },
    {
        "feuille": "Feuil1",
        "theme": "Effectifs du primaire par région",
        "variables_principales": "Région, sexe",
        "periode": "2015/2016 à 2024/2025",
        "unite": "Nombre d'élèves",
        "utilite": "Analyse des disparités filles-garçons entre les régions",
        "limites": "Les effectifs ne représentent pas directement des taux d'accès à l'école."
    },
    {
        "feuille": "Feuil2",
        "theme": "Effectifs du primaire par statut",
        "variables_principales": "Statut, sexe",
        "periode": "2015/2016 à 2024/2025",
        "unite": "Nombre d'élèves",
        "utilite": "Comparer les effectifs dans les établissements publics et privés",
        "limites": "Les catégories de statut doivent être interprétées selon les définitions officielles."
    },
    {
        "feuille": "Feuil3",
        "theme": "Effectifs du primaire par milieu",
        "variables_principales": "Milieu urbain ou rural, sexe",
        "periode": "2015/2016 à 2024/2025",
        "unite": "Nombre d'élèves",
        "utilite": "Étudier la répartition des effectifs entre les milieux urbain et rural",
        "limites": "Les effectifs ne permettent pas, à eux seuls, de comparer les taux d'accès urbains et ruraux."
    },
    {
        "feuille": "Feuil4",
        "theme": "Effectifs du primaire par niveau",
        "variables_principales": "Statut, niveau scolaire, sexe",
        "periode": "2015/2016 à 2024/2025",
        "unite": "Nombre d'élèves",
        "utilite": "Étudier les différences filles-garçons selon le niveau scolaire",
        "limites": "Vérifier la cohérence des totaux entre les niveaux et les statuts."
    },
    {
        "feuille": "Feuil5",
        "theme": "Nouveaux entrants au CP1",
        "variables_principales": "Région, sexe",
        "periode": "2015/2016 à 2024/2025",
        "unite": "Nombre de nouveaux entrants",
        "utilite": "Étudier les disparités de sexe à l'entrée au primaire",
        "limites": "Les effectifs ne constituent pas un taux d'accès sans les populations de référence correspondantes."
    },
    {
        "feuille": "Feuil6",
        "theme": "Taux brut d'admission (TBA)",
        "variables_principales": "Région, sexe",
        "periode": "2015/2016 à 2024/2025",
        "unite": "Pourcentage",
        "utilite": "Comparer l'admission au primaire entre filles et garçons et entre régions",
        "limites": "Vérifier la définition officielle et les dénominateurs utilisés."
    },
    {
        "feuille": "Feuil7",
        "theme": "Taux brut de scolarisation (TBS)",
        "variables_principales": "Région, sexe",
        "periode": "2015/2016 à 2024/2025",
        "unite": "Pourcentage",
        "utilite": "Étudier les disparités de scolarisation selon le sexe et la région",
        "limites": "Un TBS supérieur à 100 % est possible. Vérifier la définition officielle."
    },
    {
        "feuille": "Feuil8",
        "theme": "Taux d'achèvement du primaire (TAP)",
        "variables_principales": "Région, sexe",
        "periode": "2015/2016 à 2024/2025",
        "unite": "Pourcentage",
        "utilite": "Étudier les différences d'achèvement entre filles et garçons",
        "limites": "Vérifier la définition officielle et les dénominateurs utilisés."
    },
    {
        "feuille": "Feuil9",
        "theme": "Taux de réussite au CEP",
        "variables_principales": "Région, sexe",
        "periode": "2016 à 2025",
        "unite": "Pourcentage",
        "utilite": "Analyser les écarts de réussite au CEP entre filles et garçons",
        "limites": "Les années sont des années civiles. Ne pas les confondre automatiquement avec les années scolaires."
    },
    {
        "feuille": "Feuil10",
        "theme": "Indice de parité du TBA",
        "variables_principales": "Région",
        "periode": "2015/2016 à 2024/2025",
        "unite": "Indice sans unité",
        "utilite": "Mesurer la parité filles-garçons en matière d'admission",
        "limites": "Confirmer la formule officielle de calcul de l'indice."
    },
    {
        "feuille": "Feuil11",
        "theme": "Indice de parité du TBS",
        "variables_principales": "Région",
        "periode": "2015/2016 à 2024/2025",
        "unite": "Indice sans unité",
        "utilite": "Mesurer la parité filles-garçons en matière de scolarisation",
        "limites": "Confirmer la formule officielle de calcul de l'indice."
    },
    {
        "feuille": "Feuil12",
        "theme": "Indice de parité du TAP",
        "variables_principales": "Région",
        "periode": "2015/2016 à 2024/2025",
        "unite": "Indice sans unité",
        "utilite": "Mesurer la parité filles-garçons en matière d'achèvement",
        "limites": "Confirmer la formule officielle de calcul de l'indice."
    },
    {
        "feuille": "Feuil13",
        "theme": "Écoles primaires par statut",
        "variables_principales": "Région, statut",
        "periode": "2015/2016 à 2024/2025",
        "unite": "Nombre d'écoles",
        "utilite": "Étudier la répartition des écoles publiques et privées entre les régions",
        "limites": "Le nombre d'écoles ne mesure pas directement leur capacité d'accueil ni leur accessibilité."
    }
]


# Création du tableau de 01_data_collection_documentation
dictionnaire = pd.DataFrame(descriptions)


# Vérification de la présence du fichier source
if not FICHIER_SOURCE.exists():
    raise FileNotFoundError(
        f"Le fichier source est introuvable : {FICHIER_SOURCE}"
    )


# Récupération des dimensions réelles de chaque feuille
classeur = pd.ExcelFile(FICHIER_SOURCE)

dimensions = []

for nom_feuille in classeur.sheet_names:
    donnees = pd.read_excel(
        FICHIER_SOURCE,
        sheet_name=nom_feuille,
        header=None
    )

    dimensions.append({
        "feuille": nom_feuille,
        "nombre_lignes_source": donnees.shape[0],
        "nombre_colonnes_source": donnees.shape[1]
    })


# Ajout des dimensions au dictionnaire
table_dimensions = pd.DataFrame(dimensions)

dictionnaire = dictionnaire.merge(
    table_dimensions,
    on="feuille",
    how="left"
)


# Vérification de la couverture du classeur
feuilles_documentees = set(dictionnaire["feuille"])
feuilles_source = set(classeur.sheet_names)

feuilles_non_documentees = feuilles_source - feuilles_documentees

if feuilles_non_documentees:
    print("Attention : certaines feuilles ne sont pas documentées.")
    print(sorted(feuilles_non_documentees))
else:
    print("Toutes les feuilles du classeur sont documentées.")


# Création du dossier et exportation
DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

dictionnaire.to_csv(
    FICHIER_SORTIE,
    index=False,
    encoding="utf-8-sig"
)

print("\nDictionnaire des données créé avec succès.")
print(f"Nombre de feuilles documentées : {len(dictionnaire)}")
print(f"Dimensions du dictionnaire : {dictionnaire.shape}")
print(f"Fichier enregistré : {FICHIER_SORTIE}")
