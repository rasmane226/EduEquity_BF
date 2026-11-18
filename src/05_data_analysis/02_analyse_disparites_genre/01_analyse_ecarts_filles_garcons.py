
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# 1. DEFINITION DES CHEMINS
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = ROOT_DIR / "data" / "04_transformed_data" / "merged"

OUTPUT_DIR = ROOT_DIR / "outputs" / "analyses" / "02_analyse_disparites_genre"

GRAPH_DIR = OUTPUT_DIR / "graphiques"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# 2. CHARGEMENT DES DONNEES
# =====================================================

df = pd.read_csv(DATA_DIR / "indicateurs_regionaux_sexe.csv")

indicateurs = ["TBA", "TBS", "TAP"]

# =====================================================
# 3. PREPARATION DES DONNEES
# =====================================================

df["ORDRE_ANNEE"] = (
    df["ANNEE_SCOLAIRE"].str[:4].astype(int)
)

# Vérification des catégories de sexe
df["SEXE"] = df["SEXE"].str.upper().str.strip()

# =====================================================
# 4. CALCUL DES ECARTS FILLES-GARCONS
# =====================================================

df_pivot = df.pivot(
    index=["REGION", "ANNEE_SCOLAIRE", "ORDRE_ANNEE"],
    columns="SEXE",
    values=indicateurs
)

df_pivot.columns = [
    f"{indicateur}_{sexe}"
    for indicateur, sexe in df_pivot.columns
]

df_pivot = df_pivot.reset_index()

for indicateur in indicateurs:
    df_pivot[f"ECART_{indicateur}"] = (
        df_pivot[f"{indicateur}_FILLES"]
        - df_pivot[f"{indicateur}_GARCONS"]
    )

# Valeur positive : avantage des filles
# Valeur négative : avantage des garçons

df_pivot.to_csv(
    OUTPUT_DIR / "ecarts_genre_region_annee.csv",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 5. ECART MOYEN PAR REGION
# =====================================================

ecarts_regionaux = (
    df_pivot
    .groupby("REGION", as_index=False)[
        [f"ECART_{indicateur}" for indicateur in indicateurs]
    ]
    .mean()
)

ecarts_regionaux.to_csv(
    OUTPUT_DIR / "ecarts_moyens_par_region.csv",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 6. IDENTIFICATION DES REGIONS LES PLUS
#    DEFAVORABLES AUX FILLES ET AUX GARCONS
# =====================================================

synthese_regions = []

for indicateur in indicateurs:

    colonne = f"ECART_{indicateur}"

    region_defavorable_filles = (
        ecarts_regionaux.loc[ecarts_regionaux[colonne].idxmin()]
    )

    region_defavorable_garcons = (
        ecarts_regionaux.loc[ecarts_regionaux[colonne].idxmax()]
    )

    synthese_regions.append({
        "INDICATEUR": indicateur,
        "REGION_PLUS_DEFAVORABLE_AUX_FILLES":
            region_defavorable_filles["REGION"],
        "ECART_MOYEN_FILLES":
            region_defavorable_filles[colonne],
        "REGION_PLUS_DEFAVORABLE_AUX_GARCONS":
            region_defavorable_garcons["REGION"],
        "ECART_MOYEN_GARCONS":
            region_defavorable_garcons[colonne]
    })

synthese_regions = pd.DataFrame(synthese_regions)

synthese_regions.to_csv(
    OUTPUT_DIR / "regions_ecarts_genre_extremes.csv",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 7. EVOLUTION TEMPORELLE DES ECARTS
# =====================================================

evolution_ecarts = (
    df_pivot
    .groupby(
        ["ORDRE_ANNEE", "ANNEE_SCOLAIRE"],
        as_index=False
    )[
        [f"ECART_{indicateur}" for indicateur in indicateurs]
    ]
    .mean()
    .sort_values("ORDRE_ANNEE")
)

evolution_ecarts.to_csv(
    OUTPUT_DIR / "evolution_ecarts_genre.csv",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 8. VISUALISATION DE L'EVOLUTION DES ECARTS
# =====================================================

for indicateur in indicateurs:

    colonne = f"ECART_{indicateur}"

    plt.figure(figsize=(11, 6))

    plt.plot(
        evolution_ecarts["ANNEE_SCOLAIRE"],
        evolution_ecarts[colonne],
        marker="o"
    )

    plt.axhline(
        y=0,
        linestyle="--",
        label="Absence d'écart"
    )

    plt.title(f"Evolution de l'écart filles-garçons : {indicateur}")
    plt.xlabel("Année scolaire")
    plt.ylabel("Ecart en points de pourcentage")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR / f"evolution_ecart_{indicateur.lower()}.png",
        dpi=300
    )

    plt.close()

# =====================================================
# 9. VISUALISATION DES ECARTS REGIONAUX
# =====================================================

for indicateur in indicateurs:

    colonne = f"ECART_{indicateur}"

    donnees = ecarts_regionaux.sort_values(colonne)

    plt.figure(figsize=(11, 7))

    plt.barh(
        donnees["REGION"],
        donnees[colonne]
    )

    plt.axvline(x=0, linestyle="--")

    plt.title(f"Ecarts filles-garçons par région : {indicateur}")
    plt.xlabel("Ecart en points de pourcentage (filles - garçons)")
    plt.ylabel("Région")
    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR / f"ecarts_regionaux_{indicateur.lower()}.png",
        dpi=300
    )

    plt.close()

# =====================================================
# 10. AFFICHAGE DES RESULTATS
# =====================================================

print("\n===== ECARTS MOYENS PAR REGION =====")
print(ecarts_regionaux.round(2).to_string(index=False))

print("\n===== REGIONS PRESENTANT LES ECARTS EXTREMES =====")
print(synthese_regions.round(2).to_string(index=False))

print("\n===== EVOLUTION TEMPORELLE DES ECARTS =====")
print(evolution_ecarts.round(2).to_string(index=False))

print("\nAnalyse des disparites de genre terminee.")
print(f"Resultats : {OUTPUT_DIR}")
print(f"Graphiques : {GRAPH_DIR}")
