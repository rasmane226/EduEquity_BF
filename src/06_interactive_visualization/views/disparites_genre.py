
import streamlit as st
import pandas as pd
import plotly.express as px

from config import COLORS


# ============================================================
# 1. CONFIGURATION
# ============================================================

INDICATORS = {
    "ECART_TBA": "Écart TBA",
    "ECART_TBS": "Écart TBS",
    "ECART_TAP": "Écart TAP",
}

INDICATOR_COLORS = {
    "ECART_TBA": "#087E8B",
    "ECART_TBS": "#3986C8",
    "ECART_TAP": "#D66B91",
}


# ============================================================
# 2. PREPARATION DES DONNEES
# ============================================================

def prepare_evolution_data(gender_data):

    df = gender_data["evolution_gaps"].copy()

    df = df.sort_values("ORDRE_ANNEE")

    return df


def prepare_regional_data(gender_data):

    df = gender_data["regional_gaps"].copy()

    return df.sort_values("REGION")


def prepare_details_data(gender_data):

    df = gender_data["details"].copy()

    df = df.sort_values(
        ["REGION", "ORDRE_ANNEE"]
    )

    return df


# ============================================================
# 3. GRAPHIQUE DE L'EVOLUTION NATIONALE
# ============================================================

def create_evolution_chart(df):

    melted = df.melt(
        id_vars=[
            "ORDRE_ANNEE",
            "ANNEE_SCOLAIRE",
        ],
        value_vars=[
            "ECART_TBA",
            "ECART_TBS",
            "ECART_TAP",
        ],
        var_name="INDICATEUR",
        value_name="ECART",
    )

    melted["INDICATEUR"] = melted[
        "INDICATEUR"
    ].map(INDICATORS)

    fig = px.line(
        melted,
        x="ANNEE_SCOLAIRE",
        y="ECART",
        color="INDICATEUR",
        markers=True,
        color_discrete_sequence=[
            INDICATOR_COLORS["ECART_TBA"],
            INDICATOR_COLORS["ECART_TBS"],
            INDICATOR_COLORS["ECART_TAP"],
        ],
        labels={
            "ANNEE_SCOLAIRE": "Année scolaire",
            "ECART": "Écart (points)",
            "INDICATEUR": "Indicateur",
        },
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#DC5353",
        annotation_text="Égalité",
    )

    fig.update_layout(
        height=480,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Inter",
            color=COLORS["primary"],
        ),
        legend_title="Indicateur",
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20,
        ),
        hovermode="x unified",
    )

    return fig


# ============================================================
# 4. GRAPHIQUE DES ECARTS REGIONAUX
# ============================================================

def create_regional_chart(df):

    melted = df.melt(
        id_vars=["REGION"],
        value_vars=[
            "ECART_TBA",
            "ECART_TBS",
            "ECART_TAP",
        ],
        var_name="INDICATEUR",
        value_name="ECART",
    )

    melted["INDICATEUR"] = melted[
        "INDICATEUR"
    ].map(INDICATORS)

    fig = px.bar(
        melted,
        x="ECART",
        y="REGION",
        color="INDICATEUR",
        barmode="group",
        orientation="h",
        color_discrete_sequence=[
            INDICATOR_COLORS["ECART_TBA"],
            INDICATOR_COLORS["ECART_TBS"],
            INDICATOR_COLORS["ECART_TAP"],
        ],
        labels={
            "ECART": "Écart (points)",
            "REGION": "Région",
            "INDICATEUR": "Indicateur",
        },
    )

    fig.add_vline(
        x=0,
        line_dash="dash",
        line_color="#DC5353",
    )

    fig.update_layout(
        height=650,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Inter",
            color=COLORS["primary"],
        ),
        margin=dict(
            l=10,
            r=20,
            t=20,
            b=20,
        ),
        legend_title="Indicateur",
    )

    return fig


# ============================================================
# 5. GRAPHIQUE DETAILLE PAR REGION
# ============================================================

def create_region_chart(df, region):

    region_df = df[
        df["REGION"] == region
    ].copy()

    region_df = region_df.sort_values(
        "ORDRE_ANNEE"
    )

    melted = region_df.melt(
        id_vars=[
            "ANNEE_SCOLAIRE",
            "ORDRE_ANNEE",
        ],
        value_vars=[
            "ECART_TBA",
            "ECART_TBS",
            "ECART_TAP",
        ],
        var_name="INDICATEUR",
        value_name="ECART",
    )

    melted["INDICATEUR"] = melted[
        "INDICATEUR"
    ].map(INDICATORS)

    fig = px.line(
        melted,
        x="ANNEE_SCOLAIRE",
        y="ECART",
        color="INDICATEUR",
        markers=True,
        color_discrete_sequence=[
            INDICATOR_COLORS["ECART_TBA"],
            INDICATOR_COLORS["ECART_TBS"],
            INDICATOR_COLORS["ECART_TAP"],
        ],
        labels={
            "ANNEE_SCOLAIRE": "Année scolaire",
            "ECART": "Écart (points)",
            "INDICATEUR": "Indicateur",
        },
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#DC5353",
    )

    fig.update_layout(
        height=450,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Inter",
            color=COLORS["primary"],
        ),
        hovermode="x unified",
    )

    return fig


# ============================================================
# 6. INTERPRETATION DES ECARTS
# ============================================================

def interpret_gap(value):

    if pd.isna(value):
        return "Donnée non disponible"

    if value < 0:
        return "Écart défavorable aux filles"

    elif value > 0:
        return "Écart favorable aux filles"

    return "Égalité entre filles et garçons"


# ============================================================
# 7. PAGE PRINCIPALE
# ============================================================

def render(gender_data):

    st.title("Disparités de genre")

    st.write(
        "Analyse des différences entre filles et garçons "
        "dans l'accès et le parcours scolaire au Burkina Faso."
    )

    st.caption(
        "Source : données DGESS | Période : 2015-2016 à 2024-2025"
    )

    st.divider()

    # Vérification des données

    required_keys = [
        "evolution_gaps",
        "regional_gaps",
        "details",
    ]

    for key in required_keys:

        if key not in gender_data:

            st.error(
                f"Jeu de données manquant : {key}"
            )

            return

    evolution = prepare_evolution_data(gender_data)

    regional = prepare_regional_data(gender_data)

    details = prepare_details_data(gender_data)

    # ========================================================
    # SECTION 1 : EVOLUTION NATIONALE
    # ========================================================

    st.subheader("1. Évolution nationale des écarts de genre")

    st.write(
        "Cette analyse présente l'évolution des écarts "
        "entre filles et garçons pour les trois indicateurs."
    )

    fig_evolution = create_evolution_chart(evolution)

    st.plotly_chart(
        fig_evolution,
        use_container_width=True,
    )

    st.caption(
        "Un écart négatif indique une situation défavorable "
        "aux filles. Un écart positif indique une situation "
        "favorable aux filles."
    )

    st.divider()

    # ========================================================
    # SECTION 2 : COMPARAISON REGIONALE
    # ========================================================

    st.subheader("2. Comparaison des écarts entre régions")

    st.write(
        "Comparaison des écarts moyens de TBA, TBS et TAP "
        "entre les 13 régions."
    )

    fig_regional = create_regional_chart(regional)

    st.plotly_chart(
        fig_regional,
        use_container_width=True,
    )

    st.divider()

    # ========================================================
    # SECTION 3 : DIAGNOSTIC REGIONAL
    # ========================================================

    st.subheader("3. Diagnostic par région")

    selected_region = st.selectbox(
        "Sélectionner une région",
        options=sorted(details["REGION"].unique()),
        key="gender_region",
    )

    region_data = details[
        details["REGION"] == selected_region
    ].sort_values("ORDRE_ANNEE")

    st.markdown(f"### {selected_region}")

    latest = region_data.iloc[-1]

    col1, col2, col3 = st.columns(3)

    for col, indicator in zip(
        [col1, col2, col3],
        ["ECART_TBA", "ECART_TBS", "ECART_TAP"],
    ):

        value = latest[indicator]

        with col:

            st.metric(
                label=INDICATORS[indicator],
                value=f"{value:.2f} points",
            )

            st.caption(
                interpret_gap(value)
            )

    fig_region = create_region_chart(
        details,
        selected_region,
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True,
    )

    st.caption(
        f"Année scolaire la plus récente disponible : "
        f"{latest['ANNEE_SCOLAIRE']}"
    )

    st.divider()

    # ========================================================
    # SECTION 4 : TABLEAU DES DONNEES
    # ========================================================

    with st.expander(
        "Afficher les données détaillées des écarts"
    ):

        display_columns = [
            "REGION",
            "ANNEE_SCOLAIRE",
            "ECART_TBA",
            "ECART_TBS",
            "ECART_TAP",
        ]

        st.dataframe(
            details[display_columns],
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            label="Télécharger les données CSV",
            data=details[
                display_columns
            ].to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="ecarts_genre_region_annee.csv",
            mime="text/csv",
        )

    st.caption(
        "Les écarts sont calculés selon la convention : "
        "valeur des filles moins valeur des garçons."
    )
