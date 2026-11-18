
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
    / "03_cleaned_data"
    / "final"
)

DOSSIER_SORTIE = (
    RACINE_PROJET
    / "data"
    / "04_transformed_data"
    / "transformed_sheets"
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
# 2. FONCTIONS UTILITAIRES
# ============================================================

def lire_donnees(nom_fichier):
    """Charge un fichier CSV nettoyé."""

    chemin = DOSSIER_SOURCE / nom_fichier

    if not chemin.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {chemin}"
        )

    return pd.read_csv(
        chemin,
        encoding="utf-8-sig"
    )


def verifier_colonnes(df, colonnes, nom_fichier):
    """Vérifie la présence des colonnes nécessaires."""

    absentes = [
        col for col in colonnes
        if col not in df.columns
    ]

    if absentes:
        raise ValueError(
            f"{nom_fichier} : colonnes absentes : {absentes}"
        )


def convertir_valeurs_numeriques(df, colonne):
    """Convertit une colonne en format numérique."""

    df = df.copy()

    df[colonne] = pd.to_numeric(
        df[colonne],
        errors="raise"
    )

    return df


def enregistrer_transformation(
    nom_fichier,
    df_source,
    df_long,
    colonnes_cles,
    colonne_valeur
):
    """Contrôle et enregistre un jeu de données transformé."""

    df_long = df_long.copy()

    # Vérifier les valeurs manquantes
    valeurs_manquantes = int(
        df_long.isna().sum().sum()
    )

    # Vérifier les doublons sur les clés métier
    doublons = int(
        df_long.duplicated(
            subset=colonnes_cles
        ).sum()
    )

    # Convertir la variable étudiée en numérique
    df_long = convertir_valeurs_numeriques(
        df_long,
        colonne_valeur
    )

    # Vérifier les valeurs négatives
    valeurs_negatives = int(
        (df_long[colonne_valeur] < 0).sum()
    )

    # Vérifier les valeurs infinies
    valeurs_numeriques = df_long[colonne_valeur].to_numpy(
        dtype=float
    )

    valeurs_infinies = int(
        np.isinf(valeurs_numeriques).sum()
    )

    # Déterminer le statut
    statut = "VALIDE"

    if valeurs_manquantes > 0:
        statut = "A VERIFIER"

    if doublons > 0:
        statut = "A VERIFIER"

    if valeurs_negatives > 0:
        statut = "A VERIFIER"

    if valeurs_infinies > 0:
        statut = "A VERIFIER"

    # Enregistrer le fichier transformé
    nom_sortie = nom_fichier.replace(
        ".csv",
        "_long.csv"
    )

    chemin_sortie = DOSSIER_SORTIE / nom_sortie

    df_long.to_csv(
        chemin_sortie,
        index=False,
        encoding="utf-8-sig"
    )

    # Afficher les résultats
    print(f"\nFichier : {nom_fichier}")
    print(f"Nombre de lignes initial : {len(df_source)}")
    print(f"Nombre de lignes transformé : {len(df_long)}")
    print(f"Valeurs manquantes : {valeurs_manquantes}")
    print(f"Doublons sur les clés : {doublons}")
    print(f"Valeurs négatives : {valeurs_negatives}")
    print(f"Valeurs infinies : {valeurs_infinies}")
    print(f"Statut : {statut}")
    print(f"Fichier enregistré : {chemin_sortie}")

    return {
        "FICHIER_SOURCE": nom_fichier,
        "LIGNES_SOURCE": len(df_source),
        "LIGNES_TRANSFORMEES": len(df_long),
        "VALEURS_MANQUANTES": valeurs_manquantes,
        "DOUBLONS_CLES": doublons,
        "VALEURS_NEGATIVES": valeurs_negatives,
        "VALEURS_INFINIES": valeurs_infinies,
        "STATUT": statut,
        "FICHIER_SORTIE": str(chemin_sortie)
    }


# ============================================================
# 3. TRANSFORMATION DES EFFECTIFS PAR REGION ET SEXE
# ============================================================

def transformer_effectifs_region():

    nom = "effectifs_primaire_region_sexe.csv"

    df = lire_donnees(nom)

    verifier_colonnes(
        df,
        ["REGION", "SEXE"],
        nom
    )

    colonnes_annees = [
        col for col in df.columns
        if col not in ["REGION", "SEXE"]
    ]

    df_long = df.melt(
        id_vars=["REGION", "SEXE"],
        value_vars=colonnes_annees,
        var_name="ANNEE_SCOLAIRE",
        value_name="EFFECTIF"
    )

    return enregistrer_transformation(
        nom,
        df,
        df_long,
        ["REGION", "SEXE", "ANNEE_SCOLAIRE"],
        "EFFECTIF"
    )


# ============================================================
# 4. TRANSFORMATION DES EFFECTIFS PAR MILIEU ET SEXE
# ============================================================

def transformer_effectifs_milieu():

    nom = "effectifs_primaire_milieu_sexe.csv"

    df = lire_donnees(nom)

    verifier_colonnes(
        df,
        ["MILIEU", "SEXE"],
        nom
    )

    # Exclure le niveau national pour comparer
    # uniquement les milieux urbain et rural.

    df_analytique = df[
        df["MILIEU"].isin(["URBAIN", "RURAL"])
    ].copy()

    colonnes_annees = [
        col for col in df.columns
        if col not in ["MILIEU", "SEXE"]
    ]

    df_long = df_analytique.melt(
        id_vars=["MILIEU", "SEXE"],
        value_vars=colonnes_annees,
        var_name="ANNEE_SCOLAIRE",
        value_name="EFFECTIF"
    )

    return enregistrer_transformation(
        nom,
        df_analytique,
        df_long,
        ["MILIEU", "SEXE", "ANNEE_SCOLAIRE"],
        "EFFECTIF"
    )


# ============================================================
# 5. TRANSFORMATION DES TAUX PAR REGION, ANNEE ET SEXE
# ============================================================

def transformer_taux_region(nom_fichier, nom_valeur):

    df = lire_donnees(nom_fichier)

    verifier_colonnes(
        df,
        ["REGION"],
        nom_fichier
    )

    colonnes_indicateurs = [
        col for col in df.columns
        if col != "REGION"
    ]

    df_long = df.melt(
        id_vars=["REGION"],
        value_vars=colonnes_indicateurs,
        var_name="ANNEE_SEXE",
        value_name=nom_valeur
    )

    # Séparer l'année scolaire et la catégorie de sexe
    elements = df_long["ANNEE_SEXE"].str.rsplit(
        "_",
        n=1,
        expand=True
    )

    if elements.shape[1] != 2:
        raise ValueError(
            f"Format année/sexe inattendu dans {nom_fichier}"
        )

    df_long["ANNEE_SCOLAIRE"] = elements[0]
    df_long["SEXE"] = elements[1]

    df_long = df_long.drop(
        columns=["ANNEE_SEXE"]
    )

    df_long = df_long[
        ["REGION", "ANNEE_SCOLAIRE", "SEXE", nom_valeur]
    ]

    return enregistrer_transformation(
        nom_fichier,
        df,
        df_long,
        ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
        nom_valeur
    )


# ============================================================
# 6. TRANSFORMATION DES TAUX DE REUSSITE AU CEP
# ============================================================

def transformer_cep():

    nom = "taux_reussite_cep_region_sexe.csv"

    df = lire_donnees(nom)

    verifier_colonnes(
        df,
        ["REGION", "SEXE"],
        nom
    )

    colonnes_annees = [
        col for col in df.columns
        if col not in ["REGION", "SEXE"]
    ]

    df_long = df.melt(
        id_vars=["REGION", "SEXE"],
        value_vars=colonnes_annees,
        var_name="ANNEE_CIVILE",
        value_name="TAUX_REUSSITE"
    )

    return enregistrer_transformation(
        nom,
        df,
        df_long,
        ["REGION", "SEXE", "ANNEE_CIVILE"],
        "TAUX_REUSSITE"
    )


# ============================================================
# 7. TRANSFORMATION DES INDICES DE PARITE
# ============================================================

def transformer_ips(nom_fichier):

    df = lire_donnees(nom_fichier)

    verifier_colonnes(
        df,
        ["REGION"],
        nom_fichier
    )

    colonnes_annees = [
        col for col in df.columns
        if col != "REGION"
    ]

    df_long = df.melt(
        id_vars=["REGION"],
        value_vars=colonnes_annees,
        var_name="ANNEE_SCOLAIRE",
        value_name="IPS"
    )

    return enregistrer_transformation(
        nom_fichier,
        df,
        df_long,
        ["REGION", "ANNEE_SCOLAIRE"],
        "IPS"
    )


# ============================================================
# 8. TRANSFORMATION DU NOMBRE D'ECOLES
# ============================================================

def transformer_ecoles():

    nom = "ecoles_primaire_region_statut.csv"

    df = lire_donnees(nom)

    verifier_colonnes(
        df,
        ["REGION", "STATUT"],
        nom
    )

    colonnes_annees = [
        col for col in df.columns
        if col not in ["REGION", "STATUT"]
    ]

    df_long = df.melt(
        id_vars=["REGION", "STATUT"],
        value_vars=colonnes_annees,
        var_name="ANNEE_SCOLAIRE",
        value_name="NOMBRE_ECOLES"
    )

    return enregistrer_transformation(
        nom,
        df,
        df_long,
        ["REGION", "STATUT", "ANNEE_SCOLAIRE"],
        "NOMBRE_ECOLES"
    )


# ============================================================
# 9. TRANSFORMATION DES NOUVEAUX INSCRITS AU CP1 (FEUIL5)
# ============================================================

def transformer_nouveaux_inscrits_cp1():

    nom = "nouveaux_inscrits_cp1_region_sexe.csv"

    df = lire_donnees(nom)

    # Nom réel de la colonne dans le fichier nettoyé
    colonnes_requises = [
        "REGION",
        "ANNEE_SCOLAIRE",
        "SEXE",
        "NOUVEAUX_INSCRITS_CP1"
    ]

    verifier_colonnes(
        df,
        colonnes_requises,
        nom
    )

    # Le fichier est déjà au format long.
    # On ne lui applique donc pas melt().

    df_long = df[colonnes_requises].copy()

    # Harmoniser le nom de la variable d'effectif
    df_long = df_long.rename(
        columns={
            "NOUVEAUX_INSCRITS_CP1": "EFFECTIF"
        }
    )

    # Vérifier le nombre d'observations
    if len(df_long) != 260:
        raise ValueError(
            f"{nom} : 260 observations attendues, "
            f"{len(df_long)} trouvées."
        )

    # Vérifier les 13 régions
    if df_long["REGION"].nunique() != 13:
        raise ValueError(
            f"{nom} : 13 régions attendues."
        )

    # Vérifier les 10 années scolaires
    annees_attendues = {
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
    }

    annees_observees = set(
        df_long["ANNEE_SCOLAIRE"].dropna().unique()
    )

    if annees_observees != annees_attendues:
        raise ValueError(
            f"{nom} : les années scolaires ne correspondent pas "
            "à la période attendue."
        )

    # Vérifier les catégories de sexe
    categories_attendues = {"FILLES", "GARCONS"}

    categories_observees = set(
        df_long["SEXE"].dropna().unique()
    )

    if categories_observees != categories_attendues:
        raise ValueError(
            f"{nom} : catégories incorrectes : "
            f"{categories_observees}"
        )

    # Vérifier les combinaisons régionales
    doublons = df_long.duplicated(
        subset=[
            "REGION",
            "ANNEE_SCOLAIRE",
            "SEXE"
        ]
    ).sum()

    if doublons > 0:
        raise ValueError(
            f"{nom} : {doublons} combinaison(s) en double."
        )

    # Vérifier les valeurs manquantes
    if df_long.isna().sum().sum() > 0:
        raise ValueError(
            f"{nom} : valeurs manquantes détectées."
        )

    # Vérifier les valeurs numériques
    df_long["EFFECTIF"] = pd.to_numeric(
        df_long["EFFECTIF"],
        errors="raise"
    )

    # Vérifier les valeurs négatives
    if (df_long["EFFECTIF"] < 0).any():
        raise ValueError(
            f"{nom} : valeurs négatives détectées."
        )

    # Vérifier les valeurs infinies
    if not np.isfinite(
        df_long["EFFECTIF"].to_numpy(dtype=float)
    ).all():
        raise ValueError(
            f"{nom} : valeurs infinies détectées."
        )

    # Vérifier les combinaisons attendues
    nombre_combinaisons_attendues = (
        13 * 10 * 2
    )

    if len(df_long) != nombre_combinaisons_attendues:
        raise ValueError(
            f"{nom} : combinaisons attendues : "
            f"{nombre_combinaisons_attendues}."
        )

    print("\nContrôles spécifiques Feuil5 :")
    print("Nombre d'observations :", len(df_long))
    print("Nombre de régions :", df_long["REGION"].nunique())
    print("Nombre d'années :", df_long["ANNEE_SCOLAIRE"].nunique())
    print("Catégories :", sorted(categories_observees))
    print("Combinaisons en double :", int(doublons))
    print("Contrôles spécifiques : VALIDÉS")

    return enregistrer_transformation(
        nom,
        df,
        df_long,
        [
            "REGION",
            "ANNEE_SCOLAIRE",
            "SEXE"
        ],
        "EFFECTIF"
    )


# ============================================================
# 10. EXECUTION DE TOUTES LES TRANSFORMATIONS
# ============================================================

def main():

    print("=" * 65)
    print("DEBUT DE LA TRANSFORMATION GLOBALE DES DONNEES")
    print("=" * 65)

    rapports = []

    # Effectifs par région et par sexe
    rapports.append(
        transformer_effectifs_region()
    )

    # Effectifs par milieu et par sexe
    rapports.append(
        transformer_effectifs_milieu()
    )

    # Taux d'admission, de scolarisation et d'achèvement
    rapports.append(
        transformer_taux_region(
            "tba_primaire_region_sexe.csv",
            "TBA"
        )
    )

    rapports.append(
        transformer_taux_region(
            "tbs_primaire_region_sexe.csv",
            "TBS"
        )
    )

    rapports.append(
        transformer_taux_region(
            "tap_primaire_region_sexe.csv",
            "TAP"
        )
    )

    # Taux de réussite au CEP
    rapports.append(
        transformer_cep()
    )

    # Indices de parité
    rapports.append(
        transformer_ips(
            "ips_tba_primaire_region.csv"
        )
    )

    rapports.append(
        transformer_ips(
            "ips_tbs_primaire_region.csv"
        )
    )

    rapports.append(
        transformer_ips(
            "ips_tap_primaire_region.csv"
        )
    )

    # Nombre d'écoles par région et statut
    rapports.append(
        transformer_ecoles()
    )

    # Nouveaux inscrits au CP1 (Feuil5)
    rapports.append(
        transformer_nouveaux_inscrits_cp1()
    )

    # Construire le rapport global
    rapport = pd.DataFrame(rapports)

    chemin_rapport = (
        DOSSIER_RAPPORT
        / "rapport_transformation_globale.csv"
    )

    rapport.to_csv(
        chemin_rapport,
        index=False,
        encoding="utf-8-sig"
    )

    # Résumé global
    print("\n" + "=" * 65)
    print("RESUME GLOBAL")
    print("=" * 65)

    print(
        rapport[
            [
                "FICHIER_SOURCE",
                "LIGNES_TRANSFORMEES",
                "STATUT"
            ]
        ].to_string(index=False)
    )

    nombre_fichiers = len(rapport)

    nombre_valides = int(
        (rapport["STATUT"] == "VALIDE").sum()
    )

    nombre_a_verifier = int(
        (rapport["STATUT"] != "VALIDE").sum()
    )

    print("\nNombre de fichiers traités :", nombre_fichiers)
    print("Fichiers valides :", nombre_valides)
    print("Fichiers à vérifier :", nombre_a_verifier)

    print("\nRapport enregistré :", chemin_rapport)

    if nombre_a_verifier > 0:
        print("\nTRANSFORMATION TERMINEE AVEC DES ANOMALIES.")
    else:
        print("\nTRANSFORMATION GLOBALE TERMINEE AVEC SUCCES.")


if __name__ == "__main__":
    main()
