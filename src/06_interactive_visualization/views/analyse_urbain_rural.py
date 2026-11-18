# views/analyse_urbain_rural.py

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from config import URBAN_RURAL_DIR, REGIONS, COLORS


# ============================================================
# 1. CHARGEMENT DES DONNÉES
# ============================================================

INSD_DIR = URBAN_RURAL_DIR / "insd_rgph_2019"


@st.cache_data
def load_urban_rural_data():
    """Charge les fichiers DGESS et INSD nécessaires à l'analyse."""

    files = {
        "annual": URBAN_RURAL_DIR / "evolution_annuelle_urbain_rural.csv",
        "annual_by_sex": URBAN_RURAL_DIR / "evolution_urbain_rural_par_sexe.csv",
        "statistics_by_sex": URBAN_RURAL_DIR / "statistiques_urbain_rural_par_sexe.csv",
        "variation": URBAN_RURAL_DIR / "variation_effectifs_periode.csv",
        "insd_situation": INSD_DIR / "comparaison_situation_scolaire_milieu_sexe.csv",
        "insd_gender_gaps": INSD_DIR / "ecarts_filles_garcons_par_milieu.csv",
        "insd_urban_rural_gaps": INSD_DIR / "ecarts_situation_scolaire_urbain_rural.csv",
        "insd_regional": INSD_DIR / "situation_scolaire_6_11_ans_par_region.csv",
    }

    data = {}

    for key, path in files.items():
        if not path.exists():
            st.error(f"Fichier introuvable : {path.name}")
            return None

        data[key] = pd.read_csv(path)

    return data


# ============================================================
# 2. FONCTIONS UTILITAIRES
# ============================================================

def section_title(title, description=None):
    st.subheader(title)

    if description:
        st.caption(description)


def format_number(value):
    return f"{value:,.0f}".replace(",", " ")


def get_region_data(df):
    """Conserve uniquement les 13 régions, sans la ligne nationale."""

    df = df.copy()
    region_names = {str(region).strip().upper() for region in REGIONS}

    df["_REGION_NORMALIZED"] = df["REGION"].astype(str).str.strip().str.upper()

    return (
        df[df["_REGION_NORMALIZED"].isin(region_names)]
        .drop(columns=["_REGION_NORMALIZED"])
        .copy()
    )


# ============================================================
# 3. ANALYSE DGESS : ÉVOLUTION DES EFFECTIFS
# ============================================================

def render_dgess_annual(data):

    section_title(
        "3.1. Évolution des effectifs scolaires selon le milieu",
        "Source : DGESS — données annuelles de 2015-2016 à 2024-2025. "
        "Les valeurs représentent des effectifs, et non des taux d'accès."
    )

    df = data["annual"].copy()

    col1, col2, col3 = st.columns(3)

    latest = df.iloc[-1]

    with col1:
        st.metric(
            "Effectif urbain",
            format_number(latest["EFFECTIF_URBAIN_TOTAL"])
        )

    with col2:
        st.metric(
            "Effectif rural",
            format_number(latest["EFFECTIF_RURAL_TOTAL"])
        )

    with col3:
        st.metric(
            "Part urbaine",
            f'{latest["PART_URBAINE_DANS_TOTAL"]:.2f} %'
        )

    chart_df = df.melt(
        id_vars="ANNEE_SCOLAIRE",
        value_vars=[
            "EFFECTIF_URBAIN_TOTAL",
            "EFFECTIF_RURAL_TOTAL"
        ],
        var_name="MILIEU",
        value_name="EFFECTIF"
    )

    chart_df["MILIEU"] = chart_df["MILIEU"].replace({
        "EFFECTIF_URBAIN_TOTAL": "Urbain",
        "EFFECTIF_RURAL_TOTAL": "Rural"
    })

    fig = px.line(
        chart_df,
        x="ANNEE_SCOLAIRE",
        y="EFFECTIF",
        color="MILIEU",
        markers=True,
        color_discrete_map={
            "Urbain": COLORS["secondary"],
            "Rural": COLORS["primary"]
        },
        labels={
            "ANNEE_SCOLAIRE": "Année scolaire",
            "EFFECTIF": "Nombre d'élèves",
            "MILIEU": "Milieu"
        },
        title="Évolution des effectifs scolaires urbains et ruraux"
    )

    fig.update_layout(
        hovermode="x unified",
        yaxis_title="Nombre d'élèves",
        xaxis_title="Année scolaire",
        legend_title="Milieu"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Les effectifs ruraux et urbains décrivent la répartition des élèves. "
        "Ils ne permettent pas, à eux seuls, de mesurer les taux d'accès "
        "à l'école dans chaque milieu."
    )


# ============================================================
# 4. ANALYSE DGESS : COMPARAISON PAR SEXE
# ============================================================

def render_dgess_by_sex(data):

    section_title(
        "3.2. Évolution des effectifs selon le sexe et le milieu",
        "Source : DGESS — effectifs annuels des filles et des garçons."
    )

    df = data["annual_by_sex"].copy()

    chart_df = df.melt(
        id_vars=["ANNEE_SCOLAIRE", "SEXE"],
        value_vars=["EFFECTIF_URBAIN", "EFFECTIF_RURAL"],
        var_name="MILIEU",
        value_name="EFFECTIF"
    )

    chart_df["MILIEU"] = chart_df["MILIEU"].replace({
        "EFFECTIF_URBAIN": "Urbain",
        "EFFECTIF_RURAL": "Rural"
    })

    fig = px.line(
        chart_df,
        x="ANNEE_SCOLAIRE",
        y="EFFECTIF",
        color="MILIEU",
        facet_col="SEXE",
        markers=True,
        color_discrete_map={
            "Urbain": COLORS["secondary"],
            "Rural": COLORS["primary"]
        },
        labels={
            "ANNEE_SCOLAIRE": "Année scolaire",
            "EFFECTIF": "Nombre d'élèves",
            "MILIEU": "Milieu",
            "SEXE": "Sexe"
        },
        title="Évolution des effectifs par sexe et milieu"
    )

    fig.update_layout(
        hovermode="x unified",
        legend_title="Milieu"
    )

    st.plotly_chart(fig, use_container_width=True)

    variation = data["variation"].copy()

    variation_long = variation.melt(
        id_vars="SEXE",
        value_vars=[
            "VARIATION_EFFECTIF_URBAIN_POURCENT",
            "VARIATION_EFFECTIF_RURAL_POURCENT"
        ],
        var_name="MILIEU",
        value_name="VARIATION"
    )

    variation_long["MILIEU"] = variation_long["MILIEU"].replace({
        "VARIATION_EFFECTIF_URBAIN_POURCENT": "Urbain",
        "VARIATION_EFFECTIF_RURAL_POURCENT": "Rural"
    })

    fig_variation = px.bar(
        variation_long,
        x="SEXE",
        y="VARIATION",
        color="MILIEU",
        barmode="group",
        text_auto=".2f",
        color_discrete_map={
            "Urbain": COLORS["secondary"],
            "Rural": COLORS["primary"]
        },
        labels={
            "SEXE": "Sexe",
            "VARIATION": "Variation (%)",
            "MILIEU": "Milieu"
        },
        title="Variation des effectifs entre la première et la dernière année"
    )

    fig_variation.add_hline(y=0, line_dash="dash", line_color="gray")

    st.plotly_chart(fig_variation, use_container_width=True)

    st.caption(
        "La variation compare les effectifs de 2015-2016 et de 2024-2025. "
        "Elle décrit une évolution des effectifs, pas une évolution du taux "
        "de scolarisation."
    )


# ============================================================
# 5. ANALYSE INSD : SITUATION SCOLAIRE PAR MILIEU
# ============================================================

def render_insd_situation(data):

    section_title(
        "3.3. Situation scolaire selon le milieu de résidence",
        "Source : INSD — RGPH 2019, enfants âgés de 6 à 11 ans. "
        "Les valeurs sont des pourcentages."
    )

    df = data["insd_situation"].copy()

    # Sélection de la ligne Ensemble pour comparer les deux milieux.
    overall = df[
        df["SEXE"].astype(str).str.strip().str.lower().isin(
            ["ensemble", "total", "tous"]
        )
    ].copy()

    if overall.empty:
        st.warning(
            "La ligne correspondant à l'ensemble des sexes "
            "n'a pas été trouvée dans le fichier INSD."
        )
        return

    chart_df = overall.melt(
        id_vars="MILIEU_RESIDENCE",
        value_vars=["Scolarisé", "Déscolarisé", "Jamais fréquenté"],
        var_name="STATUT",
        value_name="POURCENTAGE"
    )

    fig = px.bar(
        chart_df,
        x="MILIEU_RESIDENCE",
        y="POURCENTAGE",
        color="STATUT",
        barmode="group",
        text_auto=".1f",
        labels={
            "MILIEU_RESIDENCE": "Milieu de résidence",
            "POURCENTAGE": "Pourcentage (%)",
            "STATUT": "Situation scolaire"
        },
        title="Situation scolaire des enfants de 6 à 11 ans"
    )

    fig.update_layout(
        yaxis_title="Pourcentage (%)",
        xaxis_title="Milieu de résidence",
        legend_title="Situation"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Les données INSD décrivent la situation scolaire au moment du "
        "recensement de 2019. Elles ne constituent pas une série annuelle."
    )


# ============================================================
# 6. ANALYSE INSD : ÉCARTS ENTRE FILLES ET GARÇONS
# ============================================================

def render_insd_gender_gaps(data):

    section_title(
        "3.4. Écarts entre filles et garçons selon le milieu",
        "Source : INSD — RGPH 2019. Écart calculé comme "
        "pourcentage féminin moins pourcentage masculin."
    )

    df = data["insd_gender_gaps"].copy()

    fig = px.bar(
        df,
        x="STATUT_SCOLAIRE",
        y="ECART_FEMININ_MOINS_MASCULIN",
        color="MILIEU_RESIDENCE",
        barmode="group",
        text_auto=".1f",
        labels={
            "STATUT_SCOLAIRE": "Situation scolaire",
            "ECART_FEMININ_MOINS_MASCULIN": "Écart (points de pourcentage)",
            "MILIEU_RESIDENCE": "Milieu"
        },
        title="Écarts filles-garçons par situation scolaire et milieu"
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray")

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Un écart négatif indique un pourcentage féminin inférieur au "
        "pourcentage masculin. Un écart positif indique l'inverse."
    )


# ============================================================
# 7. ANALYSE INSD : DISPARITÉS RÉGIONALES
# ============================================================

def render_insd_regional(data):

    section_title(
        "3.5. Disparités régionales de la situation scolaire",
        "Source : INSD — RGPH 2019, enfants âgés de 6 à 11 ans."
    )

    df = get_region_data(data["insd_regional"])

    if df.empty:
        st.warning(
            "Aucune des 13 régions configurées n'a été retrouvée "
            "dans le fichier régional INSD."
        )
        return

    indicator = st.selectbox(
        "Choisir un indicateur",
        options=[
            "SCOLARISE_PCT",
            "DESCOLARISE_PCT",
            "JAMAIS_FREQUENTE_PCT"
        ],
        format_func=lambda x: {
            "SCOLARISE_PCT": "Enfants scolarisés",
            "DESCOLARISE_PCT": "Enfants déscolarisés",
            "JAMAIS_FREQUENTE_PCT": "Enfants n'ayant jamais fréquenté"
        }[x],
        key="insd_regional_indicator"
    )

    labels = {
        "SCOLARISE_PCT": "Scolarisés (%)",
        "DESCOLARISE_PCT": "Déscolarisés (%)",
        "JAMAIS_FREQUENTE_PCT": "Jamais fréquenté (%)"
    }

    df = df.sort_values(indicator, ascending=True)

    fig = px.bar(
        df,
        x=indicator,
        y="REGION",
        orientation="h",
        text_auto=".1f",
        labels={
            indicator: labels[indicator],
            "REGION": "Région"
        },
        title=labels[indicator] + " par région"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Cette comparaison concerne uniquement les enfants de 6 à 11 ans "
        "au RGPH 2019. Elle ne doit pas être interprétée comme une évolution "
        "annuelle des régions."
    )


# ============================================================
# 8. FONCTION PRINCIPALE
# ============================================================

def render():

    st.title("Analyse des disparités urbain-rural")

    st.markdown(
        """
        Cette section examine les différences de situation scolaire
        entre les milieux urbain et rural au Burkina Faso.

        L'analyse s'appuie sur deux sources complémentaires :
        les données annuelles de la DGESS et le RGPH 2019 de l'INSD.
        """
    )

    data = load_urban_rural_data()

    if data is None:
        st.error(
            "Le module ne peut pas être affiché car certains fichiers "
            "de données sont introuvables."
        )
        return

    st.divider()

    st.header("Partie I — Données annuelles DGESS")

    render_dgess_annual(data)
    st.divider()

    render_dgess_by_sex(data)
    st.divider()

    st.header("Partie II — Recensement INSD 2019")

    render_insd_situation(data)
    st.divider()

    render_insd_gender_gaps(data)
    st.divider()

    render_insd_regional(data)

    st.divider()

    st.caption(
        "EduEquity BF | Sources : DGESS et INSD — RGPH 2019"
    )