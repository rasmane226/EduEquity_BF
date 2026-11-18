
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# =====================================================
# 1. DEFINITION DES CHEMINS
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = ROOT_DIR / "data" / "04_transformed_data" / "merged"

OUTPUT_DIR = ROOT_DIR / "outputs" / "analyses" / "03_analyse_disparites_regionales"

GRAPH_DIR = OUTPUT_DIR / "graphiques"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# 2. CHARGEMENT ET PREPARATION DES DONNEES
# =====================================================

df = pd.read_csv(DATA_DIR / "indicateurs_regionaux_sexe.csv")

indicateurs = ["TBA", "TBS", "TAP"]

df["SEXE"] = df["SEXE"].str.upper().str.strip()

df["ORDRE_ANNEE"] = (
    df["ANNEE_SCOLAIRE"].str[:4].astype(int)
)

for colonne in indicateurs:
    df[colonne] = pd.to_numeric(df[colonne], errors="coerce")

# Vérification des données
print("\n===== CONTROLE DES DONNEES =====")
print(f"Observations : {len(df)}")
print(f"Régions : {df['REGION'].nunique()}")
print(f"Années : {df['ANNEE_SCOLAIRE'].nunique()}")
print(f"Valeurs manquantes : {df[indicateurs].isna().sum().sum()}")

# =====================================================
# 3. MOYENNES DES INDICATEURS PAR REGION
# =====================================================

moyennes_region = (
    df.groupby("REGION")[indicateurs]
    .mean()
    .reset_index()
)

moyennes_region.to_csv(
    OUTPUT_DIR / "moyennes_indicateurs_par_region.csv",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 4. CLASSEMENT DES REGIONS
# =====================================================

classements = []

for indicateur in indicateurs:

    classement = moyennes_region[
        ["REGION", indicateur]
    ].sort_values(indicateur, ascending=True)

    classement = classement.reset_index(drop=True)

    classement["RANG"] = range(1, len(classement) + 1)
    classement["INDICATEUR"] = indicateur

    classement = classement.rename(
        columns={indicateur: "VALEUR_MOYENNE"}
    )

    classements.append(classement)

classements = pd.concat(classements, ignore_index=True)

classements = classements[
    ["INDICATEUR", "RANG", "REGION", "VALEUR_MOYENNE"]
]

classements.to_csv(
    OUTPUT_DIR / "classement_regions_indicateurs.csv",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 5. EVOLUTION TEMPORELLE PAR REGION
# =====================================================

evolution = (
    df.groupby(
        ["REGION", "ORDRE_ANNEE", "ANNEE_SCOLAIRE"]
    )[indicateurs]
    .mean()
    .reset_index()
    .sort_values(["REGION", "ORDRE_ANNEE"])
)

evolution.to_csv(
    OUTPUT_DIR / "evolution_indicateurs_par_region.csv",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 6. VARIATION ENTRE LA PREMIERE ET LA DERNIERE ANNEE
# =====================================================

variations = []

for region in sorted(df["REGION"].unique()):

    donnees = evolution[
        evolution["REGION"] == region
    ].sort_values("ORDRE_ANNEE")

    for indicateur in indicateurs:

        valeur_initiale = donnees.iloc[0][indicateur]
        valeur_finale = donnees.iloc[-1][indicateur]

        variations.append({
            "REGION": region,
            "INDICATEUR": indicateur,
            "ANNEE_DEBUT": donnees.iloc[0]["ANNEE_SCOLAIRE"],
            "ANNEE_FIN": donnees.iloc[-1]["ANNEE_SCOLAIRE"],
            "VALEUR_INITIALE": valeur_initiale,
            "VALEUR_FINALE": valeur_finale,
            "VARIATION_POINTS": valeur_finale - valeur_initiale
        })

variations = pd.DataFrame(variations)

def determiner_evolution(valeur):
    if valeur > 0:
        return "Progression"
    elif valeur < 0:
        return "Recul"
    return "Stable"

variations["EVOLUTION"] = variations[
    "VARIATION_POINTS"
].apply(determiner_evolution)

variations.to_csv(
    OUTPUT_DIR / "variations_indicateurs_par_region.csv",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 7. IDENTIFICATION DES REGIONS A FAIBLES INDICATEURS
# =====================================================

regions_prioritaires = []

for indicateur in indicateurs:

    donnees = moyennes_region.sort_values(
        indicateur, ascending=True
    )

    for _, ligne in donnees.head(5).iterrows():

        regions_prioritaires.append({
            "INDICATEUR": indicateur,
            "REGION": ligne["REGION"],
            "VALEUR_MOYENNE": ligne[indicateur],
            "CRITERE": "5 moyennes régionales les plus faibles"
        })

regions_prioritaires = pd.DataFrame(regions_prioritaires)

regions_prioritaires.to_csv(
    OUTPUT_DIR / "regions_a_examiner_par_indicateur.csv",
    index=False,
    encoding="utf-8-sig"
)

# =====================================================
# 8. GRAPHIQUES DES MOYENNES REGIONALES
# =====================================================

for indicateur in indicateurs:

    donnees = moyennes_region.sort_values(indicateur)

    plt.figure(figsize=(11, 7))

    plt.barh(
        donnees["REGION"],
        donnees[indicateur]
    )

    plt.title(f"Moyenne régionale du {indicateur}")
    plt.xlabel(f"{indicateur} (%)")
    plt.ylabel("Région")
    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR / f"moyenne_regionale_{indicateur.lower()}.png",
        dpi=300
    )

    plt.close()

# =====================================================
# 9. GRAPHIQUES DES EVOLUTIONS REGIONALES
# =====================================================

for indicateur in indicateurs:

    plt.figure(figsize=(13, 7))

    for region in sorted(evolution["REGION"].unique()):

        donnees = evolution[
            evolution["REGION"] == region
        ]

        plt.plot(
            donnees["ANNEE_SCOLAIRE"],
            donnees[indicateur],
            marker="o",
            label=region
        )

    plt.title(f"Evolution régionale du {indicateur}")
    plt.xlabel("Année scolaire")
    plt.ylabel(f"{indicateur} (%)")
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR / f"evolution_regionale_{indicateur.lower()}.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

# =====================================================
# 10. AFFICHAGE DES RESULTATS
# =====================================================

print("\n===== MOYENNES DES INDICATEURS PAR REGION =====")
print(moyennes_region.round(2).to_string(index=False))

print("\n===== CLASSEMENT DES REGIONS =====")
print(classements.round(2).to_string(index=False))

print("\n===== VARIATIONS REGIONALES =====")
print(variations.round(2).to_string(index=False))

print("\n===== CINQ REGIONS AUX MOYENNES LES PLUS FAIBLES =====")
print(regions_prioritaires.round(2).to_string(index=False))

print("\nAnalyse des disparités régionales terminée.")
print(f"Tableaux : {OUTPUT_DIR}")
print(f"Graphiques : {GRAPH_DIR}")
