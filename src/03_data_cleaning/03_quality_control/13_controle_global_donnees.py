
from pathlib import Path
import pandas as pd


# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

# Dossier contenant les fichiers nettoyés
DATA_DIR = (
    BASE_DIR / "data" /
    "03_cleaned_data" / "final"
)

# Dossier de sauvegarde du rapport
OUTPUT_DIR = (
    BASE_DIR / "outputs" /
    "tables" / "cleaning"
)

OUTPUT_PATH = OUTPUT_DIR / "rapport_controle_global.csv"


# ============================================================
# 2. LISTE DES FICHIERS A CONTROLER
# ============================================================

fichiers_attendus = [
    "effectifs_primaire_region_sexe.csv",
    "effectifs_primaire_milieu_sexe.csv",
    "tba_primaire_region_sexe.csv",
    "tbs_primaire_region_sexe.csv",
    "tap_primaire_region_sexe.csv",
    "taux_reussite_cep_region_sexe.csv",
    "ips_tba_primaire_region.csv",
    "ips_tbs_primaire_region.csv",
    "ips_tap_primaire_region.csv",
    "ecoles_primaire_region_statut.csv",
    "nouveaux_inscrits_cp1_region_sexe.csv"
]


# ============================================================
# 3. PREPARATION DU CONTROLE
# ============================================================

resultats = []

print("\n========== CONTROLE GLOBAL DES DONNEES ==========")

print("\nDossier des données :", DATA_DIR)

if not DATA_DIR.exists():
    raise FileNotFoundError(
        f"Dossier des données introuvable : {DATA_DIR}"
    )


# ============================================================
# 4. CONTROLE DE CHAQUE FICHIER
# ============================================================

for nom_fichier in fichiers_attendus:

    chemin_fichier = DATA_DIR / nom_fichier

    print("\n----------------------------------------")
    print("FICHIER :", nom_fichier)

    # Initialisation des résultats
    dimensions = "NON VERIFIEES"
    nombre_lignes = 0
    nombre_colonnes = 0
    nombre_manquants = "NON VERIFIES"
    nombre_doublons = "NON VERIFIES"
    statut = "A VERIFIER"

    # Vérifier l'existence
    if not chemin_fichier.exists():

        print("ERREUR : fichier introuvable.")

        resultats.append({
            "FICHIER": nom_fichier,
            "EXISTENCE": "NON",
            "LIGNES": nombre_lignes,
            "COLONNES": nombre_colonnes,
            "VALEURS_MANQUANTES": nombre_manquants,
            "DOUBLONS": nombre_doublons,
            "STATUT": "FICHIER ABSENT"
        })

        continue

    # Lire le fichier
    try:

        df = pd.read_csv(
            chemin_fichier,
            encoding="utf-8-sig"
        )

    except Exception as erreur:

        print("ERREUR DE LECTURE :", erreur)

        resultats.append({
            "FICHIER": nom_fichier,
            "EXISTENCE": "OUI",
            "LIGNES": nombre_lignes,
            "COLONNES": nombre_colonnes,
            "VALEURS_MANQUANTES": nombre_manquants,
            "DOUBLONS": nombre_doublons,
            "STATUT": "ERREUR DE LECTURE"
        })

        continue

    # Vérifier les dimensions observées
    nombre_lignes, nombre_colonnes = df.shape

    dimensions = f"{nombre_lignes} x {nombre_colonnes}"

    print("Dimensions observées :", dimensions)

    # Vérifier si le fichier est vide
    fichier_non_vide = (
        nombre_lignes > 0 and nombre_colonnes > 0
    )

    if fichier_non_vide:
        print("Structure : fichier non vide.")
    else:
        print("ATTENTION : fichier vide.")

    # Vérifier les valeurs manquantes
    nombre_manquants = int(
        df.isna().sum().sum()
    )

    print(
        "Nombre total de valeurs manquantes :",
        nombre_manquants
    )

    # Vérifier les lignes entièrement dupliquées
    nombre_doublons = int(
        df.duplicated().sum()
    )

    print(
        "Nombre de lignes entièrement dupliquées :",
        nombre_doublons
    )

    # Afficher les colonnes
    print("Colonnes :", df.columns.tolist())

    # Déterminer le statut du fichier
    if (
        fichier_non_vide
        and nombre_manquants == 0
        and nombre_doublons == 0
    ):
        statut = "VALIDE"

    else:
        statut = "A VERIFIER"

    print("STATUT :", statut)

    # Enregistrer les résultats
    resultats.append({
        "FICHIER": nom_fichier,
        "EXISTENCE": "OUI",
        "LIGNES": nombre_lignes,
        "COLONNES": nombre_colonnes,
        "VALEURS_MANQUANTES": nombre_manquants,
        "DOUBLONS": nombre_doublons,
        "STATUT": statut
    })


# ============================================================
# 5. CONSTRUCTION DU RAPPORT RECAPITULATIF
# ============================================================

rapport = pd.DataFrame(resultats)

print("\n========== RAPPORT RECAPITULATIF ==========")

print(
    rapport.to_string(index=False)
)


# ============================================================
# 6. BILAN GLOBAL
# ============================================================

nombre_total = len(fichiers_attendus)

nombre_disponibles = (
    rapport["EXISTENCE"] == "OUI"
).sum()

nombre_valides = (
    rapport["STATUT"] == "VALIDE"
).sum()

nombre_a_verifier = (
    rapport["STATUT"] != "VALIDE"
).sum()

print("\n========== BILAN GLOBAL ==========")

print("Nombre de fichiers attendus :", nombre_total)

print(
    "Nombre de fichiers disponibles :",
    nombre_disponibles
)

print(
    "Nombre de fichiers valides :",
    nombre_valides
)

print(
    "Nombre de fichiers à vérifier :",
    nombre_a_verifier
)


# ============================================================
# 7. ENREGISTREMENT DU RAPPORT
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

rapport.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("\nRAPPORT ENREGISTRE :", OUTPUT_PATH)


# ============================================================
# 8. RESULTAT FINAL
# ============================================================

if nombre_valides == nombre_total:

    print("\nCONTROLE GLOBAL TERMINE AVEC SUCCES.")

else:

    print(
        "\nATTENTION : certains fichiers nécessitent "
        "une vérification."
    )
