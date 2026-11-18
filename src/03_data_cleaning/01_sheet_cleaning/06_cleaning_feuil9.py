
import pandas as pd
from pathlib import Path

# Chemin du projet
BASE_DIR = Path(__file__).resolve().parents[3]
# Chemin du fichier Excel original
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Dossier de sauvegarde
OUTPUT_DIR = BASE_DIR / "data" / "intermediate"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Noms des colonnes
colonnes = [
    "REGION",
    "SEXE",
    "2016",
    "2017",
    "2018",
    "2019",
    "2020",
    "2021",
    "2022",
    "2023",
    "2024",
    "2025"
]

regions_attendues = [
    "BOUCLE DU MOUHOUN",
    "CASCADES",
    "CENTRE",
    "CENTRE-EST",
    "CENTRE-NORD",
    "CENTRE-OUEST",
    "CENTRE-SUD",
    "EST",
    "HAUT-BASSINS",
    "NORD",
    "PLATEAU CENTRAL",
    "SAHEL",
    "SUD-OUEST",
    "NATIONAL"
]
# Vérification du fichier
if not FILE_PATH.exists():
    raise FileNotFoundError(f"Fichier introuvable : {FILE_PATH}")

# Lecture de Feuil9
df = pd.read_excel(
    FILE_PATH,
    sheet_name="Feuil9",
    header=None,
    skiprows=2
)

# Attribution des noms de colonnes
df.columns = colonnes

# Suppression des lignes sans catégorie de sexe
df = df.loc[df["SEXE"].notna()].copy()

# Complétion des noms des régions
df["REGION"] = df["REGION"].ffill()

# Harmonisation des libellés
df["REGION"] = (
    df["REGION"]
    .astype("string")
    .str.strip()
    .str.upper()
)

df["SEXE"] = (
    df["SEXE"]
    .astype("string")
    .str.strip()
    .str.upper()
)

# Conservation des régions attendues
df = df.loc[
    df["REGION"].isin(regions_attendues)
].copy()

# Harmonisation des catégories
df["SEXE"] = df["SEXE"].replace({
    "GARÇONS": "GARCONS",
    "GARÇON": "GARCONS",
    "FILLES": "FILLES",
    "TOTAL": "TOTAL"
})

# Conversion des années en valeurs numériques
annees = colonnes[2:]

for annee in annees:
    df[annee] = pd.to_numeric(
        df[annee],
        errors="coerce"
    )

# Vérification de la structure
print("\nSTRUCTURE DU TABLEAU NETTOYÉ")
print("Nombre de lignes :", df.shape[0])
print("Nombre de colonnes :", df.shape[1])

# Répartition des catégories
print("\nRÉPARTITION DES CATÉGORIES")
print(df.groupby(["REGION", "SEXE"]).size())

# Régions absentes
regions_trouvees = df["REGION"].unique().tolist()

regions_absentes = [
    region for region in regions_attendues
    if region not in regions_trouvees
]

print("\nRÉGIONS ABSENTES")
print(regions_absentes)

# Valeurs manquantes
print("\nVALEURS MANQUANTES")
print(df.isnull().sum())

# Vérification du nombre de lignes
if len(df) == 42:
    print("\nLes 42 observations attendues sont présentes.")
else:
    print("\nATTENTION : le nombre d'observations est différent de 42.")

# Contrôle des catégories
print("\nCATÉGORIES DE SEXE")
print(df["SEXE"].unique())

# Contrôle : garçons + filles et total
print("\nCONTRÔLE EXPLORATOIRE DES TAUX TOTAUX")

for annee in annees:
    tableau = df.pivot(
        index="REGION",
        columns="SEXE",
        values=annee
    )

    moyenne = (
        tableau["GARCONS"] + tableau["FILLES"]
    ) / 2

    ecart = (moyenne - tableau["TOTAL"]).abs()

    print(
        f"{annee} | Écart maximal : {ecart.max():.4f}"
    )

# Recherche des valeurs hors de l'intervalle 0–100
print("\nVALEURS INFÉRIEURES À 0 OU SUPÉRIEURES À 100")

for annee in annees:
    valeurs = df.loc[
        (df[annee] < 0) | (df[annee] > 100),
        ["REGION", "SEXE", annee]
    ]

    if not valeurs.empty:
        print(f"\nAnnée : {annee}")
        print(valeurs.to_string(index=False))

# Enregistrement du fichier nettoyé
output_file = OUTPUT_DIR / "taux_reussite_cep_region_sexe.csv"

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("\nFICHIER NETTOYÉ ENREGISTRÉ :", output_file)

