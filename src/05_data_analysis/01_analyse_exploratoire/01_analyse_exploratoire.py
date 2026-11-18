
from pathlib import Path
import pandas as pd

# Définition des chemins du projet
ROOT_DIR = Path(__file__).resolve().parents[3]

DATA_DIR = ROOT_DIR / "data" / "04_transformed_data" / "merged"

OUTPUT_DIR = ROOT_DIR / "outputs" / "analyses" / "01_analyse_exploratoire"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Chargement des données
df_indicateurs = pd.read_csv(
    DATA_DIR / "indicateurs_regionaux_sexe.csv"
)

df_parite = pd.read_csv(
    DATA_DIR / "indices_parite_regionaux.csv"
)

# Définition des variables numériques
variables_indicateurs = [
    "EFFECTIF",
    "NOUVEAUX_INSCRITS_CP1",
    "TBA",
    "TBS",
    "TAP"
]

variables_parite = [
    "IPS_TBA",
    "IPS_TBS",
    "IPS_TAP"
]

# Analyse de la qualité des données
def analyser_qualite(df, nom_fichier):
    return {
        "FICHIER": nom_fichier,
        "NOMBRE_LIGNES": len(df),
        "NOMBRE_COLONNES": len(df.columns),
        "VALEURS_MANQUANTES": int(df.isna().sum().sum()),
        "LIGNES_DUPLIQUEES": int(df.duplicated().sum()),
        "NOMBRE_REGIONS": df["REGION"].nunique(),
        "NOMBRE_ANNEES": df["ANNEE_SCOLAIRE"].nunique()
    }

rapport_qualite = pd.DataFrame([
    analyser_qualite(df_indicateurs, "indicateurs_regionaux_sexe.csv"),
    analyser_qualite(df_parite, "indices_parite_regionaux.csv")
])

# Statistiques descriptives
stats_indicateurs = df_indicateurs[
    variables_indicateurs
].describe().T

stats_parite = df_parite[
    variables_parite
].describe().T

statistiques = pd.concat([
    stats_indicateurs,
    stats_parite
])

# Vérification des valeurs supérieures à 100
controle_indicateurs = []

for variable in ["TBA", "TBS", "TAP"]:
    controle_indicateurs.append({
        "INDICATEUR": variable,
        "VALEURS_INFERIEURES_A_ZERO": int(
            (df_indicateurs[variable] < 0).sum()
        ),
        "VALEURS_SUPERIEURES_A_100": int(
            (df_indicateurs[variable] > 100).sum()
        ),
        "VALEUR_MINIMALE": df_indicateurs[variable].min(),
        "VALEUR_MAXIMALE": df_indicateurs[variable].max()
    })

controle_indicateurs = pd.DataFrame(controle_indicateurs)

# Synthèse de la structure
synthese = pd.DataFrame([
    {
        "DIMENSION": "Régions",
        "NOMBRE": df_indicateurs["REGION"].nunique()
    },
    {
        "DIMENSION": "Années scolaires",
        "NOMBRE": df_indicateurs["ANNEE_SCOLAIRE"].nunique()
    },
    {
        "DIMENSION": "Sexes",
        "NOMBRE": df_indicateurs["SEXE"].nunique()
    },
    {
        "DIMENSION": "Observations indicateurs",
        "NOMBRE": len(df_indicateurs)
    },
    {
        "DIMENSION": "Observations parité",
        "NOMBRE": len(df_parite)
    }
])

# Exportation des résultats
rapport_qualite.to_csv(
    OUTPUT_DIR / "rapport_qualite_donnees.csv",
    index=False,
    encoding="utf-8-sig"
)

statistiques.to_csv(
    OUTPUT_DIR / "statistiques_descriptives.csv",
    encoding="utf-8-sig"
)

controle_indicateurs.to_csv(
    OUTPUT_DIR / "controle_valeurs_indicateurs.csv",
    index=False,
    encoding="utf-8-sig"
)

synthese.to_csv(
    OUTPUT_DIR / "synthese_structure_donnees.csv",
    index=False,
    encoding="utf-8-sig"
)

# Affichage des résultats
print("\n===== QUALITE DES DONNEES =====")
print(rapport_qualite.to_string(index=False))

print("\n===== STATISTIQUES DESCRIPTIVES =====")
print(statistiques.round(2).to_string())

print("\n===== CONTROLE DES INDICATEURS =====")
print(controle_indicateurs.round(2).to_string(index=False))

print("\n===== STRUCTURE DES DONNEES =====")
print(synthese.to_string(index=False))

print("\nAnalyse exploratoire initiale terminee.")
print(f"Resultats enregistres dans : {OUTPUT_DIR}")
