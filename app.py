from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

from vero.intelligence.profile_engine import build_company_profile
from vero.intelligence.vero_score_engine import analyze_vero_score

try:
    from vero.research.agent import ResearchError, research_company, research_to_description
    AI_RESEARCH_AVAILABLE = True
except Exception:
    AI_RESEARCH_AVAILABLE = False
    ResearchError = RuntimeError


BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "Outputs"

st.set_page_config(
    page_title="VERO | Startup Intelligence",
    page_icon="V",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Make Streamlit Cloud secrets available to the research agent.
try:
    if "OPENAI_API_KEY" in st.secrets:
        os.environ["OPENAI_API_KEY"] = str(st.secrets["OPENAI_API_KEY"])
    if "VERO_AI_MODEL" in st.secrets:
        os.environ["VERO_AI_MODEL"] = str(st.secrets["VERO_AI_MODEL"])
except Exception:
    pass

THEMES = {
    "Executive": {
        "primary": "#3155D9",
        "secondary": "#D8A928",
        "background": "#F5F7FC",
        "surface": "#FFFFFF",
        "surface_alt": "#EEF2FF",
        "text": "#121A2F",
        "muted": "#667085",
        "border": "#DFE4EF",
        "positive": "#16A36A",
        "warning": "#D98E04",
        "danger": "#D64545",
        "sidebar": "#11182B",
        "sidebar_text": "#F8FAFC",
    },
    "Evergreen": {
        "primary": "#167A5B",
        "secondary": "#C6A15B",
        "background": "#F4F7F2",
        "surface": "#FFFFFF",
        "surface_alt": "#E9F4EE",
        "text": "#16312A",
        "muted": "#66746F",
        "border": "#D8E2DA",
        "positive": "#12805C",
        "warning": "#C08A24",
        "danger": "#C95151",
        "sidebar": "#102E26",
        "sidebar_text": "#F4FBF8",
    },
    "Capital": {
        "primary": "#0F9B6C",
        "secondary": "#0A4D3B",
        "background": "#F2F8F5",
        "surface": "#FFFFFF",
        "surface_alt": "#E4F4EC",
        "text": "#102A22",
        "muted": "#63716B",
        "border": "#D6E5DD",
        "positive": "#0F9B6C",
        "warning": "#C88719",
        "danger": "#CF4D4D",
        "sidebar": "#092A21",
        "sidebar_text": "#F0FFF9",
    },
    "Midnight": {
        "primary": "#65B8FF",
        "secondary": "#A6E0FF",
        "background": "#09111F",
        "surface": "#111C2E",
        "surface_alt": "#15243A",
        "text": "#F5F8FC",
        "muted": "#9AAAC0",
        "border": "#26364E",
        "positive": "#42D39B",
        "warning": "#F2B84B",
        "danger": "#FF7272",
        "sidebar": "#060C16",
        "sidebar_text": "#F5F8FC",
    },
    "Minimal": {
        "primary": "#161616",
        "secondary": "#707070",
        "background": "#F6F6F6",
        "surface": "#FFFFFF",
        "surface_alt": "#EEEEEE",
        "text": "#111111",
        "muted": "#6E6E6E",
        "border": "#DDDDDD",
        "positive": "#1D7A4C",
        "warning": "#A96F0A",
        "danger": "#B94242",
        "sidebar": "#111111",
        "sidebar_text": "#FFFFFF",
    },
    "Quantum": {
        "primary": "#2E9BFF",
        "secondary": "#8B5CF6",
        "background": "#080A10",
        "surface": "#11141D",
        "surface_alt": "#181C28",
        "text": "#F7F8FC",
        "muted": "#A0A7B8",
        "border": "#292E3D",
        "positive": "#36D399",
        "warning": "#F7B955",
        "danger": "#FF6B77",
        "sidebar": "#05060A",
        "sidebar_text": "#F7F8FC",
    },
    "Ivy": {
        "primary": "#7A2233",
        "secondary": "#C5A35A",
        "background": "#F7F3EC",
        "surface": "#FFFDFC",
        "surface_alt": "#F0E6E2",
        "text": "#2D1720",
        "muted": "#75666B",
        "border": "#E4D8D5",
        "positive": "#2E7B57",
        "warning": "#B17A17",
        "danger": "#B8454E",
        "sidebar": "#35121B",
        "sidebar_text": "#FFF9F7",
    },
    "Ocean": {
        "primary": "#0077B6",
        "secondary": "#48CAE4",
        "background": "#F1FAFF",
        "surface": "#FFFFFF",
        "surface_alt": "#DFF4FC",
        "text": "#08263A",
        "muted": "#607D8B",
        "border": "#CBE7F2",
        "positive": "#129970",
        "warning": "#D9911B",
        "danger": "#D84D4D",
        "sidebar": "#06283D",
        "sidebar_text": "#F4FBFF",
    },
    "Sunset": {
        "primary": "#F26B38",
        "secondary": "#F6B73C",
        "background": "#FFF7F1",
        "surface": "#FFFFFF",
        "surface_alt": "#FFE8D8",
        "text": "#352018",
        "muted": "#806A61",
        "border": "#F1D8C8",
        "positive": "#2A9D6F",
        "warning": "#E39A18",
        "danger": "#D94A4A",
        "sidebar": "#3A1F18",
        "sidebar_text": "#FFF8F4",
    },
    "Lavender": {
        "primary": "#7C5CE7",
        "secondary": "#C084FC",
        "background": "#F7F4FF",
        "surface": "#FFFFFF",
        "surface_alt": "#EFE9FF",
        "text": "#251C3D",
        "muted": "#756B8C",
        "border": "#DFD6F5",
        "positive": "#2F9E72",
        "warning": "#C78A17",
        "danger": "#D45267",
        "sidebar": "#261A46",
        "sidebar_text": "#FBF8FF",
    },
    "Rose": {
        "primary": "#D9467B",
        "secondary": "#F59AB7",
        "background": "#FFF5F8",
        "surface": "#FFFFFF",
        "surface_alt": "#FFE5EE",
        "text": "#351A25",
        "muted": "#846B74",
        "border": "#F0D1DC",
        "positive": "#21926A",
        "warning": "#C68A1A",
        "danger": "#C93D52",
        "sidebar": "#3A1422",
        "sidebar_text": "#FFF8FB",
    },
    "Copper": {
        "primary": "#B7652A",
        "secondary": "#D99A5D",
        "background": "#FAF5EF",
        "surface": "#FFFDFC",
        "surface_alt": "#F1E4D5",
        "text": "#2E2118",
        "muted": "#77695E",
        "border": "#E5D7C7",
        "positive": "#2D8661",
        "warning": "#B98221",
        "danger": "#C84D48",
        "sidebar": "#2E1B12",
        "sidebar_text": "#FFF9F3",
    },
    "Arctic": {
        "primary": "#2C7BE5",
        "secondary": "#8ED7F7",
        "background": "#F6FBFF",
        "surface": "#FFFFFF",
        "surface_alt": "#EAF5FC",
        "text": "#12263A",
        "muted": "#6E8091",
        "border": "#D7E8F3",
        "positive": "#1F9A72",
        "warning": "#C98C1C",
        "danger": "#D64B57",
        "sidebar": "#0B2035",
        "sidebar_text": "#F4FAFF",
    },
    "Solar": {
        "primary": "#E6A700",
        "secondary": "#FFCC33",
        "background": "#FFFBEF",
        "surface": "#FFFFFF",
        "surface_alt": "#FFF3C7",
        "text": "#2B2411",
        "muted": "#786F55",
        "border": "#E9DCA7",
        "positive": "#24845F",
        "warning": "#D38A00",
        "danger": "#D24C42",
        "sidebar": "#2D250E",
        "sidebar_text": "#FFFDF5",
    },
    "Crimson": {
        "primary": "#C62828",
        "secondary": "#EF5350",
        "background": "#FFF5F5",
        "surface": "#FFFFFF",
        "surface_alt": "#FDE6E6",
        "text": "#321A1A",
        "muted": "#816A6A",
        "border": "#EED0D0",
        "positive": "#24845F",
        "warning": "#C58B1A",
        "danger": "#B71C1C",
        "sidebar": "#330F12",
        "sidebar_text": "#FFF8F8",
    },
    "Teal": {
        "primary": "#0F8B8D",
        "secondary": "#49C5B6",
        "background": "#F1FAF9",
        "surface": "#FFFFFF",
        "surface_alt": "#DFF3F1",
        "text": "#123332",
        "muted": "#647B79",
        "border": "#CDE6E3",
        "positive": "#1D956B",
        "warning": "#C58A1C",
        "danger": "#D34B55",
        "sidebar": "#0A3435",
        "sidebar_text": "#F3FFFD",
    },
    "Sakura": {
        "primary": "#E76F9A",
        "secondary": "#F6B8CE",
        "background": "#FFF8FB",
        "surface": "#FFFFFF",
        "surface_alt": "#FDEAF1",
        "text": "#35202A",
        "muted": "#836E77",
        "border": "#EFD7E0",
        "positive": "#2A8D68",
        "warning": "#C58A1C",
        "danger": "#C84763",
        "sidebar": "#43202E",
        "sidebar_text": "#FFF9FC",
    },
    "Obsidian Gold": {
        "primary": "#E0B84F",
        "secondary": "#F2D781",
        "background": "#0D0D0E",
        "surface": "#171719",
        "surface_alt": "#222225",
        "text": "#FAF8F1",
        "muted": "#B8B3A5",
        "border": "#343438",
        "positive": "#45C58A",
        "warning": "#E0B84F",
        "danger": "#FF7373",
        "sidebar": "#080809",
        "sidebar_text": "#FFF9E8",
    },
    "Cyber Lime": {
        "primary": "#B7F34A",
        "secondary": "#43E6C2",
        "background": "#090D0A",
        "surface": "#131915",
        "surface_alt": "#1A231D",
        "text": "#F4FFE8",
        "muted": "#AAB8A3",
        "border": "#2D3A31",
        "positive": "#62E6A7",
        "warning": "#F0C95A",
        "danger": "#FF6B7A",
        "sidebar": "#050805",
        "sidebar_text": "#F6FFE9",
    },

}

if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Executive"
if "page" not in st.session_state:
    st.session_state.page = "Overview"
if "terms_accepted" not in st.session_state:
    st.session_state.terms_accepted = False

# Apply navigation requests before the sidebar radio widget is created.
# Streamlit does not allow changing st.session_state.page after the widget
# with key="page" has already been instantiated during the same run.
pending_page = st.session_state.pop("pending_page", None)
if pending_page:
    st.session_state.page = pending_page


def navigate_to(page_name: str) -> None:
    st.session_state["pending_page"] = page_name
    st.rerun()


def inject_css(theme: dict[str, str]) -> None:
    st.markdown(
        f"""
        <style>
        :root {{
            --vero-primary: {theme['primary']};
            --vero-secondary: {theme['secondary']};
            --vero-bg: {theme['background']};
            --vero-surface: {theme['surface']};
            --vero-surface-alt: {theme['surface_alt']};
            --vero-text: {theme['text']};
            --vero-muted: {theme['muted']};
            --vero-border: {theme['border']};
            --vero-positive: {theme['positive']};
            --vero-warning: {theme['warning']};
            --vero-danger: {theme['danger']};
        }}

        .stApp {{
            background: var(--vero-bg);
            color: var(--vero-text);
        }}

        [data-testid="stSidebar"] {{
            background: {theme['sidebar']};
            border-right: 1px solid {theme['border']};
        }}

        [data-testid="stSidebar"] * {{
            color: {theme['sidebar_text']};
        }}

        [data-testid="stSidebar"] .stRadio label {{
            border-radius: 10px;
            padding: 0.35rem 0.5rem;
        }}

        .block-container {{
            max-width: 1440px;
            padding-top: 1.7rem;
            padding-bottom: 3rem;
        }}

        h1, h2, h3, h4, h5, h6, p, label {{
            color: var(--vero-text);
        }}

        .vero-brand {{
            font-size: 1.8rem;
            font-weight: 850;
            letter-spacing: 0.18em;
            color: {theme['sidebar_text']};
            margin: 0.35rem 0 0;
        }}

        .vero-brand-sub {{
            color: {theme['sidebar_text']};
            opacity: 0.68;
            font-size: 0.82rem;
            margin-bottom: 1.25rem;
        }}

        .vero-eyebrow {{
            color: var(--vero-primary);
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.76rem;
            font-weight: 800;
            margin-bottom: 0.45rem;
        }}

        .vero-page-title {{
            font-size: clamp(2rem, 4vw, 3.35rem);
            line-height: 1.04;
            font-weight: 850;
            letter-spacing: -0.045em;
            margin: 0;
            color: var(--vero-text);
        }}

        .vero-page-copy {{
            color: var(--vero-muted);
            font-size: 1.04rem;
            max-width: 760px;
            margin-top: 0.65rem;
            margin-bottom: 1.8rem;
        }}

        .vero-card {{
            background: var(--vero-surface);
            border: 1px solid var(--vero-border);
            border-radius: 18px;
            padding: 1.15rem 1.2rem;
            box-shadow: 0 10px 28px rgba(16, 24, 40, 0.06);
            height: 100%;
        }}

        .vero-card:hover {{
            transform: translateY(-2px);
            transition: transform 150ms ease, box-shadow 150ms ease;
            box-shadow: 0 14px 34px rgba(16, 24, 40, 0.10);
        }}

        .vero-kpi-label {{
            font-size: 0.80rem;
            color: var(--vero-muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 760;
        }}

        .vero-kpi-value {{
            font-size: 2rem;
            font-weight: 850;
            letter-spacing: -0.04em;
            color: var(--vero-text);
            margin: 0.24rem 0 0.18rem;
        }}

        .vero-kpi-sub {{
            color: var(--vero-muted);
            font-size: 0.86rem;
        }}

        .vero-badge {{
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.32rem 0.65rem;
            background: var(--vero-surface-alt);
            color: var(--vero-primary);
            border: 1px solid var(--vero-border);
            font-size: 0.78rem;
            font-weight: 750;
        }}

        .vero-section-title {{
            font-size: 1.28rem;
            font-weight: 820;
            letter-spacing: -0.02em;
            margin: 1.8rem 0 0.2rem;
        }}

        .vero-section-copy {{
            color: var(--vero-muted);
            margin: 0 0 0.9rem;
        }}

        .vero-score-ring {{
            width: 164px;
            height: 164px;
            border-radius: 50%;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            background: conic-gradient(var(--vero-primary) calc(var(--score) * 1%), var(--vero-border) 0);
            position: relative;
        }}

        .vero-score-ring::before {{
            content: "";
            position: absolute;
            width: 126px;
            height: 126px;
            border-radius: 50%;
            background: var(--vero-surface);
        }}

        .vero-score-inner {{
            z-index: 1;
            text-align: center;
        }}

        .vero-score-number {{
            font-size: 2.35rem;
            font-weight: 900;
            line-height: 1;
        }}

        .vero-score-label {{
            color: var(--vero-muted);
            font-size: 0.78rem;
            margin-top: 0.25rem;
        }}

        .vero-progress-wrap {{
            margin-bottom: 0.95rem;
        }}

        .vero-progress-head {{
            display: flex;
            justify-content: space-between;
            font-size: 0.87rem;
            margin-bottom: 0.35rem;
        }}

        .vero-progress-track {{
            height: 9px;
            border-radius: 999px;
            overflow: hidden;
            background: var(--vero-border);
        }}

        .vero-progress-fill {{
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, var(--vero-primary), var(--vero-secondary));
        }}

        div.stButton > button, div.stDownloadButton > button {{
            border-radius: 11px;
            border: 1px solid var(--vero-primary);
            background: var(--vero-primary);
            color: white;
            font-weight: 760;
            min-height: 2.8rem;
            box-shadow: none;
        }}

        div.stButton > button:hover, div.stDownloadButton > button:hover {{
            border-color: var(--vero-secondary);
            background: var(--vero-secondary);
            color: white;
        }}

        div.stButton > button *,
        div.stDownloadButton > button * {{
            color: #FFFFFF !important;
        }}

        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input,
        [data-baseweb="select"] > div {{
            border-radius: 11px !important;
            border-color: var(--vero-border) !important;
            background: var(--vero-surface) !important;
            color: var(--vero-text) !important;
        }}


        /* Keep select boxes readable in every theme */
        [data-baseweb="select"] > div {{
            background: var(--vero-surface) !important;
            color: var(--vero-text) !important;
        }}

        [data-baseweb="select"] input,
        [data-baseweb="select"] span,
        [data-baseweb="select"] svg {{
            color: var(--vero-text) !important;
            fill: var(--vero-text) !important;
        }}

        [role="listbox"] {{
            background: var(--vero-surface) !important;
            border: 1px solid var(--vero-border) !important;
        }}

        [role="option"] {{
            background: var(--vero-surface) !important;
            color: var(--vero-text) !important;
        }}

        [role="option"]:hover,
        [aria-selected="true"][role="option"] {{
            background: var(--vero-surface-alt) !important;
            color: var(--vero-text) !important;
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background: #FFFFFF !important;
            color: #111827 !important;
        }}

        [data-testid="stSidebar"] [data-baseweb="select"] span,
        [data-testid="stSidebar"] [data-baseweb="select"] input,
        [data-testid="stSidebar"] [data-baseweb="select"] svg {{
            color: #111827 !important;
            fill: #111827 !important;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid var(--vero-border);
            border-radius: 14px;
            overflow: hidden;
        }}

        hr {{
            border-color: var(--vero-border);
        }}

        @media (max-width: 700px) {{
            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}
            .vero-page-title {{ font-size: 2.25rem; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def safe_html(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def safe_number(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def clean_text(value: Any, fallback: str = "") -> str:
    """Return readable text without exposing pandas NaN values."""
    if value is None:
        return fallback
    try:
        if pd.isna(value):
            return fallback
    except (TypeError, ValueError):
        pass
    cleaned = str(value).strip()
    if not cleaned or cleaned.lower() in {"nan", "none", "null", "n/a", "unknown"}:
        return fallback
    return cleaned


def first_present(row: pd.Series, columns: list[str], fallback: Any = "") -> Any:
    """Return the first non-empty value found across possible column aliases."""
    for column in columns:
        if column in row.index:
            value = row.get(column)
            if clean_text(value):
                return value
            if isinstance(value, (int, float)) and not pd.isna(value):
                return value
    return fallback


def first_number(row: pd.Series, columns: list[str], default: float = 0.0) -> float:
    """Return the first valid numeric value across possible column aliases."""
    for column in columns:
        if column not in row.index:
            continue
        value = safe_number(row.get(column), default=float("nan"))
        if not pd.isna(value):
            return value
    return default


def valid_company_name(value: Any) -> bool:
    """Reject IDs, descriptions, and missing values that sometimes leak into name fields."""
    name = clean_text(value)
    if not name or len(name) > 64:
        return False
    if name.replace(".", "").replace("-", "").isdigit():
        return False
    words = name.split()
    if len(words) > 8:
        return False
    sentence_markers = (" is a ", " helps ", " provides ", " platform for ", " company that ")
    if any(marker in name.lower() for marker in sentence_markers):
        return False
    return any(character.isalpha() for character in name)


def page_header(eyebrow: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="vero-eyebrow">{safe_html(eyebrow)}</div>
        <div class="vero-page-title">{safe_html(title)}</div>
        <div class="vero-page-copy">{safe_html(copy)}</div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, copy: str = "") -> None:
    st.markdown(
        f"""
        <div class="vero-section-title">{safe_html(title)}</div>
        <div class="vero-section-copy">{safe_html(copy)}</div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: Any, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="vero-card">
            <div class="vero-kpi-label">{safe_html(label)}</div>
            <div class="vero-kpi-value">{safe_html(value)}</div>
            <div class="vero-kpi-sub">{safe_html(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def progress_bar(label: str, value: float) -> None:
    value = max(0.0, min(100.0, value))
    st.markdown(
        f"""
        <div class="vero-progress-wrap">
            <div class="vero-progress-head"><span>{safe_html(label)}</span><strong>{value:.0f}</strong></div>
            <div class="vero-progress-track"><div class="vero-progress-fill" style="width:{value:.1f}%"></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_csv(filename: str, required: bool = False) -> pd.DataFrame:
    path = OUTPUTS_DIR / filename
    if not path.exists():
        if required:
            st.error(f"Required data file not found: {path}")
            st.stop()
        return pd.DataFrame()
    try:
        return pd.read_csv(path, low_memory=False)
    except Exception as exc:
        if required:
            st.error(f"Could not load {filename}: {exc}")
            st.stop()
        return pd.DataFrame()


@st.cache_resource(show_spinner=False)
def load_model() -> Any:
    path = OUTPUTS_DIR / "startup_credit_score_model.pkl"
    if not path.exists():
        return None
    try:
        return joblib.load(path)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def load_yc_data() -> pd.DataFrame:
    return load_csv("yc_github_metrics.csv")


def _first_existing_column(data: pd.DataFrame, aliases: list[str]) -> str | None:
    return next((column for column in aliases if column in data.columns), None)


def _numeric_signal(data: pd.DataFrame, aliases: list[str]) -> pd.Series:
    column = _first_existing_column(data, aliases)
    if column is None:
        return pd.Series(0.0, index=data.index, dtype=float)
    return pd.to_numeric(data[column], errors="coerce").fillna(0).clip(lower=0)


def _binary_signal(data: pd.DataFrame, aliases: list[str]) -> pd.Series:
    column = _first_existing_column(data, aliases)
    if column is None:
        return pd.Series(0.0, index=data.index, dtype=float)

    values = data[column].fillna("").astype(str).str.strip().str.lower()
    truthy = {"1", "true", "yes", "y", "present", "active"}
    return values.isin(truthy).astype(float)


def _percentile_signal(values: pd.Series) -> pd.Series:
    values = pd.to_numeric(values, errors="coerce").fillna(0).clip(lower=0)
    positive = values > 0
    result = pd.Series(0.0, index=values.index, dtype=float)

    if positive.any():
        # Rank only companies with real observations. Zero or missing data stays zero.
        result.loc[positive] = values.loc[positive].rank(
            method="average",
            pct=True,
        )

    return result



def recalculate_signal_scores(data: pd.DataFrame) -> pd.DataFrame:
    """Create a differentiated, evidence-aware 0-100 signal score.

    Missing Product Hunt or GitHub observations are treated as unknown rather
    than as proof that a company has no traction.
    """
    if data.empty:
        return data

    scored = data.copy()

    ph_votes_raw = _numeric_signal(scored, [
        "ph_votes", "product_hunt_votes", "votes_count", "votes",
    ])
    ph_comments_raw = _numeric_signal(scored, [
        "ph_comments", "product_hunt_comments", "comments_count", "comments",
    ])
    github_stars_raw = _numeric_signal(scored, [
        "github_total_stars", "github_stars", "stars",
    ])
    github_followers_raw = _numeric_signal(scored, [
        "github_followers", "followers",
    ])
    github_repos_raw = _numeric_signal(scored, [
        "github_public_repos", "public_repos", "repositories", "repo_count",
    ])
    github_forks_raw = _numeric_signal(scored, [
        "github_total_forks", "github_forks", "forks",
    ])

    ph_votes = _percentile_signal(ph_votes_raw)
    ph_comments = _percentile_signal(ph_comments_raw)
    github_stars = _percentile_signal(github_stars_raw)
    github_followers = _percentile_signal(github_followers_raw)
    github_repos = _percentile_signal(github_repos_raw)
    github_forks = _percentile_signal(github_forks_raw)

    hiring = _binary_signal(scored, [
        "isHiring", "is_hiring", "hiring", "hiring_binary",
    ])
    yc_top = _binary_signal(scored, [
        "top_company", "is_top_company", "yc_top_company",
    ])
    product_hunt = _binary_signal(scored, [
        "Product_Hunt_Present", "product_hunt_present", "has_product_hunt",
    ])
    ai_company = _binary_signal(scored, [
        "AI_Company", "ai_company", "is_ai", "ai_classification_inferred",
    ])

    description_column = _first_existing_column(scored, [
        "description_clean", "description", "short_description",
        "long_description", "one_liner", "tagline",
    ])

    if description_column is None:
        descriptions = pd.Series("", index=scored.index, dtype=str)
    else:
        descriptions = scored[description_column].fillna("").astype(str)

    invalid_description = descriptions.str.strip().str.lower().isin(
        {"", "nan", "none", "null", "unknown", "unclassified"}
    )
    descriptions = descriptions.mask(invalid_description, "")

    description_length = descriptions.str.len().astype(float)
    description_words = descriptions.str.split().map(len).astype(float)
    description_quality = (
        0.60 * (description_length / 420).clip(0, 1)
        + 0.40 * (description_words / 70).clip(0, 1)
    )

    richness_terms = [
        "platform", "software", "saas", "marketplace", "api", "customers",
        "businesses", "teams", "developers", "consumer", "subscription",
        "payments", "enterprise", "automation", "cloud", "ai",
        "machine learning", "health", "travel", "security", "data",
        "workflow", "booking", "creator", "commerce", "infrastructure",
    ]
    lowered_descriptions = descriptions.str.lower()
    richness_hits = pd.Series(0.0, index=scored.index, dtype=float)
    for term in richness_terms:
        richness_hits += lowered_descriptions.str.contains(
            re.escape(term),
            regex=True,
            na=False,
        ).astype(float)
    text_richness = (richness_hits / 8).clip(0, 1)

    completeness_aliases = [
        ["website_clean", "website", "url"],
        ["industry_clean", "industry", "industry_inferred", "category"],
        ["business_type", "Business_Type", "business_type_inferred"],
        ["business_model", "revenue_model", "business_model_inferred"],
        ["batch", "yc_batch"],
        ["founded_year", "year_founded"],
        ["location", "city", "country"],
        ["team_size", "employee_count", "employees"],
        ["source"],
        ["tags", "tag_list", "keywords"],
    ]

    completeness = pd.Series(0.0, index=scored.index, dtype=float)

    for aliases in completeness_aliases:
        column = _first_existing_column(scored, aliases)
        if column is None:
            continue

        values = scored[column]
        string_values = values.fillna("").astype(str).str.strip()
        present = values.notna() & string_values.ne("")
        present &= ~string_values.str.lower().isin({
            "nan", "none", "null", "unknown", "unclassified",
            "industry unavailable", "industry not classified",
            "revenue model not classified",
        })
        completeness += present.astype(float)

    completeness = (completeness / len(completeness_aliases)).clip(0, 1)

    classification_text = _classification_text(scored)
    industry_results = classification_text.apply(
        lambda value: _best_taxonomy_match(value, INDUSTRY_TAXONOMY)
    )
    business_model_results = classification_text.apply(
        lambda value: _best_taxonomy_match(value, BUSINESS_MODEL_TAXONOMY)
    )

    industry_confidence = industry_results.map(lambda item: float(item[1]))
    business_model_confidence = business_model_results.map(
        lambda item: float(item[1])
    )

    source_column = _first_existing_column(scored, ["source", "dataset"])
    if source_column is None:
        verified_source = pd.Series(0.0, index=scored.index, dtype=float)
    else:
        source_values = scored[source_column].fillna("").astype(str).str.lower()
        verified_source = source_values.str.contains(
            "yc|y combinator|techstars|500 global|product hunt|"
            "sequoia|a16z|andreessen|vc|crunchbase",
            regex=True,
        ).astype(float)

    external_observations = (
        (ph_votes_raw > 0).astype(int)
        + (ph_comments_raw > 0).astype(int)
        + (github_stars_raw > 0).astype(int)
        + (github_followers_raw > 0).astype(int)
        + (github_repos_raw > 0).astype(int)
        + (github_forks_raw > 0).astype(int)
    )

    external_numerator = (
        ph_votes * 30 * (ph_votes_raw > 0)
        + ph_comments * 8 * (ph_comments_raw > 0)
        + github_stars * 28 * (github_stars_raw > 0)
        + github_followers * 12 * (github_followers_raw > 0)
        + github_repos * 12 * (github_repos_raw > 0)
        + github_forks * 10 * (github_forks_raw > 0)
    )

    external_denominator = (
        30 * (ph_votes_raw > 0).astype(float)
        + 8 * (ph_comments_raw > 0).astype(float)
        + 28 * (github_stars_raw > 0).astype(float)
        + 12 * (github_followers_raw > 0).astype(float)
        + 12 * (github_repos_raw > 0).astype(float)
        + 10 * (github_forks_raw > 0).astype(float)
    )

    external_score = (
        external_numerator
        / external_denominator.replace(0, pd.NA)
    ).fillna(0) * 100

    profile_score = (
        18
        + description_quality * 18
        + text_richness * 9
        + completeness * 17
        + verified_source * 8
        + industry_confidence * 8
        + business_model_confidence * 6
        + hiring * 5
        + yc_top * 7
        + product_hunt * 3
        + ai_company * 1
    ).clip(0, 100)

    has_external = external_observations.gt(0)
    raw_score = profile_score.astype(float).copy()
    raw_score.loc[has_external] = (
        external_score.loc[has_external].astype(float) * 0.62
        + profile_score.loc[has_external].astype(float) * 0.38
    )

    confidence = (
        10
        + external_observations * 10
        + completeness * 20
        + description_quality * 12
        + text_richness * 8
        + verified_source * 8
        + industry_confidence * 8
        + business_model_confidence * 6
    ).clip(10, 100)

    confidence_factor = (
        0.55 + 0.45 * (confidence / 100)
    ).clip(0.55, 1.0)

    confidence_adjusted = 50 + (raw_score - 50) * confidence_factor

    relative_rank = (
        confidence_adjusted.rank(method="average", pct=True) * 100
    )

    meaningful = (
        descriptions.str.len().gt(0)
        | external_observations.gt(0)
        | completeness.gt(0)
        | verified_source.gt(0)
    )

    final_score = confidence_adjusted.copy()
    final_score.loc[meaningful] = (
        confidence_adjusted.loc[meaningful] * 0.80
        + relative_rank.loc[meaningful] * 0.20
    )

    scored["signal_score"] = final_score.round(1).clip(0, 100)
    scored["signal_confidence"] = confidence.round(0)
    scored["signal_external_score"] = external_score.round(1)
    scored["signal_profile_score"] = profile_score.round(1)
    scored["signal_observations"] = external_observations.astype(int)

    scored["signal_basis"] = "Profile evidence only"
    scored.loc[
        external_observations.between(1, 2),
        "signal_basis",
    ] = "Limited external evidence"
    scored.loc[
        external_observations.between(3, 4),
        "signal_basis",
    ] = "Mixed evidence"
    scored.loc[
        external_observations.ge(5),
        "signal_basis",
    ] = "Strong external evidence"

    return scored


@st.cache_data(show_spinner=False)
def load_graph_data() -> pd.DataFrame:
    return recalculate_signal_scores(enrich_company_classifications(load_csv("final_startup_graph.csv")))


@st.cache_data(show_spinner=False)
def load_master_data() -> pd.DataFrame:
    data = load_csv("master_startup_database_standardized.csv")
    if data.empty:
        return load_graph_data()
    return recalculate_signal_scores(enrich_company_classifications(data))


model = load_model()
yc_data = load_yc_data()

enterprise_keywords = [
    "enterprise", "business", "companies", "workflow", "automation", "saas",
    "platform", "teams", "developers", "infrastructure", "cloud", "api",
    "integration", "analytics", "security", "compliance",
]
healthcare_keywords = [
    "healthcare", "health", "hospital", "clinical", "doctor", "patient",
    "medical", "care", "diagnosis", "treatment", "pharma", "biotech", "medtech",
]
ai_keywords = [
    "artificial intelligence", "machine learning", "llm", "large language model",
    "generative ai", "computer vision", "deep learning", "neural network", "gpt",
    "ai-powered", "ai-driven", "ai assistant", "ai platform", "ai automation",
]
fintech_keywords = [
    "payments", "banking", "fintech", "financial", "credit", "loans", "mortgage",
    "insurance", "investing", "trading", "wealth", "crypto", "blockchain",
    "wallet", "transaction", "invoice", "accounting", "payroll", "tax",
]
developer_keywords = [
    "api", "sdk", "developer", "infrastructure", "cloud", "database", "deployment",
    "backend", "frontend", "devops", "container", "kubernetes", "hosting",
    "repository", "github", "code", "software engineering", "framework",
]
consumer_keywords = [
    "social", "friends", "community", "chat", "messaging", "creator", "influencer",
    "video", "photos", "music", "dating", "consumer", "users", "followers",
    "streaming", "lifestyle", "shopping", "marketplace",
]
security_keywords = [
    "security", "cybersecurity", "threat", "authentication", "encryption", "identity",
    "compliance", "vpn", "firewall", "fraud", "monitoring", "zero trust", "detection",
]
climate_keywords = [
    "climate", "carbon", "renewable", "solar", "energy", "battery", "sustainability",
    "emissions", "electric vehicle", "ev", "recycling", "clean energy",
]
education_keywords = [
    "education", "learning", "students", "teacher", "classroom", "courses",
    "tutoring", "school", "university", "curriculum", "exam", "study",
]
robotics_keywords = [
    "robotics", "robot", "hardware", "iot", "sensor", "manufacturing", "drone",
    "autonomous", "embedded", "machine vision", "industrial", "supply chain",
]
biotech_keywords = [
    "biotech", "genomics", "dna", "drug discovery", "therapeutics", "bioinformatics",
    "protein", "clinical trial", "pharmaceutical", "molecular", "biology",
]


def keyword_count(text: Any, keywords: list[str]) -> int:
    lowered = str(text).lower()
    return sum(1 for word in keywords if word.lower() in lowered)


def classify_ai(text: Any) -> str:
    return "Yes" if keyword_count(text, ai_keywords) else "No"


def classify_business_type(text: Any) -> str:
    lowered = str(text).lower()
    b2b = keyword_count(lowered, ["enterprise", "businesses", "companies", "teams", "developers", "saas", "workflow", "infrastructure", "platform"])
    b2c = keyword_count(lowered, ["consumer", "users", "shoppers", "students", "creators", "families", "personal", "social", "fitness"])
    if b2b > b2c:
        return "B2B"
    if b2c > b2b:
        return "B2C"
    return "Mixed"



INDUSTRY_TAXONOMY: dict[str, list[str]] = {
    "Artificial Intelligence": [
        "artificial intelligence", "generative ai", "machine learning", "deep learning",
        "large language model", "llm", "computer vision", "ai-powered", "ai driven",
        "ai assistant", "foundation model", "natural language processing", "nlp",
        "ai agent", "ai agents", "agentic", "autocomplete", "ai video",
        "ai monitoring", "generative video", "ai visibility",
    ],
    "Healthcare": [
        "healthcare", "health care", "medical", "hospital", "patient", "clinical",
        "doctor", "physician", "telehealth", "diagnostic", "care delivery", "medtech",
    ],
    "Biotechnology": [
        "biotech", "biotechnology", "genomics", "therapeutics", "drug discovery",
        "clinical trial", "protein", "molecular", "pharmaceutical", "bioinformatics",
    ],
    "Financial Technology": [
        "fintech", "payments", "banking", "financial services", "credit", "lending",
        "loan", "mortgage", "insurance", "wealth", "investing", "payroll", "accounting",
        "invoice", "tax", "fraud", "transaction", "wallet",
    ],
    "Enterprise Software": [
        "enterprise software", "saas", "workflow", "business software", "operations",
        "crm", "erp", "productivity", "collaboration", "automation platform",
        "back office", "sales enablement", "customer support",
    ],
    "Developer Tools": [
        "developer tools", "developer platform", "api", "sdk", "devops", "database",
        "cloud infrastructure", "deployment", "observability", "kubernetes", "hosting",
        "software development", "code", "repository", "web apps", "edge platform",
        "framework", "frameworks", "deploy", "developers", "developer infrastructure",
    ],
    "Cybersecurity": [
        "cybersecurity", "security", "zero trust", "authentication", "encryption",
        "identity", "threat detection", "firewall", "vpn", "compliance", "data protection",
    ],
    "Consumer": [
        "consumer app", "social network", "social media", "dating", "friends", "creator",
        "community", "messaging", "chat", "lifestyle", "personal", "mobile app",
    ],
    "E-commerce and Retail": [
        "ecommerce", "e-commerce", "online store", "retail", "shopping", "merchant",
        "commerce", "marketplace", "brands", "checkout", "direct to consumer", "d2c",
    ],
    "Education": [
        "education", "edtech", "learning", "student", "teacher", "school", "university",
        "classroom", "course", "tutoring", "curriculum", "study", "training platform",
    ],
    "Climate and Energy": [
        "climate", "clean energy", "renewable", "solar", "battery", "carbon", "emissions",
        "sustainability", "electric vehicle", "energy storage", "recycling", "grid",
    ],
    "Real Estate and Construction": [
        "real estate", "property", "construction", "housing", "homebuilder", "mortgage tech",
        "proptech", "building", "contractor", "rental", "landlord", "tenant",
    ],
    "Logistics and Supply Chain": [
        "logistics", "supply chain", "shipping", "freight", "warehouse", "delivery",
        "fleet", "transportation", "procurement", "inventory", "last mile",
    ],
    "Robotics and Hardware": [
        "robotics", "robot", "hardware", "sensor", "drone", "iot", "industrial automation",
        "autonomous vehicle", "embedded", "semiconductor", "manufacturing equipment",
    ],
    "Media and Entertainment": [
        "media", "entertainment", "music", "video", "streaming", "gaming", "game studio",
        "podcast", "content platform", "film", "sports media",
    ],
    "Food and Agriculture": [
        "food", "restaurant", "agriculture", "agtech", "farm", "crop", "grocery",
        "beverage", "kitchen", "meal", "farming",
    ],
    "Travel and Hospitality": [
        "travel", "hotel", "hospitality", "tourism", "booking", "vacation", "flight",
        "accommodation", "trip", "restaurant reservation",
    ],
    "Human Resources": [
        "human resources", "hr tech", "recruiting", "hiring", "talent", "employee",
        "workforce", "benefits", "people operations", "applicant tracking",
    ],
    "Legal Technology": [
        "legal tech", "legal", "law firm", "lawyer", "contract management", "compliance software",
        "litigation", "court", "attorney",
    ],
    "Government and Civic Technology": [
        "government", "civic", "public sector", "municipality", "federal", "defense",
        "public safety", "city government", "govtech",
    ],
}

BUSINESS_MODEL_TAXONOMY: dict[str, list[str]] = {
    "SaaS": ["saas", "software as a service", "cloud software", "subscription software", "web platform", "dashboard"],
    "Enterprise Contract": ["enterprise contract", "annual contract", "multi-year contract", "enterprise customers", "sold to enterprises", "procurement"],
    "Marketplace": ["marketplace", "connects buyers and sellers", "two-sided", "booking platform", "matching platform"],
    "Transaction Fee": ["transaction fee", "take rate", "commission", "per transaction", "payment processing fee"],
    "Usage-Based": ["usage based", "usage-based", "pay as you go", "consumption based", "per request", "metered"],
    "Subscription": ["subscription", "monthly plan", "annual plan", "membership", "recurring fee"],
    "API / Infrastructure": ["api", "sdk", "developer platform", "infrastructure platform", "api-first", "platform as a service"],
    "E-commerce": ["ecommerce", "e-commerce", "online store", "direct to consumer", "d2c", "sells products"],
    "Advertising": ["advertising", "ad-supported", "sponsored", "media buying", "ad network"],
    "Hardware Sales": ["hardware", "device", "equipment", "sensor", "robot", "manufacturing hardware"],
    "Services": ["consulting", "professional services", "agency", "managed service", "implementation services"],
    "Licensing": ["licensing", "license fee", "technology license", "royalty"],
}


def _usable_series(data: pd.DataFrame, aliases: list[str]) -> pd.Series:
    column = _first_existing_column(data, aliases)
    if column is None:
        return pd.Series("", index=data.index, dtype=str)
    values = data[column].fillna("").astype(str).str.strip()
    invalid = values.str.lower().isin({"", "nan", "none", "null", "unknown", "unclassified", "n/a"})
    return values.mask(invalid, "")


def _classification_text(data: pd.DataFrame) -> pd.Series:
    combined = pd.Series("", index=data.index, dtype=str)
    alias_groups = [
        ["name", "company_name", "startup_name"],
        ["description_clean", "description", "short_description", "tagline"],
        ["tags", "tag_list", "keywords"],
        ["industry_clean", "industry", "category", "vertical"],
        ["business_type", "Business_Type"],
    ]
    for aliases in alias_groups:
        combined = combined + " " + _usable_series(data, aliases)
    return combined.str.lower().str.replace(r"\s+", " ", regex=True).str.strip()


def _best_taxonomy_match(text: str, taxonomy: dict[str, list[str]]) -> tuple[str, float]:
    if not text:
        return "", 0.0
    scored: list[tuple[str, float]] = []
    for label, terms in taxonomy.items():
        score = 0.0
        for term in terms:
            normalized = term.lower()
            if normalized in text:
                score += 1.0 + min(1.5, 0.22 * max(0, len(normalized.split()) - 1))
        if score:
            scored.append((label, score))
    if not scored:
        return "", 0.0
    scored.sort(key=lambda item: item[1], reverse=True)
    label, top = scored[0]
    second = scored[1][1] if len(scored) > 1 else 0.0
    confidence = min(0.95, 0.42 + 0.09 * top + 0.16 * ((top - second) / top if top else 0))
    return label, round(confidence, 2)


def enrich_company_classifications(data: pd.DataFrame) -> pd.DataFrame:
    """Fill genuinely missing classifications from existing company text.

    Existing source classifications are preserved. Inferred values are clearly
    marked with method and confidence columns so VERO does not pretend that a
    keyword inference is verified source data.
    """
    if data.empty:
        return data

    enriched = data.copy()
    text = _classification_text(enriched)
    industry_results = text.apply(lambda value: _best_taxonomy_match(value, INDUSTRY_TAXONOMY))
    model_results = text.apply(lambda value: _best_taxonomy_match(value, BUSINESS_MODEL_TAXONOMY))

    inferred_industry = industry_results.map(lambda item: item[0])
    industry_confidence = industry_results.map(lambda item: item[1])
    inferred_model = model_results.map(lambda item: item[0])
    model_confidence = model_results.map(lambda item: item[1])

    existing_industry = _usable_series(enriched, ["industry_clean", "industry", "category", "vertical"])
    existing_type = _usable_series(enriched, ["business_type", "Business_Type"])

    enriched["industry_inferred"] = existing_industry.where(existing_industry.ne(""), inferred_industry)
    enriched["industry_classification_method"] = "Source data"
    missing_industry = existing_industry.eq("")
    enriched.loc[missing_industry, "industry_classification_method"] = "VERO text inference"
    enriched["industry_classification_confidence"] = 1.0
    enriched.loc[missing_industry, "industry_classification_confidence"] = industry_confidence[missing_industry]
    enriched.loc[enriched["industry_inferred"].eq(""), "industry_classification_method"] = "Insufficient evidence"

    inferred_audience = text.apply(classify_business_type)
    enriched["business_type_inferred"] = existing_type.where(existing_type.ne(""), inferred_audience)
    enriched["business_type_classification_method"] = existing_type.ne("").map({True: "Source data", False: "VERO text inference"})

    enriched["business_model_inferred"] = inferred_model
    enriched["business_model_confidence"] = model_confidence
    enriched["ai_classification_inferred"] = text.apply(classify_ai)

    # Put enriched industry into the common display/filter column without destroying originals.
    if "industry" not in enriched.columns:
        enriched["industry"] = enriched["industry_inferred"]
    else:
        current = enriched["industry"].fillna("").astype(str).str.strip()
        invalid = current.str.lower().isin({"", "nan", "none", "null", "unknown", "unclassified", "n/a"})
        enriched.loc[invalid, "industry"] = enriched.loc[invalid, "industry_inferred"]

    return enriched


def find_yc_match(name: str) -> pd.Series | None:
    if not name or yc_data.empty or "name" not in yc_data.columns:
        return None
    normalized = yc_data["name"].astype(str).str.lower().str.strip()
    target = name.lower().strip()
    exact = yc_data[normalized == target]
    if not exact.empty:
        return exact.iloc[0]
    partial = yc_data[normalized.str.contains(re.escape(target), na=False)]
    return partial.iloc[0] if not partial.empty else None



def _clean_website_phrase(value: Any) -> str:
    """Normalize website copy and reject common navigation / browser noise."""
    cleaned = clean_text(value)

    if not cleaned:
        return ""

    cleaned = BeautifulSoup(cleaned, "html.parser").get_text(" ", strip=True)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    lowered = cleaned.lower()

    noise_phrases = [
        "skip to content",
        "enable javascript",
        "javascript enabled",
        "we're sorry",
        "we’re sorry",
        "privacy preferences",
        "log in or sign up",
        "help center",
        "gift cards",
        "add dates",
        "add guests",
        "0 of 0 items",
        "homepage",
    ]

    if any(phrase in lowered for phrase in noise_phrases) and len(cleaned) < 180:
        return ""

    return cleaned


def _unique_web_fragments(
    fragments: list[str],
    *,
    max_chars: int = 1400,
) -> str:
    """Deduplicate useful website fragments while preserving order."""
    result: list[str] = []
    seen: set[str] = set()
    total = 0

    for fragment in fragments:
        cleaned = _clean_website_phrase(fragment)

        if not cleaned:
            continue

        chunks = re.split(
            r"(?<=[.!?])\s+|(?:\s+[|•·]\s+)",
            cleaned,
        )

        for chunk in chunks:
            chunk = re.sub(r"\s+", " ", chunk).strip(" -–—|")

            if len(chunk) < 18:
                continue

            lowered = chunk.casefold()

            if any(
                phrase in lowered
                for phrase in [
                    "skip to content",
                    "log in or sign up",
                    "become a host",
                    "help center",
                    "gift cards",
                    "add dates",
                    "add guests",
                    "0 of 0 items",
                    "javascript enabled",
                    "all homes",
                    "homes on",
                ]
            ):
                continue

            normalized = re.sub(
                r"[^a-z0-9]+",
                " ",
                lowered,
            ).strip()

            if not normalized or normalized in seen:
                continue

            duplicate = False
            for prior in seen:
                if (
                    len(normalized) > 30
                    and (
                        normalized in prior
                        or prior in normalized
                    )
                ):
                    duplicate = True
                    break

            if duplicate:
                continue

            seen.add(normalized)
            result.append(chunk)
            total += len(chunk) + 1

            if total >= max_chars:
                return " ".join(result).strip()

    return " ".join(result).strip()


def analyze_website(url: str) -> tuple[str, str]:
    """Extract concise company evidence instead of dumping page navigation."""
    if not url:
        return "", ""

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for tag in soup(
            [
                "script",
                "style",
                "noscript",
                "nav",
                "footer",
                "header",
                "form",
                "button",
                "svg",
            ]
        ):
            tag.decompose()

        fragments: list[str] = []

        title = ""
        if soup.title and soup.title.string:
            title = _clean_website_phrase(
                soup.title.string
            )

        meta_candidates = [
            ("property", "og:description"),
            ("name", "twitter:description"),
            ("name", "description"),
        ]

        for attribute, value in meta_candidates:
            tag = soup.find(
                "meta",
                attrs={attribute: value},
            )

            if tag:
                content = _clean_website_phrase(
                    tag.get("content", "")
                )
                if content:
                    fragments.append(content)

        for script in soup.find_all(
            "script",
            attrs={"type": "application/ld+json"},
        ):
            raw = script.string or script.get_text(
                " ",
                strip=True,
            )

            if not raw:
                continue

            try:
                payload = json.loads(raw)
            except Exception:
                continue

            nodes = payload if isinstance(payload, list) else [payload]

            while nodes:
                node = nodes.pop(0)

                if isinstance(node, list):
                    nodes.extend(node)
                    continue

                if not isinstance(node, dict):
                    continue

                graph_nodes = node.get("@graph")
                if isinstance(graph_nodes, list):
                    nodes.extend(graph_nodes)

                description = _clean_website_phrase(
                    node.get("description")
                )
                if description:
                    fragments.append(description)

        for selector in [
            "main h1",
            "main h2",
            "main p",
            "article h1",
            "article h2",
            "article p",
            "h1",
            "h2",
        ]:
            for element in soup.select(selector)[:12]:
                phrase = _clean_website_phrase(
                    element.get_text(
                        " ",
                        strip=True,
                    )
                )
                if phrase:
                    fragments.append(phrase)

        clean_description = _unique_web_fragments(
            fragments,
            max_chars=1200,
        )

        # Some modern sites provide little usable metadata. Fall back to
        # visible paragraph copy after navigation/script elements were removed.
        if not clean_description:
            fallback_fragments: list[str] = []

            body = soup.find("main") or soup.find("body")
            if body is not None:
                for element in body.find_all(
                    ["p", "h1", "h2", "h3"],
                    limit=40,
                ):
                    phrase = re.sub(
                        r"\s+",
                        " ",
                        element.get_text(" ", strip=True),
                    ).strip()

                    lowered_phrase = phrase.lower()

                    if len(phrase) < 25:
                        continue

                    if any(
                        noise in lowered_phrase
                        for noise in [
                            "skip to content",
                            "log in or sign up",
                            "become a host",
                            "help center",
                            "gift cards",
                            "add dates",
                            "add guests",
                            "0 of 0 items",
                            "javascript enabled",
                            "cookie preferences",
                        ]
                    ):
                        continue

                    fallback_fragments.append(phrase)

            clean_description = _unique_web_fragments(
                fallback_fragments,
                max_chars=1000,
            )

        # If the page exposes only a meaningful title, preserve it rather
        # than returning an empty description.
        if not clean_description and title:
            clean_description = title

        if (
            title
            and title.casefold()
            not in clean_description.casefold()
            and len(title) <= 160
        ):
            clean_description = _unique_web_fragments(
                [title, clean_description],
                max_chars=1200,
            )

        blocked = [
            "verify you are human",
            "cloudflare",
            "access denied",
            "captcha",
        ]

        if any(
            phrase in clean_description.lower()
            for phrase in blocked
        ):
            clean_description = ""

        github_match = re.search(
            r"https?://github\.com/[A-Za-z0-9_.-]+",
            response.text,
        )
        github_url = (
            github_match.group(0)
            if github_match
            else ""
        )

        return (
            clean_description.strip(),
            github_url,
        )

    except requests.RequestException:
        return "", ""


def get_database_description(company_name: str) -> str:
    """Return the cleanest stored description VERO already has for a company."""
    if not company_name.strip():
        return ""

    try:
        row = get_unified_company_record(company_name)
    except Exception:
        row = pd.Series(dtype=object)

    if row.empty:
        return ""

    description = clean_text(
        first_present(
            row,
            [
                "description_clean",
                "description",
                "short_description",
                "long_description",
                "one_liner",
                "tagline",
            ],
        )
    )

    if not description:
        return ""

    # Stored descriptions can also contain navigation-like junk from old imports.
    description = re.sub(r"\s+", " ", description).strip()

    junk_patterns = [
        r"\bskip to content\b",
        r"\blog in or sign up\b",
        r"\badd dates\b",
        r"\badd guests\b",
        r"\bhelp center\b",
        r"\bgift cards\b",
        r"\b0 of 0 items showing\b",
        r"\bwe(?:'|’)re sorry\b.*?javascript enabled\.?",
    ]

    for pattern in junk_patterns:
        description = re.sub(
            pattern,
            " ",
            description,
            flags=re.IGNORECASE,
        )

    description = re.sub(r"\s+", " ", description).strip()

    # Keep enough detail for scoring, but avoid giant raw database dumps.
    return description[:1600].strip()


def build_import_description(
    company_name: str,
    website_description: str,
) -> tuple[str, str]:
    """Choose the best non-empty description without deleting existing evidence."""
    website_description = clean_text(website_description)

    if website_description:
        return website_description, "website"

    database_description = get_database_description(company_name)

    if database_description:
        return database_description, "VERO database"

    existing = clean_text(
        st.session_state.get("description_text")
    )

    if existing:
        return existing, "existing description"

    return "", "none"


FORM_DEFAULTS = {
    "description_text": "AI platform that helps hospitals automate clinical workflows",
    "ai_company": "Yes",
    "business_type": "B2B",
    "top_company": False,
    "product_hunt": "No",
    "hiring": "false",
    "startup_age": 2,
    "tag_count": 0,
    "github_followers": 0,
    "github_public_repos": 0,
    "github_total_stars": 0,
    "github_total_forks": 0,
    "score_result": None,
    "ai_research_report": None,
}
for key, value in FORM_DEFAULTS.items():
    st.session_state.setdefault(key, value)


with st.sidebar:
    st.markdown('<div class="vero-brand">VERO</div>', unsafe_allow_html=True)
    st.markdown('<div class="vero-brand-sub">Startup Intelligence Platform</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Analyze Startup",
            "Compare Startups",
            "Startup Database",
            "Startup Profile",
            "Leaderboards",
            "Model Insights",
            "About",
            "Privacy Policy",
            "Settings",
        ],
        key="page",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.caption("Appearance")
    selected_theme = st.selectbox(
        "Theme",
        list(THEMES),
        index=list(THEMES).index(st.session_state.theme_name),
        label_visibility="collapsed",
    )
    st.session_state.theme_name = selected_theme
    st.caption("VERO v1.0")

inject_css(THEMES[st.session_state.theme_name])



def build_row_classification_text(row: pd.Series) -> str:
    fields = [
        "name", "company_name", "startup_name",
        "description_clean", "description", "short_description",
        "long_description", "one_liner", "tagline",
        "tags", "tag_list", "keywords", "industries",
        "industry_clean", "industry", "industry_inferred",
        "category", "vertical", "subindustry",
        "business_type", "Business_Type", "business_type_inferred",
        "business_model", "revenue_model", "business_model_inferred",
        "customers", "products", "program_names",
    ]

    parts: list[str] = []
    for field in fields:
        if field not in row.index:
            continue
        value = clean_text(row.get(field))
        if value and value.lower() not in {
            "industry unavailable",
            "industry not classified",
            "unclassified",
            "unknown",
            "insufficient evidence",
        } and value not in parts:
            parts.append(value)

    return " ".join(parts).strip()


def resolve_row_industry(
    row: pd.Series,
    fallback: str = "Insufficient evidence",
) -> tuple[str, str, float]:
    source_value = clean_text(
        first_present(
            row,
            [
                "industry_clean",
                "industry",
                "industry_inferred",
                "category",
                "vertical",
            ],
        )
    )

    invalid = {
        "",
        "industry unavailable",
        "industry not classified",
        "unclassified",
        "unknown",
        "insufficient evidence",
    }

    if source_value.lower() not in invalid:
        return source_value, "Source data", 1.0

    evidence_text = build_row_classification_text(row)

    if evidence_text:
        label, confidence = _best_taxonomy_match(
            evidence_text.lower(),
            INDUSTRY_TAXONOMY,
        )
        if label:
            return label, "VERO text inference", confidence

        try:
            profile = build_company_profile(evidence_text)
            if profile.primary_industry:
                return (
                    profile.primary_industry,
                    "VERO intelligence engine",
                    safe_number(profile.industry_confidence),
                )
        except Exception:
            pass

    return fallback, "Insufficient evidence", 0.0


def _normalize_company_lookup_name(value: Any) -> str:
    return re.sub(
        r"[^a-z0-9]+",
        "",
        clean_text(value).lower(),
    )


def _company_row_value_quality(value: Any) -> float:
    cleaned = clean_text(value)

    if not cleaned:
        return 0.0

    try:
        if isinstance(value, (int, float)) and not pd.isna(value):
            return 1.0 if float(value) != 0 else 0.15
    except (TypeError, ValueError):
        pass

    if cleaned.lower() in {
        "unknown",
        "unclassified",
        "industry unavailable",
        "industry not classified",
        "revenue model not classified",
        "location unavailable",
        "unavailable",
        "insufficient evidence",
    }:
        return 0.0

    return 0.35 + min(len(cleaned) / 140.0, 1.0)


def _matching_company_rows(
    data: pd.DataFrame,
    company_name: str,
) -> pd.DataFrame:
    if data.empty or not company_name.strip():
        return pd.DataFrame()

    name_column = next(
        (
            column
            for column in [
                "name",
                "company_name",
                "startup_name",
                "organization_name",
            ]
            if column in data.columns
        ),
        None,
    )

    if name_column is None:
        return pd.DataFrame()

    names = data[name_column].fillna("").astype(str)
    target = _normalize_company_lookup_name(company_name)

    exact = data[
        names.map(_normalize_company_lookup_name).eq(target)
    ]

    if not exact.empty:
        return exact.copy()

    lowered = company_name.strip().lower()

    return data[
        names.str.lower().str.contains(
            re.escape(lowered),
            na=False,
        )
    ].copy()


def get_unified_company_record(
    company_name: str,
) -> pd.Series:
    """Merge all matching VERO/YC rows into one best-evidence record."""
    groups: list[pd.DataFrame] = []

    for data in [
        load_graph_data(),
        load_master_data(),
        yc_data,
    ]:
        matches = _matching_company_rows(
            data,
            company_name,
        )
        if not matches.empty:
            groups.append(matches)

    if not groups:
        return pd.Series(dtype=object)

    combined = pd.concat(
        groups,
        ignore_index=True,
        sort=False,
    )

    merged: dict[str, Any] = {}

    for column in combined.columns:
        best_value: Any = None
        best_quality = -1.0

        for value in combined[column].tolist():
            quality = _company_row_value_quality(value)

            if quality > best_quality:
                best_value = value
                best_quality = quality

        merged[column] = best_value

    merged["name"] = company_name
    merged["_merged_record_count"] = len(combined)

    return pd.Series(merged)


def enrich_structural_evidence(
    company_name: str,
    row: pd.Series,
    evidence_text: str,
) -> str:
    """Translate detected company structure into partial-weight VERO evidence.

    The calibrated moat engine recognizes the 'Structural evidence:' section and
    intentionally gives it less weight than direct/source evidence.
    """
    if row is None or row.empty:
        return evidence_text.strip()

    industry, _, _ = resolve_row_industry(row)

    business_model = clean_text(
        first_present(
            row,
            [
                "business_model",
                "revenue_model",
                "business_model_inferred",
            ],
        )
    )

    source_text = (
        " "
        + company_name.lower()
        + " "
        + evidence_text.lower()
        + " "
        + industry.lower()
        + " "
        + business_model.lower()
        + " "
    )

    clues: list[str] = []

    if any(
        term in source_text
        for term in [
            "marketplace",
            "two-sided",
            "booking platform",
            "hosts",
            "guests",
            "buyers and sellers",
            "rental marketplace",
        ]
    ):
        clues.extend([
            "two sided marketplace",
            "marketplace liquidity",
            "network effects",
            "repeat transactions",
            "customer trust and reputation system",
        ])

    if any(
        term in source_text
        for term in [
            "api",
            "sdk",
            "developer",
            "infrastructure",
            "payments infrastructure",
            "cloud infrastructure",
        ]
    ):
        clues.extend([
            "deep product integrations",
            "developer ecosystem",
            "embedded into customer workflows",
            "switching costs",
            "integration complexity",
            "recurring usage",
        ])

    if any(
        term in source_text
        for term in [
            "enterprise",
            "annual contract",
            "multi-year contract",
            "procurement",
            "saas",
            "b2b",
        ]
    ):
        clues.extend([
            "recurring revenue",
            "enterprise customer relationships",
            "workflow integration",
            "switching costs",
            "long sales cycle",
            "implementation complexity",
        ])

    if industry == "Travel and Hospitality":
        clues.extend([
            "travel demand exposure",
            "regulatory complexity",
            "local market regulation",
            "competitive marketplace",
        ])

    if industry == "Financial Technology":
        clues.extend([
            "regulatory complexity",
            "compliance requirements",
            "payments infrastructure",
            "fraud risk",
            "high technical depth",
        ])

    if industry == "Healthcare":
        clues.extend([
            "regulatory complexity",
            "compliance requirements",
            "workflow integration",
            "high switching costs",
        ])

    if industry == "Developer Tools":
        clues.extend([
            "developer adoption",
            "technical depth",
            "integration into software workflows",
            "switching costs",
        ])

    if industry == "Artificial Intelligence":
        clues.extend([
            "technical depth",
            "model dependency risk",
            "rapidly evolving competition",
        ])

    deduped: list[str] = []
    for clue in clues:
        if clue not in deduped:
            deduped.append(clue)

    pieces = [evidence_text.strip()] if evidence_text.strip() else []

    if deduped:
        pieces.append(
            "Structural evidence: "
            + "; ".join(deduped)
            + "."
        )

    return "\n".join(pieces).strip()


def build_unified_vero_result(
    company_name: str,
    *,
    manual_text: str = "",
    metadata_text: str = "",
    ai_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """One scoring pipeline used by Analyze, Profile, Compare, and Overview.

    Database evidence is always the common baseline when a matching company
    exists. Manual/website or AI evidence is additive and explicitly changes the
    evidence mode rather than silently creating a different scoring system.
    """
    clean_name = clean_text(company_name, "Unnamed startup")
    row = get_unified_company_record(clean_name)

    evidence_sections: list[str] = []
    evidence_modes: list[str] = []

    if not row.empty:
        database_text = build_row_classification_text(row)
        database_text = enrich_structural_evidence(
            clean_name,
            row,
            database_text,
        )

        if database_text:
            evidence_sections.append(
                "Database evidence:\n" + database_text
            )
            evidence_modes.append("Database")

    clean_manual = manual_text.strip()

    if clean_manual:
        evidence_sections.append(
            "Manual / website evidence:\n"
            + clean_manual
        )
        evidence_modes.append("Manual")

    if metadata_text.strip():
        evidence_sections.append(
            "Structured metadata:\n"
            + metadata_text.strip()
        )

    if isinstance(ai_report, dict):
        ai_text = research_to_description(ai_report).strip()

        if ai_text:
            evidence_sections.append(
                "AI researched evidence:\n"
                + ai_text
            )
            evidence_modes.append("AI research")

    # De-duplicate entire sections while preserving order.
    unique_sections: list[str] = []
    for section in evidence_sections:
        if section and section not in unique_sections:
            unique_sections.append(section)

    evidence_text = "\n\n".join(unique_sections).strip()

    if not evidence_text:
        raise ValueError(
            "VERO does not have enough evidence to score this company."
        )

    profile = build_company_profile(evidence_text)
    vero = analyze_vero_score(profile)

    mode_order = [
        mode
        for mode in ["Database", "Manual", "AI research"]
        if mode in evidence_modes
    ]
    evidence_mode = " + ".join(mode_order) or "Manual"

    evidence_confidence = safe_number(
        getattr(
            profile,
            "overall_evidence_confidence",
            0,
        )
    ) * 100

    return {
        "name": clean_name,
        "row": row,
        "evidence_text": evidence_text,
        "evidence_mode": evidence_mode,
        "evidence_confidence": evidence_confidence,
        "profile": profile,
        "vero": vero,
    }



@st.cache_data(show_spinner=False)
def build_cached_database_vero_result(
    company_name: str,
) -> dict[str, Any]:
    """Cached database-only VERO result for browsing pages.

    This avoids repeatedly re-running every intelligence engine for the same
    company on every Streamlit rerun/page switch.
    """
    result = build_unified_vero_result(company_name)

    # Return only serializable/simple objects Streamlit can cache safely.
    return {
        "name": result["name"],
        "evidence_text": result["evidence_text"],
        "evidence_mode": result["evidence_mode"],
        "evidence_confidence": result["evidence_confidence"],
        "profile_dict": result["profile"].to_dict(),
        "vero_dict": result["vero"].to_dict(),
    }


def get_cached_database_vero_objects(
    company_name: str,
) -> tuple[dict[str, Any], dict[str, Any], float, str, str]:
    """Convenience wrapper around the cached serializable result."""
    result = build_cached_database_vero_result(company_name)
    return (
        result["profile_dict"],
        result["vero_dict"],
        safe_number(result["evidence_confidence"]),
        clean_text(result["evidence_mode"], "Database"),
        result["evidence_text"],
    )


def render_overview() -> None:
    page_header(
        "Startup intelligence",
        "Make startup signals understandable.",
        "Explore companies, estimate follow-on funding potential, and compare the traction signals that shape the VERO score.",
    )

    graph = load_graph_data()
    total_startups = len(graph) if not graph.empty else len(yc_data)
    source_count = graph["source"].nunique() if not graph.empty and "source" in graph.columns else 1
    success_rate = ((yc_data.get("Raised_Next_Round", pd.Series(dtype=str)) == "Yes").mean() * 100) if not yc_data.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Startups indexed", f"{total_startups:,}", "Across the current VERO database")
    with c2:
        kpi_card("Data sources", f"{source_count:,}", "Unified into one searchable graph")
    with c3:
        kpi_card("Model ROC AUC", "0.79", "Cross-validated performance")
    with c4:
        kpi_card("Training success rate", f"{success_rate:.1f}%", "Raised a follow-on round")

    section_header("Start with a company", "Jump directly into one of VERO's core workflows.")
    left, right = st.columns([1.5, 1])
    with left:
        st.markdown('<div class="vero-card">', unsafe_allow_html=True)
        company = st.text_input("Search or analyze a startup", placeholder="Try Stripe, Airbnb, or a startup website")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Analyze startup", width="stretch"):
                st.session_state["overview_company"] = company or "Example Startup"
                navigate_to("Analyze Startup")
        with col_b:
            if st.button("Open profile search", width="stretch"):
                st.session_state["profile_query"] = company or "Airbnb"
                navigate_to("Startup Profile")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown(
            """
            <div class="vero-card">
                <div class="vero-kpi-label">How VERO works</div>
                <div style="font-size:1.05rem;font-weight:760;margin-top:.55rem;">Evidence → Signals → Score</div>
                <div class="vero-kpi-sub" style="margin-top:.55rem;line-height:1.65;">
                    VERO combines company descriptions, YC metadata, Product Hunt activity, GitHub traction, hiring, and startup age into a single decision-support view.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not graph.empty:
        section_header("Strongest current signals", "A quick view of highly ranked companies in the graph database.")

        name_columns = ["name", "company_name", "startup_name", "organization_name"]
        score_columns = ["signal_score", "vero_score", "score", "startup_score"]
        description_columns = ["description_clean", "description", "short_description", "tagline"]
        industry_columns = ["industry", "industry_clean", "category", "sector"]

        cards: list[dict[str, Any]] = []
        seen_names: set[str] = set()

        sortable = graph.copy()
        score_column = next((column for column in score_columns if column in sortable.columns), None)
        if score_column:
            sortable["_display_score"] = pd.to_numeric(sortable[score_column], errors="coerce").fillna(0)
            sortable = sortable.sort_values("_display_score", ascending=False)

        for _, row in sortable.iterrows():
            name = clean_text(first_present(row, name_columns))
            if not valid_company_name(name):
                continue
            normalized_name = name.lower()
            if normalized_name in seen_names:
                continue

            try:
                (
                    profile_dict,
                    vero_dict,
                    card_confidence,
                    _evidence_mode,
                    _evidence_text,
                ) = get_cached_database_vero_objects(name)

                score = safe_number(
                    vero_dict.get("overall_score"),
                    0,
                )
                industry = clean_text(
                    profile_dict.get("industry", {}).get("primary"),
                    resolve_row_industry(row)[0],
                )
                industry_method = "Unified VERO pipeline"
                industry_confidence = safe_number(
                    profile_dict.get("industry", {}).get("confidence"),
                    0,
                )
            except Exception:
                score = first_number(row, score_columns, 0)
                card_confidence = safe_number(
                    row.get("signal_confidence"),
                    0,
                )
                industry, industry_method, industry_confidence = resolve_row_industry(row)
            description = clean_text(
                first_present(row, description_columns),
                f"{name} is included in VERO's startup intelligence database."
            )
            if len(description) > 135:
                description = description[:132].rstrip() + "..."

            cards.append({
                "name": name,
                "score": score,
                "industry": industry,
                "industry_method": industry_method,
                "industry_confidence": industry_confidence,
                "signal_confidence": card_confidence,
                "description": description,
            })
            seen_names.add(normalized_name)
            if len(cards) == 8:
                break

        if cards:
            cols = st.columns(4)
            for index, card in enumerate(cards):
                with cols[index % 4]:
                    initials = "".join(word[0] for word in card["name"].split()[:2]).upper()
                    st.markdown(
                        f"""
                        <div class="vero-card">
                            <div style="display:flex;align-items:center;gap:.75rem;margin-bottom:.8rem;">
                                <div style="width:42px;height:42px;border-radius:12px;background:var(--vero-surface-alt);display:flex;align-items:center;justify-content:center;font-weight:850;color:var(--vero-primary);">
                                    {safe_html(initials)}
                                </div>
                                <div>
                                    <div style="font-weight:850;font-size:1rem;">{safe_html(card["name"])}</div>
                                    <span class="vero-badge">{safe_html(card["industry"])}</span>
                                    <div class="vero-kpi-sub" style="margin-top:.28rem;">
                                        {safe_html(card["industry_method"])}
                                        {f" · {card['industry_confidence']:.0%}" if card["industry_confidence"] else ""}
                                    </div>
                                </div>
                            </div>
                            <div class="vero-kpi-sub" style="min-height:58px;line-height:1.5;">{safe_html(card["description"])}</div>
                            <div style="display:flex;justify-content:space-between;align-items:end;margin-top:1rem;">
                                <span class="vero-kpi-sub">VERO score · {card["signal_confidence"]:.0f}% confidence</span>
                                <strong style="font-size:1.7rem;">{card["score"]:.0f}</strong>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            st.info("No clean company records were available for this section.")


def apply_yc_match(match: pd.Series) -> None:
    st.session_state.top_company = bool(match.get("top_company", False))
    st.session_state.product_hunt = "Yes" if str(match.get("Product_Hunt_Present", "No")).lower() == "yes" else "No"
    st.session_state.hiring = "true" if str(match.get("isHiring", False)).lower() == "true" else "false"
    for state_key, column in [
        ("startup_age", "startup_age"),
        ("tag_count", "tag_count"),
        ("github_followers", "github_followers"),
        ("github_public_repos", "github_public_repos"),
        ("github_total_stars", "github_total_stars"),
        ("github_total_forks", "github_total_forks"),
    ]:
        st.session_state[state_key] = int(safe_number(match.get(column, 0)))


def render_analysis_result(result: dict[str, Any]) -> None:
    profile = result.get("profile")
    vero = result.get("vero")
    company_name = clean_text(result.get("name"), "Startup")

    if profile is None or vero is None:
        st.error("The saved VERO result is incomplete. Run the analysis again.")
        return

    def readable(value: Any) -> str:
        if value in (None, ""):
            return "Not detected"
        return str(value).replace("_", " ").title()

    def evidence_items(evidence: dict[str, list[str]] | None, limit: int = 12) -> list[str]:
        items: list[str] = []
        for category, values in (evidence or {}).items():
            for value in values:
                cleaned = str(value).lstrip("+ -").strip()
                if cleaned:
                    items.append(f"{readable(category)}: {cleaned}")
                if len(items) >= limit:
                    return items
        return items

    score = safe_number(getattr(vero, "overall_score", 0))
    grade = clean_text(getattr(vero, "investment_grade", ""), "Unrated")
    components = dict(getattr(vero, "score_components", {}) or {})
    strengths = list(getattr(vero, "strengths", []) or [])
    concerns = list(getattr(vero, "concerns", []) or [])

    section_header(
        f"{company_name} — VERO assessment",
        "Deterministic scoring based on the submitted profile and any verified AI research evidence.",
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("VERO score", f"{score:.1f}/100")
    c2.metric("Investment grade", grade)
    c3.metric("Business quality", f"{profile.overall_business_quality_score:.2f}/10")
    c4.metric("Risk", f"{profile.overall_risk_score:.2f}/10")

    evidence_mode = clean_text(
        result.get("evidence_mode"),
        "Manual",
    )
    evidence_confidence = safe_number(
        result.get(
            "evidence_confidence",
            getattr(profile, "overall_evidence_confidence", 0) * 100,
        )
    )

    st.caption(
        f"Evidence mode: {evidence_mode} · "
        f"{evidence_confidence:.0f}% overall evidence confidence"
    )

    st.info(
        f"**Why this rating:** VERO assigned **{grade}** because the weighted "
        f"components total **{score:.1f}/100**. Business quality contributed "
        f"{safe_number(components.get('business_quality')):.2f}/30, moat "
        f"{safe_number(components.get('moat')):.2f}/25, strategic signals "
        f"{safe_number(components.get('signals')):.2f}/15, risk adjustment "
        f"{safe_number(components.get('risk_adjustment')):.2f}/20, and evidence "
        f"confidence {safe_number(components.get('confidence')):.2f}/10."
    )

    section_header("Detected profile", "VERO's primary classifications from the available evidence.")
    p1, p2, p3 = st.columns(3)
    with p1:
        kpi_card("Industry", profile.primary_industry or "Not detected", profile.primary_subindustry or "No subindustry")
    with p2:
        kpi_card("Business model", profile.primary_business_model or "Not detected", f"{profile.business_model_confidence:.0%} confidence")
    with p3:
        kpi_card("Signal engine", f"{profile.overall_signal_score:.1f}/100", "Strategic evidence score")

    if getattr(profile, "overall_evidence_confidence", 1.0) < 0.35:
        st.warning(
            "This assessment has limited supporting evidence. Low-confidence "
            "components are pulled toward neutral rather than treated as proof "
            "of weakness."
        )

    section_header(
        "Score breakdown",
        "Each component's contribution to the final 100-point score.",
    )
    maximums = {
        "business_quality": 30.0,
        "moat": 25.0,
        "signals": 15.0,
        "risk_adjustment": 20.0,
        "confidence": 10.0,
    }
    moat_status = getattr(profile, "moat_status", "supported")
    business_quality_status = getattr(
        profile,
        "business_quality_status",
        "supported",
    )
    risk_status = getattr(profile, "risk_status", "supported")

    explanations = {
        "business_quality": (
            "Insufficient evidence to measure business quality reliably."
            if business_quality_status == "insufficient_evidence"
            else f"Raw business-quality score: {profile.overall_business_quality_score:.2f}/10."
        ),
        "moat": (
            "Insufficient direct evidence to measure competitive moat. "
            "VERO treats this as unknown rather than a zero-quality moat."
            if moat_status == "insufficient_evidence"
            else (
                f"Raw moat score: {profile.overall_moat_score:.2f}/10; "
                f"strongest moat: {readable(profile.strongest_moat)}."
            )
        ),
        "signals": (
            f"Raw strategic-signal score: "
            f"{profile.overall_signal_score:.2f}/100."
        ),
        "risk_adjustment": (
            "Insufficient evidence to measure risk reliably."
            if risk_status == "insufficient_evidence"
            else (
                f"Raw risk score: {profile.overall_risk_score:.2f}/10. "
                "Lower risk earns more points."
            )
        ),
        "confidence": (
            "Measures how strongly the available evidence supports VERO's "
            "component estimates."
        ),
    }
    for key in maximums:
        value = safe_number(components.get(key))
        progress_bar(readable(key), value / maximums[key] * 100)
        st.caption(f"{value:.2f} / {maximums[key]:.0f} — {explanations[key]}")

    section_header("Decision notes", "Threshold-based strengths and concerns.")
    left, right = st.columns(2)
    with left:
        st.markdown("### Strengths")
        if strengths:
            for item in strengths:
                st.markdown(f"- {item}")
        else:
            st.info("No current strength threshold was triggered by the supplied evidence.")
    with right:
        st.markdown("### Concerns")
        if concerns:
            for item in concerns:
                st.markdown(f"- {item}")
        else:
            st.info("No current concern threshold was triggered.")

    section_header("Evidence", "Phrases used by the business-quality, moat, risk, and signal engines.")
    tabs = st.tabs(["Business quality", "Moats", "Risks", "Signals"])
    with tabs[0]:
        items = evidence_items(profile.business_quality_evidence)
        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.info("No direct business-quality evidence was detected.")
    with tabs[1]:
        items = evidence_items(profile.moat_evidence)
        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.info("No direct moat evidence was detected.")
    with tabs[2]:
        items = evidence_items(profile.risk_evidence)
        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.info("No direct risk phrases were detected; industry baselines may still apply.")
    with tabs[3]:
        if profile.strategic_scores:
            for category, value in profile.strategic_scores.items():
                progress_bar(readable(category), safe_number(value) * 10)
                st.caption(f"{safe_number(value):.2f}/10")
        else:
            st.info("No strategic signal category received a score.")

    section_header("Competitive and risk context")
    left, right = st.columns(2)
    with left:
        st.markdown("### Likely competitors")
        if profile.competitors:
            for competitor in profile.competitors[:10]:
                st.markdown(f"- {competitor}")
        else:
            st.info("No likely competitor was identified from this evidence.")
    with right:
        st.markdown("### Largest risks")
        if profile.largest_risks:
            for risk in profile.largest_risks:
                st.markdown(f"- **{readable(risk)}:** {safe_number(profile.risk_scores.get(risk)):.2f}/10")
        else:
            st.info("No risk category crossed the major-risk threshold.")

    st.warning(
        "Missing information is treated as unknown, not automatically negative. "
        "This output is decision support, not an investment recommendation."
    )

    if result.get("evidence_text"):
        with st.expander("View unified evidence used for this score"):
            st.code(
                result["evidence_text"],
                language="text",
            )

    with st.expander("View full VERO intelligence profile"):
        st.json(profile.to_dict())
    with st.expander("View full VERO score output"):
        st.json(vero.to_dict())



def render_analyze() -> None:
    page_header(
        "Company assessment",
        "Analyze a startup.",
        "Use manual evidence, website imports, and optional live AI research. The final score remains deterministic and explainable.",
    )

    name_default = clean_text(st.session_state.get("overview_company"), "Example Startup")
    top_left, top_right = st.columns([1.2, 1])
    with top_left:
        name = st.text_input("Startup name", value=name_default, key="analysis_company_name")
    with top_right:
        website_url = st.text_input("Website URL", placeholder="https://example.com", key="analysis_website_url")

    research_col, import_col, clear_col = st.columns([2, 2, 1])
    with research_col:
        ai_research_clicked = st.button("Research with AI + live web", width="stretch", type="primary")
    with import_col:
        import_signals_clicked = st.button("Import website and YC signals", width="stretch")
    with clear_col:
        if st.button("Clear", width="stretch"):
            st.session_state.score_result = None
            st.session_state.ai_research_report = None
            st.rerun()

    if ai_research_clicked:
        if not AI_RESEARCH_AVAILABLE:
            st.error("The VERO AI research module is missing. Copy vero/research into the project.")
        else:
            with st.spinner("Researching current public sources..."):
                try:
                    report = research_company(
                        company_name=name,
                        website_url=website_url,
                        existing_description=st.session_state.get("description_text", ""),
                    )
                    st.session_state.ai_research_report = report
                    enriched = research_to_description(report)
                    if enriched:
                        st.session_state.description_text = enriched
                    st.success(f"Research complete — {report.get('research_confidence', 0)}% evidence confidence.")
                except ResearchError as exc:
                    message = str(exc)
                    if "quota" in message.lower() or "429" in message:
                        st.warning(
                            "AI research is temporarily unavailable because the API account has no remaining quota. "
                            "Manual scoring and website/YC imports still work. Add API billing, then retry."
                        )
                    else:
                        st.error(message)

    if import_signals_clicked:
        with st.spinner("Collecting public website signals..."):
            auto_description, auto_github = analyze_website(website_url)

            chosen_description, description_source = build_import_description(
                name,
                auto_description,
            )

            if chosen_description:
                st.session_state.description_text = chosen_description
                st.session_state.ai_company = classify_ai(chosen_description)
                st.session_state.business_type = classify_business_type(
                    chosen_description
                )

            yc_match = find_yc_match(name)

            if yc_match is not None:
                apply_yc_match(yc_match)

            if chosen_description:
                if description_source == "website":
                    st.success(
                        "Imported a cleaned website description"
                        + (
                            f" and matched {yc_match.get('name', name)} in YC."
                            if yc_match is not None
                            else "."
                        )
                    )
                elif description_source == "VERO database":
                    st.info(
                        "The website did not expose a clean description, "
                        "so VERO used its stored company description instead."
                    )
                else:
                    st.info(
                        "The website did not expose a clean description. "
                        "VERO kept the existing description instead of clearing it."
                    )
            elif yc_match is not None:
                st.success(
                    f"Matched {yc_match.get('name', name)} in the YC dataset. "
                    "No clean company description was available."
                )
            else:
                st.warning(
                    "VERO could not extract a clean website description or find "
                    "stored company text. Enter the description manually."
                )

            if auto_github:
                st.info(
                    f"Detected GitHub organization: {auto_github}"
                )

    report = st.session_state.get("ai_research_report")
    if isinstance(report, dict):
        section_header("AI research evidence", "Review current external evidence before scoring.")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Research confidence", f"{report.get('research_confidence', 0)}%")
        r2.metric("Sources", len(report.get("sources", [])))
        r3.metric("Positive signals", len(report.get("positive_signals", [])))
        r4.metric("Risk signals", len(report.get("risk_signals", [])))
        if report.get("one_sentence_summary"):
            st.info(report["one_sentence_summary"])
        tabs = st.tabs(["Signals", "News", "Sources", "Missing evidence"])
        with tabs[0]:
            a, b = st.columns(2)
            with a:
                st.markdown("#### Positive")
                for item in report.get("positive_signals", []) or ["No verified positive signals found."]:
                    st.markdown(f"- {item}")
            with b:
                st.markdown("#### Risks")
                for item in report.get("risk_signals", []) or ["No verified risk signals found."]:
                    st.markdown(f"- {item}")
        with tabs[1]:
            for item in report.get("recent_news", []):
                if isinstance(item, dict):
                    st.markdown(f"**{item.get('headline', 'News item')}**")
                    st.caption(f"{item.get('date') or 'Date unavailable'} · {str(item.get('impact', 'neutral')).title()}")
                    st.write(item.get("why_it_matters", ""))
                    if item.get("source_url"):
                        st.link_button("Open source", item["source_url"])
                    st.divider()
        with tabs[2]:
            for source in report.get("sources", []):
                if isinstance(source, dict) and source.get("url"):
                    st.markdown(f"- [{source.get('title') or source['url']}]({source['url']}) — {source.get('source_type', 'other')}")
        with tabs[3]:
            for item in report.get("missing_information", []) or ["No major missing field identified."]:
                st.markdown(f"- {item}")

    section_header("Startup evidence", "Provide specific product, customer, revenue, traction, moat, and risk evidence.")
    with st.form("startup_score_form"):
        description = st.text_area("Description and evidence", key="description_text", height=230)
        left, middle, right = st.columns(3)
        with left:
            ai_company = st.selectbox("AI company", ["Yes", "No"], key="ai_company")
            business_type = st.selectbox("Business type", ["B2B", "B2C", "Mixed"], key="business_type")
            hiring = st.selectbox("Currently hiring", ["true", "false"], key="hiring")
            top_company = st.selectbox("YC top company", [False, True], key="top_company")
        with middle:
            product_hunt = st.selectbox("Product Hunt presence", ["No", "Yes"], key="product_hunt")
            startup_age = st.number_input("Startup age", min_value=0, max_value=50, key="startup_age")
            tag_count = st.number_input("Tag count", min_value=0, max_value=100, key="tag_count")
            github_followers = st.number_input("GitHub followers", min_value=0, key="github_followers")
        with right:
            github_public_repos = st.number_input("GitHub public repositories", min_value=0, key="github_public_repos")
            github_total_stars = st.number_input("GitHub total stars", min_value=0, key="github_total_stars")
            github_total_forks = st.number_input("GitHub total forks", min_value=0, key="github_total_forks")
        submitted = st.form_submit_button("Calculate VERO score", width="stretch")

    if submitted:
        cleaned = description.strip()
        if len(cleaned) < 25:
            st.error("Add a more detailed description before scoring.")
        else:
            metadata = (
                f"\n\nCompany metadata: business type {business_type}; AI company {ai_company}; "
                f"currently hiring {hiring}; YC top company {top_company}; Product Hunt {product_hunt}; "
                f"startup age {startup_age}; tag count {tag_count}; GitHub followers {github_followers}; "
                f"public repositories {github_public_repos}; stars {github_total_stars}; forks {github_total_forks}."
            )
            with st.spinner("Building VERO intelligence profile..."):
                try:
                    unified = build_unified_vero_result(
                        name.strip() or "Unnamed startup",
                        manual_text=cleaned,
                        metadata_text=metadata,
                        ai_report=st.session_state.get("ai_research_report"),
                    )
                    st.session_state.score_result = unified
                except Exception as exc:
                    st.error(f"VERO could not analyze this startup: {exc}")

    if st.session_state.score_result:
        render_analysis_result(st.session_state.score_result)



def fuzzy_match(data: pd.DataFrame, name: str) -> pd.Series | None:
    if data.empty or not name.strip():
        return None

    name_column = next(
        (column for column in ["name", "company_name", "startup_name", "organization_name"] if column in data.columns),
        None,
    )
    if name_column is None:
        return None

    names = data[name_column].fillna("").astype(str).str.strip()
    target = name.lower().strip()

    exact = data[names.str.lower() == target]
    candidates = exact if not exact.empty else data[names.str.lower().str.contains(re.escape(target), na=False)]
    if candidates.empty:
        return None

    # Prefer the matching record containing the most usable traction information.
    metric_aliases = [
        "signal_score", "vero_score", "score",
        "ph_votes", "product_hunt_votes", "votes_count",
        "github_total_stars", "github_stars", "stars",
        "github_followers", "followers",
    ]
    ranked = candidates.copy()
    ranked["_record_quality"] = 0.0
    for column in metric_aliases:
        if column in ranked.columns:
            ranked["_record_quality"] += pd.to_numeric(ranked[column], errors="coerce").fillna(0).gt(0).astype(float)
    return ranked.sort_values("_record_quality", ascending=False).iloc[0]


def company_signal(row: pd.Series, columns: str | list[str]) -> float:
    aliases = [columns] if isinstance(columns, str) else columns
    return max(0.0, first_number(row, aliases, 0))



def enrich_comparison_evidence(
    company_name: str,
    row: pd.Series,
    evidence_text: str,
) -> str:
    """Add deterministic structural clues so VERO engines can evaluate sparse rows.

    This does not invent company facts. It converts already-detected industry,
    business-model, customer, and platform structure into normalized evidence
    phrases the existing moat/risk/business-quality engines understand.
    """
    parts: list[str] = [evidence_text.strip()] if evidence_text.strip() else []

    industry, _, _ = resolve_row_industry(row)

    business_model = clean_text(
        first_present(
            row,
            [
                "business_model",
                "revenue_model",
                "business_model_inferred",
            ],
        )
    )

    if not business_model:
        model_label, _ = _best_taxonomy_match(
            build_row_classification_text(row).lower(),
            BUSINESS_MODEL_TAXONOMY,
        )
        business_model = model_label

    business_type = clean_text(
        first_present(
            row,
            [
                "business_type",
                "Business_Type",
                "business_type_inferred",
            ],
        )
    )

    lowered = (
        " "
        + company_name.lower()
        + " "
        + evidence_text.lower()
        + " "
        + industry.lower()
        + " "
        + business_model.lower()
        + " "
        + business_type.lower()
        + " "
    )

    structural_clues: list[str] = []

    # Marketplace structure
    marketplace_terms = [
        "marketplace",
        "two-sided",
        "booking platform",
        "matching platform",
        "buyers and sellers",
        "hosts",
        "guests",
        "rental marketplace",
        "travel marketplace",
    ]
    if (
        "marketplace" in business_model.lower()
        or any(term in lowered for term in marketplace_terms)
    ):
        structural_clues.extend([
            "two sided marketplace",
            "marketplace liquidity",
            "network effects",
            "supply and demand network",
            "repeat transactions",
            "customer trust and reputation system",
        ])

    # API / developer infrastructure structure
    api_terms = [
        "api",
        "sdk",
        "developer",
        "infrastructure",
        "payments infrastructure",
        "cloud infrastructure",
        "platform as a service",
    ]
    if (
        "api" in business_model.lower()
        or "infrastructure" in business_model.lower()
        or any(term in lowered for term in api_terms)
    ):
        structural_clues.extend([
            "deep product integrations",
            "developer ecosystem",
            "embedded into customer workflows",
            "switching costs",
            "integration complexity",
            "recurring usage",
            "platform dependency risk",
        ])

    # Enterprise SaaS / contract structure
    enterprise_terms = [
        "enterprise",
        "annual contract",
        "multi-year contract",
        "procurement",
        "b2b",
        "saas",
    ]
    if any(term in lowered for term in enterprise_terms):
        structural_clues.extend([
            "recurring revenue",
            "annual contracts",
            "enterprise customer relationships",
            "workflow integration",
            "switching costs",
            "long sales cycle",
            "implementation complexity",
        ])

    # Consumer / brand-led structure
    consumer_terms = [
        "consumer",
        "users",
        "travel",
        "shopping",
        "creator",
        "social",
        "mobile app",
    ]
    if any(term in lowered for term in consumer_terms):
        structural_clues.extend([
            "brand awareness",
            "consumer demand",
            "customer acquisition risk",
            "competitive market",
        ])

    # Industry context
    if industry == "Travel and Hospitality":
        structural_clues.extend([
            "travel demand exposure",
            "regulatory complexity",
            "local market regulation",
            "competitive marketplace",
        ])

    if industry == "Financial Technology":
        structural_clues.extend([
            "regulatory complexity",
            "compliance requirements",
            "payments infrastructure",
            "fraud risk",
            "high technical depth",
        ])

    if industry == "Healthcare":
        structural_clues.extend([
            "regulatory complexity",
            "compliance requirements",
            "workflow integration",
            "high switching costs",
        ])

    if industry == "Developer Tools":
        structural_clues.extend([
            "developer adoption",
            "technical depth",
            "integration into software workflows",
            "switching costs",
        ])

    if industry == "Artificial Intelligence":
        structural_clues.extend([
            "technical depth",
            "model dependency risk",
            "rapidly evolving competition",
        ])

    # Observable metadata
    if company_signal(
        row,
        ["github_total_stars", "github_stars", "stars"],
    ) > 0:
        structural_clues.append("developer interest")

    if company_signal(
        row,
        ["github_public_repos", "public_repos", "repo_count"],
    ) > 0:
        structural_clues.append("open source activity")

    if company_signal(
        row,
        ["ph_votes", "product_hunt_votes", "votes_count"],
    ) > 0:
        structural_clues.append("product demand signal")

    hiring_value = clean_text(
        first_present(
            row,
            ["isHiring", "is_hiring", "hiring", "hiring_binary"],
        )
    ).lower()
    if hiring_value in {"true", "yes", "1"}:
        structural_clues.append("currently hiring")

    # Keep deterministic phrases deduplicated.
    deduped: list[str] = []
    for clue in structural_clues:
        if clue and clue not in deduped:
            deduped.append(clue)

    if deduped:
        parts.append(
            "Structural evidence: "
            + "; ".join(deduped)
            + "."
        )

    return "\n".join(part for part in parts if part).strip()

def render_compare() -> None:
    page_header(
        "Side-by-side analysis",
        "Compare startups.",
        "Compare two companies across VERO signal strength, profile evidence, business quality, moat, risk, and any observable external traction.",
    )

    master = load_master_data()
    graph = load_graph_data()

    if master.empty and graph.empty:
        st.warning("No comparison database is currently available.")
        return

    c1, c2 = st.columns(2)

    with c1:
        startup_1 = st.text_input(
            "First startup",
            "Airbnb",
            key="compare_startup_1",
        )

    with c2:
        startup_2 = st.text_input(
            "Second startup",
            "Stripe",
            key="compare_startup_2",
        )

    if not st.button(
        "Run comparison",
        width="stretch",
        type="primary",
    ):
        return

    def candidate_rows(
        data: pd.DataFrame,
        company_name: str,
    ) -> list[pd.Series]:
        if data.empty:
            return []

        name_col = next(
            (
                column
                for column in [
                    "name",
                    "company_name",
                    "startup_name",
                    "organization_name",
                ]
                if column in data.columns
            ),
            None,
        )

        if name_col is None:
            return []

        names = data[name_col].fillna("").astype(str).str.strip()
        target = company_name.strip().lower()

        exact = data[names.str.lower().eq(target)]

        if not exact.empty:
            return [
                row
                for _, row in exact.iterrows()
            ]

        partial = data[
            names.str.lower().str.contains(
                re.escape(target),
                na=False,
            )
        ]

        return [
            row
            for _, row in partial.iterrows()
        ]

    def row_quality(row: pd.Series) -> float:
        quality = 0.0

        descriptive_fields = [
            "description_clean",
            "description",
            "short_description",
            "long_description",
            "one_liner",
            "tagline",
            "industry",
            "industry_clean",
            "industry_inferred",
            "business_model_inferred",
            "website_clean",
            "website",
            "source",
        ]

        for field in descriptive_fields:
            if field in row.index and clean_text(row.get(field)):
                quality += 1.0

        metric_groups = [
            ["signal_score"],
            ["signal_confidence"],
            ["ph_votes", "product_hunt_votes", "votes_count"],
            ["ph_comments", "product_hunt_comments", "comments_count"],
            ["github_total_stars", "github_stars", "stars"],
            ["github_followers", "followers"],
            ["github_public_repos", "public_repos", "repo_count"],
            ["github_total_forks", "github_forks", "forks"],
        ]

        for aliases in metric_groups:
            if first_number(row, aliases, 0) > 0:
                quality += 1.5

        return quality

    def best_match(company_name: str) -> pd.Series | None:
        candidates: list[pd.Series] = []

        for data in [master, graph, yc_data]:
            candidates.extend(
                candidate_rows(
                    data,
                    company_name,
                )
            )

        if not candidates:
            return None

        return max(
            candidates,
            key=row_quality,
        )

    row1 = best_match(startup_1)
    row2 = best_match(startup_2)

    if row1 is None or row2 is None:
        missing = startup_1 if row1 is None else startup_2
        st.warning(
            f"No match was found for {missing}. Try a shorter company name."
        )
        return

    def build_company_comparison(row: pd.Series) -> dict[str, Any]:
        name = clean_text(
            first_present(
                row,
                [
                    "name",
                    "company_name",
                    "startup_name",
                    "organization_name",
                ],
            ),
            "Unknown company",
        )

        unified = build_unified_vero_result(name)
        merged_row = unified["row"]
        profile = unified["profile"]
        vero = unified["vero"]

        industry = (
            profile.primary_industry
            or resolve_row_industry(merged_row)[0]
        )

        business_model = (
            profile.primary_business_model
            or clean_text(
                first_present(
                    merged_row,
                    [
                        "business_model",
                        "revenue_model",
                        "business_model_inferred",
                    ],
                ),
                "Insufficient evidence",
            )
        )

        source = clean_text(
            first_present(
                merged_row,
                [
                    "source",
                    "data_source",
                    "platform",
                    "dataset",
                ],
            ),
            "VERO database",
        )

        observations = int(
            safe_number(
                merged_row.get("signal_observations"),
                0,
            )
        )

        return {
            "row": merged_row,
            "name": name,
            "industry": industry,
            "industry_method": "Unified VERO pipeline",
            "industry_confidence": safe_number(
                profile.industry_confidence
            ),
            "business_model": business_model,
            "source": source,
            "signal_score": safe_number(vero.overall_score),
            "signal_confidence": safe_number(
                unified["evidence_confidence"]
            ),
            "profile_score": safe_number(vero.overall_score),
            "external_score": safe_number(
                merged_row.get("signal_external_score"),
                0,
            ),
            "observations": observations,
            "profile": profile,
            "vero": vero,
            "business_quality": safe_number(
                profile.overall_business_quality_score
            ),
            "moat": safe_number(
                profile.overall_moat_score
            ),
            "risk": safe_number(
                profile.overall_risk_score
            ),
            "strategic_signal": safe_number(
                profile.overall_signal_score
            ),
            "evidence_mode": unified["evidence_mode"],
            "evidence_text": unified["evidence_text"],
        }

    company1 = build_company_comparison(row1)
    company2 = build_company_comparison(row2)

    def render_company_summary(company: dict[str, Any]) -> None:
        vero = company["vero"]

        st.markdown(
            f"""
            <div class="vero-card">
                <span class="vero-badge">{safe_html(company["source"])}</span>
                <div style="font-size:1.8rem;font-weight:850;margin-top:.8rem;">
                    {safe_html(company["name"])}
                </div>
                <div class="vero-kpi-sub" style="margin-top:.25rem;">
                    {safe_html(company["industry"])}
                </div>
                <div class="vero-kpi-sub">
                    {safe_html(company["business_model"])}
                </div>
                <div style="display:flex;align-items:end;justify-content:space-between;margin-top:1rem;">
                    <div>
                        <div class="vero-kpi-label">VERO SCORE</div>
                        <div class="vero-kpi-value">{company["signal_score"]:.0f}</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="vero-kpi-label">CONFIDENCE</div>
                        <div style="font-size:1.25rem;font-weight:850;">
                            {company["signal_confidence"]:.0f}%
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if vero is not None:
            st.caption(
                f"VERO investment score: "
                f"{vero.overall_score:.1f}/100 · "
                f"{vero.investment_grade}"
            )

    left_summary, right_summary = st.columns(2)

    with left_summary:
        render_company_summary(company1)

    with right_summary:
        render_company_summary(company2)

    section_header(
        "VERO score comparison",
        "These metrics use VERO's profile evidence and intelligence engines, so the comparison still works when Product Hunt or GitHub data is unavailable.",
    )

    def compare_metric(
        label: str,
        value1: float,
        value2: float,
        maximum: float,
        suffix: str = "",
        higher_is_better: bool = True,
    ) -> None:
        value1 = max(0.0, value1)
        value2 = max(0.0, value2)

        st.markdown(f"**{label}**")
        a, b = st.columns(2)

        if higher_is_better:
            pct1 = (
                value1 / maximum * 100
                if maximum
                else 0
            )
            pct2 = (
                value2 / maximum * 100
                if maximum
                else 0
            )
        else:
            pct1 = (
                (maximum - value1) / maximum * 100
                if maximum
                else 0
            )
            pct2 = (
                (maximum - value2) / maximum * 100
                if maximum
                else 0
            )

        with a:
            progress_bar(
                company1["name"],
                pct1,
            )
            st.caption(
                f"{value1:.1f}{suffix}"
            )

        with b:
            progress_bar(
                company2["name"],
                pct2,
            )
            st.caption(
                f"{value2:.1f}{suffix}"
            )

    compare_metric(
        "Overall VERO score",
        company1["signal_score"],
        company2["signal_score"],
        100,
        "/100",
    )

    compare_metric(
        "Evidence confidence",
        company1["signal_confidence"],
        company2["signal_confidence"],
        100,
        "%",
    )


    if (
        company1["profile"] is not None
        or company2["profile"] is not None
    ):
        section_header(
            "Business intelligence comparison",
            "Scores inferred from each company's available description, classifications, and metadata. Low-confidence components should be read as incomplete evidence, not definitive weakness.",
        )

        compare_metric(
            "Business quality",
            company1["business_quality"],
            company2["business_quality"],
            10,
            "/10",
        )

        compare_metric(
            "Moat strength (evidence-backed)",
            company1["moat"],
            company2["moat"],
            10,
            "/10",
        )

        compare_metric(
            "Strategic signal engine",
            company1["strategic_signal"],
            company2["strategic_signal"],
            100,
            "/100",
        )

        # Risk is shown as raw risk, but the bar is inverted so a longer bar
        # means the company has the more favorable lower-risk profile.
        compare_metric(
            "Risk position",
            company1["risk"],
            company2["risk"],
            10,
            "/10 risk",
            higher_is_better=False,
        )

        st.markdown("### What actually differs")

        differences: list[str] = []

        bq_gap = company1["business_quality"] - company2["business_quality"]
        if abs(bq_gap) >= 0.4:
            leader = company1["name"] if bq_gap > 0 else company2["name"]
            differences.append(
                f"**{leader}** has the stronger business-quality profile."
            )

        moat_gap = company1["moat"] - company2["moat"]
        moat_conf_1 = safe_number(
            getattr(company1["profile"], "moat_confidence", 0)
        )
        moat_conf_2 = safe_number(
            getattr(company2["profile"], "moat_confidence", 0)
        )

        if max(moat_conf_1, moat_conf_2) < 0.40:
            differences.append(
                "Moat comparison is **low confidence** for both companies, so the "
                "current moat values should be treated as evidence-limited rather "
                "than definitive."
            )
        elif abs(moat_gap) >= 0.4:
            leader = company1["name"] if moat_gap > 0 else company2["name"]
            differences.append(
                f"**{leader}** currently has the stronger supported moat evidence."
            )

        signal_gap = company1["strategic_signal"] - company2["strategic_signal"]
        if abs(signal_gap) >= 4:
            leader = company1["name"] if signal_gap > 0 else company2["name"]
            differences.append(
                f"**{leader}** has the stronger strategic-signal profile."
            )

        risk_gap = company1["risk"] - company2["risk"]
        if abs(risk_gap) >= 0.4:
            safer = company1["name"] if risk_gap < 0 else company2["name"]
            differences.append(
                f"**{safer}** currently has the more favorable lower-risk profile."
            )

        if company1["business_model"] != company2["business_model"]:
            differences.append(
                f"The companies use different business models: "
                f"**{company1['name']} — {company1['business_model']}** vs "
                f"**{company2['name']} — {company2['business_model']}**."
            )

        if company1["industry"] != company2["industry"]:
            differences.append(
                f"They operate in different primary industries: "
                f"**{company1['name']} — {company1['industry']}** vs "
                f"**{company2['name']} — {company2['industry']}**."
            )

        if not differences:
            differences.append(
                "VERO does not currently see a large enough evidence-backed gap "
                "to call one company clearly stronger across these components."
            )

        for item in differences:
            st.markdown(f"- {item}")

    section_header(
        "Observable external traction",
        "Only metrics with at least one real observation are shown. Missing metrics are treated as unknown rather than as zero traction.",
    )

    external_metrics = [
        (
            "Product Hunt votes",
            ["ph_votes", "product_hunt_votes", "votes_count", "votes"],
        ),
        (
            "Product Hunt comments",
            ["ph_comments", "product_hunt_comments", "comments_count", "comments"],
        ),
        (
            "GitHub stars",
            ["github_total_stars", "github_stars", "stars"],
        ),
        (
            "GitHub followers",
            ["github_followers", "followers"],
        ),
        (
            "GitHub repositories",
            ["github_public_repos", "public_repos", "repositories", "repo_count"],
        ),
        (
            "GitHub forks",
            ["github_total_forks", "github_forks", "forks"],
        ),
    ]

    displayed_external = 0

    for label, aliases in external_metrics:
        value1 = company_signal(
            company1["row"],
            aliases,
        )
        value2 = company_signal(
            company2["row"],
            aliases,
        )

        if value1 <= 0 and value2 <= 0:
            continue

        displayed_external += 1
        maximum = max(
            value1,
            value2,
            1,
        )

        st.markdown(f"**{label}**")
        a, b = st.columns(2)

        with a:
            progress_bar(
                company1["name"],
                value1 / maximum * 100,
            )
            st.caption(
                f"Observed value: {value1:,.0f}"
                if value1 > 0
                else "No stored observation"
            )

        with b:
            progress_bar(
                company2["name"],
                value2 / maximum * 100,
            )
            st.caption(
                f"Observed value: {value2:,.0f}"
                if value2 > 0
                else "No stored observation"
            )

    if displayed_external == 0:
        st.info(
            "VERO does not currently have Product Hunt or GitHub observations "
            "for either of these company records. The comparison above therefore "
            "uses profile evidence and VERO intelligence instead of displaying "
            "misleading rows of zeros."
        )

    section_header(
        "Profile differences",
        "A quick qualitative view of where the companies differ.",
    )

    profile_left, profile_right = st.columns(2)

    def render_profile_differences(
        company: dict[str, Any],
    ) -> None:
        st.markdown(
            f"### {company['name']}"
        )
        st.markdown(
            f"**Industry:** {company['industry']}"
        )
        st.markdown(
            f"**Business model:** "
            f"{company['business_model']}"
        )

        profile = company["profile"]

        if profile is None:
            st.caption(
                "Insufficient evidence for a full intelligence profile."
            )
            return

        st.markdown(
            f"**Strongest moat:** "
            f"{str(profile.strongest_moat or 'Not detected').replace('_', ' ').title()}"
        )
        st.markdown(
            f"**Strongest business quality:** "
            f"{str(profile.strongest_business_quality or 'Not detected').replace('_', ' ').title()}"
        )

        if profile.largest_risks:
            readable_risks = ", ".join(
                risk.replace("_", " ").title()
                for risk in profile.largest_risks[:3]
            )
            st.markdown(
                f"**Largest risks:** {readable_risks}"
            )
        else:
            st.markdown(
                "**Largest risks:** No major risk threshold triggered"
            )

        if profile.competitors:
            st.markdown(
                "**Likely competitors:** "
                + ", ".join(
                    profile.competitors[:5]
                )
            )

        with st.expander("View comparison evidence"):
            st.code(
                enrich_comparison_evidence(
                    company["name"],
                    company["row"],
                    build_row_classification_text(company["row"]),
                ),
                language="text",
            )

    with profile_left:
        render_profile_differences(
            company1
        )

    with profile_right:
        render_profile_differences(
            company2
        )

    st.warning(
        "A missing external metric means VERO has no stored observation for "
        "that metric. It does not mean the company has zero real-world traction."
    )

    st.caption(
        "Moat scoring distinguishes direct company evidence from VERO-inferred "
        "structural evidence. Inferred marketplace, integration, or network-effect "
        "clues receive partial weight and cannot by themselves create a near-perfect moat."
    )



def render_database() -> None:
    page_header(
        "Startup database",
        "Explore the startup database.",
        "Search and inspect VERO's cleaned company records without loading every intelligence engine at once.",
    )

    master = load_master_data()
    graph = load_graph_data()

    sources = [
        data
        for data in [master, graph, yc_data]
        if not data.empty
    ]

    if not sources:
        st.warning("The startup database is unavailable.")
        return

    combined = pd.concat(
        sources,
        ignore_index=True,
        sort=False,
    )

    name_column = next(
        (
            column
            for column in [
                "name",
                "company_name",
                "startup_name",
                "organization_name",
            ]
            if column in combined.columns
        ),
        None,
    )

    if name_column is None:
        st.warning("No company-name column was found in the database.")
        return

    combined["_display_name"] = (
        combined[name_column]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    malformed_name = (
        combined["_display_name"].str.len().gt(90)
        | combined["_display_name"].str.contains(
            r"[.!?]\s",
            regex=True,
            na=False,
        )
        | combined["_display_name"].str.lower().isin(
            {"", "nan", "none", "null", "unknown"}
        )
    )

    database = combined.loc[~malformed_name].copy()
    database["_normalized_name"] = database["_display_name"].map(
        _normalize_company_lookup_name
    )

    # Lightweight dedupe: keep the first useful row per normalized company name.
    # Deep merging happens only when a company is actually opened/scored.
    database = database.drop_duplicates(
        subset=["_normalized_name"],
        keep="first",
    ).copy()

    search_col, source_col = st.columns([2.2, 1.2])

    with search_col:
        search_query = st.text_input(
            "Search startups",
            "",
            key="database_search",
            placeholder="Search Airbnb, Stripe, FlatX...",
        )

    source_values = []
    if "source" in database.columns:
        source_values = sorted(
            {
                clean_text(value)
                for value in database["source"].tolist()
                if clean_text(value)
            },
            key=str.lower,
        )

    with source_col:
        selected_source = st.selectbox(
            "Source",
            ["All"] + source_values,
            key="database_source_filter",
        )

    filtered = database.copy()

    if search_query.strip():
        query_normalized = _normalize_company_lookup_name(search_query)
        query_lower = search_query.strip().lower()

        exact_mask = filtered["_normalized_name"].eq(query_normalized)

        if exact_mask.any():
            filtered = filtered.loc[exact_mask].copy()
        else:
            filtered = filtered[
                filtered["_display_name"]
                .str.lower()
                .str.contains(
                    re.escape(query_lower),
                    na=False,
                )
            ].copy()

    if selected_source != "All" and "source" in filtered.columns:
        filtered = filtered[
            filtered["source"]
            .fillna("")
            .astype(str)
            .str.strip()
            .eq(selected_source)
        ].copy()

    # Critical performance guard:
    # never run the full intelligence pipeline across the whole database.
    result_limit = 100

    if not search_query.strip():
        st.info(
            "Showing the first 100 companies. Search for a company to load "
            "its unified VERO score and classifications."
        )
        visible = filtered.head(result_limit).copy()
        deep_score = False
    else:
        if len(filtered) > result_limit:
            st.info(
                f"{len(filtered):,} companies matched. Showing the first "
                f"{result_limit} results for performance."
            )
        visible = filtered.head(result_limit).copy()
        deep_score = True

    rows: list[dict[str, Any]] = []

    for _, row in visible.iterrows():
        company_name = clean_text(row.get("_display_name"), "Unknown company")

        industry, _, _ = resolve_row_industry(
            row,
            fallback="Insufficient evidence",
        )

        business_type = clean_text(
            first_present(
                row,
                [
                    "business_type",
                    "Business_Type",
                    "business_type_inferred",
                ],
            )
        ) or "Insufficient evidence"

        business_model = clean_text(
            first_present(
                row,
                [
                    "business_model",
                    "revenue_model",
                    "business_model_inferred",
                ],
            )
        ) or "Insufficient evidence"

        source = clean_text(
            first_present(
                row,
                ["source", "dataset", "platform"],
            ),
            "VERO database",
        )

        website = clean_text(
            first_present(
                row,
                ["website_clean", "website", "url"],
            )
        ) or "Not observed"

        # Only deep-score actual search results. Browsing the first 100 stays fast.
        if deep_score:
            try:
                (
                    profile_dict,
                    vero_dict,
                    confidence,
                    _mode,
                    _evidence,
                ) = get_cached_database_vero_objects(company_name)

                score = safe_number(
                    vero_dict.get("overall_score"),
                    0,
                )

                industry = clean_text(
                    profile_dict.get("industry", {}).get("primary"),
                    industry,
                )

                business_model = clean_text(
                    profile_dict.get("business_model", {}).get("primary"),
                    business_model,
                )
            except Exception:
                score = safe_number(row.get("signal_score"), 0)
                confidence = safe_number(row.get("signal_confidence"), 0)
        else:
            score = safe_number(row.get("signal_score"), 0)
            confidence = safe_number(row.get("signal_confidence"), 0)

        rows.append(
            {
                "Company": company_name,
                "Industry": industry,
                "Business Type": business_type,
                "Business Model": business_model,
                "Source": source,
                "VERO Score": round(score, 1),
                "Confidence": round(confidence, 0),
                "Website": website,
            }
        )

    view = pd.DataFrame(rows)

    if view.empty:
        st.info("No companies match the current filters.")
        return

    a, b, c = st.columns(3)

    with a:
        kpi_card(
            "Matching startups",
            f"{len(filtered):,}",
            "After the current filters",
        )

    with b:
        kpi_card(
            "Total database",
            f"{len(database):,}",
            "Unique cleaned company records",
        )

    with c:
        avg = pd.to_numeric(
            view["VERO Score"],
            errors="coerce",
        ).mean()
        kpi_card(
            "Average VERO score",
            f"{safe_number(avg):.1f}",
            "For currently displayed rows",
        )

    sort_col, direction_col = st.columns([2, 1])

    with sort_col:
        sort_by = st.selectbox(
            "Sort by",
            [
                "Company",
                "VERO Score",
                "Confidence",
                "Industry",
            ],
            key="database_sort_by",
        )

    with direction_col:
        descending = st.checkbox(
            "Descending",
            value=sort_by in {"VERO Score", "Confidence"},
            key="database_sort_desc",
        )

    view = view.sort_values(
        sort_by,
        ascending=not descending,
        key=(
            (lambda series: series.str.lower())
            if sort_by in {"Company", "Industry"}
            else None
        ),
    )

    st.dataframe(
        view,
        width="stretch",
        hide_index=True,
        column_config={
            "VERO Score": st.column_config.NumberColumn(
                "VERO Score",
                format="%.1f",
            ),
            "Confidence": st.column_config.NumberColumn(
                "Confidence",
                format="%.0f%%",
            ),
        },
    )


def render_profile() -> None:
    page_header(
        "Company intelligence",
        "Open a startup profile.",
        "Search VERO's database for one clean, consistent company profile.",
    )

    graph = load_graph_data()
    master = load_master_data()

    if graph.empty and master.empty and yc_data.empty:
        st.warning("The startup profile database is unavailable.")
        return

    def available_names(data: pd.DataFrame) -> list[str]:
        if data.empty:
            return []

        column = next(
            (
                candidate
                for candidate in [
                    "name",
                    "company_name",
                    "startup_name",
                    "organization_name",
                ]
                if candidate in data.columns
            ),
            None,
        )

        if column is None:
            return []

        return [
            name
            for name in (
                data[column]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            )
            if valid_company_name(name)
        ]

    unique_names = sorted(
        set(
            available_names(graph)
            + available_names(master)
            + available_names(yc_data)
        ),
        key=str.lower,
    )

    if not unique_names:
        st.warning("No valid company names are available.")
        return

    search_col, count_col = st.columns([4, 1])

    with search_col:
        default_query = clean_text(
            st.session_state.get("profile_query"),
            "Airbnb",
        )

        query = st.text_input(
            "Search company",
            value=default_query,
            placeholder="Search Airbnb, Stripe, FlatX...",
            key="profile_search_query",
        )

    with count_col:
        st.metric(
            "Companies",
            f"{len(unique_names):,}",
        )

    if query.strip():
        query_lower = query.strip().lower()

        exact = [
            name
            for name in unique_names
            if name.lower() == query_lower
        ]

        partial = [
            name
            for name in unique_names
            if query_lower in name.lower()
            and name.lower() != query_lower
        ]

        options = exact + partial
    else:
        options = unique_names[:100]

    if not options:
        st.warning("No startup found. Try a shorter company name.")
        return

    selected_name = st.selectbox(
        "Select startup",
        options[:100],
        key="profile_company_selector",
    )

    try:
        unified = build_unified_vero_result(
            selected_name
        )
    except Exception as exc:
        st.warning(
            f"VERO could not build this company profile: {exc}"
        )
        return

    row = unified["row"]
    profile = unified["profile"]
    vero = unified["vero"]

    if row.empty:
        st.warning(
            "VERO could not assemble a usable company record."
        )
        return

    company_name = clean_text(
        row.get("name"),
        selected_name,
    )

    source = clean_text(
        first_present(
            row,
            [
                "source",
                "dataset",
                "program_names",
            ],
        ),
        "VERO database",
    )

    # Use the same classification resolver used elsewhere instead of exposing
    # raw hierarchical labels such as "Consumer -> Travel ...".
    industry, industry_method, industry_confidence = resolve_row_industry(
        row,
        fallback=profile.primary_industry or "Insufficient evidence",
    )

    if (
        profile.primary_industry
        and (
            "->" in industry
            or ">" in industry
            or industry.lower()
            in {
                "industry unavailable",
                "industry not classified",
                "unclassified",
            }
        )
    ):
        industry = profile.primary_industry
        industry_method = "VERO intelligence engine"
        industry_confidence = safe_number(
            profile.industry_confidence
        )

    subindustry = (
        profile.primary_subindustry
        or clean_text(row.get("subindustry"))
        or "Insufficient evidence"
    )

    business_model = (
        profile.primary_business_model
        or clean_text(
            first_present(
                row,
                [
                    "business_model",
                    "revenue_model",
                    "business_model_inferred",
                ],
            )
        )
        or "Insufficient evidence"
    )

    business_type = clean_text(
        first_present(
            row,
            [
                "business_type",
                "Business_Type",
                "business_type_inferred",
            ],
        )
    )

    if not business_type:
        business_type = classify_business_type(
            unified["evidence_text"]
        )

    ai_classification = clean_text(
        first_present(
            row,
            [
                "AI_Company",
                "ai_company",
                "ai_classification_inferred",
            ],
        )
    )

    if not ai_classification:
        ai_classification = classify_ai(
            unified["evidence_text"]
        )

    location_parts: list[str] = []

    for column in [
        "location",
        "city",
        "country",
    ]:
        value = clean_text(
            row.get(column)
        )
        if value and value not in location_parts:
            location_parts.append(value)

    location = (
        ", ".join(location_parts)
        if location_parts
        else "Location not observed"
    )

    website = clean_text(
        first_present(
            row,
            [
                "website_clean",
                "website",
                "url",
            ],
        )
    )

    raw_description = get_database_description(
        company_name
    )

    if not raw_description:
        raw_description = clean_text(
            first_present(
                row,
                [
                    "description_clean",
                    "description",
                    "short_description",
                    "long_description",
                    "one_liner",
                    "tagline",
                ],
            )
        )

    if raw_description:
        description = raw_description
    else:
        description = (
            f"{company_name} is classified by VERO as "
            f"{subindustry} within {industry}, using a "
            f"{business_model} business model."
            if industry != "Insufficient evidence"
            else
            "VERO does not currently have enough descriptive evidence "
            "to create a reliable company summary."
        )

    founded = clean_text(
        first_present(
            row,
            [
                "founded_year",
                "year_founded",
                "batch",
                "yc_batch",
            ],
        ),
        "Not observed",
    )

    hiring_raw = clean_text(
        first_present(
            row,
            [
                "isHiring",
                "is_hiring",
                "hiring",
                "hiring_binary",
            ],
        )
    ).lower()

    if hiring_raw in {"true", "yes", "1"}:
        hiring = "Yes"
    elif hiring_raw in {"false", "no", "0"}:
        hiring = "No"
    else:
        hiring = "Not observed"

    score = safe_number(
        vero.overall_score,
        50.0,
    )

    evidence_confidence = safe_number(
        unified["evidence_confidence"],
        0.0,
    )

    evidence_mode = clean_text(
        unified["evidence_mode"],
        "Database",
    )

    merged_count = int(
        safe_number(
            row.get("_merged_record_count"),
            1,
        )
    )

    header_left, header_right = st.columns([3, 1])

    with header_left:
        st.markdown(
            f"""
            <div class="vero-card" style="min-height:250px;">
                <span class="vero-badge">{safe_html(source)}</span>
                <div style="font-size:2.35rem;font-weight:900;margin-top:.85rem;line-height:1.05;">
                    {safe_html(company_name)}
                </div>
                <div class="vero-kpi-sub" style="font-size:1rem;margin-top:.55rem;">
                    {safe_html(industry)} · {safe_html(location)}
                </div>
                <div style="margin-top:1rem;line-height:1.7;max-width:900px;">
                    {safe_html(description)}
                </div>
                <div class="vero-kpi-sub" style="margin-top:1rem;">
                    Evidence mode: {safe_html(evidence_mode)} ·
                    merged from {merged_count} matching record(s)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if website:
            st.link_button(
                "Visit company website",
                website,
                width="content",
            )

    with header_right:
        st.markdown(
            f"""
            <div class="vero-card" style="text-align:center;min-height:250px;display:flex;flex-direction:column;justify-content:center;">
                <div class="vero-kpi-label">VERO SCORE</div>
                <div style="font-size:3.6rem;font-weight:950;line-height:1;margin:.55rem 0;">
                    {score:.0f}
                </div>
                <div class="vero-kpi-sub">out of 100</div>
                <div style="margin-top:.9rem;font-weight:750;">
                    {safe_html(vero.investment_grade)}
                </div>
                <div class="vero-kpi-sub">
                    {evidence_confidence:.0f}% evidence confidence
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section_header(
        "Observed external signals",
        "Only values actually stored in VERO are shown. Missing data is not treated as zero traction.",
    )

    signal_metrics = [
        (
            "Product Hunt votes",
            first_number(
                row,
                [
                    "ph_votes",
                    "product_hunt_votes",
                    "votes_count",
                ],
                default=float("nan"),
            ),
            "Community demand",
        ),
        (
            "GitHub stars",
            first_number(
                row,
                [
                    "github_total_stars",
                    "github_stars",
                    "stars",
                ],
                default=float("nan"),
            ),
            "Developer interest",
        ),
        (
            "GitHub followers",
            first_number(
                row,
                [
                    "github_followers",
                    "followers",
                ],
                default=float("nan"),
            ),
            "Organization reach",
        ),
        (
            "Public repositories",
            first_number(
                row,
                [
                    "github_public_repos",
                    "public_repos",
                    "repo_count",
                ],
                default=float("nan"),
            ),
            "Open-source activity",
        ),
    ]

    for column, (
        label,
        value,
        subtitle,
    ) in zip(
        st.columns(4),
        signal_metrics,
    ):
        with column:
            display_value = (
                "Not observed"
                if pd.isna(value) or value <= 0
                else f"{value:,.0f}"
            )
            kpi_card(
                label,
                display_value,
                subtitle,
            )

    (
        profile_tab,
        classification_tab,
        intelligence_tab,
        explanation_tab,
        raw_tab,
    ) = st.tabs(
        [
            "Company profile",
            "Classifications",
            "VERO intelligence",
            "Score explanation",
            "Raw metadata",
        ]
    )

    with profile_tab:
        left, right = st.columns(2)

        with left:
            kpi_card(
                "Industry",
                industry,
                (
                    f"{industry_method} · "
                    f"{industry_confidence:.0%} confidence"
                    if industry_confidence
                    else industry_method
                ),
            )

            kpi_card(
                "Subindustry",
                subindustry,
                (
                    f"{profile.subindustry_confidence:.0%} confidence"
                    if profile.primary_subindustry
                    else "Insufficient evidence"
                ),
            )

            kpi_card(
                "Customer type",
                business_type or "Insufficient evidence",
                "B2B, B2C, or mixed",
            )

        with right:
            kpi_card(
                "Business model",
                business_model,
                (
                    f"{profile.business_model_confidence:.0%} confidence"
                    if profile.primary_business_model
                    else "Insufficient evidence"
                ),
            )

            kpi_card(
                "Founded / batch",
                founded,
                "Stored company timeline data",
            )

            kpi_card(
                "Hiring",
                hiring,
                "Current stored hiring signal",
            )

    with classification_tab:
        st.markdown("### Why VERO classified it this way")

        classification_rows = [
            (
                "Industry",
                industry,
                industry_method,
                industry_confidence,
            ),
            (
                "Subindustry",
                subindustry,
                "VERO subindustry engine",
                safe_number(
                    profile.subindustry_confidence
                ),
            ),
            (
                "Business model",
                business_model,
                "VERO business-model engine",
                safe_number(
                    profile.business_model_confidence
                ),
            ),
            (
                "AI company",
                ai_classification or "Not observed",
                "Text and metadata classification",
                0.0,
            ),
        ]

        for label, value, method, confidence in classification_rows:
            st.markdown(
                f"**{label}: {value}**"
            )
            if confidence:
                st.caption(
                    f"{method} · {confidence:.0%} confidence"
                )
            else:
                st.caption(method)

        with st.expander(
            "View evidence used for classification"
        ):
            st.code(
                unified["evidence_text"],
                language="text",
            )

    with intelligence_tab:
        top = st.columns(4)

        business_quality_status = getattr(
            profile,
            "business_quality_status",
            "supported",
        )
        moat_status = getattr(
            profile,
            "moat_status",
            "supported",
        )
        risk_status = getattr(
            profile,
            "risk_status",
            "supported",
        )

        with top[0]:
            kpi_card(
                "VERO score",
                f"{score:.1f}/100",
                vero.investment_grade,
            )

        with top[1]:
            kpi_card(
                "Business quality",
                (
                    "Insufficient evidence"
                    if business_quality_status == "insufficient_evidence"
                    else f"{profile.overall_business_quality_score:.2f}/10"
                ),
                (
                    f"{profile.business_quality_confidence:.0%} confidence"
                ),
            )

        with top[2]:
            kpi_card(
                "Moat",
                (
                    "Insufficient evidence"
                    if moat_status == "insufficient_evidence"
                    else f"{profile.overall_moat_score:.2f}/10"
                ),
                f"{profile.moat_confidence:.0%} confidence",
            )

        with top[3]:
            kpi_card(
                "Risk",
                (
                    "Insufficient evidence"
                    if risk_status == "insufficient_evidence"
                    else f"{profile.overall_risk_score:.2f}/10"
                ),
                f"{profile.risk_confidence:.0%} confidence",
            )

        left, right = st.columns(2)

        with left:
            st.markdown("### Likely competitors")

            if profile.competitors:
                for competitor in profile.competitors[:10]:
                    st.markdown(f"- {competitor}")
            else:
                st.info(
                    "No likely competitors were identified from the available evidence."
                )

        with right:
            st.markdown("### Largest risks")

            if profile.largest_risks:
                for risk_name in profile.largest_risks:
                    value = safe_number(
                        profile.risk_scores.get(
                            risk_name,
                            0,
                        )
                    )
                    st.markdown(
                        f"- **{risk_name.replace('_', ' ').title()}:** "
                        f"{value:.2f}/10"
                    )
            else:
                st.info(
                    "No risk category crossed VERO's major-risk threshold."
                )

    with explanation_tab:
        components = dict(
            getattr(
                vero,
                "score_components",
                {},
            )
            or {}
        )

        component_confidence = dict(
            getattr(
                vero,
                "component_confidence",
                {},
            )
            or {}
        )

        st.markdown("### Why this VERO score was assigned")
        st.write(
            f"VERO gives **{company_name}** a score of "
            f"**{score:.1f}/100 ({vero.investment_grade})** using the "
            f"same unified scoring pipeline used across Analyze and Compare."
        )

        maximums = {
            "business_quality": 30.0,
            "moat": 25.0,
            "signals": 15.0,
            "risk_adjustment": 20.0,
            "confidence": 10.0,
        }

        labels = {
            "business_quality": "Business quality",
            "moat": "Moat",
            "signals": "Strategic signals",
            "risk_adjustment": "Risk adjustment",
            "confidence": "Evidence confidence",
        }

        for key, maximum in maximums.items():
            value = safe_number(
                components.get(key)
            )
            progress_bar(
                labels[key],
                value / maximum * 100
                if maximum
                else 0,
            )

            if key == "moat" and moat_status == "insufficient_evidence":
                explanation = (
                    "Moat evidence is insufficient, so VERO pulls this component "
                    "toward neutral instead of treating it as a true zero."
                )
            elif key == "business_quality" and business_quality_status == "insufficient_evidence":
                explanation = (
                    "Business-quality evidence is limited, so this component is "
                    "confidence-adjusted toward neutral."
                )
            elif key == "risk_adjustment" and risk_status == "insufficient_evidence":
                explanation = (
                    "Risk evidence is limited, so VERO avoids assuming the company "
                    "is either low-risk or high-risk."
                )
            else:
                confidence_key = (
                    "risk"
                    if key == "risk_adjustment"
                    else key
                )
                confidence_value = safe_number(
                    component_confidence.get(
                        confidence_key,
                        0,
                    )
                )
                explanation = (
                    f"{value:.2f}/{maximum:.0f} points"
                    + (
                        f" · {confidence_value:.0%} component confidence"
                        if confidence_value
                        else ""
                    )
                )

            st.caption(explanation)

        decision_left, decision_right = st.columns(2)

        with decision_left:
            st.markdown("### Strengths")
            if vero.strengths:
                for item in vero.strengths:
                    st.markdown(f"- {item}")
            else:
                st.info(
                    "No strength threshold was triggered by the available evidence."
                )

        with decision_right:
            st.markdown("### Concerns")
            if vero.concerns:
                for item in vero.concerns:
                    st.markdown(f"- {item}")
            else:
                st.info(
                    "No concern threshold was triggered by the available evidence."
                )

        st.caption(
            f"Evidence mode: {evidence_mode} · "
            f"{evidence_confidence:.0f}% overall evidence confidence"
        )

    with raw_tab:
        metadata: dict[str, Any] = {}

        for key, value in row.to_dict().items():
            try:
                metadata[str(key)] = (
                    None
                    if pd.isna(value)
                    else value
                )
            except (TypeError, ValueError):
                metadata[str(key)] = str(value)

        st.json(metadata)


def render_leaderboards() -> None:
    page_header(
        "Leaderboards",
        "Startup leaderboards.",
        "Rank companies using only observed metrics and the cleaned VERO company layer.",
    )

    graph = load_graph_data()
    master = load_master_data()

    sources = [
        data
        for data in [graph, master, yc_data]
        if not data.empty
    ]

    if not sources:
        st.warning("Leaderboard data is unavailable.")
        return

    combined = pd.concat(
        sources,
        ignore_index=True,
        sort=False,
    )

    name_column = next(
        (
            column
            for column in [
                "name",
                "company_name",
                "startup_name",
                "organization_name",
            ]
            if column in combined.columns
        ),
        None,
    )

    if name_column is None:
        st.warning("No company-name column was found.")
        return

    combined["_display_name"] = (
        combined[name_column]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    combined = combined[
        combined["_display_name"].map(valid_company_name)
    ].copy()

    combined["_normalized_name"] = (
        combined["_display_name"].map(
            _normalize_company_lookup_name
        )
    )

    combined = combined[
        combined["_normalized_name"].ne("")
    ].copy()

    malformed = (
        combined["_display_name"].str.len().gt(90)
        | combined["_display_name"].str.contains(
            r"[.!?]\s",
            regex=True,
            na=False,
        )
    )

    combined = combined.loc[~malformed].copy()

    def quality(row: pd.Series) -> float:
        score = 0.0

        for field in [
            "description_clean",
            "description",
            "short_description",
            "long_description",
            "one_liner",
            "industry",
            "industry_clean",
            "industry_inferred",
            "business_model_inferred",
            "source",
            "website_clean",
            "website",
        ]:
            if field in row.index and clean_text(row.get(field)):
                score += 1

        for aliases in [
            ["ph_votes", "product_hunt_votes", "votes_count"],
            ["github_total_stars", "github_stars", "stars"],
            ["github_followers", "followers"],
            ["github_public_repos", "public_repos", "repo_count"],
            ["signal_score"],
        ]:
            if first_number(row, aliases, 0) > 0:
                score += 1.5

        return score

    best_indexes: list[int] = []

    for _, group in combined.groupby(
        "_normalized_name",
        sort=False,
    ):
        if group.empty:
            continue

        best_idx = max(
            group.index,
            key=lambda idx: quality(
                combined.loc[idx]
            ),
        )
        best_indexes.append(best_idx)

    database = combined.loc[best_indexes].copy()

    leaderboard = st.selectbox(
        "Leaderboard",
        [
            "Top VERO Scores",
            "Top Product Hunt",
            "Top GitHub",
            "Top YC Companies",
            "Top AI Startups",
        ],
        key="leaderboard_type",
    )

    def base_row(row: pd.Series) -> dict[str, Any]:
        company_name = clean_text(
            row.get("_display_name"),
            "Unknown company",
        )

        industry, _, _ = resolve_row_industry(
            row,
            fallback="Insufficient evidence",
        )

        source = clean_text(
            first_present(
                row,
                [
                    "source",
                    "dataset",
                    "platform",
                ],
            ),
            "VERO database",
        )

        return {
            "Company": company_name,
            "Industry": industry,
            "Source": source,
        }

    def score_candidates(
        candidates: pd.DataFrame,
        *,
        limit: int = 25,
    ) -> pd.DataFrame:
        records: list[dict[str, Any]] = []

        shortlist = candidates.head(limit).copy()

        for _, row in shortlist.iterrows():
            info = base_row(row)
            company_name = info["Company"]

            try:
                (
                    profile_dict,
                    vero_dict,
                    evidence_confidence,
                    _mode,
                    _evidence,
                ) = get_cached_database_vero_objects(
                    company_name
                )

                info["Industry"] = clean_text(
                    profile_dict.get("industry", {}).get("primary"),
                    info["Industry"],
                )
                info["VERO Score"] = safe_number(
                    vero_dict.get("overall_score"),
                    0,
                )
                info["Confidence"] = evidence_confidence
            except Exception:
                info["VERO Score"] = safe_number(
                    row.get("signal_score"),
                    0,
                )
                info["Confidence"] = safe_number(
                    row.get("signal_confidence"),
                    0,
                )

            records.append(info)

        frame = pd.DataFrame(records)

        if not frame.empty:
            frame = frame.sort_values(
                ["VERO Score", "Confidence"],
                ascending=[False, False],
            )

        return frame

    if leaderboard == "Top Product Hunt":
        database["_ph_votes"] = database.apply(
            lambda row: first_number(
                row,
                [
                    "ph_votes",
                    "product_hunt_votes",
                    "votes_count",
                    "votes",
                ],
                0,
            ),
            axis=1,
        )

        candidates = database[
            database["_ph_votes"].gt(0)
        ].copy()

        if candidates.empty:
            st.info(
                "VERO does not currently have observed Product Hunt vote data "
                "for enough companies to build this leaderboard."
            )
            return

        candidates = candidates.sort_values(
            "_ph_votes",
            ascending=False,
        ).head(25)

        rows: list[dict[str, Any]] = []

        for _, row in candidates.iterrows():
            info = base_row(row)
            info["Product Hunt Votes"] = int(
                row["_ph_votes"]
            )
            rows.append(info)

        view = pd.DataFrame(rows)
        view.insert(0, "Rank", range(1, len(view) + 1))

        st.dataframe(
            view,
            width="stretch",
            hide_index=True,
        )
        return

    if leaderboard == "Top GitHub":
        database["_github_stars"] = database.apply(
            lambda row: first_number(
                row,
                [
                    "github_total_stars",
                    "github_stars",
                    "stars",
                ],
                0,
            ),
            axis=1,
        )

        database["_github_followers"] = database.apply(
            lambda row: first_number(
                row,
                [
                    "github_followers",
                    "followers",
                ],
                0,
            ),
            axis=1,
        )

        database["_github_repos"] = database.apply(
            lambda row: first_number(
                row,
                [
                    "github_public_repos",
                    "public_repos",
                    "repo_count",
                ],
                0,
            ),
            axis=1,
        )

        # GitHub enrichment in older source files can occasionally duplicate
        # one organization's follower/repository bundle across unrelated rows.
        # Reject suspicious repeated metric bundles before ranking.
        observed = database[
            (
                database["_github_stars"].gt(0)
                | database["_github_followers"].gt(0)
                | database["_github_repos"].gt(0)
            )
        ].copy()

        if observed.empty:
            st.info(
                "VERO does not currently have observed GitHub metrics for "
                "enough companies to build a meaningful GitHub leaderboard."
            )
            return

        observed["_github_bundle"] = (
            observed["_github_stars"].astype(str)
            + "|"
            + observed["_github_followers"].astype(str)
            + "|"
            + observed["_github_repos"].astype(str)
        )

        bundle_counts = observed["_github_bundle"].value_counts()

        suspicious_bundles = set(
            bundle_counts[
                bundle_counts.ge(3)
            ].index.tolist()
        )

        if suspicious_bundles:
            observed = observed[
                ~observed["_github_bundle"].isin(
                    suspicious_bundles
                )
            ].copy()

        # A row with followers/repositories but zero stars can still be valid,
        # so we keep it unless it belongs to a suspicious duplicated bundle.
        if observed.empty:
            st.info(
                "VERO found GitHub data, but the available records contain "
                "duplicated attribution patterns and are not reliable enough "
                "to rank safely."
            )
            return

        observed = observed.sort_values(
            [
                "_github_stars",
                "_github_followers",
                "_github_repos",
            ],
            ascending=False,
        ).head(25)

        rows: list[dict[str, Any]] = []

        for _, row in observed.iterrows():
            info = base_row(row)
            info["GitHub Stars"] = int(
                row["_github_stars"]
            )
            info["GitHub Followers"] = int(
                row["_github_followers"]
            )
            info["Public Repositories"] = int(
                row["_github_repos"]
            )
            rows.append(info)

        view = pd.DataFrame(rows)
        view.insert(
            0,
            "Rank",
            range(1, len(view) + 1),
        )

        st.dataframe(
            view,
            width="stretch",
            hide_index=True,
        )

        if suspicious_bundles:
            st.caption(
                "VERO excluded duplicated GitHub metric bundles that appeared "
                "across multiple unrelated companies."
            )

        return

    if leaderboard == "Top YC Companies":
        if yc_data.empty:
            st.info("YC data is not currently available.")
            return

        yc_name_col = next(
            (
                column
                for column in [
                    "name",
                    "company_name",
                    "startup_name",
                ]
                if column in yc_data.columns
            ),
            None,
        )

        if yc_name_col is None:
            st.info("YC company names are not available.")
            return

        yc_names = {
            _normalize_company_lookup_name(value)
            for value in (
                yc_data[yc_name_col]
                .dropna()
                .astype(str)
                .tolist()
            )
            if valid_company_name(value)
        }

        candidates = database[
            database["_normalized_name"].isin(
                yc_names
            )
        ].copy()

        if candidates.empty:
            st.info(
                "No cleaned YC company records are currently available."
            )
            return

        candidates["_stored_score"] = pd.to_numeric(
            candidates.get(
                "signal_score",
                pd.Series(
                    0,
                    index=candidates.index,
                ),
            ),
            errors="coerce",
        ).fillna(0)

        candidates = candidates.sort_values(
            "_stored_score",
            ascending=False,
        ).head(30)

        view = score_candidates(
            candidates,
            limit=30,
        ).head(20)

        if view.empty:
            st.info(
                "VERO could not score the current YC shortlist."
            )
            return

        view.insert(0, "Rank", range(1, len(view) + 1))

        st.dataframe(
            view[
                [
                    "Rank",
                    "Company",
                    "Industry",
                    "VERO Score",
                    "Confidence",
                    "Source",
                ]
            ],
            width="stretch",
            hide_index=True,
            column_config={
                "VERO Score": st.column_config.NumberColumn(
                    "VERO Score",
                    format="%.1f",
                ),
                "Confidence": st.column_config.NumberColumn(
                    "Confidence",
                    format="%.0f%%",
                ),
            },
        )
        return

    if leaderboard == "Top AI Startups":
        classification_text = _classification_text(
            database
        )

        ai_mask = classification_text.str.contains(
            r"\b(ai|artificial intelligence|machine learning|"
            r"generative ai|llm|large language model|ai agent|"
            r"computer vision|natural language processing)\b",
            regex=True,
            na=False,
        )

        candidates = database[
            ai_mask
        ].copy()

        if candidates.empty:
            st.info(
                "No AI-classified companies are currently available."
            )
            return

        candidates["_stored_score"] = pd.to_numeric(
            candidates.get(
                "signal_score",
                pd.Series(
                    0,
                    index=candidates.index,
                ),
            ),
            errors="coerce",
        ).fillna(0)

        candidates = candidates.sort_values(
            "_stored_score",
            ascending=False,
        ).head(30)

        view = score_candidates(
            candidates,
            limit=30,
        ).head(20)

        if view.empty:
            st.info(
                "VERO could not score the current AI shortlist."
            )
            return

        view.insert(0, "Rank", range(1, len(view) + 1))

        st.dataframe(
            view[
                [
                    "Rank",
                    "Company",
                    "Industry",
                    "VERO Score",
                    "Confidence",
                    "Source",
                ]
            ],
            width="stretch",
            hide_index=True,
            column_config={
                "VERO Score": st.column_config.NumberColumn(
                    "VERO Score",
                    format="%.1f",
                ),
                "Confidence": st.column_config.NumberColumn(
                    "Confidence",
                    format="%.0f%%",
                ),
            },
        )
        return

    # Top VERO Scores
    database["_stored_score"] = pd.to_numeric(
        database.get(
            "signal_score",
            pd.Series(
                0,
                index=database.index,
            ),
        ),
        errors="coerce",
    ).fillna(0)

    shortlist = database.sort_values(
        "_stored_score",
        ascending=False,
    ).head(35)

    view = score_candidates(
        shortlist,
        limit=35,
    ).head(20)

    if view.empty:
        st.info(
            "VERO could not score the current leaderboard shortlist."
        )
        return

    view.insert(0, "Rank", range(1, len(view) + 1))

    st.dataframe(
        view[
            [
                "Rank",
                "Company",
                "Industry",
                "VERO Score",
                "Confidence",
                "Source",
            ]
        ],
        width="stretch",
        hide_index=True,
        column_config={
            "VERO Score": st.column_config.NumberColumn(
                "VERO Score",
                format="%.1f",
            ),
            "Confidence": st.column_config.NumberColumn(
                "Confidence",
                format="%.0f%%",
            ),
        },
    )


def render_model_insights() -> None:
    page_header(
        "Model insights",
        "Understand the historical funding model.",
        "Review the model's validation performance, dataset balance, and the signals that influenced follow-on funding predictions.",
    )

    st.info(
        "This page describes VERO's historical machine-learning model for "
        "follow-on funding outcomes. It is separate from the current VERO "
        "0–100 intelligence score used across Analyze, Profile, Compare, and Leaderboards."
    )

    a, b, c = st.columns(3)

    with a:
        kpi_card(
            "Cross-validated ROC AUC",
            "0.79",
            "Average validation performance",
        )

    with b:
        kpi_card(
            "Standard deviation",
            "0.019",
            "Consistency across validation folds",
        )

    with c:
        kpi_card(
            "Observed success rate",
            "17.98%",
            "Follow-on rounds in training data",
        )

    section_header(
        "What the model predicts",
        "The historical model estimates patterns associated with whether a startup raises a follow-on funding round.",
    )

    st.markdown(
        """
        The model was trained on historical startup records and learns from the
        features available in that dataset. It does **not** directly measure
        company quality, valuation, investment return, or today's VERO score.
        """
    )

    section_header(
        "Key findings",
        "These are directional findings from the trained model, not percentages or probabilities.",
    )

    findings = [
        (
            "YC top-company status",
            "One of the strongest positive predictors observed in the trained model. "
            "Companies carrying this signal were more strongly associated with the "
            "follow-on funding outcome.",
        ),
        (
            "Hiring activity",
            "A meaningful positive signal in the training data. Active hiring was "
            "associated with companies showing expansion or operating momentum.",
        ),
        (
            "Enterprise orientation",
            "Enterprise-focused companies showed somewhat stronger results in the "
            "training data, though this signal should be interpreted together with "
            "industry, age, and other features.",
        ),
        (
            "Product Hunt presence",
            "Useful context, but weaker on its own than stronger company-quality or "
            "operating signals. Presence alone should not be treated as proof of traction.",
        ),
        (
            "Basic GitHub presence",
            "Simple GitHub presence mattered less than deeper traction. Repository activity, "
            "stars, followers, and other engagement signals are more informative than a "
            "binary yes/no flag.",
        ),
    ]

    for title, explanation in findings:
        st.markdown(
            f"""
            <div class="vero-card" style="margin-bottom:.8rem;">
                <div style="font-weight:850;font-size:1.05rem;">
                    {safe_html(title)}
                </div>
                <div class="vero-kpi-sub" style="margin-top:.4rem;line-height:1.6;">
                    {safe_html(explanation)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section_header(
        "How to interpret the statistics",
        "These metrics describe model discrimination and dataset behavior, not certainty for any one company.",
    )

    st.markdown(
        """
        - **ROC AUC 0.79** means the model showed useful ability to rank positive outcomes above negative ones across validation folds.
        - **Standard deviation 0.019** means performance was relatively consistent across those folds.
        - **17.98% observed success rate** is the share of training records labeled with the follow-on funding outcome.
        - None of these numbers mean VERO is 79% accurate on every company.
        """
    )

    st.warning(
        "Historical model outputs are decision-support signals only. They should "
        "not be interpreted as a guarantee that a company will raise another round."
    )


def render_about() -> None:
    page_header(
        "About",
        "About VERO.",
        "VERO is a startup intelligence platform built to turn fragmented company information into structured, explainable analysis.",
    )

    st.markdown(
        """
        <div class="vero-card">
            <div class="vero-eyebrow">THE MISSION</div>
            <h3 style="margin-top:.7rem;">
                Turn scattered startup evidence into a clear, explainable decision-support view.
            </h3>
            <p style="line-height:1.75;margin-bottom:0;">
                VERO combines company descriptions, startup datasets, classifications,
                traction indicators, and other available evidence. Its intelligence
                engines evaluate areas such as business quality, moat strength,
                strategic signals, and risk, then combine those components into an
                explainable 0–100 VERO Score. When enabled, AI research can gather
                additional evidence from current public web sources.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="vero-card">
            <div class="vero-eyebrow">HOW VERO WORKS</div>
            <p style="line-height:1.75;margin-top:.7rem;margin-bottom:0;">
                VERO follows a simple pipeline:
                <strong>Evidence → Classification → Intelligence → Score.</strong>
                Available company evidence is cleaned and classified before VERO's
                engines evaluate business quality, moat, strategic signals, risk,
                and evidence confidence. The final score remains deterministic and
                explainable rather than being directly chosen by an AI model.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="vero-card">
            <div class="vero-eyebrow">CURRENT STACK</div>
            <div style="line-height:2;margin-top:.7rem;">
                Python and pandas<br>
                Scikit-learn historical model pipeline<br>
                Streamlit product interface<br>
                Unified startup database and company profiles<br>
                Industry, business-model, moat, signal, risk, and business-quality engines<br>
                Deterministic VERO scoring pipeline<br>
                YC, Product Hunt, GitHub, and other available startup signals<br>
                Optional AI and live-web research<br>
                Cross-validated historical model evaluation
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="vero-card">
            <div class="vero-eyebrow">HISTORICAL FUNDING MODEL</div>
            <p style="line-height:1.75;margin-top:.7rem;margin-bottom:0;">
                VERO also includes a separate historical machine-learning model used
                to study patterns associated with whether startups raised a follow-on
                funding round. Its validation statistics are shown on the Model
                Insights page. That historical model is not the same thing as the
                current 0–100 VERO intelligence score.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )



def render_privacy() -> None:
    page_header(
        "Privacy Policy",
        "VERO Privacy Policy.",
        "A plain-language explanation of what information VERO may process and how the current application handles it.",
    )

    st.caption("Last updated: August 21, 2026")

    st.warning(
        "VERO is currently an early-stage project. This policy should be reviewed "
        "again before adding production user accounts, payments, analytics, advertising, "
        "or other services that collect additional personal information."
    )

    section_header(
        "1. Information you provide",
        "VERO processes information that you choose to enter into the application.",
    )
    st.markdown(
        """
        This can include startup names, company websites, company descriptions,
        business information, and other evidence entered for analysis. Do not submit
        passwords, financial account information, government identification numbers,
        private health information, or other highly sensitive personal information.
        """
    )

    section_header(
        "2. Startup and public-source data",
        "VERO uses company information from startup datasets and other available sources.",
    )
    st.markdown(
        """
        VERO may process company descriptions, classifications, Product Hunt activity,
        GitHub-related signals, YC information, hiring indicators, company age, and
        other startup evidence available to the application. When optional AI research
        is used, VERO may also gather relevant information from public web sources.
        """
    )

    section_header(
        "3. AI and external services",
        "Some optional VERO features may send a research request to an external AI provider.",
    )
    st.markdown(
        """
        When the **AI + live web research** feature is used, the startup name, website,
        description, and research instructions needed to perform that request may be
        sent to the configured AI service. Users should avoid placing confidential or
        personal information into research fields unless they are authorized to do so.

        VERO's final 0–100 score is produced by its scoring pipeline rather than being
        directly selected by the AI research model.
        """
    )

    section_header(
        "4. Storage",
        "The current VERO application primarily works with its startup datasets and the information needed for the active app session.",
    )
    st.markdown(
        """
        VERO does not intentionally require users to provide sensitive personal data
        to use its core startup-analysis features. Theme and interface choices may be
        stored in the current browser/app session.

        If VERO later adds persistent accounts, saved analyses, cloud databases, or
        other long-term storage, this policy should be updated to explain exactly what
        is retained and for how long.
        """
    )

    section_header(
        "5. How information is used",
        "Information processed by VERO is used to provide and improve startup-intelligence features.",
    )
    st.markdown(
        """
        VERO uses available information to research companies, classify startups,
        calculate intelligence components, generate VERO Scores, compare companies,
        populate profiles and leaderboards, troubleshoot the application, and improve
        the reliability of its analysis.
        """
    )

    section_header(
        "6. Sharing",
        "VERO does not sell user-submitted personal information.",
    )
    st.markdown(
        """
        Information may be processed by service providers only when necessary to
        operate a feature, such as the configured AI provider used for optional
        research. Public company information may also originate from third-party
        datasets and websites.

        VERO should not be used to upload information that you do not have permission
        to share.
        """
    )

    section_header(
        "7. Cookies and analytics",
        "VERO does not currently use its own advertising or behavioral-tracking system.",
    )
    st.markdown(
        """
        The hosting platform or other infrastructure used to operate VERO may process
        basic technical information needed to deliver the application. If VERO later
        adds analytics, advertising, or additional tracking technologies, this policy
        should be updated before those systems are treated as part of the product.
        """
    )

    section_header(
        "8. Children and minors",
        "VERO is a business and startup-analysis tool and is not designed to collect personal information from children.",
    )
    st.markdown(
        """
        Users should not submit personal information about children through VERO.
        """
    )

    section_header(
        "9. Security",
        "VERO is designed to limit unnecessary collection of personal information, but no online service can guarantee absolute security.",
    )
    st.markdown(
        """
        API keys and other private credentials should be stored in protected
        environment variables or Streamlit secrets and should never be entered into
        public company-description or research fields.
        """
    )

    section_header(
        "10. Changes to this policy",
        "This policy may change as VERO's features and infrastructure change.",
    )
    st.markdown(
        """
        Material additions such as user accounts, saved user data, payments,
        analytics, or new external services should be reflected in an updated privacy
        policy.
        """
    )

    section_header(
        "11. Contact",
        "Questions or privacy requests should be directed to the VERO operator.",
    )
    st.markdown(
        """
        Before public launch, replace this paragraph with a monitored contact email
        or other reliable privacy-contact method.
        """
    )



@st.dialog("Terms & Privacy")
def show_terms_privacy_dialog() -> None:
    st.markdown(
        """
        **Welcome to VERO.** Please review these terms before continuing.

        **VERO is a decision-support tool**
        - VERO provides startup and private-company research, scoring, comparisons, and analysis.
        - VERO outputs are informational and are not financial, legal, or investment advice.

        **Information you enter**
        - Startup names, websites, descriptions, and other evidence may be processed to provide VERO's analysis.
        - Do not submit passwords, financial account information, government ID numbers, private health information, or other highly sensitive personal information.

        **AI + live web research**
        - If you use this optional feature, company information and research instructions needed for the request may be sent to the configured AI provider.
        - The final 0–100 VERO Score is still produced by VERO's scoring pipeline rather than being directly chosen by the AI model.

        **Public and third-party information**
        - VERO may use startup datasets and public-source company information.
        - Third-party information can be incomplete or inaccurate.

        **No guarantee**
        - VERO does not guarantee funding, business success, investment returns, or any specific company outcome.

        By continuing, you agree to these Terms and acknowledge the Privacy Policy.
        """
    )

    agreed = st.checkbox(
        "I agree to the Terms and acknowledge the Privacy Policy.",
        key="terms_agree_checkbox",
    )

    left, right = st.columns(2)

    with left:
        if st.button(
            "View Privacy Policy",
            width="stretch",
            key="terms_view_privacy",
        ):
            st.session_state.terms_accepted = True
            st.session_state["pending_page"] = "Privacy Policy"
            st.rerun()

    with right:
        if st.button(
            "Accept and continue",
            width="stretch",
            type="primary",
            disabled=not agreed,
            key="terms_accept_button",
        ):
            st.session_state.terms_accepted = True
            st.rerun()


def render_settings() -> None:
    page_header(
        "Personalization",
        "Customize VERO.",
        "Choose a visual identity for the platform. The layout stays consistent while the full color system changes instantly.",
    )
    st.selectbox("Interface theme", list(THEMES), key="theme_name")
    selected = THEMES[st.session_state.theme_name]
    st.markdown("#### Theme preview")
    swatches = st.columns(5)
    for column, (label, color) in zip(swatches, [
        ("Primary", selected["primary"]),
        ("Secondary", selected["secondary"]),
        ("Background", selected["background"]),
        ("Surface", selected["surface"]),
        ("Text", selected["text"]),
    ]):
        with column:
            st.markdown(
                f'<div class="vero-card"><div style="height:58px;border-radius:11px;background:{color};border:1px solid var(--vero-border);"></div><div class="vero-kpi-sub" style="margin-top:.55rem;">{label}<br>{color}</div></div>',
                unsafe_allow_html=True,
            )
    st.caption("Theme selection is stored for the current browser session.")


PAGES = {
    "Overview": render_overview,
    "Analyze Startup": render_analyze,
    "Compare Startups": render_compare,
    "Startup Database": render_database,
    "Startup Profile": render_profile,
    "Leaderboards": render_leaderboards,
    "Model Insights": render_model_insights,
    "About": render_about,
    "Privacy Policy": render_privacy,
    "Settings": render_settings,
}

if not st.session_state.get("terms_accepted", False):
    show_terms_privacy_dialog()

PAGES[page]()