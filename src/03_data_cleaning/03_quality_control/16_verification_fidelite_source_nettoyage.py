from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import pandas as pd


# ============================================================
# 1. CONFIGURATION DES CHEMINS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

FICHIER_EXCEL = (
    BASE_DIR / "data" / "01_raw_data" /
    "donnees_education_bf.xlsx"
)

DOSSIER_SCRIPTS_NETTOYAGE = (
    BASE_DIR / "src" / "03_data_cleaning" / "01_sheet_cleaning"
)

DOSSIER_SCRIPTS_HARMONISATION = (
    BASE_DIR / "src" / "03_data_cleaning" / "02_data_harmonization"
)

DOSSIER_DONNEES_FINALES = (
    BASE_DIR / "data" / "03_cleaned_data" / "final"
)

DOSSIER_RAPPORT = (
    BASE_DIR / "outputs" / "tables" / "cleaning"
)

FICHIER_RAPPORT = (
    DOSSIER_RAPPORT / "rapport_fidelite_source_nettoyage.csv"
)


# ============================================================
# 2. FICHIERS A COMPARER
# ============================================================

FICHIERS = [
    "effectifs_primaire_region_sexe.csv",
    "effectifs_primaire_milieu_sexe.csv",
    "tba_primaire_region_sexe.csv",
    "tbs_primaire_region_sexe.csv",
    "tap_primaire_region_sexe.csv",
    "taux_reussite_cep_region_sexe.csv",
    "ips_tba_primaire_region.csv",
    "ips_tbs_primaire_region.csv",
    "ips_tap_primaire_region.csv",
    "ecoles_primaire_region_statut.csv",
    "nouveaux_inscrits_cp1_region_sexe.csv",
]

CLES_TRI = {
    "effectifs_primaire_region_sexe.csv": ["REGION", "SEXE"],
    "effectifs_primaire_milieu_sexe.csv": ["MILIEU", "SEXE"],
    "tba_primaire_region_sexe.csv": ["REGION"],
    "tbs_primaire_region_sexe.csv": ["REGION"],
    "tap_primaire_region_sexe.csv": ["REGION"],
    "taux_reussite_cep_region_sexe.csv": ["REGION", "SEXE"],
    "ips_tba_primaire_region.csv": ["REGION"],
    "ips_tbs_primaire_region.csv": ["REGION"],
    "ips_tap_primaire_region.csv": ["REGION"],
    "ecoles_primaire_region_statut.csv": ["REGION", "STATUT"],
    "nouveaux_inscrits_cp1_region_sexe.csv": [
        "REGION", "ANNEE_SCOLAIRE", "SEXE"
    ],
}


# ============================================================
# 3. VERIFICATION DES FICHIERS NECESSAIRES
# ============================================================

def verifier_presence():

    chemins = [
        FICHIER_EXCEL,
        DOSSIER_SCRIPTS_NETTOYAGE,
        DOSSIER_SCRIPTS_HARMONISATION,
        DOSSIER_DONNEES_FINALES,
    ]

    for chemin in chemins:

        if not chemin.exists():
            raise FileNotFoundError(
                f"Élément requis introuvable : {chemin}"
            )

    for nom in FICHIERS:

        if not (DOSSIER_DONNEES_FINALES / nom).exists():
            raise FileNotFoundError(
                f"Fichier nettoyé introuvable : {nom}"
            )


# ============================================================
# 4. RECONSTRUCTION DES DONNEES A PARTIR DE L'EXCEL
# ============================================================

def reconstruire_donnees_source(dossier_temporaire):

    racine_temp = Path(dossier_temporaire)

    dossier_scripts = (
        racine_temp / "src" / "03_data_cleaning"
    )

    dossier_nettoyage = (
        dossier_scripts / "01_sheet_cleaning"
    )

    dossier_harmonisation = (
        dossier_scripts / "02_data_harmonization"
    )

    dossier_brut = (
        racine_temp / "data" / "01_raw_data"
    )

    dossier_nettoyage.mkdir(parents=True, exist_ok=True)
    dossier_harmonisation.mkdir(parents=True, exist_ok=True)
    dossier_brut.mkdir(parents=True, exist_ok=True)

    # Copie du classeur Excel original
    shutil.copy2(
        FICHIER_EXCEL,
        dossier_brut / "donnees_education_bf.xlsx"
    )

    # Copie des scripts de nettoyage
    for fichier in DOSSIER_SCRIPTS_NETTOYAGE.glob("*.py"):

        shutil.copy2(
            fichier,
            dossier_nettoyage / fichier.name
        )

    # Copie des scripts d'harmonisation
    for fichier in DOSSIER_SCRIPTS_HARMONISATION.glob("*.py"):

        shutil.copy2(
            fichier,
            dossier_harmonisation / fichier.name
        )

    # Vérification du nombre de scripts
    scripts = sorted(dossier_nettoyage.glob("*.py"))

    if len(scripts) != 11:

        raise ValueError(
            f"11 scripts de nettoyage attendus, "
            f"{len(scripts)} trouvés."
        )

    # Exécution des 11 scripts de nettoyage
    for script in scripts:

        print(f"\nExécution : {script.name}")

        resultat = subprocess.run(
            [sys.executable, str(script)],
            cwd=racine_temp,
            capture_output=True,
            text=True
        )

        if resultat.returncode != 0:

            raise RuntimeError(
                f"Échec du script {script.name}.\n"
                f"{resultat.stdout}\n"
                f"{resultat.stderr}"
            )

    # Exécution du script d'harmonisation
    script_harmonisation = (
        dossier_harmonisation /
        "13_harmonisation_et_suppression_totaux.py"
    )

    if not script_harmonisation.exists():

        raise FileNotFoundError(
            "Script d'harmonisation introuvable."
        )

    resultat = subprocess.run(
        [sys.executable, str(script_harmonisation)],
        cwd=racine_temp,
        capture_output=True,
        text=True
    )

    if resultat.returncode != 0:

        raise RuntimeError(
            "Échec du script d'harmonisation.\n"
            f"{resultat.stdout}\n"
            f"{resultat.stderr}"
        )

    return racine_temp


# ============================================================
# 5. LECTURE ET PREPARATION DES FICHIERS
# ============================================================

def lire_csv(chemin):

    return pd.read_csv(
        chemin,
        encoding="utf-8-sig"
    )


def preparer_tableau(df, cles):

    df = df.copy()

    df.columns = [
        str(colonne).strip()
        for colonne in df.columns
    ]

    # Normalisation des espaces dans les valeurs textuelles
    for colonne in df.columns:

        if pd.api.types.is_object_dtype(df[colonne]):

            df[colonne] = (
                df[colonne]
                .astype("string")
                .str.strip()
            )

    # Vérification des clés
    colonnes_absentes = [
        cle for cle in cles
        if cle not in df.columns
    ]

    if colonnes_absentes:

        raise ValueError(
            f"Clés absentes : {colonnes_absentes}"
        )

    return df.sort_values(
        by=cles,
        kind="stable"
    ).reset_index(drop=True)


# ============================================================
# 6. COMPARAISON DES VALEURS
# ============================================================

def comparer_tableaux(df_reference, df_final):

    if list(df_reference.columns) != list(df_final.columns):

        return {
            "statut": "A_VERIFIER",
            "ecarts": "Colonnes différentes",
            "valeurs_comparees": 0,
            "valeurs_differentes": 0,
        }

    if df_reference.shape != df_final.shape:

        return {
            "statut": "A_VERIFIER",
            "ecarts": "Dimensions différentes",
            "valeurs_comparees": 0,
            "valeurs_differentes": 0,
        }

    valeurs_comparees = 0
    valeurs_differentes = 0
    details = []

    for colonne in df_reference.columns:

        reference = df_reference[colonne]
        final = df_final[colonne]

        ref_num = pd.to_numeric(
            reference,
            errors="coerce"
        )

        fin_num = pd.to_numeric(
            final,
            errors="coerce"
        )

        est_numerique = (
            ref_num.notna().any()
            or fin_num.notna().any()
            or (
                reference.isna().all()
                and final.isna().all()
            )
        )

        if est_numerique:

            valeurs_comparees += len(reference)

            meme_valeur = (
                (ref_num - fin_num).abs() <= 1e-9
            ) | (
                ref_num.isna() & fin_num.isna()
            )

        else:

            valeurs_comparees += len(reference)

            ref_txt = (
                reference
                .fillna("<MANQUANT>")
                .astype(str)
            )

            fin_txt = (
                final
                .fillna("<MANQUANT>")
                .astype(str)
            )

            meme_valeur = ref_txt == fin_txt

        nombre_ecarts = int(
            (~meme_valeur).sum()
        )

        if nombre_ecarts > 0:

            valeurs_differentes += nombre_ecarts

            details.append(
                f"{colonne}: {nombre_ecarts} différence(s)"
            )

    return {
        "statut": (
            "FIDÈLE"
            if valeurs_differentes == 0
            else "A_VERIFIER"
        ),
        "ecarts": "; ".join(details),
        "valeurs_comparees": valeurs_comparees,
        "valeurs_differentes": valeurs_differentes,
    }


# ============================================================
# 7. VERIFICATION DE FIDELITE DES 11 FICHIERS
# ============================================================

def verifier_fidelite(racine_temp):

    rapports = []

    for nom_fichier in FICHIERS:

        fichier_final = (
            DOSSIER_DONNEES_FINALES / nom_fichier
        )

        # Le fichier CP1 est généré directement
        # dans data/03_cleaned_data/final.
        if nom_fichier == "nouveaux_inscrits_cp1_region_sexe.csv":

            fichier_reconstruit = (
                racine_temp / "data" /
                "03_cleaned_data" / "final" /
                nom_fichier
            )

        else:

            fichier_reconstruit = (
                racine_temp / "data" /
                "final" / nom_fichier
            )

        if not fichier_reconstruit.exists():

            raise FileNotFoundError(
                f"Fichier reconstruit introuvable : "
                f"{fichier_reconstruit}"
            )

        df_reference = lire_csv(fichier_reconstruit)
        df_final = lire_csv(fichier_final)

        cles = CLES_TRI[nom_fichier]

        df_reference = preparer_tableau(
            df_reference,
            cles
        )

        df_final = preparer_tableau(
            df_final,
            cles
        )

        resultat = comparer_tableaux(
            df_reference,
            df_final
        )

        rapports.append({
            "fichier": nom_fichier,
            "lignes_reconstruites": len(df_reference),
            "lignes_fichier_final": len(df_final),
            "colonnes": len(df_final.columns),
            **resultat,
        })

        print(
            f"{nom_fichier} : {resultat['statut']} | "
            f"Différences : {resultat['valeurs_differentes']}"
        )

    # Création du rapport
    rapport = pd.DataFrame(rapports)

    DOSSIER_RAPPORT.mkdir(
        parents=True,
        exist_ok=True
    )

    rapport.to_csv(
        FICHIER_RAPPORT,
        index=False,
        encoding="utf-8-sig"
    )

    # Résumé final
    print("\n" + "=" * 60)
    print("BILAN DE LA VERIFICATION DE FIDELITE")
    print("=" * 60)

    print("Fichiers contrôlés :", len(rapport))

    print(
        "Fichiers fidèles :",
        int((rapport["statut"] == "FIDÈLE").sum())
    )

    print(
        "Fichiers à vérifier :",
        int((rapport["statut"] != "FIDÈLE").sum())
    )

    print(
        "Différences détectées :",
        int(rapport["valeurs_differentes"].sum())
    )

    print(
        "\nRapport enregistré :",
        FICHIER_RAPPORT
    )

    if (rapport["statut"] != "FIDÈLE").any():

        print(
            "\nVERIFICATION NON VALIDEE : "
            "examiner le rapport."
        )

    else:

        print(
            "\nVERIFICATION DE FIDELITE "
            "TERMINEE AVEC SUCCES."
        )


# ============================================================
# 8. EXECUTION PRINCIPALE
# ============================================================

def main():

    print(
        "VERIFICATION DE FIDELITE : "
        "EXCEL ORIGINAL -> CSV NETTOYES"
    )

    verifier_presence()

    with tempfile.TemporaryDirectory(
        prefix="eduequity_fidelite_"
    ) as dossier_temporaire:

        racine_temp = reconstruire_donnees_source(
            dossier_temporaire
        )

        verifier_fidelite(racine_temp)


if __name__ == "__main__":
    main()