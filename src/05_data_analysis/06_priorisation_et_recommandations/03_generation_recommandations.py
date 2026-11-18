
from pathlib import Path
import pandas as pd


# ============================================================
# 1. INITIALISATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

DOSSIER_ANALYSES = BASE_DIR / "outputs" / "analyses"

DOSSIER_PRIORISATION = (
    DOSSIER_ANALYSES / "06_priorisation_et_recommandations"
)

DOSSIER_SORTIE = DOSSIER_PRIORISATION
DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)

FICHIER_REGIONAL = (
    DOSSIER_PRIORISATION / "donnees_consolidees_regionales.csv"
)

FICHIER_SITUATION_MILIEU = (
    DOSSIER_PRIORISATION / "donnees_situation_milieu_sexe.csv"
)

FICHIER_ECARTS_GENRE_MILIEU = (
    DOSSIER_PRIORISATION / "donnees_ecarts_genre_milieu.csv"
)

FICHIER_ECARTS_MILIEUX = (
    DOSSIER_PRIORISATION / "donnees_ecarts_urbain_rural.csv"
)


# ============================================================
# 2. CHARGEMENT DES DONNEES
# ============================================================

fichiers = [
    FICHIER_REGIONAL,
    FICHIER_SITUATION_MILIEU,
    FICHIER_ECARTS_GENRE_MILIEU,
    FICHIER_ECARTS_MILIEUX
]

for fichier in fichiers:
    if not fichier.exists():
        raise FileNotFoundError(f"Fichier introuvable : {fichier}")

df = pd.read_csv(FICHIER_REGIONAL, encoding="utf-8")
df_milieu = pd.read_csv(FICHIER_SITUATION_MILIEU, encoding="utf-8")
df_genre_milieu = pd.read_csv(
    FICHIER_ECARTS_GENRE_MILIEU,
    encoding="utf-8"
)
df_ecarts_milieux = pd.read_csv(
    FICHIER_ECARTS_MILIEUX,
    encoding="utf-8"
)

print("Sources chargées avec succès.")


# ============================================================
# 3. GENERATION DES CONSTATS REGIONAUX
# ============================================================

def generer_constats(ligne):

    constats = []

    # Accès et fréquentation scolaire
    if ligne["SCOLARISE_PCT"] < 40:
        constats.append(
            "Faible proportion d'enfants scolarisés "
            "dans les données INSD"
        )

    if ligne["JAMAIS_FREQUENTE_PCT"] >= 50:
        constats.append(
            "Proportion élevée d'enfants n'ayant jamais fréquenté l'école"
        )

    if ligne["TAP"] < 50:
        constats.append(
            "Taux moyen d'achèvement du primaire inférieur à 50 %"
        )

    # Disparités filles-garçons à l'admission
    if ligne["ECART_TBA"] <= -5:
        constats.append(
            "Désavantage moyen marqué des filles à l'admission"
        )
    elif ligne["ECART_TBA"] < 0:
        constats.append(
            "Désavantage moyen des filles à l'admission"
        )

    # Disparités filles-garçons en scolarisation
    if ligne["ECART_TBS"] <= -1:
        constats.append(
            "Désavantage moyen des filles en scolarisation"
        )

    # Disparités filles-garçons à l'achèvement
    if ligne["ECART_TAP"] < 0:
        constats.append(
            "Désavantage moyen des filles à l'achèvement"
        )
    elif ligne["ECART_TAP"] > 0:
        constats.append(
            "Avantage moyen des filles à l'achèvement"
        )

    if not constats:
        constats.append(
            "Aucune difficulté spécifique détectée par les règles retenues"
        )

    return " ; ".join(constats)


# ============================================================
# 4. GENERATION DES RECOMMANDATIONS REGIONALES
# ============================================================

def generer_recommandations(ligne):

    recommandations = []

    # Priorité territoriale
    if ligne["NIVEAU_PRIORITE"] == "PRIORITE ELEVEE":
        recommandations.append(
            "Accorder une attention prioritaire à cette région "
            "dans la planification des interventions éducatives"
        )

    elif ligne["NIVEAU_PRIORITE"] == "PRIORITE MOYENNE":
        recommandations.append(
            "Renforcer les interventions éducatives "
            "et suivre régulièrement les indicateurs"
        )

    else:
        recommandations.append(
            "Maintenir les acquis et surveiller l'évolution "
            "des indicateurs scolaires"
        )

    # Accès à l'éducation
    if ligne["SCOLARISE_PCT"] < 40:
        recommandations.append(
            "Étudier les obstacles à la scolarisation "
            "et renforcer les dispositifs d'accès à l'école"
        )

    if ligne["JAMAIS_FREQUENTE_PCT"] >= 50:
        recommandations.append(
            "Développer des actions ciblées vers les enfants "
            "n'ayant jamais fréquenté l'école"
        )

    # Achèvement
    if ligne["TAP"] < 50:
        recommandations.append(
            "Renforcer les dispositifs de maintien scolaire "
            "et de soutien à l'achèvement du primaire"
        )

    # Genre : admission
    if ligne["ECART_TBA"] < -1:
        recommandations.append(
            "Renforcer le suivi de l'accès des filles "
            "à l'entrée au primaire"
        )

    # Genre : scolarisation
    if ligne["ECART_TBS"] < -1:
        recommandations.append(
            "Examiner les écarts de scolarisation entre filles et garçons"
        )

    # Genre : achèvement
    if ligne["ECART_TAP"] < 0:
        recommandations.append(
            "Porter une attention particulière à l'achèvement "
            "du primaire par les filles"
        )

    return " ; ".join(recommandations)


# ============================================================
# 5. APPLICATION AUX 13 REGIONS
# ============================================================

df["CONSTATS_OBSERVES"] = df.apply(
    generer_constats,
    axis=1
)

df["RECOMMANDATIONS"] = df.apply(
    generer_recommandations,
    axis=1
)


# ============================================================
# 6. SYNTHESE NATIONALE URBAIN-RURAL
# ============================================================

# Extraire les écarts observés entre milieux
ecart_scolarisation = df_ecarts_milieux.loc[
    df_ecarts_milieux["STATUT_SCOLAIRE"] == "Scolarisé",
    "ECART_URBAIN_MOINS_RURAL"
].iloc[0]

ecart_non_frequentation = df_ecarts_milieux.loc[
    df_ecarts_milieux["STATUT_SCOLAIRE"] == "Jamais fréquenté",
    "ECART_URBAIN_MOINS_RURAL"
].iloc[0]

ecart_descolarisation = df_ecarts_milieux.loc[
    df_ecarts_milieux["STATUT_SCOLAIRE"] == "Déscolarisé",
    "ECART_URBAIN_MOINS_RURAL"
].iloc[0]

synthese_milieu = pd.DataFrame([
    {
        "DIMENSION": "Scolarisation",
        "ECART_URBAIN_MOINS_RURAL": ecart_scolarisation,
        "CONSTAT": (
            f"Proportion de scolarisation supérieure de "
            f"{ecart_scolarisation:.1f} points en milieu urbain"
        ),
        "RECOMMANDATION": (
            "Examiner les disparités d'accès entre les milieux "
            "et renforcer les actions en faveur des populations rurales"
        )
    },
    {
        "DIMENSION": "Jamais fréquenté",
        "ECART_URBAIN_MOINS_RURAL": ecart_non_frequentation,
        "CONSTAT": (
            f"Écart urbain-rural de "
            f"{ecart_non_frequentation:.1f} points"
        ),
        "RECOMMANDATION": (
            "Renforcer les actions visant les enfants "
            "n'ayant jamais fréquenté l'école, notamment en milieu rural"
        )
    },
    {
        "DIMENSION": "Déscolarisation",
        "ECART_URBAIN_MOINS_RURAL": ecart_descolarisation,
        "CONSTAT": (
            f"Écart urbain-rural de "
            f"{ecart_descolarisation:.1f} points"
        ),
        "RECOMMANDATION": (
            "Approfondir l'analyse du maintien scolaire "
            "dans les deux milieux"
        )
    }
])


# ============================================================
# 7. SYNTHESE NATIONALE FILLES-GARCONS SELON LE MILIEU
# ============================================================

synthese_genre_milieu = df_genre_milieu.copy()

synthese_genre_milieu["INTERPRETATION"] = (
    synthese_genre_milieu["ECART_FEMININ_MOINS_MASCULIN"]
    .apply(
        lambda x:
        "Désavantage des filles"
        if x < 0
        else (
            "Avantage des filles"
            if x > 0
            else "Égalité observée"
        )
    )
)


# ============================================================
# 8. EXPORTATION DES RESULTATS
# ============================================================

colonnes_finales = [
    "RANG_PRIORITE",
    "REGION",
    "SCORE_PRIORITE",
    "NIVEAU_PRIORITE",
    "TBA",
    "TBS",
    "TAP",
    "SCOLARISE_PCT",
    "JAMAIS_FREQUENTE_PCT",
    "ECART_TBA",
    "ECART_TBS",
    "ECART_TAP",
    "CONSTATS_OBSERVES",
    "RECOMMANDATIONS"
]

df_final = df[colonnes_finales].copy()

df_final.to_csv(
    DOSSIER_SORTIE / "recommandations_territoriales.csv",
    index=False,
    encoding="utf-8-sig"
)

synthese_milieu.to_csv(
    DOSSIER_SORTIE / "recommandations_urbain_rural.csv",
    index=False,
    encoding="utf-8-sig"
)

synthese_genre_milieu.to_csv(
    DOSSIER_SORTIE / "synthese_genre_par_milieu.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 9. AFFICHAGE DES RESULTATS
# ============================================================

print("\n========== RECOMMANDATIONS TERRITORIALES ==========")

for _, ligne in df_final.iterrows():

    print(f"\nRégion : {ligne['REGION']}")
    print(f"Priorité : {ligne['NIVEAU_PRIORITE']}")
    print(f"Constats : {ligne['CONSTATS_OBSERVES']}")
    print(f"Recommandations : {ligne['RECOMMANDATIONS']}")


print("\n========== SYNTHESE URBAIN-RURAL ==========")
print(synthese_milieu.to_string(index=False))


print("\n========== SYNTHESE GENRE PAR MILIEU ==========")
print(
    synthese_genre_milieu.to_string(index=False)
)


# ============================================================
# 10. BILAN FINAL
# ============================================================

print("\n==============================================")
print("GENERATION DES RECOMMANDATIONS TERMINEE.")
print(f"Régions traitées : {len(df_final)}")
print("Fichiers produits :")
print("- recommandations_territoriales.csv")
print("- recommandations_urbain_rural.csv")
print("- synthese_genre_par_milieu.csv")
print("==============================================")
