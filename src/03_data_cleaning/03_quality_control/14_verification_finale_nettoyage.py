
from pathlib import Path
import pandas as pd


# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

DOSSIER_DONNEES = (
    BASE_DIR / "data" / "03_cleaned_data" / "final"
)

DOSSIER_SORTIE = (
    BASE_DIR / "outputs" / "tables" / "cleaning"
)

FICHIER_RAPPORT = (
    DOSSIER_SORTIE / "verification_finale_nettoyage.csv"
)


# ============================================================
# 2. PARAMETRES DE REFERENCE
# ============================================================

REGIONS_REFERENCE = {
    "BOUCLE DU MOUHOUN",
    "CASCADES",
    "CENTRE",
    "CENTRE-EST",
    "CENTRE-NORD",
    "CENTRE-OUEST",
    "CENTRE-SUD",
    "EST",
    "HAUTS-BASSINS",
    "NORD",
    "PLATEAU CENTRAL",
    "SAHEL",
    "SUD-OUEST"
}

ANNEES_SCOLAIRES = [
    "2015-2016",
    "2016-2017",
    "2017-2018",
    "2018-2019",
    "2019-2020",
    "2020-2021",
    "2021-2022",
    "2022-2023",
    "2023-2024",
    "2024-2025"
]

ANNEES_CEP = [
    str(annee)
    for annee in range(2016, 2026)
]


# ============================================================
# 3. CONFIGURATION DES FICHIERS
# ============================================================

CONFIGURATION = {

    "effectifs_primaire_region_sexe.csv": {
        "lignes": 26,
        "cles": ["REGION", "SEXE"],
        "region": "REGION",
        "categories": {
            "SEXE": {"FILLES", "GARCONS"}
        },
        "colonnes_annees": ANNEES_SCOLAIRES
    },

    "effectifs_primaire_milieu_sexe.csv": {
        "lignes": 6,
        "cles": ["MILIEU", "SEXE"],
        "region": None,
        "categories": {
            "MILIEU": {"URBAIN", "RURAL", "NATIONAL"},
            "SEXE": {"FILLES", "GARCONS"}
        },
        "colonnes_annees": ANNEES_SCOLAIRES
    },

    "tba_primaire_region_sexe.csv": {
        "lignes": 13,
        "cles": ["REGION"],
        "region": "REGION",
        "categories": {},
        "colonnes_annees": [
            f"{annee}_{sexe}"
            for annee in ANNEES_SCOLAIRES
            for sexe in ["GARCONS", "FILLES", "TOTAL"]
        ]
    },

    "tbs_primaire_region_sexe.csv": {
        "lignes": 13,
        "cles": ["REGION"],
        "region": "REGION",
        "categories": {},
        "colonnes_annees": [
            f"{annee}_{sexe}"
            for annee in ANNEES_SCOLAIRES
            for sexe in ["GARCONS", "FILLES", "TOTAL"]
        ]
    },

    "tap_primaire_region_sexe.csv": {
        "lignes": 13,
        "cles": ["REGION"],
        "region": "REGION",
        "categories": {},
        "colonnes_annees": [
            f"{annee}_{sexe}"
            for annee in ANNEES_SCOLAIRES
            for sexe in ["GARCONS", "FILLES", "TOTAL"]
        ]
    },

    "taux_reussite_cep_region_sexe.csv": {
        "lignes": 26,
        "cles": ["REGION", "SEXE"],
        "region": "REGION",
        "categories": {
            "SEXE": {"FILLES", "GARCONS"}
        },
        "colonnes_annees": ANNEES_CEP
    },

    "ips_tba_primaire_region.csv": {
        "lignes": 13,
        "cles": ["REGION"],
        "region": "REGION",
        "categories": {},
        "colonnes_annees": ANNEES_SCOLAIRES
    },

    "ips_tbs_primaire_region.csv": {
        "lignes": 13,
        "cles": ["REGION"],
        "region": "REGION",
        "categories": {},
        "colonnes_annees": ANNEES_SCOLAIRES
    },

    "ips_tap_primaire_region.csv": {
        "lignes": 13,
        "cles": ["REGION"],
        "region": "REGION",
        "categories": {},
        "colonnes_annees": ANNEES_SCOLAIRES
    },

    "ecoles_primaire_region_statut.csv": {
        "lignes": 26,
        "cles": ["REGION", "STATUT"],
        "region": "REGION",
        "categories": {
            "STATUT": {"PUBLIC", "PRIVÉ"}
        },
        "colonnes_annees": ANNEES_SCOLAIRES
    },

    "nouveaux_inscrits_cp1_region_sexe.csv": {
        "lignes": 260,
        "cles": [
            "REGION",
            "ANNEE_SCOLAIRE",
            "SEXE"
        ],
        "region": "REGION",
        "categories": {
            "SEXE": {"FILLES", "GARCONS"}
        },
        "colonnes_annees": None
    }
}


# ============================================================
# 4. FONCTIONS UTILITAIRES
# ============================================================

def trouver_colonne(df, nom_recherche):

    for colonne in df.columns:

        if str(colonne).strip().upper() == nom_recherche.upper():
            return colonne

    return None


def normaliser_texte(serie):

    return (
        serie.astype("string")
        .str.strip()
        .str.upper()
    )


def ajouter_anomalie(anomalies, message):

    if message not in anomalies:
        anomalies.append(message)


# ============================================================
# 5. INITIALISATION
# ============================================================

resultats = []

print("\n========== VERIFICATION FINALE DU NETTOYAGE ==========")

print("Dossier des données :", DOSSIER_DONNEES)

if not DOSSIER_DONNEES.exists():

    raise FileNotFoundError(
        f"Dossier introuvable : {DOSSIER_DONNEES}"
    )


# ============================================================
# 6. CONTROLE DES FICHIERS
# ============================================================

for nom_fichier, regles in CONFIGURATION.items():

    chemin = DOSSIER_DONNEES / nom_fichier

    print("\n" + "=" * 60)
    print("FICHIER :", nom_fichier)

    anomalies = []

    nombre_lignes = 0
    nombre_colonnes = 0
    nombre_manquants = "NON VERIFIE"
    doublons_cles = "NON VERIFIE"
    regions_distinctes = 0
    regions_inconnues = []
    regions_manquantes = []
    dimensions_correctes = False

    # --------------------------------------------------------
    # 6.1. EXISTENCE DU FICHIER
    # --------------------------------------------------------

    if not chemin.exists():

        ajouter_anomalie(anomalies, "FICHIER ABSENT")

        resultats.append({
            "FICHIER": nom_fichier,
            "LIGNES": 0,
            "COLONNES": 0,
            "REGIONS_DISTINCTES": 0,
            "REGIONS_INCONNUES": "",
            "REGIONS_MANQUANTES": "",
            "VALEURS_MANQUANTES": "NON VERIFIE",
            "DOUBLONS_CLES": "NON VERIFIE",
            "DIMENSIONS_CORRECTES": False,
            "ANOMALIES": "FICHIER ABSENT",
            "VALIDATION": "ECHEC"
        })

        print("Fichier absent.")
        continue

    # --------------------------------------------------------
    # 6.2. LECTURE DU FICHIER
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            chemin,
            encoding="utf-8-sig"
        )

    except Exception as erreur:

        resultats.append({
            "FICHIER": nom_fichier,
            "LIGNES": 0,
            "COLONNES": 0,
            "REGIONS_DISTINCTES": 0,
            "REGIONS_INCONNUES": "",
            "REGIONS_MANQUANTES": "",
            "VALEURS_MANQUANTES": "NON VERIFIE",
            "DOUBLONS_CLES": "NON VERIFIE",
            "DIMENSIONS_CORRECTES": False,
            "ANOMALIES": f"ERREUR DE LECTURE : {erreur}",
            "VALIDATION": "ECHEC"
        })

        print("Erreur de lecture :", erreur)
        continue

    nombre_lignes, nombre_colonnes = df.shape

    print("Dimensions observées :", df.shape)

    # --------------------------------------------------------
    # 6.3. VERIFICATION DES DIMENSIONS
    # --------------------------------------------------------

    dimensions_correctes = (
        nombre_lignes == regles["lignes"]
        and nombre_colonnes > 0
    )

    if not dimensions_correctes:

        ajouter_anomalie(
            anomalies,
            "DIMENSIONS INCORRECTES"
        )

    print(
        "Nombre de lignes attendu :",
        regles["lignes"]
    )

    # --------------------------------------------------------
    # 6.4. VERIFICATION DES VALEURS MANQUANTES
    # --------------------------------------------------------

    nombre_manquants = int(
        df.isna().sum().sum()
    )

    if nombre_manquants > 0:

        ajouter_anomalie(
            anomalies,
            "VALEURS MANQUANTES"
        )

    print("Valeurs manquantes :", nombre_manquants)

    # --------------------------------------------------------
    # 6.5. VERIFICATION DES REGIONS
    # --------------------------------------------------------

    if regles["region"] is not None:

        colonne_region = trouver_colonne(
            df,
            regles["region"]
        )

        if colonne_region is None:

            ajouter_anomalie(
                anomalies,
                "COLONNE REGION ABSENTE"
            )

        else:

            valeurs_regions = normaliser_texte(
                df[colonne_region]
            )

            regions_presentes = set(
                valeurs_regions.dropna()
            )

            regions_distinctes = len(
                regions_presentes
            )

            regions_inconnues = sorted(
                regions_presentes - REGIONS_REFERENCE
            )

            regions_manquantes = sorted(
                REGIONS_REFERENCE - regions_presentes
            )

            if regions_inconnues:

                ajouter_anomalie(
                    anomalies,
                    "REGIONS INCONNUES"
                )

            if regions_manquantes:

                ajouter_anomalie(
                    anomalies,
                    "REGIONS MANQUANTES"
                )

            if (
                "NATIONAL" in regions_presentes
                or "BURKINA FASO" in regions_presentes
            ):

                ajouter_anomalie(
                    anomalies,
                    "LIGNE NATIONALE PRESENTE"
                )

            print("Régions distinctes :", regions_distinctes)
            print("Régions inconnues :", regions_inconnues)
            print("Régions manquantes :", regions_manquantes)

    # --------------------------------------------------------
    # 6.6. VERIFICATION DES CATEGORIES
    # --------------------------------------------------------

    for nom_categorie, valeurs_attendues in regles[
        "categories"
    ].items():

        colonne = trouver_colonne(
            df,
            nom_categorie
        )

        if colonne is None:

            ajouter_anomalie(
                anomalies,
                f"COLONNE {nom_categorie} ABSENTE"
            )

            continue

        valeurs_observees = set(
            normaliser_texte(df[colonne]).dropna()
        )

        valeurs_inconnues = (
            valeurs_observees - valeurs_attendues
        )

        valeurs_absentes = (
            valeurs_attendues - valeurs_observees
        )

        if valeurs_inconnues:

            ajouter_anomalie(
                anomalies,
                f"VALEURS INCONNUES DANS {nom_categorie}"
            )

        if valeurs_absentes:

            ajouter_anomalie(
                anomalies,
                f"CATEGORIES MANQUANTES DANS {nom_categorie}"
            )

    # --------------------------------------------------------
    # 6.7. VERIFICATION DES ANNEES
    # --------------------------------------------------------

    if nom_fichier == "nouveaux_inscrits_cp1_region_sexe.csv":

        colonne_annee = trouver_colonne(
            df,
            "ANNEE_SCOLAIRE"
        )

        if colonne_annee is None:

            ajouter_anomalie(
                anomalies,
                "COLONNE ANNEE_SCOLAIRE ABSENTE"
            )

        else:

            annees_observees = set(
                df[colonne_annee]
                .astype(str)
                .str.strip()
            )

            annees_manquantes = (
                set(ANNEES_SCOLAIRES) - annees_observees
            )

            annees_inconnues = (
                annees_observees - set(ANNEES_SCOLAIRES)
            )

            if annees_manquantes:

                ajouter_anomalie(
                    anomalies,
                    "ANNEES SCOLAIRES MANQUANTES"
                )

            if annees_inconnues:

                ajouter_anomalie(
                    anomalies,
                    "ANNEES SCOLAIRES INCONNUES"
                )

    else:

        colonnes_attendues = regles["colonnes_annees"]

        colonnes_manquantes = [
            colonne
            for colonne in colonnes_attendues
            if trouver_colonne(df, colonne) is None
        ]

        if colonnes_manquantes:

            ajouter_anomalie(
                anomalies,
                "COLONNES ANNUELLES MANQUANTES"
            )

    # --------------------------------------------------------
    # 6.8. VERIFICATION DES CLES UNIQUES
    # --------------------------------------------------------

    colonnes_cles = []

    for nom_cle in regles["cles"]:

        colonne = trouver_colonne(
            df,
            nom_cle
        )

        if colonne is None:

            ajouter_anomalie(
                anomalies,
                f"CLE ABSENTE : {nom_cle}"
            )

        else:

            colonnes_cles.append(colonne)

    if len(colonnes_cles) == len(regles["cles"]):

        doublons_cles = int(
            df.duplicated(
                subset=colonnes_cles
            ).sum()
        )

        if doublons_cles > 0:

            ajouter_anomalie(
                anomalies,
                "DOUBLONS SUR LES CLES"
            )

    # --------------------------------------------------------
    # 6.9. VERIFICATION DES VALEURS NUMERIQUES DE FEUIL5
    # --------------------------------------------------------

    if nom_fichier == "nouveaux_inscrits_cp1_region_sexe.csv":

        colonne_effectif = trouver_colonne(
            df,
            "NOUVEAUX_INSCRITS_CP1"
        )

        if colonne_effectif is None:

            ajouter_anomalie(
                anomalies,
                "COLONNE EFFECTIFS CP1 ABSENTE"
            )

        else:

            valeurs_numeriques = pd.to_numeric(
                df[colonne_effectif],
                errors="coerce"
            )

            if valeurs_numeriques.isna().any():

                ajouter_anomalie(
                    anomalies,
                    "VALEURS NUMERIQUES INCORRECTES"
                )

            elif (valeurs_numeriques < 0).any():

                ajouter_anomalie(
                    anomalies,
                    "EFFECTIFS NEGATIFS"
                )

    # --------------------------------------------------------
    # 6.10. VALIDATION DU FICHIER
    # --------------------------------------------------------

    valide = len(anomalies) == 0

    statut = "VALIDE" if valide else "A CORRIGER"

    print("Doublons sur les clés :", doublons_cles)
    print("Anomalies :", anomalies)
    print("Résultat :", statut)

    resultats.append({

        "FICHIER": nom_fichier,
        "LIGNES": nombre_lignes,
        "COLONNES": nombre_colonnes,
        "REGIONS_DISTINCTES": regions_distinctes,
        "REGIONS_INCONNUES": ", ".join(regions_inconnues),
        "REGIONS_MANQUANTES": ", ".join(regions_manquantes),
        "VALEURS_MANQUANTES": nombre_manquants,
        "DOUBLONS_CLES": doublons_cles,
        "DIMENSIONS_CORRECTES": dimensions_correctes,
        "ANOMALIES": " | ".join(anomalies),
        "VALIDATION": statut

    })


# ============================================================
# 7. GENERATION DU RAPPORT FINAL
# ============================================================

rapport = pd.DataFrame(resultats)

DOSSIER_SORTIE.mkdir(
    parents=True,
    exist_ok=True
)

rapport.to_csv(
    FICHIER_RAPPORT,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 8. BILAN GLOBAL
# ============================================================

nombre_total = len(CONFIGURATION)

nombre_valides = int(
    (rapport["VALIDATION"] == "VALIDE").sum()
)

nombre_a_corriger = (
    nombre_total - nombre_valides
)

print("\n" + "=" * 60)
print("RESULTAT DE LA VERIFICATION FINALE")
print("=" * 60)

print("Fichiers contrôlés :", nombre_total)
print("Fichiers validés :", nombre_valides)
print("Fichiers à corriger :", nombre_a_corriger)

print("\nRapport enregistré :", FICHIER_RAPPORT)


# ============================================================
# 9. CONCLUSION
# ============================================================

if nombre_valides == nombre_total:

    print(
        "\nVERIFICATION STRUCTURELLE TERMINEE AVEC SUCCES."
    )

else:

    print(
        "\nCERTAINS FICHIERS NECESSITENT UNE VERIFICATION."
    )
