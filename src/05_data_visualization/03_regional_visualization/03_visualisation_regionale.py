
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
    / "03_analyse_disparites_regionales"
)

OUTPUT_DIR = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "06_data_visualization"
    / "03_regional_visualization"
)

FIGURES_DIR = OUTPUT_DIR / "figures"

FIGURES_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FILE_MEANS = SOURCE_DIR / "moyennes_indicateurs_par_region.csv"
FILE_EVOLUTION = SOURCE_DIR / "evolution_indicateurs_par_region.csv"
FILE_RANKING = SOURCE_DIR / "classement_regions_indicateurs.csv"
FILE_VARIATIONS = SOURCE_DIR / "variations_indicateurs_par_region.csv"


# ============================================================
# 2. IDENTITE VISUELLE EDU EQUITY BF
# ============================================================

NAVY = "#17365D"
BLUE = "#2878A5"
ORANGE = "#E69F35"
RED = "#D95F59"
GREEN = "#3A9278"
GREY = "#64748B"
LIGHT_GREY = "#E9EEF3"

INDICATOR_COLORS = {
    "TBA": BLUE,
    "TBS": ORANGE,
    "TAP": GREEN
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
# 3. CHARGEMENT DES DONNEES
# ============================================================

files = [
    FILE_MEANS,
    FILE_EVOLUTION,
    FILE_RANKING,
    FILE_VARIATIONS
]

for file in files:

    if not file.exists():

        raise FileNotFoundError(
            f"Fichier introuvable : {file}"
        )

df_means = pd.read_csv(FILE_MEANS)

df_evolution = pd.read_csv(FILE_EVOLUTION)

df_ranking = pd.read_csv(FILE_RANKING)

df_variations = pd.read_csv(FILE_VARIATIONS)


print("=" * 65)
print("VERIFICATION DES DONNEES REGIONALES")
print("=" * 65)

for name, data in [
    ("Moyennes régionales", df_means),
    ("Evolution régionale", df_evolution),
    ("Classement régional", df_ranking),
    ("Variations régionales", df_variations)
]:

    print(f"{name} : {data.shape}")


# ============================================================
# 4. VALIDATION DES COLONNES
# ============================================================

required_means = [
    "REGION",
    "TBA",
    "TBS",
    "TAP"
]

required_evolution = [
    "REGION",
    "ORDRE_ANNEE",
    "ANNEE_SCOLAIRE",
    "TBA",
    "TBS",
    "TAP"
]

required_ranking = [
    "INDICATEUR",
    "RANG",
    "REGION",
    "VALEUR_MOYENNE"
]

required_variations = [
    "REGION",
    "INDICATEUR",
    "ANNEE_DEBUT",
    "ANNEE_FIN",
    "VALEUR_INITIALE",
    "VALEUR_FINALE",
    "VARIATION_POINTS",
    "EVOLUTION"
]


for data, required in [
    (df_means, required_means),
    (df_evolution, required_evolution),
    (df_ranking, required_ranking),
    (df_variations, required_variations)
]:

    missing = [
        col for col in required
        if col not in data.columns
    ]

    if missing:

        raise ValueError(
            f"Colonnes manquantes : {missing}"
        )


# Vérification des doublons

if df_means["REGION"].duplicated().any():

    raise ValueError(
        "Régions dupliquées dans les moyennes."
    )


if df_evolution.duplicated(
    ["REGION", "ORDRE_ANNEE"]
).any():

    raise ValueError(
        "Doublons région-année détectés."
    )


if df_ranking.duplicated(
    ["REGION", "INDICATEUR"]
).any():

    raise ValueError(
        "Doublons région-indicateur dans le classement."
    )


if df_variations.duplicated(
    ["REGION", "INDICATEUR"]
).any():

    raise ValueError(
        "Doublons région-indicateur dans les variations."
    )


# Conversion des colonnes numériques

for data, columns in [

    (df_means, ["TBA", "TBS", "TAP"]),

    (df_evolution, ["TBA", "TBS", "TAP"]),

    (df_ranking, ["RANG", "VALEUR_MOYENNE"]),

    (df_variations, ["VARIATION_POINTS"])

]:

    for column in columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="raise"
        )


# Vérification du nombre de régions

if df_means["REGION"].nunique() != 13:

    raise ValueError(
        "Le fichier des moyennes ne contient pas 13 régions."
    )


print("\nValidation des données : OK")


# ============================================================
# 5. FONCTION D'EXPORTATION DES FIGURES
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

    print(
        f"Figure enregistrée : {chemin}"
    )


# ============================================================
# 6. HEATMAP DES INDICATEURS REGIONAUX
# ============================================================

print("\n1. Génération de la heatmap régionale...")


heatmap_data = (

    df_means

    .set_index("REGION")[["TBA", "TBS", "TAP"]]

)

# Tri des régions selon le TAP

heatmap_data = heatmap_data.sort_values(
    "TAP"
)


plt.figure(
    figsize=(12, 9)
)


sns.heatmap(

    heatmap_data,

    annot=True,

    fmt=".1f",

    cmap="YlGnBu",

    linewidths=1,

    linecolor="white",

    cbar_kws={
        "label": "Valeur moyenne de l'indicateur (%)"
    },

    annot_kws={
        "size": 10,
        "weight": "bold"
    }

)


plt.title(
    "Profil des indicateurs scolaires dans les 13 régions",
    fontsize=16,
    color=NAVY
)

plt.xlabel(
    "Indicateurs scolaires",
    fontsize=12
)

plt.ylabel(
    "Régions",
    fontsize=12
)


sauvegarder_figure(
    "01_heatmap_indicateurs_regionaux.png"
)


# ============================================================
# 7. CLASSEMENT REGIONAL PAR INDICATEUR
# ============================================================

print("\n2. Génération du classement régional...")


fig, axes = plt.subplots(
    1,
    3,
    figsize=(21, 10)
)


for ax, indicator in zip(
    axes,
    ["TBA", "TBS", "TAP"]
):

    data = (

        df_ranking[

            df_ranking["INDICATEUR"] == indicator

        ]

        .sort_values("RANG")

    )


    if len(data) != 13:

        raise ValueError(
            f"Le classement {indicator} ne contient pas 13 régions."
        )


    bars = ax.barh(

        data["REGION"],

        data["VALEUR_MOYENNE"],

        color=INDICATOR_COLORS[indicator],

        height=0.68

    )


    ax.invert_yaxis()


    ax.set_title(
        f"Classement selon le {indicator}",
        fontsize=14
    )


    ax.set_xlabel(
        "Valeur moyenne (%)"
    )

    ax.set_ylabel("")


    ax.grid(
        axis="x",
        alpha=0.5
    )

    ax.grid(
        axis="y",
        visible=False
    )


    ax.tick_params(
        axis="y",
        labelsize=8
    )


    for bar, rank, value in zip(

        bars,

        data["RANG"],

        data["VALEUR_MOYENNE"]

    ):

        ax.text(

            value + 0.8,

            bar.get_y() + bar.get_height() / 2,

            f"Rang {int(rank)} | {value:.1f}",

            va="center",

            fontsize=7.5

        )


fig.suptitle(

    "Classement des régions selon les indicateurs scolaires",

    fontsize=18,

    fontweight="bold",

    color=NAVY

)


sauvegarder_figure(
    "02_classement_regional_indicateurs.png"
)


# ============================================================
# 8. HEATMAPS DE L'EVOLUTION TEMPORELLE PAR REGION
# ============================================================

print("\n3. Génération des heatmaps temporelles...")


# Palettes de couleurs

heatmap_palettes = {

    "TBA": "YlGnBu",

    "TBS": "YlOrBr",

    "TAP": "YlGn"

}


# Titres des graphiques

heatmap_titles = {

    "TBA": "Evolution du taux brut d'admission par région",

    "TBS": "Evolution du taux brut de scolarisation par région",

    "TAP": "Evolution du taux d'achèvement du primaire par région"

}


# Préparation des données

df_evolution_sorted = df_evolution.sort_values(

    ["REGION", "ORDRE_ANNEE"]

)


# Vérification de la couverture temporelle

expected_years = sorted(
    df_evolution["ORDRE_ANNEE"].unique()
)

expected_regions = set(
    df_means["REGION"]
)

if len(expected_years) != 10:

    raise ValueError(
        "Le fichier temporel ne contient pas 10 années."
    )

if set(df_evolution["REGION"]) != expected_regions:

    raise ValueError(
        "Les régions des fichiers moyens et temporel ne correspondent pas."
    )

if not df_evolution.groupby("REGION")["ORDRE_ANNEE"].nunique().eq(10).all():

    raise ValueError(
        "Certaines régions ne possèdent pas les 10 années attendues."
    )


# Ordre chronologique des années

year_order = (

    df_evolution_sorted[

        ["ORDRE_ANNEE", "ANNEE_SCOLAIRE"]

    ]

    .drop_duplicates()

    .sort_values("ORDRE_ANNEE")

    ["ANNEE_SCOLAIRE"]

    .tolist()

)


# Génération des trois heatmaps

for indicator in ["TBA", "TBS", "TAP"]:


    # Matrice région × année

    pivot_data = df_evolution_sorted.pivot(

        index="REGION",

        columns="ANNEE_SCOLAIRE",

        values=indicator

    )


    # Réorganisation chronologique des colonnes

    pivot_data = pivot_data.reindex(
        columns=year_order
    )


    # Organisation des régions selon leur moyenne

    region_order = (

        df_means

        .sort_values(indicator)

        ["REGION"]

        .tolist()

    )


    pivot_data = pivot_data.reindex(
        region_order
    )


    # Création de la figure

    fig, ax = plt.subplots(

        figsize=(16, 9)

    )


    sns.heatmap(

        pivot_data,

        annot=True,

        fmt=".1f",

        cmap=heatmap_palettes[indicator],

        linewidths=0.8,

        linecolor="white",

        cbar_kws={

            "label": f"{indicator} (%)",

            "shrink": 0.85

        },

        annot_kws={

            "size": 9,

            "weight": "bold"

        },

        ax=ax

    )


    ax.set_title(

        heatmap_titles[indicator],

        fontsize=17,

        fontweight="bold",

        color=NAVY,

        pad=20

    )


    ax.set_xlabel(

        "Année scolaire",

        fontsize=12,

        labelpad=12

    )


    ax.set_ylabel(

        "Régions",

        fontsize=12,

        labelpad=12

    )


    ax.tick_params(

        axis="x",

        rotation=35,

        labelsize=9

    )


    ax.tick_params(

        axis="y",

        rotation=0,

        labelsize=10

    )


    # Exportation

    sauvegarder_figure(

        f"03_heatmap_evolution_{indicator.lower()}.png"

    )


# ============================================================
# 9. VARIATIONS DES INDICATEURS PAR REGION
# ============================================================

print("\n4. Génération des variations régionales...")


fig, axes = plt.subplots(

    1,

    3,

    figsize=(21, 10)

)


for ax, indicator in zip(

    axes,

    ["TBA", "TBS", "TAP"]

):


    data = (

        df_variations[

            df_variations["INDICATEUR"] == indicator

        ]

        .sort_values("VARIATION_POINTS")

    )


    if len(data) != 13:

        raise ValueError(

            f"Les variations {indicator} ne contiennent pas 13 régions."

        )


    colors = [

        GREEN if value > 0 else RED

        if value < 0 else GREY

        for value in data["VARIATION_POINTS"]

    ]


    bars = ax.barh(

        data["REGION"],

        data["VARIATION_POINTS"],

        color=colors,

        height=0.68

    )


    ax.axvline(

        0,

        color=NAVY,

        linewidth=1.2

    )


    ax.set_title(

        f"Variation du {indicator}",

        fontsize=14

    )


    ax.set_xlabel(

        "Variation (points)"

    )


    ax.set_ylabel("")


    ax.tick_params(

        axis="y",

        labelsize=8

    )


    ax.grid(

        axis="x",

        alpha=0.5

    )

    ax.grid(

        axis="y",

        visible=False

    )


    for bar, value in zip(

        bars,

        data["VARIATION_POINTS"]

    ):


        offset = (

            0.35 if value >= 0 else -0.35

        )


        ax.text(

            value + offset,

            bar.get_y() + bar.get_height() / 2,

            f"{value:+.1f}",

            va="center",

            ha="left" if value >= 0 else "right",

            fontsize=7.5,

            fontweight="bold"

        )


fig.suptitle(

    "Evolution des indicateurs entre 2015-2016 et 2024-2025",

    fontsize=18,

    fontweight="bold",

    color=NAVY

)


sauvegarder_figure(
    "04_variations_indicateurs_regionaux.png"
)


# ============================================================
# 10. GENERATION DU RAPPORT DESCRIPTIF
# ============================================================

print("\n5. Génération de l'interprétation descriptive...")


report = []


report.append(
    "ANALYSE DES DISPARITES REGIONALES"
)

report.append(
    "=" * 70
)


report.append(

    "Les valeurs présentées sont des moyennes descriptives régionales."

)

report.append(

    "Elles ne constituent pas des moyennes nationales pondérées."

)


indicators = ["TBA", "TBS", "TAP"]


# Analyse des moyennes régionales

for indicator in indicators:


    report.append("")

    report.append(
        "-" * 70
    )

    report.append(
        f"INDICATEUR : {indicator}"
    )


    data = df_means.sort_values(
        indicator
    )


    lowest = data.iloc[0]

    highest = data.iloc[-1]


    report.append(

        f"Valeur la plus faible : {lowest['REGION']} "

        f"({lowest[indicator]:.2f} %)"

    )


    report.append(

        f"Valeur la plus élevée : {highest['REGION']} "

        f"({highest[indicator]:.2f} %)"

    )


    report.append(

        f"Amplitude régionale : "

        f"{highest[indicator] - lowest[indicator]:.2f} points"

    )


# Analyse des variations

report.append("")

report.append(
    "-" * 70
)

report.append(
    "VARIATIONS ENTRE LES DEUX ANNEES EXTREMES"
)


for indicator in indicators:


    data = df_variations[

        df_variations["INDICATEUR"] == indicator

    ]


    progressions = (

        data["VARIATION_POINTS"] > 0

    ).sum()


    reculs = (

        data["VARIATION_POINTS"] < 0

    ).sum()


    stabilites = (

        data["VARIATION_POINTS"] == 0

    ).sum()


    report.append("")

    report.append(
        f"Indicateur : {indicator}"
    )


    report.append(

        f"Progressions : {progressions} régions"

    )


    report.append(

        f"Reculs : {reculs} régions"

    )


    report.append(

        f"Stabilités : {stabilites} régions"

    )


    best = data.loc[

        data["VARIATION_POINTS"].idxmax()

    ]


    worst = data.loc[

        data["VARIATION_POINTS"].idxmin()

    ]


    report.append(

        f"Variation positive la plus élevée : "

        f"{best['REGION']} "

        f"({best['VARIATION_POINTS']:+.2f} points)"

    )


    report.append(

        f"Variation la plus négative : "

        f"{worst['REGION']} "

        f"({worst['VARIATION_POINTS']:+.2f} points)"

    )


# Enregistrement du rapport

REPORT_FILE = OUTPUT_DIR / "interpretation_regionale.txt"


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
    "VISUALISATION REGIONALE TERMINEE"
)

print("=" * 65)


print(

    "Nombre de régions :",

    df_means["REGION"].nunique()

)


print(

    "Nombre d'observations temporelles :",

    len(df_evolution)

)


print(

    "Nombre de graphiques générés : 6"

)


print(

    "\nDossier des figures :",

    FIGURES_DIR

)


print(

    "Rapport :",

    REPORT_FILE

)
