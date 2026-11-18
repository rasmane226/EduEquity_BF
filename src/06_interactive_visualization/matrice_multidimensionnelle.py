
import pandas as pd

from config import (
    GENDER_DIR,
    URBAN_RURAL_DIR,
    PRIORITIZATION_DIR,
)


# ============================================================
# 1. CONFIGURATION DES FICHIERS
# ============================================================

# Analyse territoriale
TERRITORIAL_FILE = (
    PRIORITIZATION_DIR
    / "score_priorisation_territoriale.csv"
)

PROFILES_FILE = (
    PRIORITIZATION_DIR
    / "profils_regionaux.csv"
)

# Analyse des disparités de genre
GENDER_REGIONAL_FILE = (
    GENDER_DIR
    / "ecarts_moyens_par_region.csv"
)

# Analyse urbain-rural
URBAN_ANNUAL_FILE = (
    URBAN_RURAL_DIR
    / "evolution_annuelle_urbain_rural.csv"
)

URBAN_SEX_FILE = (
    URBAN_RURAL_DIR
    / "evolution_urbain_rural_par_sexe.csv"
)

URBAN_STATS_FILE = (
    URBAN_RURAL_DIR
    / "statistiques_urbain_rural_par_sexe.csv"
)


# Fichiers de sortie
OUTPUT_TERRITORIAL = (
    PRIORITIZATION_DIR / "matrice_territoriale.csv"
)

OUTPUT_GENDER = (
    PRIORITIZATION_DIR / "matrice_genre.csv"
)

OUTPUT_URBAN = (
    PRIORITIZATION_DIR / "matrice_urbain_rural.csv"
)

OUTPUT_FINAL = (
    PRIORITIZATION_DIR / "matrice_multidimensionnelle.csv"
)


# ============================================================
# 2. FONCTION GENERALE DE CHARGEMENT
# ============================================================

def load_csv(file_path, separator=";"):

    if not file_path.exists():

        raise FileNotFoundError(
            f"Fichier introuvable : {file_path}"
        )

    df = pd.read_csv(
        file_path,
        sep=separator,
        encoding="utf-8-sig"
    )

    # Nettoyage des noms de colonnes
    df.columns = (
        df.columns
        .str.strip()
    )

    return df


# ============================================================
# 3. NORMALISATION DES NOMS DE REGIONS
# ============================================================

def normalize_region_names(df):

    df = df.copy()

    # Uniformisation des noms de régions
    df["REGION"] = (
        df["REGION"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.upper()
    )

    return df


# ============================================================
# 4. CHARGEMENT DES DONNEES TERRITORIALES
# ============================================================

def load_territorial_data():

    print("\n========== DONNEES TERRITORIALES ==========")

    territorial = load_csv(
        TERRITORIAL_FILE,
        separator=";"
    )

    profiles = load_csv(
        PROFILES_FILE,
        separator=";"
    )

    territorial = normalize_region_names(territorial)

    profiles = normalize_region_names(profiles)

    required_territorial = [
        "REGION",
        "NON_FREQUENTATION_PCT",
        "DESCOLARISATION_PCT",
        "SCORE_PRIORISATION",
        "RANG",
    ]

    required_profiles = [
        "REGION",
        "PROFIL_REGIONAL",
    ]

    for column in required_territorial:

        if column not in territorial.columns:

            raise ValueError(
                f"Colonne absente des données territoriales : "
                f"{column}"
            )

    for column in required_profiles:

        if column not in profiles.columns:

            raise ValueError(
                f"Colonne absente des profils régionaux : "
                f"{column}"
            )

    territorial = territorial[
        required_territorial
    ].copy()

    profiles = profiles[
        required_profiles
    ].copy()

    # Vérification des doublons
    if territorial["REGION"].duplicated().any():

        raise ValueError(
            "Doublons dans les données territoriales."
        )

    if profiles["REGION"].duplicated().any():

        raise ValueError(
            "Doublons dans les profils régionaux."
        )

    # Association des scores et des profils
    territorial = territorial.merge(
        profiles,
        on="REGION",
        how="left",
        validate="one_to_one"
    )

    if territorial["PROFIL_REGIONAL"].isna().any():

        raise ValueError(
            "Certains profils régionaux sont manquants."
        )

    if len(territorial) != 13:

        raise ValueError(
            f"13 régions attendues, "
            f"{len(territorial)} détectées."
        )

    print("Nombre de régions :", len(territorial))

    print("Données territoriales chargées.")

    return territorial


# ============================================================
# 5. CHARGEMENT DES DONNEES DE GENRE
# ============================================================

def load_gender_data():

    print("\n========== DONNEES DE GENRE ==========")

    # Le fichier utilise une virgule comme séparateur
    gender = load_csv(
        GENDER_REGIONAL_FILE,
        separator=","
    )

    gender = normalize_region_names(gender)

    print("Dimensions :", gender.shape)

    print("Colonnes :", gender.columns.tolist())

    required_columns = [
        "REGION",
        "ECART_TBA",
        "ECART_TBS",
        "ECART_TAP",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in gender.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Colonnes manquantes dans les données de genre : "
            f"{missing_columns}"
        )

    gender = gender[required_columns].copy()

    # Conversion des indicateurs en valeurs numériques
    for column in [
        "ECART_TBA",
        "ECART_TBS",
        "ECART_TAP",
    ]:

        gender[column] = pd.to_numeric(
            gender[column],
            errors="coerce"
        )

    if gender.isnull().any().any():

        raise ValueError(
            "Valeurs manquantes dans les données de genre."
        )

    if gender["REGION"].duplicated().any():

        raise ValueError(
            "Doublons dans les données de genre."
        )

    if len(gender) != 13:

        raise ValueError(
            f"13 régions attendues dans les données de genre, "
            f"{len(gender)} détectées."
        )

    print("Données de genre chargées.")

    return gender


# ============================================================
# 6. CHARGEMENT DES DONNEES URBAIN-RURAL
# ============================================================

def load_urban_data():

    print("\n========== DONNEES URBAIN-RURAL ==========")

    # Les trois fichiers utilisent une virgule
    annual = load_csv(
        URBAN_ANNUAL_FILE,
        separator=","
    )

    by_sex = load_csv(
        URBAN_SEX_FILE,
        separator=","
    )

    statistics = load_csv(
        URBAN_STATS_FILE,
        separator=","
    )

    print("Données annuelles :", annual.shape)

    print("Colonnes annuelles :", annual.columns.tolist())

    print("Données par sexe :", by_sex.shape)

    print("Colonnes par sexe :", by_sex.columns.tolist())

    print("Statistiques :", statistics.shape)

    print("Colonnes statistiques :", statistics.columns.tolist())

    # Colonnes attendues dans les données annuelles
    required_annual = [
        "ANNEE_SCOLAIRE",
        "EFFECTIF_URBAIN_TOTAL",
        "EFFECTIF_RURAL_TOTAL",
        "ECART_TOTAL",
        "RATIO_URBAIN_RURAL",
        "PART_URBAINE_DANS_TOTAL",
    ]

    # Colonnes attendues dans les données par sexe
    required_sex = [
        "ANNEE_SCOLAIRE",
        "SEXE",
        "EFFECTIF_URBAIN",
        "EFFECTIF_RURAL",
        "ECART_URBAIN_MOINS_RURAL",
        "RATIO_URBAIN_RURAL",
    ]

    # Vérification des données annuelles
    for column in required_annual:

        if column not in annual.columns:

            raise ValueError(
                f"Colonne absente des données annuelles : "
                f"{column}"
            )

    # Vérification des données par sexe
    for column in required_sex:

        if column not in by_sex.columns:

            raise ValueError(
                f"Colonne absente des données par sexe : "
                f"{column}"
            )

    if "SEXE" not in statistics.columns:

        raise ValueError(
            "Colonne SEXE absente des statistiques."
        )

    print("\nValidation des fichiers urbain-rural réussie.")

    return annual, by_sex, statistics


# ============================================================
# 7. PREPARATION DE LA MATRICE TERRITORIALE
# ============================================================

def prepare_territorial_matrix(territorial):

    columns = [
        "REGION",
        "NON_FREQUENTATION_PCT",
        "DESCOLARISATION_PCT",
        "SCORE_PRIORISATION",
        "RANG",
        "PROFIL_REGIONAL",
    ]

    result = territorial[columns].copy()

    result = result.rename(
        columns={
            "NON_FREQUENTATION_PCT":
                "NON_FREQUENTATION_RGPH2019_PCT",

            "DESCOLARISATION_PCT":
                "DESCOLARISATION_RGPH2019_PCT",

            "SCORE_PRIORISATION":
                "SCORE_TERRITORIAL",

            "RANG":
                "RANG_PRIORITE_TERRITORIALE",
        }
    )

    result["SOURCE_TERRITORIALE"] = (
        "INSD - RGPH 2019 - Enfants de 6 à 11 ans"
    )

    return result


# ============================================================
# 8. PREPARATION DE LA MATRICE DE GENRE
# ============================================================

def prepare_gender_matrix(gender):

    result = gender.copy()

    result["SOURCE_GENRE"] = (
        "DGESS - Analyse des écarts de genre"
    )

    return result


# ============================================================
# 9. PREPARATION DES DONNEES URBAIN-RURAL
# ============================================================

def prepare_urban_matrix(
    annual,
    by_sex,
    statistics
):

    if annual.empty:

        raise ValueError(
            "Le fichier annuel urbain-rural est vide."
        )

    # Sélection de la dernière année disponible
    annual = annual.sort_values(
        "ANNEE_SCOLAIRE"
    )

    annual_summary = annual.iloc[-1]

    urban_summary = pd.DataFrame([
        {
            "DIMENSION": "Urbain-rural",

            "ANNEE_SCOLAIRE": (
                annual_summary["ANNEE_SCOLAIRE"]
            ),

            "EFFECTIF_URBAIN": (
                annual_summary["EFFECTIF_URBAIN_TOTAL"]
            ),

            "EFFECTIF_RURAL": (
                annual_summary["EFFECTIF_RURAL_TOTAL"]
            ),

            "ECART_URBAIN_MOINS_RURAL": (
                annual_summary["ECART_TOTAL"]
            ),

            "RATIO_URBAIN_RURAL": (
                annual_summary["RATIO_URBAIN_RURAL"]
            ),

            "PART_URBAINE_PCT": (
                annual_summary["PART_URBAINE_DANS_TOTAL"]
            ),

            "SOURCE": "DGESS - Données annuelles",
        }
    ])

    # Données par sexe
    sex_summary = by_sex.copy()

    sex_summary["SOURCE"] = (
        "DGESS - Données annuelles par sexe"
    )

    # Statistiques descriptives
    statistics_summary = statistics.copy()

    statistics_summary["SOURCE"] = (
        "DGESS - Statistiques descriptives"
    )

    return (
        urban_summary,
        sex_summary,
        statistics_summary
    )


# ============================================================
# 10. VERIFICATION DES CORRESPONDANCES REGIONALES
# ============================================================

def verify_region_matching(
    territorial_matrix,
    gender_matrix
):

    territorial_regions = set(
        territorial_matrix["REGION"]
    )

    gender_regions = set(
        gender_matrix["REGION"]
    )

    missing_gender = (
        territorial_regions - gender_regions
    )

    unexpected_gender = (
        gender_regions - territorial_regions
    )

    print("\n========== CORRESPONDANCE DES REGIONS ==========")

    print(
        "Régions territoriales :",
        len(territorial_regions)
    )

    print(
        "Régions de genre :",
        len(gender_regions)
    )

    print(
        "Régions sans données de genre :",
        sorted(missing_gender)
    )

    print(
        "Régions supplémentaires dans les données de genre :",
        sorted(unexpected_gender)
    )

    if missing_gender or unexpected_gender:

        raise ValueError(
            "Les régions des deux sources ne correspondent pas. "
            "Vérifie les noms avant de poursuivre."
        )

    print(
        "Les 13 régions correspondent entre les deux sources."
    )


# ============================================================
# 11. CONSTRUCTION DE LA MATRICE MULTIDIMENSIONNELLE
# ============================================================

def build_multidimensional_matrix(
    territorial_matrix,
    gender_matrix
):

    verify_region_matching(
        territorial_matrix,
        gender_matrix
    )

    final_matrix = territorial_matrix.merge(
        gender_matrix,
        on="REGION",
        how="left",
        validate="one_to_one",
        suffixes=("", "_GENRE")
    )

    print("\n========== MATRICE MULTIDIMENSIONNELLE ==========")

    print("Nombre de régions :", len(final_matrix))

    print("Dimensions :", final_matrix.shape)

    return final_matrix


# ============================================================
# 12. EXPORTATION DES MATRICES
# ============================================================

def export_matrices(
    territorial_matrix,
    gender_matrix,
    urban_summary,
    sex_summary,
    statistics_summary,
    final_matrix
):

    PRIORITIZATION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Matrice territoriale
    territorial_matrix.to_csv(
        OUTPUT_TERRITORIAL,
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    # Matrice de genre
    gender_matrix.to_csv(
        OUTPUT_GENDER,
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    # Synthèse urbain-rural
    urban_summary.to_csv(
        OUTPUT_URBAN,
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    # Données urbain-rural par sexe
    sex_summary.to_csv(
        PRIORITIZATION_DIR
        / "matrice_urbain_rural_par_sexe.csv",
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    # Statistiques descriptives urbain-rural
    statistics_summary.to_csv(
        PRIORITIZATION_DIR
        / "matrice_statistiques_urbain_rural.csv",
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    # Matrice multidimensionnelle finale
    final_matrix.to_csv(
        OUTPUT_FINAL,
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    print("\n========== EXPORTATION ==========")

    print("Matrice territoriale :", OUTPUT_TERRITORIAL)

    print("Matrice genre :", OUTPUT_GENDER)

    print("Matrice urbain-rural :", OUTPUT_URBAN)

    print("Matrice multidimensionnelle :", OUTPUT_FINAL)


# ============================================================
# 13. AFFICHAGE DES RESULTATS
# ============================================================

def display_results(
    final_matrix,
    urban_summary
):

    print("\n========== APERCU DE LA MATRICE ==========")

    display_columns = [
        "REGION",
        "SCORE_TERRITORIAL",
        "RANG_PRIORITE_TERRITORIALE",
        "PROFIL_REGIONAL",
        "ECART_TBA",
        "ECART_TBS",
        "ECART_TAP",
    ]

    print(
        final_matrix[
            display_columns
        ].to_string(index=False)
    )

    print("\n========== SYNTHESE URBAIN-RURAL ==========")

    print(
        urban_summary.to_string(index=False)
    )

    print("\nAnalyse multidimensionnelle terminée.")


# ============================================================
# 14. PIPELINE PRINCIPAL
# ============================================================

def main():

    # 1. Chargement des données
    territorial = load_territorial_data()

    gender = load_gender_data()

    annual, by_sex, statistics = load_urban_data()

    # 2. Préparation territoriale
    territorial_matrix = (
        prepare_territorial_matrix(territorial)
    )

    # 3. Préparation genre
    gender_matrix = (
        prepare_gender_matrix(gender)
    )

    # 4. Préparation urbain-rural
    (
        urban_summary,
        sex_summary,
        statistics_summary
    ) = prepare_urban_matrix(
        annual,
        by_sex,
        statistics
    )

    # 5. Construction de la matrice
    final_matrix = build_multidimensional_matrix(
        territorial_matrix,
        gender_matrix
    )

    # 6. Exportation
    export_matrices(
        territorial_matrix,
        gender_matrix,
        urban_summary,
        sex_summary,
        statistics_summary,
        final_matrix
    )

    # 7. Affichage
    display_results(
        final_matrix,
        urban_summary
    )


# ============================================================
# 15. EXECUTION
# ============================================================

if __name__ == "__main__":

    main()
