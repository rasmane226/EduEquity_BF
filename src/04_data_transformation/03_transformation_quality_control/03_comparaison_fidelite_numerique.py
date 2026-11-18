
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

RACINE_PROJET = Path(__file__).resolve().parents[3]

DOSSIER_NETTOYE = (
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

DOSSIER_RAPPORTS = (
    RACINE_PROJET
    / "outputs"
    / "tables"
    / "transformation"
)

DOSSIER_RAPPORTS.mkdir(
    parents=True,
    exist_ok=True
)

TOLERANCE_NUMERIQUE = 1e-9


# ============================================================
# 2. CONFIGURATION DES DATASETS
# ============================================================

DATASETS = [

    {
        "nom": "Effectifs régionaux par sexe",
        "source": "effectifs_primaire_region_sexe.csv",
        "transforme": "effectifs_primaire_region_sexe_long.csv",
        "type": "standard",
        "cles": ["REGION", "SEXE", "ANNEE_SCOLAIRE"],
        "valeur_source": ["EFFECTIF"],
        "valeur_transformee": "EFFECTIF",
        "dimensions": ["REGION", "SEXE"]
    },

    {
        "nom": "Effectifs urbains et ruraux",
        "source": "effectifs_primaire_milieu_sexe.csv",
        "transforme": "effectifs_primaire_milieu_sexe_long.csv",
        "type": "milieu",
        "cles": ["MILIEU", "SEXE", "ANNEE_SCOLAIRE"],
        "valeur_source": ["EFFECTIF"],
        "valeur_transformee": "EFFECTIF",
        "dimensions": ["MILIEU", "SEXE"]
    },

    {
        "nom": "Nouveaux inscrits au CP1",
        "source": "nouveaux_inscrits_cp1_region_sexe.csv",
        "transforme": "nouveaux_inscrits_cp1_region_sexe_long.csv",
        "type": "cp1",
        "cles": ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
        "valeur_source": [
            "NOUVEAUX_INSCRITS_CP1",
            "EFFECTIF"
        ],
        "valeur_transformee": "EFFECTIF"
    },

    {
        "nom": "TBA",
        "source": "tba_primaire_region_sexe.csv",
        "transforme": "tba_primaire_region_sexe_long.csv",
        "type": "indicateur_sexe",
        "cles": ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
        "valeur_source": ["TBA"],
        "valeur_transformee": "TBA",
        "dimensions": ["REGION"]
    },

    {
        "nom": "TBS",
        "source": "tbs_primaire_region_sexe.csv",
        "transforme": "tbs_primaire_region_sexe_long.csv",
        "type": "indicateur_sexe",
        "cles": ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
        "valeur_source": ["TBS"],
        "valeur_transformee": "TBS",
        "dimensions": ["REGION"]
    },

    {
        "nom": "TAP",
        "source": "tap_primaire_region_sexe.csv",
        "transforme": "tap_primaire_region_sexe_long.csv",
        "type": "indicateur_sexe",
        "cles": ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
        "valeur_source": ["TAP"],
        "valeur_transformee": "TAP",
        "dimensions": ["REGION"]
    },

    {
        "nom": "Résultats CEP",
        "source": "taux_reussite_cep_region_sexe.csv",
        "transforme": "taux_reussite_cep_region_sexe_long.csv",
        "type": "cep",
        "cles": ["REGION", "SEXE", "ANNEE_CIVILE"],
        "valeur_source": ["TAUX_REUSSITE"],
        "valeur_transformee": "TAUX_REUSSITE"
    },

    {
        "nom": "IPS TBA",
        "source": "ips_tba_primaire_region.csv",
        "transforme": "ips_tba_primaire_region_long.csv",
        "type": "ips",
        "cles": ["REGION", "ANNEE_SCOLAIRE"],
        "valeur_source": ["IPS"],
        "valeur_transformee": "IPS"
    },

    {
        "nom": "IPS TBS",
        "source": "ips_tbs_primaire_region.csv",
        "transforme": "ips_tbs_primaire_region_long.csv",
        "type": "ips",
        "cles": ["REGION", "ANNEE_SCOLAIRE"],
        "valeur_source": ["IPS"],
        "valeur_transformee": "IPS"
    },

    {
        "nom": "IPS TAP",
        "source": "ips_tap_primaire_region.csv",
        "transforme": "ips_tap_primaire_region_long.csv",
        "type": "ips",
        "cles": ["REGION", "ANNEE_SCOLAIRE"],
        "valeur_source": ["IPS"],
        "valeur_transformee": "IPS"
    },

    {
        "nom": "Écoles par statut",
        "source": "ecoles_primaire_region_statut.csv",
        "transforme": "ecoles_primaire_region_statut_long.csv",
        "type": "standard",
        "cles": ["REGION", "STATUT", "ANNEE_SCOLAIRE"],
        "valeur_source": ["NOMBRE_ECOLES"],
        "valeur_transformee": "NOMBRE_ECOLES",
        "dimensions": ["REGION", "STATUT"]
    }
]


# ============================================================
# 3. FONCTIONS GENERALES
# ============================================================

def normaliser_entetes(df):
    """Nettoie les noms des colonnes."""

    df = df.copy()

    df.columns = [
        str(colonne).replace("\ufeff", "").strip().upper()
        for colonne in df.columns
    ]

    return df


def normaliser_texte(serie):
    """Uniformise les valeurs textuelles."""

    resultat = (
        serie.astype("string")
        .str.strip()
        .str.upper()
    )

    return resultat.replace("", pd.NA)


def normaliser_cles(df, colonnes):
    """Uniformise les colonnes utilisées comme clés."""

    df = df.copy()

    for colonne in colonnes:

        if colonne not in df.columns:

            raise ValueError(
                f"Colonne clé absente : {colonne}"
            )

        df[colonne] = normaliser_texte(
            df[colonne]
        )

    return df


def convertir_numerique(serie):
    """Convertit les valeurs en format numérique."""

    return pd.to_numeric(
        serie,
        errors="coerce"
    )


def trouver_colonne(df, candidats, nom_dataset):
    """Retrouve une colonne parmi plusieurs noms possibles."""

    for candidat in candidats:

        if candidat in df.columns:

            return candidat

    raise ValueError(
        f"Aucune colonne numérique reconnue pour "
        f"{nom_dataset}. "
        f"Noms recherchés : {candidats}. "
        f"Colonnes disponibles : {list(df.columns)}"
    )


def construire_ensemble_cles(df, colonnes):

    df_valides = df.dropna(
        subset=colonnes
    )

    return set(
        map(
            tuple,
            df_valides[colonnes].itertuples(
                index=False,
                name=None
            )
        )
    )


def compter_valeurs_infinies(serie):

    valeurs = serie.dropna()

    if valeurs.empty:
        return 0

    return int(
        np.isinf(
            valeurs.to_numpy(dtype=float)
        ).sum()
    )


# ============================================================
# 4. RECONSTRUCTION DES SOURCES AU FORMAT LONG
# ============================================================

def reconstruire_source(dataset, source):

    type_dataset = dataset["type"]

    # --------------------------------------------------------
    # 4.1 EFFECTIFS REGIONAUX ET ECOLES
    # --------------------------------------------------------

    if type_dataset == "standard":

        dimensions = dataset["dimensions"]

        colonnes_absentes = [
            colonne
            for colonne in dimensions
            if colonne not in source.columns
        ]

        if colonnes_absentes:

            raise ValueError(
                f"Dimensions absentes : {colonnes_absentes}"
            )

        source_long = source.melt(
            id_vars=dimensions,
            var_name="ANNEE_SCOLAIRE",
            value_name=dataset["valeur_source"][0]
        )

    # --------------------------------------------------------
    # 4.2 EFFECTIFS URBAINS ET RURAUX
    # --------------------------------------------------------

    elif type_dataset == "milieu":

        source_long = source.melt(
            id_vars=["MILIEU", "SEXE"],
            var_name="ANNEE_SCOLAIRE",
            value_name="EFFECTIF"
        )

        source_long = source_long[
            source_long["MILIEU"].isin(
                ["URBAIN", "RURAL"]
            )
        ].copy()

    # --------------------------------------------------------
    # 4.3 NOUVEAUX INSCRITS AU CP1
    # --------------------------------------------------------

    elif type_dataset == "cp1":

        # Le fichier nettoyé est déjà au format long.
        # Il ne faut pas appliquer melt() une seconde fois.

        source_long = source.copy()

        colonne_source = trouver_colonne(
            source_long,
            dataset["valeur_source"],
            dataset["nom"]
        )

        # Le nom original est conservé pour la comparaison.
        # Aucun renommage prématuré n'est effectué.

        dataset["_colonne_source_detectee"] = colonne_source

    # --------------------------------------------------------
    # 4.4 TBA, TBS ET TAP
    # --------------------------------------------------------

    elif type_dataset == "indicateur_sexe":

        source_long = source.melt(
            id_vars=dataset["dimensions"],
            var_name="ANNEE_SEXE",
            value_name=dataset["valeur_source"][0]
        )

        morceaux = source_long[
            "ANNEE_SEXE"
        ].str.rsplit(
            "_",
            n=1,
            expand=True
        )

        if morceaux.shape[1] != 2:

            raise ValueError(
                f"Format année/sexe incorrect pour "
                f"{dataset['nom']}"
            )

        source_long["ANNEE_SCOLAIRE"] = morceaux[0]
        source_long["SEXE"] = morceaux[1]

        source_long = source_long.drop(
            columns=["ANNEE_SEXE"]
        )

    # --------------------------------------------------------
    # 4.5 RESULTATS CEP
    # --------------------------------------------------------

    elif type_dataset == "cep":

        source_long = source.melt(
            id_vars=["REGION", "SEXE"],
            var_name="ANNEE_CIVILE",
            value_name="TAUX_REUSSITE"
        )

    # --------------------------------------------------------
    # 4.6 INDICES DE PARITE
    # --------------------------------------------------------

    elif type_dataset == "ips":

        source_long = source.melt(
            id_vars=["REGION"],
            var_name="ANNEE_SCOLAIRE",
            value_name="IPS"
        )

    else:

        raise ValueError(
            f"Type de dataset inconnu : {type_dataset}"
        )

    return source_long


# ============================================================
# 5. CONTROLE DES EFFECTIFS NATIONAUX
# ============================================================

def verifier_coherence_nationale(source):

    source = normaliser_entetes(source)

    colonnes_requises = [
        "MILIEU",
        "SEXE"
    ]

    absentes = [
        colonne
        for colonne in colonnes_requises
        if colonne not in source.columns
    ]

    if absentes:

        return {
            "comparaisons_nationales": 0,
            "ecarts_nationaux": 0,
            "statut_national": "A_VERIFIER",
            "detail_national": (
                f"Colonnes absentes : {absentes}"
            )
        }

    source_long = source.melt(
        id_vars=["MILIEU", "SEXE"],
        var_name="ANNEE_SCOLAIRE",
        value_name="EFFECTIF"
    )

    source_long = normaliser_cles(
        source_long,
        ["ANNEE_SCOLAIRE", "SEXE", "MILIEU"]
    )

    source_long["EFFECTIF"] = convertir_numerique(
        source_long["EFFECTIF"]
    )

    doublons = source_long.duplicated(
        subset=["ANNEE_SCOLAIRE", "SEXE", "MILIEU"]
    ).sum()

    if doublons > 0:

        return {
            "comparaisons_nationales": 0,
            "ecarts_nationaux": 0,
            "statut_national": "A_VERIFIER",
            "detail_national": "Doublons dans les clés nationales"
        }

    tableau = source_long.pivot(
        index=["ANNEE_SCOLAIRE", "SEXE"],
        columns="MILIEU",
        values="EFFECTIF"
    ).reset_index()

    colonnes_requises = [
        "URBAIN",
        "RURAL",
        "NATIONAL"
    ]

    if not all(
        colonne in tableau.columns
        for colonne in colonnes_requises
    ):

        return {
            "comparaisons_nationales": 0,
            "ecarts_nationaux": 0,
            "statut_national": "A_VERIFIER",
            "detail_national": "Catégories de milieu incomplètes"
        }

    masque_valide = (
        tableau["URBAIN"].notna()
        & tableau["RURAL"].notna()
        & tableau["NATIONAL"].notna()
    )

    nombre_comparaisons = int(
        masque_valide.sum()
    )

    total_calcule = (
        tableau["URBAIN"]
        + tableau["RURAL"]
    )

    if nombre_comparaisons > 0:

        correspondances = np.isclose(
            total_calcule.loc[masque_valide].to_numpy(dtype=float),
            tableau.loc[
                masque_valide,
                "NATIONAL"
            ].to_numpy(dtype=float),
            rtol=0,
            atol=TOLERANCE_NUMERIQUE
        )

        nombre_ecarts = int(
            (~correspondances).sum()
        )

    else:

        nombre_ecarts = 0

    statut = (
        "VALIDE"
        if nombre_comparaisons == 20
        and nombre_ecarts == 0
        else "A_VERIFIER"
    )

    return {
        "comparaisons_nationales": nombre_comparaisons,
        "ecarts_nationaux": nombre_ecarts,
        "statut_national": statut,
        "detail_national": "Contrôle urbain + rural = national"
    }


# ============================================================
# 6. COMPARAISON D'UN DATASET
# ============================================================

def comparer_dataset(dataset):

    nom = dataset["nom"]

    chemin_source = DOSSIER_NETTOYE / dataset["source"]
    chemin_transformee = DOSSIER_TRANSFORME / dataset["transforme"]

    print("\n" + "=" * 70)
    print(f"DATASET : {nom}")
    print("=" * 70)

    if not chemin_source.exists():

        raise FileNotFoundError(
            f"Fichier source introuvable : {chemin_source}"
        )

    if not chemin_transformee.exists():

        raise FileNotFoundError(
            f"Fichier transformé introuvable : {chemin_transformee}"
        )

    source = pd.read_csv(
        chemin_source,
        encoding="utf-8-sig"
    )

    transforme = pd.read_csv(
        chemin_transformee,
        encoding="utf-8-sig"
    )

    source = normaliser_entetes(source)
    transforme = normaliser_entetes(transforme)

    # --------------------------------------------------------
    # 6.1 RECONSTRUCTION DE LA SOURCE
    # --------------------------------------------------------

    source_long = reconstruire_source(
        dataset,
        source
    )

    cles = dataset["cles"]

    if dataset["type"] == "cp1":

        colonne_source = dataset[
            "_colonne_source_detectee"
        ]

    else:

        colonne_source = trouver_colonne(
            source_long,
            dataset["valeur_source"],
            nom
        )

    colonne_transformee = dataset[
        "valeur_transformee"
    ]

    # --------------------------------------------------------
    # 6.2 VERIFICATION DES COLONNES
    # --------------------------------------------------------

    for colonne in cles + [colonne_source]:

        if colonne not in source_long.columns:

            raise ValueError(
                f"Colonne {colonne} absente de la source "
                f"pour {nom}"
            )

    for colonne in cles + [colonne_transformee]:

        if colonne not in transforme.columns:

            raise ValueError(
                f"Colonne {colonne} absente du fichier transformé "
                f"pour {nom}"
            )

    # --------------------------------------------------------
    # 6.3 NORMALISATION DES CLES
    # --------------------------------------------------------

    source_long = normaliser_cles(
        source_long,
        cles
    )

    transforme = normaliser_cles(
        transforme,
        cles
    )

    # --------------------------------------------------------
    # 6.4 CONVERSION NUMERIQUE
    # --------------------------------------------------------

    source_long[colonne_source] = convertir_numerique(
        source_long[colonne_source]
    )

    transforme[colonne_transformee] = convertir_numerique(
        transforme[colonne_transformee]
    )

    # --------------------------------------------------------
    # 6.5 CONTROLE DES CLES MANQUANTES
    # --------------------------------------------------------

    cles_manquantes_source = int(
        source_long[cles].isna().any(axis=1).sum()
    )

    cles_manquantes_transformees = int(
        transforme[cles].isna().any(axis=1).sum()
    )

    # --------------------------------------------------------
    # 6.6 CONTROLE DES DOUBLONS
    # --------------------------------------------------------

    doublons_source = int(
        source_long.duplicated(subset=cles).sum()
    )

    doublons_transformes = int(
        transforme.duplicated(subset=cles).sum()
    )

    # --------------------------------------------------------
    # 6.7 COMPARAISON DES CLES
    # --------------------------------------------------------

    ensemble_source = construire_ensemble_cles(
        source_long,
        cles
    )

    ensemble_transformee = construire_ensemble_cles(
        transforme,
        cles
    )

    cles_manquantes = ensemble_source - ensemble_transformee
    cles_supplementaires = ensemble_transformee - ensemble_source

    # --------------------------------------------------------
    # 6.8 VALEURS MANQUANTES ET INFINIES
    # --------------------------------------------------------

    valeurs_manquantes_source = int(
        source_long[colonne_source].isna().sum()
    )

    valeurs_manquantes_transformees = int(
        transforme[colonne_transformee].isna().sum()
    )

    valeurs_infinies_source = compter_valeurs_infinies(
        source_long[colonne_source]
    )

    valeurs_infinies_transformees = compter_valeurs_infinies(
        transforme[colonne_transformee]
    )

    # --------------------------------------------------------
    # 6.9 COMPARAISON NUMERIQUE
    # --------------------------------------------------------

    differences_numeriques = 0
    incoherences_valeurs_manquantes = 0
    anomalies = []

    comparaison_possible = (
        cles_manquantes_source == 0
        and cles_manquantes_transformees == 0
        and doublons_source == 0
        and doublons_transformes == 0
        and len(cles_manquantes) == 0
        and len(cles_supplementaires) == 0
        and valeurs_infinies_source == 0
        and valeurs_infinies_transformees == 0
    )

    if comparaison_possible:

        source_comparaison = source_long[
            cles + [colonne_source]
        ].rename(
            columns={
                colonne_source: "VALEUR_SOURCE"
            }
        )

        transforme_comparaison = transforme[
            cles + [colonne_transformee]
        ].rename(
            columns={
                colonne_transformee: "VALEUR_TRANSFORMEE"
            }
        )

        comparaison = source_comparaison.merge(
            transforme_comparaison,
            on=cles,
            how="inner",
            validate="one_to_one"
        )

        valeur_source = comparaison["VALEUR_SOURCE"]
        valeur_transformee = comparaison["VALEUR_TRANSFORMEE"]

        masque_manquant_source = valeur_source.isna()
        masque_manquant_transformee = valeur_transformee.isna()

        incoherences_valeurs_manquantes = int(
            (
                masque_manquant_source
                != masque_manquant_transformee
            ).sum()
        )

        masque_comparable = (
            valeur_source.notna()
            & valeur_transformee.notna()
        )

        masque_differences = pd.Series(
            False,
            index=comparaison.index
        )

        if masque_comparable.any():

            identiques = np.isclose(
                valeur_source.loc[
                    masque_comparable
                ].to_numpy(dtype=float),

                valeur_transformee.loc[
                    masque_comparable
                ].to_numpy(dtype=float),

                rtol=0,
                atol=TOLERANCE_NUMERIQUE
            )

            masque_differences.loc[
                masque_comparable
            ] = ~identiques

        differences_numeriques = int(
            masque_differences.sum()
        )

        # Enregistrement des différences numériques.
        for _, ligne in comparaison.loc[
            masque_differences
        ].iterrows():

            cle = " | ".join(
                str(ligne[colonne])
                for colonne in cles
            )

            anomalies.append({
                "DATASET": nom,
                "TYPE_ANOMALIE": "DIFFERENCE_NUMERIQUE",
                "CLE": cle,
                "VALEUR_SOURCE": ligne["VALEUR_SOURCE"],
                "VALEUR_TRANSFORMEE": ligne["VALEUR_TRANSFORMEE"]
            })

        # Enregistrement des incohérences de valeurs manquantes.
        lignes_manquantes = comparaison.loc[
            masque_manquant_source
            != masque_manquant_transformee
        ]

        for _, ligne in lignes_manquantes.iterrows():

            cle = " | ".join(
                str(ligne[colonne])
                for colonne in cles
            )

            anomalies.append({
                "DATASET": nom,
                "TYPE_ANOMALIE": "INCOHERENCE_VALEUR_MANQUANTE",
                "CLE": cle,
                "VALEUR_SOURCE": ligne["VALEUR_SOURCE"],
                "VALEUR_TRANSFORMEE": ligne["VALEUR_TRANSFORMEE"]
            })

    # --------------------------------------------------------
    # 6.10 CONTROLE NATIONAL URBAIN-RURAL
    # --------------------------------------------------------

    comparaisons_nationales = 0
    ecarts_nationaux = 0
    statut_national = "NON_APPLICABLE"
    detail_national = ""

    if dataset["type"] == "milieu":

        controle_national = verifier_coherence_nationale(
            source
        )

        comparaisons_nationales = (
            controle_national["comparaisons_nationales"]
        )

        ecarts_nationaux = (
            controle_national["ecarts_nationaux"]
        )

        statut_national = (
            controle_national["statut_national"]
        )

        detail_national = (
            controle_national["detail_national"]
        )

    # --------------------------------------------------------
    # 6.11 ENREGISTREMENT DES CLES ANORMALES
    # --------------------------------------------------------

    for cle in sorted(cles_manquantes):

        anomalies.append({
            "DATASET": nom,
            "TYPE_ANOMALIE": "CLE_MANQUANTE",
            "CLE": " | ".join(map(str, cle)),
            "VALEUR_SOURCE": None,
            "VALEUR_TRANSFORMEE": None
        })

    for cle in sorted(cles_supplementaires):

        anomalies.append({
            "DATASET": nom,
            "TYPE_ANOMALIE": "CLE_SUPPLEMENTAIRE",
            "CLE": " | ".join(map(str, cle)),
            "VALEUR_SOURCE": None,
            "VALEUR_TRANSFORMEE": None
        })

    # --------------------------------------------------------
    # 6.12 DETERMINATION DU STATUT
    # --------------------------------------------------------

    statut = "VALIDE"

    anomalies_detectees = (
        cles_manquantes_source > 0
        or cles_manquantes_transformees > 0
        or doublons_source > 0
        or doublons_transformes > 0
        or len(cles_manquantes) > 0
        or len(cles_supplementaires) > 0
        or valeurs_manquantes_source > 0
        or valeurs_manquantes_transformees > 0
        or valeurs_infinies_source > 0
        or valeurs_infinies_transformees > 0
        or differences_numeriques > 0
        or incoherences_valeurs_manquantes > 0
        or statut_national == "A_VERIFIER"
    )

    if anomalies_detectees or not comparaison_possible:

        statut = "A_VERIFIER"

    # --------------------------------------------------------
    # 6.13 AFFICHAGE DES RESULTATS
    # --------------------------------------------------------

    print(f"Lignes source reconstruites : {len(source_long)}")
    print(f"Lignes transformées : {len(transforme)}")

    print(f"Colonne numérique source : {colonne_source}")
    print(f"Colonne numérique transformée : {colonne_transformee}")

    print(f"Clés manquantes dans la source : {cles_manquantes_source}")
    print(f"Clés manquantes dans le transformé : {cles_manquantes_transformees}")

    print(f"Doublons source : {doublons_source}")
    print(f"Doublons transformés : {doublons_transformes}")

    print(f"Clés manquantes : {len(cles_manquantes)}")
    print(f"Clés supplémentaires : {len(cles_supplementaires)}")

    print(f"Valeurs manquantes source : {valeurs_manquantes_source}")
    print(f"Valeurs manquantes transformées : {valeurs_manquantes_transformees}")

    print(f"Valeurs infinies source : {valeurs_infinies_source}")
    print(f"Valeurs infinies transformées : {valeurs_infinies_transformees}")

    print(f"Différences numériques : {differences_numeriques}")
    print(f"Incohérences de valeurs manquantes : {incoherences_valeurs_manquantes}")

    if dataset["type"] == "milieu":

        print(f"Comparaisons nationales : {comparaisons_nationales}")
        print(f"Écarts nationaux : {ecarts_nationaux}")
        print(f"Contrôle national : {statut_national}")

    print(f"STATUT : {statut}")

    # --------------------------------------------------------
    # 6.14 RAPPORT DU DATASET
    # --------------------------------------------------------

    rapport = {

        "DATASET": nom,

        "COLONNE_SOURCE": colonne_source,

        "COLONNE_TRANSFORMEE": colonne_transformee,

        "LIGNES_SOURCE": len(source_long),

        "LIGNES_TRANSFORMEES": len(transforme),

        "CLES_MANQUANTES_SOURCE": cles_manquantes_source,

        "CLES_MANQUANTES_TRANSFORMEES": cles_manquantes_transformees,

        "DOUBLONS_SOURCE": doublons_source,

        "DOUBLONS_TRANSFORMES": doublons_transformes,

        "CLES_MANQUANTES": len(cles_manquantes),

        "CLES_SUPPLEMENTAIRES": len(cles_supplementaires),

        "VALEURS_MANQUANTES_SOURCE": valeurs_manquantes_source,

        "VALEURS_MANQUANTES_TRANSFORMEES": valeurs_manquantes_transformees,

        "VALEURS_INFINIES_SOURCE": valeurs_infinies_source,

        "VALEURS_INFINIES_TRANSFORMEES": valeurs_infinies_transformees,

        "DIFFERENCES_NUMERIQUES": differences_numeriques,

        "INCOHERENCES_VALEURS_MANQUANTES": incoherences_valeurs_manquantes,

        "COMPARAISONS_NATIONALES": comparaisons_nationales,

        "ECARTS_NATIONAUX": ecarts_nationaux,

        "STATUT_CONTROLE_NATIONAL": statut_national,

        "DETAIL_CONTROLE_NATIONAL": detail_national,

        "STATUT": statut
    }

    return rapport, anomalies


# ============================================================
# 7. EXECUTION GLOBALE
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("COMPARAISON DE FIDELITE NUMERIQUE")
    print("=" * 70)

    rapports = []
    toutes_anomalies = []

    for dataset in DATASETS:

        # Évite de conserver une ancienne valeur détectée
        # si le script est relancé dans le même environnement.
        dataset.pop("_colonne_source_detectee", None)

        try:

            rapport, anomalies = comparer_dataset(
                dataset
            )

            rapports.append(rapport)
            toutes_anomalies.extend(anomalies)

        except Exception as erreur:

            print("\n" + "=" * 70)
            print(f"ERREUR : {dataset['nom']}")
            print(str(erreur))
            print("=" * 70)

            rapports.append({

                "DATASET": dataset["nom"],

                "STATUT": "ERREUR",

                "DETAIL_ERREUR": str(erreur)
            })

            toutes_anomalies.append({

                "DATASET": dataset["nom"],

                "TYPE_ANOMALIE": "ERREUR_EXECUTION",

                "CLE": "",

                "VALEUR_SOURCE": None,

                "VALEUR_TRANSFORMEE": None
            })

    # --------------------------------------------------------
    # 7.1 RAPPORT GLOBAL
    # --------------------------------------------------------

    df_rapport = pd.DataFrame(rapports)

    chemin_rapport = (
        DOSSIER_RAPPORTS
        / "rapport_fidelite_numerique.csv"
    )

    df_rapport.to_csv(
        chemin_rapport,
        index=False,
        encoding="utf-8-sig"
    )

    # --------------------------------------------------------
    # 7.2 RAPPORT DES ANOMALIES
    # --------------------------------------------------------

    df_anomalies = pd.DataFrame(
        toutes_anomalies,
        columns=[
            "DATASET",
            "TYPE_ANOMALIE",
            "CLE",
            "VALEUR_SOURCE",
            "VALEUR_TRANSFORMEE"
        ]
    )

    chemin_anomalies = (
        DOSSIER_RAPPORTS
        / "details_anomalies_fidelite.csv"
    )

    df_anomalies.to_csv(
        chemin_anomalies,
        index=False,
        encoding="utf-8-sig"
    )

    # --------------------------------------------------------
    # 7.3 BILAN GLOBAL
    # --------------------------------------------------------

    nombre_valides = int(
        (df_rapport["STATUT"] == "VALIDE").sum()
    )

    nombre_a_verifier = int(
        (df_rapport["STATUT"] == "A_VERIFIER").sum()
    )

    nombre_erreurs = int(
        (df_rapport["STATUT"] == "ERREUR").sum()
    )

    statut_global = (
        "VALIDE"
        if (
            nombre_valides == len(DATASETS)
            and nombre_a_verifier == 0
            and nombre_erreurs == 0
        )
        else "A_VERIFIER"
    )

    # --------------------------------------------------------
    # 7.4 AFFICHAGE FINAL
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("RAPPORT DETAILLE")
    print("=" * 70)

    print(
        df_rapport.to_string(
            index=False
        )
    )

    print("\n" + "=" * 70)
    print("BILAN GLOBAL")
    print("=" * 70)

    print(f"Datasets examinés : {len(DATASETS)}")

    print(
        f"Datasets validés : "
        f"{nombre_valides}/{len(DATASETS)}"
    )

    print(
        f"Datasets à vérifier : "
        f"{nombre_a_verifier}/{len(DATASETS)}"
    )

    print(
        f"Erreurs d'exécution : "
        f"{nombre_erreurs}/{len(DATASETS)}"
    )

    print(
        f"Anomalies détaillées : "
        f"{len(df_anomalies)}"
    )

    print(f"\nSTATUT GLOBAL : {statut_global}")

    print("\n" + "=" * 70)
    print("RAPPORTS GENERES")
    print("=" * 70)

    print(f"Rapport global : {chemin_rapport}")
    print(f"Rapport anomalies : {chemin_anomalies}")

    print("\n" + "=" * 70)


# ============================================================
# 8. POINT D'ENTREE
# ============================================================

if __name__ == "__main__":

    main()
