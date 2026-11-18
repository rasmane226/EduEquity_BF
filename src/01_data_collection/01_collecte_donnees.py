
import pandas as pd
from pathlib import Path
from datetime import datetime

# Chemin racine du projet
ROOT_DIR = Path(__file__).resolve().parents[2]

# Chemin du fichier source
SOURCE_FILE = (
    ROOT_DIR / "data" / "01_raw_data" /
    "donnees_education_bf.xlsx"
)

# Dossier de sortie
OUTPUT_DIR = ROOT_DIR / "outputs" / "tables" / "collection"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Vérifier la présence du fichier source
if not SOURCE_FILE.exists():
    raise FileNotFoundError(
        f"Fichier source introuvable : {SOURCE_FILE}"
    )

print("========== INVENTAIRE DES DONNEES ==========")
print("Fichier source :", SOURCE_FILE.name)

inventaire = []

try:
    # Ouvrir le classeur Excel
    with pd.ExcelFile(SOURCE_FILE) as excel:

        # Récupérer les noms des feuilles
        sheet_names = excel.sheet_names

        # Vérifier le nombre de feuilles attendu
        if len(sheet_names) != 14:
            raise ValueError(
                f"Nombre de feuilles inattendu : {len(sheet_names)}"
            )

        # Examiner chaque feuille
        for sheet_name in sheet_names:

            df = pd.read_excel(
                excel,
                sheet_name=sheet_name
            )

            inventaire.append({
                "FEUILLE": sheet_name,
                "NOMBRE_LIGNES": df.shape[0],
                "NOMBRE_COLONNES": df.shape[1],
                "COLONNES": " | ".join(map(str, df.columns)),
                "STATUT": "COLLECTEE"
            })

            print(
                f"{sheet_name} : "
                f"{df.shape[0]} lignes, "
                f"{df.shape[1]} colonnes"
            )

    # Créer le rapport d'inventaire
    df_inventaire = pd.DataFrame(inventaire)

    rapport_path = OUTPUT_DIR / "inventaire_donnees.csv"

    df_inventaire.to_csv(
        rapport_path,
        index=False,
        encoding="utf-8-sig"
    )

    # Créer le rapport général
    rapport_general = pd.DataFrame([{
        "FICHIER_SOURCE": SOURCE_FILE.name,
        "DATE_COLLECTE": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "NOMBRE_FEUILLES": len(inventaire),
        "STATUT": "TERMINEE"
    }])

    rapport_general.to_csv(
        OUTPUT_DIR / "rapport_collecte.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n========== RESULTAT ==========")
    print("Nombre de feuilles :", len(inventaire))
    print("Inventaire enregistré :", rapport_path)
    print("Collecte terminée avec succès.")

except Exception as e:
    print("\nErreur pendant l'inventaire :", str(e))
    raise
