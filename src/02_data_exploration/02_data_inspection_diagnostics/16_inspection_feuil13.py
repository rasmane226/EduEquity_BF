
from pathlib import Path
import pandas as pd

# Définir le chemin principal du projet
BASE_DIR = Path(__file__).resolve().parents[3]

# Chemin du fichier Excel original
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Lire la feuille Feuil13 sans interpréter automatiquement les en-têtes
df = pd.read_excel(
    FILE_PATH,
    sheet_name="Feuil13",
    header=None
)

# Afficher les dimensions du tableau
print("\nDIMENSIONS DU TABLEAU")
print("Nombre de lignes :", df.shape[0])
print("Nombre de colonnes :", df.shape[1])

# Afficher les 25 premières lignes
print("\nPREMIÈRES LIGNES")
print(df.head(25).to_string())

# Afficher les 15 dernières lignes
print("\nDERNIÈRES LIGNES")
print(df.tail(15).to_string())

# Afficher les informations générales
print("\nINFORMATIONS GÉNÉRALES")
df.info()

# Afficher le nombre de valeurs manquantes par colonne
print("\nVALEURS MANQUANTES PAR COLONNE")
print(df.isna().sum())
