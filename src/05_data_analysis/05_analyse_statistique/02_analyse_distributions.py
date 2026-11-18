
import pandas as pd
from pathlib import Path

# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

# Racine du projet EduEquity_BF
BASE_DIR = Path(__file__).resolve().parents[3]

# Fichier de données en entrée
INPUT_FILE = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "03_analyse_disparites_regionales"
    / "moyennes_indicateurs_par_region.csv"
)

# Dossier de sauvegarde des résultats
OUTPUT_DIR = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "05_analyse_statistique"
    / "distributions"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\n========== CONFIGURATION ==========")
print("Dossier racine :", BASE_DIR)
print("Fichier recherché :", INPUT_FILE)
print("Fichier existant :", INPUT_FILE.exists())

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Le fichier source est introuvable : {INPUT_FILE}"
    )

# ============================================================
# 2. CHARGEMENT ET CONTROLE DES DONNEES
# ============================================================

df = pd.read_csv(INPUT_FILE)

indicateurs = ["TBA", "TBS", "TAP"]
colonnes_requises = ["REGION"] + indicateurs

colonnes_absentes = [
    colonne for colonne in colonnes_requises
    if colonne not in df.columns
]

if colonnes_absentes:
    raise ValueError(
        f"Colonnes absentes dans le fichier : {colonnes_absentes}"
    )

print("\n========== CONTROLE DES DONNEES ==========")
print("Dimensions :", df.shape)
print("Nombre de régions :", df["REGION"].nunique())

print("\nValeurs manquantes :")
print(df[colonnes_requises].isnull().sum())

if df[indicateurs].isnull().any().any():
    raise ValueError(
        "Des valeurs manquantes sont présentes dans les indicateurs."
    )

# ============================================================
# 3. STATISTIQUES DESCRIPTIVES
# ============================================================

statistiques = df[indicateurs].describe().T

# Variance
statistiques["variance"] = df[indicateurs].var()

# Étendue
statistiques["etendue"] = (
    df[indicateurs].max() - df[indicateurs].min()
)

# Intervalle interquartile
statistiques["IQR"] = (
    df[indicateurs].quantile(0.75)
    - df[indicateurs].quantile(0.25)
)

# Coefficient de variation en pourcentage
statistiques["coefficient_variation_pct"] = (
    df[indicateurs].std()
    / df[indicateurs].mean()
) * 100

print("\n========== STATISTIQUES DESCRIPTIVES ==========")
print(statistiques.round(3))

statistiques.to_csv(
    OUTPUT_DIR / "statistiques_distributions.csv",
    encoding="utf-8-sig"
)

# ============================================================
# 4. IDENTIFICATION DES VALEURS ATYPIQUES
# METHODE : INTERVALLE INTERQUARTILE (IQR)
# ============================================================

resultats_extremes = []

print("\n========== DETECTION DES VALEURS ATYPIQUES ==========")

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

    print(f"\nIndicateur : {indicateur}")
    print("Q1 :", round(Q1, 3))
    print("Q3 :", round(Q3, 3))
    print("IQR :", round(IQR, 3))
    print("Borne inférieure :", round(borne_inferieure, 3))
    print("Borne supérieure :", round(borne_superieure, 3))
    print("Nombre de valeurs atypiques :", len(valeurs_extremes))

    for _, ligne in valeurs_extremes.iterrows():

        resultats_extremes.append({
            "REGION": ligne["REGION"],
            "INDICATEUR": indicateur,
            "VALEUR": ligne[indicateur],
            "BORNE_INFERIEURE": borne_inferieure,
            "BORNE_SUPERIEURE": borne_superieure
        })

# Conversion en DataFrame
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
    OUTPUT_DIR / "valeurs_extremes.csv",
    index=False,
    encoding="utf-8-sig"
)

# ============================================================
# 5. COMPARAISON DE LA DISPERSION
# ============================================================

dispersion = pd.DataFrame({
    "INDICATEUR": indicateurs,

    "ECART_TYPE": [
        df[col].std()
        for col in indicateurs
    ],

    "COEFFICIENT_VARIATION_PCT": [
        (df[col].std() / df[col].mean()) * 100
        for col in indicateurs
    ]
})

print("\n========== COMPARAISON DE LA DISPERSION ==========")
print(dispersion.round(3))

dispersion.to_csv(
    OUTPUT_DIR / "comparaison_dispersion.csv",
    index=False,
    encoding="utf-8-sig"
)

# ============================================================
# 6. SYNTHESE FINALE
# ============================================================

print("\n========== SYNTHESE FINALE ==========")

print("Nombre de régions analysées :", len(df))

for indicateur in indicateurs:

    moyenne = df[indicateur].mean()
    mediane = df[indicateur].median()
    minimum = df[indicateur].min()
    maximum = df[indicateur].max()
    ecart_type = df[indicateur].std()
    cv = (ecart_type / moyenne) * 100

    print(f"\n{indicateur}")
    print("Moyenne :", round(moyenne, 2))
    print("Médiane :", round(mediane, 2))
    print("Minimum :", round(minimum, 2))
    print("Maximum :", round(maximum, 2))
    print("Écart-type :", round(ecart_type, 2))
    print("Coefficient de variation :", round(cv, 2), "%")

print("\nNombre total de valeurs atypiques :", len(extremes_df))

print("\nAnalyse des distributions terminée.")
print("Résultats enregistrés dans :")
print(OUTPUT_DIR)
