
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# ============================================================
# 1. CONFIGURATION GENERALE
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

SOURCE_DIR = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "02_analyse_disparites_genre"
)

OUTPUT_DIR = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "06_data_visualization"
    / "02_gender_disparity_visualization"
)

FIGURES_DIR = OUTPUT_DIR / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

FILE_REGIONS = SOURCE_DIR / "ecarts_moyens_par_region.csv"
FILE_EVOLUTION = SOURCE_DIR / "evolution_ecarts_genre.csv"
FILE_EXTREMES = SOURCE_DIR / "regions_ecarts_genre_extremes.csv"
FILE_DETAIL = SOURCE_DIR / "ecarts_genre_region_annee.csv"


# ============================================================
# 2. IDENTITE VISUELLE EDU EQUITY BF
# ============================================================

NAVY = "#17365D"
BLUE = "#2878A5"
ORANGE = "#E69F35"
RED = "#D95F59"
GREY = "#64748B"
LIGHT_GREY = "#E9EEF3"

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
    "axes.titlepad": 18,
    "grid.color": LIGHT_GREY,
    "grid.linewidth": 0.8,
    "legend.frameon": False,
    "savefig.facecolor": "white"
})


# ============================================================
# 3. CHARGEMENT DES DONNEES
# ============================================================

files = [
    FILE_REGIONS,
    FILE_EVOLUTION,
    FILE_EXTREMES,
    FILE_DETAIL
]

for file in files:
    if not file.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {file}"
        )

df_regions = pd.read_csv(FILE_REGIONS)
df_evolution = pd.read_csv(FILE_EVOLUTION)
df_extremes = pd.read_csv(FILE_EXTREMES)
df_detail = pd.read_csv(FILE_DETAIL)

print("=" * 65)
print("VERIFICATION DES DONNEES")
print("=" * 65)

for name, data in [
    ("Ecarts moyens par région", df_regions),
    ("Evolution des écarts", df_evolution),
    ("Régions extrêmes", df_extremes),
    ("Données détaillées", df_detail)
]:
    print(f"{name} : {data.shape}")


# ============================================================
# 4. VALIDATION DES COLONNES
# ============================================================

required_regions = [
    "REGION", "ECART_TBA", "ECART_TBS", "ECART_TAP"
]

required_evolution = [
    "ORDRE_ANNEE",
    "ANNEE_SCOLAIRE",
    "ECART_TBA",
    "ECART_TBS",
    "ECART_TAP"
]

required_extremes = [
    "INDICATEUR",
    "REGION_PLUS_DEFAVORABLE_AUX_FILLES",
    "ECART_MOYEN_FILLES",
    "REGION_PLUS_DEFAVORABLE_AUX_GARCONS",
    "ECART_MOYEN_GARCONS"
]

required_detail = [
    "REGION",
    "ANNEE_SCOLAIRE",
    "ORDRE_ANNEE",
    "ECART_TBA",
    "ECART_TBS",
    "ECART_TAP"
]

for data, required in [
    (df_regions, required_regions),
    (df_evolution, required_evolution),
    (df_extremes, required_extremes),
    (df_detail, required_detail)
]:
    missing = [col for col in required if col not in data.columns]

    if missing:
        raise ValueError(
            f"Colonnes manquantes : {missing}"
        )

if df_regions["REGION"].duplicated().any():
    raise ValueError("Des régions sont dupliquées.")

if df_detail.duplicated(
    ["REGION", "ORDRE_ANNEE"]
).any():
    raise ValueError("Doublons région-année détectés.")


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
# 6. HEATMAP DES ECARTS DE GENRE PAR REGION
# ============================================================

print("\n1. Génération de la heatmap...")

heatmap_data = (
    df_regions
    .set_index("REGION")[
        ["ECART_TBA", "ECART_TBS", "ECART_TAP"]
    ]
    .rename(columns={
        "ECART_TBA": "TBA",
        "ECART_TBS": "TBS",
        "ECART_TAP": "TAP"
    })
)

plt.figure(figsize=(12, 9))

sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".2f",
    cmap="RdYlBu",
    center=0,
    linewidths=1,
    linecolor="white",
    cbar_kws={
        "label": "Écart filles - garçons (points)"
    },
    annot_kws={
        "size": 10,
        "weight": "bold"
    }
)

plt.title(
    "Disparités de genre dans l'enseignement primaire par région",
    fontsize=16
)

plt.xlabel("Indicateurs scolaires", fontsize=12)
plt.ylabel("Régions", fontsize=12)

sauvegarder_figure(
    "01_heatmap_ecarts_genre.png"
)


# ============================================================
# 7. COMPARAISON DES ECARTS REGIONAUX
# ============================================================

print("\n2. Génération de la comparaison régionale...")

indicators = [
    ("ECART_TBA", "TBA"),
    ("ECART_TBS", "TBS"),
    ("ECART_TAP", "TAP")
]

fig, axes = plt.subplots(
    1, 3,
    figsize=(21, 10)
)

for ax, (column, title) in zip(axes, indicators):

    data = df_regions.sort_values(column)

    colors = [
        RED if value < 0 else BLUE
        for value in data[column]
    ]

    bars = ax.barh(
        data["REGION"],
        data[column],
        color=colors,
        height=0.68
    )

    ax.axvline(
        0,
        color=NAVY,
        linewidth=1.3
    )

    ax.set_title(
        title,
        fontsize=15
    )

    ax.set_xlabel(
        "Écart filles - garçons (points)"
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

    ax.tick_params(axis="y", labelsize=9)

    for bar, value in zip(bars, data[column]):

        offset = 0.18 if value >= 0 else -0.18

        ax.text(
            value + offset,
            bar.get_y() + bar.get_height() / 2,
            f"{value:+.1f}",
            va="center",
            ha="left" if value >= 0 else "right",
            fontsize=8,
            fontweight="bold"
        )

fig.suptitle(
    "Comparaison des disparités de genre entre les 13 régions",
    fontsize=18,
    fontweight="bold",
    color=NAVY
)

sauvegarder_figure(
    "02_comparaison_ecarts_regionaux.png"
)


# ============================================================
# 8. EVOLUTION TEMPORELLE DES ECARTS DE GENRE
# ============================================================

print("\n3. Génération de l'évolution temporelle...")

fig, ax = plt.subplots(figsize=(14, 7))

time_series = {
    "ECART_TBA": {
        "label": "TBA",
        "color": BLUE
    },
    "ECART_TBS": {
        "label": "TBS",
        "color": ORANGE
    },
    "ECART_TAP": {
        "label": "TAP",
        "color": RED
    }
}

for column, config in time_series.items():

    ax.plot(
        df_evolution["ANNEE_SCOLAIRE"],
        df_evolution[column],
        marker="o",
        markersize=7,
        linewidth=2.8,
        color=config["color"],
        label=config["label"]
    )

    for x, y in zip(
        df_evolution["ANNEE_SCOLAIRE"],
        df_evolution[column]
    ):
        ax.annotate(
            f"{y:.1f}",
            (x, y),
            textcoords="offset points",
            xytext=(0, 9),
            ha="center",
            fontsize=8
        )

ax.axhline(
    0,
    color=NAVY,
    linestyle="--",
    linewidth=1.3,
    label="Égalité filles-garçons"
)

ax.set_title(
    "Évolution des écarts de genre dans l'enseignement primaire",
    fontsize=16
)

ax.set_xlabel("Année scolaire")
ax.set_ylabel("Écart filles - garçons (points)")

ax.tick_params(
    axis="x",
    rotation=35
)

ax.legend(
    title="Indicateurs",
    loc="best"
)

ax.grid(
    axis="y",
    alpha=0.5
)

sauvegarder_figure(
    "03_evolution_ecarts_genre.png"
)


# ============================================================
# 9. REGIONS PRESENTANT LES ECARTS EXTREMES
# ============================================================

print("\n4. Génération des régions extrêmes...")

fig, axes = plt.subplots(
    1, 3,
    figsize=(18, 7)
)

for ax, (_, row) in zip(
    axes,
    df_extremes.iterrows()
):

    indicator = row["INDICATEUR"]

    regions = [
        row["REGION_PLUS_DEFAVORABLE_AUX_FILLES"],
        row["REGION_PLUS_DEFAVORABLE_AUX_GARCONS"]
    ]

    values = [
        row["ECART_MOYEN_FILLES"],
        row["ECART_MOYEN_GARCONS"]
    ]

    colors = [RED, BLUE]

    bars = ax.bar(
        ["Désavantage filles", "Désavantage garçons"],
        values,
        color=colors,
        width=0.58
    )

    ax.axhline(
        0,
        color=NAVY,
        linewidth=1
    )

    ax.set_title(
        indicator,
        fontsize=15
    )

    ax.set_ylabel(
        "Écart filles - garçons (points)"
    )

    ax.tick_params(
        axis="x",
        rotation=12
    )

    for bar, region, value in zip(
        bars,
        regions,
        values
    ):

        ax.annotate(
            f"{region}\n({value:+.2f})",
            (
                bar.get_x() + bar.get_width() / 2,
                value
            ),
            xytext=(0, 9 if value >= 0 else -28),
            textcoords="offset points",
            ha="center",
            fontsize=8,
            fontweight="bold"
        )

fig.suptitle(
    "Régions présentant les disparités de genre les plus marquées",
    fontsize=17,
    fontweight="bold",
    color=NAVY
)

sauvegarder_figure(
    "04_regions_ecarts_extremes.png"
)


# ============================================================
# 10. GENERATION DU RAPPORT DESCRIPTIF
# ============================================================

print("\n5. Génération du rapport descriptif...")

report = []

report.append(
    "ANALYSE DES DISPARITES DE GENRE PAR REGION"
)

report.append("=" * 65)

report.append(
    "Convention : écart = valeur filles - valeur garçons."
)

report.append(
    "Écart négatif : désavantage des filles."
)

report.append(
    "Écart positif : valeur supérieure chez les filles."
)

report.append(
    "Les écarts sont exprimés en points de pourcentage."
)

for column, indicator in indicators:

    report.append("")
    report.append("-" * 65)
    report.append(f"INDICATEUR : {indicator}")

    minimum = df_regions.loc[
        df_regions[column].idxmin()
    ]

    maximum = df_regions.loc[
        df_regions[column].idxmax()
    ]

    report.append(
        f"Écart le plus négatif : {minimum['REGION']} "
        f"({minimum[column]:+.2f} points)"
    )

    report.append(
        f"Écart le plus positif : {maximum['REGION']} "
        f"({maximum[column]:+.2f} points)"
    )

    report.append(
        f"Régions avec écart négatif : "
        f"{(df_regions[column] < 0).sum()}"
    )

    report.append(
        f"Régions avec écart positif : "
        f"{(df_regions[column] > 0).sum()}"
    )

# Evolution temporelle
report.append("")
report.append("-" * 65)
report.append("EVOLUTION TEMPORELLE")

for column, indicator in indicators:

    first = df_evolution.iloc[0][column]
    last = df_evolution.iloc[-1][column]

    report.append(
        f"{indicator} : {first:+.2f} points en "
        f"{df_evolution.iloc[0]['ANNEE_SCOLAIRE']} "
        f"contre {last:+.2f} points en "
        f"{df_evolution.iloc[-1]['ANNEE_SCOLAIRE']}."
    )

REPORT_FILE = OUTPUT_DIR / "interpretation_genre.txt"

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write("\n".join(report))


# ============================================================
# 11. FIN DU TRAITEMENT
# ============================================================

print("\n" + "=" * 65)
print("VISUALISATION DES DISPARITES DE GENRE TERMINEE")
print("=" * 65)

print("Nombre de graphiques générés : 4")
print("Nombre de régions :", df_regions["REGION"].nunique())
print("Nombre d'années :", df_evolution["ORDRE_ANNEE"].nunique())

print("\nDossier des figures :", FIGURES_DIR)
print("Rapport :", REPORT_FILE)
