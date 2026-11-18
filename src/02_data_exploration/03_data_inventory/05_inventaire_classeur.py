
from pathlib import Path
import pandas as pd

# Définir le chemin principal du projet
BASE_DIR = Path(__file__).resolve().parents[3]

# Chemin du classeur Excel original
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Ouvrir le classeur Excel
classeur = pd.ExcelFile(FILE_PATH)

# Préparer la liste des informations
inventaire = []

print("\n========== INVENTAIRE DU CLASSEUR ==========")

# Examiner chaque feuille du classeur
for nom_feuille in classeur.sheet_names:

    # Lire la feuille sans définir d'en-tête
    df = pd.read_excel(
        FILE_PATH,
        sheet_name=nom_feuille,
        header=None
    )

    # Calculer les dimensions
    nombre_lignes = df.shape[0]
    nombre_colonnes = df.shape[1]

    # Compter les lignes contenant au moins une donnée
    lignes_non_vides = df.dropna(how="all").shape[0]

    # Compter les colonnes contenant au moins une donnée
    colonnes_non_vides = df.dropna(axis=1, how="all").shape[1]

    # Ajouter les informations à l'inventaire
    inventaire.append({
        "FEUILLE": nom_feuille,
        "NOMBRE_LIGNES": nombre_lignes,
        "NOMBRE_COLONNES": nombre_colonnes,
        "LIGNES_NON_VIDES": lignes_non_vides,
        "COLONNES_NON_VIDES": colonnes_non_vides
    })

    # Afficher les informations
    print("\nFeuille :", nom_feuille)
    print("Nombre de lignes :", nombre_lignes)
    print("Nombre de colonnes :", nombre_colonnes)
    print("Lignes non vides :", lignes_non_vides)
    print("Colonnes non vides :", colonnes_non_vides)

# Construire le tableau récapitulatif
df_inventaire = pd.DataFrame(inventaire)

# Afficher le tableau final
print("\n========== TABLEAU RÉCAPITULATIF ==========")
print(df_inventaire.to_string(index=False))

# Créer le dossier de sortie
OUTPUT_DIR = BASE_DIR / "outputs" / "tables"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Enregistrer l'inventaire
OUTPUT_PATH = OUTPUT_DIR / "inventaire_classeur.csv"

df_inventaire.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("\nINVENTAIRE ENREGISTRÉ :", OUTPUT_PATH)
print("\nNombre total de feuilles :", len(df_inventaire))
