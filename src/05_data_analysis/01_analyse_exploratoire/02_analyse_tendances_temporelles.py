
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# 1. DEFINITION DES CHEMINS
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = ROOT_DIR / "data" / "04_transformed_data" / "merged"

OUTPUT_DIR = ROOT_DIR / "outputs" / "analyses" / "01_analyse_exploratoire"

GRAPH_DIR = OUTPUT_DIR / "graphiques_tendances"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# 2. CHARGEMENT DES DONNEES
# =====================================================

df_indicateurs = pd.read_csv(
    DATA_DIR / "indicateurs_regionaux_sexe.csv"
)

df_parite = pd.read_csv(
    DATA_DIR / "indices_parite_regionaux.csv"
)

# =====================================================
# 3. PREPARATION DES VARIABLES
# =====================================================

indicateurs = ["TBA", "TBS", "TAP"]

indices_parite = [
    "IPS_TBA",
    "IPS_TBS",
    "IPS_TAP"
]

# Conversion des variables numériques
for colonne in indicateurs:
    df_indicateurs[colonne] = pd.to_numeric(
        df_indicateurs[colonne],
        errors="coerce"
    )

for colonne in indices_parite:
    df_parite[colonne] = pd.to_numeric(
        df_parite[colonne],
        errors="coerce"
    )

# Ordre chronologique des années scolaires
df_indicateurs["ORDRE_ANNEE"] = (
    df_indicateurs["ANNEE_SCOLAIRE"]
    .str[:4]
    .astype(int)
)

df_parite["ORDRE_ANNEE"] = (
    df_parite["ANNEE_SCOLAIRE"]
    .str[:4]
    .astype(int)
)

# =====================================================
# 4. EVOLUTION DES INDICATEURS PAR SEXE
# =====================================================

evolution_indicateurs = (
    df_indicateurs
    .groupby(
        ["ORDRE_ANNEE", "ANNEE_SCOLAIRE", "SEXE"],
        as_index=False
    )[indicateurs]
    .mean()
    .sort_values("ORDRE_ANNEE")
)

evolution_indicateurs.to_csv(
    OUTPUT_DIR / "evolution_annuelle_indicateurs_sexe.csv",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 5. EVOLUTION DES INDICES DE PARITE
# =====================================================

evolution_parite = (
    df_parite
    .groupby(
        ["ORDRE_ANNEE", "ANNEE_SCOLAIRE"],
        as_index=False
    )[indices_parite]
    .mean()
    .sort_values("ORDRE_ANNEE")
)

evolution_parite.to_csv(
    OUTPUT_DIR / "evolution_annuelle_indices_parite.csv",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 6. CALCUL DES VARIATIONS ENTRE LA PREMIERE
#    ET LA DERNIERE ANNEE
# =====================================================

synthese_variations = []

for indicateur in indicateurs:

    for sexe in sorted(df_indicateurs["SEXE"].unique()):

        donnees = evolution_indicateurs[
            evolution_indicateurs["SEXE"] == sexe
        ].sort_values("ORDRE_ANNEE")

        premiere_valeur = donnees.iloc[0][indicateur]
        derniere_valeur = donnees.iloc[-1][indicateur]

        synthese_variations.append({
            "INDICATEUR": indicateur,
            "SEXE": sexe,
            "ANNEE_DEBUT": donnees.iloc[0]["ANNEE_SCOLAIRE"],
            "ANNEE_FIN": donnees.iloc[-1]["ANNEE_SCOLAIRE"],
            "VALEUR_INITIALE": premiere_valeur,
            "VALEUR_FINALE": derniere_valeur,
            "VARIATION": derniere_valeur - premiere_valeur
        })

for indice in indices_parite:

    donnees = evolution_parite.sort_values("ORDRE_ANNEE")

    premiere_valeur = donnees.iloc[0][indice]
    derniere_valeur = donnees.iloc[-1][indice]

    synthese_variations.append({
        "INDICATEUR": indice,
        "SEXE": "Ensemble",
        "ANNEE_DEBUT": donnees.iloc[0]["ANNEE_SCOLAIRE"],
        "ANNEE_FIN": donnees.iloc[-1]["ANNEE_SCOLAIRE"],
        "VALEUR_INITIALE": premiere_valeur,
        "VALEUR_FINALE": derniere_valeur,
        "VARIATION": derniere_valeur - premiere_valeur
    })

synthese_variations = pd.DataFrame(synthese_variations)

synthese_variations.to_csv(
    OUTPUT_DIR / "synthese_variations_temporelles.csv",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 7. VISUALISATION DES INDICATEURS
# =====================================================

for indicateur in indicateurs:

    plt.figure(figsize=(11, 6))

    for sexe in sorted(df_indicateurs["SEXE"].unique()):

        donnees = evolution_indicateurs[
            evolution_indicateurs["SEXE"] == sexe
        ]

        plt.plot(
            donnees["ANNEE_SCOLAIRE"],
            donnees[indicateur],
            marker="o",
            label=sexe
        )

    plt.title(f"Evolution du {indicateur} selon le sexe")
    plt.xlabel("Année scolaire")
    plt.ylabel(f"{indicateur} (%)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR / f"evolution_{indicateur.lower()}_sexe.png",
        dpi=300
    )

    plt.close()

# =====================================================
# 8. VISUALISATION DES INDICES DE PARITE
# =====================================================

for indice in indices_parite:

    plt.figure(figsize=(11, 6))

    plt.plot(
        evolution_parite["ANNEE_SCOLAIRE"],
        evolution_parite[indice],
        marker="o",
        label=indice
    )

    plt.axhline(y=1, linestyle="--", label="Parité égale")

    plt.title(f"Evolution de {indice}")
    plt.xlabel("Année scolaire")
    plt.ylabel("Indice de parité")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR / f"evolution_{indice.lower()}.png",
        dpi=300
    )

    plt.close()

# =====================================================
# 9. AFFICHAGE DES RESULTATS
# =====================================================

print("\n===== EVOLUTION ANNUELLE DES INDICATEURS =====")
print(evolution_indicateurs.round(2).to_string(index=False))

print("\n===== EVOLUTION ANNUELLE DES INDICES DE PARITE =====")
print(evolution_parite.round(3).to_string(index=False))

print("\n===== VARIATIONS ENTRE LA PREMIERE ET LA DERNIERE ANNEE =====")
print(synthese_variations.round(3).to_string(index=False))

print("\nAnalyse des tendances temporelles terminee.")
print(f"Tableaux : {OUTPUT_DIR}")
print(f"Graphiques : {GRAPH_DIR}")
