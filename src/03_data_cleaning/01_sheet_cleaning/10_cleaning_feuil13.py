
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

# Définir les noms des colonnes
colonnes = [
    "REGION",
    "STATUT",
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
    "HAUT-BASSINS",
    "NORD",
    "PLATEAU CENTRAL",
    "SAHEL",
    "SUD-OUEST",
    "NATIONAL"
]


# Normaliser les noms des régions et les statuts
df["REGION"] = df["REGION"].astype("string").str.strip().str.upper()
df["STATUT"] = df["STATUT"].astype("string").str.strip().str.upper()

# Compléter les noms des régions dans les cellules vides
df["REGION"] = df["REGION"].ffill()

# Définir les statuts attendus
statuts_attendus = ["PUBLIC", "PRIVÉ", "TOTAL"]

# Conserver uniquement les observations statistiques attendues
df = df[
    df["REGION"].isin(regions_attendues)
    & df["STATUT"].isin(statuts_attendus)
].copy()

# Convertir les colonnes annuelles en valeurs numériques
annees = colonnes[2:]

for annee in annees:
    df[annee] = pd.to_numeric(df[annee], errors="coerce")

# Réinitialiser les index
df = df.reset_index(drop=True)

# Afficher la structure du tableau nettoyé
print("\nSTRUCTURE DU TABLEAU NETTOYÉ")
print("Nombre de lignes :", df.shape[0])
print("Nombre de colonnes :", df.shape[1])

# Afficher les régions et les statuts
print("\nRÉGIONS IDENTIFIÉES")
print(sorted(df["REGION"].unique().tolist()))

print("\nSTATUTS IDENTIFIÉS")
print(sorted(df["STATUT"].unique().tolist()))

# Vérifier les régions absentes
regions_absentes = set(regions_attendues) - set(df["REGION"])

print("\nRÉGIONS ABSENTES")
print(regions_absentes)

# Vérifier les doublons région-statut
print("\nDOUBLONS RÉGION-STATUT")
print(df.duplicated(subset=["REGION", "STATUT"]).sum())

# Vérifier les valeurs manquantes
print("\nVALEURS MANQUANTES")
print(df.isna().sum())

# Vérifier la présence des trois statuts pour chaque région
print("\nCONTRÔLE DES STATUTS PAR RÉGION")
for region in regions_attendues:
    statuts = set(df.loc[df["REGION"] == region, "STATUT"])
    if statuts == set(statuts_attendus):
        print(f"{region} : les trois statuts sont présents.")
    else:
        print(f"{region} : statuts manquants ou incorrects : {statuts}")

# Vérifier la cohérence Public + Privé = Total
print("\nCONTRÔLE DES TOTAUX")

for annee in annees:
    tableau = df.pivot(
        index="REGION",
        columns="STATUT",
        values=annee
    )

    ecart = tableau["PUBLIC"] + tableau["PRIVÉ"] - tableau["TOTAL"]

    nombre_erreurs = (ecart.abs() > 0.01).sum()

    if nombre_erreurs == 0:
        print(f"{annee} : tous les totaux sont cohérents.")
    else:
        print(f"{annee} : {nombre_erreurs} incohérence(s) détectée(s).")
        print(ecart[ecart.abs() > 0.01])

# Vérifier le nombre total d'observations
if len(df) == 42:
    print("\nLes 42 observations attendues sont présentes.")
else:
    print("\nATTENTION : le nombre d'observations est différent de 42.")

# Enregistrer le fichier nettoyé
OUTPUT_DIR = BASE_DIR / "data" / "intermediate"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "ecoles_primaire_region_statut.csv"

df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

print("\nFICHIER NETTOYÉ ENREGISTRÉ :", OUTPUT_PATH)
