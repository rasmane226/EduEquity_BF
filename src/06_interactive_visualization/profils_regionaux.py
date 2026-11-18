
import pandas as pd

from config import PRIORITIZATION_DIR


# ============================================================
# 1. CONFIGURATION
# ============================================================

INPUT_FILE = (
    PRIORITIZATION_DIR
    / "score_priorisation_territoriale.csv"
)

OUTPUT_FILE = (
    PRIORITIZATION_DIR
    / "profils_regionaux.csv"
)


# ============================================================
# 2. CHARGEMENT DES DONNEES
# ============================================================

def load_data():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Fichier introuvable : {INPUT_FILE}\n"
            "Exécute d'abord calculer_score_territorial.py."
        )

    df = pd.read_csv(
        INPUT_FILE,
        sep=";"
    )

    print("\n========== CHARGEMENT DES DONNEES ==========")

    print("Dimensions :", df.shape)

    return df


# ============================================================
# 3. VALIDATION DES DONNEES
# ============================================================

def validate_data(df):

    required_columns = [
        "REGION",
        "SCORE_NON_FREQUENTATION",
        "SCORE_DESCOLARISATION",
        "SCORE_PRIORISATION",
        "RANG",
    ]

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

    numeric_columns = [
        "SCORE_NON_FREQUENTATION",
        "SCORE_DESCOLARISATION",
        "SCORE_PRIORISATION",
        "RANG",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    if df.isnull().any().any():

        raise ValueError(
            "Des valeurs manquantes ou non numériques "
            "ont été détectées."
        )

    if df["REGION"].duplicated().any():

        raise ValueError(
            "Des régions sont présentes plusieurs fois."
        )

    if len(df) != 13:

        raise ValueError(
            f"13 régions attendues, {len(df)} détectées."
        )

    print("\n========== VALIDATION ==========")

    print("Nombre de régions :", len(df))

    print("Valeurs manquantes : aucune")

    print("Doublons : aucun")

    return df


# ============================================================
# 4. CALCUL DES MEDIANES REGIONALES
# ============================================================

def calculate_medians(df):

    median_non_attendance = (
        df["SCORE_NON_FREQUENTATION"].median()
    )

    median_dropout = (
        df["SCORE_DESCOLARISATION"].median()
    )

    print("\n========== MEDIANES DE REFERENCE ==========")

    print(
        "Médiane non-fréquentation :",
        round(median_non_attendance, 2)
    )

    print(
        "Médiane déscolarisation :",
        round(median_dropout, 2)
    )

    return median_non_attendance, median_dropout


# ============================================================
# 5. CLASSIFICATION DES PROFILS REGIONAUX
# ============================================================

def classify_profiles(
    df,
    median_non_attendance,
    median_dropout
):

    df = df.copy()

    # Comparaison des scores avec leurs médianes
    df["NON_FREQUENTATION_ELEVEE"] = (
        df["SCORE_NON_FREQUENTATION"]
        >= median_non_attendance
    )

    df["DESCOLARISATION_ELEVEE"] = (
        df["SCORE_DESCOLARISATION"]
        >= median_dropout
    )

    def assign_profile(row):

        non_attendance = row[
            "NON_FREQUENTATION_ELEVEE"
        ]

        dropout = row[
            "DESCOLARISATION_ELEVEE"
        ]

        if non_attendance and dropout:

            return "Difficultés cumulées"

        elif non_attendance and not dropout:

            return "Non-fréquentation dominante"

        elif not non_attendance and dropout:

            return "Déscolarisation dominante"

        else:

            return "Difficultés relativement moins élevées"

    df["PROFIL_REGIONAL"] = df.apply(
        assign_profile,
        axis=1
    )

    print("\n========== CLASSIFICATION ==========")

    print(
        df[
            ["REGION", "PROFIL_REGIONAL"]
        ].to_string(index=False)
    )

    return df


# ============================================================
# 6. DESCRIPTION DES PROFILS
# ============================================================

def describe_profiles(df):

    descriptions = {

        "Difficultés cumulées":
            "Niveaux relativement élevés de "
            "non-fréquentation et de déscolarisation.",

        "Non-fréquentation dominante":
            "La non-fréquentation est relativement élevée, "
            "tandis que la déscolarisation est plus faible.",

        "Déscolarisation dominante":
            "La déscolarisation est relativement élevée, "
            "tandis que la non-fréquentation est plus faible.",

        "Difficultés relativement moins élevées":
            "Les deux indicateurs sont inférieurs "
            "aux médianes régionales."
    }

    df["DESCRIPTION_PROFIL"] = (
        df["PROFIL_REGIONAL"].map(descriptions)
    )

    return df


# ============================================================
# 7. PREPARATION DU TABLEAU FINAL
# ============================================================

def prepare_final_table(df):

    columns = [
        "RANG",
        "REGION",
        "SCORE_NON_FREQUENTATION",
        "SCORE_DESCOLARISATION",
        "SCORE_PRIORISATION",
        "PROFIL_REGIONAL",
        "DESCRIPTION_PROFIL",
    ]

    result = df[columns].copy()

    numeric_columns = [
        "SCORE_NON_FREQUENTATION",
        "SCORE_DESCOLARISATION",
        "SCORE_PRIORISATION",
    ]

    result[numeric_columns] = (
        result[numeric_columns].round(2)
    )

    result = result.sort_values(
        "RANG"
    ).reset_index(drop=True)

    return result


# ============================================================
# 8. ANALYSE DE LA REPARTITION DES PROFILS
# ============================================================

def analyze_profiles(df):

    distribution = (
        df["PROFIL_REGIONAL"]
        .value_counts()
        .rename_axis("PROFIL_REGIONAL")
        .reset_index(name="NOMBRE_REGIONS")
    )

    distribution["POURCENTAGE"] = (
        distribution["NOMBRE_REGIONS"]
        / len(df)
        * 100
    ).round(2)

    print("\n========== REPARTITION DES PROFILS ==========")

    print(
        distribution.to_string(index=False)
    )

    return distribution


# ============================================================
# 9. EXPORTATION DES RESULTATS
# ============================================================

def export_results(df, distribution):

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

    distribution.to_csv(
        PRIORITIZATION_DIR / "distribution_profils_regionaux.csv",
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    print("\n========== EXPORTATION ==========")

    print("Tableau des profils :")
    print(OUTPUT_FILE)

    print("\nDistribution des profils :")
    print(
        PRIORITIZATION_DIR
        / "distribution_profils_regionaux.csv"
    )


# ============================================================
# 10. PIPELINE PRINCIPAL
# ============================================================

def main():

    # 1. Chargement
    df = load_data()

    # 2. Validation
    df = validate_data(df)

    # 3. Calcul des médianes
    median_non_attendance, median_dropout = (
        calculate_medians(df)
    )

    # 4. Classification
    df = classify_profiles(
        df,
        median_non_attendance,
        median_dropout
    )

    # 5. Description
    df = describe_profiles(df)

    # 6. Tableau final
    result = prepare_final_table(df)

    # 7. Analyse de la distribution
    distribution = analyze_profiles(result)

    # 8. Exportation
    export_results(
        result,
        distribution
    )

    print(
        "\nAnalyse des profils régionaux terminée."
    )


# ============================================================
# 11. EXECUTION
# ============================================================

if __name__ == "__main__":

    main()
