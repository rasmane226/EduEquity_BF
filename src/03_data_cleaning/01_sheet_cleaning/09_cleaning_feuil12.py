
from pathlib import Path
import pandas as pd

# Définir le chemin principal du projet
BASE_DIR = Path(__file__).resolve().parents[3]

# Chemin du fichier Excel original
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Lire la feuille Feuil12
df = pd.read_excel(
    FILE_PATH,
    sheet_name="Feuil12",
    header=None,
    skiprows=2
)

# Définir les noms des colonnes
colonnes = [
    "REGION",
    "2015-2016",
    "2016-2017",
    "2017-2018",
    "2018-2019",
    "2019-2020",
    "2020-2021",
    "2021-2022",
    "2022-2023",
    "2023-2024",
    "2024-2025"
]

df.columns = colonnes

# Définir les régions attendues
regions_attendues = [
    "BOUCLE DU MOUHOUN",
    "CASCADES",
    "CENTRE",
    "CENTRE-EST",
    "CENTRE-NORD",
    "CENTRE-OUEST",
    "CENTRE-SUD",
    "EST",
    "HAUTS-BASSINS",
    "NORD",
    "PLATEAU CENTRAL",
    "SAHEL",
    "SUD-OUEST",
    "BURKINA FASO"
]

# Conserver uniquement les régions statistiques attendues
df["REGION"] = df["REGION"].astype("string").str.strip().str.upper()
df = df[df["REGION"].isin(regions_attendues)].copy()

# Convertir les colonnes annuelles en valeurs numériques
annees = colonnes[1:]

for annee in annees:
    df[annee] = pd.to_numeric(df[annee], errors="coerce")

# Réinitialiser les index
df = df.reset_index(drop=True)

# Afficher la structure du tableau nettoyé
print("\nSTRUCTURE DU TABLEAU NETTOYÉ")
print("Nombre de lignes :", df.shape[0])
print("Nombre de colonnes :", df.shape[1])

# Afficher les régions identifiées
print("\nRÉGIONS IDENTIFIÉES")
print(df["REGION"].tolist())

# Vérifier les régions absentes
regions_absentes = set(regions_attendues) - set(df["REGION"])

print("\nRÉGIONS ABSENTES")
print(regions_absentes)

# Vérifier les doublons
print("\nDOUBLONS")
print(df["REGION"].duplicated().sum())

# Vérifier les valeurs manquantes
print("\nVALEURS MANQUANTES")
print(df.isna().sum())

# Vérifier les valeurs de l'IPS
print("\nCONTRÔLE DES VALEURS DE L'IPS")

for annee in annees:
    valeurs_invalides = df[annee].isna() | (df[annee] <= 0)

    if valeurs_invalides.any():
        print(f"{annee} : valeurs manquantes ou non positives détectées.")
    else:
        print(f"{annee} : aucune valeur manquante ou non positive.")

# Vérifier le nombre d'observations
if len(df) == 14:
    print("\nLes 14 observations attendues sont présentes.")
else:
    print("\nATTENTION : le nombre d'observations est différent de 14.")

# Enregistrer le fichier nettoyé
OUTPUT_DIR = BASE_DIR / "data" / "intermediate"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "ips_tap_primaire_region.csv"

df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

print("\nFICHIER NETTOYÉ ENREGISTRÉ :", OUTPUT_PATH)
