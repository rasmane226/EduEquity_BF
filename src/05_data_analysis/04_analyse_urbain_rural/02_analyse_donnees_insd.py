
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# 1. Chemins du projet
# --------------------------------------------------

RACINE_PROJET = Path(__file__).resolve().parents[3]

FICHIER_ENTREE = (
    RACINE_PROJET
    / "data"
    / "02_donnees_complementaires"
    / "donnees_scolarisation_insd_rgph_2019.csv"
)

DOSSIER_SORTIE = (
    RACINE_PROJET
    / "outputs"
    / "analyses"
    / "04_analyse_urbain_rural"
    / "insd_rgph_2019"
)

DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Chargement des donnees
# --------------------------------------------------

df = pd.read_csv(FICHIER_ENTREE)

colonnes_requises = [
    "TABLE_SOURCE",
    "REGION",
    "GROUPE_AGE",
    "MILIEU_RESIDENCE",
    "SEXE",
    "STATUT_SCOLAIRE",
    "PROPORTION_PCT",
    "EFFECTIF_REFERENCE"
]

assert all(col in df.columns for col in colonnes_requises), (
    "Certaines colonnes requises sont absentes."
)

print("=== STRUCTURE DES DONNEES ===")
print("Nombre de lignes :", len(df))
print("Nombre de colonnes :", len(df.columns))
print("\nValeurs manquantes :")
print(df.isna().sum())


# --------------------------------------------------
# 3. Separation des tableaux 37 et 38
# --------------------------------------------------

tableau_37 = df[df["TABLE_SOURCE"] == "Tableau 37"].copy()

tableau_38 = df[df["TABLE_SOURCE"] == "Tableau 38"].copy()

assert len(tableau_37) == 18
assert len(tableau_38) == 42

print("\n=== REPARTITION DES TABLEAUX ===")
print("Tableau 37 :", len(tableau_37), "lignes")
print("Tableau 38 :", len(tableau_38), "lignes")


# --------------------------------------------------
# 4. Validation des donnees
# --------------------------------------------------

assert tableau_37["MILIEU_RESIDENCE"].notna().all()
assert tableau_37["EFFECTIF_REFERENCE"].notna().all()

assert tableau_38["MILIEU_RESIDENCE"].isna().all()
assert tableau_38["EFFECTIF_REFERENCE"].isna().all()

assert tableau_37["PROPORTION_PCT"].between(0, 100).all()
assert tableau_38["PROPORTION_PCT"].between(0, 100).all()

# Verification des doublons
cles_37 = [
    "REGION",
    "GROUPE_AGE",
    "MILIEU_RESIDENCE",
    "SEXE",
    "STATUT_SCOLAIRE"
]

cles_38 = [
    "REGION",
    "GROUPE_AGE",
    "SEXE",
    "STATUT_SCOLAIRE"
]

assert not tableau_37.duplicated(subset=cles_37).any()
assert not tableau_38.duplicated(subset=cles_38).any()

# Verification des sommes des proportions
sommes_37 = tableau_37.groupby(
    ["REGION", "MILIEU_RESIDENCE", "SEXE"]
)["PROPORTION_PCT"].sum()

sommes_38 = tableau_38.groupby(
    ["REGION", "GROUPE_AGE"]
)["PROPORTION_PCT"].sum()

print("\n=== VALIDATION DES PROPORTIONS ===")

print("\nTableau 37 :")
print(sommes_37.round(2))

print("\nTableau 38 :")
print(sommes_38.round(2))

assert sommes_37.between(99.5, 100.5).all()
assert sommes_38.between(99.5, 100.5).all()

print("\nValidation des proportions : OK")


# --------------------------------------------------
# 5. Analyse du tableau 37
# Situation scolaire selon le milieu et le sexe
# --------------------------------------------------

print("\n=== ANALYSE DU TABLEAU 37 ===")

# Transformation des donnees en tableau comparatif
comparaison_37 = tableau_37.pivot_table(
    index=["MILIEU_RESIDENCE", "SEXE"],
    columns="STATUT_SCOLAIRE",
    values="PROPORTION_PCT"
).reset_index()

comparaison_37.to_csv(
    DOSSIER_SORTIE / "comparaison_situation_scolaire_milieu_sexe.csv",
    index=False,
    encoding="utf-8-sig"
)

print(comparaison_37.to_string(index=False))


# Comparaison entre milieu urbain et rural
pivot_milieu = tableau_37[
    tableau_37["SEXE"] == "Ensemble"
].pivot(
    index="STATUT_SCOLAIRE",
    columns="MILIEU_RESIDENCE",
    values="PROPORTION_PCT"
)

pivot_milieu["ECART_URBAIN_MOINS_RURAL"] = (
    pivot_milieu["Urbain"] - pivot_milieu["Rural"]
)

pivot_milieu = pivot_milieu.round(2)

pivot_milieu.to_csv(
    DOSSIER_SORTIE / "ecarts_situation_scolaire_urbain_rural.csv",
    encoding="utf-8-sig"
)

print("\n=== ECARTS URBAIN - RURAL ===")
print(pivot_milieu)


# Comparaison filles et garcons par milieu
comparaison_sexe = tableau_37[
    tableau_37["SEXE"].isin(["Féminin", "Masculin"])
].pivot_table(
    index=["MILIEU_RESIDENCE", "STATUT_SCOLAIRE"],
    columns="SEXE",
    values="PROPORTION_PCT"
).reset_index()

comparaison_sexe["ECART_FEMININ_MOINS_MASCULIN"] = (
    comparaison_sexe["Féminin"]
    - comparaison_sexe["Masculin"]
)

comparaison_sexe = comparaison_sexe.round(2)

comparaison_sexe.to_csv(
    DOSSIER_SORTIE / "ecarts_filles_garcons_par_milieu.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n=== ECARTS FILLES - GARCONS ===")
print(comparaison_sexe.to_string(index=False))


# --------------------------------------------------
# 6. Analyse du tableau 38
# Situation scolaire des 6-11 ans par region
# --------------------------------------------------

print("\n=== ANALYSE DU TABLEAU 38 ===")

comparaison_38 = tableau_38.pivot(
    index="REGION",
    columns="STATUT_SCOLAIRE",
    values="PROPORTION_PCT"
).reset_index()

comparaison_38 = comparaison_38.rename(columns={
    "Scolarisé": "SCOLARISE_PCT",
    "Déscolarisé": "DESCOLARISE_PCT",
    "Jamais fréquenté": "JAMAIS_FREQUENTE_PCT"
})

comparaison_38 = comparaison_38.sort_values(
    "SCOLARISE_PCT"
)

comparaison_38.to_csv(
    DOSSIER_SORTIE / "situation_scolaire_6_11_ans_par_region.csv",
    index=False,
    encoding="utf-8-sig"
)

print(comparaison_38.to_string(index=False))


# Classement des regions selon la proportion scolarisee
classement_regions = comparaison_38[
    ["REGION", "SCOLARISE_PCT"]
].sort_values(
    "SCOLARISE_PCT",
    ascending=True
)

classement_regions.to_csv(
    DOSSIER_SORTIE / "classement_regions_scolarisation_6_11_ans.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n=== REGIONS : PROPORTIONS DE SCOLARISATION LES PLUS FAIBLES ===")
print(classement_regions.head(5).to_string(index=False))


# --------------------------------------------------
# 7. Graphique : situation scolaire selon le milieu
# --------------------------------------------------

statuts = [
    "Scolarisé",
    "Déscolarisé",
    "Jamais fréquenté"
]

milieux = ["Urbain", "Rural"]

fig, ax = plt.subplots(figsize=(10, 6))

largeur = 0.35
positions = range(len(statuts))

for i, milieu in enumerate(milieux):
    valeurs = []

    for statut in statuts:
        valeur = tableau_37[
            (tableau_37["SEXE"] == "Ensemble")
            & (tableau_37["MILIEU_RESIDENCE"] == milieu)
            & (tableau_37["STATUT_SCOLAIRE"] == statut)
        ]["PROPORTION_PCT"].iloc[0]

        valeurs.append(valeur)

    ax.bar(
        [p + (i - 0.5) * largeur for p in positions],
        valeurs,
        width=largeur,
        label=milieu
    )

ax.set_title("Situation scolaire des 6-16 ans selon le milieu")
ax.set_ylabel("Proportion (%)")
ax.set_xticks(list(positions))
ax.set_xticklabels(statuts)
ax.legend()
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig(
    DOSSIER_SORTIE / "01_situation_scolaire_urbain_rural.png",
    dpi=300
)
plt.close()


# --------------------------------------------------
# 8. Graphique : ecarts filles et garcons
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(10, 6))

for sexe in ["Féminin", "Masculin"]:
    valeurs = []

    for milieu in milieux:
        valeur = tableau_37[
            (tableau_37["SEXE"] == sexe)
            & (tableau_37["MILIEU_RESIDENCE"] == milieu)
            & (tableau_37["STATUT_SCOLAIRE"] == "Scolarisé")
        ]["PROPORTION_PCT"].iloc[0]

        valeurs.append(valeur)

    ax.plot(
        milieux,
        valeurs,
        marker="o",
        label=sexe
    )

ax.set_title("Proportion de scolarisation selon le sexe et le milieu")
ax.set_ylabel("Proportion scolarisée (%)")
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(
    DOSSIER_SORTIE / "02_scolarisation_sexe_milieu.png",
    dpi=300
)
plt.close()


# --------------------------------------------------
# 9. Graphique : scolarisation par region
# --------------------------------------------------

plt.figure(figsize=(12, 7))

plt.barh(
    comparaison_38["REGION"],
    comparaison_38["SCOLARISE_PCT"]
)

plt.title("Proportion des enfants de 6-11 ans scolarises par region")
plt.xlabel("Proportion scolarisee (%)")
plt.ylabel("Region")
plt.grid(axis="x", alpha=0.3)
plt.tight_layout()

plt.savefig(
    DOSSIER_SORTIE / "03_scolarisation_6_11_ans_par_region.png",
    dpi=300
)
plt.close()


# --------------------------------------------------
# 10. Sauvegarde du rapport de validation
# --------------------------------------------------

rapport_validation = pd.DataFrame([
    {
        "CONTROLE": "Nombre de lignes",
        "RESULTAT": len(df),
        "STATUT": "OK"
    },
    {
        "CONTROLE": "Lignes Tableau 37",
        "RESULTAT": len(tableau_37),
        "STATUT": "OK"
    },
    {
        "CONTROLE": "Lignes Tableau 38",
        "RESULTAT": len(tableau_38),
        "STATUT": "OK"
    },
    {
        "CONTROLE": "Proportions Tableau 37",
        "RESULTAT": "Sommes proches de 100 %",
        "STATUT": "OK"
    },
    {
        "CONTROLE": "Proportions Tableau 38",
        "RESULTAT": "Sommes proches de 100 %",
        "STATUT": "OK"
    },
    {
        "CONTROLE": "Doublons",
        "RESULTAT": 0,
        "STATUT": "OK"
    }
])

rapport_validation.to_csv(
    DOSSIER_SORTIE / "rapport_validation_insd.csv",
    index=False,
    encoding="utf-8-sig"
)


# --------------------------------------------------
# 11. Fin de l'analyse
# --------------------------------------------------

print("\n===================================")
print("ANALYSE INSD TERMINEE AVEC SUCCES")
print("===================================")
print("Dossier des resultats :", DOSSIER_SORTIE)
