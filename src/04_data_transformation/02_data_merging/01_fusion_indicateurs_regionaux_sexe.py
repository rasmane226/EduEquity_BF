
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
# 2. DEFINITION DES CLES ET PARAMETRES
# ============================================================

CLES_FUSION = [
    "REGION",
    "ANNEE_SCOLAIRE",
    "SEXE"
]

CATEGORIES_SEXE = [
    "GARCONS",
    "FILLES"
]

NOMBRE_REGIONS_ATTENDU = 13
NOMBRE_ANNEES_ATTENDU = 10
NOMBRE_LIGNES_ATTENDU = 260

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
# 3. FONCTION DE LECTURE DES DONNEES
# ============================================================

def lire_donnees(nom_fichier):

    chemin = DOSSIER_SOURCE / nom_fichier

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
            f"Le fichier {nom_fichier} est vide."
        )

    print(
        f"\nChargement : {nom_fichier}"
        f" | {len(df)} lignes"
    )

    return df


# ============================================================
# 4. PREPARATION ET CONTROLE DES FICHIERS
# ============================================================

def preparer_fichier(df, nom_fichier, colonne_valeur):

    colonnes_requises = CLES_FUSION + [colonne_valeur]

    colonnes_absentes = [
        col for col in colonnes_requises
        if col not in df.columns
    ]

    if colonnes_absentes:
        raise ValueError(
            f"{nom_fichier} : colonnes absentes : "
            f"{colonnes_absentes}"
        )

    df = df[colonnes_requises].copy()

    # Harmonisation des clés
    for colonne in CLES_FUSION:

        df[colonne] = (
            df[colonne]
            .astype("string")
            .str.strip()
            .str.upper()
        )

    # Vérification des clés manquantes
    if df[CLES_FUSION].isna().any().any():
        raise ValueError(
            f"{nom_fichier} contient des clés manquantes."
        )

    # Vérification des clés vides
    if (df[CLES_FUSION] == "").any().any():
        raise ValueError(
            f"{nom_fichier} contient des clés vides."
        )

    # Conversion de la variable numérique
    df[colonne_valeur] = pd.to_numeric(
        df[colonne_valeur],
        errors="raise"
    )

    # Vérification des valeurs manquantes
    if df[colonne_valeur].isna().any():
        raise ValueError(
            f"{nom_fichier} contient des valeurs manquantes "
            f"dans {colonne_valeur}."
        )

    # Vérification des valeurs infinies
    if np.isinf(df[colonne_valeur]).any():
        raise ValueError(
            f"{nom_fichier} contient des valeurs infinies."
        )

    # Vérification des valeurs négatives
    if (df[colonne_valeur] < 0).any():
        raise ValueError(
            f"{nom_fichier} contient des valeurs négatives."
        )

    # Vérification des catégories de sexe
    categories = set(df["SEXE"].unique())

    if categories != set(CATEGORIES_SEXE):
        raise ValueError(
            f"{nom_fichier} : catégories de sexe inattendues. "
            f"Catégories trouvées : {categories}"
        )

    # Vérification des doublons sur les clés
    doublons = int(
        df.duplicated(subset=CLES_FUSION).sum()
    )

    if doublons > 0:
        raise ValueError(
            f"{nom_fichier} contient {doublons} doublons "
            f"sur les clés de fusion."
        )

    print(
        f"Préparation validée : {nom_fichier}"
    )

    return df


# ============================================================
# 5. VERIFICATION DE LA COMPATIBILITE DES CLES
# ============================================================

def verifier_compatibilite(
    df_reference,
    df_comparaison,
    nom_comparaison
):

    cles_reference = (
        df_reference[CLES_FUSION]
        .drop_duplicates()
    )

    cles_comparaison = (
        df_comparaison[CLES_FUSION]
        .drop_duplicates()
    )

    comparaison = cles_reference.merge(
        cles_comparaison,
        on=CLES_FUSION,
        how="outer",
        indicator=True
    )

    cles_manquantes = int(
        (comparaison["_merge"] == "left_only").sum()
    )

    cles_supplementaires = int(
        (comparaison["_merge"] == "right_only").sum()
    )

    print(
        f"\nCompatibilité avec {nom_comparaison} :"
    )

    print(
        "Clés de référence :",
        len(cles_reference)
    )

    print(
        "Clés comparées :",
        len(cles_comparaison)
    )

    print(
        "Clés manquantes :",
        cles_manquantes
    )

    print(
        "Clés supplémentaires :",
        cles_supplementaires
    )

    statut = (
        "VALIDE"
        if cles_manquantes == 0
        and cles_supplementaires == 0
        else "A VERIFIER"
    )

    rapport = {
        "FICHIER_COMPARE": nom_comparaison,
        "CLES_REFERENCE": len(cles_reference),
        "CLES_COMPARAISON": len(cles_comparaison),
        "CLES_MANQUANTES": cles_manquantes,
        "CLES_SUPPLEMENTAIRES": cles_supplementaires,
        "STATUT": statut
    }

    if statut != "VALIDE":
        raise ValueError(
            f"Incompatibilité des clés avec "
            f"{nom_comparaison}. Fusion interrompue."
        )

    return rapport


# ============================================================
# 6. VERIFICATION DE LA STRUCTURE DES ANNEES
# ============================================================

def verifier_annees(df, nom_fichier):

    annees = set(
        df["ANNEE_SCOLAIRE"].dropna().unique()
    )

    annees_attendues = set(ANNEES_ATTENDUES)

    if annees != annees_attendues:
        raise ValueError(
            f"{nom_fichier} : les années scolaires "
            f"ne correspondent pas aux années attendues.\n"
            f"Années trouvées : {sorted(annees)}"
        )


# ============================================================
# 7. CHARGEMENT ET PREPARATION DES CINQ FICHIERS
# ============================================================

def main():

    print("=" * 70)
    print("FUSION DES INDICATEURS REGIONAUX PAR SEXE")
    print("=" * 70)

    rapports = []

    # --------------------------------------------------------
    # A. EFFECTIFS DU PRIMAIRE
    # --------------------------------------------------------

    effectifs = lire_donnees(
        "effectifs_primaire_region_sexe_long.csv"
    )

    effectifs = preparer_fichier(
        effectifs,
        "effectifs_primaire_region_sexe_long.csv",
        "EFFECTIF"
    )

    # --------------------------------------------------------
    # B. TAUX BRUT D'ADMISSION
    # --------------------------------------------------------

    tba = lire_donnees(
        "tba_primaire_region_sexe_long.csv"
    )

    # Exclusion de TOTAL pour conserver les deux sexes
    tba = tba[
        tba["SEXE"].isin(CATEGORIES_SEXE)
    ].copy()

    tba = preparer_fichier(
        tba,
        "tba_primaire_region_sexe_long.csv",
        "TBA"
    )

    # --------------------------------------------------------
    # C. TAUX BRUT DE SCOLARISATION
    # --------------------------------------------------------

    tbs = lire_donnees(
        "tbs_primaire_region_sexe_long.csv"
    )

    tbs = tbs[
        tbs["SEXE"].isin(CATEGORIES_SEXE)
    ].copy()

    tbs = preparer_fichier(
        tbs,
        "tbs_primaire_region_sexe_long.csv",
        "TBS"
    )

    # --------------------------------------------------------
    # D. TAUX D'ACHEVEMENT DU PRIMAIRE
    # --------------------------------------------------------

    tap = lire_donnees(
        "tap_primaire_region_sexe_long.csv"
    )

    tap = tap[
        tap["SEXE"].isin(CATEGORIES_SEXE)
    ].copy()

    tap = preparer_fichier(
        tap,
        "tap_primaire_region_sexe_long.csv",
        "TAP"
    )

    # --------------------------------------------------------
    # E. NOUVEAUX INSCRITS AU CP1
    # --------------------------------------------------------

    cp1 = lire_donnees(
        "nouveaux_inscrits_cp1_region_sexe_long.csv"
    )

    # IMPORTANT :
    # La colonne numérique du fichier CP1 s'appelle EFFECTIF.
    cp1 = preparer_fichier(
        cp1,
        "nouveaux_inscrits_cp1_region_sexe_long.csv",
        "EFFECTIF"
    )

    # Renommer pour distinguer les nouveaux inscrits
    # de l'effectif total du primaire.
    cp1 = cp1.rename(
        columns={
            "EFFECTIF": "NOUVEAUX_INSCRITS_CP1"
        }
    )

    # --------------------------------------------------------
    # F. CONTROLES INDIVIDUELS DES CINQ FICHIERS
    # --------------------------------------------------------

    fichiers = {
        "EFFECTIFS": effectifs,
        "TBA": tba,
        "TBS": tbs,
        "TAP": tap,
        "NOUVEAUX_INSCRITS_CP1": cp1
    }

    print("\n" + "=" * 70)
    print("CONTROLES INDIVIDUELS DES FICHIERS")
    print("=" * 70)

    for nom, df in fichiers.items():

        if len(df) != NOMBRE_LIGNES_ATTENDU:
            raise ValueError(
                f"{nom} : {len(df)} observations trouvées, "
                f"{NOMBRE_LIGNES_ATTENDU} attendues."
            )

        if df["REGION"].nunique() != NOMBRE_REGIONS_ATTENDU:
            raise ValueError(
                f"{nom} : nombre de régions incorrect."
            )

        if df["SEXE"].nunique() != len(CATEGORIES_SEXE):
            raise ValueError(
                f"{nom} : nombre de catégories de sexe incorrect."
            )

        verifier_annees(df, nom)

        print(
            f"{nom} : VALIDE | "
            f"{len(df)} observations | "
            f"{df['REGION'].nunique()} régions | "
            f"{df['ANNEE_SCOLAIRE'].nunique()} années"
        )

    # --------------------------------------------------------
    # G. VERIFICATION DE LA COMPATIBILITE DES CLES
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("VERIFICATION DE LA COMPATIBILITE DES CLES")
    print("=" * 70)

    rapports.append(
        verifier_compatibilite(
            effectifs,
            tba,
            "TBA"
        )
    )

    rapports.append(
        verifier_compatibilite(
            effectifs,
            tbs,
            "TBS"
        )
    )

    rapports.append(
        verifier_compatibilite(
            effectifs,
            tap,
            "TAP"
        )
    )

    rapports.append(
        verifier_compatibilite(
            effectifs,
            cp1,
            "NOUVEAUX_INSCRITS_CP1"
        )
    )

    # --------------------------------------------------------
    # H. FUSION DES CINQ JEUX DE DONNEES
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FUSION DES CINQ JEUX DE DONNEES")
    print("=" * 70)

    donnees_fusionnees = effectifs.merge(
        tba,
        on=CLES_FUSION,
        how="inner",
        validate="one_to_one"
    )

    donnees_fusionnees = donnees_fusionnees.merge(
        tbs,
        on=CLES_FUSION,
        how="inner",
        validate="one_to_one"
    )

    donnees_fusionnees = donnees_fusionnees.merge(
        tap,
        on=CLES_FUSION,
        how="inner",
        validate="one_to_one"
    )

    donnees_fusionnees = donnees_fusionnees.merge(
        cp1,
        on=CLES_FUSION,
        how="inner",
        validate="one_to_one"
    )

    # --------------------------------------------------------
    # I. CONTROLE DE LA TABLE FUSIONNEE
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("CONTROLE DE LA TABLE FUSIONNEE")
    print("=" * 70)

    doublons_finaux = int(
        donnees_fusionnees.duplicated(
            subset=CLES_FUSION
        ).sum()
    )

    valeurs_manquantes = int(
        donnees_fusionnees.isna().sum().sum()
    )

    colonnes_numeriques = (
        donnees_fusionnees.select_dtypes(
            include=[np.number]
        )
    )

    valeurs_infinies = int(
        np.isinf(colonnes_numeriques).sum().sum()
    )

    nombre_lignes_obtenu = len(donnees_fusionnees)

    regions = donnees_fusionnees["REGION"].nunique()

    annees = donnees_fusionnees["ANNEE_SCOLAIRE"].nunique()

    sexes = donnees_fusionnees["SEXE"].nunique()

    print(
        "Nombre de lignes attendu :",
        NOMBRE_LIGNES_ATTENDU
    )

    print(
        "Nombre de lignes obtenu :",
        nombre_lignes_obtenu
    )

    print("Nombre de régions :", regions)

    print("Nombre d'années scolaires :", annees)

    print("Nombre de catégories de sexe :", sexes)

    print("Doublons finaux :", doublons_finaux)

    print("Valeurs manquantes :", valeurs_manquantes)

    print("Valeurs infinies :", valeurs_infinies)

    # --------------------------------------------------------
    # J. VERIFICATION DU STATUT FINAL
    # --------------------------------------------------------

    fusion_valide = (
        nombre_lignes_obtenu == NOMBRE_LIGNES_ATTENDU
        and regions == NOMBRE_REGIONS_ATTENDU
        and annees == NOMBRE_ANNEES_ATTENDU
        and sexes == len(CATEGORIES_SEXE)
        and doublons_finaux == 0
        and valeurs_manquantes == 0
        and valeurs_infinies == 0
    )

    statut_final = (
        "VALIDE"
        if fusion_valide
        else "A VERIFIER"
    )

    print("\nSTATUT FINAL :", statut_final)

    if not fusion_valide:
        raise ValueError(
            "La fusion ne satisfait pas les contrôles finaux. "
            "Le fichier ne sera pas enregistré."
        )

    # --------------------------------------------------------
    # K. ORGANISATION DES COLONNES
    # --------------------------------------------------------

    donnees_fusionnees = donnees_fusionnees[
        [
            "REGION",
            "ANNEE_SCOLAIRE",
            "SEXE",
            "EFFECTIF",
            "NOUVEAUX_INSCRITS_CP1",
            "TBA",
            "TBS",
            "TAP"
        ]
    ]

    donnees_fusionnees = donnees_fusionnees.sort_values(
        by=[
            "REGION",
            "ANNEE_SCOLAIRE",
            "SEXE"
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # L. ENREGISTREMENT DE LA TABLE FUSIONNEE
    # --------------------------------------------------------

    chemin_sortie = (
        DOSSIER_SORTIE
        / "indicateurs_regionaux_sexe.csv"
    )

    donnees_fusionnees.to_csv(
        chemin_sortie,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nFichier fusionné enregistré :")
    print(chemin_sortie)

    # --------------------------------------------------------
    # M. ENREGISTREMENT DU RAPPORT DE COMPATIBILITE
    # --------------------------------------------------------

    rapport_compatibilite = pd.DataFrame(rapports)

    chemin_rapport = (
        DOSSIER_RAPPORT
        / "rapport_fusion_regionale_sexe.csv"
    )

    rapport_compatibilite.to_csv(
        chemin_rapport,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nRapport de compatibilité enregistré :")
    print(chemin_rapport)

    # --------------------------------------------------------
    # N. APERCU DE LA TABLE FUSIONNEE
    # --------------------------------------------------------

    print("\nAperçu des données fusionnées :")

    print(
        donnees_fusionnees.head(10).to_string(index=False)
    )

    print("\nDimensions finales :")
    print(donnees_fusionnees.shape)

    print("\nColonnes finales :")
    print(list(donnees_fusionnees.columns))

    print("\n" + "=" * 70)
    print("FUSION TERMINEE AVEC SUCCES")
    print("=" * 70)


# ============================================================
# 8. POINT D'ENTREE
# ============================================================

if __name__ == "__main__":
    main()
