
import pandas as pd
from pathlib import Path

# Définir les chemins du projet
BASE_DIR = Path(__file__).resolve().parents[3]

FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

OUTPUT_DIR = BASE_DIR / "data" / "intermediate"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Définir les noms des colonnes
colonnes = [
    "REGION",
    "2015-2016",
    "2016-2017",
    "2017-2018",
    "2018-2019",
    "2019-2020",
    "2020-2021",
    "2021-2022",
    "2022-2023",
    "2023-2024",
    "2024-2025"
]

# Vérifier l'existence du fichier
if not FILE_PATH.exists():
    raise FileNotFoundError(f"Fichier introuvable : {FILE_PATH}")

# Lire la feuille Feuil10 en ignorant le titre
df = pd.read_excel(
    FILE_PATH,
    sheet_name="Feuil10",
    header=None,
    skiprows=2
)

# Attribuer les noms des colonnes
df.columns = colonnes

# Supprimer les lignes sans région
df = df.loc[df["REGION"].notna()].copy()

# Nettoyer les noms des régions
df["REGION"] = (
    df["REGION"]
    .astype(str)
    .str.strip()
    .str.upper()
)

# Définir les colonnes des années
annees = colonnes[1:]

# Convertir les valeurs annuelles en nombres
for annee in annees:
    df[annee] = pd.to_numeric(df[annee], errors="coerce")

# Afficher la structure obtenue
print("\nSTRUCTURE DU TABLEAU NETTOYÉ")
print("Nombre de lignes :", df.shape[0])
print("Nombre de colonnes :", df.shape[1])

# Vérifier les régions
print("\nRÉGIONS IDENTIFIÉES")
print(df["REGION"].tolist())

# Vérifier les doublons régionaux
print("\nDOUBLONS")
print(df["REGION"].duplicated().sum())

# Vérifier les valeurs manquantes
print("\nVALEURS MANQUANTES")
print(df.isnull().sum())

# Vérifier les valeurs numériques de l'IPS
print("\nCONTRÔLE DES VALEURS DE L'IPS")
for annee in annees:
    valeurs_invalides = df.loc[
        (df[annee] <= 0) | (df[annee].isna()),
        ["REGION", annee]
    ]

    if valeurs_invalides.empty:
        print(f"{annee} : aucune valeur manquante ou non positive.")
    else:
        print(f"{annee} : valeurs à vérifier.")
        print(valeurs_invalides.to_string(index=False))

# Vérifier le nombre d'observations
if len(df) == 14:
    print("\nLes 14 observations attendues sont présentes.")
else:
    print("\nATTENTION : le nombre d'observations est différent de 14.")

# Enregistrer le fichier nettoyé
output_file = OUTPUT_DIR / "ips_tba_primaire_region.csv"

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("\nFICHIER NETTOYÉ ENREGISTRÉ :", output_file)
