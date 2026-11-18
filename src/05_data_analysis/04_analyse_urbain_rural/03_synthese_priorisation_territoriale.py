
from pathlib import Path
import unicodedata

import pandas as pd
import matplotlib.pyplot as plt


# ==================================================
# 1. CHEMINS DU PROJET
# ==================================================

RACINE_PROJET = Path(__file__).resolve().parents[3]

FICHIER_DGESS = (
    RACINE_PROJET
    / "outputs"
    / "analyses"
    / "03_analyse_disparites_regionales"
    / "moyennes_indicateurs_par_region.csv"
)

FICHIER_INSD = (
    RACINE_PROJET
    / "outputs"
    / "analyses"
    / "04_analyse_urbain_rural"
    / "insd_rgph_2019"
    / "situation_scolaire_6_11_ans_par_region.csv"
)

DOSSIER_SORTIE = (
    RACINE_PROJET
    / "outputs"
    / "analyses"
    / "04_analyse_urbain_rural"
    / "synthese_priorisation"
)

DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. FONCTIONS UTILITAIRES
# ==================================================

def normaliser_region(valeur):

    texte = str(valeur).strip().upper()

    texte = unicodedata.normalize("NFKD", texte)

    texte = "".join(
        caractere
        for caractere in texte
        if not unicodedata.combining(caractere)
    )

    return " ".join(texte.split())


def trouver_colonne(df, candidats, nom_logique):

    for colonne in candidats:

        if colonne in df.columns:
            return colonne

    raise ValueError(
        f"Colonne introuvable pour {nom_logique}. "
        f"Colonnes disponibles : {list(df.columns)}"
    )


# ==================================================
# 3. CHARGEMENT DES DONNEES
# ==================================================

if not FICHIER_DGESS.exists():

    raise FileNotFoundError(
        f"Fichier DGESS introuvable : {FICHIER_DGESS}"
    )

if not FICHIER_INSD.exists():

    raise FileNotFoundError(
        f"Fichier INSD introuvable : {FICHIER_INSD}"
    )


dgess = pd.read_csv(FICHIER_DGESS)

insd = pd.read_csv(FICHIER_INSD)


print("==========================================")
print("CHARGEMENT DES DONNEES")
print("==========================================")

print("DGESS :", dgess.shape)
print("INSD :", insd.shape)

print("\nColonnes DGESS :")
print(dgess.columns.tolist())

print("\nColonnes INSD :")
print(insd.columns.tolist())


# ==================================================
# 4. IDENTIFICATION DES COLONNES
# ==================================================

col_region_dgess = trouver_colonne(
    dgess,
    ["REGION"],
    "Region DGESS"
)

col_region_insd = trouver_colonne(
    insd,
    ["REGION"],
    "Region INSD"
)

col_tba = trouver_colonne(
    dgess,
    ["TBA", "TBA_MOYEN", "TBA_MOYENNE"],
    "TBA DGESS"
)

col_tbs = trouver_colonne(
    dgess,
    ["TBS", "TBS_MOYEN", "TBS_MOYENNE"],
    "TBS DGESS"
)

col_tap = trouver_colonne(
    dgess,
    ["TAP", "TAP_MOYEN", "TAP_MOYENNE"],
    "TAP DGESS"
)

col_scolarise = trouver_colonne(
    insd,
    ["SCOLARISE_PCT"],
    "Proportion scolarisee INSD"
)

col_descolarise = trouver_colonne(
    insd,
    ["DESCOLARISE_PCT"],
    "Proportion descolarisee INSD"
)

col_jamais = trouver_colonne(
    insd,
    ["JAMAIS_FREQUENTE_PCT"],
    "Proportion jamais frequente INSD"
)


# ==================================================
# 5. PREPARATION DES TABLEAUX
# ==================================================

dgess_selection = dgess[
    [
        col_region_dgess,
        col_tba,
        col_tbs,
        col_tap
    ]
].copy()

dgess_selection.columns = [
    "REGION",
    "TBA_DGESS",
    "TBS_DGESS",
    "TAP_DGESS"
]


insd_selection = insd[
    [
        col_region_insd,
        col_scolarise,
        col_descolarise,
        col_jamais
    ]
].copy()

insd_selection.columns = [
    "REGION",
    "SCOLARISE_INSD_PCT",
    "DESCOLARISE_INSD_PCT",
    "JAMAIS_FREQUENTE_INSD_PCT"
]


# Exclusion de la ligne nationale
insd_selection = insd_selection[
    insd_selection["REGION"].str.strip().str.upper()
    != "BURKINA FASO"
].copy()


# Normalisation des regions
dgess_selection["REGION_CLE"] = (
    dgess_selection["REGION"].apply(normaliser_region)
)

insd_selection["REGION_CLE"] = (
    insd_selection["REGION"].apply(normaliser_region)
)


# Conversion numerique
colonnes_dgess = [
    "TBA_DGESS",
    "TBS_DGESS",
    "TAP_DGESS"
]

colonnes_insd = [
    "SCOLARISE_INSD_PCT",
    "DESCOLARISE_INSD_PCT",
    "JAMAIS_FREQUENTE_INSD_PCT"
]

for colonne in colonnes_dgess:

    dgess_selection[colonne] = pd.to_numeric(
        dgess_selection[colonne],
        errors="raise"
    )

for colonne in colonnes_insd:

    insd_selection[colonne] = pd.to_numeric(
        insd_selection[colonne],
        errors="raise"
    )


# ==================================================
# 6. CONTROLE DES DONNEES
# ==================================================

assert dgess_selection["REGION_CLE"].notna().all()

assert insd_selection["REGION_CLE"].notna().all()

assert not dgess_selection["REGION_CLE"].duplicated().any(), (
    "Doublons regionaux detectes dans DGESS."
)

assert not insd_selection["REGION_CLE"].duplicated().any(), (
    "Doublons regionaux detectes dans INSD."
)

assert dgess_selection[colonnes_dgess].notna().all().all()

assert insd_selection[colonnes_insd].notna().all().all()

assert insd_selection[colonnes_insd].ge(0).all().all()

assert insd_selection[colonnes_insd].le(100).all().all()


regions_dgess = set(dgess_selection["REGION_CLE"])

regions_insd = set(insd_selection["REGION_CLE"])


print("\n==========================================")
print("CONTROLE DES REGIONS")
print("==========================================")

print("Regions DGESS :", len(regions_dgess))

print("Regions INSD :", len(regions_insd))

print(
    "Regions absentes de DGESS :",
    sorted(regions_insd - regions_dgess)
)

print(
    "Regions absentes de INSD :",
    sorted(regions_dgess - regions_insd)
)


assert regions_dgess == regions_insd, (
    "Les regions des deux sources ne correspondent pas."
)


# ==================================================
# 7. FUSION DES DEUX SOURCES
# ==================================================

synthese = pd.merge(
    dgess_selection,
    insd_selection.drop(columns=["REGION"]),
    on="REGION_CLE",
    how="inner",
    validate="one_to_one"
)


assert len(synthese) == 13, (
    "Le nombre de regions fusionnees est different de 13."
)


synthese = synthese.drop(
    columns=["REGION_CLE"]
)

synthese = synthese.sort_values(
    "REGION"
).reset_index(drop=True)


print("\n==========================================")
print("SYNTHESE DGESS + INSD")
print("==========================================")

print(
    synthese.round(2).to_string(index=False)
)


# ==================================================
# 8. CLASSEMENTS PAR INDICATEUR
# ==================================================

# Rang 1 = situation la moins favorable

synthese["RANG_DGESS_TAP"] = (
    synthese["TAP_DGESS"]
    .rank(method="min", ascending=True)
    .astype(int)
)

synthese["RANG_INSD_SCOLARISATION"] = (
    synthese["SCOLARISE_INSD_PCT"]
    .rank(method="min", ascending=True)
    .astype(int)
)

synthese["RANG_INSD_JAMAIS_FREQUENTE"] = (
    synthese["JAMAIS_FREQUENTE_INSD_PCT"]
    .rank(method="min", ascending=False)
    .astype(int)
)


# Identification des signaux defavorables

synthese["SIGNAL_DGESS_TAP"] = (
    synthese["RANG_DGESS_TAP"] <= 3
)

synthese["SIGNAL_INSD_SCOLARISATION"] = (
    synthese["RANG_INSD_SCOLARISATION"] <= 3
)

synthese["CONVERGENCE_SIGNAUX"] = (
    synthese["SIGNAL_DGESS_TAP"]
    & synthese["SIGNAL_INSD_SCOLARISATION"]
)


# ==================================================
# 9. CLASSIFICATION TERRITORIALE
# ==================================================

def classer_region(ligne):

    rang_dgess = ligne["RANG_DGESS_TAP"]

    rang_insd = ligne["RANG_INSD_SCOLARISATION"]

    # Niveau 1 : convergence des trois situations les plus defavorables
    if rang_dgess <= 3 and rang_insd <= 3:

        return "VIGILANCE ELEVEE"

    # Niveau 2 : convergence parmi les cinq situations les plus defavorables
    if rang_dgess <= 5 and rang_insd <= 5:

        return "ATTENTION RENFORCEE"

    # Niveau 3 : surveillance reguliere
    return "SURVEILLANCE"


synthese["NIVEAU_VIGILANCE"] = synthese.apply(
    classer_region,
    axis=1
)


# ==================================================
# 10. PISTES D'INTERVENTION
# ==================================================

# Seuil exploratoire correspondant aux cinq TAP les plus faibles

seuil_tap = synthese["TAP_DGESS"].nsmallest(5).max()


def proposer_piste(ligne):

    pistes = []

    if ligne["JAMAIS_FREQUENTE_INSD_PCT"] >= 40:

        pistes.append(
            "Etudier les obstacles a la premiere scolarisation"
        )

    if ligne["DESCOLARISE_INSD_PCT"] >= 12:

        pistes.append(
            "Examiner les facteurs associes a la descolarisation"
        )

    if ligne["TAP_DGESS"] <= seuil_tap:

        pistes.append(
            "Analyser les obstacles a l'achevement du primaire"
        )

    if not pistes:

        pistes.append(
            "Maintenir le suivi des indicateurs scolaires"
        )

    return " ; ".join(pistes)


synthese["PISTES_INTERVENTION"] = synthese.apply(
    proposer_piste,
    axis=1
)


# ==================================================
# 11. EXPORT DE LA SYNTHESE
# ==================================================

fichier_synthese = (
    DOSSIER_SORTIE
    / "synthese_regionale_dgess_insd.csv"
)

synthese.to_csv(
    fichier_synthese,
    index=False,
    encoding="utf-8-sig"
)


# Classement final
ordre_niveaux = {
    "VIGILANCE ELEVEE": 1,
    "ATTENTION RENFORCEE": 2,
    "SURVEILLANCE": 3
}

synthese["ORDRE_VIGILANCE"] = (
    synthese["NIVEAU_VIGILANCE"]
    .map(ordre_niveaux)
)

classement = synthese.sort_values(
    [
        "ORDRE_VIGILANCE",
        "RANG_DGESS_TAP",
        "RANG_INSD_SCOLARISATION"
    ]
)

classement = classement.drop(
    columns=["ORDRE_VIGILANCE"]
)

classement.to_csv(
    DOSSIER_SORTIE / "priorisation_territoriale.csv",
    index=False,
    encoding="utf-8-sig"
)


# ==================================================
# 12. AFFICHAGE DE LA PRIORISATION
# ==================================================

print("\n==========================================")
print("PRIORISATION TERRITORIALE")
print("==========================================")

colonnes_affichage = [
    "REGION",
    "TAP_DGESS",
    "SCOLARISE_INSD_PCT",
    "JAMAIS_FREQUENTE_INSD_PCT",
    "RANG_DGESS_TAP",
    "RANG_INSD_SCOLARISATION",
    "NIVEAU_VIGILANCE"
]

print(
    classement[colonnes_affichage]
    .round(2)
    .to_string(index=False)
)


# ==================================================
# 13. REPARTITION DES NIVEAUX DE VIGILANCE
# ==================================================

ordre_vigilance = [
    "VIGILANCE ELEVEE",
    "ATTENTION RENFORCEE",
    "SURVEILLANCE"
]

print("\n==========================================")
print("REPARTITION DES NIVEAUX DE VIGILANCE")
print("==========================================")

repartition = (
    synthese["NIVEAU_VIGILANCE"]
    .value_counts()
    .reindex(ordre_vigilance, fill_value=0)
)

print(repartition.to_string())


# Export de la repartition
repartition.to_csv(
    DOSSIER_SORTIE / "repartition_niveaux_vigilance.csv",
    header=["NOMBRE_REGIONS"],
    encoding="utf-8-sig"
)


# ==================================================
# 14. PISTES D'INTERVENTION
# ==================================================

print("\n==========================================")
print("PISTES D'INTERVENTION")
print("==========================================")


for _, ligne in classement.iterrows():

    print(
        f"\n{ligne['REGION']} : "
        f"{ligne['NIVEAU_VIGILANCE']}"
    )

    print(ligne["PISTES_INTERVENTION"])


# ==================================================
# 15. GRAPHIQUE : COMPARAISON DGESS ET INSD
# ==================================================

plt.figure(figsize=(12, 8))

for _, ligne in synthese.iterrows():

    plt.scatter(
        ligne["SCOLARISE_INSD_PCT"],
        ligne["TAP_DGESS"]
    )

    plt.annotate(
        ligne["REGION"],
        (
            ligne["SCOLARISE_INSD_PCT"],
            ligne["TAP_DGESS"]
        ),
        fontsize=8,
        xytext=(4, 4),
        textcoords="offset points"
    )


plt.xlabel(
    "Proportion scolarisee INSD 2019 (%)"
)

plt.ylabel(
    "TAP moyen DGESS 2015-2025"
)

plt.title(
    "Comparaison regionale : TAP DGESS et scolarisation INSD"
)

plt.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    DOSSIER_SORTIE / "01_comparaison_tap_insd.png",
    dpi=300
)

plt.close()


# ==================================================
# 16. GRAPHIQUE : PRIORISATION REGIONALE
# ==================================================

ordre = synthese.sort_values(
    "SCOLARISE_INSD_PCT",
    ascending=True
)

plt.figure(figsize=(12, 8))

plt.barh(
    ordre["REGION"],
    ordre["SCOLARISE_INSD_PCT"]
)

plt.xlabel(
    "Proportion scolarisee INSD (%)"
)

plt.ylabel("Region")

plt.title(
    "Situation de scolarisation des enfants de 6-11 ans par region"
)

plt.grid(
    axis="x",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    DOSSIER_SORTIE / "02_priorisation_regions_insd.png",
    dpi=300
)

plt.close()


# ==================================================
# 17. GRAPHIQUE : NIVEAUX DE VIGILANCE
# ==================================================

plt.figure(figsize=(9, 6))

repartition_graphique = repartition[
    repartition > 0
]

plt.bar(
    repartition_graphique.index,
    repartition_graphique.values
)

plt.title(
    "Repartition des regions par niveau de vigilance"
)

plt.xlabel("Niveau de vigilance")

plt.ylabel("Nombre de regions")

plt.xticks(rotation=15)

plt.grid(
    axis="y",
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    DOSSIER_SORTIE / "03_repartition_niveaux_vigilance.png",
    dpi=300
)

plt.close()


# ==================================================
# 18. FIN DE L'ANALYSE
# ==================================================

print("\n==========================================")
print("SYNTHESE TERRITORIALE TERMINEE")
print("==========================================")

print("Nombre de regions analysees :", len(synthese))

print("Nombre de fichiers CSV generes : 3")

print("Nombre de graphiques generes : 3")

print(
    "Dossier des resultats :",
    DOSSIER_SORTIE
)
