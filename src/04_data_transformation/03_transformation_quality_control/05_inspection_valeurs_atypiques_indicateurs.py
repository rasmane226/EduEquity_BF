
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# 1. CONFIGURATION
# ============================================================

RACINE_PROJET = Path(__file__).resolve().parents[3]

FICHIER = (
    RACINE_PROJET
    / "data"
    / "04_transformed_data"
    / "merged"
    / "indicateurs_regionaux_sexe.csv"
)

DOSSIER_RAPPORTS = (
    RACINE_PROJET
    / "outputs"
    / "tables"
    / "transformation"
)

DOSSIER_RAPPORTS.mkdir(
    parents=True,
    exist_ok=True
)

ANNEE_PRECEDENTE = "2021-2022"
ANNEE_ACTUELLE = "2022-2023"

VARIABLES_TAUX = ["TBA", "TBS", "TAP"]

CLES = [
    "REGION",
    "ANNEE_SCOLAIRE",
    "SEXE"
]

COLONNES_INSPECTION = [
    "REGION",
    "ANNEE_SCOLAIRE",
    "SEXE",
    "EFFECTIF",
    "TBA",
    "TBS",
    "TAP"
]


# ============================================================
# 2. CHARGEMENT ET VERIFICATION
# ============================================================

print("\n========== INSPECTION DES VALEURS ATYPIQUES ==========")

if not FICHIER.exists():
    raise FileNotFoundError(
        f"Fichier introuvable : {FICHIER}"
    )

df = pd.read_csv(
    FICHIER,
    encoding="utf-8-sig"
)

df.columns = (
    df.columns.astype(str)
    .str.replace("\ufeff", "", regex=False)
    .str.strip()
    .str.upper()
)

colonnes_absentes = [
    colonne
    for colonne in COLONNES_INSPECTION
    if colonne not in df.columns
]

if colonnes_absentes:
    raise ValueError(
        f"Colonnes absentes : {colonnes_absentes}"
    )

for colonne in CLES:
    df[colonne] = (
        df[colonne]
        .astype("string")
        .str.strip()
        .str.upper()
    )

for colonne in ["EFFECTIF"] + VARIABLES_TAUX:
    df[colonne] = pd.to_numeric(
        df[colonne],
        errors="coerce"
    )

print("Dimensions :", df.shape)
print("Valeurs manquantes :")
print(df[COLONNES_INSPECTION].isna().sum())

doublons = int(df.duplicated(subset=CLES).sum())

print("\nDoublons sur les clés :", doublons)

if doublons > 0:
    print(
        "ATTENTION : les doublons doivent être examinés "
        "avant toute comparaison."
    )


# ============================================================
# 3. INSPECTION DES TAP SUPERIEURS A 100 %
# ============================================================

print("\n========== 1. TAP SUPERIEUR A 100 % ==========")

tap_superieur_100 = (
    df.loc[
        df["TAP"] > 100,
        COLONNES_INSPECTION
    ]
    .sort_values(
        by="TAP",
        ascending=False
    )
)

print(
    tap_superieur_100.to_string(index=False)
)

print(
    "\nNombre d'observations :",
    len(tap_superieur_100)
)

chemin_tap_superieur = (
    DOSSIER_RAPPORTS
    / "inspection_tap_superieur_100.csv"
)

tap_superieur_100.to_csv(
    chemin_tap_superieur,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 4. INSPECTION DES TAP INFERIEURS A 15 %
# ============================================================

print("\n========== 2. TAP INFERIEUR A 15 % ==========")

tap_faible = (
    df.loc[
        df["TAP"] < 15,
        COLONNES_INSPECTION
    ]
    .sort_values(
        by="TAP",
        ascending=True
    )
)

print(
    tap_faible.to_string(index=False)
)

print(
    "\nNombre d'observations :",
    len(tap_faible)
)

chemin_tap_faible = (
    DOSSIER_RAPPORTS
    / "inspection_tap_inferieur_15.csv"
)

tap_faible.to_csv(
    chemin_tap_faible,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 5. INSPECTION DE L'ANNEE 2022-2023
# ============================================================

print("\n========== 3. INSPECTION 2022-2023 ==========")

annee = (
    df.loc[
        df["ANNEE_SCOLAIRE"] == ANNEE_ACTUELLE,
        COLONNES_INSPECTION
    ]
    .sort_values(
        by=["REGION", "SEXE"]
    )
)

print(
    annee.to_string(index=False)
)

chemin_annee = (
    DOSSIER_RAPPORTS
    / "inspection_indicateurs_2022_2023.csv"
)

annee.to_csv(
    chemin_annee,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 6. COMPARAISON ENTRE LES DEUX ANNEES
# ============================================================

print(
    "\n========== 4. COMPARAISON 2021-2022 / 2022-2023 =========="
)

donnees_comparaison = df.loc[
    df["ANNEE_SCOLAIRE"].isin(
        [ANNEE_PRECEDENTE, ANNEE_ACTUELLE]
    )
].copy()

if donnees_comparaison.empty:
    raise ValueError(
        "Aucune observation trouvée pour les années à comparer."
    )

doublons_comparaison = donnees_comparaison.duplicated(
    subset=["REGION", "SEXE", "ANNEE_SCOLAIRE"]
).sum()

if doublons_comparaison > 0:
    raise ValueError(
        f"{doublons_comparaison} doublons détectés "
        "dans les données de comparaison."
    )

nombre_combinaisons_attendu = (
    df["REGION"].nunique()
    * df["SEXE"].nunique()
)

nombre_combinaisons_observe = (
    donnees_comparaison[
        ["REGION", "SEXE", "ANNEE_SCOLAIRE"]
    ]
    .drop_duplicates()
    .shape[0]
)

if len(donnees_comparaison["ANNEE_SCOLAIRE"].unique()) != 2:
    raise ValueError(
        "Les deux années nécessaires à la comparaison "
        "ne sont pas présentes."
    )

comparaison = donnees_comparaison.pivot(
    index=["REGION", "SEXE"],
    columns="ANNEE_SCOLAIRE",
    values=VARIABLES_TAUX
)

colonnes_attendues = [
    (variable, annee)
    for variable in VARIABLES_TAUX
    for annee in [ANNEE_PRECEDENTE, ANNEE_ACTUELLE]
]

colonnes_manquantes = [
    colonne
    for colonne in colonnes_attendues
    if colonne not in comparaison.columns
]

if colonnes_manquantes:
    raise ValueError(
        f"Combinaisons de valeurs absentes : {colonnes_manquantes}"
    )

resultats_comparaison = []

for variable in VARIABLES_TAUX:

    valeur_precedente = comparaison[
        (variable, ANNEE_PRECEDENTE)
    ]

    valeur_actuelle = comparaison[
        (variable, ANNEE_ACTUELLE)
    ]

    ecart = (
        valeur_actuelle - valeur_precedente
    )

    tableau = pd.DataFrame({
        "VALEUR_2021_2022": valeur_precedente,
        "VALEUR_2022_2023": valeur_actuelle,
        "ECART": ecart
    })

    tableau = tableau.reset_index()

    tableau["INDICATEUR"] = variable

    tableau["SENS_EVOLUTION"] = np.select(
        [
            tableau["ECART"] > 0,
            tableau["ECART"] < 0
        ],
        [
            "HAUSSE",
            "BAISSE"
        ],
        default="STABLE"
    )

    resultats_comparaison.append(tableau)

comparaison_detaillee = pd.concat(
    resultats_comparaison,
    ignore_index=True
)

comparaison_detaillee = comparaison_detaillee[
    [
        "REGION",
        "SEXE",
        "INDICATEUR",
        "VALEUR_2021_2022",
        "VALEUR_2022_2023",
        "ECART",
        "SENS_EVOLUTION"
    ]
]

comparaison_detaillee = comparaison_detaillee.sort_values(
    by="ECART"
)

print(
    comparaison_detaillee.to_string(index=False)
)

chemin_comparaison = (
    DOSSIER_RAPPORTS
    / "comparaison_indicateurs_2021_2022_2022_2023.csv"
)

comparaison_detaillee.to_csv(
    chemin_comparaison,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 7. SYNTHESE DES VARIATIONS
# ============================================================

print("\n========== 5. SYNTHESE DES VARIATIONS ==========")

synthese_variations = (
    comparaison_detaillee
    .groupby("INDICATEUR")
    .agg(
        NOMBRE_COMPARAISONS=("ECART", "count"),
        NOMBRE_BAISSES=(
            "SENS_EVOLUTION",
            lambda x: (x == "BAISSE").sum()
        ),
        NOMBRE_HAUSSES=(
            "SENS_EVOLUTION",
            lambda x: (x == "HAUSSE").sum()
        ),
        NOMBRE_STABILITES=(
            "SENS_EVOLUTION",
            lambda x: (x == "STABLE").sum()
        ),
        ECART_MOYEN=("ECART", "mean"),
        ECART_MINIMUM=("ECART", "min"),
        ECART_MAXIMUM=("ECART", "max")
    )
    .reset_index()
)

print(
    synthese_variations.to_string(index=False)
)

chemin_synthese = (
    DOSSIER_RAPPORTS
    / "synthese_variations_indicateurs_2021_2023.csv"
)

synthese_variations.to_csv(
    chemin_synthese,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 8. BILAN DE L'INSPECTION
# ============================================================

print("\n========== 6. BILAN DE L'INSPECTION ==========")

print(
    "TAP supérieurs à 100 % :",
    len(tap_superieur_100)
)

print(
    "TAP inférieurs à 15 % :",
    len(tap_faible)
)

print(
    "Observations comparées par région et sexe :",
    len(comparaison_detaillee)
)

print("\nFichiers générés :")

print(chemin_tap_superieur)
print(chemin_tap_faible)
print(chemin_annee)
print(chemin_comparaison)
print(chemin_synthese)

print("\n========== FIN DE L'INSPECTION ==========")
