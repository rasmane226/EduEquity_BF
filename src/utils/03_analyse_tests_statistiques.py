
import pandas as pd
import numpy as np

from pathlib import Path
from scipy.stats import (
    shapiro,
    friedmanchisquare,
    wilcoxon
)
from statsmodels.stats.multitest import multipletests


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
    / "tests_statistiques"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CHARGEMENT ET VALIDATION DES DONNEES
# ============================================================

print("\n========== CHARGEMENT DES DONNEES ==========")

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Fichier introuvable : {INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)

indicateurs = ["TBA", "TBS", "TAP"]

colonnes_requises = ["REGION"] + indicateurs

if not all(col in df.columns for col in colonnes_requises):
    raise ValueError("Certaines colonnes requises sont absentes.")

if df[colonnes_requises].isnull().any().any():
    raise ValueError("Des valeurs manquantes sont presentes.")

if df["REGION"].duplicated().any():
    raise ValueError("Des regions sont dupliquees.")

if len(df) < 3:
    raise ValueError("Nombre de regions insuffisant.")

print("Nombre de regions :", len(df))
print("Indicateurs :", indicateurs)
print("Aucune valeur manquante.")
print("Aucune region dupliquee.")


# ============================================================
# 3. TEST DE NORMALITE : SHAPIRO-WILK
# ============================================================

print("\n========== TEST DE NORMALITE ==========")

resultats_shapiro = []

for indicateur in indicateurs:

    valeurs = df[indicateur].dropna()

    statistique, p_value = shapiro(valeurs)

    decision = (
        "Rejet de la normalite"
        if p_value < 0.05
        else "Normalite non rejetee"
    )

    resultats_shapiro.append({
        "INDICATEUR": indicateur,
        "STATISTIQUE_W": statistique,
        "P_VALUE": p_value,
        "DECISION": decision
    })

    print(f"\n{indicateur}")
    print("Statistique W :", round(statistique, 5))
    print("P-value :", round(p_value, 5))
    print("Decision :", decision)

shapiro_df = pd.DataFrame(resultats_shapiro)

shapiro_df.to_csv(
    OUTPUT_DIR / "resultats_shapiro.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 4. TEST DE FRIEDMAN
# COMPARAISON DES TROIS INDICATEURS APPARIES
# ============================================================

print("\n========== TEST DE FRIEDMAN ==========")

stat_friedman, p_friedman = friedmanchisquare(
    df["TBA"],
    df["TBS"],
    df["TAP"]
)

n = len(df)
k = len(indicateurs)

# Coefficient W de Kendall
kendall_w = stat_friedman / (n * (k - 1))

decision_friedman = (
    "Difference statistiquement significative"
    if p_friedman < 0.05
    else "Aucune difference statistiquement significative detectee"
)

print("Statistique de Friedman :", round(stat_friedman, 5))
print("P-value :", round(p_friedman, 8))
print("Kendall W :", round(kendall_w, 5))
print("Decision :", decision_friedman)

friedman_df = pd.DataFrame([{
    "NOMBRE_REGIONS": n,
    "NOMBRE_INDICATEURS": k,
    "STATISTIQUE_FRIEDMAN": stat_friedman,
    "P_VALUE": p_friedman,
    "KENDALL_W": kendall_w,
    "DECISION": decision_friedman
}])

friedman_df.to_csv(
    OUTPUT_DIR / "resultat_friedman.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 5. COMPARAISONS DEUX A DEUX : WILCOXON
# ============================================================

print("\n========== TESTS DE WILCOXON ==========")

comparaisons = [
    ("TBA", "TBS"),
    ("TBA", "TAP"),
    ("TBS", "TAP")
]

resultats_wilcoxon = []

for indicateur_1, indicateur_2 in comparaisons:

    valeurs_1 = df[indicateur_1].to_numpy()
    valeurs_2 = df[indicateur_2].to_numpy()

    differences = valeurs_1 - valeurs_2

    # Verification des differences nulles
    if np.allclose(differences, 0):
        statistique = 0.0
        p_value = 1.0
    else:
        statistique, p_value = wilcoxon(
            valeurs_1,
            valeurs_2,
            alternative="two-sided",
            method="auto"
        )

    mediane_difference = np.median(differences)

    resultats_wilcoxon.append({
        "COMPARAISON": f"{indicateur_1} vs {indicateur_2}",
        "MEDIANE_DIFFERENCE": mediane_difference,
        "STATISTIQUE_W": statistique,
        "P_VALUE_BRUTE": p_value
    })

    print(f"\n{indicateur_1} vs {indicateur_2}")
    print("Mediane des differences :", round(mediane_difference, 4))
    print("Statistique :", round(statistique, 5))
    print("P-value brute :", round(p_value, 8))


# ============================================================
# 6. CORRECTION DE HOLM
# ============================================================

print("\n========== CORRECTION DE HOLM ==========")

wilcoxon_df = pd.DataFrame(resultats_wilcoxon)

p_values = wilcoxon_df["P_VALUE_BRUTE"].to_numpy()

rejets, p_values_corrigees, _, _ = multipletests(
    p_values,
    alpha=0.05,
    method="holm"
)

wilcoxon_df["P_VALUE_HOLM"] = p_values_corrigees

wilcoxon_df["SIGNIFICATIF_APRES_HOLM"] = rejets

wilcoxon_df["DECISION"] = [
    "Difference significative"
    if rejet
    else "Difference non significative"
    for rejet in rejets
]

print(
    wilcoxon_df[
        [
            "COMPARAISON",
            "P_VALUE_BRUTE",
            "P_VALUE_HOLM",
            "DECISION"
        ]
    ].to_string(index=False)
)

wilcoxon_df.to_csv(
    OUTPUT_DIR / "resultats_wilcoxon_holm.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 7. SYNTHESE DES RESULTATS
# ============================================================

print("\n========== SYNTHESE DES TESTS STATISTIQUES ==========")

print("\nTest de Friedman :")
print("P-value :", round(p_friedman, 8))
print("Kendall W :", round(kendall_w, 5))

if p_friedman < 0.05:
    print("Les rangs des trois indicateurs different significativement.")
else:
    print("Aucune difference significative n'a ete detectee.")

print("\nComparaisons de Wilcoxon apres correction de Holm :")

for _, ligne in wilcoxon_df.iterrows():

    print(
        ligne["COMPARAISON"],
        "->",
        ligne["DECISION"],
        "| P-value corrigee :",
        round(ligne["P_VALUE_HOLM"], 8)
    )

print("\nAnalyse statistique terminee.")
print("Resultats enregistres dans :")
print(OUTPUT_DIR)
