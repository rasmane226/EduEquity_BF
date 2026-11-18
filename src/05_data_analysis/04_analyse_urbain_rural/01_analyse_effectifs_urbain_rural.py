
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# 1. Chemins
# --------------------------------------------------

RACINE_PROJET = Path(__file__).resolve().parents[3]

FICHIER_ENTREE = (
    RACINE_PROJET
    / "data"
    / "04_transformed_data"
    / "merged"
    / "comparaison_effectifs_urbain_rural.csv"
)

DOSSIER_SORTIE = (
    RACINE_PROJET
    / "outputs"
    / "analyses"
    / "04_analyse_urbain_rural"
)

DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. Chargement et contrôle des données
# --------------------------------------------------

df = pd.read_csv(FICHIER_ENTREE)

colonnes_requises = [
    "ANNEE_SCOLAIRE",
    "SEXE",
    "EFFECTIF_URBAIN",
    "EFFECTIF_RURAL",
    "ECART_URBAIN_MOINS_RURAL",
    "ECART_ABSOLU",
    "RATIO_URBAIN_RURAL"
]

assert all(col in df.columns for col in colonnes_requises), (
    "Certaines colonnes requises sont absentes."
)

assert df[colonnes_requises].notna().all().all(), (
    "Des valeurs manquantes ont été détectées."
)

assert not df.duplicated(
    subset=["ANNEE_SCOLAIRE", "SEXE"]
).any(), "Des doublons ont été détectés."

assert (df["EFFECTIF_URBAIN"] >= 0).all()
assert (df["EFFECTIF_RURAL"] >= 0).all()

# Vérification des indicateurs déjà calculés
ecart_calcule = (
    df["EFFECTIF_URBAIN"] - df["EFFECTIF_RURAL"]
)

ratio_calcule = (
    df["EFFECTIF_URBAIN"] / df["EFFECTIF_RURAL"]
)

assert (
    ecart_calcule - df["ECART_URBAIN_MOINS_RURAL"]
).abs().max() < 0.01

assert (
    ratio_calcule - df["RATIO_URBAIN_RURAL"]
).abs().max() < 0.00001

print("=== QUALITE DES DONNEES ===")
print("Nombre d'observations :", len(df))
print("Nombre d'annees :", df["ANNEE_SCOLAIRE"].nunique())
print("Nombre de sexes :", df["SEXE"].nunique())
print("Valeurs manquantes :", df.isna().sum().sum())
print("Doublons :", df.duplicated(
    ["ANNEE_SCOLAIRE", "SEXE"]
).sum())


# --------------------------------------------------
# 3. Statistiques descriptives par sexe
# --------------------------------------------------

statistiques_sexe = df.groupby("SEXE").agg(
    EFFECTIF_URBAIN_MOYEN=("EFFECTIF_URBAIN", "mean"),
    EFFECTIF_RURAL_MOYEN=("EFFECTIF_RURAL", "mean"),
    EFFECTIF_URBAIN_MIN=("EFFECTIF_URBAIN", "min"),
    EFFECTIF_URBAIN_MAX=("EFFECTIF_URBAIN", "max"),
    EFFECTIF_RURAL_MIN=("EFFECTIF_RURAL", "min"),
    EFFECTIF_RURAL_MAX=("EFFECTIF_RURAL", "max"),
    RATIO_MOYEN=("RATIO_URBAIN_RURAL", "mean")
).round(2)

statistiques_sexe.to_csv(
    DOSSIER_SORTIE / "statistiques_urbain_rural_par_sexe.csv",
    index=True,
    encoding="utf-8-sig"
)

print("\n=== STATISTIQUES PAR SEXE ===")
print(statistiques_sexe)


# --------------------------------------------------
# 4. Evolution annuelle des effectifs
# --------------------------------------------------

evolution = df.groupby("ANNEE_SCOLAIRE").agg(
    EFFECTIF_URBAIN_TOTAL=("EFFECTIF_URBAIN", "sum"),
    EFFECTIF_RURAL_TOTAL=("EFFECTIF_RURAL", "sum"),
    ECART_TOTAL=("ECART_URBAIN_MOINS_RURAL", "sum")
).reset_index()

evolution["RATIO_URBAIN_RURAL"] = (
    evolution["EFFECTIF_URBAIN_TOTAL"]
    / evolution["EFFECTIF_RURAL_TOTAL"]
)

evolution["PART_URBAINE_DANS_TOTAL"] = (
    evolution["EFFECTIF_URBAIN_TOTAL"]
    / (
        evolution["EFFECTIF_URBAIN_TOTAL"]
        + evolution["EFFECTIF_RURAL_TOTAL"]
    )
    * 100
)

evolution = evolution.round(2)

evolution.to_csv(
    DOSSIER_SORTIE / "evolution_annuelle_urbain_rural.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\n=== EVOLUTION ANNUELLE ===")
print(evolution.to_string(index=False))


# --------------------------------------------------
# 5. Evolution des écarts selon le sexe
# --------------------------------------------------

evolution_sexe = df[
    [
        "ANNEE_SCOLAIRE",
        "SEXE",
        "EFFECTIF_URBAIN",
        "EFFECTIF_RURAL",
        "ECART_URBAIN_MOINS_RURAL",
        "RATIO_URBAIN_RURAL"
    ]
].copy()

evolution_sexe.to_csv(
    DOSSIER_SORTIE / "evolution_urbain_rural_par_sexe.csv",
    index=False,
    encoding="utf-8-sig"
)


# --------------------------------------------------
# 6. Variation entre la premiere et la derniere annee
# --------------------------------------------------

annees = sorted(df["ANNEE_SCOLAIRE"].unique())

premiere_annee = annees[0]
derniere_annee = annees[-1]

debut = df[df["ANNEE_SCOLAIRE"] == premiere_annee].set_index("SEXE")
fin = df[df["ANNEE_SCOLAIRE"] == derniere_annee].set_index("SEXE")

comparaison = pd.DataFrame(index=debut.index)

for colonne in ["EFFECTIF_URBAIN", "EFFECTIF_RURAL"]:
    comparaison[f"{colonne}_DEBUT"] = debut[colonne]
    comparaison[f"{colonne}_FIN"] = fin[colonne]

    comparaison[f"VARIATION_{colonne}_POURCENT"] = (
        (fin[colonne] - debut[colonne])
        / debut[colonne]
        * 100
    )

comparaison = comparaison.round(2)

comparaison.to_csv(
    DOSSIER_SORTIE / "variation_effectifs_periode.csv",
    index=True,
    encoding="utf-8-sig"
)

print("\n=== VARIATION SUR LA PERIODE ===")
print(comparaison)


# --------------------------------------------------
# 7. Graphique : evolution des effectifs urbains et ruraux
# --------------------------------------------------

plt.figure(figsize=(12, 6))

plt.plot(
    evolution["ANNEE_SCOLAIRE"],
    evolution["EFFECTIF_URBAIN_TOTAL"],
    marker="o",
    label="Milieu urbain"
)

plt.plot(
    evolution["ANNEE_SCOLAIRE"],
    evolution["EFFECTIF_RURAL_TOTAL"],
    marker="o",
    label="Milieu rural"
)

plt.title("Evolution des effectifs scolaires selon le milieu")
plt.xlabel("Annee scolaire")
plt.ylabel("Nombre d'eleves")
plt.xticks(rotation=45)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    DOSSIER_SORTIE / "01_evolution_effectifs_urbain_rural.png",
    dpi=300
)
plt.close()


# --------------------------------------------------
# 8. Graphique : evolution du ratio urbain/rural
# --------------------------------------------------

plt.figure(figsize=(12, 6))

plt.plot(
    evolution["ANNEE_SCOLAIRE"],
    evolution["RATIO_URBAIN_RURAL"],
    marker="o"
)

plt.title("Evolution du ratio des effectifs urbains et ruraux")
plt.xlabel("Annee scolaire")
plt.ylabel("Ratio urbain / rural")
plt.xticks(rotation=45)
plt.grid(alpha=0.3)
plt.tight_layout()

plt.savefig(
    DOSSIER_SORTIE / "02_evolution_ratio_urbain_rural.png",
    dpi=300
)
plt.close()


# --------------------------------------------------
# 9. Graphique : comparaison filles et garcons
# --------------------------------------------------

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for sexe in ["FILLES", "GARCONS"]:
    sous_df = df[df["SEXE"] == sexe]

    axes[0].plot(
        sous_df["ANNEE_SCOLAIRE"],
        sous_df["EFFECTIF_URBAIN"],
        marker="o",
        label=sexe
    )

    axes[1].plot(
        sous_df["ANNEE_SCOLAIRE"],
        sous_df["EFFECTIF_RURAL"],
        marker="o",
        label=sexe
    )

axes[0].set_title("Effectifs urbains selon le sexe")
axes[1].set_title("Effectifs ruraux selon le sexe")

for ax in axes:
    ax.set_xlabel("Annee scolaire")
    ax.set_ylabel("Nombre d'eleves")
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(alpha=0.3)

plt.tight_layout()

plt.savefig(
    DOSSIER_SORTIE / "03_comparaison_par_sexe.png",
    dpi=300
)
plt.close()


# --------------------------------------------------
# 10. Fin
# --------------------------------------------------

print("\nAnalyse terminee.")
print("Resultats enregistres dans :", DOSSIER_SORTIE)
