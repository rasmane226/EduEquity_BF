
import json

import streamlit as st
import plotly.express as px

from config import GEOJSON_FILE, COLORS, INDICATORS


# ============================================================
# 1. CONFIGURATION
# ============================================================

INDICATOR_NAMES = INDICATORS

BURKINA_CENTER = {
    "lat": 12.3,
    "lon": -1.7,
}


# ============================================================
# 2. CHARGEMENT DU GEOJSON
# ============================================================

@st.cache_data
def load_geojson():

    if not GEOJSON_FILE.exists():
        raise FileNotFoundError(
            f"Fichier GeoJSON introuvable : {GEOJSON_FILE}"
        )

    with open(GEOJSON_FILE, "r", encoding="utf-8") as file:
        geojson = json.load(file)

    if geojson.get("type") != "FeatureCollection":
        raise ValueError("Format GeoJSON invalide.")

    features = geojson.get("features", [])

    if len(features) != 13:
        raise ValueError(
            "Le GeoJSON ne contient pas exactement 13 régions."
        )

    # Normaliser les noms des régions du GeoJSON
    for feature in features:

        properties = feature.get("properties", {})

        if "admin1Name" not in properties:
            raise ValueError(
                "Le nom d'une région est absent du GeoJSON."
            )

        region_name = properties["admin1Name"]

        properties["REGION_KEY"] = (
            str(region_name).strip().upper()
        )

    return geojson


# ============================================================
# 3. NORMALISATION DES NOMS
# ============================================================

def normalize_region(name):

    return str(name).strip().upper()


# ============================================================
# 4. PREPARATION DES DONNEES
# ============================================================

def prepare_map_data(regional_data, selected_year):

    df = regional_data["evolution"].copy()

    # Normaliser les noms des régions du CSV
    df["REGION_KEY"] = (
        df["REGION"].apply(normalize_region)
    )

    # Filtrer les données selon l'année sélectionnée
    filtered = df[
        df["ANNEE_SCOLAIRE"] == selected_year
    ].copy()

    if filtered.empty:
        raise ValueError(
            f"Aucune donnée disponible pour {selected_year}."
        )

    # Vérifier la couverture des 13 régions
    if filtered["REGION_KEY"].nunique() != 13:
        raise ValueError(
            "Les données sélectionnées ne couvrent pas les 13 régions."
        )

    # Vérifier qu'une région n'apparaît pas plusieurs fois
    if filtered["REGION_KEY"].duplicated().any():
        raise ValueError(
            "Certaines régions apparaissent plusieurs fois pour cette année."
        )

    # Vérifier les indicateurs disponibles
    for indicator in INDICATORS:

        if indicator not in filtered.columns:
            raise ValueError(
                f"Indicateur manquant dans les données : {indicator}"
            )

    return filtered


# ============================================================
# 5. CREATION DE LA CARTE INTERACTIVE
# ============================================================



def create_choropleth(df, geojson, indicator):

    fig = px.choropleth_map(
        df,
        geojson=geojson,
        locations="REGION_KEY",
        featureidkey="properties.REGION_KEY",
        color=indicator,
        hover_name="REGION",
        hover_data={
            "TBA": ":.2f",
            "TBS": ":.2f",
            "TAP": ":.2f",
            "REGION_KEY": False,
        },
        color_continuous_scale="YlGnBu",
        map_style="carto-positron",
        center={
            "lat": 12.3,
            "lon": -1.7,
        },
        zoom=5.5,
        opacity=0.85,
        labels={
            indicator: f"{indicator} (%)",
            "REGION": "Région",
        },
    )

    fig.update_layout(
        height=650,
        margin=dict(
            r=0,
            t=10,
            l=0,
            b=0,
        ),
        paper_bgcolor="white",
        font=dict(
            family="Inter",
            color=COLORS["primary"],
        ),
        coloraxis_colorbar=dict(
            title=f"{indicator} (%)",
            thickness=14,
            len=0.7,
        ),
    )

    fig.update_traces(
        marker_line_color="white",
        marker_line_width=1.5,
    )

    return fig


# ============================================================
# 6. PAGE PRINCIPALE
# ============================================================

def render(regional_data):

    st.title("Équité territoriale")

    st.write(
        "Explorez les disparités éducatives entre les "
        "13 régions du Burkina Faso à travers une "
        "cartographie interactive."
    )

    st.divider()

    # Charger les données géographiques
    try:

        geojson = load_geojson()

    except Exception as error:

        st.error(f"Erreur cartographique : {error}")
        return

    evolution = regional_data["evolution"].copy()

    # Vérifier les données disponibles
    if evolution.empty:

        st.warning("Aucune donnée régionale disponible.")
        return

    # ========================================================
    # 6.1 FILTRES
    # ========================================================

    col1, col2 = st.columns(2)

    years = sorted(
        evolution["ANNEE_SCOLAIRE"].dropna().unique()
    )

    if len(years) == 0:

        st.warning("Aucune année scolaire disponible.")
        return

    with col1:

        selected_indicator = st.selectbox(
            "Indicateur scolaire",
            options=list(INDICATORS.keys()),
            format_func=lambda x: (
                f"{x} — {INDICATOR_NAMES[x]}"
            ),
        )

    with col2:

        selected_year = st.selectbox(
            "Année scolaire",
            options=years,
            index=len(years) - 1,
        )

    # ========================================================
    # 6.2 PREPARATION DES DONNEES
    # ========================================================

    try:

        map_data = prepare_map_data(
            regional_data,
            selected_year,
        )

        fig = create_choropleth(
            map_data,
            geojson,
            selected_indicator,
        )

    except Exception as error:

        st.error(
            f"Impossible de générer la carte : {error}"
        )
        return

    # ========================================================
    # 6.3 AFFICHAGE DE LA CARTE
    # ========================================================

    st.subheader(
        f"Carte régionale — {selected_indicator}"
    )

    st.caption(
        f"Année scolaire : {selected_year} | "
        "Source : données DGESS"
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": True,
            "scrollZoom": True,
        },
    )

    st.divider()

    # ========================================================
    # 7. DIAGNOSTIC REGIONAL
    # ========================================================

    st.subheader("Diagnostic régional")

    selected_region = st.selectbox(
        "Sélectionner une région",
        options=sorted(map_data["REGION"].unique()),
    )

    region_data = map_data[
        map_data["REGION"] == selected_region
    ].iloc[0]

    st.markdown(f"### {selected_region}")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "TBA",
            f"{region_data['TBA']:.2f} %",
        )

    with col2:

        st.metric(
            "TBS",
            f"{region_data['TBS']:.2f} %",
        )

    with col3:

        st.metric(
            "TAP",
            f"{region_data['TAP']:.2f} %",
        )

    st.divider()

    # ========================================================
    # 8. COMPARAISON DES 13 REGIONS
    # ========================================================

    st.subheader("Comparaison des régions")

    comparison = map_data[
        ["REGION", "TBA", "TBS", "TAP"]
    ].sort_values(
        selected_indicator,
        ascending=True,
    )

    fig_comparison = px.bar(
        comparison,
        x=selected_indicator,
        y="REGION",
        orientation="h",
        color=selected_indicator,
        color_continuous_scale="YlGnBu",
        labels={
            selected_indicator: f"{selected_indicator} (%)",
            "REGION": "Région",
        },
    )

    fig_comparison.update_layout(
        height=550,
        showlegend=False,
        coloraxis_showscale=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(
            l=10,
            r=20,
            t=20,
            b=20,
        ),
    )

    st.plotly_chart(
        fig_comparison,
        use_container_width=True,
    )

    st.divider()

    # ========================================================
    # 9. TABLEAU DES DONNEES
    # ========================================================

    with st.expander("Afficher les données régionales"):

        st.dataframe(
            comparison,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            label="Télécharger les données CSV",
            data=comparison.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="comparaison_regionale.csv",
            mime="text/csv",
        )

    st.caption(
        "Source : DGESS. Les valeurs sont des indicateurs "
        "scolaires régionaux et ne constituent pas des "
        "mesures directes de la population non scolarisée."
    )
