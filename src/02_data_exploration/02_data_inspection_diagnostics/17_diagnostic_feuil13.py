
from pathlib import Path
import pandas as pd

# Définir le chemin principal du projet
BASE_DIR = Path(__file__).resolve().parents[3]
# Chemin du fichier Excel original
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Lire la feuille Feuil13
df = pd.read_excel(
    FILE_PATH,
    sheet_name="Feuil13",
    header=None,
    skiprows=2
)

# Afficher toutes les valeurs originales de la colonne REGION
print("\nVALEURS ORIGINALES DE LA COLONNE REGION")

for index, valeur in df.iloc[:, 0].items():
    if pd.notna(valeur):
        print(index, repr(valeur))

# Afficher les différentes valeurs de la colonne STATUT
print("\nVALEURS ORIGINALES DE LA COLONNE STATUT")

for valeur in df.iloc[:, 1].dropna().unique():
    print(repr(valeur))

# Afficher les lignes contenant les deux régions recherchées
print("\nRECHERCHE DE HAUTS-BASSINS ET BURKINA FASO")

for index, ligne in df.iterrows():
    region = ligne.iloc[0]

    if pd.notna(region):
        texte = str(region).upper()

        if "BASSIN" in texte or "BURKINA" in texte or "NATIONAL" in texte:
            print("\nIndex :", index)
            print(ligne.to_string())
