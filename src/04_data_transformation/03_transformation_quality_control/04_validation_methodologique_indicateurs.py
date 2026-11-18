
from pathlib import Path

import itertools
import numpy as np
import pandas as pd


# ============================================================
# 1. CONFIGURATION
# ============================================================

RACINE_PROJET = Path(__file__).resolve().parents[3]

DOSSIER_DONNEES = (
    RACINE_PROJET
    / "data"
    / "04_transformed_data"
    / "merged"
)

DOSSIER_RAPPORTS = (
    RACINE_PROJET
    / "outputs"
    / "tables"
    / "transformation"
)

DOSSIER_RAPPORTS.mkdir(parents=True, exist_ok=True)

FICHIER = DOSSIER_DONNEES / "indicateurs_regionaux_sexe.csv"

ANNEES_ATTENDUES = [
    "2015-2016", "2016-2017", "2017-2018",
    "2018-2019", "2019-2020", "2020-2021",
    "2021-2022", "2022-2023", "2023-2024",
    "2024-2025"
]

SEXES_ATTENDUS = ["FILLES", "GARCONS"]

CLES = ["REGION", "ANNEE_SCOLAIRE", "SEXE"]

VARIABLES_NUMERIQUES = [
    "EFFECTIF",
    "NOUVEAUX_INSCRITS_CP1",
    "TBA",
    "TBS",
    "TAP"
]

VARIABLES_EFFECTIFS = [
    "EFFECTIF",
    "NOUVEAUX_INSCRITS_CP1"
]

VARIABLES_TAUX = ["TBA", "TBS", "TAP"]


# ============================================================
# 2. CHARGEMENT ET VERIFICATION DE LA STRUCTURE
# ============================================================

print("\n========== VALIDATION METHODOLOGIQUE ==========")
print("TABLE : INDICATEURS REGIONAUX PAR SEXE")

if not FICHIER.exists():
    raise FileNotFoundError(f"Fichier introuvable : {FICHIER}")

df = pd.read_csv(FICHIER, encoding="utf-8-sig")

df.columns = (
    df.columns.astype(str)
    .str.replace("\ufeff", "", regex=False)
    .str.strip()
    .str.upper()
)

print("\nDimensions initiales :", df.shape)
print("Colonnes :", df.columns.tolist())

colonnes_requises = CLES + VARIABLES_NUMERIQUES
colonnes_absentes = [
    col for col in colonnes_requises
    if col not in df.columns
]

if colonnes_absentes:
    raise ValueError(
        f"Colonnes obligatoires absentes : {colonnes_absentes}"
    )

# Normalisation des clés textuelles
for colonne in CLES:
    df[colonne] = (
        df[colonne]
        .astype("string")
        .str.strip()
        .str.upper()
    )

# Les chaînes vides deviennent des valeurs manquantes
df[CLES] = df[CLES].replace("", pd.NA)


# ============================================================
# 3. VERIFICATION DES DIMENSIONS ATTENDUES
# ============================================================

print("\n========== 1. DIMENSIONS ATTENDUES ==========")

nombre_regions = df["REGION"].nunique()
nombre_annees = df["ANNEE_SCOLAIRE"].nunique()
nombre_sexes = df["SEXE"].nunique()

print("Nombre de régions :", nombre_regions)
print("Nombre d'années :", nombre_annees)
print("Nombre de catégories de sexe :", nombre_sexes)

regions = sorted(df["REGION"].dropna().unique().tolist())

controles_dimensions = {
    "13_REGIONS": nombre_regions == 13,
    "10_ANNEES": sorted(
        df["ANNEE_SCOLAIRE"].dropna().unique().tolist()
    ) == sorted(ANNEES_ATTENDUES),
    "2_CATEGORIES_SEXE": sorted(
        df["SEXE"].dropna().unique().tolist()
    ) == sorted(SEXES_ATTENDUS)
}

for nom, resultat in controles_dimensions.items():
    print(nom, ":", "VALIDE" if resultat else "A_VERIFIER")


# ============================================================
# 4. VERIFICATION DES CLES ET DES COMBINAISONS
# ============================================================

print("\n========== 2. VERIFICATION DES CLES ==========")

cles_manquantes = int(df[CLES].isna().any(axis=1).sum())
doublons = int(df.duplicated(subset=CLES).sum())

print("Lignes avec clés manquantes :", cles_manquantes)
print("Doublons sur les clés :", doublons)

combinaisons_attendues = pd.DataFrame(
    list(
        itertools.product(
            regions,
            ANNEES_ATTENDUES,
            SEXES_ATTENDUS
        )
    ),
    columns=CLES
)

combinaisons_observees = (
    df[CLES]
    .dropna()
    .drop_duplicates()
)

comparaison_cles = combinaisons_attendues.merge(
    combinaisons_observees,
    on=CLES,
    how="outer",
    indicator=True
)

cles_absentes = int(
    (comparaison_cles["_merge"] == "left_only").sum()
)

cles_supplementaires = int(
    (comparaison_cles["_merge"] == "right_only").sum()
)

print("Combinaisons attendues :", len(combinaisons_attendues))
print("Combinaisons absentes :", cles_absentes)
print("Combinaisons supplémentaires :", cles_supplementaires)


# ============================================================
# 5. CONTROLE DES VALEURS NUMERIQUES
# ============================================================

print("\n========== 3. CONTROLE NUMERIQUE ==========")

rapport_numerique = []

for colonne in VARIABLES_NUMERIQUES:

    valeurs_originales = df[colonne].copy()

    df[colonne] = pd.to_numeric(
        df[colonne],
        errors="coerce"
    )

    conversions_invalides = int(
        (valeurs_originales.notna() & df[colonne].isna()).sum()
    )

    valeurs_manquantes = int(df[colonne].isna().sum())

    valeurs_infinies = int(
        np.isinf(df[colonne].dropna()).sum()
    )

    valeurs_negatives = int(
        (df[colonne] < 0).sum()
    )

    valeurs_non_entieres = 0

    if colonne in VARIABLES_EFFECTIFS:
        valeurs_non_entieres = int(
            (
                df[colonne].notna()
                & ~np.isclose(
                    df[colonne].fillna(0),
                    np.round(df[colonne].fillna(0))
                )
            ).sum()
        )

    rapport_numerique.append({
        "VARIABLE": colonne,
        "VALEURS_MANQUANTES": valeurs_manquantes,
        "CONVERSIONS_INVALIDES": conversions_invalides,
        "VALEURS_INFINIES": valeurs_infinies,
        "VALEURS_NEGATIVES": valeurs_negatives,
        "VALEURS_NON_ENTIERES": valeurs_non_entieres,
        "MINIMUM": df[colonne].min(),
        "MAXIMUM": df[colonne].max(),
        "MOYENNE": df[colonne].mean(),
        "MEDIANE": df[colonne].median()
    })

    print(f"\n--- {colonne} ---")
    print("Minimum :", df[colonne].min())
    print("Maximum :", df[colonne].max())
    print("Valeurs manquantes :", valeurs_manquantes)
    print("Conversions invalides :", conversions_invalides)
    print("Valeurs infinies :", valeurs_infinies)
    print("Valeurs négatives :", valeurs_negatives)

    if colonne in VARIABLES_EFFECTIFS:
        print("Valeurs non entières :", valeurs_non_entieres)

rapport_numerique = pd.DataFrame(rapport_numerique)

rapport_numerique.to_csv(
    DOSSIER_RAPPORTS / "validation_methodologique_controle_numerique.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 6. STATISTIQUES DESCRIPTIVES
# ============================================================

print("\n========== 4. STATISTIQUES DESCRIPTIVES ==========")

statistiques = df[VARIABLES_NUMERIQUES].describe().T

print(statistiques.to_string())

statistiques.to_csv(
    DOSSIER_RAPPORTS
    / "validation_methodologique_statistiques_indicateurs.csv",
    encoding="utf-8-sig"
)


# ============================================================
# 7. DISTRIBUTION PAR SEXE
# ============================================================

print("\n========== 5. DISTRIBUTION PAR SEXE ==========")

distribution_sexe = (
    df.groupby("SEXE")[VARIABLES_NUMERIQUES]
    .agg(["count", "mean", "median", "min", "max"])
)

print(distribution_sexe.to_string())

distribution_sexe.to_csv(
    DOSSIER_RAPPORTS
    / "validation_methodologique_distribution_sexe.csv",
    encoding="utf-8-sig"
)


# ============================================================
# 8. EVOLUTION DES INDICATEURS PAR ANNEE
# ============================================================

print("\n========== 6. EVOLUTION PAR ANNEE ==========")

evolution = (
    df.groupby("ANNEE_SCOLAIRE")[VARIABLES_NUMERIQUES]
    .agg(["count", "mean", "median", "min", "max"])
)

print(evolution.to_string())

evolution.to_csv(
    DOSSIER_RAPPORTS
    / "validation_methodologique_evolution_indicateurs.csv",
    encoding="utf-8-sig"
)

print(
    "\nNOTE : les moyennes calculées sont des moyennes régionales "
    "non pondérées. Elles ne représentent pas automatiquement "
    "les taux nationaux."
)


# ============================================================
# 9. CONTROLE DES TAUX
# ============================================================

print("\n========== 7. CONTROLE DES TAUX ==========")

for colonne in VARIABLES_TAUX:

    valeurs_superieures_100 = int(
        (df[colonne] > 100).sum()
    )

    valeurs_egales_zero = int(
        (df[colonne] == 0).sum()
    )

    print(f"\n--- {colonne} ---")
    print("Valeurs supérieures à 100 :", valeurs_superieures_100)
    print("Valeurs égales à zéro :", valeurs_egales_zero)

print(
    "\nAttention : une valeur supérieure à 100 n'est pas "
    "automatiquement une erreur. Elle doit être interprétée "
    "selon la définition de l'indicateur."
)


# ============================================================
# 10. COMPARAISON FILLES-GARCONS
# ============================================================

print("\n========== 8. COMPARAISON FILLES-GARCONS ==========")

tableau_comparatif = None

if (
    doublons == 0
    and cles_manquantes == 0
    and set(df["SEXE"].dropna().unique()) == set(SEXES_ATTENDUS)
):

    tableau_comparatif = df.pivot(
        index=["REGION", "ANNEE_SCOLAIRE"],
        columns="SEXE",
        values=VARIABLES_NUMERIQUES
    )

    print("Dimensions du tableau :", tableau_comparatif.shape)
    print("\nAperçu :")
    print(tableau_comparatif.head(10).to_string())

    tableau_comparatif.to_csv(
        DOSSIER_RAPPORTS
        / "validation_methodologique_comparaison_filles_garcons.csv",
        encoding="utf-8-sig"
    )

else:
    print(
        "PIVOT NON EXECUTE : les clés présentent des anomalies "
        "ou les catégories de sexe attendues sont absentes."
    )


# ============================================================
# 11. SYNTHESE DES CONTROLES
# ============================================================

print("\n========== 9. SYNTHESE DES CONTROLES ==========")

controles = {
    **controles_dimensions,
    "CLES_SANS_VALEURS_MANQUANTES": cles_manquantes == 0,
    "ABSENCE_DOUBLONS": doublons == 0,
    "COMBINAISONS_COMPLETES": (
        cles_absentes == 0 and cles_supplementaires == 0
    ),
    "VALEURS_NUMERIQUES_COMPLETES": (
        rapport_numerique["VALEURS_MANQUANTES"].sum() == 0
    ),
    "CONVERSIONS_NUMERIQUES_VALIDES": (
        rapport_numerique["CONVERSIONS_INVALIDES"].sum() == 0
    ),
    "ABSENCE_VALEURS_INFINIES": (
        rapport_numerique["VALEURS_INFINIES"].sum() == 0
    ),
    "ABSENCE_VALEURS_NEGATIVES": (
        rapport_numerique["VALEURS_NEGATIVES"].sum() == 0
    ),
    "EFFECTIFS_ENTIERS": (
        rapport_numerique["VALEURS_NON_ENTIERES"].sum() == 0
    )
}

for nom, resultat in controles.items():
    print(
        f"{nom} :",
        "VALIDE" if resultat else "A_VERIFIER"
    )

statut_global = (
    "VALIDE"
    if all(controles.values())
    else "A_VERIFIER"
)

print("\nSTATUT GLOBAL :", statut_global)


# ============================================================
# 12. EXPORT DU RAPPORT DE SYNTHESE
# ============================================================

rapport_synthese = pd.DataFrame([
    {
        "CONTROLE": nom,
        "RESULTAT": "VALIDE" if resultat else "A_VERIFIER"
    }
    for nom, resultat in controles.items()
])

rapport_synthese.loc[len(rapport_synthese)] = {
    "CONTROLE": "STATUT_GLOBAL",
    "RESULTAT": statut_global
}

chemin_synthese = (
    DOSSIER_RAPPORTS
    / "rapport_validation_methodologique_indicateurs.csv"
)

rapport_synthese.to_csv(
    chemin_synthese,
    index=False,
    encoding="utf-8-sig"
)

print("\n========== RAPPORTS GENERES ==========")

print(
    DOSSIER_RAPPORTS
    / "validation_methodologique_controle_numerique.csv"
)
print(
    DOSSIER_RAPPORTS
    / "validation_methodologique_statistiques_indicateurs.csv"
)
print(
    DOSSIER_RAPPORTS
    / "validation_methodologique_distribution_sexe.csv"
)
print(
    DOSSIER_RAPPORTS
    / "validation_methodologique_evolution_indicateurs.csv"
)
print(chemin_synthese)

print("\n========== FIN DE LA VALIDATION ==========")
