
from pathlib import Path
from itertools import product

import numpy as np
import pandas as pd


# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

RACINE_PROJET = Path(__file__).resolve().parents[3]

DOSSIER_INDIVIDUEL = (
    RACINE_PROJET
    / "data"
    / "04_transformed_data"
    / "transformed_sheets"
)

DOSSIER_FUSIONNE = (
    RACINE_PROJET
    / "data"
    / "04_transformed_data"
    / "merged"
)

DOSSIER_FINAL = (
    RACINE_PROJET
    / "data"
    / "04_transformed_data"
    / "final"
)

DOSSIER_RAPPORT = (
    RACINE_PROJET
    / "outputs"
    / "tables"
    / "transformation"
)


# ============================================================
# 2. PARAMETRES GENERAUX DE VALIDATION
# ============================================================

ANNEES_SCOLAIRES = {
    f"{annee}-{annee + 1}"
    for annee in range(2015, 2025)
}

ANNEES_CIVILES = {
    str(annee)
    for annee in range(2016, 2026)
}

SEXES = {"FILLES", "GARCONS"}

CATEGORIES_SEXE_AUTORISEES = SEXES | {"TOTAL"}

STATUTS_ATTENDUS = {"PUBLIC", "PRIVÉ"}

MILIEUX_ATTENDUS = {"URBAIN", "RURAL"}

REGIONS_ATTENDUES = 13


# ============================================================
# 3. DEFINITION DES FICHIERS INDIVIDUELS
# ============================================================

fichiers_individuels = {

    "Effectifs régionaux par sexe": {
        "chemin": (
            DOSSIER_INDIVIDUEL
            / "effectifs_primaire_region_sexe_long.csv"
        ),
        "cles": ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
        "lignes": 260,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES,
            "SEXE": SEXES
        }
    },

    "Nouveaux inscrits au CP1": {
        "chemin": (
            DOSSIER_INDIVIDUEL
            / "nouveaux_inscrits_cp1_region_sexe_long.csv"
        ),
        "cles": ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
        "lignes": 260,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES,
            "SEXE": SEXES
        }
    },

    "Effectifs urbains et ruraux": {
        "chemin": (
            DOSSIER_INDIVIDUEL
            / "effectifs_primaire_milieu_sexe_long.csv"
        ),
        "cles": ["MILIEU", "ANNEE_SCOLAIRE", "SEXE"],
        "lignes": 40,
        "domaines": {
            "MILIEU": MILIEUX_ATTENDUS,
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES,
            "SEXE": SEXES
        }
    },

    "TBA": {
        "chemin": (
            DOSSIER_INDIVIDUEL
            / "tba_primaire_region_sexe_long.csv"
        ),
        "cles": ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
        "lignes": 390,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES,
            "SEXE": CATEGORIES_SEXE_AUTORISEES
        }
    },

    "TBS": {
        "chemin": (
            DOSSIER_INDIVIDUEL
            / "tbs_primaire_region_sexe_long.csv"
        ),
        "cles": ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
        "lignes": 390,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES,
            "SEXE": CATEGORIES_SEXE_AUTORISEES
        }
    },

    "TAP": {
        "chemin": (
            DOSSIER_INDIVIDUEL
            / "tap_primaire_region_sexe_long.csv"
        ),
        "cles": ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
        "lignes": 390,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES,
            "SEXE": CATEGORIES_SEXE_AUTORISEES
        }
    },

    "Résultats CEP": {
        "chemin": (
            DOSSIER_INDIVIDUEL
            / "taux_reussite_cep_region_sexe_long.csv"
        ),
        "cles": ["REGION", "ANNEE_CIVILE", "SEXE"],
        "lignes": 260,
        "domaines": {
            "ANNEE_CIVILE": ANNEES_CIVILES,
            "SEXE": SEXES
        }
    },

    "IPS TBA": {
        "chemin": (
            DOSSIER_INDIVIDUEL
            / "ips_tba_primaire_region_long.csv"
        ),
        "cles": ["REGION", "ANNEE_SCOLAIRE"],
        "lignes": 130,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES
        }
    },

    "IPS TBS": {
        "chemin": (
            DOSSIER_INDIVIDUEL
            / "ips_tbs_primaire_region_long.csv"
        ),
        "cles": ["REGION", "ANNEE_SCOLAIRE"],
        "lignes": 130,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES
        }
    },

    "IPS TAP": {
        "chemin": (
            DOSSIER_INDIVIDUEL
            / "ips_tap_primaire_region_long.csv"
        ),
        "cles": ["REGION", "ANNEE_SCOLAIRE"],
        "lignes": 130,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES
        }
    },

    "Écoles par statut": {
        "chemin": (
            DOSSIER_INDIVIDUEL
            / "ecoles_primaire_region_statut_long.csv"
        ),
        "cles": ["REGION", "ANNEE_SCOLAIRE", "STATUT"],
        "lignes": 260,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES,
            "STATUT": STATUTS_ATTENDUS
        }
    }
}


# ============================================================
# 4. DEFINITION DES TABLES ANALYTIQUES
# ============================================================

fichiers_analytiques = {

    "Indicateurs régionaux par sexe": {
        "chemin": (
            DOSSIER_FUSIONNE
            / "indicateurs_regionaux_sexe.csv"
        ),
        "cles": ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
        "lignes": 260,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES,
            "SEXE": SEXES
        }
    },

    "Indices de parité régionaux": {
        "chemin": (
            DOSSIER_FUSIONNE
            / "indices_parite_regionaux.csv"
        ),
        "cles": ["REGION", "ANNEE_SCOLAIRE"],
        "lignes": 130,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES
        }
    },

    "Comparaison urbain-rural": {
        "chemin": (
            DOSSIER_FUSIONNE
            / "comparaison_effectifs_urbain_rural.csv"
        ),
        "cles": ["ANNEE_SCOLAIRE", "SEXE"],
        "lignes": 20,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES,
            "SEXE": SEXES
        }
    },

    "Résultats CEP régionaux": {
        "chemin": (
            DOSSIER_FINAL
            / "resultats_cep_regionaux_sexe.csv"
        ),
        "cles": ["REGION", "ANNEE_CIVILE"],
        "lignes": 130,
        "domaines": {
            "ANNEE_CIVILE": ANNEES_CIVILES
        }
    },

    "Répartition régionale des écoles": {
        "chemin": (
            DOSSIER_FINAL
            / "repartition_ecoles_primaire_regionale.csv"
        ),
        "cles": ["REGION", "ANNEE_SCOLAIRE"],
        "lignes": 130,
        "domaines": {
            "ANNEE_SCOLAIRE": ANNEES_SCOLAIRES
        }
    }
}


# ============================================================
# 5. FONCTION DE NORMALISATION
# ============================================================

def normaliser_colonnes_cles(df, colonnes):

    df = df.copy()

    for colonne in colonnes:

        df[colonne] = (
            df[colonne]
            .astype("string")
            .str.strip()
        )

        if colonne in [
            "REGION",
            "SEXE",
            "MILIEU",
            "STATUT"
        ]:
            df[colonne] = df[colonne].str.upper()

    return df


# ============================================================
# 6. FONCTION DE CONTROLE D'UN FICHIER
# ============================================================

def controler_fichier(nom, configuration, categorie):

    chemin = configuration["chemin"]
    cles = configuration["cles"]
    lignes_attendues = configuration["lignes"]
    domaines = configuration["domaines"]

    resultat = {
        "CATEGORIE": categorie,
        "FICHIER": nom,
        "NOMBRE_LIGNES": None,
        "NOMBRE_COLONNES": None,
        "COLONNES_CLES_PRESENTES": False,
        "CLES_MANQUANTES": None,
        "DOUBLONS": None,
        "VALEURS_MANQUANTES": None,
        "VALEURS_INFINIES": None,
        "REGIONS": None,
        "ANNEES": None,
        "COMBINAISONS_MANQUANTES": None,
        "COMBINAISONS_SUPPLEMENTAIRES": None,
        "STATUT": "A_VERIFIER",
        "DETAIL": ""
    }

    if not chemin.exists():

        resultat["DETAIL"] = "Fichier introuvable"

        return resultat, None

    try:

        df = pd.read_csv(
            chemin,
            encoding="utf-8-sig"
        )

        resultat["NOMBRE_LIGNES"] = len(df)
        resultat["NOMBRE_COLONNES"] = len(df.columns)

        if df.empty:

            resultat["DETAIL"] = "Fichier vide"

            return resultat, df

        colonnes_absentes = [
            colonne
            for colonne in cles
            if colonne not in df.columns
        ]

        if colonnes_absentes:

            resultat["DETAIL"] = (
                "Colonnes clés absentes : "
                + ", ".join(colonnes_absentes)
            )

            return resultat, df

        df = normaliser_colonnes_cles(
            df,
            cles
        )

        resultat["COLONNES_CLES_PRESENTES"] = True

        # ----------------------------------------------------
        # 6.1 Valeurs manquantes
        # ----------------------------------------------------

        resultat["CLES_MANQUANTES"] = int(
            df[cles].isna().sum().sum()
            +
            sum(
                (df[colonne] == "").sum()
                for colonne in cles
            )
        )

        resultat["VALEURS_MANQUANTES"] = int(
            df.isna().sum().sum()
        )

        # ----------------------------------------------------
        # 6.2 Doublons
        # ----------------------------------------------------

        resultat["DOUBLONS"] = int(
            df.duplicated(
                subset=cles
            ).sum()
        )

        # ----------------------------------------------------
        # 6.3 Valeurs infinies dans les colonnes numériques
        # ----------------------------------------------------

        colonnes_numeriques = (
            df.select_dtypes(include="number")
            .columns
        )

        if len(colonnes_numeriques) > 0:

            resultat["VALEURS_INFINIES"] = int(
                np.isinf(
                    df[colonnes_numeriques].to_numpy(dtype=float)
                ).sum()
            )

        else:

            resultat["VALEURS_INFINIES"] = 0

        # ----------------------------------------------------
        # 6.4 Nombre de régions
        # ----------------------------------------------------

        if "REGION" in df.columns:

            resultat["REGIONS"] = int(
                df["REGION"].nunique(dropna=True)
            )

        # ----------------------------------------------------
        # 6.5 Nombre d'années
        # ----------------------------------------------------

        if "ANNEE_SCOLAIRE" in df.columns:

            resultat["ANNEES"] = int(
                df["ANNEE_SCOLAIRE"].nunique(dropna=True)
            )

        elif "ANNEE_CIVILE" in df.columns:

            resultat["ANNEES"] = int(
                df["ANNEE_CIVILE"].nunique(dropna=True)
            )

        # ----------------------------------------------------
        # 6.6 Vérification des périodes et catégories
        # ----------------------------------------------------

        problemes = []

        if len(df) != lignes_attendues:

            problemes.append(
                f"Nombre de lignes attendu : {lignes_attendues}"
            )

        if resultat["CLES_MANQUANTES"] != 0:

            problemes.append(
                "Présence de clés manquantes"
            )

        if resultat["DOUBLONS"] != 0:

            problemes.append(
                "Présence de doublons"
            )

        if resultat["VALEURS_MANQUANTES"] != 0:

            problemes.append(
                "Présence de valeurs manquantes"
            )

        if resultat["VALEURS_INFINIES"] != 0:

            problemes.append(
                "Présence de valeurs infinies"
            )

        # Nombre de régions
        if "REGION" in df.columns:

            if resultat["REGIONS"] != REGIONS_ATTENDUES:

                problemes.append(
                    "Nombre de régions différent de 13"
                )

        # Vérification des domaines attendus
        for colonne, valeurs_attendues in domaines.items():

            valeurs_detectees = set(
                df[colonne].dropna().unique()
            )

            if valeurs_detectees != valeurs_attendues:

                problemes.append(
                    f"Valeurs inattendues dans {colonne}"
                )

        # ----------------------------------------------------
        # 6.7 Vérification des combinaisons attendues
        # ----------------------------------------------------

        if resultat["CLES_MANQUANTES"] == 0:

            domaines_cles = []

            for colonne in cles:

                if colonne in domaines:

                    valeurs = domaines[colonne]

                else:

                    valeurs = set(
                        df[colonne].dropna().unique()
                    )

                domaines_cles.append(
                    sorted(valeurs)
                )

            combinaisons_attendues = set(
                product(*domaines_cles)
            )

            combinaisons_observees = set(
                df[cles].itertuples(
                    index=False,
                    name=None
                )
            )

            combinaisons_manquantes = (
                combinaisons_attendues
                - combinaisons_observees
            )

            combinaisons_supplementaires = (
                combinaisons_observees
                - combinaisons_attendues
            )

            resultat["COMBINAISONS_MANQUANTES"] = len(
                combinaisons_manquantes
            )

            resultat["COMBINAISONS_SUPPLEMENTAIRES"] = len(
                combinaisons_supplementaires
            )

            if combinaisons_manquantes:

                problemes.append(
                    "Combinaisons de clés manquantes"
                )

            if combinaisons_supplementaires:

                problemes.append(
                    "Combinaisons de clés supplémentaires"
                )

        else:

            resultat["COMBINAISONS_MANQUANTES"] = None
            resultat["COMBINAISONS_SUPPLEMENTAIRES"] = None

        # ----------------------------------------------------
        # 6.8 Statut final du fichier
        # ----------------------------------------------------

        if problemes:

            resultat["DETAIL"] = " ; ".join(problemes)

        else:

            resultat["STATUT"] = "VALIDE"

            resultat["DETAIL"] = (
                "Tous les contrôles sont conformes"
            )

        return resultat, df

    except Exception as erreur:

        resultat["DETAIL"] = str(erreur)

        return resultat, None


# ============================================================
# 7. FONCTIONS DE CONTROLE DE COHERENCE ENTRE LES TABLES
# ============================================================

controles_coherence = []


def ajouter_controle(nom, condition, detail):

    controles_coherence.append({

        "CONTROLE": nom,

        "RESULTAT": (
            "VALIDE"
            if condition
            else "A_VERIFIER"
        ),

        "DETAIL": detail
    })


def comparer_cles(
    nom,
    df1,
    df2,
    colonnes,
    nom1,
    nom2
):

    if df1 is None or df2 is None:

        ajouter_controle(
            nom,
            False,
            "Un ou plusieurs fichiers ne sont pas disponibles"
        )

        return

    colonnes_absentes = [
        colonne
        for colonne in colonnes
        if (
            colonne not in df1.columns
            or colonne not in df2.columns
        )
    ]

    if colonnes_absentes:

        ajouter_controle(
            nom,
            False,
            "Colonnes absentes : "
            + ", ".join(colonnes_absentes)
        )

        return

    df1 = normaliser_colonnes_cles(df1, colonnes)
    df2 = normaliser_colonnes_cles(df2, colonnes)

    if (
        df1[colonnes].isna().any().any()
        or df2[colonnes].isna().any().any()
    ):

        ajouter_controle(
            nom,
            False,
            "Présence de clés manquantes"
        )

        return

    cles1 = set(
        df1[colonnes].itertuples(
            index=False,
            name=None
        )
    )

    cles2 = set(
        df2[colonnes].itertuples(
            index=False,
            name=None
        )
    )

    coherence = cles1 == cles2

    cles_manquantes = cles1 - cles2
    cles_supplementaires = cles2 - cles1

    ajouter_controle(
        nom,
        coherence,
        (
            f"{nom1} : {len(cles1)} ; "
            f"{nom2} : {len(cles2)} ; "
            f"manquantes : {len(cles_manquantes)} ; "
            f"supplémentaires : {len(cles_supplementaires)}"
        )
    )


# ============================================================
# 8. EXECUTION DES CONTROLES INDIVIDUELS
# ============================================================

resultats = []
donnees_chargees = {}

print("\n" + "=" * 70)
print("CONTROLE DES FICHIERS INDIVIDUELS")
print("=" * 70)

for nom, configuration in fichiers_individuels.items():

    resultat, df = controler_fichier(
        nom,
        configuration,
        "INDIVIDUEL"
    )

    resultats.append(resultat)

    donnees_chargees[nom] = df

    print(
        f"{nom} : {resultat['STATUT']} "
        f"| lignes = {resultat['NOMBRE_LIGNES']} "
        f"| doublons = {resultat['DOUBLONS']} "
        f"| manquants = {resultat['VALEURS_MANQUANTES']}"
    )


# ============================================================
# 9. EXECUTION DES CONTROLES DES TABLES ANALYTIQUES
# ============================================================

print("\n" + "=" * 70)
print("CONTROLE DES TABLES ANALYTIQUES")
print("=" * 70)

for nom, configuration in fichiers_analytiques.items():

    resultat, df = controler_fichier(
        nom,
        configuration,
        "ANALYTIQUE"
    )

    resultats.append(resultat)

    donnees_chargees[nom] = df

    print(
        f"{nom} : {resultat['STATUT']} "
        f"| lignes = {resultat['NOMBRE_LIGNES']} "
        f"| doublons = {resultat['DOUBLONS']} "
        f"| manquants = {resultat['VALEURS_MANQUANTES']}"
    )


# ============================================================
# 10. CONTROLES DE COHERENCE ENTRE LES TABLES
# ============================================================

# ------------------------------------------------------------
# 10.1 EFFECTIFS REGIONAUX / INDICATEURS REGIONAUX
# ------------------------------------------------------------

comparer_cles(
    "Clés effectifs / indicateurs régionaux",
    donnees_chargees.get("Effectifs régionaux par sexe"),
    donnees_chargees.get("Indicateurs régionaux par sexe"),
    ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
    "Effectifs",
    "Indicateurs"
)


# ------------------------------------------------------------
# 10.2 NOUVEAUX INSCRITS CP1 / INDICATEURS REGIONAUX
# ------------------------------------------------------------

comparer_cles(
    "Clés CP1 / indicateurs régionaux",
    donnees_chargees.get("Nouveaux inscrits au CP1"),
    donnees_chargees.get("Indicateurs régionaux par sexe"),
    ["REGION", "ANNEE_SCOLAIRE", "SEXE"],
    "CP1",
    "Indicateurs"
)


# ------------------------------------------------------------
# 10.3 INDICATEURS REGIONAUX / INDICES DE PARITE
# ------------------------------------------------------------

df_indicateurs = donnees_chargees.get(
    "Indicateurs régionaux par sexe"
)

df_indices = donnees_chargees.get(
    "Indices de parité régionaux"
)

if df_indicateurs is not None:

    df_indicateurs_region = (
        df_indicateurs[
            ["REGION", "ANNEE_SCOLAIRE"]
        ]
        .drop_duplicates()
        .copy()
    )

else:

    df_indicateurs_region = None

comparer_cles(
    "Clés indicateurs / indices de parité",
    df_indicateurs_region,
    df_indices,
    ["REGION", "ANNEE_SCOLAIRE"],
    "Indicateurs",
    "Indices"
)


# ------------------------------------------------------------
# 10.4 CEP INDIVIDUEL / CEP FINAL
# ------------------------------------------------------------

comparer_cles(
    "Clés CEP individuel / CEP final",
    donnees_chargees.get("Résultats CEP"),
    donnees_chargees.get("Résultats CEP régionaux"),
    ["REGION", "ANNEE_CIVILE"],
    "CEP individuel",
    "CEP final"
)


# ------------------------------------------------------------
# 10.5 ECOLES INDIVIDUELLES / ECOLES FINALES
# ------------------------------------------------------------

df_ecoles_individuel = donnees_chargees.get(
    "Écoles par statut"
)

if df_ecoles_individuel is not None:

    df_ecoles_individuel_region = (
        df_ecoles_individuel[
            ["REGION", "ANNEE_SCOLAIRE"]
        ]
        .drop_duplicates()
        .copy()
    )

else:

    df_ecoles_individuel_region = None

comparer_cles(
    "Clés écoles individuel / écoles finales",
    df_ecoles_individuel_region,
    donnees_chargees.get("Répartition régionale des écoles"),
    ["REGION", "ANNEE_SCOLAIRE"],
    "Écoles individuelles",
    "Écoles finales"
)


# ============================================================
# 11. VERIFICATION DES PARTS PUBLIC / PRIVE
# ============================================================

df_ecoles_final = donnees_chargees.get(
    "Répartition régionale des écoles"
)

if df_ecoles_final is not None:

    colonnes_parts = [
        "PART_PUBLIC_POURCENT",
        "PART_PRIVE_POURCENT"
    ]

    if all(
        colonne in df_ecoles_final.columns
        for colonne in colonnes_parts
    ):

        somme_parts = (
            df_ecoles_final["PART_PUBLIC_POURCENT"]
            + df_ecoles_final["PART_PRIVE_POURCENT"]
        )

        valeurs_parts_valides = (
            np.isfinite(somme_parts.to_numpy(dtype=float)).all()
            and np.isclose(
                somme_parts.to_numpy(dtype=float),
                100.0,
                atol=0.001
            ).all()
        )

        ajouter_controle(
            "Somme des parts public et privé",
            valeurs_parts_valides,
            "Les parts public et privé doivent totaliser 100 %"
        )

    else:

        ajouter_controle(
            "Somme des parts public et privé",
            False,
            "Colonnes de parts absentes"
        )

else:

    ajouter_controle(
        "Somme des parts public et privé",
        False,
        "Table finale des écoles indisponible"
    )


# ============================================================
# 12. VERIFICATION DES CALCULS DES TABLES ANALYTIQUES
# ============================================================

# ------------------------------------------------------------
# 12.1 COMPARAISON URBAIN-RURAL
# ------------------------------------------------------------

df_urbain_rural = donnees_chargees.get(
    "Comparaison urbain-rural"
)

colonnes_urbain_rural = [
    "EFFECTIF_URBAIN",
    "EFFECTIF_RURAL",
    "ECART_URBAIN_MOINS_RURAL",
    "ECART_ABSOLU",
    "RATIO_URBAIN_RURAL"
]

if df_urbain_rural is not None:

    if all(
        colonne in df_urbain_rural.columns
        for colonne in colonnes_urbain_rural
    ):

        ecart_calcule = (
            df_urbain_rural["EFFECTIF_URBAIN"]
            - df_urbain_rural["EFFECTIF_RURAL"]
        )

        ecart_absolu_calcule = ecart_calcule.abs()

        controle_ecart = np.isclose(
            df_urbain_rural[
                "ECART_URBAIN_MOINS_RURAL"
            ].to_numpy(dtype=float),
            ecart_calcule.to_numpy(dtype=float)
        ).all()

        controle_ecart_absolu = np.isclose(
            df_urbain_rural[
                "ECART_ABSOLU"
            ].to_numpy(dtype=float),
            ecart_absolu_calcule.to_numpy(dtype=float)
        ).all()

        ajouter_controle(
            "Calcul des écarts urbain-rural",
            bool(controle_ecart and controle_ecart_absolu),
            "Vérification de l'écart signé et de l'écart absolu"
        )

        # Le ratio est vérifié uniquement lorsque le dénominateur
        # rural est différent de zéro.
        masque_ratio = (
            df_urbain_rural["EFFECTIF_RURAL"] != 0
        )

        if masque_ratio.any():

            ratio_calcule = (
                df_urbain_rural.loc[
                    masque_ratio,
                    "EFFECTIF_URBAIN"
                ]
                /
                df_urbain_rural.loc[
                    masque_ratio,
                    "EFFECTIF_RURAL"
                ]
            )

            ratio_observe = df_urbain_rural.loc[
                masque_ratio,
                "RATIO_URBAIN_RURAL"
            ]

            controle_ratio = bool(
                np.isclose(
                    ratio_observe.to_numpy(dtype=float),
                    ratio_calcule.to_numpy(dtype=float)
                ).all()
            )

        else:

            controle_ratio = True

        ajouter_controle(
            "Calcul du ratio urbain-rural",
            controle_ratio,
            "Vérification du ratio des effectifs urbains et ruraux"
        )

    else:

        ajouter_controle(
            "Calcul des indicateurs urbain-rural",
            False,
            "Colonnes analytiques nécessaires absentes"
        )

else:

    ajouter_controle(
        "Calcul des indicateurs urbain-rural",
        False,
        "Table de comparaison urbain-rural indisponible"
    )


# ------------------------------------------------------------
# 12.2 RESULTATS CEP
# ------------------------------------------------------------

df_cep_final = donnees_chargees.get(
    "Résultats CEP régionaux"
)

colonnes_cep = [
    "TAUX_FILLES",
    "TAUX_GARCONS",
    "ECART_FILLES_MOINS_GARCONS",
    "ECART_ABSOLU"
]

if df_cep_final is not None:

    if all(
        colonne in df_cep_final.columns
        for colonne in colonnes_cep
    ):

        ecart_cep = (
            df_cep_final["TAUX_FILLES"]
            - df_cep_final["TAUX_GARCONS"]
        )

        controle_ecart_cep = bool(
            np.isclose(
                df_cep_final[
                    "ECART_FILLES_MOINS_GARCONS"
                ].to_numpy(dtype=float),
                ecart_cep.to_numpy(dtype=float)
            ).all()
        )

        controle_absolu_cep = bool(
            np.isclose(
                df_cep_final["ECART_ABSOLU"].to_numpy(dtype=float),
                ecart_cep.abs().to_numpy(dtype=float)
            ).all()
        )

        ajouter_controle(
            "Calcul des écarts de réussite au CEP",
            controle_ecart_cep and controle_absolu_cep,
            "Vérification des écarts entre filles et garçons"
        )

    else:

        ajouter_controle(
            "Calcul des écarts de réussite au CEP",
            False,
            "Colonnes analytiques nécessaires absentes"
        )

else:

    ajouter_controle(
        "Calcul des écarts de réussite au CEP",
        False,
        "Table finale du CEP indisponible"
    )


# ------------------------------------------------------------
# 12.3 REPARTITION DES ECOLES
# ------------------------------------------------------------

if df_ecoles_final is not None:

    colonnes_ecoles = [
        "NOMBRE_ECOLES_PUBLIC",
        "NOMBRE_ECOLES_PRIVE",
        "NOMBRE_ECOLES_TOTAL",
        "ECART_PUBLIC_MOINS_PRIVE"
    ]

    if all(
        colonne in df_ecoles_final.columns
        for colonne in colonnes_ecoles
    ):

        total_calcule = (
            df_ecoles_final["NOMBRE_ECOLES_PUBLIC"]
            + df_ecoles_final["NOMBRE_ECOLES_PRIVE"]
        )

        ecart_calcule = (
            df_ecoles_final["NOMBRE_ECOLES_PUBLIC"]
            - df_ecoles_final["NOMBRE_ECOLES_PRIVE"]
        )

        controle_total = bool(
            np.isclose(
                df_ecoles_final[
                    "NOMBRE_ECOLES_TOTAL"
                ].to_numpy(dtype=float),
                total_calcule.to_numpy(dtype=float)
            ).all()
        )

        controle_ecart_ecoles = bool(
            np.isclose(
                df_ecoles_final[
                    "ECART_PUBLIC_MOINS_PRIVE"
                ].to_numpy(dtype=float),
                ecart_calcule.to_numpy(dtype=float)
            ).all()
        )

        ajouter_controle(
            "Calcul du total des écoles",
            controle_total,
            "Total = établissements publics + établissements privés"
        )

        ajouter_controle(
            "Calcul de l'écart public-privé",
            controle_ecart_ecoles,
            "Écart = établissements publics - établissements privés"
        )

    else:

        ajouter_controle(
            "Calcul des indicateurs des écoles",
            False,
            "Colonnes analytiques nécessaires absentes"
        )

else:

    ajouter_controle(
        "Calcul des indicateurs des écoles",
        False,
        "Table finale des écoles indisponible"
    )


# ============================================================
# 13. GENERATION DES RAPPORTS
# ============================================================

DOSSIER_RAPPORT.mkdir(
    parents=True,
    exist_ok=True
)

rapport_fichiers = pd.DataFrame(resultats)

rapport_coherence = pd.DataFrame(
    controles_coherence
)

FICHIER_RAPPORT_FICHIERS = (
    DOSSIER_RAPPORT
    / "rapport_validation_fichiers_transformation.csv"
)

FICHIER_RAPPORT_COHERENCE = (
    DOSSIER_RAPPORT
    / "rapport_coherence_tables_transformation.csv"
)

rapport_fichiers.to_csv(
    FICHIER_RAPPORT_FICHIERS,
    index=False,
    encoding="utf-8-sig"
)

rapport_coherence.to_csv(
    FICHIER_RAPPORT_COHERENCE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 14. CALCUL DU STATUT GLOBAL
# ============================================================

tous_fichiers_valides = bool(
    (
        rapport_fichiers["STATUT"] == "VALIDE"
    ).all()
)

toutes_coherences_valides = bool(
    (
        rapport_coherence["RESULTAT"] == "VALIDE"
    ).all()
)

statut_global = (
    "VALIDE"
    if tous_fichiers_valides and toutes_coherences_valides
    else "A_VERIFIER"
)


# ============================================================
# 15. AFFICHAGE DU RAPPORT DES FICHIERS
# ============================================================

print("\n" + "=" * 70)
print("RAPPORT GLOBAL DES FICHIERS")
print("=" * 70)

colonnes_affichage = [
    "CATEGORIE",
    "FICHIER",
    "NOMBRE_LIGNES",
    "DOUBLONS",
    "VALEURS_MANQUANTES",
    "VALEURS_INFINIES",
    "COMBINAISONS_MANQUANTES",
    "STATUT",
    "DETAIL"
]

print(
    rapport_fichiers[
        colonnes_affichage
    ].to_string(index=False)
)


# ============================================================
# 16. AFFICHAGE DES CONTROLES DE COHERENCE
# ============================================================

print("\n" + "=" * 70)
print("COHERENCE ENTRE LES TABLES")
print("=" * 70)

print(
    rapport_coherence.to_string(index=False)
)


# ============================================================
# 17. BILAN FINAL
# ============================================================

nombre_fichiers_valides = int(
    (
        rapport_fichiers["STATUT"] == "VALIDE"
    ).sum()
)

nombre_coherences_valides = int(
    (
        rapport_coherence["RESULTAT"] == "VALIDE"
    ).sum()
)

print("\n" + "=" * 70)
print("BILAN FINAL DE LA VALIDATION")
print("=" * 70)

print(
    f"Fichiers individuels : "
    f"{len(fichiers_individuels)}"
)

print(
    f"Tables analytiques : "
    f"{len(fichiers_analytiques)}"
)

print(
    f"Total des fichiers : "
    f"{len(rapport_fichiers)}"
)

print(
    f"Fichiers validés : "
    f"{nombre_fichiers_valides}/{len(rapport_fichiers)}"
)

print(
    f"Contrôles de cohérence validés : "
    f"{nombre_coherences_valides}/{len(rapport_coherence)}"
)

print(
    f"STATUT GLOBAL : {statut_global}"
)


# ============================================================
# 18. FICHIERS DE RAPPORT GENERES
# ============================================================

print("\n========== RAPPORTS GENERES ==========")

print(
    f"Rapport des fichiers : "
    f"{FICHIER_RAPPORT_FICHIERS}"
)

print(
    f"Rapport de cohérence : "
    f"{FICHIER_RAPPORT_COHERENCE}"
)

print("\n" + "=" * 70)

if statut_global == "VALIDE":

    print("VALIDATION DE LA TRANSFORMATION TERMINEE AVEC SUCCES")

else:

    print("CERTAINS CONTROLES NECESSITENT UNE VERIFICATION")

print("=" * 70)
