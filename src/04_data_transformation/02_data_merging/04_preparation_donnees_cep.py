
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
    / "taux_reussite_cep_region_sexe_long.csv"
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

FICHIER_SORTIE = DOSSIER_SORTIE / "resultats_cep_regionaux_sexe.csv"
FICHIER_RAPPORT = DOSSIER_RAPPORTS / "rapport_preparation_cep.csv"


# ============================================================
# 2. PARAMETRES DE VALIDATION
# ============================================================

ANNEES_ATTENDUES = {
    str(annee) for annee in range(2016, 2026)
}

SEXES_ATTENDUS = {"FILLES", "GARCONS"}

NOMBRE_REGIONS_ATTENDU = 13
NOMBRE_LIGNES_ATTENDU = 130

COLONNES_CLES = [
    "REGION",
    "ANNEE_CIVILE",
    "SEXE"
]


# ============================================================
# 3. VERIFICATION ET CHARGEMENT DU FICHIER
# ============================================================

print("=" * 70)
print("PREPARATION DES RESULTATS DU CEP PAR REGION ET PAR SEXE")
print("=" * 70)

if not FICHIER_SOURCE.exists():
    raise FileNotFoundError(
        f"Fichier source introuvable : {FICHIER_SOURCE}"
    )

DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)
DOSSIER_RAPPORTS.mkdir(parents=True, exist_ok=True)

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
# 4. VERIFICATION DES COLONNES OBLIGATOIRES
# ============================================================

for colonne in COLONNES_CLES:
    if colonne not in df.columns:
        raise ValueError(
            f"La colonne obligatoire '{colonne}' est absente."
        )

# Normalisation des variables de regroupement
df["REGION"] = (
    df["REGION"]
    .astype("string")
    .str.strip()
    .str.upper()
)

df["ANNEE_CIVILE"] = (
    df["ANNEE_CIVILE"]
    .astype("string")
    .str.strip()
)

df["SEXE"] = (
    df["SEXE"]
    .astype("string")
    .str.strip()
    .str.upper()
)


# ============================================================
# 5. IDENTIFICATION DE LA COLONNE DU TAUX DE REUSSITE
# ============================================================

colonnes_possibles = [
    "TAUX_REUSSITE",
    "TAUX_REUSSITE_CEP",
    "TAUX_REUSSITE_CEP_POURCENT",
    "TAUX"
]

colonne_taux = next(
    (
        colonne
        for colonne in colonnes_possibles
        if colonne in df.columns
    ),
    None
)

if colonne_taux is None:

    colonnes_numeriques = [
        colonne
        for colonne in df.select_dtypes(include="number").columns
        if colonne not in COLONNES_CLES
    ]

    if len(colonnes_numeriques) == 1:
        colonne_taux = colonnes_numeriques[0]

    else:
        raise ValueError(
            "Impossible d'identifier automatiquement la colonne du taux. "
            f"Colonnes numériques détectées : {colonnes_numeriques}. "
            "Vérifie le fichier source."
        )

print(f"\nColonne du taux identifiée : {colonne_taux}")

df[colonne_taux] = pd.to_numeric(
    df[colonne_taux],
    errors="coerce"
)


# ============================================================
# 6. CONTROLES DE QUALITE INITIAUX
# ============================================================

nombre_lignes_source = len(df)

nombre_doublons = int(
    df.duplicated(
        subset=COLONNES_CLES
    ).sum()
)

nombre_valeurs_manquantes = int(
    df[COLONNES_CLES + [colonne_taux]]
    .isna()
    .sum()
    .sum()
)

valeurs_infinies = int(
    np.isinf(df[colonne_taux]).sum()
)

regions = set(
    df["REGION"].dropna().unique()
)

annees = set(
    df["ANNEE_CIVILE"].dropna().unique()
)

sexes = set(
    df["SEXE"].dropna().unique()
)

print("\n========== CONTROLES INITIAUX ==========")
print(f"Nombre de régions : {len(regions)}")
print(f"Années détectées : {sorted(annees)}")
print(f"Catégories de sexe : {sorted(sexes)}")
print(f"Doublons : {nombre_doublons}")
print(f"Valeurs manquantes : {nombre_valeurs_manquantes}")
print(f"Valeurs infinies : {valeurs_infinies}")


# ============================================================
# 7. VERIFICATION DES DONNEES AVANT TRANSFORMATION
# ============================================================

if nombre_valeurs_manquantes > 0:
    raise ValueError(
        "Des valeurs manquantes sont présentes dans les colonnes "
        "nécessaires à la transformation."
    )

if valeurs_infinies > 0:
    raise ValueError(
        f"Le fichier contient {valeurs_infinies} valeurs infinies."
    )

if nombre_doublons > 0:
    raise ValueError(
        f"Le fichier contient {nombre_doublons} doublons "
        "sur les clés REGION, ANNEE_CIVILE et SEXE. "
        "La transformation est interrompue."
    )

if len(regions) != NOMBRE_REGIONS_ATTENDU:
    raise ValueError(
        f"Nombre de régions incorrect : {len(regions)} "
        f"au lieu de {NOMBRE_REGIONS_ATTENDU}."
    )

if annees != ANNEES_ATTENDUES:
    raise ValueError(
        "Les années détectées ne correspondent pas "
        "aux années attendues de 2016 à 2025."
    )

if sexes != SEXES_ATTENDUS:
    raise ValueError(
        f"Catégories de sexe incorrectes : {sorted(sexes)}."
    )


# ============================================================
# 8. VERIFICATION DES COMBINAISONS ATTENDUES
# ============================================================

cles_attendues = {
    (region, annee, sexe)
    for region in regions
    for annee in ANNEES_ATTENDUES
    for sexe in SEXES_ATTENDUS
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

if len(cles_manquantes) > 0:
    print("Exemples de combinaisons manquantes :")
    print(list(cles_manquantes)[:10])

if len(cles_supplementaires) > 0:
    print("Exemples de combinaisons supplémentaires :")
    print(list(cles_supplementaires)[:10])

if cles_manquantes or cles_supplementaires:
    raise ValueError(
        "Le contrôle de complétude a échoué. "
        "La transformation est interrompue."
    )

print("Complétude : VALIDEE")


# ============================================================
# 9. VERIFICATION DE L'ECHELLE DES TAUX
# ============================================================

taux_min = df[colonne_taux].min()
taux_max = df[colonne_taux].max()

echelle_valide = (
    pd.notna(taux_min)
    and pd.notna(taux_max)
    and taux_min >= 0
    and taux_max <= 100
)

print("\n========== CONTROLE DE L'ECHELLE ==========")
print(f"Taux minimum : {taux_min}")
print(f"Taux maximum : {taux_max}")
print(f"Echelle comprise entre 0 et 100 : {echelle_valide}")

if not echelle_valide:
    raise ValueError(
        "Les taux de réussite ne respectent pas l'échelle "
        "attendue de 0 à 100. Vérifie leur unité dans la source."
    )


# ============================================================
# 10. TRANSFORMATION : TABLEAU CROISE FILLES / GARCONS
# ============================================================

df_cep = df[
    COLONNES_CLES + [colonne_taux]
].copy()

table_cep = df_cep.pivot(
    index=["REGION", "ANNEE_CIVILE"],
    columns="SEXE",
    values=colonne_taux
).reset_index()

table_cep.columns.name = None

# Renommage des colonnes des deux sexes
table_cep = table_cep.rename(
    columns={
        "FILLES": "TAUX_FILLES",
        "GARCONS": "TAUX_GARCONS"
    }
)

colonnes_taux_finales = [
    "TAUX_FILLES",
    "TAUX_GARCONS"
]

for colonne in colonnes_taux_finales:
    if colonne not in table_cep.columns:
        raise ValueError(
            f"La colonne attendue '{colonne}' est absente après pivot."
        )

# Calcul de l'écart entre les deux sexes
table_cep["ECART_FILLES_MOINS_GARCONS"] = (
    table_cep["TAUX_FILLES"]
    - table_cep["TAUX_GARCONS"]
)

table_cep["ECART_ABSOLU"] = (
    table_cep["ECART_FILLES_MOINS_GARCONS"].abs()
)

# Organisation du tableau
table_cep = table_cep.sort_values(
    by=["ANNEE_CIVILE", "REGION"]
).reset_index(drop=True)


# ============================================================
# 11. VALIDATION DE LA TABLE ANALYTIQUE
# ============================================================

nombre_lignes_final = len(table_cep)

nombre_doublons_final = int(
    table_cep.duplicated(
        subset=["REGION", "ANNEE_CIVILE"]
    ).sum()
)

colonnes_controle_final = [
    "REGION",
    "ANNEE_CIVILE",
    "TAUX_FILLES",
    "TAUX_GARCONS",
    "ECART_FILLES_MOINS_GARCONS",
    "ECART_ABSOLU"
]

nombre_manquants_final = int(
    table_cep[colonnes_controle_final]
    .isna()
    .sum()
    .sum()
)

colonnes_numeriques_finales = [
    "TAUX_FILLES",
    "TAUX_GARCONS",
    "ECART_FILLES_MOINS_GARCONS",
    "ECART_ABSOLU"
]

valeurs_infinies_finales = int(
    np.isinf(
        table_cep[colonnes_numeriques_finales]
        .to_numpy(dtype=float)
    ).sum()
)

# Vérification de la cohérence du calcul des écarts
ecarts_calcules = (
    table_cep["TAUX_FILLES"]
    - table_cep["TAUX_GARCONS"]
)

controle_ecarts = bool(
    np.allclose(
        table_cep["ECART_FILLES_MOINS_GARCONS"],
        ecarts_calcules,
        equal_nan=False
    )
)

controle_ecarts_absolus = bool(
    np.allclose(
        table_cep["ECART_ABSOLU"],
        table_cep["ECART_FILLES_MOINS_GARCONS"].abs(),
        equal_nan=False
    )
)

conditions_valides = [
    nombre_lignes_source == NOMBRE_LIGNES_ATTENDU * 2,
    len(regions) == NOMBRE_REGIONS_ATTENDU,
    annees == ANNEES_ATTENDUES,
    sexes == SEXES_ATTENDUS,
    nombre_doublons == 0,
    nombre_valeurs_manquantes == 0,
    valeurs_infinies == 0,
    len(cles_manquantes) == 0,
    len(cles_supplementaires) == 0,
    nombre_lignes_final == NOMBRE_LIGNES_ATTENDU,
    nombre_doublons_final == 0,
    nombre_manquants_final == 0,
    valeurs_infinies_finales == 0,
    echelle_valide,
    controle_ecarts,
    controle_ecarts_absolus
]

statut = (
    "VALIDE"
    if all(conditions_valides)
    else "A_VERIFIER"
)


# ============================================================
# 12. GENERATION DU RAPPORT DE QUALITE
# ============================================================

rapport = pd.DataFrame([
    {
        "CONTROLE": "Lignes source",
        "RESULTAT": nombre_lignes_source
    },
    {
        "CONTROLE": "Régions détectées",
        "RESULTAT": len(regions)
    },
    {
        "CONTROLE": "Années détectées",
        "RESULTAT": len(annees)
    },
    {
        "CONTROLE": "Catégories de sexe",
        "RESULTAT": len(sexes)
    },
    {
        "CONTROLE": "Doublons source",
        "RESULTAT": nombre_doublons
    },
    {
        "CONTROLE": "Valeurs manquantes source",
        "RESULTAT": nombre_valeurs_manquantes
    },
    {
        "CONTROLE": "Valeurs infinies source",
        "RESULTAT": valeurs_infinies
    },
    {
        "CONTROLE": "Combinaisons manquantes",
        "RESULTAT": len(cles_manquantes)
    },
    {
        "CONTROLE": "Combinaisons supplémentaires",
        "RESULTAT": len(cles_supplementaires)
    },
    {
        "CONTROLE": "Lignes de la table finale",
        "RESULTAT": nombre_lignes_final
    },
    {
        "CONTROLE": "Doublons table finale",
        "RESULTAT": nombre_doublons_final
    },
    {
        "CONTROLE": "Valeurs manquantes table finale",
        "RESULTAT": nombre_manquants_final
    },
    {
        "CONTROLE": "Valeurs infinies table finale",
        "RESULTAT": valeurs_infinies_finales
    },
    {
        "CONTROLE": "Taux minimum",
        "RESULTAT": taux_min
    },
    {
        "CONTROLE": "Taux maximum",
        "RESULTAT": taux_max
    },
    {
        "CONTROLE": "Echelle comprise entre 0 et 100",
        "RESULTAT": echelle_valide
    },
    {
        "CONTROLE": "Cohérence des écarts",
        "RESULTAT": controle_ecarts
    },
    {
        "CONTROLE": "Cohérence des écarts absolus",
        "RESULTAT": controle_ecarts_absolus
    },
    {
        "CONTROLE": "STATUT GLOBAL",
        "RESULTAT": statut
    }
])


# ============================================================
# 13. EXPORTATION DES RESULTATS SI VALIDES
# ============================================================

if statut == "VALIDE":

    table_cep.to_csv(
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

# Le rapport est enregistré même si le résultat est invalide.
rapport.to_csv(
    FICHIER_RAPPORT,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 14. AFFICHAGE DU BILAN FINAL
# ============================================================

print("\n========== TABLE ANALYTIQUE CEP ==========")

if statut == "VALIDE":
    print(
        table_cep.head(10).to_string(index=False)
    )

print("\n========== BILAN DE VALIDATION ==========")
print(
    rapport.to_string(index=False)
)

print("\n========== FICHIERS GENERES ==========")
print(f"Rapport qualité : {FICHIER_RAPPORT}")

if statut == "VALIDE":
    print(f"Table analytique : {FICHIER_SORTIE}")

print("\n" + "=" * 70)
print(f"STATUT FINAL : {statut}")
print("=" * 70)

if statut != "VALIDE":
    raise ValueError(
        "La validation finale a échoué. "
        "Consulte le rapport de qualité."
    )
