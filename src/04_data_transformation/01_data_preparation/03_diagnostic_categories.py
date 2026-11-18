
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = (
    PROJECT_ROOT
    / "data"
    / "03_cleaned_data"
    / "final"
)

fichiers = {
    "effectifs_primaire_milieu_sexe.csv": ["MILIEU", "SEXE"],
    "ecoles_primaire_region_statut.csv": ["STATUT"]
}

print("=" * 60)
print("DIAGNOSTIC DES CATEGORIES")
print("=" * 60)

for nom_fichier, colonnes in fichiers.items():

    chemin = DATA_DIR / nom_fichier
    df = pd.read_csv(chemin, encoding="utf-8-sig")

    print(f"\nFICHIER : {nom_fichier}")

    for colonne in colonnes:
        print(f"\nCatégorie : {colonne}")

        print("Valeurs distinctes :")
        print(df[colonne].unique())

        print("\nFréquences :")
        print(df[colonne].value_counts(dropna=False))

print("\nDiagnostic terminé.")
