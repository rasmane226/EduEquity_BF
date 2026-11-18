
from pathlib import Path

import pandas as pd


# Chemins du projet
BASE_DIR = Path(__file__).resolve().parents[3]

DOSSIER_SOURCE = BASE_DIR / "data" / "intermediate"
DOSSIER_SORTIE = BASE_DIR / "data" / "final"


# Nomenclature géographique de référence
regions_reference = [
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
    "SUD-OUEST"
]


# Fichiers et colonnes à traiter
configuration = {
    "effectifs_primaire_region_sexe.csv": {
        "region": "REGION",
        "categories": ["SEXE"]
    },
    "effectifs_primaire_milieu_sexe.csv": {
        "region": None,
        "categories": ["MILIEU", "SEXE"]
    },
    "tba_primaire_region_sexe.csv": {
        "region": "REGION",
        "categories": []
    },
    "tbs_primaire_region_sexe.csv": {
        "region": "REGION",
        "categories": []
    },
    "tap_primaire_region_sexe.csv": {
        "region": "REGION",
        "categories": []
    },
    "taux_reussite_cep_region_sexe.csv": {
        "region": "REGION",
        "categories": ["SEXE"]
    },
    "ips_tba_primaire_region.csv": {
        "region": "REGION",
        "categories": []
    },
    "ips_tbs_primaire_region.csv": {
        "region": "REGION",
        "categories": []
    },
    "ips_tap_primaire_region.csv": {
        "region": "REGION",
        "categories": []
    },
    "ecoles_primaire_region_statut.csv": {
        "region": "REGION",
        "categories": ["STATUT"]
    }
}


# Fonction pour retrouver une colonne sans dépendre des majuscules
def trouver_colonne(df, nom_recherche):

    for colonne in df.columns:
        if colonne.strip().upper() == nom_recherche.upper():
            return colonne

    return None


# Création du dossier de destination
DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)


# Liste des rapports de traitement
rapports = []


# Traitement des fichiers
for nom_fichier, regles in configuration.items():

    chemin_source = DOSSIER_SOURCE / nom_fichier

    print(f"\nTraitement : {nom_fichier}")

    if not chemin_source.exists():
        raise FileNotFoundError(
            f"Fichier source introuvable : {chemin_source}"
        )

    # Lecture du fichier original nettoyé
    df = pd.read_csv(
        chemin_source,
        encoding="utf-8-sig"
    )

    nombre_lignes_initial = len(df)

    # Harmonisation du nom de région
    colonne_region = None

    if regles["region"] is not None:

        colonne_region = trouver_colonne(
            df,
            regles["region"]
        )

        if colonne_region is None:
            raise ValueError(
                f"Colonne région introuvable dans {nom_fichier}"
            )

        df[colonne_region] = (
            df[colonne_region]
            .astype("string")
            .str.strip()
            .str.upper()
            .replace({
                "HAUT-BASSINS": "HAUTS-BASSINS"
            })
        )

        # Conservation des 13 régions uniquement
        df = df[
            df[colonne_region].isin(regions_reference)
        ].copy()

    # Suppression des catégories TOTAL
    for nom_categorie in regles["categories"]:

        colonne_categorie = trouver_colonne(
            df,
            nom_categorie
        )

        if colonne_categorie is None:
            raise ValueError(
                f"Colonne {nom_categorie} introuvable "
                f"dans {nom_fichier}"
            )

        df[colonne_categorie] = (
            df[colonne_categorie]
            .astype("string")
            .str.strip()
            .str.upper()
        )

        df = df[
            df[colonne_categorie] != "TOTAL"
        ].copy()

    # Vérification des régions présentes
    if colonne_region is not None:

        regions_presentes = set(df[colonne_region].dropna())

        regions_manquantes = (
            set(regions_reference) - regions_presentes
        )

        regions_inconnues = (
            regions_presentes - set(regions_reference)
        )

        if regions_manquantes:
            raise ValueError(
                f"Régions manquantes dans {nom_fichier} : "
                f"{sorted(regions_manquantes)}"
            )

        if regions_inconnues:
            raise ValueError(
                f"Régions inconnues dans {nom_fichier} : "
                f"{sorted(regions_inconnues)}"
            )

    # Exportation sans écraser le fichier source
    chemin_sortie = DOSSIER_SORTIE / nom_fichier

    df.to_csv(
        chemin_sortie,
        index=False,
        encoding="utf-8-sig"
    )

    # Enregistrement des informations de contrôle
    lignes_supprimees = nombre_lignes_initial - len(df)

    rapports.append({
        "fichier": nom_fichier,
        "lignes_initiales": nombre_lignes_initial,
        "lignes_finales": len(df),
        "lignes_supprimees": lignes_supprimees,
        "regions_distinctes": (
            df[colonne_region].nunique()
            if colonne_region is not None
            else "Non applicable"
        ),
        "fichier_genere": chemin_sortie.name
    })

    print(f"Lignes initiales : {nombre_lignes_initial}")
    print(f"Lignes finales : {len(df)}")
    print(f"Lignes supprimées : {lignes_supprimees}")
    print("Traitement terminé.")


# Création du rapport global
rapport = pd.DataFrame(rapports)

DOSSIER_RAPPORT = BASE_DIR / "outputs" / "tables"
DOSSIER_RAPPORT.mkdir(parents=True, exist_ok=True)

fichier_rapport = (
    DOSSIER_RAPPORT
    / "rapport_harmonisation_suppression_totaux.csv"
)

rapport.to_csv(
    fichier_rapport,
    index=False,
    encoding="utf-8-sig"
)


# Résumé final
print("\n" + "=" * 55)
print("RÉSUMÉ DE L'HARMONISATION ET DU NETTOYAGE")
print("=" * 55)

print(f"Fichiers traités : {len(rapport)}")
print(f"Lignes initiales : {rapport['lignes_initiales'].sum()}")
print(f"Lignes finales : {rapport['lignes_finales'].sum()}")
print(f"Lignes supprimées : {rapport['lignes_supprimees'].sum()}")

print(f"\nDossier de sortie : {DOSSIER_SORTIE}")
print(f"Rapport : {fichier_rapport}")
