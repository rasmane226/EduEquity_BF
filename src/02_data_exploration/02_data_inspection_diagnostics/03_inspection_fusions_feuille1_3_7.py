
# Importation de la bibliothèque Path
from pathlib import Path

# Importation de load_workbook pour lire la structure Excel
from openpyxl import load_workbook


# Définition du chemin du projet
BASE_DIR = Path(__file__).resolve().parents[3]
# Chemin du fichier Excel
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"


# Ouverture du classeur en lecture seule
workbook = load_workbook(FILE_PATH, read_only=False, data_only=False)


# Feuilles à examiner
feuilles_a_examiner = ["Feuil1", "Feuil3", "Feuil7"]


# Inspection des cellules fusionnées
for nom_feuille in feuilles_a_examiner:

    # Sélection de la feuille actuelle
    worksheet = workbook[nom_feuille]

    print("\n" + "=" * 60)
    print(f"CELLULES FUSIONNÉES : {nom_feuille}")
    print("=" * 60)

    # Récupération des plages de cellules fusionnées
    cellules_fusionnees = worksheet.merged_cells.ranges

    # Vérification de la présence de cellules fusionnées
    if cellules_fusionnees:

        for plage in cellules_fusionnees:
            print(plage)

    else:
        print("Aucune cellule fusionnée.")
