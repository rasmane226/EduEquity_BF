
import json
import unicodedata

import pandas as pd
import plotly.express as px
import streamlit as st

from config import (
    GEOJSON_FILE,
    GENDER_DIR,
    URBAN_RURAL_DIR,
    PRIORITIZATION_DIR,
    REGIONS,
)


# ============================================================
# 1. CONFIGURATION
# ============================================================

REGIONAL_DIAGNOSTIC_FILE = (
    PRIORITIZATION_DIR / "diagnostic_disparites_regionaux.csv"
)

URBAN_DIAGNOSTIC_FILE = (
    PRIORITIZATION_DIR / "diagnostic_urbain_rural.csv"
)

INSD_DIR = URBAN_RURAL_DIR / "insd_rgph_2019"

INSD_GAPS_FILE = (
    INSD_DIR / "ecarts_situation_scolaire_urbain_rural.csv"
)

INSD_REGIONAL_FILE = (
    INSD_DIR / "situation_scolaire_6_11_ans_par_region.csv"
)

GENDER_EVOLUTION_FILE = (
    GENDER_DIR / "evolution_ecarts_genre.csv"
)

NAVY = "#17365D"
BLUE = "#2878A5"
TEAL = "#087E8B"
ORANGE = "#E69F35"
RED = "#D95F59"
GREEN = "#299D75"
GREY = "#64748B"

GENDER_COLUMNS = [
    "ECART_TBA",
    "ECART_TBS",
    "ECART_TAP",
]

INSD_COLUMNS = [
    "DESCOLARISE_PCT",
    "JAMAIS_FREQUENTE_PCT",
    "SCOLARISE_PCT",
]

GENDER_LABELS = {
    "ECART_TBA": "TBA",
    "ECART_TBS": "TBS",
    "ECART_TAP": "TAP",
}


# ============================================================
# 2. OUTILS ET CHARGEMENT DES DONNEES
# ============================================================

def normalize_region(value):

    value = str(value).strip().upper()

    value = unicodedata.normalize(
        "NFKD",
        value
    )

    return "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )


def read_csv_checked(
    path,
    separator,
    required_columns,
    label
):

    if not path.exists():

        raise FileNotFoundError(
            f"Fichier manquant ({label}) : {path}"
        )

    df = pd.read_csv(
        path,
        sep=separator,
        encoding="utf-8-sig"
    )

    df.columns = df.columns.str.strip()

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Colonnes absentes dans {label} : {missing}"
        )

    if df.empty:

        raise ValueError(
            f"Le fichier {label} est vide."
        )

    return df


@st.cache_data
def load_decision_data():

    # --------------------------------------------------------
    # 1. CHARGEMENT DU DIAGNOSTIC REGIONAL
    # --------------------------------------------------------

    regional = read_csv_checked(
        REGIONAL_DIAGNOSTIC_FILE,
        ";",
        [
            "REGION",
            "SCORE_TERRITORIAL",
            "RANG_PRIORITE_TERRITORIALE",
            "PROFIL_REGIONAL",
            "ECART_TBA",
            "ECART_TBS",
            "ECART_TAP",
            "DIAGNOSTIC_GENRE",
            "NIVEAU_DIFFICULTE_TERRITORIALE",
            "DIAGNOSTIC_COMBINE",
        ],
        "diagnostic régional",
    )

    # --------------------------------------------------------
    # 2. CHARGEMENT DU DIAGNOSTIC URBAIN-RURAL
    # --------------------------------------------------------

    urban_diagnostic = read_csv_checked(
        URBAN_DIAGNOSTIC_FILE,
        ";",
        [
            "PREMIERE_ANNEE",
            "DERNIERE_ANNEE",
            "EFFECTIF_URBAIN_INITIAL",
            "EFFECTIF_URBAIN_FINAL",
            "VARIATION_URBAINE_PCT",
            "EFFECTIF_RURAL_INITIAL",
            "EFFECTIF_RURAL_FINAL",
            "VARIATION_RURALE_PCT",
        ],
        "diagnostic urbain-rural",
    )

    # --------------------------------------------------------
    # 3. DONNEES INSD URBAIN-RURAL
    # --------------------------------------------------------

    insd_gaps = read_csv_checked(
        INSD_GAPS_FILE,
        ",",
        [
            "STATUT_SCOLAIRE",
            "Rural",
            "Urbain",
            "ECART_URBAIN_MOINS_RURAL",
        ],
        "écarts INSD urbain-rural",
    )

    # --------------------------------------------------------
    # 4. DONNEES INSD PAR REGION
    # --------------------------------------------------------

    insd_regional = read_csv_checked(
        INSD_REGIONAL_FILE,
        ",",
        [
            "REGION",
            *INSD_COLUMNS,
        ],
        "situation scolaire régionale INSD",
    )

    # --------------------------------------------------------
    # 5. EVOLUTION DES ECARTS DE GENRE
    # --------------------------------------------------------

    gender_evolution = read_csv_checked(
        GENDER_EVOLUTION_FILE,
        ",",
        [
            "ANNEE_SCOLAIRE",
            *GENDER_COLUMNS,
        ],
        "évolution des écarts de genre",
    )

    # --------------------------------------------------------
    # 6. NORMALISATION DES REGIONS
    # --------------------------------------------------------

    valid_regions = {
        normalize_region(region)
        for region in REGIONS
    }

    regional["REGION"] = (
        regional["REGION"].astype(str).str.strip()
    )

    regional["REGION_KEY"] = (
        regional["REGION"].apply(normalize_region)
    )

    regional = regional[
        regional["REGION_KEY"].isin(valid_regions)
    ].copy()

    if regional["REGION_KEY"].duplicated().any():

        raise ValueError(
            "Des régions sont présentes plusieurs fois "
            "dans le diagnostic régional."
        )

    if len(regional) != 13:

        raise ValueError(
            f"13 régions attendues dans le diagnostic, "
            f"{len(regional)} trouvées."
        )

    # --------------------------------------------------------
    # 7. CONVERSION DES VARIABLES NUMERIQUES
    # --------------------------------------------------------

    for column in [
        "SCORE_TERRITORIAL",
        "RANG_PRIORITE_TERRITORIALE",
        *GENDER_COLUMNS,
    ]:

        regional[column] = pd.to_numeric(
            regional[column],
            errors="coerce"
        )

    if regional[
        [
            "SCORE_TERRITORIAL",
            "RANG_PRIORITE_TERRITORIALE",
            *GENDER_COLUMNS,
        ]
    ].isna().any().any():

        raise ValueError(
            "Valeurs numériques manquantes dans "
            "le diagnostic régional."
        )

    # --------------------------------------------------------
    # 8. PREPARATION DES DONNEES INSD REGIONALES
    # --------------------------------------------------------

    insd_regional["REGION_KEY"] = (
        insd_regional["REGION"].apply(normalize_region)
    )

    insd_regional = insd_regional[
        insd_regional["REGION_KEY"].isin(valid_regions)
    ].copy()

    if insd_regional["REGION_KEY"].duplicated().any():

        raise ValueError(
            "Des régions sont présentes plusieurs fois "
            "dans les données INSD."
        )

    if len(insd_regional) != 13:

        raise ValueError(
            f"13 régions INSD attendues, "
            f"{len(insd_regional)} trouvées."
        )

    for column in INSD_COLUMNS:

        insd_regional[column] = pd.to_numeric(
            insd_regional[column],
            errors="coerce"
        )

    if insd_regional[INSD_COLUMNS].isna().any().any():

        raise ValueError(
            "Valeurs manquantes dans les données INSD régionales."
        )

    # --------------------------------------------------------
    # 9. FUSION DES DONNEES TERRITORIALES ET INSD
    # --------------------------------------------------------

    regional = regional.merge(
        insd_regional[
            [
                "REGION_KEY",
                *INSD_COLUMNS,
            ]
        ],
        on="REGION_KEY",
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    unmatched = regional[
        regional["_merge"] != "both"
    ]

    if not unmatched.empty:

        missing_regions = unmatched["REGION"].tolist()

        raise ValueError(
            "Correspondance INSD impossible pour : "
            f"{missing_regions}"
        )

    regional = regional.drop(
        columns=["_merge"]
    )

    # --------------------------------------------------------
    # 10. PREPARATION DES DONNEES DE GENRE
    # --------------------------------------------------------

    for column in GENDER_COLUMNS:

        gender_evolution[column] = pd.to_numeric(
            gender_evolution[column],
            errors="coerce"
        )

    gender_evolution = gender_evolution.dropna(
        subset=GENDER_COLUMNS
    ).copy()

    if gender_evolution.empty:

        raise ValueError(
            "Aucune donnée valide pour l'évolution des écarts de genre."
        )

    # --------------------------------------------------------
    # 11. PREPARATION DES DONNEES URBAIN-RURAL
    # --------------------------------------------------------

    numeric_urban_columns = [
        "VARIATION_URBAINE_PCT",
        "VARIATION_RURALE_PCT",
    ]

    for column in numeric_urban_columns:

        urban_diagnostic[column] = pd.to_numeric(
            urban_diagnostic[column],
            errors="coerce"
        )

    if urban_diagnostic[numeric_urban_columns].isna().any().any():

        raise ValueError(
            "Valeurs manquantes dans le diagnostic urbain-rural."
        )

    for column in [
        "Rural",
        "Urbain",
        "ECART_URBAIN_MOINS_RURAL",
    ]:

        insd_gaps[column] = pd.to_numeric(
            insd_gaps[column],
            errors="coerce"
        )

    if insd_gaps[
        [
            "Rural",
            "Urbain",
            "ECART_URBAIN_MOINS_RURAL",
        ]
    ].isna().any().any():

        raise ValueError(
            "Valeurs manquantes dans les écarts INSD urbain-rural."
        )

    # --------------------------------------------------------
    # 12. CALCUL DU SEUIL COMPARATIF
    # --------------------------------------------------------

    median_score = regional[
        "SCORE_TERRITORIAL"
    ].median()

    regional["NIVEAU_DIFFICULTE_CALCULEE"] = regional[
        "SCORE_TERRITORIAL"
    ].apply(
        lambda score:
        "Difficulté relative élevée"
        if score >= median_score
        else "Difficulté relative moins élevée"
    )

    return {
        "regional": regional.sort_values(
            "RANG_PRIORITE_TERRITORIALE"
        ),
        "urban_diagnostic": urban_diagnostic,
        "insd_gaps": insd_gaps,
        "insd_regional": insd_regional,
        "gender_evolution": gender_evolution,
        "median_score": median_score,
    }


# ============================================================
# 3. DIAGNOSTIC ET RECOMMANDATIONS
# ============================================================

def gender_direction(value):

    if value < 0:

        return "Désavantage relatif des filles"

    if value > 0:

        return "Désavantage relatif des garçons"

    return "Parité sur cet indicateur"


def build_recommendations(row, median_score):

    recommendations = []

    profile = str(row["PROFIL_REGIONAL"])

    score = float(row["SCORE_TERRITORIAL"])

    # --------------------------------------------------------
    # A. RECOMMANDATIONS TERRITORIALES
    # --------------------------------------------------------

    if profile == "Non-fréquentation dominante":

        recommendations.append(
            "Prioriser l'identification des enfants n'ayant "
            "jamais fréquenté l'école et approfondir les obstacles "
            "à leur première inscription."
        )

    elif profile == "Déscolarisation dominante":

        recommendations.append(
            "Renforcer l'analyse des parcours scolaires et "
            "examiner les facteurs associés à la sortie du système "
            "éducatif."
        )

    elif profile == "Difficultés cumulées":

        recommendations.append(
            "Examiner conjointement la non-fréquentation et "
            "la déscolarisation afin de définir des interventions "
            "adaptées aux deux situations."
        )

    else:

        recommendations.append(
            "Maintenir le suivi des indicateurs et examiner "
            "les disparités éventuelles au niveau local."
        )

    # --------------------------------------------------------
    # B. RECOMMANDATIONS LIEES AUX ECARTS DE GENRE
    # --------------------------------------------------------

    gender_values = {
        "TBA": float(row["ECART_TBA"]),
        "TBS": float(row["ECART_TBS"]),
        "TAP": float(row["ECART_TAP"]),
    }

    largest_indicator = max(
        gender_values,
        key=lambda key: abs(gender_values[key])
    )

    largest_value = gender_values[largest_indicator]

    if largest_value < 0:

        recommendations.append(
            f"Examiner prioritairement le désavantage relatif "
            f"des filles sur le {largest_indicator} "
            f"(écart : {largest_value:.2f} points)."
        )

    elif largest_value > 0:

        recommendations.append(
            f"Examiner prioritairement le désavantage relatif "
            f"des garçons sur le {largest_indicator} "
            f"(écart : +{largest_value:.2f} points)."
        )

    else:

        recommendations.append(
            "Maintenir le suivi des trois indicateurs de genre."
        )

    # --------------------------------------------------------
    # C. PRIORITE TERRITORIALE
    # --------------------------------------------------------

    if score >= median_score:

        recommendations.append(
            "Inclure cette région parmi les territoires à examiner "
            "en priorité selon le classement comparatif."
        )

    else:

        recommendations.append(
            "Maintenir le suivi régulier : un score inférieur "
            "à la médiane ne signifie pas absence de difficultés."
        )

    # --------------------------------------------------------
    # D. DONNEES INSD OBSERVEES
    # --------------------------------------------------------

    non_attendance = float(
        row["JAMAIS_FREQUENTE_PCT"]
    )

    dropout = float(
        row["DESCOLARISE_PCT"]
    )

    recommendations.append(
        f"Utiliser les niveaux observés en 2019 comme référence "
        f"pour le diagnostic local : {non_attendance:.1f} % "
        f"de non-fréquentation et {dropout:.1f} % "
        f"de déscolarisation chez les enfants de 6 à 11 ans."
    )

    return recommendations


def render_recommendation_card(row, median_score):

    recommendations = build_recommendations(
        row,
        median_score
    )

    st.markdown(
        f"#### Orientations proposées — {row['REGION']}"
    )

    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):

        st.markdown(
            f"**{index}.** {recommendation}"
        )

    st.info(
        "Ces orientations sont des pistes à valider avec les "
        "acteurs locaux. Les données décrivent des disparités "
        "et ne démontrent pas leurs causes."
    )


# ============================================================
# 4. INDICATEURS CLES
# ============================================================

def render_kpis(regional, urban):

    high_priority = regional[
        regional["NIVEAU_DIFFICULTE_CALCULEE"]
        == "Difficulté relative élevée"
    ]

    gender_mixed = regional[
        regional["DIAGNOSTIC_GENRE"]
        == "Écarts contrastés selon l'indicateur"
    ]

    last = urban.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Régions analysées",
        f"{regional['REGION'].nunique()}"
    )

    col2.metric(
        "Difficultés territoriales élevées",
        f"{len(high_priority)} / 13"
    )

    col3.metric(
        "Écarts de genre contrastés",
        f"{len(gender_mixed)} / 13"
    )

    col4.metric(
        "Dernière année DGESS",
        str(last["DERNIERE_ANNEE"])
    )


# ============================================================
# 5. PRIORISATION TERRITORIALE
# ============================================================

def render_territorial_priorities(regional, median_score):

    st.subheader(
        "1. Où concentrer l'attention ?"
    )

    st.caption(
        "Classement fondé sur le score territorial INSD RGPH 2019 : "
        "50 % non-fréquentation et 50 % déscolarisation, "
        "après normalisation min-max."
    )

    chart = regional.sort_values(
        "SCORE_TERRITORIAL",
        ascending=True
    )

    fig = px.bar(
        chart,
        x="SCORE_TERRITORIAL",
        y="REGION",
        orientation="h",
        color="SCORE_TERRITORIAL",
        color_continuous_scale=[
            GREEN,
            ORANGE,
            RED,
        ],
        text_auto=".2f",
        labels={
            "SCORE_TERRITORIAL": "Score territorial",
            "REGION": "Région",
        },
    )

    fig.add_vline(
        x=median_score,
        line_dash="dash",
        line_color=GREY,
        annotation_text="Médiane des régions",
    )

    fig.update_layout(
        height=500,
        coloraxis_showscale=False,
        xaxis_title="Score comparatif (0–100)",
        yaxis_title="",
        margin=dict(l=10, r=20, t=40, b=20),
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    display = regional[
        [
            "RANG_PRIORITE_TERRITORIALE",
            "REGION",
            "SCORE_TERRITORIAL",
            "PROFIL_REGIONAL",
            "NIVEAU_DIFFICULTE_CALCULEE",
            "JAMAIS_FREQUENTE_PCT",
            "DESCOLARISE_PCT",
            "SCOLARISE_PCT",
        ]
    ].rename(
        columns={
            "RANG_PRIORITE_TERRITORIALE": "Rang",
            "REGION": "Région",
            "SCORE_TERRITORIAL": "Score",
            "PROFIL_REGIONAL": "Profil observé",
            "NIVEAU_DIFFICULTE_CALCULEE":
                "Comparaison à la médiane",
            "JAMAIS_FREQUENTE_PCT":
                "Jamais fréquenté (%)",
            "DESCOLARISE_PCT":
                "Déscolarisé (%)",
            "SCOLARISE_PCT":
                "Scolarisé (%)",
        }
    )

    st.markdown(
        "**Indicateurs territoriaux par région — INSD RGPH 2019**"
    )

    st.dataframe(
        display.round(2),
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 6. ANALYSE DES DISPARITES DE GENRE
# ============================================================

def render_gender_diagnostic(regional, evolution):

    st.subheader(
        "2. Où et sur quel indicateur observer les écarts de genre ?"
    )

    st.caption(
        "Convention : écart = filles moins garçons. "
        "Négatif : désavantage relatif des filles ; "
        "positif : désavantage relatif des garçons."
    )

    selected_indicator = st.selectbox(
        "Indicateur à examiner",
        options=GENDER_COLUMNS,
        format_func=lambda x: GENDER_LABELS[x],
        key="decision_gender_indicator",
    )

    chart = regional.sort_values(
        selected_indicator
    )

    fig = px.bar(
        chart,
        x=selected_indicator,
        y="REGION",
        orientation="h",
        color=selected_indicator,
        color_continuous_scale=[
            RED,
            GREY,
            BLUE,
        ],
        text_auto="+.2f",
        labels={
            selected_indicator: "Écart filles - garçons (points)",
            "REGION": "Région",
        },
    )

    fig.add_vline(
        x=0,
        line_dash="dash",
        line_color=NAVY
    )

    fig.update_layout(
        height=470,
        coloraxis_showscale=False,
        yaxis_title="",
        margin=dict(l=10, r=20, t=30, b=20),
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    counts = (
        regional["DIAGNOSTIC_GENRE"]
        .value_counts()
        .rename_axis("Diagnostic")
        .reset_index(name="Régions")
    )

    st.markdown(
        "**Synthèse des profils de genre**"
    )

    st.dataframe(
        counts,
        use_container_width=True,
        hide_index=True
    )

    with st.expander(
        "Voir l'évolution annuelle des écarts de genre"
    ):

        chart_df = evolution.melt(
            id_vars=["ANNEE_SCOLAIRE"],
            value_vars=GENDER_COLUMNS,
            var_name="Indicateur",
            value_name="Écart",
        )

        chart_df["Indicateur"] = (
            chart_df["Indicateur"].replace(
                GENDER_LABELS
            )
        )

        if "ORDRE_ANNEE" in evolution.columns:

            order = evolution[
                ["ANNEE_SCOLAIRE", "ORDRE_ANNEE"]
            ].drop_duplicates()

            chart_df = chart_df.merge(
                order,
                on="ANNEE_SCOLAIRE",
                how="left"
            ).sort_values("ORDRE_ANNEE")

        fig = px.line(
            chart_df,
            x="ANNEE_SCOLAIRE",
            y="Écart",
            color="Indicateur",
            markers=True,
        )

        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color=GREY
        )

        fig.update_layout(
            xaxis_title="Année scolaire",
            yaxis_title="Écart filles - garçons (points)",
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# 7. ANALYSE URBAIN-RURAL
# ============================================================

def render_urban_rural(urban_diagnostic, insd_gaps):

    st.subheader(
        "3. Que montrent les données urbain-rural ?"
    )

    row = urban_diagnostic.iloc[0]

    col1, col2 = st.columns(2)

    col1.metric(
        f"Variation des effectifs urbains "
        f"({row['PREMIERE_ANNEE']} à {row['DERNIERE_ANNEE']})",
        f"{float(row['VARIATION_URBAINE_PCT']):+.2f} %"
    )

    col2.metric(
        f"Variation des effectifs ruraux "
        f"({row['PREMIERE_ANNEE']} à {row['DERNIERE_ANNEE']})",
        f"{float(row['VARIATION_RURALE_PCT']):+.2f} %"
    )

    st.caption(
        "DGESS : effectifs scolaires nationaux, pas des taux d'accès. "
        "Les variations ne permettent pas, à elles seules, "
        "de comparer les probabilités d'accès à l'école."
    )

    chart_df = insd_gaps.melt(
        id_vars="STATUT_SCOLAIRE",
        value_vars=["Rural", "Urbain"],
        var_name="Milieu",
        value_name="Pourcentage",
    )

    fig = px.bar(
        chart_df,
        x="STATUT_SCOLAIRE",
        y="Pourcentage",
        color="Milieu",
        barmode="group",
        text_auto=".1f",
        color_discrete_map={
            "Rural": ORANGE,
            "Urbain": BLUE,
        },
        labels={
            "STATUT_SCOLAIRE": "Situation scolaire",
            "Pourcentage": "%",
        },
        title=(
            "Situation scolaire des enfants de 6 à 11 ans "
            "— INSD RGPH 2019"
        ),
    )

    fig.update_layout(
        xaxis_title="",
        yaxis_title="Pourcentage (%)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    gap_display = insd_gaps.rename(
        columns={
            "STATUT_SCOLAIRE": "Situation scolaire",
            "ECART_URBAIN_MOINS_RURAL":
                "Écart urbain - rural (points)",
        }
    )

    st.dataframe(
        gap_display.round(1),
        use_container_width=True,
        hide_index=True
    )

    st.info(
        "Lecture décisionnelle : les écarts observés entre milieux "
        "justifient d'approfondir les besoins et les obstacles propres "
        "aux zones rurales et urbaines. Les données disponibles ne "
        "permettent pas de calculer des taux d'accès régionaux par milieu."
    )


# ============================================================
# 8. CARTE DES PRIORITES REGIONALES
# ============================================================

def render_regional_map(regional):

    st.subheader(
        "Cartographie des priorités territoriales"
    )

    if not GEOJSON_FILE.exists():

        st.info(
            "Carte indisponible : fichier GeoJSON introuvable."
        )

        return

    try:

        with open(
            GEOJSON_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            geojson = json.load(file)

        region_keys = set(
            regional["REGION_KEY"]
        )

        # Recherche de la propriété GeoJSON
        # qui correspond le mieux aux noms des régions.

        property_matches = {}

        for feature in geojson.get("features", []):

            properties = feature.get(
                "properties",
                {}
            )

            for key, value in properties.items():

                normalized_value = normalize_region(value)

                if normalized_value in region_keys:

                    property_matches[key] = (
                        property_matches.get(key, 0) + 1
                    )

        if not property_matches:

            st.warning(
                "Les noms des régions du GeoJSON "
                "ne correspondent pas aux données."
            )

            return

        property_name = max(
            property_matches,
            key=property_matches.get
        )

        for feature in geojson.get("features", []):

            properties = feature.setdefault(
                "properties",
                {}
            )

            properties["region_normalized"] = normalize_region(
                properties.get(property_name, "")
            )

        fig = px.choropleth(
            regional,
            geojson=geojson,
            locations="REGION_KEY",
            featureidkey="properties.region_normalized",
            color="SCORE_TERRITORIAL",
            hover_name="REGION",
            hover_data={
                "SCORE_TERRITORIAL": ":.2f",
                "PROFIL_REGIONAL": True,
                "JAMAIS_FREQUENTE_PCT": ":.1f",
                "DESCOLARISE_PCT": ":.1f",
            },
            color_continuous_scale=[
                GREEN,
                ORANGE,
                RED,
            ],
            labels={
                "SCORE_TERRITORIAL": "Score territorial",
                "JAMAIS_FREQUENTE_PCT":
                    "Jamais fréquenté (%)",
                "DESCOLARISE_PCT":
                    "Déscolarisé (%)",
            },
            title=(
                "Carte des difficultés territoriales relatives "
                "— INSD RGPH 2019"
            ),
        )

        fig.update_geos(
            fitbounds="locations",
            visible=False
        )

        fig.update_layout(
            height=520,
            margin=dict(
                l=0,
                r=0,
                t=50,
                b=0
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as error:

        st.warning(
            f"La carte n'a pas pu être affichée : {error}"
        )


# ============================================================
# 9. FICHE REGIONALE ET AIDE A LA DECISION
# ============================================================

def render_region_decision(regional, median_score):

    st.subheader(
        "4. Fiche de décision par région"
    )

    selected_region = st.selectbox(
        "Choisir une région à examiner",

        options=regional.sort_values(
            "RANG_PRIORITE_TERRITORIALE"
        )["REGION"].tolist(),

        key="decision_region_selected",
    )

    row = regional[
        regional["REGION"] == selected_region
    ].iloc[0]

    # --------------------------------------------------------
    # INDICATEURS DE LA REGION
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Rang territorial",
        f"{int(row['RANG_PRIORITE_TERRITORIALE'])} / 13"
    )

    col2.metric(
        "Score territorial",
        f"{float(row['SCORE_TERRITORIAL']):.2f} / 100"
    )

    col3.metric(
        "Profil régional",
        str(row["PROFIL_REGIONAL"])
    )

    st.divider()

    # --------------------------------------------------------
    # SITUATION SCOLAIRE INSD
    # --------------------------------------------------------

    st.markdown(
        "#### Situation scolaire — INSD RGPH 2019"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Jamais fréquenté",
        f"{float(row['JAMAIS_FREQUENTE_PCT']):.1f} %"
    )

    col2.metric(
        "Déscolarisé",
        f"{float(row['DESCOLARISE_PCT']):.1f} %"
    )

    col3.metric(
        "Scolarisé",
        f"{float(row['SCOLARISE_PCT']):.1f} %"
    )

    st.caption(
        "Enfants de 6 à 11 ans — photographie statistique RGPH 2019."
    )

    st.divider()

    # --------------------------------------------------------
    # DIAGNOSTIC TERRITORIAL ET GENRE
    # --------------------------------------------------------

    st.markdown(
        f"**Diagnostic territorial :** "
        f"{row['NIVEAU_DIFFICULTE_CALCULEE']}"
    )

    st.markdown(
        f"**Diagnostic de genre :** "
        f"{row['DIAGNOSTIC_GENRE']}"
    )

    # --------------------------------------------------------
    # TABLEAU DES ECARTS DE GENRE
    # --------------------------------------------------------

    st.markdown(
        "#### Écarts filles - garçons"
    )

    gender_table = pd.DataFrame({

        "Indicateur": [
            "TBA",
            "TBS",
            "TAP",
        ],

        "Écart (points)": [
            row["ECART_TBA"],
            row["ECART_TBS"],
            row["ECART_TAP"],
        ],

        "Lecture": [
            gender_direction(float(row["ECART_TBA"])),
            gender_direction(float(row["ECART_TBS"])),
            gender_direction(float(row["ECART_TAP"])),
        ],
    })

    st.dataframe(
        gender_table.round(2),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # --------------------------------------------------------
    # DIAGNOSTIC COMBINE
    # --------------------------------------------------------

    st.markdown(
        "#### Synthèse du diagnostic"
    )

    st.write(
        row["DIAGNOSTIC_COMBINE"]
    )

    # --------------------------------------------------------
    # RECOMMANDATIONS
    # --------------------------------------------------------

    render_recommendation_card(
        row,
        median_score
    )


# ============================================================
# 10. EXPORTATION DES RESULTATS
# ============================================================

def render_download(regional):

    st.subheader(
        "5. Télécharger les résultats"
    )

    export_columns = [
        "RANG_PRIORITE_TERRITORIALE",
        "REGION",
        "SCORE_TERRITORIAL",
        "PROFIL_REGIONAL",
        "JAMAIS_FREQUENTE_PCT",
        "DESCOLARISE_PCT",
        "SCOLARISE_PCT",
        "ECART_TBA",
        "ECART_TBS",
        "ECART_TAP",
        "DIAGNOSTIC_GENRE",
        "NIVEAU_DIFFICULTE_CALCULEE",
        "DIAGNOSTIC_COMBINE",
    ]

    export_data = regional[
        export_columns
    ].copy()

    csv = export_data.to_csv(
        index=False,
        sep=";",
        encoding="utf-8-sig"
    )

    st.download_button(
        "Télécharger le diagnostic des 13 régions (CSV)",
        data=csv,
        file_name="diagnostic_aide_decision_eduequity_bf.csv",
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# 11. METHODOLOGIE ET LIMITES
# ============================================================

def render_methodology():

    with st.expander(
        "Méthodologie, interprétation et limites"
    ):

        st.markdown(
            """
            **1. Priorisation territoriale — INSD RGPH 2019**

            Le score territorial repose sur deux indicateurs normalisés :
            50 % pour la proportion d'enfants n'ayant jamais fréquenté
            l'école et 50 % pour la proportion d'enfants déscolarisés.

            Un score élevé indique une difficulté relative plus importante
            parmi les 13 régions étudiées. La médiane est un seuil
            comparatif interne et non un seuil officiel.

            **2. Disparités de genre — DGESS**

            Les écarts sont calculés selon la convention :

            Écart = valeur des filles - valeur des garçons.

            Une valeur négative indique un désavantage relatif des filles.
            Une valeur positive indique un désavantage relatif des garçons.

            Les indicateurs TBA, TBS et TAP doivent être interprétés
            séparément, car leurs directions peuvent différer.

            **3. Disparités urbain-rural**

            Les données DGESS représentent des effectifs scolaires
            nationaux et non des taux d'accès.

            Les données INSD décrivent la situation scolaire des enfants
            de 6 à 11 ans au RGPH 2019.

            Ces deux sources ne constituent pas une même série temporelle.

            **4. Comparaison régionale**

            Les données régionales INSD représentent une photographie
            de 2019. Elles ne constituent pas une évolution annuelle
            ni un croisement régional complet entre sexe et milieu.

            **5. Aide à la décision**

            Les recommandations sont des pistes d'investigation et
            d'action à discuter avec les acteurs éducatifs.

            Les données décrivent des disparités statistiques et ne
            démontrent pas directement leurs causes.

            Les scores et diagnostics ne remplacent pas une validation
            de terrain ni une analyse des ressources disponibles.
            """
        )


# ============================================================
# 12. FONCTION PRINCIPALE
# ============================================================

def render():

    st.title(
        "Diagnostic et aide à la décision"
    )

    st.write(
        """
        Ce module transforme les analyses d'EduEquity BF en informations
        utiles pour identifier les territoires à examiner, comprendre
        les écarts de genre et orienter les investigations et les interventions.
        """
    )

    st.caption(
        "Défi 2 — Analyse des disparités d'accès à l'éducation | Burkina Faso"
    )

    st.divider()

    # --------------------------------------------------------
    # CHARGEMENT DES DONNEES
    # --------------------------------------------------------

    try:

        data = load_decision_data()

    except Exception as error:

        st.error(
            f"Impossible de charger les résultats du diagnostic : {error}"
        )

        st.info(
            "Vérifie que les scripts de diagnostic ont été exécutés "
            "et que les fichiers CSV attendus sont présents dans "
            "les dossiers de données."
        )

        st.exception(error)

        return

    regional = data["regional"]

    urban = data["urban_diagnostic"]

    median_score = data["median_score"]

    # --------------------------------------------------------
    # VUE GENERALE
    # --------------------------------------------------------

    st.header(
        "Vue d'ensemble décisionnelle"
    )

    render_kpis(
        regional,
        urban
    )

    st.caption(
        f"Médiane comparative des scores territoriaux : "
        f"{median_score:.2f} / 100."
    )

    st.divider()

    # --------------------------------------------------------
    # PARTIE I : PRIORISATION TERRITORIALE
    # --------------------------------------------------------

    st.header(
        "Partie I — Priorisation territoriale"
    )

    render_territorial_priorities(
        regional,
        median_score
    )

    with st.expander(
        "Voir la carte des priorités régionales"
    ):

        render_regional_map(
            regional
        )

    st.divider()

    # --------------------------------------------------------
    # PARTIE II : GENRE
    # --------------------------------------------------------

    st.header(
        "Partie II — Disparités de genre"
    )

    render_gender_diagnostic(
        regional,
        data["gender_evolution"]
    )

    st.divider()

    # --------------------------------------------------------
    # PARTIE III : URBAIN-RURAL
    # --------------------------------------------------------

    st.header(
        "Partie III — Disparités urbain-rural"
    )

    render_urban_rural(
        urban,
        data["insd_gaps"]
    )

    st.divider()

    # --------------------------------------------------------
    # PARTIE IV : AIDE A LA DECISION
    # --------------------------------------------------------

    st.header(
        "Partie IV — Décision et recommandations"
    )

    render_region_decision(
        regional,
        median_score
    )

    st.divider()

    # --------------------------------------------------------
    # EXPORTATION ET METHODOLOGIE
    # --------------------------------------------------------

    render_download(
        regional
    )

    render_methodology()

    st.caption(
        "EduEquity BF | Outil d'aide à la décision — Défi 2"
    )
