
import pandas as pd
from pathlib import Path


# Chemin du projet
BASE_DIR = Path(__file__).resolve().parents[3]

# Chemin du fichier Excel original
FILE_PATH = BASE_DIR / "data" / "01_raw_data" / "donnees_education_bf.xlsx"

# Dossier de sauvegarde des données nettoyées
OUTPUT_DIR = BASE_DIR / "data" / "intermediate"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Noms des colonnes du tableau
colonnes = [
    "REGION",
    "SEXE",
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


# Vérification de l'existence du fichier
if not FILE_PATH.exists():
    raise FileNotFoundError(f"Fichier introuvable : {FILE_PATH}")


# Lecture de la feuille Feuil1
df = pd.read_excel(
    FILE_PATH,
    sheet_name="Feuil1",
    header=None,
    skiprows=2
)


# Attribution des noms de colonnes
df.columns = colonnes


# Identification des lignes sans catégorie statistique
lignes_vides = df["SEXE"].isna().sum()

print("\nLIGNES SANS CATEGORIE :", lignes_vides)


# Suppression des lignes sans catégorie
df = df.loc[df["SEXE"].notna()].copy()


# Complétion des noms des régions
df["REGION"] = df["REGION"].ffill()


# Nettoyage des libellés
df["REGION"] = df["REGION"].astype(str).str.strip()
df["SEXE"] = df["SEXE"].astype(str).str.strip()


# Conversion des colonnes des années en valeurs numériques
annees = colonnes[2:]

for annee in annees:
    df[annee] = pd.to_numeric(df[annee], errors="coerce")


# Vérification de la structure du tableau
print("\nSTRUCTURE DU TABLEAU NETTOYÉ")
print("Nombre de lignes :", df.shape[0])
print("Nombre de colonnes :", df.shape[1])


# Vérification des catégories
print("\nRÉPARTITION DES CATÉGORIES")
print(df.groupby(["REGION", "SEXE"]).size())


# Vérification des valeurs manquantes
print("\nVALEURS MANQUANTES")
print(df.isnull().sum())


# Vérification des catégories présentes
print("\nRÉGIONS IDENTIFIÉES")
print(df["REGION"].unique())

print("\nCATÉGORIES DE SEXE")
print(df["SEXE"].unique())


# Vérification de la cohérence du nombre de lignes
if len(df) != 42:
    print("\nATTENTION : le nombre de lignes obtenu est différent de 42.")
else:
    print("\nVÉRIFICATION : les 42 lignes attendues sont présentes.")


# Enregistrement du tableau nettoyé
output_file = OUTPUT_DIR / "effectifs_primaire_region_sexe.csv"

df.to_csv(
    output_file,
    index=False,
    encoding="utf-8-sig"
)

print("\nFichier nettoyé enregistré :", output_file)



# Vérification de la cohérence entre garçons, filles et total

print("\nCONTRÔLE DE COHÉRENCE DES EFFECTIFS")

for annee in annees:

    tableau = df.pivot(
        index="REGION",
        columns="SEXE",
        values=annee
    )

    ecart = (
        tableau["GARCONS"]
        + tableau["FILLES"]
        - tableau["TOTAL"]
    )

    regions_incoherentes = ecart[ecart != 0]

    print(f"\nAnnée scolaire : {annee}")

    if regions_incoherentes.empty:
        print("Tous les totaux sont cohérents.")
    else:
        print("Incohérences détectées :")
        print(regions_incoherentes)


# Vérification des totaux régionaux par rapport au total national

print("\nCONTRÔLE DES TOTAUX NATIONAUX")

regions = df.loc[df["REGION"] != "NATIONAL"]

national = df.loc[df["REGION"] == "NATIONAL"].iloc[0]

for annee in annees:

    for sexe in ["GARCONS", "FILLES", "TOTAL"]:

        somme_regions = regions.loc[
            regions["SEXE"] == sexe, annee
        ].sum()

        total_national = national[annee] if national["SEXE"] == sexe else df.loc[
            (df["REGION"] == "NATIONAL") &
            (df["SEXE"] == sexe), annee
        ].iloc[0]

        ecart = somme_regions - total_national

        if ecart == 0:
            resultat = "Cohérent"
        else:
            resultat = f"Écart détecté : {ecart:,.0f}"

        print(f"{annee} | {sexe} | {resultat}")
