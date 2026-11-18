
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import pearsonr, spearmanr


# ==================================================
# 1. CHEMINS DU PROJET
# ==================================================

RACINE_PROJET = Path(__file__).resolve().parents[3]

FICHIER_ENTREE = (
    RACINE_PROJET
    / "outputs"
    / "analyses"
    / "03_analyse_disparites_regionales"
    / "moyennes_indicateurs_par_region.csv"
)

DOSSIER_SORTIE = (
    RACINE_PROJET
    / "outputs"
    / "analyses"
    / "05_analyse_statistique"
)

DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)


# ==================================================
# 2. CHARGEMENT DES DONNEES
# ==================================================

if not FICHIER_ENTREE.exists():
    raise FileNotFoundError(
        f"Fichier introuvable : {FICHIER_ENTREE}"
    )

df = pd.read_csv(FICHIER_ENTREE)

print("=== STRUCTURE DES DONNEES ===")
print("Dimensions :", df.shape)
print("Colonnes :", df.columns.tolist())


# ==================================================
# 3. SELECTION DES VARIABLES
# ==================================================

variables = ["TBA", "TBS", "TAP"]

colonnes_requises = ["REGION"] + variables

for colonne in colonnes_requises:
    if colonne not in df.columns:
        raise ValueError(
            f"Colonne absente : {colonne}"
        )

donnees = df[colonnes_requises].copy()

for colonne in variables:
    donnees[colonne] = pd.to_numeric(
        donnees[colonne],
        errors="coerce"
    )

if donnees[variables].isna().any().any():
    raise ValueError(
        "Des valeurs manquantes ou non numeriques ont ete detectees."
    )

if donnees["REGION"].duplicated().any():
    raise ValueError(
        "Plusieurs observations par region ont ete detectees."
    )

print("\n=== CONTROLE DES DONNEES ===")
print("Nombre de regions :", len(donnees))
print("Valeurs manquantes :", donnees[variables].isna().sum().sum())
print("Doublons regionaux :", donnees["REGION"].duplicated().sum())


# ==================================================
# 4. STATISTIQUES DESCRIPTIVES
# ==================================================

statistiques = donnees[variables].describe().T

statistiques["MEDIANE"] = donnees[variables].median()
statistiques["ETENDUE"] = (
    donnees[variables].max()
    - donnees[variables].min()
)

statistiques = statistiques.round(3)

statistiques.to_csv(
    DOSSIER_SORTIE / "statistiques_indicateurs.csv",
    encoding="utf-8-sig"
)

print("\n=== STATISTIQUES DESCRIPTIVES ===")
print(statistiques)


# ==================================================
# 5. MATRICES DE CORRELATION
# ==================================================

correlation_pearson = donnees[variables].corr(
    method="pearson"
)

correlation_spearman = donnees[variables].corr(
    method="spearman"
)

correlation_pearson.to_csv(
    DOSSIER_SORTIE / "matrice_correlation_pearson.csv",
    encoding="utf-8-sig"
)

correlation_spearman.to_csv(
    DOSSIER_SORTIE / "matrice_correlation_spearman.csv",
    encoding="utf-8-sig"
)

print("\n=== CORRELATION PEARSON ===")
print(correlation_pearson.round(3))

print("\n=== CORRELATION SPEARMAN ===")
print(correlation_spearman.round(3))


# ==================================================
# 6. TESTS DE CORRELATION
# ==================================================

resultats = []

for i in range(len(variables)):

    for j in range(i + 1, len(variables)):

        var1 = variables[i]
        var2 = variables[j]

        r_pearson, p_pearson = pearsonr(
            donnees[var1],
            donnees[var2]
        )

        r_spearman, p_spearman = spearmanr(
            donnees[var1],
            donnees[var2]
        )

        resultats.append({
            "VARIABLE_1": var1,
            "VARIABLE_2": var2,
            "PEARSON_R": r_pearson,
            "PEARSON_P_VALUE": p_pearson,
            "SPEARMAN_R": r_spearman,
            "SPEARMAN_P_VALUE": p_spearman
        })


resultats_df = pd.DataFrame(resultats)

resultats_df = resultats_df.round(5)

resultats_df.to_csv(
    DOSSIER_SORTIE / "tests_correlations.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n=== RESULTATS DES TESTS DE CORRELATION ===")
print(resultats_df.to_string(index=False))


# ==================================================
# 7. INTERPRETATION AUTOMATIQUE DE L'INTENSITE
# ==================================================

def interpreter_correlation(r):

    valeur = abs(r)

    if valeur < 0.20:
        intensite = "Tres faible"

    elif valeur < 0.40:
        intensite = "Faible"

    elif valeur < 0.60:
        intensite = "Moderee"

    elif valeur < 0.80:
        intensite = "Forte"

    else:
        intensite = "Tres forte"

    if r > 0:
        direction = "Positive"

    elif r < 0:
        direction = "Negative"

    else:
        direction = "Nulle"

    return f"{intensite} et {direction}"


resultats_df["INTERPRETATION_PEARSON"] = (
    resultats_df["PEARSON_R"]
    .apply(interpreter_correlation)
)

print("\n=== INTERPRETATION DES CORRELATIONS ===")

for _, ligne in resultats_df.iterrows():

    print(
        f"{ligne['VARIABLE_1']} - {ligne['VARIABLE_2']} : "
        f"{ligne['PEARSON_R']:.3f} "
        f"({ligne['INTERPRETATION_PEARSON']})"
    )


# ==================================================
# 8. GRAPHIQUE : MATRICE DE CORRELATION
# ==================================================

fig, ax = plt.subplots(figsize=(8, 6))

image = ax.imshow(
    correlation_pearson,
    vmin=-1,
    vmax=1,
    aspect="auto"
)

ax.set_xticks(range(len(variables)))
ax.set_yticks(range(len(variables)))

ax.set_xticklabels(variables)
ax.set_yticklabels(variables)

for i in range(len(variables)):
    for j in range(len(variables)):

        valeur = correlation_pearson.iloc[i, j]

        ax.text(
            j,
            i,
            f"{valeur:.2f}",
            ha="center",
            va="center"
        )

ax.set_title("Matrice de correlation Pearson")

fig.colorbar(image, ax=ax, label="Coefficient de correlation")

plt.tight_layout()

plt.savefig(
    DOSSIER_SORTIE / "01_matrice_correlation_pearson.png",
    dpi=300
)

plt.close()


# ==================================================
# 9. GRAPHIQUES DE DISPERSION
# ==================================================

paires = [
    ("TBA", "TBS"),
    ("TBA", "TAP"),
    ("TBS", "TAP")
]

for index, (x, y) in enumerate(paires, start=1):

    plt.figure(figsize=(9, 6))

    plt.scatter(
        donnees[x],
        donnees[y]
    )

    for _, ligne in donnees.iterrows():

        plt.annotate(
            ligne["REGION"],
            (ligne[x], ligne[y]),
            fontsize=8,
            xytext=(4, 4),
            textcoords="offset points"
        )

    plt.xlabel(x)
    plt.ylabel(y)

    plt.title(
        f"Relation entre {x} et {y} par region"
    )

    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        DOSSIER_SORTIE
        / f"0{index + 1}_dispersion_{x.lower()}_{y.lower()}.png",
        dpi=300
    )

    plt.close()


# ==================================================
# 10. EXPORT DES DONNEES ANALYSEES
# ==================================================

donnees.to_csv(
    DOSSIER_SORTIE / "donnees_utilisees_correlations.csv",
    index=False,
    encoding="utf-8-sig"
)


# ==================================================
# 11. FIN
# ==================================================

print("\n==========================================")
print("ANALYSE DES CORRELATIONS TERMINEE")
print("==========================================")

print("Nombre de regions analysees :", len(donnees))

print("Nombre de variables :", len(variables))

print("Dossier des resultats :", DOSSIER_SORTIE)
