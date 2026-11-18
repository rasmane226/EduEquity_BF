
import streamlit as st
from textwrap import dedent
from html import escape

from config import (
    APP_TITLE,
    APP_DESCRIPTION,
    PAGE_ICON,
    LAYOUT,
    PAGES,
    CSS_FILE,
)

from data_loader import load_all_data

from views import equite_territoriale
from views import disparites_genre
from views import analyse_urbain_rural
from views import diagnostics_aide_a_la_decision


# ============================================================
# 1. CONFIGURATION DE L'APPLICATION
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded",
)


# ============================================================
# 2. CHARGEMENT DU CSS
# ============================================================

def load_css():

    if not CSS_FILE.exists():

        st.warning("Le fichier CSS est introuvable.")
        return

    with open(CSS_FILE, "r", encoding="utf-8") as file:

        css = file.read()

    st.markdown(
        f"<style>\n{css}\n</style>",
        unsafe_allow_html=True,
    )


load_css()


# ============================================================
# 3. CHARGEMENT DES DONNEES
# ============================================================

@st.cache_data
def get_application_data():

    return load_all_data()


try:

    data = get_application_data()

except Exception as error:

    st.error(
        f"Erreur lors du chargement des données : {error}"
    )

    st.stop()


# Vérification des données nécessaires

required_keys = [
    "national",
    "regional",
]

for key in required_keys:

    if key not in data:

        st.error(
            f"Les données nécessaires sont absentes : {key}"
        )

        st.stop()


# ============================================================
# 4. FONCTION DE NAVIGATION
# ============================================================

def navigate_to(page):

    st.session_state["main_navigation"] = page


# ============================================================
# 5. ICONES SVG DES CARTES KPI
# ============================================================

ICON_GLOBE = """
<svg viewBox="0 0 24 24" aria-hidden="true">
    <circle cx="12" cy="12" r="10"></circle>
    <path d="M2 12h20"></path>
    <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10"></path>
    <path d="M12 2a15.3 15.3 0 0 0-4 10 15.3 15.3 0 0 0 4 10"></path>
</svg>
"""

ICON_CALENDAR = """
<svg viewBox="0 0 24 24" aria-hidden="true">
    <rect x="3" y="4" width="18" height="17" rx="2"></rect>
    <path d="M16 2v4"></path>
    <path d="M8 2v4"></path>
    <path d="M3 10h18"></path>
    <path d="M8 14h.01"></path>
    <path d="M12 14h.01"></path>
    <path d="M16 14h.01"></path>
    <path d="M8 17h.01"></path>
    <path d="M12 17h.01"></path>
</svg>
"""

ICON_DATABASE = """
<svg viewBox="0 0 24 24" aria-hidden="true">
    <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
    <path d="M3 5v14c0 1.7 4 3 9 3s9-1.3 9-3V5"></path>
    <path d="M3 12c0 1.7 4 3 9 3s9-1.3 9-3"></path>
</svg>
"""

ICON_CHART = """
<svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M3 3v18h18"></path>
    <path d="m7 14 4-4 4 3 6-8"></path>
    <path d="M17 5h4v4"></path>
    <path d="M7 18v-2"></path>
    <path d="M11 18v-5"></path>
    <path d="M15 18v-3"></path>
</svg>
"""


# ============================================================
# 6. FONCTION DE CREATION DES CARTES KPI
# ============================================================

def render_kpi_card(
    icon,
    badge,
    title,
    value,
    description,
    color
):

    # Construction du HTML de la carte

    card_html = f"""
    <div class="kpi-card {color}">

        <div class="kpi-top">

            <div class="kpi-icon">
                {icon}
            </div>

            <div class="kpi-badge">
                {escape(str(badge))}
            </div>

        </div>

        <div class="kpi-content">

            <div class="kpi-title">
                {escape(str(title))}
            </div>

            <div class="kpi-value">
                {escape(str(value))}
            </div>

            <div class="kpi-description">
                {escape(str(description))}
            </div>

        </div>

    </div>
    """

    # IMPORTANT : affichage HTML natif
    st.html(card_html)


# ============================================================
# 7. BARRE LATERALE — NAVIGATION
# ============================================================

PAGE_ICONS = {

    "Vue nationale":
        ":material/dashboard:",

    "Équité territoriale":
        ":material/public:",

    "Disparités de genre":
        ":material/groups:",

    "Analyse urbain-rural":
        ":material/location_city:",

    "Diagnostic et aide à la décision":
        ":material/analytics:",
}


with st.sidebar:

    # --------------------------------------------------------
    # IDENTITE VISUELLE
    # --------------------------------------------------------

    st.html("""
        <div class="sidebar-brand">

            <div class="brand-icon">E</div>

            <div>
                <h2>EduEquity BF</h2>

                <p>EDUCATION INTELLIGENCE</p>

                <p>&amp; EQUITY ANALYTICS</p>
            </div>

        </div>
    """)

    st.html("""
        <div class="sidebar-separator"></div>
    """)

    # --------------------------------------------------------
    # TITRE NAVIGATION
    # --------------------------------------------------------

    st.html("""
        <div class="sidebar-section-title">
            <span class="section-icon">▣</span>
            NAVIGATION
        </div>
    """)

    # --------------------------------------------------------
    # MENU DE NAVIGATION
    # --------------------------------------------------------

    selected_page = st.radio(
        "Navigation",

        options=list(PAGES.keys()),

        format_func=lambda page: (
            f"{PAGE_ICONS.get(page, '')}  {page}"
        ),

        label_visibility="collapsed",

        key="main_navigation",
    )

    st.html("""
        <div class="sidebar-separator"></div>
    """)

    # --------------------------------------------------------
    # SECTION A PROPOS
    # --------------------------------------------------------

    st.html("""
        <div class="sidebar-section-title">
            <span class="section-icon">ⓘ</span>
            À PROPOS
        </div>
    """)

    st.html(f"""
        <div class="sidebar-about">
            {escape(APP_DESCRIPTION)}
        </div>
    """)

    # --------------------------------------------------------
    # PIED DE LA BARRE LATERALE
    # --------------------------------------------------------

    st.html("""
        <div class="sidebar-footer">
            <span>Burkina Faso</span>
            <span class="footer-dot">•</span>
            <span>2026</span>
        </div>
    """)


# ============================================================
# 8. HERO SECTION — BANDEAU PRINCIPAL
# ============================================================

hero_html = dedent("""
    <div class="hero-container">

        <div class="hero-label">
            BURKINA FASO · EDUCATION DATA INTELLIGENCE
        </div>

        <h1>EduEquity BF</h1>

        <h3>Education Intelligence &amp; Equity Analytics</h3>

        <p>
            Analyse interactive des disparités éducatives
            pour soutenir la prise de décision au Burkina Faso.
        </p>

    </div>
""")

st.html(hero_html)


# ============================================================
# 9. VUE NATIONALE
# ============================================================

if selected_page == "Vue nationale":

    st.title("Vue nationale")

    st.write(
        "Explorez les principaux indicateurs de "
        "l'enseignement primaire au Burkina Faso."
    )

    national_data = data["national"]

    # --------------------------------------------------------
    # STATISTIQUES GENERALES
    # --------------------------------------------------------

    number_regions = 13

    number_years = (
        national_data["ANNEE_SCOLAIRE"].nunique()
    )

    number_observations = len(national_data)

    number_indicators = 3

    # --------------------------------------------------------
    # CARTES KPI PERSONNALISEES
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(
        4,
        gap="medium"
    )

    with col1:

        render_kpi_card(
            icon=ICON_GLOBE,
            badge="Territoire",
            title="Régions analysées",
            value=number_regions,
            description="Couverture nationale",
            color="kpi-blue",
        )

    with col2:

        render_kpi_card(
            icon=ICON_CALENDAR,
            badge="Temps",
            title="Années scolaires",
            value=number_years,
            description="2015–2016 à 2024–2025",
            color="kpi-green",
        )

    with col3:

        render_kpi_card(
            icon=ICON_DATABASE,
            badge="Données",
            title="Observations nationales",
            value=number_observations,
            description="Enregistrements analysés",
            color="kpi-orange",
        )

    with col4:

        render_kpi_card(
            icon=ICON_CHART,
            badge="Analyse",
            title="Indicateurs scolaires",
            value=number_indicators,
            description="TBA · TBS · TAP",
            color="kpi-purple",
        )

    st.divider()

    # --------------------------------------------------------
    # EXPLORATION DES MODULES
    # --------------------------------------------------------

    st.subheader("Explorer les analyses")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Équité territoriale")

        st.write(
            "Explorez les disparités éducatives "
            "entre les 13 régions du Burkina Faso."
        )

        st.button(
            "Explorer les régions",
            use_container_width=True,
            on_click=navigate_to,
            args=("Équité territoriale",),
        )

    with col2:

        st.markdown("### Disparités de genre")

        st.write(
            "Analysez les différences entre filles "
            "et garçons dans le système éducatif."
        )

        st.button(
            "Explorer les disparités de genre",
            use_container_width=True,
            on_click=navigate_to,
            args=("Disparités de genre",),
        )

    # --------------------------------------------------------
    # ANALYSE URBAIN-RURAL
    # --------------------------------------------------------

    st.divider()

    st.markdown("### Analyse urbain-rural")

    st.write(
        "Comparez la situation scolaire entre les milieux "
        "urbain et rural à partir des données DGESS et INSD."
    )

    st.button(
        "Explorer l'analyse urbain-rural",
        use_container_width=True,
        on_click=navigate_to,
        args=("Analyse urbain-rural",),
    )


# ============================================================
# 10. EQUITE TERRITORIALE
# ============================================================

elif selected_page == "Équité territoriale":

    try:

        regional_data = data.get("regional")

        if regional_data is None:

            st.error(
                "Les données régionales ne sont pas disponibles."
            )

        else:

            equite_territoriale.render(regional_data)

    except Exception as error:

        st.error(
            f"Erreur dans le module d'équité territoriale : {error}"
        )

        st.exception(error)


# ============================================================
# 11. DISPARITES DE GENRE
# ============================================================

elif selected_page == "Disparités de genre":

    try:

        gender_data = data.get("gender")

        if gender_data is None:

            st.error(
                "Les données sur les disparités de genre "
                "ne sont pas disponibles."
            )

        else:

            disparites_genre.render(gender_data)

    except Exception as error:

        st.error(
            f"Erreur dans le module de disparités de genre : {error}"
        )

        st.exception(error)


# ============================================================
# 12. ANALYSE URBAIN-RURAL
# ============================================================

elif selected_page == "Analyse urbain-rural":

    try:

        analyse_urbain_rural.render()

    except Exception as error:

        st.error(
            f"Erreur dans le module d'analyse urbain-rural : {error}"
        )

        st.exception(error)


# ============================================================
# 13. DIAGNOSTIC ET AIDE A LA DECISION
# ============================================================

elif selected_page == "Diagnostic et aide à la décision":

    try:

        diagnostics_aide_a_la_decision.render()

    except Exception as error:

        st.error(
            f"Erreur dans le module d'aide à la décision : {error}"
        )

        st.exception(error)


# ============================================================
# 14. PIED DE PAGE
# ============================================================

st.divider()

footer_html = dedent("""
    <div class="footer-container">

        <p>
            EduEquity BF |
            Education Intelligence &amp; Equity Analytics
        </p>

        <p>
            Burkina Faso · 2026
        </p>

    </div>
""")

st.html(footer_html)
