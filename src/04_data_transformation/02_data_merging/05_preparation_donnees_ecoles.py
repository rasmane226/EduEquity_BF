
from pathlib import Path
import numpy as np
import pandas as pd


# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

RACINE_PROJET = Path(__file__).resolve().parents[3]

FICHIER_SOURCE = (
    RACINE_PROJET
    / "data"
    / "04_transformed_data"
    / "transformed_sheets"
    / "ecoles_primaire_region_statut_long.csv"
)

DOSSIER_SORTIE = (
    RACINE_PROJET
    / "data"
    / "04_transformed_data"
    / "final"
)

DOSSIER_RAPPORTS = (
    RACINE_PROJET
    / "outputs"
    / "tables"
    / "transformation"
)

FICHIER_SORTIE = (
    DOSSIER_SORTIE
    / "repartition_ecoles_primaire_regionale.csv"
)

FICHIER_RAPPORT = (
    DOSSIER_RAPPORTS
    / "rapport_preparation_ecoles.csv"
)


# ============================================================
# 2. PARAMETRES DE VALIDATION
# ============================================================

ANNEES_ATTENDUES = {
    f"{annee}-{annee + 1}"
    for annee in range(2015, 2025)
}

STATUTS_ATTENDUS = {"PUBLIC", "PRIVÉ"}

NOMBRE_REGIONS_ATTENDU = 13
NOMBRE_ANNEES_ATTENDU = 10
NOMBRE_LIGNES_ATTENDU = 130

COLONNES_CLES = [
    "REGION",
    "ANNEE_SCOLAIRE",
    "STATUT"
]


# ============================================================
# 3. FONCTION DE CREATION DU RAPPORT
# ============================================================

def enregistrer_rapport(resultats):

    rapport = pd.DataFrame([
        {
            "CONTROLE": controle,
            "RESULTAT": resultat
        }
        for controle, resultat in resultats.items()
    ])

    DOSSIER_RAPPORTS.mkdir(
        parents=True,
        exist_ok=True
    )

    rapport.to_csv(
        FICHIER_RAPPORT,
        index=False,
        encoding="utf-8-sig"
    )

    return rapport


# ============================================================
# 4. CHARGEMENT DU FICHIER SOURCE
# ============================================================

print("=" * 70)
print("PREPARATION DES DONNEES SUR LES ECOLES PRIMAIRES")
print("=" * 70)

if not FICHIER_SOURCE.exists():
    raise FileNotFoundError(
        f"Fichier source introuvable : {FICHIER_SOURCE}"
    )

DOSSIER_SORTIE.mkdir(
    parents=True,
    exist_ok=True
)

DOSSIER_RAPPORTS.mkdir(
    parents=True,
    exist_ok=True
)

df = pd.read_csv(
    FICHIER_SOURCE,
    encoding="utf-8-sig"
)

print("\n========== STRUCTURE DU FICHIER SOURCE ==========")
print(f"Fichier chargé : {FICHIER_SOURCE.name}")
print(f"Nombre de lignes : {len(df)}")
print(f"Colonnes : {list(df.columns)}")

if df.empty:
    raise ValueError("Le fichier source est vide.")


# ============================================================
# 5. VERIFICATION DES COLONNES OBLIGATOIRES
# ============================================================

for colonne in COLONNES_CLES:
    if colonne not in df.columns:
        raise ValueError(
            f"La colonne obligatoire '{colonne}' est absente."
        )

# Normalisation des clés
df["REGION"] = (
    df["REGION"]
    .astype("string")
    .str.strip()
    .str.upper()
)

df["ANNEE_SCOLAIRE"] = (
    df["ANNEE_SCOLAIRE"]
    .astype("string")
    .str.strip()
)

df["STATUT"] = (
    df["STATUT"]
    .astype("string")
    .str.strip()
    .str.upper()
)


# ============================================================
# 6. IDENTIFICATION DE LA COLONNE DU NOMBRE D'ECOLES
# ============================================================

colonnes_possibles = [
    "NOMBRE_ECOLES",
    "EFFECTIF_ECOLES",
    "NOMBRE_ETABLISSEMENTS",
    "EFFECTIF",
    "VALEUR"
]

colonne_nombre = next(
    (
        colonne
        for colonne in colonnes_possibles
        if colonne in df.columns
    ),
    None
)

if colonne_nombre is None:

    colonnes_numeriques = [
        colonne
        for colonne in df.select_dtypes(include="number").columns
        if colonne not in COLONNES_CLES
    ]

    if len(colonnes_numeriques) == 1:
        colonne_nombre = colonnes_numeriques[0]

    else:
        raise ValueError(
            "Impossible d'identifier automatiquement la colonne "
            "du nombre d'écoles. "
            f"Colonnes numériques détectées : {colonnes_numeriques}."
        )

print(
    f"\nColonne du nombre d'écoles : {colonne_nombre}"
)

df[colonne_nombre] = pd.to_numeric(
    df[colonne_nombre],
    errors="coerce"
)


# ============================================================
# 7. CONTROLES DE QUALITE INITIAUX
# ============================================================

nombre_lignes_source = len(df)

nombre_doublons = int(
    df.duplicated(
        subset=COLONNES_CLES
    ).sum()
)

nombre_valeurs_manquantes = int(
    df[COLONNES_CLES + [colonne_nombre]]
    .isna()
    .sum()
    .sum()
)

nombre_valeurs_infinies = int(
    np.isinf(df[colonne_nombre]).sum()
)

regions = set(
    df["REGION"].dropna().unique()
)

annees = set(
    df["ANNEE_SCOLAIRE"].dropna().unique()
)

statuts = set(
    df["STATUT"].dropna().unique()
)

nombre_negatifs = int(
    (df[colonne_nombre] < 0).sum()
)

# Vérification des nombres entiers dans la source
valeurs_numeriques_valides = df[colonne_nombre].dropna()

effectifs_entiers_source = bool(
    (valeurs_numeriques_valides % 1 == 0).all()
)

print("\n========== CONTROLES INITIAUX ==========")
print(f"Nombre de régions : {len(regions)}")
print(f"Années scolaires : {sorted(annees)}")
print(f"Statuts détectés : {sorted(statuts)}")
print(f"Doublons : {nombre_doublons}")
print(f"Valeurs manquantes : {nombre_valeurs_manquantes}")
print(f"Valeurs infinies : {nombre_valeurs_infinies}")
print(f"Valeurs négatives : {nombre_negatifs}")
print(f"Effectifs entiers : {effectifs_entiers_source}")


# ============================================================
# 8. VALIDATION DES DONNEES AVANT TRANSFORMATION
# ============================================================

conditions_source = {
    "Nombre de lignes source": (
        nombre_lignes_source == NOMBRE_LIGNES_ATTENDU * 2
    ),
    "Nombre de régions": (
        len(regions) == NOMBRE_REGIONS_ATTENDU
    ),
    "Années scolaires attendues": (
        annees == ANNEES_ATTENDUES
    ),
    "Statuts attendus": (
        statuts == STATUTS_ATTENDUS
    ),
    "Absence de doublons": (
        nombre_doublons == 0
    ),
    "Absence de valeurs manquantes": (
        nombre_valeurs_manquantes == 0
    ),
    "Absence de valeurs infinies": (
        nombre_valeurs_infinies == 0
    ),
    "Absence de valeurs négatives": (
        nombre_negatifs == 0
    ),
    "Effectifs entiers": effectifs_entiers_source
}

if not all(conditions_source.values()):

    rapport_initial = {
        "Lignes source": nombre_lignes_source,
        "Régions détectées": len(regions),
        "Années détectées": len(annees),
        "Statuts détectés": len(statuts),
        "Doublons source": nombre_doublons,
        "Valeurs manquantes source": nombre_valeurs_manquantes,
        "Valeurs infinies source": nombre_valeurs_infinies,
        "Valeurs négatives source": nombre_negatifs,
        "Effectifs entiers": effectifs_entiers_source,
        "STATUT GLOBAL": "A_VERIFIER"
    }

    rapport = enregistrer_rapport(rapport_initial)

    print("\nCONTROLES DE LA SOURCE : ECHEC")

    for controle, resultat in conditions_source.items():
        print(f"{controle} : {resultat}")

    print(f"\nRapport enregistré : {FICHIER_RAPPORT}")

    raise ValueError(
        "Les contrôles initiaux ont échoué. "
        "La transformation est interrompue."
    )


# ============================================================
# 9. VERIFICATION DES COMBINAISONS ATTENDUES
# ============================================================

cles_attendues = {
    (region, annee, statut)
    for region in regions
    for annee in ANNEES_ATTENDUES
    for statut in STATUTS_ATTENDUS
}

cles_observees = set(
    df[COLONNES_CLES].itertuples(
        index=False,
        name=None
    )
)

cles_manquantes = cles_attendues - cles_observees
cles_supplementaires = cles_observees - cles_attendues

print("\n========== CONTROLE DE COMPLETUDE ==========")
print(f"Combinaisons attendues : {len(cles_attendues)}")
print(f"Combinaisons observées : {len(cles_observees)}")
print(f"Combinaisons manquantes : {len(cles_manquantes)}")
print(f"Combinaisons supplémentaires : {len(cles_supplementaires)}")

if cles_manquantes or cles_supplementaires:

    rapport_initial = {
        "Lignes source": nombre_lignes_source,
        "Combinaisons attendues": len(cles_attendues),
        "Combinaisons observées": len(cles_observees),
        "Combinaisons manquantes": len(cles_manquantes),
        "Combinaisons supplémentaires": len(cles_supplementaires),
        "STATUT GLOBAL": "A_VERIFIER"
    }

    enregistrer_rapport(rapport_initial)

    raise ValueError(
        "Le contrôle de complétude a échoué. "
        "La transformation est interrompue."
    )

print("Complétude : VALIDEE")


# ============================================================
# 10. TRANSFORMATION : SEPARATION PUBLIC / PRIVE
# ============================================================

df_ecoles = df[
    COLONNES_CLES + [colonne_nombre]
].copy()

table_ecoles = df_ecoles.pivot(
    index=["REGION", "ANNEE_SCOLAIRE"],
    columns="STATUT",
    values=colonne_nombre
).reset_index()

table_ecoles.columns.name = None

# Vérification de la présence des deux catégories
for statut in STATUTS_ATTENDUS:

    if statut not in table_ecoles.columns:
        raise ValueError(
            f"Le statut '{statut}' est absent après le pivot."
        )

# Renommage des colonnes
table_ecoles = table_ecoles.rename(
    columns={
        "PUBLIC": "NOMBRE_ECOLES_PUBLIC",
        "PRIVÉ": "NOMBRE_ECOLES_PRIVE"
    }
)

# Vérification des colonnes finales
colonnes_effectifs = [
    "NOMBRE_ECOLES_PUBLIC",
    "NOMBRE_ECOLES_PRIVE"
]

for colonne in colonnes_effectifs:

    if colonne not in table_ecoles.columns:
        raise ValueError(
            f"Colonne finale absente : {colonne}"
        )

# Calcul du nombre total d'écoles
table_ecoles["NOMBRE_ECOLES_TOTAL"] = (
    table_ecoles["NOMBRE_ECOLES_PUBLIC"]
    + table_ecoles["NOMBRE_ECOLES_PRIVE"]
)

# Différence entre le public et le privé
table_ecoles["ECART_PUBLIC_MOINS_PRIVE"] = (
    table_ecoles["NOMBRE_ECOLES_PUBLIC"]
    - table_ecoles["NOMBRE_ECOLES_PRIVE"]
)

# Vérification du dénominateur avant calcul des parts
if (table_ecoles["NOMBRE_ECOLES_TOTAL"] <= 0).any():
    raise ValueError(
        "Au moins une région présente un total d'écoles nul ou négatif. "
        "Le calcul des parts est impossible."
    )

# Part des écoles publiques
table_ecoles["PART_PUBLIC_POURCENT"] = (
    table_ecoles["NOMBRE_ECOLES_PUBLIC"]
    / table_ecoles["NOMBRE_ECOLES_TOTAL"]
    * 100
)

# Part des écoles privées
table_ecoles["PART_PRIVE_POURCENT"] = (
    table_ecoles["NOMBRE_ECOLES_PRIVE"]
    / table_ecoles["NOMBRE_ECOLES_TOTAL"]
    * 100
)

# Organisation du tableau
table_ecoles = table_ecoles.sort_values(
    by=["ANNEE_SCOLAIRE", "REGION"]
).reset_index(drop=True)


# ============================================================
# 11. VALIDATION DE LA TABLE ANALYTIQUE
# ============================================================

nombre_lignes_final = len(table_ecoles)

nombre_doublons_final = int(
    table_ecoles.duplicated(
        subset=["REGION", "ANNEE_SCOLAIRE"]
    ).sum()
)

colonnes_numeriques_finales = [
    "NOMBRE_ECOLES_PUBLIC",
    "NOMBRE_ECOLES_PRIVE",
    "NOMBRE_ECOLES_TOTAL",
    "ECART_PUBLIC_MOINS_PRIVE",
    "PART_PUBLIC_POURCENT",
    "PART_PRIVE_POURCENT"
]

nombre_valeurs_manquantes_final = int(
    table_ecoles[
        ["REGION", "ANNEE_SCOLAIRE"]
        + colonnes_numeriques_finales
    ].isna().sum().sum()
)

valeurs_infinies_finales = int(
    np.isinf(
        table_ecoles[
            colonnes_numeriques_finales
        ].to_numpy(dtype=float)
    ).sum()
)

# Vérification des valeurs négatives
nombre_negatifs_final = int(
    (
        table_ecoles[
            [
                "NOMBRE_ECOLES_PUBLIC",
                "NOMBRE_ECOLES_PRIVE",
                "NOMBRE_ECOLES_TOTAL"
            ]
        ] < 0
    ).sum().sum()
)

# Vérification de la somme des parts
somme_parts = (
    table_ecoles["PART_PUBLIC_POURCENT"]
    + table_ecoles["PART_PRIVE_POURCENT"]
)

parts_valides = bool(
    np.isclose(
        somme_parts.to_numpy(),
        100.0,
        atol=0.001
    ).all()
)

# Vérification des nombres entiers
effectifs_entiers_final = bool(
    (
        table_ecoles[
            [
                "NOMBRE_ECOLES_PUBLIC",
                "NOMBRE_ECOLES_PRIVE",
                "NOMBRE_ECOLES_TOTAL"
            ]
        ] % 1 == 0
    ).all().all()
)

# Vérification du calcul du total
total_calcule = (
    table_ecoles["NOMBRE_ECOLES_PUBLIC"]
    + table_ecoles["NOMBRE_ECOLES_PRIVE"]
)

total_coherent = bool(
    np.array_equal(
        table_ecoles["NOMBRE_ECOLES_TOTAL"].to_numpy(),
        total_calcule.to_numpy()
    )
)

# Vérification de l'écart public - privé
ecart_calcule = (
    table_ecoles["NOMBRE_ECOLES_PUBLIC"]
    - table_ecoles["NOMBRE_ECOLES_PRIVE"]
)

ecart_coherent = bool(
    np.array_equal(
        table_ecoles["ECART_PUBLIC_MOINS_PRIVE"].to_numpy(),
        ecart_calcule.to_numpy()
    )
)


# ============================================================
# 12. BILAN GLOBAL DE VALIDATION
# ============================================================

conditions_valides = [
    nombre_lignes_source == NOMBRE_LIGNES_ATTENDU * 2,
    len(regions) == NOMBRE_REGIONS_ATTENDU,
    annees == ANNEES_ATTENDUES,
    statuts == STATUTS_ATTENDUS,
    nombre_doublons == 0,
    nombre_valeurs_manquantes == 0,
    nombre_valeurs_infinies == 0,
    nombre_negatifs == 0,
    effectifs_entiers_source,
    len(cles_manquantes) == 0,
    len(cles_supplementaires) == 0,
    nombre_lignes_final == NOMBRE_LIGNES_ATTENDU,
    nombre_doublons_final == 0,
    nombre_valeurs_manquantes_final == 0,
    valeurs_infinies_finales == 0,
    nombre_negatifs_final == 0,
    parts_valides,
    effectifs_entiers_final,
    total_coherent,
    ecart_coherent
]

statut_global = (
    "VALIDE"
    if all(conditions_valides)
    else "A_VERIFIER"
)


# ============================================================
# 13. GENERATION DU RAPPORT DE QUALITE
# ============================================================

resultats_controles = {
    "Lignes source": nombre_lignes_source,
    "Régions détectées": len(regions),
    "Années scolaires détectées": len(annees),
    "Statuts détectés": len(statuts),
    "Doublons source": nombre_doublons,
    "Valeurs manquantes source": nombre_valeurs_manquantes,
    "Valeurs infinies source": nombre_valeurs_infinies,
    "Valeurs négatives source": nombre_negatifs,
    "Effectifs entiers source": effectifs_entiers_source,
    "Combinaisons attendues": len(cles_attendues),
    "Combinaisons observées": len(cles_observees),
    "Combinaisons manquantes": len(cles_manquantes),
    "Combinaisons supplémentaires": len(cles_supplementaires),
    "Lignes finales": nombre_lignes_final,
    "Doublons finaux": nombre_doublons_final,
    "Valeurs manquantes finales": nombre_valeurs_manquantes_final,
    "Valeurs infinies finales": valeurs_infinies_finales,
    "Valeurs négatives finales": nombre_negatifs_final,
    "Parts totalisant 100 %": parts_valides,
    "Effectifs entiers finaux": effectifs_entiers_final,
    "Cohérence du nombre total": total_coherent,
    "Cohérence de l'écart public-privé": ecart_coherent,
    "STATUT GLOBAL": statut_global
}

rapport = enregistrer_rapport(resultats_controles)


# ============================================================
# 14. EXPORTATION DE LA TABLE SI VALIDEE
# ============================================================

if statut_global == "VALIDE":

    table_ecoles.to_csv(
        FICHIER_SORTIE,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nTable analytique enregistrée :")
    print(FICHIER_SORTIE)

else:

    print(
        "\nATTENTION : la table analytique n'a pas été exportée "
        "car certains contrôles ne sont pas validés."
    )


# ============================================================
# 15. AFFICHAGE DU BILAN FINAL
# ============================================================

print("\n========== TABLE ANALYTIQUE DES ECOLES ==========")

if statut_global == "VALIDE":
    print(
        table_ecoles.head(10).to_string(index=False)
    )

print("\n========== BILAN DE VALIDATION ==========")
print(
    rapport.to_string(index=False)
)

print("\n========== FICHIERS GENERES ==========")
print(f"Rapport qualité : {FICHIER_RAPPORT}")

if statut_global == "VALIDE":
    print(f"Table analytique : {FICHIER_SORTIE}")

print("\n" + "=" * 70)
print(f"STATUT FINAL : {statut_global}")
print("=" * 70)

if statut_global != "VALIDE":
    raise ValueError(
        "La validation finale a échoué. "
        "Consulte le rapport de qualité."
    )
