
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

INPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "03_analyse_disparites_regionales"
    / "moyennes_indicateurs_par_region.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "05_analyse_statistique"
    / "visualisations"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\n========== CONFIGURATION ==========")
print("Dossier racine :", BASE_DIR)
print("Fichier source :", INPUT_FILE)
print("Fichier existant :", INPUT_FILE.exists())

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Fichier source introuvable : {INPUT_FILE}"
    )

# ============================================================
# 2. CHARGEMENT ET CONTROLE DES DONNEES
# ============================================================

df = pd.read_csv(INPUT_FILE)

indicateurs = ["TBA", "TBS", "TAP"]

colonnes_requises = ["REGION"] + indicateurs

colonnes_absentes = [
    col for col in colonnes_requises
    if col not in df.columns
]

if colonnes_absentes:
    raise ValueError(
        f"Colonnes absentes : {colonnes_absentes}"
    )

if df[colonnes_requises].isnull().any().any():
    raise ValueError(
        "Des valeurs manquantes sont présentes."
    )

print("\n========== CONTROLE DES DONNEES ==========")
print("Nombre de régions :", df["REGION"].nunique())
print("Dimensions :", df.shape)

# Style général
sns.set_theme(style="whitegrid")

# ============================================================
# 3. HISTOGRAMMES DES DISTRIBUTIONS
# ============================================================

print("\n========== HISTOGRAMMES ==========")

for indicateur in indicateurs:

    plt.figure(figsize=(9, 5))

    sns.histplot(
        data=df,
        x=indicateur,
        bins=7,
        kde=True
    )

    plt.title(
        f"Distribution régionale du {indicateur}"
    )
    plt.xlabel(f"{indicateur} (%)")
    plt.ylabel("Nombre de régions")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / f"distribution_{indicateur}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Graphique créé : distribution_{indicateur}.png")

# ============================================================
# 4. BOXPLOT COMPARATIF
# ============================================================

print("\n========== BOXPLOT COMPARATIF ==========")

df_long = df.melt(
    id_vars="REGION",
    value_vars=indicateurs,
    var_name="INDICATEUR",
    value_name="VALEUR"
)

plt.figure(figsize=(10, 6))

sns.boxplot(
    data=df_long,
    x="INDICATEUR",
    y="VALEUR"
)

plt.title(
    "Comparaison des distributions du TBA, TBS et TAP"
)
plt.xlabel("Indicateurs")
plt.ylabel("Valeurs (%)")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "boxplots_indicateurs.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Boxplot comparatif créé.")

# ============================================================
# 5. MATRICE DE CORRELATION PEARSON
# ============================================================

print("\n========== MATRICE DE CORRELATION ==========")

correlation = df[indicateurs].corr(method="pearson")

print(correlation.round(3))

plt.figure(figsize=(8, 6))

sns.heatmap(
    correlation,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    vmin=-1,
    vmax=1,
    center=0,
    square=True
)

plt.title("Matrice de corrélation Pearson")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "matrice_correlation_pearson.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Matrice de corrélation créée.")

# ============================================================
# 6. GRAPHIQUES DE CORRELATION
# ============================================================

print("\n========== GRAPHIQUES DE CORRELATION ==========")

paires = [
    ("TBA", "TBS"),
    ("TBA", "TAP"),
    ("TBS", "TAP")
]

for x_var, y_var in paires:

    plt.figure(figsize=(9, 6))

    sns.regplot(
        data=df,
        x=x_var,
        y=y_var,
        ci=95,
        scatter_kws={"s": 70}
    )

    # Identification des régions
    for _, ligne in df.iterrows():

        plt.annotate(
            ligne["REGION"],
            (ligne[x_var], ligne[y_var]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8
        )

    plt.title(
        f"Relation entre {x_var} et {y_var}"
    )
    plt.xlabel(f"{x_var} (%)")
    plt.ylabel(f"{y_var} (%)")

    plt.tight_layout()

    nom_fichier = (
        f"correlation_{x_var}_{y_var}.png"
    )

    plt.savefig(
        OUTPUT_DIR / nom_fichier,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Graphique créé : {nom_fichier}")

# ============================================================
# 7. SYNTHESE FINALE
# ============================================================

print("\n========== SYNTHESE FINALE ==========")

print("Nombre de régions analysées :", len(df))
print("Nombre d'indicateurs :", len(indicateurs))
print("Nombre de graphiques générés : 7")

print("\nVisualisations statistiques terminées.")
print("Résultats enregistrés dans :")
print(OUTPUT_DIR)
