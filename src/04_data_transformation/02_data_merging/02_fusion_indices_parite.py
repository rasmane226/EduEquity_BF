
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
    "ANNEE_SCOLAIRE"
]

NOMBRE_REGIONS_ATTENDU = 13
NOMBRE_ANNEES_ATTENDU = 10
NOMBRE_LIGNES_ATTENDU = 130

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
# 3. FONCTION DE LECTURE
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

def preparer_fichier(df, nom_fichier, nouvelle_colonne):

    colonnes_requises = CLES_FUSION + ["IPS"]

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

    if (df[CLES_FUSION] == "").any().any():
        raise ValueError(
            f"{nom_fichier} contient des clés vides."
        )

    # Conversion numérique
    df["IPS"] = pd.to_numeric(
        df["IPS"],
        errors="raise"
    )

    # Vérification des valeurs manquantes
    if df["IPS"].isna().any():
        raise ValueError(
            f"{nom_fichier} contient des valeurs IPS manquantes."
        )

    # Vérification des valeurs infinies
    if np.isinf(df["IPS"]).any():
        raise ValueError(
            f"{nom_fichier} contient des valeurs IPS infinies."
        )

    # Vérification des valeurs négatives
    if (df["IPS"] < 0).any():
        raise ValueError(
            f"{nom_fichier} contient des valeurs IPS négatives."
        )

    # Vérification des doublons
    doublons = int(
        df.duplicated(
            subset=CLES_FUSION
        ).sum()
    )

    if doublons > 0:
        raise ValueError(
            f"{nom_fichier} contient {doublons} doublons."
        )

    # Renommer la colonne IPS
    df = df.rename(
        columns={
            "IPS": nouvelle_colonne
        }
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

    statut = (
        "VALIDE"
        if cles_manquantes == 0
        and cles_supplementaires == 0
        else "A VERIFIER"
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

    print("Statut :", statut)

    return {
        "FICHIER_COMPARE": nom_comparaison,
        "CLES_REFERENCE": len(cles_reference),
        "CLES_COMPARAISON": len(cles_comparaison),
        "CLES_MANQUANTES": cles_manquantes,
        "CLES_SUPPLEMENTAIRES": cles_supplementaires,
        "STATUT": statut
    }


# ============================================================
# 6. VERIFICATION DES ANNEES
# ============================================================

def verifier_annees(df, nom_fichier):

    annees = set(
        df["ANNEE_SCOLAIRE"].unique()
    )

    annees_attendues = set(
        ANNEES_ATTENDUES
    )

    if annees != annees_attendues:
        raise ValueError(
            f"{nom_fichier} : années scolaires incorrectes.\n"
            f"Années trouvées : {sorted(annees)}"
        )


# ============================================================
# 7. FONCTION PRINCIPALE
# ============================================================

def main():

    print("=" * 70)
    print("FUSION DES INDICES DE PARITE SCOLAIRE")
    print("=" * 70)

    rapports = []

    # --------------------------------------------------------
    # A. IPS TBA
    # --------------------------------------------------------

    ips_tba = lire_donnees(
        "ips_tba_primaire_region_long.csv"
    )

    ips_tba = preparer_fichier(
        ips_tba,
        "ips_tba_primaire_region_long.csv",
        "IPS_TBA"
    )

    # --------------------------------------------------------
    # B. IPS TBS
    # --------------------------------------------------------

    ips_tbs = lire_donnees(
        "ips_tbs_primaire_region_long.csv"
    )

    ips_tbs = preparer_fichier(
        ips_tbs,
        "ips_tbs_primaire_region_long.csv",
        "IPS_TBS"
    )

    # --------------------------------------------------------
    # C. IPS TAP
    # --------------------------------------------------------

    ips_tap = lire_donnees(
        "ips_tap_primaire_region_long.csv"
    )

    ips_tap = preparer_fichier(
        ips_tap,
        "ips_tap_primaire_region_long.csv",
        "IPS_TAP"
    )

    fichiers = {
        "IPS_TBA": ips_tba,
        "IPS_TBS": ips_tbs,
        "IPS_TAP": ips_tap
    }

    # --------------------------------------------------------
    # D. CONTROLES INDIVIDUELS
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("CONTROLES INDIVIDUELS DES FICHIERS")
    print("=" * 70)

    for nom, df in fichiers.items():

        if len(df) != NOMBRE_LIGNES_ATTENDU:
            raise ValueError(
                f"{nom} : {len(df)} lignes trouvées, "
                f"{NOMBRE_LIGNES_ATTENDU} attendues."
            )

        nombre_regions = df["REGION"].nunique()

        if nombre_regions != NOMBRE_REGIONS_ATTENDU:
            raise ValueError(
                f"{nom} : nombre de régions incorrect."
            )

        verifier_annees(df, nom)

        print(
            f"{nom} : VALIDE | "
            f"{len(df)} observations | "
            f"{nombre_regions} régions | "
            f"{df['ANNEE_SCOLAIRE'].nunique()} années"
        )

    # --------------------------------------------------------
    # E. VERIFICATION DE LA COMPATIBILITE
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("VERIFICATION DES CLES DE FUSION")
    print("=" * 70)

    rapports.append(
        verifier_compatibilite(
            ips_tba,
            ips_tbs,
            "IPS_TBS"
        )
    )

    rapports.append(
        verifier_compatibilite(
            ips_tba,
            ips_tap,
            "IPS_TAP"
        )
    )

    if any(
        rapport["STATUT"] != "VALIDE"
        for rapport in rapports
    ):
        raise ValueError(
            "Les clés ne sont pas compatibles. "
            "Fusion interrompue."
        )

    # --------------------------------------------------------
    # F. FUSION DES TROIS INDICES
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FUSION DES TROIS INDICES")
    print("=" * 70)

    donnees_fusionnees = ips_tba.merge(
        ips_tbs,
        on=CLES_FUSION,
        how="inner",
        validate="one_to_one"
    )

    donnees_fusionnees = donnees_fusionnees.merge(
        ips_tap,
        on=CLES_FUSION,
        how="inner",
        validate="one_to_one"
    )

    # --------------------------------------------------------
    # G. CONTROLES DE LA TABLE FUSIONNEE
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("CONTROLE DE LA TABLE FUSIONNEE")
    print("=" * 70)

    nombre_lignes_obtenu = len(
        donnees_fusionnees
    )

    nombre_regions = (
        donnees_fusionnees["REGION"].nunique()
    )

    nombre_annees = (
        donnees_fusionnees["ANNEE_SCOLAIRE"].nunique()
    )

    doublons = int(
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

    print(
        "Nombre de lignes attendu :",
        NOMBRE_LIGNES_ATTENDU
    )

    print(
        "Nombre de lignes obtenu :",
        nombre_lignes_obtenu
    )

    print(
        "Nombre de régions :",
        nombre_regions
    )

    print(
        "Nombre d'années scolaires :",
        nombre_annees
    )

    print(
        "Doublons :",
        doublons
    )

    print(
        "Valeurs manquantes :",
        valeurs_manquantes
    )

    print(
        "Valeurs infinies :",
        valeurs_infinies
    )

    # --------------------------------------------------------
    # H. VALIDATION FINALE
    # --------------------------------------------------------

    fusion_valide = (
        nombre_lignes_obtenu == NOMBRE_LIGNES_ATTENDU
        and nombre_regions == NOMBRE_REGIONS_ATTENDU
        and nombre_annees == NOMBRE_ANNEES_ATTENDU
        and doublons == 0
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
            "La fusion ne satisfait pas les contrôles. "
            "Aucun fichier final ne sera enregistré."
        )

    # --------------------------------------------------------
    # I. ORGANISATION DES COLONNES
    # --------------------------------------------------------

    donnees_fusionnees = donnees_fusionnees[
        [
            "REGION",
            "ANNEE_SCOLAIRE",
            "IPS_TBA",
            "IPS_TBS",
            "IPS_TAP"
        ]
    ]

    donnees_fusionnees = donnees_fusionnees.sort_values(
        by=[
            "REGION",
            "ANNEE_SCOLAIRE"
        ]
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # J. ENREGISTREMENT DU FICHIER
    # --------------------------------------------------------

    chemin_sortie = (
        DOSSIER_SORTIE
        / "indices_parite_regionaux.csv"
    )

    donnees_fusionnees.to_csv(
        chemin_sortie,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nFichier fusionné enregistré :")
    print(chemin_sortie)

    # --------------------------------------------------------
    # K. ENREGISTREMENT DU RAPPORT
    # --------------------------------------------------------

    rapport = pd.DataFrame(rapports)

    chemin_rapport = (
        DOSSIER_RAPPORT
        / "rapport_fusion_indices_parite.csv"
    )

    rapport.to_csv(
        chemin_rapport,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nRapport de compatibilité enregistré :")
    print(chemin_rapport)

    # --------------------------------------------------------
    # L. APERCU FINAL
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
    print("FUSION DES INDICES TERMINEE AVEC SUCCES")
    print("=" * 70)


# ============================================================
# 8. POINT D'ENTREE
# ============================================================

if __name__ == "__main__":
    main()
