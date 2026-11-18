
import pandas as pd
import numpy as np

from config import (
    URBAN_RURAL_DIR,
    PRIORITIZATION_DIR,
)


# ============================================================
# 1. CONFIGURATION
# ============================================================

INSD_DIR = URBAN_RURAL_DIR / "insd_rgph_2019"

INPUT_FILE = (
    INSD_DIR / "situation_scolaire_6_11_ans_par_region.csv"
)

OUTPUT_FILE = (
    PRIORITIZATION_DIR / "score_priorisation_territoriale.csv"
)

# Pondérations validées
WEIGHT_NEVER_ATTENDED = 0.50
WEIGHT_DROPOUT = 0.50

# Nombre de régions administratives attendues
EXPECTED_REGIONS = 13

# Régions administratives du Burkina Faso
EXPECTED_REGION_NAMES = [
    "Boucle du Mouhoun",
    "Cascades",
    "Centre",
    "Centre-Est",
    "Centre-Nord",
    "Centre-Ouest",
    "Centre-Sud",
    "Est",
    "Hauts-Bassins",
    "Nord",
    "Plateau Central",
    "Sahel",
    "Sud-Ouest",
]


# ============================================================
# 2. CHARGEMENT DES DONNEES
# ============================================================

def load_data():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Fichier introuvable : {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    print("\n========== CHARGEMENT DES DONNEES ==========")

    print("Dimensions initiales :", df.shape)

    print("\nColonnes :")
    print(df.columns.tolist())

    return df


# ============================================================
# 3. VALIDATION ET NETTOYAGE DES DONNEES
# ============================================================

def validate_data(df):

    required_columns = [
        "REGION",
        "JAMAIS_FREQUENTE_PCT",
        "DESCOLARISE_PCT",
    ]

    # Vérification des colonnes nécessaires
    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Colonnes manquantes : {missing_columns}"
        )

    df = df[required_columns].copy()

    # Nettoyage des noms de régions
    df["REGION"] = (
        df["REGION"]
        .astype(str)
        .str.strip()
    )

    # Exclusion de la ligne nationale
    df = df[
        df["REGION"].str.lower() != "burkina faso"
    ].copy()

    print(
        "\nLigne nationale exclue du classement territorial."
    )

    # Conversion des indicateurs en valeurs numériques
    numeric_columns = [
        "JAMAIS_FREQUENTE_PCT",
        "DESCOLARISE_PCT",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Vérification des valeurs manquantes
    if df[required_columns].isnull().any().any():

        missing = df[
            df[required_columns].isnull().any(axis=1)
        ]

        raise ValueError(
            "Des valeurs manquantes ont été détectées :\n"
            f"{missing}"
        )

    # Vérification des doublons
    if df["REGION"].duplicated().any():

        duplicates = df.loc[
            df["REGION"].duplicated(keep=False),
            "REGION"
        ].tolist()

        raise ValueError(
            f"Régions en double : {duplicates}"
        )

    # Vérification des 13 régions attendues
    actual_regions = set(df["REGION"])

    expected_regions = set(EXPECTED_REGION_NAMES)

    missing_regions = (
        expected_regions - actual_regions
    )

    unexpected_regions = (
        actual_regions - expected_regions
    )

    if missing_regions or unexpected_regions:

        raise ValueError(
            "\nProblème dans les régions détectées."
            f"\nRégions manquantes : {sorted(missing_regions)}"
            f"\nRégions inattendues : {sorted(unexpected_regions)}"
        )

    if len(df) != EXPECTED_REGIONS:

        raise ValueError(
            f"{EXPECTED_REGIONS} régions attendues, "
            f"{len(df)} détectées."
        )

    # Vérification des pourcentages
    for column in numeric_columns:

        if not df[column].between(0, 100).all():

            raise ValueError(
                f"Valeurs hors de l'intervalle 0-100 "
                f"dans {column}"
            )

    print("\n========== VALIDATION ==========")

    print("Nombre de régions :", len(df))

    print("Valeurs manquantes : aucune")

    print("Doublons régionaux : aucun")

    print("Ligne nationale : exclue")

    print("Les 13 régions attendues sont présentes.")

    return df


# ============================================================
# 4. NORMALISATION MIN-MAX
# ============================================================

def normalize_min_max(series):

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:

        return pd.Series(
            0.0,
            index=series.index
        )

    normalized = (
        (series - minimum)
        / (maximum - minimum)
    ) * 100

    return normalized


def normalize_indicators(df):

    df = df.copy()

    # Normalisation de la non-fréquentation
    df["SCORE_NON_FREQUENTATION"] = normalize_min_max(
        df["JAMAIS_FREQUENTE_PCT"]
    )

    # Normalisation de la déscolarisation
    df["SCORE_DESCOLARISATION"] = normalize_min_max(
        df["DESCOLARISE_PCT"]
    )

    print("\n========== NORMALISATION ==========")

    print(
        "Non-fréquentation : normalisation entre 0 et 100"
    )

    print(
        "Déscolarisation : normalisation entre 0 et 100"
    )

    return df


# ============================================================
# 5. CALCUL DU SCORE DE PRIORISATION
# ============================================================

def calculate_priority_score(df):

    df = df.copy()

    # Score composite avec pondération égale
    df["SCORE_PRIORISATION"] = (
        WEIGHT_NEVER_ATTENDED
        * df["SCORE_NON_FREQUENTATION"]
        +
        WEIGHT_DROPOUT
        * df["SCORE_DESCOLARISATION"]
    )

    # Classement décroissant
    # Le score le plus élevé indique une priorité relative
    df = df.sort_values(
        "SCORE_PRIORISATION",
        ascending=False
    ).reset_index(drop=True)

    # Attribution des rangs
    df["RANG_PRIORITE"] = (
        df["SCORE_PRIORISATION"]
        .rank(
            method="min",
            ascending=False
        )
        .astype(int)
    )

    print("\n========== CALCUL DU SCORE ==========")

    print("Pondération non-fréquentation : 50 %")

    print("Pondération déscolarisation : 50 %")

    print("Score calculé avec succès.")

    return df


# ============================================================
# 6. PREPARATION DU TABLEAU FINAL
# ============================================================

def prepare_final_table(df):

    columns = [
        "RANG_PRIORITE",
        "REGION",
        "JAMAIS_FREQUENTE_PCT",
        "DESCOLARISE_PCT",
        "SCORE_NON_FREQUENTATION",
        "SCORE_DESCOLARISATION",
        "SCORE_PRIORISATION",
    ]

    result = df[columns].copy()

    # Renommage des colonnes
    result = result.rename(
        columns={
            "RANG_PRIORITE": "RANG",
            "JAMAIS_FREQUENTE_PCT": (
                "NON_FREQUENTATION_PCT"
            ),
            "DESCOLARISE_PCT": (
                "DESCOLARISATION_PCT"
            ),
        }
    )

    # Arrondi à deux décimales
    numeric_columns = [
        "NON_FREQUENTATION_PCT",
        "DESCOLARISATION_PCT",
        "SCORE_NON_FREQUENTATION",
        "SCORE_DESCOLARISATION",
        "SCORE_PRIORISATION",
    ]

    result[numeric_columns] = (
        result[numeric_columns].round(2)
    )

    return result


# ============================================================
# 7. EXPORTATION DES RESULTATS
# ============================================================

def export_results(df):

    PRIORITIZATION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    print("\n========== EXPORTATION ==========")

    print("Fichier enregistré :")

    print(OUTPUT_FILE)


# ============================================================
# 8. AFFICHAGE DES RESULTATS
# ============================================================

def display_results(df):

    print("\n========== CLASSEMENT TERRITORIAL ==========")

    print(
        df.to_string(
            index=False
        )
    )

    print("\n========== STATISTIQUES DU SCORE ==========")

    print(
        df["SCORE_PRIORISATION"].describe().round(2)
    )

    print("\n========== REGION PRIORITAIRE ==========")

    first_region = df.iloc[0]

    print(
        "Région :", first_region["REGION"]
    )

    print(
        "Score :", first_region["SCORE_PRIORISATION"]
    )

    print(
        "\nAttention : ce classement exprime une priorité "
        "relative entre les 13 régions étudiées, "
        "à partir des données du RGPH 2019. "
        "Il ne constitue pas une mesure officielle "
        "de l'accès à l'éducation."
    )


# ============================================================
# 9. PIPELINE PRINCIPAL
# ============================================================

def main():

    # 1. Chargement des données
    df = load_data()

    # 2. Validation et nettoyage
    df = validate_data(df)

    # 3. Normalisation
    df = normalize_indicators(df)

    # 4. Calcul du score
    df = calculate_priority_score(df)

    # 5. Préparation du tableau final
    result = prepare_final_table(df)

    # 6. Exportation
    export_results(result)

    # 7. Affichage des résultats
    display_results(result)


# ============================================================
# 10. EXECUTION
# ============================================================

if __name__ == "__main__":

    main()
