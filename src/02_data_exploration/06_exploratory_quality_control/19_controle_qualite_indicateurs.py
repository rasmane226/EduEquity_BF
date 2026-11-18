
from pathlib import Path

import pandas as pd


# Chemins du projet
BASE_DIR = Path(__file__).resolve().parents[3]

DOSSIER_DONNEES = BASE_DIR / "data" / "intermediate"
DOSSIER_SORTIE = BASE_DIR / "outputs" / "tables"

FICHIER_SORTIE = DOSSIER_SORTIE / "rapport_qualite_indicateurs.csv"


# Fichiers à contrôler et règles adaptées à chaque indicateur
fichiers = {
    "effectifs_primaire_region_sexe.csv": {
        "type": "effectifs"
    },
    "effectifs_primaire_milieu_sexe.csv": {
        "type": "effectifs"
    },
    "tba_primaire_region_sexe.csv": {
        "type": "taux",
        "maximum": 150
    },
    "tbs_primaire_region_sexe.csv": {
        "type": "taux",
        "maximum": 150
    },
    "tap_primaire_region_sexe.csv": {
        "type": "taux",
        "maximum": 150
    },
    "taux_reussite_cep_region_sexe.csv": {
        "type": "taux",
        "maximum": 100
    },
    "ips_tba_primaire_region.csv": {
        "type": "indice"
    },
    "ips_tbs_primaire_region.csv": {
        "type": "indice"
    },
    "ips_tap_primaire_region.csv": {
        "type": "indice"
    },
    "ecoles_primaire_region_statut.csv": {
        "type": "effectifs"
    }
}


# Liste des résultats
resultats = []


# Contrôle de chaque fichier
for nom_fichier, regles in fichiers.items():

    chemin = DOSSIER_DONNEES / nom_fichier

    print(f"\nContrôle : {nom_fichier}")

    if not chemin.exists():
        resultats.append({
            "fichier": nom_fichier,
            "statut": "Fichier manquant",
            "lignes": None,
            "colonnes": None,
            "valeurs_manquantes": None,
            "lignes_dupliquees": None,
            "colonnes_numeriques": None,
            "valeurs_non_numeriques": None,
            "valeurs_negatives": None,
            "valeurs_non_entieres": None,
            "valeurs_hors_limites": None
        })

        print("Fichier introuvable.")
        continue

    # Lecture du fichier
    df = pd.read_csv(chemin, encoding="utf-8-sig")

    # Compteurs des anomalies
    valeurs_non_numeriques = 0
    valeurs_negatives = 0
    valeurs_non_entieres = 0
    valeurs_hors_limites = 0

    colonnes_numeriques = 0

    # Contrôle des colonnes numériques
    for colonne in df.columns:

        valeurs_originales = df[colonne]

        valeurs_converties = pd.to_numeric(
            valeurs_originales,
            errors="coerce"
        )

        # Une colonne est considérée numérique
        # si elle contient au moins une valeur numérique.
        if valeurs_converties.notna().any():

            colonnes_numeriques += 1

            # Détection des textes non convertibles
            cellules_remplies = (
                valeurs_originales.notna()
                & valeurs_originales.astype(str).str.strip().ne("")
            )

            valeurs_non_numeriques += (
                cellules_remplies & valeurs_converties.isna()
            ).sum()

            valeurs_valides = valeurs_converties.dropna()

            # Détection des valeurs négatives
            valeurs_negatives += (valeurs_valides < 0).sum()

            # Règles pour les effectifs
            if regles["type"] == "effectifs":

                valeurs_non_entieres += (
                    valeurs_valides % 1 != 0
                ).sum()

            # Règles pour les taux
            elif regles["type"] == "taux":

                maximum = regles["maximum"]

                valeurs_hors_limites += (
                    (valeurs_valides < 0)
                    | (valeurs_valides > maximum)
                ).sum()

            # Règles pour les indices de parité
            elif regles["type"] == "indice":

                valeurs_hors_limites += (
                    valeurs_valides <= 0
                ).sum()

    # Contrôles généraux
    valeurs_manquantes = df.isna().sum().sum()
    lignes_dupliquees = df.duplicated().sum()

    # Résultat du fichier
    resultats.append({
        "fichier": nom_fichier,
        "statut": "Analysé",
        "lignes": df.shape[0],
        "colonnes": df.shape[1],
        "valeurs_manquantes": valeurs_manquantes,
        "lignes_dupliquees": lignes_dupliquees,
        "colonnes_numeriques": colonnes_numeriques,
        "valeurs_non_numeriques": valeurs_non_numeriques,
        "valeurs_negatives": valeurs_negatives,
        "valeurs_non_entieres": valeurs_non_entieres,
        "valeurs_hors_limites": valeurs_hors_limites
    })

    print(f"Dimensions : {df.shape}")
    print(f"Valeurs manquantes : {valeurs_manquantes}")
    print(f"Lignes dupliquées : {lignes_dupliquees}")
    print(f"Colonnes numériques : {colonnes_numeriques}")
    print(f"Valeurs non numériques : {valeurs_non_numeriques}")
    print(f"Valeurs négatives : {valeurs_negatives}")
    print(f"Valeurs non entières : {valeurs_non_entieres}")
    print(f"Valeurs hors limites : {valeurs_hors_limites}")


# Création du rapport final
rapport = pd.DataFrame(resultats)


# Création du dossier de sortie
DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)


# Exportation du rapport
rapport.to_csv(
    FICHIER_SORTIE,
    index=False,
    encoding="utf-8-sig"
)


# Résumé général
print("\n" + "=" * 50)
print("RÉSUMÉ DU CONTRÔLE QUALITÉ")
print("=" * 50)

print(f"Fichiers attendus : {len(fichiers)}")
print(
    "Fichiers analysés :",
    (rapport["statut"] == "Analysé").sum()
)
print(
    "Fichiers manquants :",
    (rapport["statut"] == "Fichier manquant").sum()
)

print(f"\nRapport enregistré : {FICHIER_SORTIE}")
