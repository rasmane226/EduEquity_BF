
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[3]

FICHIER = (
    BASE_DIR / "data" / "03_cleaned_data" /
    "final" / "ecoles_primaire_region_statut.csv"
)

df = pd.read_csv(FICHIER, encoding="utf-8-sig")

print("\n========== INSPECTION DU STATUT DES ECOLES ==========")

print("\nValeurs distinctes de STATUT :")
print(df["STATUT"].unique())

print("\nRépartition des catégories :")
print(df["STATUT"].value_counts(dropna=False))

print("\nTableau complet :")
print(df[["REGION", "STATUT"]].to_string(index=False))

print("\nDimensions :", df.shape)
print("\nValeurs manquantes :", df.isna().sum().sum())
