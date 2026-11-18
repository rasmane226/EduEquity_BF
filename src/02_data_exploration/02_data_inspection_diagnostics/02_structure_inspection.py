
import pandas as pd
from pathlib import Path
from openpyxl.utils import get_column_letter

# Chemin du fichier Excel
BASE_DIR = Path(__file__).resolve().parents[3]
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Feuilles à examiner
feuilles_a_examiner = ["Feuil1", "Feuil3", "Feuil7"]

# Ouverture du classeur
excel_file = pd.ExcelFile(FILE_PATH)

# Inspection des trois premières lignes de chaque feuille
for nom_feuille in feuilles_a_examiner:

    df = pd.read_excel(
        excel_file,
        sheet_name=nom_feuille,
        header=None
    )

    print("\n" + "=" * 60)
    print(f"STRUCTURE DE LA FEUILLE : {nom_feuille}")
    print("=" * 60)

    for index, ligne in df.head(3).iterrows():

        print(f"\nLigne {index + 1} :")

        for position, valeur in enumerate(ligne):

            colonne = get_column_letter(position + 1)

            if pd.isna(valeur):
                contenu = "[Cellule vide]"
            else:
                contenu = str(valeur).replace("\n", " ")

                # Limiter l'affichage des textes trop longs
                if len(contenu) > 45:
                    contenu = contenu[:45] + "..."

            print(f"  Colonne {colonne} : {contenu}")
