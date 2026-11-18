
import pandas as pd
from pathlib import Path

# Définir le chemin du projet
BASE_DIR = Path(__file__).resolve().parents[3]

FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Vérifier l'existence du fichier
if not FILE_PATH.exists():
    raise FileNotFoundError(f"Fichier introuvable : {FILE_PATH}")

# Charger Feuil11 sans définir d'en-tête
df = pd.read_excel(
    FILE_PATH,
    sheet_name="Feuil11",
    header=None
)

# Afficher les dimensions
print("\nDIMENSIONS DE FEUIL11")
print("Nombre de lignes :", df.shape[0])
print("Nombre de colonnes :", df.shape[1])

# Afficher les 20 premières lignes
print("\nAPERÇU DES 20 PREMIÈRES LIGNES")
print(df.head(20).to_string())

# Afficher les 10 dernières lignes
print("\nAPERÇU DES 10 DERNIÈRES LIGNES")
print(df.tail(10).to_string())

# Examiner les valeurs distinctes de chaque colonne
print("\nVALEURS DISTINCTES PAR COLONNE")

for colonne in df.columns:
    valeurs = df[colonne].dropna().unique()
    print(f"\nColonne {colonne} :")
    print(valeurs[:20])

# Afficher les informations générales
print("\nINFORMATIONS GÉNÉRALES")
df.info()
