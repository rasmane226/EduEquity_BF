
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. CHEMINS DU PROJET
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "01_analyse_exploratoire"
    / "evolution_annuelle_indicateurs_sexe.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "06_data_visualization"
    / "01_descriptive_visualization"
)

FIGURES_DIR = OUTPUT_DIR / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# Vérification des chemins
print("=" * 60)
print("VERIFICATION DES CHEMINS")
print("=" * 60)

print("BASE_DIR :", BASE_DIR)
print("INPUT_FILE :", INPUT_FILE)
print("Fichier existe :", INPUT_FILE.exists())

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Fichier introuvable : {INPUT_FILE}"
    )


# ============================================================
# 2. CHARGEMENT ET VALIDATION DES DONNEES
# ============================================================

df = pd.read_csv(INPUT_FILE)

required_columns = [
    "ORDRE_ANNEE",
    "ANNEE_SCOLAIRE",
    "SEXE",
    "TBA",
    "TBS",
    "TAP"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Colonnes manquantes : {missing_columns}"
    )

df = df[required_columns].copy()

df["ORDRE_ANNEE"] = pd.to_numeric(
    df["ORDRE_ANNEE"],
    errors="raise"
)

for col in ["TBA", "TBS", "TAP"]:
    df[col] = pd.to_numeric(
        df[col],
        errors="raise"
    )

df = df.sort_values(
    ["ORDRE_ANNEE", "SEXE"]
)

if df.duplicated(["ORDRE_ANNEE", "SEXE"]).any():
    raise ValueError(
        "Des doublons existent pour une année et un sexe."
    )

if df[required_columns].isnull().any().any():
    raise ValueError(
        "Le jeu de données contient des valeurs manquantes."
    )

print("\n" + "=" * 60)
print("VERIFICATION DU JEU DE DONNEES")
print("=" * 60)

print(f"Nombre d'observations : {len(df)}")
print(f"Nombre d'années : {df['ORDRE_ANNEE'].nunique()}")
print(f"Sexes : {df['SEXE'].unique().tolist()}")

print("\nAperçu des données :")
print(df.head())


# ============================================================
# 3. CONFIGURATION DES GRAPHIQUES
# ============================================================

indicators = {
    "TBA": {
        "title": "Évolution du taux brut d'admission selon le sexe",
        "ylabel": "TBA (%)",
        "filename": "01_evolution_tba_sexe.png"
    },
    "TBS": {
        "title": "Évolution du taux brut de scolarisation selon le sexe",
        "ylabel": "TBS (%)",
        "filename": "02_evolution_tbs_sexe.png"
    },
    "TAP": {
        "title": "Évolution du taux d'achèvement du primaire selon le sexe",
        "ylabel": "TAP (%)",
        "filename": "03_evolution_tap_sexe.png"
    }
}

colors = {
    "FILLES": "darkorange",
    "GARCONS": "steelblue"
}

labels = {
    "FILLES": "Filles",
    "GARCONS": "Garçons"
}


# ============================================================
# 4. GENERATION DES GRAPHIQUES
# ============================================================

for indicator, config in indicators.items():

    plt.figure(figsize=(12, 6))

    for sex in ["FILLES", "GARCONS"]:

        data_sex = df[
            df["SEXE"] == sex
        ].sort_values("ORDRE_ANNEE")

        if data_sex.empty:
            print(f"Attention : aucune donnée pour {sex}")
            continue

        plt.plot(
            data_sex["ANNEE_SCOLAIRE"],
            data_sex[indicator],
            marker="o",
            linewidth=2.2,
            markersize=6,
            color=colors[sex],
            label=labels[sex]
        )

    plt.title(
        config["title"],
        fontsize=14,
        fontweight="bold"
    )

    plt.xlabel(
        "Année scolaire",
        fontsize=11
    )

    plt.ylabel(
        config["ylabel"],
        fontsize=11
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.grid(
        axis="y",
        linestyle="--",
        alpha=0.4
    )

    plt.legend(title="Sexe")

    plt.tight_layout()

    output_file = FIGURES_DIR / config["filename"]

    plt.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Graphique enregistré : {output_file}")


# ============================================================
# 5. ANALYSE DES VARIATIONS
# ============================================================

report_lines = []

report_lines.append(
    "INTERPRETATION DES EVOLUTIONS DES INDICATEURS"
)

report_lines.append("=" * 60)

report_lines.append(
    "Source : DGESS, données scolaires 2015-2016 à 2024-2025"
)

report_lines.append(
    "Les résultats sont des moyennes descriptives régionales."
)

for indicator in indicators:

    report_lines.append("")
    report_lines.append("-" * 60)
    report_lines.append(f"INDICATEUR : {indicator}")

    for sex in ["FILLES", "GARCONS"]:

        data_sex = df[
            df["SEXE"] == sex
        ].sort_values("ORDRE_ANNEE")

        if data_sex.empty:
            continue

        first_value = data_sex.iloc[0][indicator]
        last_value = data_sex.iloc[-1][indicator]

        variation = last_value - first_value

        first_year = data_sex.iloc[0]["ANNEE_SCOLAIRE"]
        last_year = data_sex.iloc[-1]["ANNEE_SCOLAIRE"]

        report_lines.append(
            f"\n{labels[sex]} :"
        )

        report_lines.append(
            f"Valeur initiale ({first_year}) : {first_value:.2f}%"
        )

        report_lines.append(
            f"Valeur finale ({last_year}) : {last_value:.2f}%"
        )

        report_lines.append(
            f"Variation : {variation:+.2f} points."
        )

        if variation > 0:
            interpretation = "Une augmentation est observée."
        elif variation < 0:
            interpretation = "Une diminution est observée."
        else:
            interpretation = "Aucune variation nette n'est observée."

        report_lines.append(interpretation)


# ============================================================
# 6. EXPORTATION DU RAPPORT
# ============================================================

REPORT_FILE = OUTPUT_DIR / "interpretation_descriptive.txt"

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write("\n".join(report_lines))


# ============================================================
# 7. FIN DU TRAITEMENT
# ============================================================

print("\n" + "=" * 60)
print("VISUALISATION DESCRIPTIVE TERMINEE")
print("=" * 60)

print("Nombre de graphiques générés : 3")
print("Dossier des graphiques :", FIGURES_DIR)
print("Rapport descriptif :", REPORT_FILE)
