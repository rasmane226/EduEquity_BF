
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

DOSSIER_TRANSFORME = (
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

DOSSIER_RAPPORT.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. FONCTION DE LECTURE DES FICHIERS
# ============================================================

def lire_csv(chemin):
    """
    Charge un fichier CSV après vérification de son existence.
    """

    if not chemin.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {chemin}"
        )

    return pd.read_csv(
        chemin,
        encoding="utf-8-sig"
    )


# ============================================================
# 3. RECONSTRUCTION DES DONNEES ATTENDUES
# ============================================================

def preparer_attendu(nom_fichier):
    """
    Reconstruit le format long attendu à partir du fichier nettoyé.

    Cette reconstruction sert de référence pour vérifier
    le fichier transformé.
    """

    df = lire_csv(
        DOSSIER_SOURCE / nom_fichier
    )

    # --------------------------------------------------------
    # A. EFFECTIFS PAR REGION ET SEXE
    # --------------------------------------------------------

    if nom_fichier == "effectifs_primaire_region_sexe.csv":

        colonnes_cles = [
            "REGION",
            "SEXE"
        ]

        colonnes_annees = [
            col for col in df.columns
            if col not in colonnes_cles
        ]

        attendu = df.melt(
            id_vars=colonnes_cles,
            value_vars=colonnes_annees,
            var_name="ANNEE_SCOLAIRE",
            value_name="EFFECTIF"
        )

        cles = [
            "REGION",
            "SEXE",
            "ANNEE_SCOLAIRE"
        ]

        valeur = "EFFECTIF"

    # --------------------------------------------------------
    # B. EFFECTIFS PAR MILIEU ET SEXE
    # --------------------------------------------------------

    elif nom_fichier == "effectifs_primaire_milieu_sexe.csv":

        # Exclure NATIONAL uniquement pour l'analyse urbaine-rurale
        df = df[
            df["MILIEU"].isin(["URBAIN", "RURAL"])
        ].copy()

        colonnes_cles = [
            "MILIEU",
            "SEXE"
        ]

        colonnes_annees = [
            col for col in df.columns
            if col not in colonnes_cles
        ]

        attendu = df.melt(
            id_vars=colonnes_cles,
            value_vars=colonnes_annees,
            var_name="ANNEE_SCOLAIRE",
            value_name="EFFECTIF"
        )

        cles = [
            "MILIEU",
            "SEXE",
            "ANNEE_SCOLAIRE"
        ]

        valeur = "EFFECTIF"

    # --------------------------------------------------------
    # C. TBA, TBS ET TAP
    # --------------------------------------------------------

    elif nom_fichier in [
        "tba_primaire_region_sexe.csv",
        "tbs_primaire_region_sexe.csv",
        "tap_primaire_region_sexe.csv"
    ]:

        nom_valeur = nom_fichier.split("_")[0].upper()

        attendu = df.melt(
            id_vars=["REGION"],
            var_name="ANNEE_SEXE",
            value_name=nom_valeur
        )

        # Séparer l'année scolaire et la catégorie de sexe
        elements = attendu[
            "ANNEE_SEXE"
        ].str.rsplit(
            "_",
            n=1,
            expand=True
        )

        if elements.shape[1] != 2:
            raise ValueError(
                f"Format année/sexe incorrect : {nom_fichier}"
            )

        attendu["ANNEE_SCOLAIRE"] = elements[0]
        attendu["SEXE"] = elements[1]

        attendu = attendu.drop(
            columns=["ANNEE_SEXE"]
        )

        cles = [
            "REGION",
            "ANNEE_SCOLAIRE",
            "SEXE"
        ]

        valeur = nom_valeur

    # --------------------------------------------------------
    # D. TAUX DE REUSSITE AU CEP
    # --------------------------------------------------------

    elif nom_fichier == "taux_reussite_cep_region_sexe.csv":

        colonnes_cles = [
            "REGION",
            "SEXE"
        ]

        colonnes_annees = [
            col for col in df.columns
            if col not in colonnes_cles
        ]

        attendu = df.melt(
            id_vars=colonnes_cles,
            value_vars=colonnes_annees,
            var_name="ANNEE_CIVILE",
            value_name="TAUX_REUSSITE"
        )

        cles = [
            "REGION",
            "SEXE",
            "ANNEE_CIVILE"
        ]

        valeur = "TAUX_REUSSITE"

    # --------------------------------------------------------
    # E. INDICES DE PARITE SCOLAIRE
    # --------------------------------------------------------

    elif nom_fichier in [
        "ips_tba_primaire_region.csv",
        "ips_tbs_primaire_region.csv",
        "ips_tap_primaire_region.csv"
    ]:

        colonnes_annees = [
            col for col in df.columns
            if col != "REGION"
        ]

        attendu = df.melt(
            id_vars=["REGION"],
            value_vars=colonnes_annees,
            var_name="ANNEE_SCOLAIRE",
            value_name="IPS"
        )

        cles = [
            "REGION",
            "ANNEE_SCOLAIRE"
        ]

        valeur = "IPS"

    # --------------------------------------------------------
    # F. NOMBRE D'ECOLES PAR REGION ET STATUT
    # --------------------------------------------------------

    elif nom_fichier == "ecoles_primaire_region_statut.csv":

        colonnes_cles = [
            "REGION",
            "STATUT"
        ]

        colonnes_annees = [
            col for col in df.columns
            if col not in colonnes_cles
        ]

        attendu = df.melt(
            id_vars=colonnes_cles,
            value_vars=colonnes_annees,
            var_name="ANNEE_SCOLAIRE",
            value_name="NOMBRE_ECOLES"
        )

        cles = [
            "REGION",
            "STATUT",
            "ANNEE_SCOLAIRE"
        ]

        valeur = "NOMBRE_ECOLES"

    else:

        raise ValueError(
            f"Type de fichier non reconnu : {nom_fichier}"
        )

    # Conversion numérique des valeurs de référence
    attendu[valeur] = pd.to_numeric(
        attendu[valeur],
        errors="raise"
    )

    return attendu, cles, valeur


# ============================================================
# 4. VALIDATION D'UN FICHIER TRANSFORME
# ============================================================

def comparer_donnees(nom_fichier):

    nom_transforme = nom_fichier.replace(
        ".csv",
        "_long.csv"
    )

    chemin_transforme = (
        DOSSIER_TRANSFORME / nom_transforme
    )

    # Reconstruction des données attendues
    attendu, cles, valeur = preparer_attendu(
        nom_fichier
    )

    # Lecture du fichier transformé
    obtenu = lire_csv(
        chemin_transforme
    )

    colonnes_attendues = cles + [valeur]

    # --------------------------------------------------------
    # A. VERIFICATION DES COLONNES
    # --------------------------------------------------------

    colonnes_absentes = [
        col for col in colonnes_attendues
        if col not in obtenu.columns
    ]

    if colonnes_absentes:

        raise ValueError(
            f"{nom_transforme} : colonnes absentes "
            f"{colonnes_absentes}"
        )

    obtenu = obtenu[
        colonnes_attendues
    ].copy()

    # --------------------------------------------------------
    # B. HARMONISATION DES TYPES DES CLES
    # --------------------------------------------------------

    # Les colonnes de clés sont des identifiants.
    # On les convertit en chaînes de caractères
    # pour éviter les conflits entre str et int64.

    for colonne in cles:

        attendu[colonne] = (
            attendu[colonne]
            .astype("string")
            .str.strip()
        )

        obtenu[colonne] = (
            obtenu[colonne]
            .astype("string")
            .str.strip()
        )

    # --------------------------------------------------------
    # C. CONVERSION DES VALEURS NUMERIQUES
    # --------------------------------------------------------

    attendu[valeur] = pd.to_numeric(
        attendu[valeur],
        errors="raise"
    )

    obtenu[valeur] = pd.to_numeric(
        obtenu[valeur],
        errors="raise"
    )

    # --------------------------------------------------------
    # D. CONTROLE DES DOUBLONS
    # --------------------------------------------------------

    doublons_attendus = int(
        attendu.duplicated(
            subset=cles
        ).sum()
    )

    doublons_obtenus = int(
        obtenu.duplicated(
            subset=cles
        ).sum()
    )

    # --------------------------------------------------------
    # E. COMPARAISON DES CLES
    # --------------------------------------------------------

    comparaison = attendu.merge(
        obtenu,
        on=cles,
        how="outer",
        suffixes=("_attendu", "_obtenu"),
        indicator=True
    )

    cles_manquantes = int(
        (
            comparaison["_merge"] == "left_only"
        ).sum()
    )

    cles_supplementaires = int(
        (
            comparaison["_merge"] == "right_only"
        ).sum()
    )

    # --------------------------------------------------------
    # F. COMPARAISON DES VALEURS
    # --------------------------------------------------------

    communes = comparaison[
        comparaison["_merge"] == "both"
    ].copy()

    valeurs_attendues = communes[
        f"{valeur}_attendu"
    ].to_numpy(dtype=float)

    valeurs_obtenues = communes[
        f"{valeur}_obtenu"
    ].to_numpy(dtype=float)

    egalite = np.isclose(
        valeurs_attendues,
        valeurs_obtenues,
        rtol=1e-10,
        atol=1e-10,
        equal_nan=True
    )

    valeurs_differentes = int(
        (~egalite).sum()
    )

    # --------------------------------------------------------
    # G. CONTROLE DES VALEURS MANQUANTES
    # --------------------------------------------------------

    valeurs_manquantes = int(
        obtenu.isna().sum().sum()
    )

    # --------------------------------------------------------
    # H. DETERMINATION DU STATUT
    # --------------------------------------------------------

    valide = (
        doublons_attendus == 0
        and doublons_obtenus == 0
        and cles_manquantes == 0
        and cles_supplementaires == 0
        and valeurs_differentes == 0
        and valeurs_manquantes == 0
    )

    statut = (
        "VALIDE"
        if valide
        else "A VERIFIER"
    )

    # --------------------------------------------------------
    # I. CONSTRUCTION DU RESULTAT
    # --------------------------------------------------------

    resultat = {

        "FICHIER_SOURCE": nom_fichier,

        "FICHIER_TRANSFORME": nom_transforme,

        "LIGNES_ATTENDUES": len(attendu),

        "LIGNES_OBTENUES": len(obtenu),

        "DOUBLONS_SOURCE": doublons_attendus,

        "DOUBLONS_TRANSFORMES": doublons_obtenus,

        "CLES_MANQUANTES": cles_manquantes,

        "CLES_SUPPLEMENTAIRES": cles_supplementaires,

        "VALEURS_DIFFERENTES": valeurs_differentes,

        "VALEURS_MANQUANTES": valeurs_manquantes,

        "STATUT": statut
    }

    # --------------------------------------------------------
    # J. AFFICHAGE DES RESULTATS
    # --------------------------------------------------------

    print("\n" + "-" * 65)

    print("Fichier :", nom_fichier)

    print("Lignes attendues :", len(attendu))

    print("Lignes obtenues :", len(obtenu))

    print("Doublons source :", doublons_attendus)

    print("Doublons transformés :", doublons_obtenus)

    print("Clés manquantes :", cles_manquantes)

    print("Clés supplémentaires :", cles_supplementaires)

    print("Valeurs différentes :", valeurs_differentes)

    print("Valeurs manquantes :", valeurs_manquantes)

    print("STATUT :", statut)

    return resultat


# ============================================================
# 5. VALIDATION GLOBALE DES 10 FICHIERS
# ============================================================

def main():

    fichiers = [

        "effectifs_primaire_region_sexe.csv",

        "effectifs_primaire_milieu_sexe.csv",

        "tba_primaire_region_sexe.csv",

        "tbs_primaire_region_sexe.csv",

        "tap_primaire_region_sexe.csv",

        "taux_reussite_cep_region_sexe.csv",

        "ips_tba_primaire_region.csv",

        "ips_tbs_primaire_region.csv",

        "ips_tap_primaire_region.csv",

        "ecoles_primaire_region_statut.csv"
    ]

    print("=" * 65)

    print("DEBUT DE LA VALIDATION APPROFONDIE")

    print("=" * 65)

    resultats = []

    erreurs = []

    # Validation indépendante de chaque fichier
    # Une erreur sur un fichier ne bloque pas les suivants.

    for fichier in fichiers:

        try:

            resultat = comparer_donnees(
                fichier
            )

            resultats.append(resultat)

        except Exception as erreur:

            print("\n" + "-" * 65)

            print("ERREUR SUR LE FICHIER :", fichier)

            print("DETAIL :", str(erreur))

            erreurs.append({
                "FICHIER_SOURCE": fichier,
                "ERREUR": str(erreur)
            })

            resultats.append({

                "FICHIER_SOURCE": fichier,

                "FICHIER_TRANSFORME": fichier.replace(
                    ".csv",
                    "_long.csv"
                ),

                "LIGNES_ATTENDUES": None,

                "LIGNES_OBTENUES": None,

                "DOUBLONS_SOURCE": None,

                "DOUBLONS_TRANSFORMES": None,

                "CLES_MANQUANTES": None,

                "CLES_SUPPLEMENTAIRES": None,

                "VALEURS_DIFFERENTES": None,

                "VALEURS_MANQUANTES": None,

                "STATUT": "ERREUR"
            })

    # --------------------------------------------------------
    # 6. ENREGISTREMENT DU RAPPORT GLOBAL
    # --------------------------------------------------------

    rapport = pd.DataFrame(
        resultats
    )

    chemin_rapport = (
        DOSSIER_RAPPORT
        / "rapport_validation_transformation.csv"
    )

    rapport.to_csv(
        chemin_rapport,
        index=False,
        encoding="utf-8-sig"
    )

    # --------------------------------------------------------
    # 7. BILAN FINAL
    # --------------------------------------------------------

    nombre_valides = int(
        (rapport["STATUT"] == "VALIDE").sum()
    )

    nombre_a_verifier = int(
        (rapport["STATUT"] == "A VERIFIER").sum()
    )

    nombre_erreurs = int(
        (rapport["STATUT"] == "ERREUR").sum()
    )

    print("\n" + "=" * 65)

    print("BILAN DE LA VALIDATION")

    print("=" * 65)

    colonnes_affichage = [

        "FICHIER_SOURCE",

        "LIGNES_ATTENDUES",

        "LIGNES_OBTENUES",

        "VALEURS_DIFFERENTES",

        "STATUT"
    ]

    print(
        rapport[colonnes_affichage].to_string(
            index=False
        )
    )

    print("\nNombre de fichiers contrôlés :", len(rapport))

    print("Fichiers valides :", nombre_valides)

    print("Fichiers à vérifier :", nombre_a_verifier)

    print("Fichiers en erreur :", nombre_erreurs)

    print("\nRapport enregistré :", chemin_rapport)

    if nombre_valides == len(fichiers):

        print("\nVALIDATION APPROFONDIE REUSSIE")

    else:

        print(
            "\nATTENTION : LA VALIDATION GLOBALE "
            "N'EST PAS ENCORE REUSSIE"
        )

    if erreurs:

        print("\nDETAIL DES ERREURS :")

        for erreur in erreurs:

            print(
                erreur["FICHIER_SOURCE"],
                "->",
                erreur["ERREUR"]
            )


# ============================================================
# 8. POINT D'ENTREE DU PROGRAMME
# ============================================================

if __name__ == "__main__":

    main()
