
from pathlib import Path
import pandas as pd

# Définir le chemin du projet
BASE_DIR = Path(__file__).resolve().parents[3]

# Chemin du fichier Excel original
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Lire la feuille Feuil12 sans interpréter automatiquement les en-têtes
df = pd.read_excel(
    FILE_PATH,
    sheet_name="Feuil12",
    header=None
)

# Afficher les dimensions du tableau
print("\nDIMENSIONS DU TABLEAU")
print("Nombre de lignes :", df.shape[0])
print("Nombre de colonnes :", df.shape[1])

# Afficher les premières lignes pour examiner le titre et les en-têtes
print("\nPREMIÈRES LIGNES")
print(df.head(20).to_string())

# Afficher les dernières lignes pour repérer les éventuelles anomalies
print("\nDERNIÈRES LIGNES")
print(df.tail(10).to_string())

# Afficher les informations générales
print("\nINFORMATIONS GÉNÉRALES")
df.info()

# Afficher les valeurs manquantes par colonne
print("\nVALEURS MANQUANTES PAR COLONNE")
print(df.isna().sum())
