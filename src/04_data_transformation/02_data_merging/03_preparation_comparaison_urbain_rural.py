
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

RACINE_PROJET = Path(__file__).resolve().parents[3]

DOSSIER_SOURCE = (
    RACINE_PROJET
    / "data"
    / "04_transformed_data"
    / "transformed_sheets"
)

DOSSIER_SORTIE = (
    RACINE_PROJET
    / "data"
    / "04_transformed_data"
    / "merged"
)

DOSSIER_RAPPORT = (
    RACINE_PROJET
    / "outputs"
    / "tables"
    / "transformation"
)

DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
DOSSIER_RAPPORT.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. PARAMETRES DE VALIDATION
# ============================================================

FICHIER_SOURCE = "effectifs_primaire_milieu_sexe_long.csv"

CATEGORIES_MILIEU = [
    "URBAIN",
    "RURAL"
]

CATEGORIES_SEXE = [
    "FILLES",
    "GARCONS"
]

CLES_SOURCE = [
    "MILIEU",
    "SEXE",
    "ANNEE_SCOLAIRE"
]

NOMBRE_ANNEES_ATTENDU = 10

NOMBRE_LIGNES_SOURCE_ATTENDU = 40

NOMBRE_LIGNES_RESULTAT_ATTENDU = 20

ANNEES_ATTENDUES = [
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


# ============================================================
# 3. CHARGEMENT DES DONNEES
# ============================================================

def charger_donnees():

    chemin = DOSSIER_SOURCE / FICHIER_SOURCE

    if not chemin.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {chemin}"
        )

    df = pd.read_csv(
        chemin,
        encoding="utf-8-sig"
    )

    if df.empty:
        raise ValueError(
            "Le fichier source est vide."
        )

    print("Fichier chargé :", FICHIER_SOURCE)
    print("Nombre de lignes :", len(df))

    return df


# ============================================================
# 4. PREPARATION ET CONTROLE DES DONNEES
# ============================================================

def preparer_donnees(df):

    colonnes_requises = [
        "MILIEU",
        "SEXE",
        "ANNEE_SCOLAIRE",
        "EFFECTIF"
    ]

    colonnes_absentes = [
        col for col in colonnes_requises
        if col not in df.columns
    ]

    if colonnes_absentes:
        raise ValueError(
            f"Colonnes absentes : {colonnes_absentes}"
        )

    df = df[colonnes_requises].copy()

    # Harmonisation des variables catégorielles
    for colonne in [
        "MILIEU",
        "SEXE",
        "ANNEE_SCOLAIRE"
    ]:

        df[colonne] = (
            df[colonne]
            .astype("string")
            .str.strip()
            .str.upper()
        )

    # Vérification des valeurs manquantes
    if df.isna().any().any():
        raise ValueError(
            "Le fichier contient des valeurs manquantes."
        )

    # Vérification des chaînes vides
    for colonne in CLES_SOURCE:

        if (df[colonne] == "").any():
            raise ValueError(
                f"La colonne {colonne} contient des valeurs vides."
            )

    # Conversion numérique des effectifs
    df["EFFECTIF"] = pd.to_numeric(
        df["EFFECTIF"],
        errors="raise"
    )

    if df["EFFECTIF"].isna().any():
        raise ValueError(
            "La colonne EFFECTIF contient des valeurs manquantes."
        )

    # Vérification des valeurs infinies
    if np.isinf(df["EFFECTIF"]).any():
        raise ValueError(
            "Des valeurs infinies ont été détectées."
        )

    # Vérification des valeurs négatives
    if (df["EFFECTIF"] < 0).any():
        raise ValueError(
            "Des effectifs négatifs ont été détectés."
        )

    # Vérification des catégories de milieu
    milieux_observes = set(df["MILIEU"].unique())

    if milieux_observes != set(CATEGORIES_MILIEU):
        raise ValueError(
            f"Catégories de milieu inattendues : "
            f"{milieux_observes}"
        )

    # Vérification des catégories de sexe
    sexes_observes = set(df["SEXE"].unique())

    if sexes_observes != set(CATEGORIES_SEXE):
        raise ValueError(
            f"Catégories de sexe inattendues : "
            f"{sexes_observes}"
        )

    # Vérification des années scolaires
    annees_observees = set(
        df["ANNEE_SCOLAIRE"].unique()
    )

    if annees_observees != set(ANNEES_ATTENDUES):
        raise ValueError(
            "Les années scolaires ne correspondent pas "
            "aux années attendues.\n"
            f"Années trouvées : {sorted(annees_observees)}"
        )

    # Vérification du nombre de lignes
    if len(df) != NOMBRE_LIGNES_SOURCE_ATTENDU:
        raise ValueError(
            f"Nombre de lignes incorrect : {len(df)}. "
            f"{NOMBRE_LIGNES_SOURCE_ATTENDU} attendues."
        )

    # Vérification des doublons
    doublons = int(
        df.duplicated(
            subset=CLES_SOURCE
        ).sum()
    )

    if doublons > 0:
        raise ValueError(
            f"{doublons} doublons détectés."
        )

    print("\nPréparation des données : VALIDE")
    print("Catégories de milieu :", sorted(milieux_observes))
    print("Catégories de sexe :", sorted(sexes_observes))
    print("Nombre d'années :", len(annees_observees))
    print("Nombre d'observations :", len(df))

    return df


# ============================================================
# 5. VERIFICATION DE LA COMPLETUDE
# ============================================================

def verifier_completude(df):

    combinaisons_attendues = pd.MultiIndex.from_product(
        [
            CATEGORIES_MILIEU,
            CATEGORIES_SEXE,
            ANNEES_ATTENDUES
        ],
        names=CLES_SOURCE
    ).to_frame(index=False)

    comparaison = combinaisons_attendues.merge(
        df[CLES_SOURCE],
        on=CLES_SOURCE,
        how="outer",
        indicator=True
    )

    combinaisons_manquantes = int(
        (comparaison["_merge"] == "left_only").sum()
    )

    combinaisons_supplementaires = int(
        (comparaison["_merge"] == "right_only").sum()
    )

    print("\nCONTROLE DE COMPLETUDE")

    print(
        "Années scolaires :",
        len(ANNEES_ATTENDUES)
    )

    print(
        "Combinaisons attendues :",
        len(combinaisons_attendues)
    )

    print(
        "Combinaisons manquantes :",
        combinaisons_manquantes
    )

    print(
        "Combinaisons supplémentaires :",
        combinaisons_supplementaires
    )

    if (
        combinaisons_manquantes > 0
        or combinaisons_supplementaires > 0
    ):
        raise ValueError(
            "Les combinaisons milieu-sexe-année "
            "ne sont pas complètes."
        )

    print("Complétude : VALIDEE")

    return combinaisons_attendues


# ============================================================
# 6. CONSTRUCTION DE LA TABLE COMPARATIVE
# ============================================================

def construire_comparaison(df):

    tableau = df.pivot(
        index=[
            "ANNEE_SCOLAIRE",
            "SEXE"
        ],
        columns="MILIEU",
        values="EFFECTIF"
    ).reset_index()

    tableau.columns.name = None

    # Renommer les colonnes
    tableau = tableau.rename(
        columns={
            "URBAIN": "EFFECTIF_URBAIN",
            "RURAL": "EFFECTIF_RURAL"
        }
    )

    # Vérifier la présence des deux milieux
    colonnes_effectifs = [
        "EFFECTIF_URBAIN",
        "EFFECTIF_RURAL"
    ]

    if tableau[colonnes_effectifs].isna().any().any():
        raise ValueError(
            "Des effectifs sont manquants après le pivot."
        )

    # Calcul de la différence signée
    tableau["ECART_URBAIN_MOINS_RURAL"] = (
        tableau["EFFECTIF_URBAIN"]
        - tableau["EFFECTIF_RURAL"]
    )

    # Calcul de la différence absolue
    tableau["ECART_ABSOLU"] = (
        tableau["ECART_URBAIN_MOINS_RURAL"].abs()
    )

    # Calcul du rapport urbain/rural
    tableau["RATIO_URBAIN_RURAL"] = (
        tableau["EFFECTIF_URBAIN"]
        / tableau["EFFECTIF_RURAL"].where(
            tableau["EFFECTIF_RURAL"] != 0
        )
    )

    # Organisation des colonnes
    tableau = tableau[
        [
            "ANNEE_SCOLAIRE",
            "SEXE",
            "EFFECTIF_URBAIN",
            "EFFECTIF_RURAL",
            "ECART_URBAIN_MOINS_RURAL",
            "ECART_ABSOLU",
            "RATIO_URBAIN_RURAL"
        ]
    ]

    tableau = tableau.sort_values(
        by=[
            "ANNEE_SCOLAIRE",
            "SEXE"
        ]
    ).reset_index(drop=True)

    return tableau


# ============================================================
# 7. CONTROLE DE LA TABLE COMPARATIVE
# ============================================================

def controler_resultat(df_source, df_resultat):

    doublons = int(
        df_resultat.duplicated(
            subset=[
                "ANNEE_SCOLAIRE",
                "SEXE"
            ]
        ).sum()
    )

    valeurs_manquantes = int(
        df_resultat.isna().sum().sum()
    )

    colonnes_numeriques = (
        df_resultat.select_dtypes(
            include=[np.number]
        )
    )

    valeurs_infinies = int(
        np.isinf(colonnes_numeriques).sum().sum()
    )

    lignes_attendues = NOMBRE_LIGNES_RESULTAT_ATTENDU
    lignes_obtenues = len(df_resultat)

    # Vérification de la conservation des effectifs
    total_source = df_source["EFFECTIF"].sum()

    total_resultat = (
        df_resultat["EFFECTIF_URBAIN"].sum()
        + df_resultat["EFFECTIF_RURAL"].sum()
    )

    conservation_effectifs = (
        np.isclose(
            total_source,
            total_resultat,
            rtol=0,
            atol=1e-9
        )
    )

    statut = (
        "VALIDE"
        if (
            doublons == 0
            and valeurs_manquantes == 0
            and valeurs_infinies == 0
            and lignes_attendues == lignes_obtenues
            and conservation_effectifs
        )
        else "A VERIFIER"
    )

    print("\nCONTROLE FINAL")

    print("Lignes attendues :", lignes_attendues)
    print("Lignes obtenues :", lignes_obtenues)
    print("Doublons :", doublons)
    print("Valeurs manquantes :", valeurs_manquantes)
    print("Valeurs infinies :", valeurs_infinies)
    print("Total source :", total_source)
    print("Total comparatif :", total_resultat)
    print("Conservation des effectifs :", conservation_effectifs)
    print("STATUT :", statut)

    if statut != "VALIDE":
        raise ValueError(
            "La table comparative n'a pas passé les contrôles."
        )

    return {
        "FICHIER_SOURCE": FICHIER_SOURCE,
        "LIGNES_SOURCE": len(df_source),
        "LIGNES_RESULTAT": lignes_obtenues,
        "DOUBLONS": doublons,
        "VALEURS_MANQUANTES": valeurs_manquantes,
        "VALEURS_INFINIES": valeurs_infinies,
        "TOTAL_SOURCE": total_source,
        "TOTAL_RESULTAT": total_resultat,
        "CONSERVATION_EFFECTIFS": conservation_effectifs,
        "STATUT": statut
    }


# ============================================================
# 8. EXECUTION PRINCIPALE
# ============================================================

def main():

    print("=" * 70)
    print("PREPARATION DE LA COMPARAISON URBAIN-RURAL")
    print("=" * 70)

    # Charger les données
    df = charger_donnees()

    # Préparer les données
    df = preparer_donnees(df)

    # Vérifier la complétude
    verifier_completude(df)

    # Construire la table comparative
    comparaison = construire_comparaison(df)

    # Contrôler le résultat
    rapport = controler_resultat(
        df,
        comparaison
    )

    # Enregistrer la table comparative
    chemin_sortie = (
        DOSSIER_SORTIE
        / "comparaison_effectifs_urbain_rural.csv"
    )

    comparaison.to_csv(
        chemin_sortie,
        index=False,
        encoding="utf-8-sig"
    )

    # Enregistrer le rapport
    chemin_rapport = (
        DOSSIER_RAPPORT
        / "rapport_comparaison_urbain_rural.csv"
    )

    pd.DataFrame([rapport]).to_csv(
        chemin_rapport,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nFichier comparatif enregistré :")
    print(chemin_sortie)

    print("\nRapport enregistré :")
    print(chemin_rapport)

    print("\n" + "=" * 70)
    print("PREPARATION TERMINEE AVEC SUCCES")
    print("=" * 70)

    print("\nAperçu de la table comparative :")

    print(
        comparaison.to_string(index=False)
    )

    print("\nDimensions finales :")
    print(comparaison.shape)

    print("\nColonnes finales :")
    print(list(comparaison.columns))


# ============================================================
# 9. POINT D'ENTREE
# ============================================================

if __name__ == "__main__":
    main()
