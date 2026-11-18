
from pathlib import Path
import pandas as pd

# Déterminer le dossier racine du projet
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Dossier contenant les données nettoyées
DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "03_cleaned_data"
    / "final"
)

# Liste des fichiers à inspecter
fichiers = [
    "effectifs_primaire_region_sexe.csv",
    "effectifs_primaire_milieu_sexe.csv",
    "tba_primaire_region_sexe.csv",
    "tbs_primaire_region_sexe.csv",
    "tap_primaire_region_sexe.csv",
    "taux_reussite_cep_region_sexe.csv",
    "ips_tba_primaire_region.csv",
    "ips_tbs_primaire_region.csv",
    "ips_tap_primaire_region.csv",
    "ecoles_primaire_region_statut.csv"
]

# Liste pour enregistrer les résultats
rapport = []

print("=" * 70)
print("INSPECTION GLOBALE DES DONNÉES NETTOYÉES")
print("=" * 70)

# Examiner chaque fichier
for nom_fichier in fichiers:

    chemin = DATA_DIR / nom_fichier

    print("\n" + "=" * 70)
    print(f"FICHIER : {nom_fichier}")
    print("=" * 70)

    try:
        df = pd.read_csv(chemin, encoding="utf-8-sig")

        print(f"\nDimensions : {df.shape}")
        print(f"Colonnes : {df.columns.tolist()}")

        print("\nTypes des variables :")
        print(df.dtypes)

        print("\nValeurs manquantes :")
        print(df.isnull().sum())

        print("\nNombre de doublons complets :")
        print(df.duplicated().sum())

        print("\nAperçu :")
        print(df.head(3))

        # Enregistrer un résumé dans le rapport
        rapport.append({
            "FICHIER": nom_fichier,
            "NOMBRE_LIGNES": df.shape[0],
            "NOMBRE_COLONNES": df.shape[1],
            "DOUBLONS": df.duplicated().sum(),
            "VALEURS_MANQUANTES": df.isnull().sum().sum(),
            "COLONNES": ", ".join(df.columns)
        })

    except FileNotFoundError:
        print("ERREUR : fichier introuvable.")

        rapport.append({
            "FICHIER": nom_fichier,
            "NOMBRE_LIGNES": None,
            "NOMBRE_COLONNES": None,
            "DOUBLONS": None,
            "VALEURS_MANQUANTES": None,
            "COLONNES": "FICHIER INTROUVABLE"
        })

# Construire le rapport global
rapport_df = pd.DataFrame(rapport)

# Créer le dossier des rapports
OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "transformation"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Enregistrer le rapport
OUTPUT_PATH = OUTPUT_DIR / "rapport_inspection_globale.csv"

rapport_df.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("\n" + "=" * 70)
print("RAPPORT GLOBAL D'INSPECTION")
print("=" * 70)

print(rapport_df.to_string(index=False))

print(f"\nRapport enregistré : {OUTPUT_PATH}")
print("\nInspection globale terminée.")
