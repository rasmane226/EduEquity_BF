
import pandas as pd
from pathlib import Path

# Chemin du projet
BASE_DIR = Path(__file__).resolve().parents[3]

# Fichier Excel original
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Lecture de Feuil9
df = pd.read_excel(
    FILE_PATH,
    sheet_name="Feuil9",
    header=None,
    skiprows=2
)

# Attribution des noms de colonnes
df.columns = [
    "REGION", "SEXE",
    "2016", "2017", "2018", "2019", "2020",
    "2021", "2022", "2023", "2024", "2025"
]

# Conservation des lignes avec une catégorie de sexe
df = df.loc[df["SEXE"].notna()].copy()

# Complétion des noms des régions
df["REGION"] = df["REGION"].ffill()

# Nettoyage des libellés
df["REGION"] = (
    df["REGION"]
    .astype("string")
    .str.strip()
    .str.upper()
)

df["SEXE"] = (
    df["SEXE"]
    .astype("string")
    .str.strip()
    .str.upper()
)

# Affichage de toutes les régions réellement présentes
print("\nTOUTES LES RÉGIONS IDENTIFIÉES")

for region in df["REGION"].unique():
    print(repr(region))

# Comptage des observations par région
print("\nNOMBRE D'OBSERVATIONS PAR RÉGION")
print(df.groupby("REGION").size())

# Affichage des catégories de sexe
print("\nCATÉGORIES DE SEXE")
print(df["SEXE"].value_counts())

# Affichage des dernières observations
print("\nLES 20 DERNIÈRES OBSERVATIONS")
print(df.tail(20).to_string(index=False))
