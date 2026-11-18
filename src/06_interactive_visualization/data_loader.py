
from pathlib import Path
import pandas as pd

from config import (
    ANALYSES_DIR,
    EXPLORATORY_DIR,
    GENDER_DIR,
    REGIONAL_DIR,
    PRIORITIZATION_DIR,
    REGIONS,
)


# ============================================================
# 1. FONCTION GENERALE DE CHARGEMENT
# ============================================================

def load_csv(file_path, required_columns=None, optional=False):

    file_path = Path(file_path)

    if not file_path.exists():
        if optional:
            print(f"Fichier optionnel absent : {file_path.name}")
            return pd.DataFrame()

        raise FileNotFoundError(
            f"Fichier introuvable : {file_path}"
        )

    df = pd.read_csv(file_path)

    if required_columns:
        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Colonnes manquantes dans {file_path.name} : {missing}"
            )

    return df


# ============================================================
# 2. DONNEES EXPLORATOIRES ET EVOLUTION NATIONALE
# ============================================================

def load_national_data():

    file_path = (
        EXPLORATORY_DIR
        / "evolution_annuelle_indicateurs_sexe.csv"
    )

    return load_csv(
        file_path,
        [
            "ORDRE_ANNEE",
            "ANNEE_SCOLAIRE",
            "SEXE",
            "TBA",
            "TBS",
            "TAP",
        ],
    )


# ============================================================
# 3. DONNEES REGIONALES
# ============================================================

def load_regional_data():

    means = load_csv(
        REGIONAL_DIR / "moyennes_indicateurs_par_region.csv",
        ["REGION", "TBA", "TBS", "TAP"],
    )

    evolution = load_csv(
        REGIONAL_DIR / "evolution_indicateurs_par_region.csv",
        [
            "REGION",
            "ORDRE_ANNEE",
            "ANNEE_SCOLAIRE",
            "TBA",
            "TBS",
            "TAP",
        ],
    )

    ranking = load_csv(
        REGIONAL_DIR / "classement_regions_indicateurs.csv",
        ["INDICATEUR", "RANG", "REGION", "VALEUR_MOYENNE"],
    )

    variations = load_csv(
        REGIONAL_DIR / "variations_indicateurs_par_region.csv",
        [
            "REGION",
            "INDICATEUR",
            "ANNEE_DEBUT",
            "ANNEE_FIN",
            "VALEUR_INITIALE",
            "VALEUR_FINALE",
            "VARIATION_POINTS",
            "EVOLUTION",
        ],
    )

    if means["REGION"].nunique() != 13:
        raise ValueError(
            "Le fichier régional ne contient pas 13 régions."
        )

    if set(means["REGION"]) != set(REGIONS):
        raise ValueError(
            "Les noms des régions ne correspondent pas à config.py."
        )

    if evolution.duplicated(
        ["REGION", "ORDRE_ANNEE"]
    ).any():
        raise ValueError(
            "Doublons région-année dans les données régionales."
        )

    return {
        "means": means,
        "evolution": evolution,
        "ranking": ranking,
        "variations": variations,
    }


# ============================================================
# 4. DONNEES SUR LES DISPARITES DE GENRE
# ============================================================

def load_gender_data():

    regional_gaps = load_csv(
        GENDER_DIR / "ecarts_moyens_par_region.csv",
        ["REGION", "ECART_TBA", "ECART_TBS", "ECART_TAP"],
    )

    evolution_gaps = load_csv(
        GENDER_DIR / "evolution_ecarts_genre.csv",
        [
            "ORDRE_ANNEE",
            "ANNEE_SCOLAIRE",
            "ECART_TBA",
            "ECART_TBS",
            "ECART_TAP",
        ],
    )

    extremes = load_csv(
        GENDER_DIR / "regions_ecarts_genre_extremes.csv",
        [
            "INDICATEUR",
            "REGION_PLUS_DEFAVORABLE_AUX_FILLES",
            "ECART_MOYEN_FILLES",
            "REGION_PLUS_DEFAVORABLE_AUX_GARCONS",
            "ECART_MOYEN_GARCONS",
        ],
    )

    details = load_csv(
        GENDER_DIR / "ecarts_genre_region_annee.csv",
        [
            "REGION",
            "ANNEE_SCOLAIRE",
            "ORDRE_ANNEE",
            "ECART_TBA",
            "ECART_TBS",
            "ECART_TAP",
        ],
    )

    if regional_gaps["REGION"].nunique() != 13:
        raise ValueError(
            "Le fichier des écarts de genre ne contient pas 13 régions."
        )

    if details.duplicated(
        ["REGION", "ORDRE_ANNEE"]
    ).any():
        raise ValueError(
            "Doublons région-année dans les écarts de genre."
        )

    return {
        "regional_gaps": regional_gaps,
        "evolution_gaps": evolution_gaps,
        "extremes": extremes,
        "details": details,
    }


# ============================================================
# 5. DONNEES URBAIN-RURAL
# ============================================================

def load_urban_rural_data():

    files = {
        "evolution": "donnees_evolution_urbain_rural.csv",
        "situation": "donnees_situation_milieu_sexe.csv",
        "gender_gaps": "donnees_ecarts_genre_milieu.csv",
        "urban_rural_gaps": "donnees_ecarts_urbain_rural.csv",
    }

    data = {}

    for key, filename in files.items():
        data[key] = load_csv(
            PRIORITIZATION_DIR / filename,
            optional=True,
        )

    return data


# ============================================================
# 6. CHARGEMENT GLOBAL
# ============================================================

def load_all_data():

    return {
        "national": load_national_data(),
        "regional": load_regional_data(),
        "gender": load_gender_data(),
        "urban_rural": load_urban_rural_data(),
    }


# ============================================================
# 7. TEST DU CHARGEMENT
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("TEST DU CHARGEMENT DES DONNEES - EDUEQUITY BF")
    print("=" * 65)

    data = load_all_data()

    for section, datasets in data.items():

        print(f"\n{section.upper()}")

        if isinstance(datasets, dict):

            for name, df in datasets.items():

                print(
                    f"  {name}: {df.shape}"
                    if not df.empty
                    else f"  {name}: non disponible"
                )

        else:
            print(f"  {datasets.shape}")

    print("\nChargement terminé.")
    print("=" * 65)
