
import pandas as pd
import numpy as np

from pathlib import Path
from scipy.stats import (
    rankdata,
    friedmanchisquare,
    pearsonr,
    spearmanr
)
from statsmodels.stats.multitest import multipletests


# ============================================================
# 1. CONFIGURATION
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
    / "verification_robustesse"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INDICATEURS = ["TBA", "TBS", "TAP"]

ALPHA = 0.05


# ============================================================
# 2. CHARGEMENT ET VALIDATION
# ============================================================

print("\n========== VALIDATION DES DONNEES ==========")

if not INPUT_FILE.exists():
    raise FileNotFoundError(INPUT_FILE)

df = pd.read_csv(INPUT_FILE)

if df[["REGION"] + INDICATEURS].isnull().any().any():
    raise ValueError("Valeurs manquantes detectees.")

if df["REGION"].duplicated().any():
    raise ValueError("Regions dupliquees detectees.")

print("Nombre de regions :", len(df))
print("Donnees valides.")
print("Indicateurs :", INDICATEURS)


# ============================================================
# 3. CLASSEMENT DES REGIONS POUR CHAQUE INDICATEUR
# ============================================================

print("\n========== CLASSEMENT DES REGIONS ==========")

# Rang 1 = valeur la plus faible
rangs = df[["REGION"]].copy()

for indicateur in INDICATEURS:

    rangs[f"RANG_{indicateur}"] = (
        df[indicateur]
        .rank(method="average", ascending=True)
    )

print(rangs.to_string(index=False))

# Verification de l'ordre des regions
ordre_tba = df.sort_values("TBA")["REGION"].tolist()
ordre_tbs = df.sort_values("TBS")["REGION"].tolist()
ordre_tap = df.sort_values("TAP")["REGION"].tolist()

classement_identique = (
    ordre_tba == ordre_tbs == ordre_tap
)

print("\nOrdre TBA :", ordre_tba)
print("Ordre TBS :", ordre_tbs)
print("Ordre TAP :", ordre_tap)

print(
    "\nClassement strictement identique :",
    classement_identique
)

# Verification des ex aequo
nb_rangs_distincts = {
    indicateur: rangs[f"RANG_{indicateur}"].nunique()
    for indicateur in INDICATEURS
}

print("\nNombre de rangs distincts :")
print(nb_rangs_distincts)


# ============================================================
# 4. VERIFICATION INDEPENDANTE DE KENDALL W
# ============================================================

print("\n========== VERIFICATION DE KENDALL W ==========")

# Matrice : lignes = regions, colonnes = indicateurs
matrice_rangs = np.column_stack([
    rankdata(df[indicateur], method="average")
    for indicateur in INDICATEURS
])

n = len(df)
k = len(INDICATEURS)

# Somme des rangs pour chaque region
sommes_rangs = matrice_rangs.sum(axis=1)

# Moyenne theorique des sommes de rangs
moyenne_sommes = k * (n + 1) / 2

# Somme des ecarts au carre
S = np.sum((sommes_rangs - moyenne_sommes) ** 2)

# Correction pour les ex aequo
correction_ties = 0

for indicateur in INDICATEURS:

    valeurs = df[indicateur].to_numpy()

    _, effectifs = np.unique(
        valeurs,
        return_counts=True
    )

    correction_ties += np.sum(
        effectifs**3 - effectifs
    )

# Denominateur corrige
denominateur = k**2 * (n**3 - n) - k * correction_ties

if denominateur == 0:
    raise ValueError(
        "Impossible de calculer Kendall W avec ces donnees."
    )

kendall_w_verifie = (12 * S) / denominateur

# Test de Friedman
stat_friedman, p_friedman = friedmanchisquare(
    df["TBA"],
    df["TBS"],
    df["TAP"]
)

print("Somme S :", round(S, 5))
print("Correction ex aequo :", correction_ties)
print("Kendall W verifie :", round(kendall_w_verifie, 5))
print("Statistique Friedman :", round(stat_friedman, 5))
print("P-value :", p_friedman)

print(
    "Classement parfaitement concordant :",
    np.isclose(kendall_w_verifie, 1.0)
)

# Export des rangs
rangs.to_csv(
    OUTPUT_DIR / "classement_rangs_regions.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 5. CALCUL DES CORRELATIONS
# ============================================================

print("\n========== CORRELATIONS ET CORRECTION DE HOLM ==========")

comparaisons = [
    ("TBA", "TBS"),
    ("TBA", "TAP"),
    ("TBS", "TAP")
]

resultats = []

for methode in ["PEARSON", "SPEARMAN"]:

    p_values = []
    lignes_methode = []

    for indicateur_1, indicateur_2 in comparaisons:

        x = df[indicateur_1]
        y = df[indicateur_2]

        if methode == "PEARSON":

            coefficient, p_value = pearsonr(x, y)

        else:

            coefficient, p_value = spearmanr(x, y)

        lignes_methode.append({
            "METHODE": methode,
            "COMPARAISON": (
                f"{indicateur_1} vs {indicateur_2}"
            ),
            "COEFFICIENT": coefficient,
            "P_VALUE_BRUTE": p_value
        })

        p_values.append(p_value)

    # Correction de Holm pour chaque famille de tests
    rejets, p_corrigees, _, _ = multipletests(
        p_values,
        alpha=ALPHA,
        method="holm"
    )

    for i, ligne in enumerate(lignes_methode):

        ligne["P_VALUE_HOLM"] = p_corrigees[i]

        ligne["SIGNIFICATIF_APRES_HOLM"] = rejets[i]

        ligne["DECISION"] = (
            "Significatif"
            if rejets[i]
            else "Non significatif"
        )

        resultats.append(ligne)


correlations_df = pd.DataFrame(resultats)

print(
    correlations_df.round(6).to_string(index=False)
)

correlations_df.to_csv(
    OUTPUT_DIR / "correlations_corrigees_holm.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 6. VERIFICATION DES CONCLUSIONS
# ============================================================

print("\n========== VERIFICATION DES CONCLUSIONS ==========")

print(
    "Kendall W = 1 :",
    np.isclose(kendall_w_verifie, 1.0)
)

print(
    "Classement identique :",
    classement_identique
)

print(
    "Toutes les correlations restent significatives :",
    correlations_df["SIGNIFICATIF_APRES_HOLM"].all()
)

print(
    "\nNombre de correlations significatives apres Holm :",
    correlations_df["SIGNIFICATIF_APRES_HOLM"].sum(),
    "/",
    len(correlations_df)
)


# ============================================================
# 7. RAPPORT DE VERIFICATION
# ============================================================

rapport = []

rapport.append("VERIFICATION DE ROBUSTESSE STATISTIQUE")
rapport.append("PROJET EDU EQUITY BF")
rapport.append("=" * 60)

rapport.append(
    f"\nNombre de regions : {n}"
)

rapport.append(
    f"Nombre d'indicateurs : {k}"
)

rapport.append(
    f"\nClassement strictement identique : {classement_identique}"
)

rapport.append(
    f"Kendall W verifie : {kendall_w_verifie:.5f}"
)

rapport.append(
    f"Statistique Friedman : {stat_friedman:.5f}"
)

rapport.append(
    f"P-value Friedman : {p_friedman:.8g}"
)

rapport.append(
    "\nCORRELATIONS APRES CORRECTION DE HOLM"
)

for _, ligne in correlations_df.iterrows():

    rapport.append(
        f"{ligne['METHODE']} - {ligne['COMPARAISON']} : "
        f"coefficient = {ligne['COEFFICIENT']:.5f}, "
        f"p brute = {ligne['P_VALUE_BRUTE']:.8g}, "
        f"p Holm = {ligne['P_VALUE_HOLM']:.8g}, "
        f"{ligne['DECISION']}"
    )

rapport.append(
    "\nLes corrections de Holm sont appliquees "
    "separement aux familles Pearson et Spearman."
)

rapport.append(
    "\nCette verification confirme la concordance des rangs "
    "et examine la robustesse des correlations."
)

rapport.append(
    "\nElle ne demontre pas de causalite et ne constitue "
    "pas un test de differences entre les regions."
)

rapport_final = "\n".join(rapport)

with open(
    OUTPUT_DIR / "rapport_verification.txt",
    "w",
    encoding="utf-8"
) as fichier:

    fichier.write(rapport_final)

print("\n========== RAPPORT FINAL ==========")
print(rapport_final)

print("\nFichiers enregistres dans :")
print(OUTPUT_DIR)

print("\nVerification terminee avec succes.")
