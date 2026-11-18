
from pathlib import Path
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

DOSSIER_RAPPORT = (
    RACINE_PROJET
    / "outputs"
    / "tables"
    / "transformation"
)


# ============================================================
# 2. LISTE DES FICHIERS A INSPECTER
# ============================================================

FICHIERS = [
    {
        "nom": "Effectifs régionaux par sexe",
        "nettoye": "effectifs_primaire_region_sexe.csv",
        "transforme": "effectifs_primaire_region_sexe_long.csv"
    },
    {
        "nom": "Effectifs urbains et ruraux",
        "nettoye": "effectifs_primaire_milieu_sexe.csv",
        "transforme": "effectifs_primaire_milieu_sexe_long.csv"
    },
    {
        "nom": "Nouveaux inscrits au CP1",
        "nettoye": "nouveaux_inscrits_cp1_region_sexe.csv",
        "transforme": "nouveaux_inscrits_cp1_region_sexe_long.csv"
    },
    {
        "nom": "Taux brut d'admission",
        "nettoye": "tba_primaire_region_sexe.csv",
        "transforme": "tba_primaire_region_sexe_long.csv"
    },
    {
        "nom": "Taux brut de scolarisation",
        "nettoye": "tbs_primaire_region_sexe.csv",
        "transforme": "tbs_primaire_region_sexe_long.csv"
    },
    {
        "nom": "Taux d'achèvement du primaire",
        "nettoye": "tap_primaire_region_sexe.csv",
        "transforme": "tap_primaire_region_sexe_long.csv"
    },
    {
        "nom": "Taux de réussite au CEP",
        "nettoye": "taux_reussite_cep_region_sexe.csv",
        "transforme": "taux_reussite_cep_region_sexe_long.csv"
    },
    {
        "nom": "Indice de parité du TBA",
        "nettoye": "ips_tba_primaire_region.csv",
        "transforme": "ips_tba_primaire_region_long.csv"
    },
    {
        "nom": "Indice de parité du TBS",
        "nettoye": "ips_tbs_primaire_region.csv",
        "transforme": "ips_tbs_primaire_region_long.csv"
    },
    {
        "nom": "Indice de parité du TAP",
        "nettoye": "ips_tap_primaire_region.csv",
        "transforme": "ips_tap_primaire_region_long.csv"
    },
    {
        "nom": "Établissements primaires par statut",
        "nettoye": "ecoles_primaire_region_statut.csv",
        "transforme": "ecoles_primaire_region_statut_long.csv"
    }
]


# ============================================================
# 3. FONCTION D'INSPECTION D'UN FICHIER
# ============================================================

def inspecter_fichier(chemin):

    if not chemin.exists():

        return {
            "STATUT": "INTROUVABLE",
            "LIGNES": None,
            "COLONNES": None,
            "NOMS_COLONNES": "",
            "VALEURS_MANQUANTES": None,
            "DOUBLONS_COMPLETS": None,
            "TYPES": "",
            "ERREUR": "Fichier introuvable"
        }, None

    try:

        df = pd.read_csv(
            chemin,
            encoding="utf-8-sig"
        )

        resultat = {
            "STATUT": "LU",
            "LIGNES": len(df),
            "COLONNES": len(df.columns),
            "NOMS_COLONNES": " | ".join(
                map(str, df.columns)
            ),
            "VALEURS_MANQUANTES": int(
                df.isna().sum().sum()
            ),
            "DOUBLONS_COMPLETS": int(
                df.duplicated().sum()
            ),
            "TYPES": " | ".join(
                f"{colonne}: {type_colonne}"
                for colonne, type_colonne
                in df.dtypes.items()
            ),
            "ERREUR": ""
        }

        return resultat, df

    except Exception as erreur:

        return {
            "STATUT": "ERREUR",
            "LIGNES": None,
            "COLONNES": None,
            "NOMS_COLONNES": "",
            "VALEURS_MANQUANTES": None,
            "DOUBLONS_COMPLETS": None,
            "TYPES": "",
            "ERREUR": str(erreur)
        }, None


# ============================================================
# 4. INSPECTION DES DONNEES NETTOYEES ET TRANSFORMEES
# ============================================================

resultats = []

print("\n" + "=" * 75)
print("INSPECTION DES DONNEES NETTOYEES ET TRANSFORMEES")
print("=" * 75)

for fichier in FICHIERS:

    nom = fichier["nom"]

    chemin_nettoye = (
        DOSSIER_NETTOYE
        / fichier["nettoye"]
    )

    chemin_transformee = (
        DOSSIER_TRANSFORME
        / fichier["transforme"]
    )

    print("\n" + "=" * 75)
    print(f"DATASET : {nom.upper()}")
    print("=" * 75)

    # --------------------------------------------------------
    # 4.1 INSPECTION DU FICHIER NETTOYE
    # --------------------------------------------------------

    print("\n--- FICHIER NETTOYE ---")

    resultat_nettoye, df_nettoye = inspecter_fichier(
        chemin_nettoye
    )

    if df_nettoye is not None:

        print(f"Statut : {resultat_nettoye['STATUT']}")
        print(f"Lignes : {len(df_nettoye)}")
        print(f"Colonnes : {len(df_nettoye.columns)}")

        print("\nNoms des colonnes :")
        print(list(df_nettoye.columns))

        print("\nTypes des variables :")
        print(df_nettoye.dtypes.to_string())

        print("\nPremières observations :")
        print(
            df_nettoye.head(3).to_string(index=False)
        )

        print(
            f"\nValeurs manquantes : "
            f"{resultat_nettoye['VALEURS_MANQUANTES']}"
        )

        print(
            f"Doublons complets : "
            f"{resultat_nettoye['DOUBLONS_COMPLETS']}"
        )

    else:

        print(f"Statut : {resultat_nettoye['STATUT']}")
        print(resultat_nettoye["ERREUR"])

    # --------------------------------------------------------
    # 4.2 INSPECTION DU FICHIER TRANSFORME
    # --------------------------------------------------------

    print("\n--- FICHIER TRANSFORME ---")

    resultat_transforme, df_transforme = inspecter_fichier(
        chemin_transformee
    )

    if df_transforme is not None:

        print(f"Statut : {resultat_transforme['STATUT']}")
        print(f"Lignes : {len(df_transforme)}")
        print(f"Colonnes : {len(df_transforme.columns)}")

        print("\nNoms des colonnes :")
        print(list(df_transforme.columns))

        print("\nTypes des variables :")
        print(df_transforme.dtypes.to_string())

        print("\nPremières observations :")
        print(
            df_transforme.head(3).to_string(index=False)
        )

        print(
            f"\nValeurs manquantes : "
            f"{resultat_transforme['VALEURS_MANQUANTES']}"
        )

        print(
            f"Doublons complets : "
            f"{resultat_transforme['DOUBLONS_COMPLETS']}"
        )

    else:

        print(f"Statut : {resultat_transforme['STATUT']}")
        print(resultat_transforme["ERREUR"])

    # --------------------------------------------------------
    # 4.3 COMPARAISON STRUCTURELLE
    # --------------------------------------------------------

    if (
        df_nettoye is not None
        and df_transforme is not None
    ):

        comparaison = "Fichiers disponibles"

        print("\n--- COMPARAISON STRUCTURELLE ---")

        print(
            f"Nombre de lignes : "
            f"{len(df_nettoye)} -> {len(df_transforme)}"
        )

        print(
            f"Nombre de colonnes : "
            f"{len(df_nettoye.columns)} -> "
            f"{len(df_transforme.columns)}"
        )

        print(
            "\nRemarque : une différence de dimensions est "
            "attendue lors du passage au format long."
        )

    else:

        comparaison = "Comparaison impossible"

    # --------------------------------------------------------
    # 4.4 ENREGISTREMENT DU RESULTAT
    # --------------------------------------------------------

    resultats.append({

        "DATASET": nom,

        "FICHIER_NETTOYE": fichier["nettoye"],

        "STATUT_NETTOYE": resultat_nettoye["STATUT"],

        "LIGNES_NETTOYE": resultat_nettoye["LIGNES"],

        "COLONNES_NETTOYE": resultat_nettoye["COLONNES"],

        "FICHIER_TRANSFORME": fichier["transforme"],

        "STATUT_TRANSFORME": resultat_transforme["STATUT"],

        "LIGNES_TRANSFORME": resultat_transforme["LIGNES"],

        "COLONNES_TRANSFORME": resultat_transforme["COLONNES"],

        "COMPARAISON": comparaison

    })


# ============================================================
# 5. GENERATION DU RAPPORT D'INSPECTION
# ============================================================

DOSSIER_RAPPORT.mkdir(
    parents=True,
    exist_ok=True
)

rapport = pd.DataFrame(resultats)

FICHIER_RAPPORT = (
    DOSSIER_RAPPORT
    / "rapport_inspection_fidelite_donnees.csv"
)

rapport.to_csv(
    FICHIER_RAPPORT,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 6. BILAN FINAL
# ============================================================

nombre_nettoyes_disponibles = int(
    (rapport["STATUT_NETTOYE"] == "LU").sum()
)

nombre_transformes_disponibles = int(
    (rapport["STATUT_TRANSFORME"] == "LU").sum()
)

nombre_comparaisons_possibles = int(
    (rapport["COMPARAISON"] == "Fichiers disponibles").sum()
)

print("\n" + "=" * 75)
print("BILAN GENERAL DE L'INSPECTION")
print("=" * 75)

print(f"Datasets examinés : {len(FICHIERS)}")

print(
    f"Fichiers nettoyés disponibles : "
    f"{nombre_nettoyes_disponibles}/{len(FICHIERS)}"
)

print(
    f"Fichiers transformés disponibles : "
    f"{nombre_transformes_disponibles}/{len(FICHIERS)}"
)

print(
    f"Comparaisons structurelles possibles : "
    f"{nombre_comparaisons_possibles}/{len(FICHIERS)}"
)

print("\nRapport enregistré :")
print(FICHIER_RAPPORT)

print("\n" + "=" * 75)
print("INSPECTION DES STRUCTURES TERMINEE")
print("=" * 75)
