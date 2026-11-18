
import pandas as pd
from pathlib import Path

# Chemin du projet
BASE_DIR = Path(__file__).resolve().parents[3]
# Chemin du fichier Excel
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Feuilles à examiner
feuilles = ["Feuil1", "Feuil3", "Feuil7"]

# Ouverture du classeur
excel_file = pd.ExcelFile(FILE_PATH)

# Parcours des feuilles
for nom_feuille in feuilles:

    # Lecture de la feuille sans interpréter les en-têtes
    df = pd.read_excel(
        excel_file,
        sheet_name=nom_feuille,
        header=None
    )

    print("\n" + "=" * 60)
    print(f"CATÉGORIES DE LA FEUILLE : {nom_feuille}")
    print("=" * 60)

    # Feuil1 et Feuil3 : examiner les deux premières colonnes
    if nom_feuille in ["Feuil1", "Feuil3"]:

        for index, ligne in df.iterrows():

            premiere_colonne = ligne.iloc[0]
            deuxieme_colonne = ligne.iloc[1]

            if pd.notna(premiere_colonne) or pd.notna(deuxieme_colonne):

                print(
                    f"Ligne {index + 1} : "
                    f"{premiere_colonne} | {deuxieme_colonne}"
                )

    # Feuil7 : examiner uniquement les noms des régions
    else:

        for index, valeur in df.iloc[3:, 0].items():

            if pd.notna(valeur):
                print(f"Ligne {index + 1} : {valeur}")
