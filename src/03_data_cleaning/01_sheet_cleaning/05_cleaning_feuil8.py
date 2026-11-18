
import pandas as pd
from pathlib import Path

# Chemin du projet
BASE_DIR = Path(__file__).resolve().parents[3]
# Chemin du fichier Excel original
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Dossier de sauvegarde
OUTPUT_DIR = BASE_DIR / "data" / "intermediate"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Années scolaires
annees = [
    "2015-2016", "2016-2017", "2017-2018",
    "2018-2019", "2019-2020", "2020-2021",
    "2021-2022", "2022-2023", "2023-2024",
    "2024-2025"
]

# Création des noms de colonnes
colonnes = ["REGION"]

for annee in annees:
    colonnes.extend([
        f"{annee}_GARCONS",
        f"{annee}_FILLES",
        f"{annee}_TOTAL"
    ])

# Régions attendues
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

# Vérification du fichier
if not FILE_PATH.exists():
    raise FileNotFoundError(f"Fichier introuvable : {FILE_PATH}")

# Lecture de Feuil8
df = pd.read_excel(
    FILE_PATH,
    sheet_name="Feuil8",
    header=None,
    skiprows=3
)

# Attribution des noms de colonnes
df.columns = colonnes

# Nettoyage des noms des régions
df["REGION"] = (
    df["REGION"]
    .astype("string")
    .str.strip()
    .str.upper()
)

# Conservation des régions attendues
df = df.loc[
    df["REGION"].isin(regions_attendues)
].copy()

# Vérification des régions absentes
regions_trouvees = df["REGION"].tolist()

regions_absentes = [
    region for region in regions_attendues
    if region not in regions_trouvees
]

print("\nRÉGIONS ABSENTES")
print(regions_absentes)

# Conversion des données numériques
colonnes_numeriques = colonnes[1:]

for colonne in colonnes_numeriques:
    df[colonne] = pd.to_numeric(
        df[colonne],
        errors="coerce"
    )

# Vérification de la structure
print("\nSTRUCTURE DU TABLEAU NETTOYÉ")
print("Nombre de lignes :", df.shape[0])
print("Nombre de colonnes :", df.shape[1])

# Affichage des régions
print("\nRÉGIONS CONSERVÉES")
print(df["REGION"].tolist())

# Vérification des valeurs manquantes
print("\nVALEURS MANQUANTES")
print(df.isnull().sum())

# Vérification du nombre de régions
if len(df) == 14 and not regions_absentes:
    print("\nLes 14 lignes attendues sont présentes.")
else:
    print("\nATTENTION : la structure attendue n'est pas respectée.")

# Contrôle exploratoire des taux totaux
print("\nCONTRÔLE DES TAUX TOTAUX")

for annee in annees:
    garcons = df[f"{annee}_GARCONS"]
    filles = df[f"{annee}_FILLES"]
    total = df[f"{annee}_TOTAL"]

    moyenne = (garcons + filles) / 2
    ecart = (moyenne - total).abs()

    print(
        f"{annee} | Écart maximal : {ecart.max():.4f}"
    )

# Recherche des valeurs négatives ou supérieures à 150
print("\nVALEURS INFÉRIEURES À 0 OU SUPÉRIEURES À 150")

for colonne in colonnes_numeriques:
    valeurs = df.loc[
        (df[colonne] < 0) | (df[colonne] > 150),
        ["REGION", colonne]
    ]

    if not valeurs.empty:
        print(f"\n{colonne}")
        print(valeurs.to_string(index=False))

# Enregistrement du fichier nettoyé
output_file = OUTPUT_DIR / "tap_primaire_region_sexe.csv"

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("\nFICHIER NETTOYÉ ENREGISTRÉ :", output_file)
