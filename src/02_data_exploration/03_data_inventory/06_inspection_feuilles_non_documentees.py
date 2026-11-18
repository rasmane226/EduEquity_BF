
from pathlib import Path
import pandas as pd

# Définir le chemin principal du projet
BASE_DIR = Path(__file__).resolve().parents[3]

# Chemin du classeur Excel original
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Feuilles à examiner
feuilles_a_inspecter = [
    "PRESCOLAIRE",
    "Feuil2",
    "Feuil4",
    "Feuil5"
]

print("\n========== INSPECTION DES FEUILLES ==========")

# Examiner chaque feuille
for nom_feuille in feuilles_a_inspecter:

    print("\n")
    print("=" * 70)
    print("FEUILLE :", nom_feuille)
    print("=" * 70)

    # Lire la feuille sans définir automatiquement les en-têtes
    df = pd.read_excel(
        FILE_PATH,
        sheet_name=nom_feuille,
        header=None
    )

    # Afficher les dimensions
    print("\nDIMENSIONS")
    print("Nombre de lignes :", df.shape[0])
    print("Nombre de colonnes :", df.shape[1])

    # Afficher les premières lignes
    print("\nPREMIÈRES LIGNES")
    print(df.head(25).to_string())

    # Afficher les dernières lignes
    print("\nDERNIÈRES LIGNES")
    print(df.tail(10).to_string())

    # Afficher les informations générales
    print("\nINFORMATIONS GÉNÉRALES")
    df.info()

    # Afficher les valeurs manquantes
    print("\nVALEURS MANQUANTES PAR COLONNE")
    print(df.isna().sum())

print("\n========== FIN DE L'INSPECTION ==========")
