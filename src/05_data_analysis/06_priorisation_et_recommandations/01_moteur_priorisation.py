
import pandas as pd
from pathlib import Path

# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

DGESS_FILE = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "03_analyse_disparites_regionales"
    / "moyennes_indicateurs_par_region.csv"
)

INSD_FILE = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "04_analyse_urbain_rural"
    / "insd_rgph_2019"
    / "situation_scolaire_6_11_ans_par_region.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "outputs"
    / "analyses"
    / "06_priorisation_et_recommandations"
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 2. VERIFICATION DES FICHIERS
# ============================================================

print("\n========== VERIFICATION DES FICHIERS ==========")

for nom, chemin in [
    ("DGESS", DGESS_FILE),
    ("INSD", INSD_FILE)
]:
    print(nom, ":", chemin.exists())

    if not chemin.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {chemin}"
        )

# ============================================================
# 3. CHARGEMENT DES DONNEES
# ============================================================

dgess = pd.read_csv(DGESS_FILE)
insd = pd.read_csv(INSD_FILE)

print("\n========== DONNEES CHARGEES ==========")
print("DGESS :", dgess.shape)
print("INSD :", insd.shape)

# ============================================================
# 4. SELECTION DES INDICATEURS
# ============================================================

dgess = dgess[
    ["REGION", "TBA", "TBS", "TAP"]
].copy()

insd = insd[
    [
        "REGION",
        "DESCOLARISE_PCT",
        "JAMAIS_FREQUENTE_PCT",
        "SCOLARISE_PCT"
    ]
].copy()

# ============================================================
# 5. NORMALISATION DES NOMS DES REGIONS
# ============================================================

dgess["REGION"] = dgess["REGION"].str.strip().str.upper()
insd["REGION"] = insd["REGION"].str.strip().str.upper()

# Exclusion de la ligne nationale INSD
insd = insd[
    insd["REGION"] != "BURKINA FASO"
].copy()

# ============================================================
# 6. FUSION DES DONNEES
# ============================================================

df = pd.merge(
    dgess,
    insd,
    on="REGION",
    how="inner",
    validate="one_to_one"
)

print("\n========== FUSION DES DONNEES ==========")
print("Nombre de régions fusionnées :", len(df))
print(df.to_string(index=False))

# ============================================================
# 7. CONTROLES FINAUX
# ============================================================

if len(df) != 13:
    raise ValueError(
        "La fusion ne contient pas les 13 régions attendues."
    )

if df.isnull().any().any():
    raise ValueError(
        "Des valeurs manquantes sont présentes après fusion."
    )

if not df["REGION"].is_unique:
    raise ValueError(
        "Des régions apparaissent plusieurs fois."
    )

# ============================================================
# 8. EXPORTATION
# ============================================================

OUTPUT_FILE = OUTPUT_DIR / "indicateurs_priorisation.csv"

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nFusion terminée avec succès.")
print("Fichier enregistré :", OUTPUT_FILE)




# ============================================================
# 9. NORMALISATION DES INDICATEURS
# ============================================================

print("\n========== NORMALISATION DES INDICATEURS ==========")

# Pour ces deux indicateurs, une valeur faible
# représente une situation plus préoccupante.

df["PRIORITE_TAP"] = (
    (df["TAP"].max() - df["TAP"])
    / (df["TAP"].max() - df["TAP"].min())
) * 100

df["PRIORITE_SCOLARISATION"] = (
    (df["SCOLARISE_PCT"].max() - df["SCOLARISE_PCT"])
    / (
        df["SCOLARISE_PCT"].max()
        - df["SCOLARISE_PCT"].min()
    )
) * 100

# Pour cet indicateur, une valeur élevée
# représente une situation plus préoccupante.

df["PRIORITE_NON_FREQUENTATION"] = (
    (df["JAMAIS_FREQUENTE_PCT"] - df["JAMAIS_FREQUENTE_PCT"].min())
    / (
        df["JAMAIS_FREQUENTE_PCT"].max()
        - df["JAMAIS_FREQUENTE_PCT"].min()
    )
) * 100

# ============================================================
# 10. CALCUL DU SCORE DE PRIORITE
# ============================================================

print("\n========== CALCUL DU SCORE DE PRIORITE ==========")

df["SCORE_PRIORITE"] = (
    df["PRIORITE_TAP"] * 0.40
    + df["PRIORITE_SCOLARISATION"] * 0.30
    + df["PRIORITE_NON_FREQUENTATION"] * 0.30
)

# Classement : score le plus élevé = priorité la plus forte

df = df.sort_values(
    by="SCORE_PRIORITE",
    ascending=False
).reset_index(drop=True)

df["RANG_PRIORITE"] = range(1, len(df) + 1)

# ============================================================
# 11. AFFICHAGE DES RESULTATS
# ============================================================

print("\n========== CLASSEMENT TERRITORIAL ==========")

print(
    df[
        [
            "RANG_PRIORITE",
            "REGION",
            "SCORE_PRIORITE"
        ]
    ].round(2).to_string(index=False)
)

# ============================================================
# 12. EXPORTATION DU CLASSEMENT
# ============================================================

RESULT_FILE = OUTPUT_DIR / "classement_priorite_regions.csv"

df.to_csv(
    RESULT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nClassement enregistré :", RESULT_FILE)
print("\nCalcul du score terminé.")



# ============================================================
# 13. TEST DE SENSIBILITE DES PONDERATIONS
# ============================================================

print("\n========== TEST DE SENSIBILITE ==========")

scenarios = {
    "A_REFERENCE": {
        "TAP": 0.40,
        "SCOLARISATION": 0.30,
        "NON_FREQUENTATION": 0.30
    },
    "B_EQUILIBRE": {
        "TAP": 0.333333,
        "SCOLARISATION": 0.333333,
        "NON_FREQUENTATION": 0.333334
    },
    "C_ACCES_SCOLAIRE": {
        "TAP": 0.30,
        "SCOLARISATION": 0.40,
        "NON_FREQUENTATION": 0.30
    }
}

resultats_scenarios = []

for nom_scenario, poids in scenarios.items():

    scores = (
        df["PRIORITE_TAP"] * poids["TAP"]
        + df["PRIORITE_SCOLARISATION"]
        * poids["SCOLARISATION"]
        + df["PRIORITE_NON_FREQUENTATION"]
        * poids["NON_FREQUENTATION"]
    )

    classement = pd.DataFrame({
        "REGION": df["REGION"],
        "SCORE": scores
    }).sort_values(
        "SCORE",
        ascending=False
    ).reset_index(drop=True)

    classement["RANG"] = range(1, len(classement) + 1)

    for _, ligne in classement.iterrows():

        resultats_scenarios.append({
            "SCENARIO": nom_scenario,
            "REGION": ligne["REGION"],
            "SCORE": ligne["SCORE"],
            "RANG": ligne["RANG"]
        })

    print(f"\n--- {nom_scenario} ---")
    print(
        classement[
            ["RANG", "REGION", "SCORE"]
        ].round(2).to_string(index=False)
    )

# ============================================================
# 14. EXPORTATION DES RESULTATS
# ============================================================

sensibilite_df = pd.DataFrame(resultats_scenarios)

sensibilite_df.to_csv(
    OUTPUT_DIR / "test_sensibilite_ponderations.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nRésultats enregistrés dans :")
print(OUTPUT_DIR / "test_sensibilite_ponderations.csv")

print("\nTest de sensibilité terminé.")



# ============================================================
# 15. CLASSIFICATION DES NIVEAUX DE PRIORITE
# ============================================================

print("\n========== CLASSIFICATION TERRITORIALE ==========")

def definir_priorite(score):

    if score >= 60:
        return "PRIORITE ELEVEE"

    elif score >= 40:
        return "PRIORITE MOYENNE"

    else:
        return "PRIORITE FAIBLE"


df["NIVEAU_PRIORITE"] = df["SCORE_PRIORITE"].apply(
    definir_priorite
)

# ============================================================
# 16. CLASSEMENT FINAL
# ============================================================

classement_final = df[
    [
        "RANG_PRIORITE",
        "REGION",
        "SCORE_PRIORITE",
        "NIVEAU_PRIORITE"
    ]
].copy()

print(classement_final.round(2).to_string(index=False))

# ============================================================
# 17. EXPORTATION DU CLASSEMENT FINAL
# ============================================================

FINAL_FILE = OUTPUT_DIR / "classement_final_territorial.csv"

classement_final.to_csv(
    FINAL_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nClassement final enregistré :", FINAL_FILE)

# ============================================================
# 18. RESUME DES PRIORITES
# ============================================================

print("\n========== RESUME DES PRIORITES ==========")

print(
    classement_final["NIVEAU_PRIORITE"]
    .value_counts()
    .to_string()
)

print("\nClassification territoriale terminée.")
