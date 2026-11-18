
# 1. Importation des bibliothèques
import pandas as pd
from pathlib import Path

# 2. Définition du chemin du fichier Excel

# Chemin du fichier de données
BASE_DIR = Path(__file__).resolve().parents[3]
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"


# 3. Vérification de l'existence du fichier
if not FILE_PATH.exists():
    raise FileNotFoundError(f"Fichier introuvable : {FILE_PATH}")

# 4. Lecture du classeur Excel
excel_file = pd.ExcelFile(FILE_PATH)

# 5. Affichage des informations générales
print("=" * 60)
print("EXPLORATION DU DATASET EDUEquity BF")
print("=" * 60)

print(f"Nombre de feuilles : {len(excel_file.sheet_names)}")

# 6. Affichage des noms des feuilles
print("\nNOMS DES FEUILLES :")

for sheet in excel_file.sheet_names:
    print("-", sheet)

# 7. Inventaire des dimensions
print("\nDIMENSIONS DES FEUILLES :")

for sheet in excel_file.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet, header=None)

    print(
        f"{sheet} : "
        f"{df.shape[0]} lignes et "
        f"{df.shape[1]} colonnes"
    )
