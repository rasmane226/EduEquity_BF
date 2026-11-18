
from pathlib import Path
import pandas as pd

# ============================================================
# 1. CONFIGURATION DU PROJET
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "03_cleaned_data"
    / "final"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "transformation"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 2. DEFINITION DES FICHIERS ET DES CLES METIER
# ============================================================

fichiers = {
    "effectifs_primaire_region_sexe.csv": {
        "cles": ["REGION", "SEXE"]
    },

    "effectifs_primaire_milieu_sexe.csv": {
        "cles": ["MILIEU", "SEXE"]
    },

    "tba_primaire_region_sexe.csv": {
        "cles": ["REGION"]
    },

    "tbs_primaire_region_sexe.csv": {
        "cles": ["REGION"]
    },

    "tap_primaire_region_sexe.csv": {
        "cles": ["REGION"]
    },

    "taux_reussite_cep_region_sexe.csv": {
        "cles": ["REGION", "SEXE"]
    },

    "ips_tba_primaire_region.csv": {
        "cles": ["REGION"]
    },

    "ips_tbs_primaire_region.csv": {
        "cles": ["REGION"]
    },

    "ips_tap_primaire_region.csv": {
        "cles": ["REGION"]
    },

    "ecoles_primaire_region_statut.csv": {
        "cles": ["REGION", "STATUT"]
    }
}

# ============================================================
# 3. CATEGORIES ATTENDUES
# ============================================================

regions_attendues = 13

sexes_attendus = {"FILLES", "GARCONS"}

milieux_attendus = {"URBAIN", "RURAL", "NATIONAL"}

statuts_attendus = {"PUBLIC", "PRIVÉ"}

# ============================================================
# 4. FONCTION DE CONTROLE QUALITE
# ============================================================

def controler_fichier(nom_fichier, configuration):

    chemin = DATA_DIR / nom_fichier

    # Vérifier l'existence du fichier
    if not chemin.exists():

        return {
            "FICHIER": nom_fichier,
            "STATUT": "FICHIER INTROUVABLE",
            "LIGNES": None,
            "DOUBLONS_COMPLETS": None,
            "DOUBLONS_CLES": None,
            "VALEURS_MANQUANTES": None,
            "VALEURS_NON_NUMERIQUES": None,
            "VALEURS_NEGATIVES": None,
            "CATEGORIES_INVALIDES": None
        }

    # Charger les données
    df = pd.read_csv(chemin, encoding="utf-8-sig")

    # Identifier les clés métier
    colonnes_cles = configuration["cles"]

    # Vérifier que les clés existent
    if not all(colonne in df.columns for colonne in colonnes_cles):

        return {
            "FICHIER": nom_fichier,
            "STATUT": "CLES MANQUANTES",
            "LIGNES": len(df),
            "DOUBLONS_COMPLETS": None,
            "DOUBLONS_CLES": None,
            "VALEURS_MANQUANTES": None,
            "VALEURS_NON_NUMERIQUES": None,
            "VALEURS_NEGATIVES": None,
            "CATEGORIES_INVALIDES": None
        }

    # Identifier les colonnes quantitatives
    colonnes_valeurs = [
        colonne for colonne in df.columns
        if colonne not in colonnes_cles
    ]

    # --------------------------------------------------------
    # A. CONTROLE DES DOUBLONS
    # --------------------------------------------------------

    doublons_complets = int(df.duplicated().sum())

    doublons_cles = int(
        df.duplicated(subset=colonnes_cles).sum()
    )

    # --------------------------------------------------------
    # B. CONTROLE DES VALEURS MANQUANTES
    # --------------------------------------------------------

    valeurs_manquantes = int(
        df.isnull().sum().sum()
    )

    # --------------------------------------------------------
    # C. CONTROLE DES VALEURS NUMERIQUES
    # --------------------------------------------------------

    valeurs_converties = df[colonnes_valeurs].apply(
        pd.to_numeric,
        errors="coerce"
    )

    valeurs_non_numeriques = int(
        (
            valeurs_converties.isna()
            & df[colonnes_valeurs].notna()
        ).sum().sum()
    )

    # --------------------------------------------------------
    # D. CONTROLE DES VALEURS NEGATIVES
    # --------------------------------------------------------

    valeurs_negatives = int(
        (valeurs_converties < 0).sum().sum()
    )

    # --------------------------------------------------------
    # E. CONTROLE DES CATEGORIES
    # --------------------------------------------------------

    categories_invalides = 0

    # Vérification des sexes
    if "SEXE" in df.columns:

        categories_invalides += int(
            (~df["SEXE"].isin(sexes_attendus)).sum()
        )

    # Vérification des milieux
    if "MILIEU" in df.columns:

        categories_invalides += int(
            (~df["MILIEU"].isin(milieux_attendus)).sum()
        )

    # Vérification des statuts
    if "STATUT" in df.columns:

        categories_invalides += int(
            (~df["STATUT"].isin(statuts_attendus)).sum()
        )

    # Vérification du nombre de régions
    if "REGION" in df.columns:

        nombre_regions = df["REGION"].nunique()

        if nombre_regions != regions_attendues:
            categories_invalides += 1

    # --------------------------------------------------------
    # F. DETERMINATION DU STATUT GLOBAL
    # --------------------------------------------------------

    problemes = (
        doublons_complets
        + doublons_cles
        + valeurs_manquantes
        + valeurs_non_numeriques
        + valeurs_negatives
        + categories_invalides
    )

    statut = "VALIDE" if problemes == 0 else "A VERIFIER"

    return {
        "FICHIER": nom_fichier,
        "STATUT": statut,
        "LIGNES": len(df),
        "DOUBLONS_COMPLETS": doublons_complets,
        "DOUBLONS_CLES": doublons_cles,
        "VALEURS_MANQUANTES": valeurs_manquantes,
        "VALEURS_NON_NUMERIQUES": valeurs_non_numeriques,
        "VALEURS_NEGATIVES": valeurs_negatives,
        "CATEGORIES_INVALIDES": categories_invalides
    }


# ============================================================
# 5. EXECUTION DES CONTROLES
# ============================================================

print("=" * 75)
print("CONTROLE GLOBAL DE LA QUALITE DES DONNEES")
print("=" * 75)

resultats = []

for nom_fichier, configuration in fichiers.items():

    print(f"\nAnalyse : {nom_fichier}")

    resultat = controler_fichier(
        nom_fichier,
        configuration
    )

    resultats.append(resultat)

    print(f"Statut : {resultat['STATUT']}")


# ============================================================
# 6. GENERATION DU RAPPORT GLOBAL
# ============================================================

rapport = pd.DataFrame(resultats)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "rapport_controle_qualite_transformation.csv"
)

rapport.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)

# ============================================================
# 7. AFFICHAGE DES RESULTATS
# ============================================================

print("\n" + "=" * 75)
print("RESULTATS DU CONTROLE GLOBAL")
print("=" * 75)

print(rapport.to_string(index=False))

nombre_valides = (
    rapport["STATUT"] == "VALIDE"
).sum()

nombre_a_verifier = (
    rapport["STATUT"] == "A VERIFIER"
).sum()

nombre_introuvables = (
    rapport["STATUT"] == "FICHIER INTROUVABLE"
).sum()

print("\n" + "=" * 75)
print("BILAN FINAL")
print("=" * 75)

print(f"Nombre de fichiers inspectés : {len(fichiers)}")
print(f"Fichiers valides : {nombre_valides}")
print(f"Fichiers à vérifier : {nombre_a_verifier}")
print(f"Fichiers introuvables : {nombre_introuvables}")

print(f"\nRapport enregistré : {OUTPUT_PATH}")

print("\nContrôle global terminé.")
