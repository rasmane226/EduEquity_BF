
import pandas as pd
from pathlib import Path
from openpyxl import load_workbook

# Chemin du projet
BASE_DIR = Path(__file__).resolve().parents[3]
# Chemin du fichier Excel original
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Vérification de l'existence du fichier
if not FILE_PATH.exists():
    raise FileNotFoundError(f"Fichier introuvable : {FILE_PATH}")

# Lecture de Feuil7 sans définir les en-têtes
df = pd.read_excel(
    FILE_PATH,
    sheet_name="Feuil7",
    header=None
)

# Affichage des dimensions
print("\nDIMENSIONS DE FEUIL7")
print("Nombre de lignes :", df.shape[0])
print("Nombre de colonnes :", df.shape[1])

# Affichage des 12 premières lignes
print("\nAPERÇU DES 12 PREMIÈRES LIGNES")
print(df.head(12).to_string(index=False, header=False))

# Chargement du classeur Excel
workbook = load_workbook(FILE_PATH, data_only=True)

# Sélection de Feuil7
sheet = workbook["Feuil7"]

# Affichage des cellules fusionnées
print("\nCELLULES FUSIONNÉES")
for plage in sheet.merged_cells.ranges:
    print(plage)

# Examen des trois premières lignes
print("\nEXAMEN DES TROIS PREMIÈRES LIGNES")

for ligne in range(1, 4):
    valeurs = [
        sheet.cell(row=ligne, column=colonne).value
        for colonne in range(1, sheet.max_column + 1)
    ]
    print(f"Ligne {ligne} :", valeurs)
