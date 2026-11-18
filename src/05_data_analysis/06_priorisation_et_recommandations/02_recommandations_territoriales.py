
from pathlib import Path
import pandas as pd


# ============================================================
# 1. INITIALISATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

DOSSIER_ANALYSES = BASE_DIR / "outputs" / "analyses"

DOSSIER_PRIORISATION = (
    DOSSIER_ANALYSES / "06_priorisation_et_recommandations"
)

DOSSIER_GENRE = (
    DOSSIER_ANALYSES / "02_analyse_disparites_genre"
)

DOSSIER_URBAIN_RURAL = (
    DOSSIER_ANALYSES / "04_analyse_urbain_rural"
)

DOSSIER_INSD = DOSSIER_URBAIN_RURAL / "insd_rgph_2019"

DOSSIER_SORTIE = DOSSIER_PRIORISATION
DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CHEMINS DES SOURCES
# ============================================================

FICHIER_CLASSEMENT = (
    DOSSIER_PRIORISATION / "classement_final_territorial.csv"
)

FICHIER_INDICATEURS = (
    DOSSIER_PRIORISATION / "indicateurs_priorisation.csv"
)

FICHIER_GENRE_REGION = (
    DOSSIER_GENRE / "ecarts_moyens_par_region.csv"
)

FICHIER_SITUATION_MILIEU = (
    DOSSIER_INSD / "comparaison_situation_scolaire_milieu_sexe.csv"
)

FICHIER_ECARTS_GENRE_MILIEU = (
    DOSSIER_INSD / "ecarts_filles_garcons_par_milieu.csv"
)

FICHIER_ECARTS_MILIEUX = (
    DOSSIER_INSD / "ecarts_situation_scolaire_urbain_rural.csv"
)

# CORRECTION : fichier situé directement dans le dossier urbain-rural
FICHIER_EVOLUTION = (
    DOSSIER_URBAIN_RURAL
    / "evolution_urbain_rural_par_sexe.csv"
)


# ============================================================
# 3. VERIFICATION DES FICHIERS
# ============================================================

fichiers = {
    "Classement territorial": FICHIER_CLASSEMENT,
    "Indicateurs régionaux": FICHIER_INDICATEURS,
    "Écarts de genre par région": FICHIER_GENRE_REGION,
    "Situation scolaire par milieu et sexe": FICHIER_SITUATION_MILIEU,
    "Écarts filles-garçons par milieu": FICHIER_ECARTS_GENRE_MILIEU,
    "Écarts urbain-rural": FICHIER_ECARTS_MILIEUX,
    "Évolution urbain-rural par sexe": FICHIER_EVOLUTION
}

print("========== VERIFICATION DES SOURCES ==========")

for nom, chemin in fichiers.items():

    if not chemin.exists():
        raise FileNotFoundError(
            f"{nom} introuvable : {chemin}"
        )

    print(f"[OK] {nom}")


# ============================================================
# 4. CHARGEMENT DES DONNEES
# ============================================================

df_classement = pd.read_csv(
    FICHIER_CLASSEMENT,
    encoding="utf-8"
)

df_indicateurs = pd.read_csv(
    FICHIER_INDICATEURS,
    encoding="utf-8"
)

df_genre_region = pd.read_csv(
    FICHIER_GENRE_REGION,
    encoding="utf-8"
)

df_situation_milieu = pd.read_csv(
    FICHIER_SITUATION_MILIEU,
    encoding="utf-8"
)

df_ecarts_genre_milieu = pd.read_csv(
    FICHIER_ECARTS_GENRE_MILIEU,
    encoding="utf-8"
)

df_ecarts_milieux = pd.read_csv(
    FICHIER_ECARTS_MILIEUX,
    encoding="utf-8"
)

df_evolution = pd.read_csv(
    FICHIER_EVOLUTION,
    encoding="utf-8"
)


# ============================================================
# 5. NORMALISATION DES NOMS DES REGIONS
# ============================================================

for df in [
    df_classement,
    df_indicateurs,
    df_genre_region
]:
    df["REGION"] = (
        df["REGION"]
        .astype(str)
        .str.strip()
        .str.upper()
    )


# ============================================================
# 6. CONVERSION DES ECARTS DE GENRE
# ============================================================

colonnes_genre = [
    "ECART_TBA",
    "ECART_TBS",
    "ECART_TAP"
]

for colonne in colonnes_genre:

    df_genre_region[colonne] = pd.to_numeric(
        df_genre_region[colonne],
        errors="coerce"
    )


# ============================================================
# 7. FUSION DES DONNEES REGIONALES
# ============================================================

print("\n========== FUSION DES DONNEES REGIONALES ==========")

df_regional = df_classement.merge(
    df_indicateurs,
    on="REGION",
    how="inner",
    validate="one_to_one"
)

df_regional = df_regional.merge(
    df_genre_region,
    on="REGION",
    how="inner",
    validate="one_to_one"
)

print("Dimensions du jeu de données régional :")
print(df_regional.shape)

print("\nAperçu des données régionales :")
print(df_regional.head(13).to_string(index=False))


# Vérification des 13 régions
if df_regional["REGION"].nunique() != 13:
    raise ValueError(
        "Le jeu régional ne contient pas exactement 13 régions."
    )

if df_regional.isnull().any().any():
    raise ValueError(
        "Des valeurs manquantes existent dans le jeu régional."
    )


# ============================================================
# 8. AFFICHAGE DES DONNEES URBAIN-RURAL
# ============================================================

print("\n========== SITUATION SCOLAIRE PAR MILIEU ET SEXE ==========")

print(
    df_situation_milieu.to_string(index=False)
)

print("\n========== ECARTS FILLES-GARCONS PAR MILIEU ==========")

print(
    df_ecarts_genre_milieu.to_string(index=False)
)

print("\n========== ECARTS ENTRE MILIEUX ==========")

print(
    df_ecarts_milieux.to_string(index=False)
)

print("\n========== EVOLUTION URBAIN-RURAL PAR SEXE ==========")

print(
    df_evolution.head(10).to_string(index=False)
)


# ============================================================
# 9. CONTROLES DES DONNEES URBAIN-RURAL
# ============================================================

# Vérifier les doublons dans la situation scolaire
if df_situation_milieu.duplicated().any():
    raise ValueError(
        "Doublons dans la situation scolaire par milieu et sexe."
    )

# Vérifier les doublons dans les écarts de genre
if df_ecarts_genre_milieu.duplicated().any():
    raise ValueError(
        "Doublons dans les écarts de genre par milieu."
    )

# Vérifier les doublons dans les écarts urbain-rural
if df_ecarts_milieux.duplicated().any():
    raise ValueError(
        "Doublons dans les écarts entre milieux."
    )

# Vérifier les doublons dans l'évolution
if df_evolution.duplicated().any():
    raise ValueError(
        "Doublons dans les données d'évolution."
    )


# ============================================================
# 10. EXPORTATION DES JEUX DE DONNEES
# ============================================================

df_regional.to_csv(
    DOSSIER_SORTIE / "donnees_consolidees_regionales.csv",
    index=False,
    encoding="utf-8-sig"
)

df_situation_milieu.to_csv(
    DOSSIER_SORTIE / "donnees_situation_milieu_sexe.csv",
    index=False,
    encoding="utf-8-sig"
)

df_ecarts_genre_milieu.to_csv(
    DOSSIER_SORTIE / "donnees_ecarts_genre_milieu.csv",
    index=False,
    encoding="utf-8-sig"
)

df_ecarts_milieux.to_csv(
    DOSSIER_SORTIE / "donnees_ecarts_urbain_rural.csv",
    index=False,
    encoding="utf-8-sig"
)

df_evolution.to_csv(
    DOSSIER_SORTIE / "donnees_evolution_urbain_rural.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 11. BILAN FINAL
# ============================================================

print("\n========== BILAN DE LA FUSION ==========")

print(
    f"Régions consolidées : {df_regional['REGION'].nunique()}"
)

print(
    f"Lignes situation scolaire : {len(df_situation_milieu)}"
)

print(
    f"Lignes écarts de genre : {len(df_ecarts_genre_milieu)}"
)

print(
    f"Lignes écarts urbain-rural : {len(df_ecarts_milieux)}"
)

print(
    f"Lignes évolution : {len(df_evolution)}"
)

print("\nFichiers exportés dans :")
print(DOSSIER_SORTIE)

print("\nFUSION DES SOURCES TERMINEE.")
