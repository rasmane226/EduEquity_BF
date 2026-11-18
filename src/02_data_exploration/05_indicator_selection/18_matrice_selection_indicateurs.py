
from pathlib import Path

import pandas as pd


# Chemins du projet
BASE_DIR = Path(__file__).resolve().parents[3]

DOSSIER_SORTIE = BASE_DIR / "outputs" / "tables"
FICHIER_SORTIE = DOSSIER_SORTIE / "matrice_selection_indicateurs.csv"


# Sélection des indicateurs selon les objectifs du défi
indicateurs = [
    {
        "axe": "Parité filles-garçons",
        "indicateur": "Effectifs du primaire par sexe et région",
        "feuille_source": "Feuil1",
        "fichier_traite": "effectifs_primaire_region_sexe.csv",
        "variables": "Région, sexe, année scolaire",
        "categorie": "Principal",
        "utilisation": "Comparer les effectifs des filles et des garçons entre les régions.",
        "limite": "Les effectifs ne mesurent pas directement les taux d'accès."
    },
    {
        "axe": "Parité filles-garçons",
        "indicateur": "Taux brut d'admission (TBA)",
        "feuille_source": "Feuil6",
        "fichier_traite": "tba_primaire_region_sexe.csv",
        "variables": "Région, sexe, année scolaire",
        "categorie": "Principal",
        "utilisation": "Comparer l'admission au primaire entre filles et garçons.",
        "limite": "Vérifier la définition officielle et les dénominateurs utilisés."
    },
    {
        "axe": "Parité filles-garçons",
        "indicateur": "Taux brut de scolarisation (TBS)",
        "feuille_source": "Feuil7",
        "fichier_traite": "tbs_primaire_region_sexe.csv",
        "variables": "Région, sexe, année scolaire",
        "categorie": "Principal",
        "utilisation": "Étudier les écarts de scolarisation entre filles et garçons.",
        "limite": "Un TBS supérieur à 100 % est possible."
    },
    {
        "axe": "Parité filles-garçons",
        "indicateur": "Taux d'achèvement du primaire (TAP)",
        "feuille_source": "Feuil8",
        "fichier_traite": "tap_primaire_region_sexe.csv",
        "variables": "Région, sexe, année scolaire",
        "categorie": "Principal",
        "utilisation": "Comparer l'achèvement du primaire selon le sexe.",
        "limite": "Vérifier la définition officielle de l'indicateur."
    },
    {
        "axe": "Parité filles-garçons",
        "indicateur": "Indice de parité du TBA",
        "feuille_source": "Feuil10",
        "fichier_traite": "ips_tba_primaire_region.csv",
        "variables": "Région, année scolaire",
        "categorie": "Principal",
        "utilisation": "Mesurer directement la parité filles-garçons à l'admission.",
        "limite": "Confirmer la formule officielle de calcul."
    },
    {
        "axe": "Parité filles-garçons",
        "indicateur": "Indice de parité du TBS",
        "feuille_source": "Feuil11",
        "fichier_traite": "ips_tbs_primaire_region.csv",
        "variables": "Région, année scolaire",
        "categorie": "Principal",
        "utilisation": "Mesurer la parité filles-garçons en matière de scolarisation.",
        "limite": "Confirmer la formule officielle de calcul."
    },
    {
        "axe": "Parité filles-garçons",
        "indicateur": "Indice de parité du TAP",
        "feuille_source": "Feuil12",
        "fichier_traite": "ips_tap_primaire_region.csv",
        "variables": "Région, année scolaire",
        "categorie": "Principal",
        "utilisation": "Mesurer la parité filles-garçons en matière d'achèvement.",
        "limite": "Confirmer la formule officielle de calcul."
    },
    {
        "axe": "Parité filles-garçons",
        "indicateur": "Taux de réussite au CEP",
        "feuille_source": "Feuil9",
        "fichier_traite": "taux_reussite_cep_region_sexe.csv",
        "variables": "Région, sexe, année civile",
        "categorie": "Complémentaire",
        "utilisation": "Examiner les différences de réussite à l'examen selon le sexe.",
        "limite": "Les années civiles ne doivent pas être confondues avec les années scolaires."
    },
    {
        "axe": "Parité filles-garçons",
        "indicateur": "Nouveaux entrants au CP1",
        "feuille_source": "Feuil5",
        "fichier_traite": "À nettoyer",
        "variables": "Région, sexe, année scolaire",
        "categorie": "Complémentaire",
        "utilisation": "Étudier les différences entre filles et garçons à l'entrée au primaire.",
        "limite": "Les effectifs ne constituent pas un taux d'accès sans population de référence."
    },
    {
        "axe": "Parité filles-garçons",
        "indicateur": "Effectifs par niveau scolaire",
        "feuille_source": "Feuil4",
        "fichier_traite": "À nettoyer",
        "variables": "Statut, niveau, sexe, année scolaire",
        "categorie": "Complémentaire",
        "utilisation": "Approfondir les différences entre filles et garçons selon le niveau.",
        "limite": "Nécessite un contrôle de cohérence des totaux par niveau et statut."
    },
    {
        "axe": "Disparités urbain-rural",
        "indicateur": "Effectifs du primaire par milieu et sexe",
        "feuille_source": "Feuil3",
        "fichier_traite": "effectifs_primaire_milieu_sexe.csv",
        "variables": "Milieu, sexe, année scolaire",
        "categorie": "Principal",
        "utilisation": "Comparer la répartition des effectifs entre les milieux urbain et rural.",
        "limite": "Sans population d'âge scolaire par milieu, les taux d'accès ne peuvent pas être calculés."
    },
    {
        "axe": "Disparités régionales",
        "indicateur": "Nombre d'écoles par statut et région",
        "feuille_source": "Feuil13",
        "fichier_traite": "ecoles_primaire_region_statut.csv",
        "variables": "Région, statut, année scolaire",
        "categorie": "Complémentaire",
        "utilisation": "Contextualiser la répartition territoriale des établissements.",
        "limite": "Le nombre d'écoles ne renseigne pas directement sur leur capacité d'accueil ou leur accessibilité."
    },
    {
        "axe": "Disparités territoriales",
        "indicateur": "Effectifs du primaire par statut",
        "feuille_source": "Feuil2",
        "fichier_traite": "À nettoyer",
        "variables": "Statut, sexe, année scolaire",
        "categorie": "Complémentaire",
        "utilisation": "Comparer les effectifs du public et du privé selon le sexe.",
        "limite": "Les catégories de statut doivent être interprétées selon les définitions officielles."
    },
    {
        "axe": "Contexte éducatif",
        "indicateur": "Effectifs du préscolaire",
        "feuille_source": "PRESCOLAIRE",
        "fichier_traite": "À examiner",
        "variables": "Région, statut, sexe, année",
        "categorie": "Contexte",
        "utilisation": "Présenter le contexte éducatif avant l'entrée au primaire.",
        "limite": "Vérifier la correspondance entre les années affichées et les années scolaires."
    }
]


# Création du tableau
matrice = pd.DataFrame(indicateurs)


# Vérification des fichiers déjà nettoyés
DOSSIER_PROCESSED = BASE_DIR / "data" / "intermediate"


def verifier_fichier(nom_fichier):
    if nom_fichier in ["À nettoyer", "À examiner"]:
        return "À préparer"

    chemin = DOSSIER_PROCESSED / nom_fichier

    if chemin.exists():
        return "Disponible"

    return "Manquant"


matrice["disponibilite"] = matrice["fichier_traite"].apply(
    verifier_fichier
)


# Contrôle des catégories
categories_valides = [
    "Principal",
    "Complémentaire",
    "Contexte"
]

if not matrice["categorie"].isin(categories_valides).all():
    raise ValueError("Une catégorie d'indicateur est invalide.")


# Création du dossier de sortie
DOSSIER_SORTIE.mkdir(parents=True, exist_ok=True)


# Exportation de la matrice
matrice.to_csv(
    FICHIER_SORTIE,
    index=False,
    encoding="utf-8-sig"
)


# Résumé des résultats
print("Matrice de sélection créée avec succès.")
print(f"Nombre d'indicateurs : {len(matrice)}")

print("\nRépartition par catégorie :")
print(matrice["categorie"].value_counts())

print("\nDisponibilité des fichiers :")
print(matrice["disponibilite"].value_counts())

print(f"\nFichier enregistré : {FICHIER_SORTIE}")
