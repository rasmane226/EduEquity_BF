
from pathlib import Path

import pandas as pd


# Chemins du projet
BASE_DIR = Path(__file__).resolve().parents[3]

DOSSIER_DONNEES = BASE_DIR / "data" / "intermediate"
DOSSIER_SORTIE = BASE_DIR / "outputs" / "tables"

FICHIER_SORTIE = DOSSIER_SORTIE / "inventaire_noms_geographiques.csv"


# Fichiers contenant des informations géographiques
fichiers = [
    "effectifs_primaire_region_sexe.csv",
    "tba_primaire_region_sexe.csv",
    "tbs_primaire_region_sexe.csv",
    "tap_primaire_region_sexe.csv",
    "taux_reussite_cep_region_sexe.csv",
    "ips_tba_primaire_region.csv",
    "ips_tbs_primaire_region.csv",
    "ips_tap_primaire_region.csv",
    "ecoles_primaire_region_statut.csv"
]


# Liste des noms géographiques trouvés
inventaire = []


# Inspection de chaque fichier
for nom_fichier in fichiers:

    chemin = DOSSIER_DONNEES / nom_fichier

    print(f"\nInspection : {nom_fichier}")

    if not chemin.exists():
        print("Fichier introuvable.")
        continue

    df = pd.read_csv(chemin, encoding="utf-8-sig")

    # Recherche de la colonne contenant les régions
    colonnes_regions = [
        colonne
        for colonne in df.columns
        if colonne.strip().upper() == "REGION"
    ]

    if not colonnes_regions:
        print("Aucune colonne REGION trouvée.")
        continue

    colonne_region = colonnes_regions[0]

    # Récupération des noms distincts et de leur fréquence
    frequences = df[colonne_region].value_counts(dropna=False)

    for nom_region, nombre in frequences.items():

        inventaire.append({
            "fichier": nom_fichier,
            "nom_original": nom_region,
            "nombre_occurrences": nombre
        })

        print(f"{nom_region} : {nombre}")


# Création du rapport
rapport = pd.DataFrame(inventaire)


# Vérification des résultats
if rapport.empty:
    raise ValueError(
        "Aucun nom de région n'a été trouvé dans les fichiers."
    )


# Exportation
DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

rapport.to_csv(
    FICHIER_SORTIE,
    index=False,
    encoding="utf-8-sig"
)


# Résumé
print("\n" + "=" * 50)
print("RÉSUMÉ DE L'INVENTAIRE GÉOGRAPHIQUE")
print("=" * 50)

print(f"Fichiers examinés : {len(fichiers)}")
print(f"Noms géographiques recensés : {len(rapport)}")

print(
    "Noms géographiques distincts :",
    rapport["nom_original"].nunique()
)

print(f"\nRapport enregistré : {FICHIER_SORTIE}")
