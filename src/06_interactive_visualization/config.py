
from pathlib import Path

# ============================================================
# 1. CHEMINS DU PROJET
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
ANALYSES_DIR = OUTPUTS_DIR / "analyses"

# Analyses existantes
EXPLORATORY_DIR = ANALYSES_DIR / "01_analyse_exploratoire"
GENDER_DIR = ANALYSES_DIR / "02_analyse_disparites_genre"
REGIONAL_DIR = ANALYSES_DIR / "03_analyse_disparites_regionales"
URBAN_RURAL_DIR = ANALYSES_DIR / "04_analyse_urbain_rural"
PRIORITIZATION_DIR = ANALYSES_DIR / "06_priorisation_et_recommandations"

# Ressources du module interactif
MODULE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = MODULE_DIR / "assets"
CSS_FILE = ASSETS_DIR / "style.css"
GEOJSON_FILE = ASSETS_DIR / "geojson" / "burkina_faso_regions.geojson"


# ============================================================
# 2. IDENTITÉ DE L'APPLICATION
# ============================================================

APP_TITLE = "EduEquity BF"

APP_SUBTITLE = (
    "Education Intelligence & Equity Analytics"
)

APP_DESCRIPTION = (
    "Plateforme interactive d'analyse des disparités "
    "éducatives au Burkina Faso."
)

PAGE_ICON = "🎓"
LAYOUT = "wide"


# ============================================================
# 3. RÉGIONS DU BURKINA FASO
# ============================================================

REGIONS = [
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
    "SUD-OUEST",
]


# ============================================================
# 4. INDICATEURS SCOLAIRES
# ============================================================

INDICATORS = {
    "TBA": "Taux Brut d'Admission",
    "TBS": "Taux Brut de Scolarisation",
    "TAP": "Taux d'Achèvement du Primaire",
}

GENDER_LABELS = {
    "FILLES": "Filles",
    "GARCONS": "Garçons",
}

START_YEAR = 2015
END_YEAR = 2025


# ============================================================
# 5. PRIORISATION TERRITORIALE
# ============================================================

PRIORITY_LEVELS = {
    "ÉLEVÉE": {
        "minimum": 60,
        "maximum": 100,
        "color": "#DC5353",
    },
    "MOYENNE": {
        "minimum": 40,
        "maximum": 60,
        "color": "#E9A23B",
    },
    "FAIBLE": {
        "minimum": 0,
        "maximum": 40,
        "color": "#36A887",
    },
}


# ============================================================
# 6. IDENTITÉ VISUELLE
# ============================================================

COLORS = {
    "primary": "#142B4A",
    "secondary": "#087E8B",
    "accent": "#E5AE48",
    "background": "#F4F7FB",
    "surface": "#FFFFFF",
    "text": "#243447",
    "muted": "#738196",
    "girls": "#D66B91",
    "boys": "#3986C8",
    "success": "#36A887",
    "warning": "#E9A23B",
    "danger": "#DC5353",
}


# ============================================================
# 7. NAVIGATION
# ============================================================

PAGES = {
    "Vue nationale": "01_vue_nationale",
    "Équité territoriale": "02_equite_territoriale",
    "Disparités de genre": "03_disparites_genre",
    "Analyse urbain-rural": "04_analyse_urbain_rural",
    "Diagnostic et aide à la décision": "05_priorisation_recommandations",
}

URBAN_RURAL_ANALYSIS_DIR = (
    ANALYSES_DIR / "04_analyse_urbain_rural"
)