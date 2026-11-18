
import pandas as pd

from config import (
    URBAN_RURAL_DIR,
    PRIORITIZATION_DIR,
)


# ============================================================
# 1. CONFIGURATION
# ============================================================

MATRIX_FILE = (
    PRIORITIZATION_DIR
    / "matrice_multidimensionnelle.csv"
)

URBAN_ANNUAL_FILE = (
    URBAN_RURAL_DIR
    / "evolution_annuelle_urbain_rural.csv"
)

OUTPUT_REGIONAL = (
    PRIORITIZATION_DIR
    / "diagnostic_disparites_regionaux.csv"
)

OUTPUT_URBAN = (
    PRIORITIZATION_DIR
    / "diagnostic_urbain_rural.csv"
)

# Colonnes de genre
GENDER_INDICATORS = [
    "ECART_TBA",
    "ECART_TBS",
    "ECART_TAP",
]


# ============================================================
# 2. CHARGEMENT DES DONNEES
# ============================================================

def load_data():

    print("\n========== CHARGEMENT DES DONNEES ==========")

    if not MATRIX_FILE.exists():

        raise FileNotFoundError(
            f"Matrice introuvable : {MATRIX_FILE}"
        )

    if not URBAN_ANNUAL_FILE.exists():

        raise FileNotFoundError(
            f"Fichier urbain-rural introuvable : "
            f"{URBAN_ANNUAL_FILE}"
        )

    # La matrice finale utilise le point-virgule
    regional = pd.read_csv(
        MATRIX_FILE,
        sep=";",
        encoding="utf-8-sig"
    )

    # Le fichier annuel urbain-rural utilise la virgule
    urban = pd.read_csv(
        URBAN_ANNUAL_FILE,
        sep=",",
        encoding="utf-8-sig"
    )

    regional.columns = regional.columns.str.strip()
    urban.columns = urban.columns.str.strip()

    print("Matrice régionale :", regional.shape)

    print("Données urbain-rural :", urban.shape)

    return regional, urban


# ============================================================
# 3. VALIDATION DES DONNEES
# ============================================================

def validate_data(regional, urban):

    print("\n========== VALIDATION DES DONNEES ==========")

    required_regional = [
        "REGION",
        "SCORE_TERRITORIAL",
        "RANG_PRIORITE_TERRITORIALE",
        "PROFIL_REGIONAL",
        "ECART_TBA",
        "ECART_TBS",
        "ECART_TAP",
    ]

    required_urban = [
        "ANNEE_SCOLAIRE",
        "EFFECTIF_URBAIN_TOTAL",
        "EFFECTIF_RURAL_TOTAL",
        "ECART_TOTAL",
        "RATIO_URBAIN_RURAL",
        "PART_URBAINE_DANS_TOTAL",
    ]

    for column in required_regional:

        if column not in regional.columns:

            raise ValueError(
                f"Colonne manquante dans la matrice : {column}"
            )

    for column in required_urban:

        if column not in urban.columns:

            raise ValueError(
                f"Colonne manquante dans le fichier urbain-rural : "
                f"{column}"
            )

    # Conversion numérique
    numeric_regional = [
        "SCORE_TERRITORIAL",
        "RANG_PRIORITE_TERRITORIALE",
        *GENDER_INDICATORS,
    ]

    for column in numeric_regional:

        regional[column] = pd.to_numeric(
            regional[column],
            errors="coerce"
        )

    if regional[numeric_regional].isnull().any().any():

        raise ValueError(
            "Valeurs manquantes ou non numériques "
            "dans la matrice régionale."
        )

    if regional["REGION"].duplicated().any():

        raise ValueError(
            "Des régions sont présentes plusieurs fois."
        )

    if len(regional) != 13:

        raise ValueError(
            f"13 régions attendues, {len(regional)} détectées."
        )

    if urban.empty:

        raise ValueError(
            "Le fichier urbain-rural est vide."
        )

    print("Régions analysées :", len(regional))

    print("Valeurs régionales valides.")

    print("Validation terminée.")

    return regional, urban


# ============================================================
# 4. DIAGNOSTIC DES DISPARITES DE GENRE
# ============================================================

def diagnose_gender(row):

    values = {
        "TBA": row["ECART_TBA"],
        "TBS": row["ECART_TBS"],
        "TAP": row["ECART_TAP"],
    }

    girls_disadvantaged = [
        indicator
        for indicator, value in values.items()
        if value < 0
    ]

    boys_disadvantaged = [
        indicator
        for indicator, value in values.items()
        if value > 0
    ]

    parity = [
        indicator
        for indicator, value in values.items()
        if value == 0
    ]

    # Les trois indicateurs sont à zéro
    if len(parity) == 3:

        profile = "Parité sur les trois indicateurs"

    # Les trois indicateurs indiquent un désavantage des filles
    elif len(girls_disadvantaged) == 3:

        profile = "Désavantage des filles"

    # Les trois indicateurs indiquent un désavantage des garçons
    elif len(boys_disadvantaged) == 3:

        profile = "Désavantage des garçons"

    # Les indicateurs présentent des directions différentes
    elif girls_disadvantaged and boys_disadvantaged:

        profile = "Écarts contrastés selon l'indicateur"

    # Un ou plusieurs indicateurs négatifs, aucun positif
    elif girls_disadvantaged:

        profile = "Désavantage des filles sur certains indicateurs"

    # Un ou plusieurs indicateurs positifs, aucun négatif
    elif boys_disadvantaged:

        profile = "Désavantage des garçons sur certains indicateurs"

    else:

        profile = "Situation à examiner"

    return pd.Series({

        "DIAGNOSTIC_GENRE": profile,

        "NB_INDICATEURS_DESAVANTAGE_FILLES":
            len(girls_disadvantaged),

        "NB_INDICATEURS_DESAVANTAGE_GARCONS":
            len(boys_disadvantaged),

        "INDICATEURS_DESAVANTAGE_FILLES":
            ", ".join(girls_disadvantaged),

        "INDICATEURS_DESAVANTAGE_GARCONS":
            ", ".join(boys_disadvantaged),

        "INDICATEURS_PARITE":
            ", ".join(parity),
    })


def analyze_gender(regional):

    print("\n========== DIAGNOSTIC DE GENRE ==========")

    gender_diagnostics = regional.apply(
        diagnose_gender,
        axis=1
    )

    result = pd.concat(
        [
            regional.reset_index(drop=True),
            gender_diagnostics.reset_index(drop=True)
        ],
        axis=1
    )

    print(
        result[
            ["REGION", "DIAGNOSTIC_GENRE"]
        ].to_string(index=False)
    )

    return result


# ============================================================
# 5. DIAGNOSTIC TERRITORIAL
# ============================================================

def analyze_territorial(regional):

    print("\n========== DIAGNOSTIC TERRITORIAL ==========")

    result = regional.copy()

    median_score = result[
        "SCORE_TERRITORIAL"
    ].median()

    print(
        "Médiane du score territorial :",
        round(median_score, 2)
    )

    result["NIVEAU_DIFFICULTE_TERRITORIALE"] = (
        result["SCORE_TERRITORIAL"].apply(
            lambda score:
                "Difficulté relative élevée"
                if score >= median_score
                else "Difficulté relative moins élevée"
        )
    )

    print(
        result[
            [
                "REGION",
                "SCORE_TERRITORIAL",
                "NIVEAU_DIFFICULTE_TERRITORIALE",
            ]
        ].to_string(index=False)
    )

    return result


# ============================================================
# 6. DIAGNOSTIC COMBINE TERRITOIRE ET GENRE
# ============================================================

def build_combined_diagnosis(regional):

    print("\n========== DIAGNOSTIC COMBINE ==========")

    result = regional.copy()

    def combine(row):

        territorial = row[
            "NIVEAU_DIFFICULTE_TERRITORIALE"
        ]

        gender = row[
            "DIAGNOSTIC_GENRE"
        ]

        if territorial == "Difficulté relative élevée":

            if gender == "Désavantage des filles":

                return (
                    "Difficulté territoriale élevée "
                    "et désavantage des filles"
                )

            elif gender == "Désavantage des garçons":

                return (
                    "Difficulté territoriale élevée "
                    "et désavantage des garçons"
                )

            elif gender == "Écarts contrastés selon l'indicateur":

                return (
                    "Difficulté territoriale élevée "
                    "et écarts de genre contrastés"
                )

            else:

                return (
                    "Difficulté territoriale élevée "
                    "et diagnostic de genre à nuancer"
                )

        else:

            return (
                "Difficulté territoriale relativement moins élevée "
                "et diagnostic de genre à examiner séparément"
            )

    result["DIAGNOSTIC_COMBINE"] = result.apply(
        combine,
        axis=1
    )

    print(
        result[
            ["REGION", "DIAGNOSTIC_COMBINE"]
        ].to_string(index=False)
    )

    return result


# ============================================================
# 7. DIAGNOSTIC URBAIN-RURAL
# ============================================================

def analyze_urban_rural(urban):

    print("\n========== DIAGNOSTIC URBAIN-RURAL ==========")

    result = urban.copy()

    # Tri chronologique des années scolaires
    result = result.sort_values(
        "ANNEE_SCOLAIRE"
    ).reset_index(drop=True)

    first_year = result.iloc[0]

    last_year = result.iloc[-1]

    indicators = [
        "EFFECTIF_URBAIN_TOTAL",
        "EFFECTIF_RURAL_TOTAL",
    ]

    for column in indicators:

        result[column] = pd.to_numeric(
            result[column],
            errors="coerce"
        )

    if result[indicators].isnull().any().any():

        raise ValueError(
            "Valeurs manquantes dans les effectifs urbain-rural."
        )

    # Evolution entre première et dernière année
    urban_start = first_year[
        "EFFECTIF_URBAIN_TOTAL"
    ]

    urban_end = last_year[
        "EFFECTIF_URBAIN_TOTAL"
    ]

    rural_start = first_year[
        "EFFECTIF_RURAL_TOTAL"
    ]

    rural_end = last_year[
        "EFFECTIF_RURAL_TOTAL"
    ]

    urban_variation = (
        (urban_end - urban_start)
        / urban_start
        * 100
        if urban_start != 0
        else None
    )

    rural_variation = (
        (rural_end - rural_start)
        / rural_start
        * 100
        if rural_start != 0
        else None
    )

    diagnostic = pd.DataFrame([
        {
            "PREMIERE_ANNEE": first_year["ANNEE_SCOLAIRE"],

            "DERNIERE_ANNEE": last_year["ANNEE_SCOLAIRE"],

            "EFFECTIF_URBAIN_INITIAL": urban_start,

            "EFFECTIF_URBAIN_FINAL": urban_end,

            "VARIATION_URBAINE_PCT": (
                round(urban_variation, 2)
                if urban_variation is not None
                else None
            ),

            "EFFECTIF_RURAL_INITIAL": rural_start,

            "EFFECTIF_RURAL_FINAL": rural_end,

            "VARIATION_RURALE_PCT": (
                round(rural_variation, 2)
                if rural_variation is not None
                else None
            ),

            "SOURCE": "DGESS - Effectifs scolaires annuels",

            "PORTEE": "Nationale",
        }
    ])

    print(
        diagnostic.to_string(index=False)
    )

    print(
        "\nCes résultats décrivent des effectifs scolaires. "
        "Ils ne constituent pas des taux d'accès."
    )

    return diagnostic


# ============================================================
# 8. SYNTHESE DES DIAGNOSTICS
# ============================================================

def summarize_diagnostics(regional):

    print("\n========== SYNTHESE DES DIAGNOSTICS ==========")

    print("\nRépartition des diagnostics de genre :")

    gender_distribution = (
        regional["DIAGNOSTIC_GENRE"]
        .value_counts()
        .rename_axis("DIAGNOSTIC")
        .reset_index(name="NOMBRE_REGIONS")
    )

    gender_distribution["POURCENTAGE"] = (
        gender_distribution["NOMBRE_REGIONS"]
        / len(regional)
        * 100
    ).round(2)

    print(
        gender_distribution.to_string(index=False)
    )

    print("\nRépartition des difficultés territoriales :")

    territorial_distribution = (
        regional["NIVEAU_DIFFICULTE_TERRITORIALE"]
        .value_counts()
        .rename_axis("NIVEAU")
        .reset_index(name="NOMBRE_REGIONS")
    )

    print(
        territorial_distribution.to_string(index=False)
    )

    return (
        gender_distribution,
        territorial_distribution
    )


# ============================================================
# 9. EXPORTATION DES RESULTATS
# ============================================================

def export_results(
    regional,
    urban,
    gender_distribution,
    territorial_distribution
):

    PRIORITIZATION_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    regional.to_csv(
        OUTPUT_REGIONAL,
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    urban.to_csv(
        OUTPUT_URBAN,
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    gender_distribution.to_csv(
        PRIORITIZATION_DIR
        / "distribution_diagnostic_genre.csv",
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    territorial_distribution.to_csv(
        PRIORITIZATION_DIR
        / "distribution_diagnostic_territorial.csv",
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    print("\n========== EXPORTATION ==========")

    print("Diagnostic régional :")
    print(OUTPUT_REGIONAL)

    print("\nDiagnostic urbain-rural :")
    print(OUTPUT_URBAN)

    print("\nDistribution du diagnostic de genre :")
    print(
        PRIORITIZATION_DIR
        / "distribution_diagnostic_genre.csv"
    )

    print("\nDistribution territoriale :")
    print(
        PRIORITIZATION_DIR
        / "distribution_diagnostic_territorial.csv"
    )


# ============================================================
# 10. PIPELINE PRINCIPAL
# ============================================================

def main():

    # 1. Chargement
    regional, urban = load_data()

    # 2. Validation
    regional, urban = validate_data(
        regional,
        urban
    )

    # 3. Diagnostic de genre
    regional = analyze_gender(regional)

    # 4. Diagnostic territorial
    regional = analyze_territorial(regional)

    # 5. Diagnostic combiné
    regional = build_combined_diagnosis(regional)

    # 6. Diagnostic urbain-rural
    urban_diagnostic = analyze_urban_rural(urban)

    # 7. Synthèse
    (
        gender_distribution,
        territorial_distribution
    ) = summarize_diagnostics(regional)

    # 8. Exportation
    export_results(
        regional,
        urban_diagnostic,
        gender_distribution,
        territorial_distribution
    )

    print(
        "\nDiagnostic multidimensionnel terminé."
    )


# ============================================================
# 11. EXECUTION
# ============================================================

if __name__ == "__main__":

    main()
