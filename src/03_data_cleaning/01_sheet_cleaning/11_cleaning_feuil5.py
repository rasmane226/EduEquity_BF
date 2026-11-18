
from pathlib import Path
import pandas as pd


# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[3]

SOURCE_FILE = (
    ROOT_DIR / "data" / "01_raw_data" /
    "donnees_education_bf.xlsx"
)

OUTPUT_DIR = ROOT_DIR / "data" / "03_cleaned_data" / "final"

OUTPUT_FILE = OUTPUT_DIR / "nouveaux_inscrits_cp1_region_sexe.csv"


# ============================================================
# 2. DEFINITION DES VARIABLES
# ============================================================

ANNEES = [
    "2015-2016",
    "2016-2017",
    "2017-2018",
    "2018-2019",
    "2019-2020",
    "2020-2021",
    "2021-2022",
    "2022-2023",
    "2023-2024",
    "2024-2025"
]

SEXES = ["GARCONS", "FILLES"]

REGIONS_ATTENDUES = [
    "BOUCLE DU MOUHOUN",
    "CASCADES",
    "CENTRE",
    "CENTRE-EST",
    "CENTRE-NORD",
    "CENTRE-OUEST",
    "CENTRE-SUD",
    "EST",
    "HAUTS-BASSINS",
    "NORD",
    "PLATEAU CENTRAL",
    "SAHEL",
    "SUD-OUEST"
]


# ============================================================
# 3. LECTURE DE LA FEUILLE SOURCE
# ============================================================

def charger_donnees():

    if not SOURCE_FILE.exists():
        raise FileNotFoundError(
            f"Fichier source introuvable : {SOURCE_FILE}"
        )

    df = pd.read_excel(
        SOURCE_FILE,
        sheet_name="Feuil5",
        header=1
    )

    print("Dimensions initiales :", df.shape)

    return df


# ============================================================
# 4. NETTOYAGE DE LA STRUCTURE
# ============================================================

def nettoyer_structure(df):

    # Suppression des espaces dans les noms de colonnes
    df.columns = df.columns.astype(str).str.strip()

    # Vérification des colonnes attendues
    colonnes_attendues = ["REGION", "SEXE"] + ANNEES

    colonnes_manquantes = [
        col for col in colonnes_attendues
        if col not in df.columns
    ]

    if colonnes_manquantes:
        raise ValueError(
            f"Colonnes manquantes : {colonnes_manquantes}"
        )

    df = df[colonnes_attendues].copy()

    # Suppression des lignes totalement vides
    df = df.dropna(how="all")

    # Récupération des noms de régions sur les lignes suivantes
    df["REGION"] = df["REGION"].ffill()

    # Normalisation des variables textuelles
    df["REGION"] = (
        df["REGION"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["SEXE"] = (
        df["SEXE"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # Conservation des catégories attendues
    df = df[
        df["SEXE"].isin(["GARCONS", "FILLES", "TOTAL"])
    ].copy()

    return df


# ============================================================
# 5. CONVERSION DES VARIABLES NUMERIQUES
# ============================================================

def convertir_variables_numeriques(df):

    for annee in ANNEES:

        df[annee] = pd.to_numeric(
            df[annee],
            errors="coerce"
        )

    if df[ANNEES].isna().any().any():
        raise ValueError(
            "Des valeurs manquantes ou non numériques "
            "ont été détectées dans les effectifs."
        )

    if (df[ANNEES] < 0).any().any():
        raise ValueError(
            "Des effectifs négatifs ont été détectés."
        )

    return df


# ============================================================
# 6. CONTROLE DE COHERENCE DES DONNEES
# ============================================================

def controler_donnees(df):

    # Vérification des régions
    regions = sorted(
        df.loc[df["REGION"] != "NATIONAL", "REGION"].unique()
    )

    if sorted(REGIONS_ATTENDUES) != regions:
        raise ValueError(
            "La liste des régions ne correspond pas "
            "aux 13 régions attendues."
        )

    # Vérification des catégories par région
    for region in REGIONS_ATTENDUES + ["NATIONAL"]:

        categories = set(
            df.loc[df["REGION"] == region, "SEXE"]
        )

        if categories != {"GARCONS", "FILLES", "TOTAL"}:
            raise ValueError(
                f"Catégories incomplètes pour {region} : "
                f"{categories}"
            )

    # Vérification : GARCONS + FILLES = TOTAL
    for annee in ANNEES:

        tableau = df.pivot(
            index="REGION",
            columns="SEXE",
            values=annee
        )

        difference = (
            tableau["GARCONS"] +
            tableau["FILLES"] -
            tableau["TOTAL"]
        )

        if not (difference == 0).all():
            raise ValueError(
                f"Incohérence entre les sexes et le total "
                f"pour l'année {annee}."
            )

        # Vérification : somme des régions = NATIONAL
        somme_regions = tableau.loc[
            REGIONS_ATTENDUES, "TOTAL"
        ].sum()

        total_national = tableau.loc[
            "NATIONAL", "TOTAL"
        ]

        if somme_regions != total_national:
            raise ValueError(
                f"Incohérence entre les régions et le total "
                f"national pour {annee}."
            )

    print("Contrôle des totaux : VALIDÉ")
    print("Contrôle des 13 régions : VALIDÉ")
    print("Contrôle du total national : VALIDÉ")


# ============================================================
# 7. TRANSFORMATION AU FORMAT LONG
# ============================================================

def transformer_donnees(df):

    # Exclusion des lignes TOTAL et NATIONAL
    df = df[
        (df["REGION"] != "NATIONAL") &
        (df["SEXE"].isin(SEXES))
    ].copy()

    # Passage du format large au format long
    df_long = df.melt(
        id_vars=["REGION", "SEXE"],
        value_vars=ANNEES,
        var_name="ANNEE_SCOLAIRE",
        value_name="NOUVEAUX_INSCRITS_CP1"
    )

    # Organisation des colonnes
    df_long = df_long[
        [
            "REGION",
            "ANNEE_SCOLAIRE",
            "SEXE",
            "NOUVEAUX_INSCRITS_CP1"
        ]
    ]

    # Tri des observations
    df_long = df_long.sort_values(
        by=["REGION", "ANNEE_SCOLAIRE", "SEXE"]
    ).reset_index(drop=True)

    return df_long


# ============================================================
# 8. CONTROLE FINAL ET ENREGISTREMENT
# ============================================================

def enregistrer_donnees(df):

    if df.duplicated(
        subset=["REGION", "ANNEE_SCOLAIRE", "SEXE"]
    ).any():
        raise ValueError(
            "Des doublons ont été détectés."
        )

    if df.isna().any().any():
        raise ValueError(
            "Des valeurs manquantes sont présentes."
        )

    if len(df) != 260:
        raise ValueError(
            f"Nombre d'observations inattendu : {len(df)}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n========== RESULTAT FINAL ==========")
    print("Nombre d'observations :", len(df))
    print("Nombre de régions :", df["REGION"].nunique())
    print("Nombre d'années :", df["ANNEE_SCOLAIRE"].nunique())
    print("Catégories :", df["SEXE"].unique())
    print("Valeurs manquantes :", df.isna().sum().sum())
    print("Doublons :", df.duplicated().sum())
    print("Fichier enregistré :", OUTPUT_FILE)


# ============================================================
# 9. EXECUTION PRINCIPALE
# ============================================================

def main():

    print("========== NETTOYAGE FEUIL5 ==========")

    df = charger_donnees()

    df = nettoyer_structure(df)

    df = convertir_variables_numeriques(df)

    controler_donnees(df)

    df_final = transformer_donnees(df)

    enregistrer_donnees(df_final)

    print("\nNettoyage de Feuil5 terminé avec succès.")


if __name__ == "__main__":

    try:
        main()

    except Exception as erreur:
        print("\nERREUR :", erreur)
        raise
