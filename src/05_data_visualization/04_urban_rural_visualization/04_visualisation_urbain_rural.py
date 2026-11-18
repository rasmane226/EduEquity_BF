
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

SOURCE_DIR = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "06_priorisation_et_recommandations"
)

OUTPUT_DIR = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "06_data_visualization"
    / "04_urban_rural_visualization"
)

FIGURES_DIR = OUTPUT_DIR / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# Fichiers sources consolidés

FILE_EVOLUTION = (
    SOURCE_DIR / "donnees_evolution_urbain_rural.csv"
)

FILE_SITUATION = (
    SOURCE_DIR / "donnees_situation_milieu_sexe.csv"
)

FILE_GENDER = (
    SOURCE_DIR / "donnees_ecarts_genre_milieu.csv"
)

FILE_URBAN_RURAL = (
    SOURCE_DIR / "donnees_ecarts_urbain_rural.csv"
)


# ============================================================
# 2. IDENTITE VISUELLE EDU EQUITY BF
# ============================================================

NAVY = "#17365D"
BLUE = "#2878A5"
ORANGE = "#E69F35"
GREEN = "#3A9278"
RED = "#D95F59"
GREY = "#64748B"
LIGHT_GREY = "#E9EEF3"

COLORS = {
    "Urbain": BLUE,
    "Rural": ORANGE,
    "FILLES": "#D95F9A",
    "GARCONS": "#2878A5"
}

sns.set_theme(
    style="whitegrid",
    context="notebook",
    font_scale=1.05
)

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": LIGHT_GREY,
    "axes.labelcolor": NAVY,
    "axes.titlecolor": NAVY,
    "xtick.color": GREY,
    "ytick.color": GREY,
    "font.family": "DejaVu Sans",
    "axes.titleweight": "bold",
    "axes.titlepad": 15,
    "grid.color": LIGHT_GREY,
    "grid.linewidth": 0.7,
    "legend.frameon": False,
    "savefig.facecolor": "white"
})


# ============================================================
# 3. VERIFICATION ET CHARGEMENT DES DONNEES
# ============================================================

print("=" * 65)
print("VERIFICATION DES DONNEES URBAINES ET RURALES")
print("=" * 65)

files = [
    FILE_EVOLUTION,
    FILE_SITUATION,
    FILE_GENDER,
    FILE_URBAN_RURAL
]

for file in files:

    if not file.exists():

        raise FileNotFoundError(
            f"Fichier introuvable : {file}"
        )

df_evolution = pd.read_csv(FILE_EVOLUTION)

df_situation = pd.read_csv(FILE_SITUATION)

df_gender = pd.read_csv(FILE_GENDER)

df_urban_rural = pd.read_csv(FILE_URBAN_RURAL)


for name, data in [
    ("Evolution urbain-rural", df_evolution),
    ("Situation scolaire par milieu et sexe", df_situation),
    ("Ecarts filles-garçons", df_gender),
    ("Ecarts urbain-rural", df_urban_rural)
]:

    print(f"{name} : {data.shape}")


# ============================================================
# 4. VALIDATION DES COLONNES
# ============================================================

required_evolution = [
    "ANNEE_SCOLAIRE",
    "SEXE",
    "EFFECTIF_URBAIN",
    "EFFECTIF_RURAL"
]

required_situation = [
    "MILIEU_RESIDENCE",
    "SEXE",
    "Déscolarisé",
    "Jamais fréquenté",
    "Scolarisé"
]

required_gender = [
    "MILIEU_RESIDENCE",
    "STATUT_SCOLAIRE",
    "Féminin",
    "Masculin",
    "ECART_FEMININ_MOINS_MASCULIN"
]

required_urban_rural = [
    "STATUT_SCOLAIRE",
    "Rural",
    "Urbain",
    "ECART_URBAIN_MOINS_RURAL"
]


for data, required in [
    (df_evolution, required_evolution),
    (df_situation, required_situation),
    (df_gender, required_gender),
    (df_urban_rural, required_urban_rural)
]:

    missing = [
        col for col in required
        if col not in data.columns
    ]

    if missing:

        raise ValueError(
            f"Colonnes manquantes : {missing}"
        )


# Conversion numérique

for column in [
    "EFFECTIF_URBAIN",
    "EFFECTIF_RURAL"
]:

    df_evolution[column] = pd.to_numeric(
        df_evolution[column],
        errors="raise"
    )


for column in [
    "Déscolarisé",
    "Jamais fréquenté",
    "Scolarisé"
]:

    df_situation[column] = pd.to_numeric(
        df_situation[column],
        errors="raise"
    )


for column in [
    "Féminin",
    "Masculin",
    "ECART_FEMININ_MOINS_MASCULIN"
]:

    df_gender[column] = pd.to_numeric(
        df_gender[column],
        errors="raise"
    )


for column in [
    "Rural",
    "Urbain",
    "ECART_URBAIN_MOINS_RURAL"
]:

    df_urban_rural[column] = pd.to_numeric(
        df_urban_rural[column],
        errors="raise"
    )


print("\nValidation des colonnes : OK")


# ============================================================
# 5. FONCTION D'EXPORTATION
# ============================================================

def sauvegarder_figure(nom_fichier):

    chemin = FIGURES_DIR / nom_fichier

    plt.tight_layout()

    plt.savefig(
        chemin,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Figure enregistrée : {chemin}")


# ============================================================
# 6. EVOLUTION DES EFFECTIFS URBAINS ET RURAUX
# ============================================================

print("\n1. Génération de l'évolution des effectifs...")


fig, axes = plt.subplots(
    1,
    2,
    figsize=(17, 7),
    sharey=False
)


for ax, sex in zip(
    axes,
    ["FILLES", "GARCONS"]
):

    data = df_evolution[
        df_evolution["SEXE"] == sex
    ].copy()


    data = data.drop_duplicates(
        subset=["ANNEE_SCOLAIRE"]
    )


    data = data.sort_values(
        "ANNEE_SCOLAIRE"
    )


    ax.plot(
        data["ANNEE_SCOLAIRE"],
        data["EFFECTIF_URBAIN"],
        marker="o",
        linewidth=2.8,
        markersize=7,
        color=COLORS["Urbain"],
        label="Urbain"
    )


    ax.plot(
        data["ANNEE_SCOLAIRE"],
        data["EFFECTIF_RURAL"],
        marker="o",
        linewidth=2.8,
        markersize=7,
        color=COLORS["Rural"],
        label="Rural"
    )


    ax.set_title(
        f"Effectifs scolaires — {sex.capitalize()}",
        fontsize=14
    )


    ax.set_xlabel(
        "Année scolaire"
    )


    ax.set_ylabel(
        "Nombre d'élèves"
    )


    ax.tick_params(
        axis="x",
        rotation=35
    )


    ax.legend(
        title="Milieu de résidence"
    )


    ax.grid(
        axis="y",
        alpha=0.4
    )


fig.suptitle(
    "Evolution des effectifs scolaires selon le milieu de résidence et le sexe",
    fontsize=17,
    color=NAVY,
    fontweight="bold"
)


sauvegarder_figure(
    "01_evolution_effectifs_urbain_rural_sexe.png"
)


# ============================================================
# 7. SITUATION SCOLAIRE SELON LE MILIEU
# ============================================================

print("\n2. Génération de la situation scolaire...")


# Sélection de la catégorie Ensemble

data_ensemble = df_situation[
    df_situation["SEXE"].str.strip().str.lower()
    == "ensemble"
].copy()


if data_ensemble.empty:

    raise ValueError(
        "Aucune observation Ensemble dans le fichier INSD."
    )


data_plot = data_ensemble.melt(
    id_vars=["MILIEU_RESIDENCE", "SEXE"],
    value_vars=[
        "Scolarisé",
        "Déscolarisé",
        "Jamais fréquenté"
    ],
    var_name="STATUT_SCOLAIRE",
    value_name="POURCENTAGE"
)


fig, ax = plt.subplots(
    figsize=(12, 7)
)


sns.barplot(
    data=data_plot,
    x="STATUT_SCOLAIRE",
    y="POURCENTAGE",
    hue="MILIEU_RESIDENCE",
    palette={
        "Urbain": BLUE,
        "Rural": ORANGE
    },
    ax=ax
)


ax.set_title(
    "Situation scolaire selon le milieu de résidence",
    fontsize=17,
    color=NAVY
)


ax.set_xlabel(
    "Statut scolaire"
)


ax.set_ylabel(
    "Proportion (%)"
)


ax.legend(
    title="Milieu de résidence"
)


ax.grid(
    axis="y",
    alpha=0.4
)


sauvegarder_figure(
    "02_situation_scolaire_urbain_rural.png"
)


# ============================================================
# 8. ECARTS FILLES-GARCONS SELON LE MILIEU
# ============================================================

print("\n3. Génération des écarts filles-garçons...")


gender_pivot = df_gender.pivot(
    index="MILIEU_RESIDENCE",
    columns="STATUT_SCOLAIRE",
    values="ECART_FEMININ_MOINS_MASCULIN"
)


gender_pivot = gender_pivot.reindex(
    index=["Rural", "Urbain"]
)


fig, ax = plt.subplots(
    figsize=(11, 6)
)


sns.heatmap(
    gender_pivot,
    annot=True,
    fmt=".1f",
    cmap="RdBu_r",
    center=0,
    linewidths=1,
    linecolor="white",
    cbar_kws={
        "label": "Ecart filles - garçons (points)"
    },
    annot_kws={
        "size": 11,
        "weight": "bold"
    },
    ax=ax
)


ax.set_title(
    "Ecarts entre filles et garçons selon le milieu de résidence",
    fontsize=16,
    color=NAVY
)


ax.set_xlabel(
    "Statut scolaire"
)


ax.set_ylabel(
    "Milieu de résidence"
)


sauvegarder_figure(
    "03_heatmap_ecarts_filles_garcons_milieu.png"
)


# ============================================================
# 9. COMPARAISON DES STATUTS SCOLAIRES URBAIN-RURAL
# ============================================================

print("\n4. Génération des différences urbain-rural...")


data_gap = df_urban_rural.sort_values(
    "ECART_URBAIN_MOINS_RURAL"
)


colors = [

    BLUE if value > 0 else ORANGE
    if value < 0 else GREY

    for value in data_gap[
        "ECART_URBAIN_MOINS_RURAL"
    ]

]


fig, ax = plt.subplots(
    figsize=(12, 7)
)


bars = ax.barh(
    data_gap["STATUT_SCOLAIRE"],
    data_gap["ECART_URBAIN_MOINS_RURAL"],
    color=colors,
    height=0.6
)


ax.axvline(
    0,
    color=NAVY,
    linewidth=1.2
)


for bar, value in zip(
    bars,
    data_gap["ECART_URBAIN_MOINS_RURAL"]
):

    offset = 0.5 if value >= 0 else -0.5

    ax.text(
        value + offset,
        bar.get_y() + bar.get_height() / 2,
        f"{value:+.1f}",
        va="center",
        ha="left" if value >= 0 else "right",
        fontweight="bold",
        fontsize=10
    )


ax.set_title(
    "Différences de situation scolaire entre milieu urbain et rural",
    fontsize=16,
    color=NAVY
)


ax.set_xlabel(
    "Ecart urbain - rural (points de pourcentage)"
)


ax.set_ylabel(
    "Statut scolaire"
)


ax.grid(
    axis="x",
    alpha=0.4
)


sauvegarder_figure(
    "04_ecarts_situation_urbain_rural.png"
)


# ============================================================
# 10. GENERATION DU RAPPORT DESCRIPTIF
# ============================================================

print("\n5. Génération du rapport descriptif...")


report = []

report.append(
    "ANALYSE DES DISPARITES ENTRE MILIEUX URBAIN ET RURAL"
)

report.append("=" * 70)


report.append(
    "PARTIE 1 : EVOLUTION DES EFFECTIFS"
)


for sex in ["FILLES", "GARCONS"]:

    data = df_evolution[
        df_evolution["SEXE"] == sex
    ].sort_values("ANNEE_SCOLAIRE")


    if not data.empty:

        first = data.iloc[0]

        last = data.iloc[-1]


        report.append("")

        report.append(
            f"Sexe : {sex}"
        )


        report.append(

            f"Effectif urbain initial : "

            f"{first['EFFECTIF_URBAIN']:.0f}"

        )


        report.append(

            f"Effectif urbain final : "

            f"{last['EFFECTIF_URBAIN']:.0f}"

        )


        report.append(

            f"Effectif rural initial : "

            f"{first['EFFECTIF_RURAL']:.0f}"

        )


        report.append(

            f"Effectif rural final : "

            f"{last['EFFECTIF_RURAL']:.0f}"

        )


report.append("")

report.append(
    "PARTIE 2 : SITUATION SCOLAIRE SELON LE MILIEU"
)


for _, row in data_ensemble.iterrows():

    report.append("")

    report.append(
        f"Milieu : {row['MILIEU_RESIDENCE']}"
    )


    for indicator in [
        "Scolarisé",
        "Déscolarisé",
        "Jamais fréquenté"
    ]:

        report.append(

            f"{indicator} : {row[indicator]:.1f} %"

        )


report.append("")

report.append(
    "PARTIE 3 : ECARTS FILLES-GARCONS"
)


for _, row in df_gender.iterrows():

    report.append("")

    report.append(

        f"Milieu : {row['MILIEU_RESIDENCE']} | "

        f"Statut : {row['STATUT_SCOLAIRE']} | "

        f"Ecart filles-garçons : "

        f"{row['ECART_FEMININ_MOINS_MASCULIN']:+.1f} points"

    )


report.append("")

report.append(
    "PARTIE 4 : DIFFERENCES URBAIN-RURAL"
)


for _, row in df_urban_rural.iterrows():

    report.append("")

    report.append(

        f"{row['STATUT_SCOLAIRE']} : "

        f"{row['ECART_URBAIN_MOINS_RURAL']:+.1f} points "

        f"(urbain - rural)"

    )


report.append("")

report.append(
    "NOTE METHODOLOGIQUE"
)

report.append(

    "Les effectifs urbains et ruraux sont des nombres d'élèves, "

    "et non des taux d'accès ou de scolarisation."

)

report.append(

    "Les données INSD de situation scolaire selon le milieu "

    "concernent les enfants de 6 à 16 ans."

)

report.append(

    "Les écarts filles-garçons sont exprimés en points de pourcentage. "

    "Leur interprétation dépend du statut scolaire considéré."

)


REPORT_FILE = OUTPUT_DIR / "interpretation_urbain_rural.txt"


with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "\n".join(report)
    )


# ============================================================
# 11. FIN DU TRAITEMENT
# ============================================================

print("\n" + "=" * 65)

print(
    "VISUALISATION URBAIN-RURAL TERMINEE"
)

print("=" * 65)


print(
    "Nombre de graphiques générés : 4"
)


print(
    "Dossier des figures :",
    FIGURES_DIR
)


print(
    "Rapport :",
    REPORT_FILE
)
