
import pandas as pd
from pathlib import Path

# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

# Chemin racine du projet
ROOT_DIR = Path(__file__).resolve().parents[2]

# Dossier des résultats
OUTPUT_DIR = ROOT_DIR / "outputs" / "tables" / "collection"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Chemin de l'inventaire
inventaire_path = OUTPUT_DIR / "inventaire_donnees.csv"

# Vérifier la présence de l'inventaire
if not inventaire_path.exists():
    raise FileNotFoundError(
        f"Rapport d'inventaire introuvable : {inventaire_path}"
    )

# Charger l'inventaire
inventaire = pd.read_csv(inventaire_path)

print("========== SELECTION DES DONNEES ==========")


# ============================================================
# 2. VERIFICATION DE L'INVENTAIRE
# ============================================================

# Vérifier la présence de la colonne FEUILLE
if "FEUILLE" not in inventaire.columns:
    raise ValueError(
        "La colonne FEUILLE est absente de l'inventaire."
    )

# Vérifier les noms de feuilles manquants
if inventaire["FEUILLE"].isna().any():
    raise ValueError(
        "L'inventaire contient des noms de feuilles manquants."
    )

# Vérifier les doublons
if inventaire["FEUILLE"].duplicated().any():
    raise ValueError(
        "L'inventaire contient des feuilles en double."
    )

# Vérifier le nombre de feuilles
if len(inventaire) != 14:
    raise ValueError(
        f"14 feuilles attendues, {len(inventaire)} trouvées."
    )

print("Inventaire vérifié : 14 feuilles uniques.")


# ============================================================
# 3. DEFINITION DES FEUILLES SELECTIONNEES
# ============================================================

selection = {

    "Feuil1": {
        "decision": "SELECTIONNEE_PRINCIPALE",
        "contenu": "Effectifs du primaire par région et par sexe",
        "indicateurs": "Effectifs scolaires",
        "justification": "Permet d'étudier les disparités régionales entre filles et garçons."
    },

    "Feuil2": {
        "decision": "SELECTIONNEE_COMPLEMENTAIRE",
        "contenu": "Effectifs du primaire par sexe et par statut",
        "indicateurs": "Effectifs selon le statut public et privé",
        "justification": "Permet de compléter l'analyse des effectifs en distinguant les établissements publics et privés selon le sexe."
    },

    "Feuil3": {
        "decision": "SELECTIONNEE_PRINCIPALE",
        "contenu": "Effectifs du primaire par milieu et par sexe",
        "indicateurs": "Effectifs urbains et ruraux",
        "justification": "Permet de comparer les effectifs scolaires selon le milieu de résidence."
    },

    "Feuil4": {
        "decision": "SELECTIONNEE_COMPLEMENTAIRE",
        "contenu": "Effectifs du primaire par niveau, sexe et statut",
        "indicateurs": "Effectifs par niveau scolaire, sexe et statut",
        "justification": "Permet d'approfondir l'analyse de la répartition des effectifs selon le niveau scolaire, le sexe et le statut."
    },

    "Feuil5": {
        "decision": "SELECTIONNEE_PRINCIPALE",
        "contenu": "Nouveaux inscrits au CP1 par région et par sexe",
        "indicateurs": "Nouveaux inscrits au CP1",
        "justification": "Permet d'étudier les nouveaux entrants dans le cycle primaire et les disparités régionales entre filles et garçons."
    },

    "Feuil6": {
        "decision": "SELECTIONNEE_PRINCIPALE",
        "contenu": "Taux brut d'admission par région et par sexe",
        "indicateurs": "TBA",
        "justification": "Permet d'étudier les disparités d'accès à l'entrée du primaire."
    },

    "Feuil7": {
        "decision": "SELECTIONNEE_PRINCIPALE",
        "contenu": "Taux brut de scolarisation par région et par sexe",
        "indicateurs": "TBS",
        "justification": "Permet d'étudier la couverture scolaire."
    },

    "Feuil8": {
        "decision": "SELECTIONNEE_PRINCIPALE",
        "contenu": "Taux d'achèvement du primaire par région et par sexe",
        "indicateurs": "TAP",
        "justification": "Permet d'étudier l'achèvement du cycle primaire."
    },

    "Feuil9": {
        "decision": "SELECTIONNEE_PRINCIPALE",
        "contenu": "Taux de réussite au CEP par région et par sexe",
        "indicateurs": "Réussite au CEP",
        "justification": "Permet de comparer les résultats à l'examen selon le sexe et la région."
    },

    "Feuil10": {
        "decision": "SELECTIONNEE_PRINCIPALE",
        "contenu": "Indice de parité du TBA par région",
        "indicateurs": "IPS TBA",
        "justification": "Permet d'étudier la parité dans l'admission."
    },

    "Feuil11": {
        "decision": "SELECTIONNEE_PRINCIPALE",
        "contenu": "Indice de parité du TBS par région",
        "indicateurs": "IPS TBS",
        "justification": "Permet d'étudier la parité dans la scolarisation."
    },

    "Feuil12": {
        "decision": "SELECTIONNEE_PRINCIPALE",
        "contenu": "Indice de parité du TAP par région",
        "indicateurs": "IPS TAP",
        "justification": "Permet d'étudier la parité dans l'achèvement."
    },

    "Feuil13": {
        "decision": "SELECTIONNEE_PRINCIPALE",
        "contenu": "Établissements primaires par statut et par région",
        "indicateurs": "Écoles publiques et privées",
        "justification": "Permet d'étudier la répartition territoriale des établissements selon leur statut."
    }
}


# ============================================================
# 4. DEFINITION DES FEUILLES EXCLUES
# ============================================================

exclusions = {
    "PRESCOLAIRE": (
        "Hors du périmètre retenu : le projet se concentre "
        "sur l'enseignement primaire."
    )
}


# ============================================================
# 5. VERIFICATION DE LA CLASSIFICATION
# ============================================================

# Vérifier que toutes les feuilles de l'inventaire
# sont présentes dans la sélection ou les exclusions
feuilles_documentees = set(selection) | set(exclusions)
feuilles_inventoriees = set(inventaire["FEUILLE"])

feuilles_non_documentees = (
    feuilles_inventoriees - feuilles_documentees
)

feuilles_absentes = (
    feuilles_documentees - feuilles_inventoriees
)

if feuilles_non_documentees:
    raise ValueError(
        f"Feuilles sans décision : {feuilles_non_documentees}"
    )

if feuilles_absentes:
    raise ValueError(
        f"Feuilles absentes de l'inventaire : {feuilles_absentes}"
    )


# ============================================================
# 6. CONSTRUCTION DU RAPPORT DE SELECTION
# ============================================================

lignes = []

for _, row in inventaire.iterrows():

    feuille = row["FEUILLE"]

    if feuille in selection:

        informations = selection[feuille]

        decision = informations["decision"]
        contenu = informations["contenu"]
        indicateurs = informations["indicateurs"]
        justification = informations["justification"]

    elif feuille in exclusions:

        decision = "EXCLUE"
        contenu = "Données relatives au préscolaire"
        indicateurs = "Non applicable"
        justification = exclusions[feuille]

    else:

        decision = "A VERIFIER"
        contenu = "Non documenté"
        indicateurs = "Non documenté"
        justification = "Décision de sélection à préciser."

    lignes.append({
        "FEUILLE": feuille,
        "DECISION": decision,
        "NOMBRE_LIGNES": row["NOMBRE_LIGNES"],
        "NOMBRE_COLONNES": row["NOMBRE_COLONNES"],
        "CONTENU": contenu,
        "INDICATEURS": indicateurs,
        "JUSTIFICATION": justification
    })


df_selection = pd.DataFrame(lignes)


# ============================================================
# 7. CONTROLE DE LA CLASSIFICATION
# ============================================================

nombre_principales = (
    df_selection["DECISION"] == "SELECTIONNEE_PRINCIPALE"
).sum()

nombre_complementaires = (
    df_selection["DECISION"] == "SELECTIONNEE_COMPLEMENTAIRE"
).sum()

nombre_exclues = (
    df_selection["DECISION"] == "EXCLUE"
).sum()

nombre_a_verifier = (
    df_selection["DECISION"] == "A VERIFIER"
).sum()

# Vérifier les résultats attendus
if (
    nombre_principales != 11
    or nombre_complementaires != 2
    or nombre_exclues != 1
    or nombre_a_verifier != 0
):
    raise ValueError(
        "La classification des feuilles ne correspond pas "
        "à la sélection attendue."
    )

print("Classification vérifiée avec succès.")


# ============================================================
# 8. ENREGISTREMENT DU RAPPORT DETAILLE
# ============================================================

selection_path = OUTPUT_DIR / "selection_donnees.csv"

df_selection.to_csv(
    selection_path,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 9. CREATION DU RAPPORT RECAPITULATIF
# ============================================================

rapport = pd.DataFrame([{

    "NOMBRE_FEUILLES_TOTAL": len(df_selection),

    "NOMBRE_FEUILLES_PRINCIPALES": nombre_principales,

    "NOMBRE_FEUILLES_COMPLEMENTAIRES": nombre_complementaires,

    "NOMBRE_FEUILLES_SELECTIONNEES": (
        nombre_principales + nombre_complementaires
    ),

    "NOMBRE_FEUILLES_EXCLUES": nombre_exclues,

    "NOMBRE_FEUILLES_A_VERIFIER": nombre_a_verifier

}])


rapport.to_csv(
    OUTPUT_DIR / "rapport_selection_donnees.csv",
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 10. AFFICHAGE DES RESULTATS
# ============================================================

print("\n========== SELECTION DES DONNEES ==========")

print(
    df_selection[["FEUILLE", "DECISION"]].to_string(index=False)
)

print("\n========== RESUME ==========")

print(rapport.to_string(index=False))

print("\n========== FICHIERS GENERES ==========")

print("Rapport détaillé :", selection_path)

print(
    "Rapport récapitulatif :",
    OUTPUT_DIR / "rapport_selection_donnees.csv"
)

print("\nSélection terminée avec succès.")
