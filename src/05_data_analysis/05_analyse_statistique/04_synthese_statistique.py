
import pandas as pd
from pathlib import Path
from scipy.stats import pearsonr, spearmanr

# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

DATA_FILE = (
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
    / "synthese_finale"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\n========== CONFIGURATION ==========")
print("Dossier racine :", BASE_DIR)
print("Fichier source :", DATA_FILE)
print("Fichier existant :", DATA_FILE.exists())

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"Fichier source introuvable : {DATA_FILE}"
    )

# ============================================================
# 2. CHARGEMENT ET CONTROLE DES DONNEES
# ============================================================

df = pd.read_csv(DATA_FILE)

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

if not df["REGION"].is_unique:
    raise ValueError(
        "Des régions apparaissent plusieurs fois dans les données."
    )

print("\n========== CONTROLE DES DONNEES ==========")
print("Nombre de régions :", df["REGION"].nunique())
print("Dimensions :", df.shape)
print("Valeurs manquantes : 0")

# ============================================================
# 3. STATISTIQUES DESCRIPTIVES
# ============================================================

print("\n========== STATISTIQUES DESCRIPTIVES ==========")

statistiques = df[indicateurs].describe().T

statistiques["IQR"] = (
    df[indicateurs].quantile(0.75)
    - df[indicateurs].quantile(0.25)
)

statistiques["COEFFICIENT_VARIATION_PCT"] = (
    df[indicateurs].std()
    / df[indicateurs].mean()
) * 100

statistiques["ETENDUE"] = (
    df[indicateurs].max()
    - df[indicateurs].min()
)

print(statistiques.round(3))

statistiques.to_csv(
    OUTPUT_DIR / "statistiques_descriptives.csv",
    encoding="utf-8-sig"
)

# ============================================================
# 4. ANALYSE DES CORRELATIONS
# ============================================================

print("\n========== ANALYSE DES CORRELATIONS ==========")

comparaisons = [
    ("TBA", "TBS"),
    ("TBA", "TAP"),
    ("TBS", "TAP")
]

resultats_correlations = []

for indicateur_1, indicateur_2 in comparaisons:

    x = df[indicateur_1]
    y = df[indicateur_2]

    pearson_r, pearson_p = pearsonr(x, y)

    spearman_rho, spearman_p = spearmanr(x, y)

    resultats_correlations.append({
        "COMPARAISON": f"{indicateur_1} - {indicateur_2}",
        "PEARSON_R": pearson_r,
        "SPEARMAN_RHO": spearman_rho
    })

correlations_df = pd.DataFrame(
    resultats_correlations
)

print(correlations_df.round(4).to_string(index=False))

correlations_df.to_csv(
    OUTPUT_DIR / "correlations_statistiques.csv",
    index=False,
    encoding="utf-8-sig"
)

# ============================================================
# 5. IDENTIFICATION DES VALEURS ATYPIQUES
# METHODE : INTERVALLE INTERQUARTILE (IQR)
# ============================================================

print("\n========== DETECTION DES VALEURS ATYPIQUES ==========")

resultats_extremes = []

for indicateur in indicateurs:

    Q1 = df[indicateur].quantile(0.25)
    Q3 = df[indicateur].quantile(0.75)

    IQR = Q3 - Q1

    borne_inferieure = Q1 - 1.5 * IQR
    borne_superieure = Q3 + 1.5 * IQR

    valeurs_extremes = df[
        (df[indicateur] < borne_inferieure)
        | (df[indicateur] > borne_superieure)
    ]

    print(f"\n{indicateur}")
    print("Nombre de valeurs atypiques :", len(valeurs_extremes))

    for _, ligne in valeurs_extremes.iterrows():

        resultats_extremes.append({
            "REGION": ligne["REGION"],
            "INDICATEUR": indicateur,
            "VALEUR": ligne[indicateur],
            "BORNE_INFERIEURE": borne_inferieure,
            "BORNE_SUPERIEURE": borne_superieure
        })

extremes_df = pd.DataFrame(
    resultats_extremes,
    columns=[
        "REGION",
        "INDICATEUR",
        "VALEUR",
        "BORNE_INFERIEURE",
        "BORNE_SUPERIEURE"
    ]
)

extremes_df.to_csv(
    OUTPUT_DIR / "valeurs_atypiques.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nNombre total de valeurs atypiques :", len(extremes_df))

# ============================================================
# 6. IDENTIFICATION DE L'INDICATEUR LE PLUS DISPERSE
# ============================================================

print("\n========== ANALYSE DE LA DISPERSION ==========")

indicateur_plus_disperse = (
    statistiques["COEFFICIENT_VARIATION_PCT"].idxmax()
)

cv_max = statistiques.loc[
    indicateur_plus_disperse,
    "COEFFICIENT_VARIATION_PCT"
]

print("Indicateur le plus dispersé :", indicateur_plus_disperse)
print("Coefficient de variation :", round(cv_max, 3), "%")

# ============================================================
# 7. CONSTRUCTION DU RAPPORT FINAL
# ============================================================

rapport = []

rapport.append("RAPPORT DE SYNTHESE STATISTIQUE")
rapport.append("PROJET EDU EQUITY BF")
rapport.append("=" * 65)

rapport.append("\n1. DESCRIPTION GENERALE")

rapport.append(
    f"Nombre de régions analysées : {len(df)}"
)

rapport.append(
    "Indicateurs étudiés : TBA, TBS et TAP."
)

rapport.append(
    "Unité d'analyse : 13 moyennes régionales."
)

rapport.append(
    "Les moyennes régionales sont calculées sur les observations disponibles "
    "et ne constituent pas des moyennes nationales pondérées."
)

rapport.append("\n2. STATISTIQUES DESCRIPTIVES")

for indicateur in indicateurs:

    ligne = statistiques.loc[indicateur]

    rapport.append(
        f"\n{indicateur} : "
        f"moyenne = {ligne['mean']:.2f}, "
        f"médiane = {ligne['50%']:.2f}, "
        f"minimum = {ligne['min']:.2f}, "
        f"maximum = {ligne['max']:.2f}, "
        f"écart-type = {ligne['std']:.2f}, "
        f"IQR = {ligne['IQR']:.2f}, "
        f"CV = {ligne['COEFFICIENT_VARIATION_PCT']:.2f}%."
    )

rapport.append("\n3. ANALYSE DES CORRELATIONS")

for _, ligne in correlations_df.iterrows():

    rapport.append(
        f"\n{ligne['COMPARAISON']} : "
        f"Pearson r = {ligne['PEARSON_R']:.4f}, "
        f"Spearman rho = {ligne['SPEARMAN_RHO']:.4f}."
    )

rapport.append(
    "Les corrélations indiquent des associations entre les indicateurs, "
    "mais ne démontrent aucune relation de causalité."
)

rapport.append("\n4. ANALYSE DE LA DISPERSION")

rapport.append(
    f"L'indicateur présentant la dispersion relative la plus importante "
    f"est {indicateur_plus_disperse}, avec un CV de {cv_max:.2f}%."
)

rapport.append("\n5. VALEURS ATYPIQUES")

if extremes_df.empty:

    rapport.append("Aucune valeur atypique détectée.")

else:

    for _, ligne in extremes_df.iterrows():

        rapport.append(
            f"{ligne['REGION']} - {ligne['INDICATEUR']} : "
            f"{ligne['VALEUR']:.2f}."
        )

rapport.append(
    "Les valeurs atypiques ne sont pas automatiquement des erreurs. "
    "Elles doivent être interprétées dans leur contexte territorial."
)

rapport.append("\n6. LIMITES METHODOLOGIQUES")

rapport.append(
    "- L'analyse repose sur seulement 13 observations régionales."
)

rapport.append(
    "- Les résultats ne représentent pas les observations individuelles des élèves."
)

rapport.append(
    "- Les corrélations ne démontrent pas de causalité."
)

rapport.append(
    "- Les moyennes régionales ne sont pas pondérées par les effectifs."
)

rapport.append(
    "- Les valeurs atypiques identifiées par la méthode IQR "
    "ne constituent pas nécessairement des erreurs."
)

rapport.append("\n7. CONCLUSION")

rapport.append(
    f"Les analyses montrent une dispersion relative particulièrement "
    f"importante du {indicateur_plus_disperse} entre les régions."
)

rapport.append(
    "Les associations positives entre les trois indicateurs "
    "et les disparités observées constituent une base descriptive "
    "pour approfondir la priorisation territoriale dans EduEquity BF."
)

rapport_final = "\n".join(rapport)

# ============================================================
# 8. ENREGISTREMENT DU RAPPORT
# ============================================================

rapport_path = (
    OUTPUT_DIR / "rapport_synthese_statistique.txt"
)

with open(
    rapport_path,
    "w",
    encoding="utf-8"
) as fichier:

    fichier.write(rapport_final)

# ============================================================
# 9. SYNTHESE GLOBALE
# ============================================================

synthese_globale = statistiques[
    [
        "mean",
        "50%",
        "std",
        "min",
        "max",
        "IQR",
        "COEFFICIENT_VARIATION_PCT"
    ]
].copy()

synthese_globale = synthese_globale.rename(
    columns={
        "mean": "MOYENNE",
        "50%": "MEDIANE",
        "std": "ECART_TYPE",
        "min": "MINIMUM",
        "max": "MAXIMUM",
        "IQR": "IQR",
        "COEFFICIENT_VARIATION_PCT": "CV_PCT"
    }
)

synthese_globale["NOMBRE_VALEURS_ATYPIQUES"] = [
    len(
        extremes_df[
            extremes_df["INDICATEUR"] == indicateur
        ]
    )
    for indicateur in indicateurs
]

synthese_globale.to_csv(
    OUTPUT_DIR / "synthese_statistique_globale.csv",
    encoding="utf-8-sig"
)

# ============================================================
# 10. AFFICHAGE FINAL
# ============================================================

print("\n========== RAPPORT FINAL ==========")
print(rapport_final)

print("\n========== EXPORTATION TERMINEE ==========")

print("Dossier des résultats :", OUTPUT_DIR)

print("\nFichiers générés :")
print("- statistiques_descriptives.csv")
print("- correlations_statistiques.csv")
print("- valeurs_atypiques.csv")
print("- synthese_statistique_globale.csv")
print("- rapport_synthese_statistique.txt")

print("\nSynthèse statistique terminée avec succès.")
